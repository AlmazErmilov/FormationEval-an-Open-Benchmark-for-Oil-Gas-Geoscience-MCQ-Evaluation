"""
Azure OpenAI provider for FormationEval evaluation pipeline.

Handles API calls, retries, and response caching.
"""

import asyncio
import json
import os
from datetime import datetime, timezone
from pathlib import Path

from openai import AsyncAzureOpenAI, APIError, APITimeoutError, RateLimitError


# System prompt - strict format to minimize parsing issues
SYSTEM_PROMPT = """You are taking a multiple-choice exam on Oil & Gas geoscience.
For each question, select the single best answer from the options provided.
Reply with exactly one letter: A, B, C, or D. No explanation."""


class AzureOpenAIProvider:
    """Provider for Azure OpenAI API calls with caching and retry logic."""

    def __init__(
        self,
        endpoint: str,
        api_key: str,
        api_version: str = "2024-02-01",
        cache_dir: Path | None = None,
        max_retries: int = 3,
        timeout: float = 30.0,
    ):
        """
        Initialize Azure OpenAI provider.

        Args:
            endpoint: Azure OpenAI endpoint URL
            api_key: API key
            api_version: API version string
            cache_dir: Directory for caching responses
            max_retries: Maximum retry attempts
            timeout: Request timeout in seconds
        """
        self.client = AsyncAzureOpenAI(
            azure_endpoint=endpoint,
            api_key=api_key,
            api_version=api_version,
            timeout=timeout,
        )
        self.cache_dir = cache_dir
        self.max_retries = max_retries

    def _get_cache_path(self, model: str, question_id: str) -> Path | None:
        """Get cache file path for a model/question pair."""
        if self.cache_dir is None:
            return None

        # Sanitize question_id for filesystem (replace problematic chars)
        safe_id = question_id.replace("/", "_").replace("\\", "_")
        model_cache_dir = self.cache_dir / model
        model_cache_dir.mkdir(parents=True, exist_ok=True)
        return model_cache_dir / f"{safe_id}.json"

    def load_cached(self, model: str, question_id: str) -> dict | None:
        """
        Load cached response if available.

        Returns:
            Cached response dict or None if not cached.
        """
        cache_path = self._get_cache_path(model, question_id)
        if cache_path is None or not cache_path.exists():
            return None

        try:
            with open(cache_path, "r") as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError):
            return None

    def save_to_cache(self, model: str, question_id: str, response: dict) -> None:
        """Save response to cache."""
        cache_path = self._get_cache_path(model, question_id)
        if cache_path is None:
            return

        with open(cache_path, "w") as f:
            json.dump(response, f, indent=2)

    def _format_prompt(self, question: dict) -> str:
        """Format question into user prompt."""
        choices = question["choices"]
        return f"""{question["question"]}

A) {choices[0]}
B) {choices[1]}
C) {choices[2]}
D) {choices[3]}

Answer:"""

    async def call_api(
        self,
        deployment: str,
        question: dict,
        temperature: float = 0,
        reasoning_effort: str | None = None,
        cache_key: str | None = None,
    ) -> dict:
        """
        Call Azure OpenAI API for a single question.

        Args:
            deployment: Deployment name (e.g., "gpt-4o-mini")
            question: Question dict with 'id', 'question', 'choices'
            temperature: Sampling temperature
            reasoning_effort: Reasoning effort for o-series models (low/medium/high)
            cache_key: Key for caching (defaults to deployment, use model name for variations)

        Returns:
            Response dict with 'raw_response', 'usage', 'model', 'timestamp'
        """
        question_id = question["id"]
        cache_key = cache_key or deployment

        # Check cache first
        cached = self.load_cached(cache_key, question_id)
        if cached is not None:
            return cached

        user_prompt = self._format_prompt(question)

        # Build API call kwargs
        kwargs = {
            "model": deployment,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
        }

        # Reasoning models don't support temperature or max_tokens
        if reasoning_effort:
            kwargs["reasoning_effort"] = reasoning_effort
            # Let the model decide output length for reasoning models
        else:
            kwargs["temperature"] = temperature
            kwargs["max_tokens"] = 50  # Short response expected for non-reasoning

        # Retry logic with exponential backoff
        last_error = None
        for attempt in range(self.max_retries):
            try:
                response = await self.client.chat.completions.create(**kwargs)

                result = {
                    "model": response.model,  # Actual model name from API
                    "deployment": deployment,  # Our deployment name
                    "cache_key": cache_key,  # Cache key (model name with reasoning suffix)
                    "question_id": question_id,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "raw_response": response.choices[0].message.content or "",
                    "reasoning_effort": reasoning_effort,
                    "usage": {
                        "prompt_tokens": response.usage.prompt_tokens if response.usage else 0,
                        "completion_tokens": response.usage.completion_tokens if response.usage else 0,
                        "total_tokens": response.usage.total_tokens if response.usage else 0,
                    },
                }

                # Cache successful response
                self.save_to_cache(cache_key, question_id, result)
                return result

            except RateLimitError as e:
                last_error = e
                wait_time = 2 ** attempt  # Exponential backoff: 1, 2, 4 seconds
                await asyncio.sleep(wait_time)

            except (APIError, APITimeoutError) as e:
                last_error = e
                wait_time = 2 ** attempt
                await asyncio.sleep(wait_time)

        # All retries failed
        return {
            "model": deployment,  # Use deployment as fallback when API fails
            "deployment": deployment,
            "question_id": question_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "raw_response": "",
            "error": str(last_error),
            "usage": {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0},
        }

    async def evaluate_batch(
        self,
        deployment: str,
        questions: list[dict],
        concurrency: int = 20,
        temperature: float = 0,
        reasoning_effort: str | None = None,
        cache_key: str | None = None,
        progress_callback: callable = None,
    ) -> list[dict]:
        """
        Evaluate a batch of questions with controlled concurrency.

        Args:
            deployment: Deployment name
            questions: List of question dicts
            concurrency: Max concurrent requests
            temperature: Sampling temperature
            reasoning_effort: For o-series models
            cache_key: Key for caching (defaults to deployment)
            progress_callback: Optional callback(completed, total) for progress

        Returns:
            List of response dicts in same order as questions
        """
        semaphore = asyncio.Semaphore(concurrency)
        completed = 0

        async def process_one(q: dict) -> dict:
            nonlocal completed
            async with semaphore:
                result = await self.call_api(
                    deployment=deployment,
                    question=q,
                    temperature=temperature,
                    reasoning_effort=reasoning_effort,
                    cache_key=cache_key,
                )
                completed += 1
                if progress_callback:
                    progress_callback(completed, len(questions))
                return result

        tasks = [process_one(q) for q in questions]
        return await asyncio.gather(*tasks)

    async def close(self):
        """Close the client connection."""
        await self.client.close()


# Factory function for creating provider from config
def create_provider_from_config(config: dict, cache_dir: Path | None = None) -> AzureOpenAIProvider:
    """
    Create provider from config dict.

    Expected config structure:
        {
            "endpoint": "https://...",
            "api_key": "...",
            "api_version": "2024-02-01"
        }
    """
    return AzureOpenAIProvider(
        endpoint=config["endpoint"],
        api_key=config["api_key"],
        api_version=config.get("api_version", "2024-02-01"),
        cache_dir=cache_dir,
        max_retries=config.get("max_retries", 3),
        timeout=config.get("timeout", 30.0),
    )
