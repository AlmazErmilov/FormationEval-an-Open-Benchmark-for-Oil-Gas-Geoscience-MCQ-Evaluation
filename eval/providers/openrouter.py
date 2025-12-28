"""
OpenRouter provider for FormationEval evaluation pipeline.

Handles API calls to OpenRouter (OpenAI-compatible) with retries and caching.
Supports 400+ models including DeepSeek, Llama, Qwen, Gemini, Claude, etc.
"""

import asyncio
import json
from datetime import datetime, timezone
from pathlib import Path

from openai import AsyncOpenAI, APIError, APITimeoutError, RateLimitError


# System prompt - strict format to minimize parsing issues
SYSTEM_PROMPT = """You are taking a multiple-choice exam on Oil & Gas geoscience.
For each question, select the single best answer from the options provided.
Reply with exactly one letter: A, B, C, or D. No explanation."""

# Models that don't support system prompts (must use user message only)
NO_SYSTEM_PROMPT_MODELS = {
    "google/gemma-3-27b-it", "google/gemma-3-27b-it:free",
    "google/gemma-3-12b-it", "google/gemma-3-12b-it:free",
    "google/gemma-3-4b-it", "google/gemma-3-4b-it:free",
    "google/gemma-3-1b-it",
    "google/gemma-3n-e4b-it", "google/gemma-3n-e4b-it:free",
    "google/gemma-3n-e2b-it", "google/gemma-3n-e2b-it:free",
    "google/gemma-2-9b-it", "google/gemma-2b-it", "google/gemma-7b-it",
}

# Models that use thinking mode (need higher max_tokens)
THINKING_MODELS = {
    "qwen/qwen3-4b:free", "qwen/qwen3-8b", "qwen/qwen3-14b", "qwen/qwen3-32b",
    "qwen/qwen3-1.7b", "qwen/qwen3-0.6b-04-28",
    "qwen/qwen3-vl-8b-thinking", "qwen/qwen3-30b-a3b-thinking-2507",
    "deepseek/deepseek-r1", "deepseek/deepseek-r1-0528-qwen3-8b",
    "deepseek/deepseek-r1-distill-llama-8b", "deepseek/deepseek-r1-distill-qwen-1.5b",
    "moonshotai/kimi-k2-thinking",
}


class OpenRouterProvider:
    """Provider for OpenRouter API calls with caching and retry logic."""

    def __init__(
        self,
        api_key: str,
        cache_dir: Path | None = None,
        max_retries: int = 3,
        timeout: float = 60.0,
        site_url: str = "https://github.com/FormationEval",
        site_name: str = "FormationEval Benchmark",
    ):
        """
        Initialize OpenRouter provider.

        Args:
            api_key: OpenRouter API key
            cache_dir: Directory for caching responses
            max_retries: Maximum retry attempts
            timeout: Request timeout in seconds
            site_url: Your site URL (for OpenRouter rankings)
            site_name: Your app name (for OpenRouter rankings)
        """
        self.client = AsyncOpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=api_key,
            timeout=timeout,
            default_headers={
                "HTTP-Referer": site_url,
                "X-Title": site_name,
            },
        )
        self.cache_dir = cache_dir
        self.max_retries = max_retries

    def _sanitize_model_name(self, model: str) -> str:
        """Sanitize model name for filesystem (replace / with _)."""
        return model.replace("/", "_").replace(":", "_")

    def _get_cache_path(self, model: str, question_id: str) -> Path | None:
        """Get cache file path for a model/question pair."""
        if self.cache_dir is None:
            return None

        safe_model = self._sanitize_model_name(model)
        safe_id = question_id.replace("/", "_").replace("\\", "_")
        model_cache_dir = self.cache_dir / safe_model
        model_cache_dir.mkdir(parents=True, exist_ok=True)
        return model_cache_dir / f"{safe_id}.json"

    def load_cached(self, model: str, question_id: str) -> dict | None:
        """Load cached response if available."""
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
        model: str,
        question: dict,
        temperature: float | None = None,
    ) -> dict:
        """
        Call OpenRouter API for a single question.

        Args:
            model: Model ID (e.g., "deepseek/deepseek-r1", "meta-llama/llama-4-scout")
            question: Question dict with 'id', 'question', 'choices'
            temperature: Sampling temperature (None = use model default)

        Returns:
            Response dict with 'raw_response', 'usage', 'model', 'timestamp'
        """
        question_id = question["id"]

        # Check cache first
        cached = self.load_cached(model, question_id)
        if cached is not None:
            return cached

        user_prompt = self._format_prompt(question)

        # Build messages based on model capabilities
        if model in NO_SYSTEM_PROMPT_MODELS:
            # Combine system prompt into user message for models that don't support system role
            combined_prompt = f"{SYSTEM_PROMPT}\n\n{user_prompt}"
            messages = [{"role": "user", "content": combined_prompt}]
        else:
            messages = [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ]

        # Build API call kwargs - let the model decide response length
        kwargs = {
            "model": model,
            "messages": messages,
        }
        # Only set temperature if explicitly specified (otherwise use model default)
        if temperature is not None:
            kwargs["temperature"] = temperature

        # Retry logic with exponential backoff
        last_error = None
        for attempt in range(self.max_retries):
            try:
                response = await self.client.chat.completions.create(**kwargs)

                # Safely extract response content
                raw_content = ""
                if response.choices and len(response.choices) > 0:
                    msg = response.choices[0].message
                    if msg and msg.content:
                        raw_content = msg.content

                result = {
                    "model": model,
                    "model_response": response.model,  # Actual model from API
                    "provider": "openrouter",
                    "question_id": question_id,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "raw_response": raw_content,
                    "usage": {
                        "prompt_tokens": response.usage.prompt_tokens if response.usage else 0,
                        "completion_tokens": response.usage.completion_tokens if response.usage else 0,
                        "total_tokens": response.usage.total_tokens if response.usage else 0,
                    },
                }

                # Cache successful response
                self.save_to_cache(model, question_id, result)
                return result

            except RateLimitError as e:
                last_error = e
                wait_time = 2 ** (attempt + 1)  # Exponential backoff: 2, 4, 8 seconds
                await asyncio.sleep(wait_time)

            except (APIError, APITimeoutError) as e:
                last_error = e
                wait_time = 2 ** attempt
                await asyncio.sleep(wait_time)

        # All retries failed
        return {
            "model": model,
            "provider": "openrouter",
            "question_id": question_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "raw_response": "",
            "error": str(last_error),
            "usage": {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0},
        }

    async def evaluate_batch(
        self,
        model: str,
        questions: list[dict],
        concurrency: int = 20,
        temperature: float | None = None,
        progress_callback: callable = None,
    ) -> list[dict]:
        """
        Evaluate a batch of questions with controlled concurrency.

        Args:
            model: Model ID
            questions: List of question dicts
            concurrency: Max concurrent requests
            temperature: Sampling temperature (None = use model default)
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
                    model=model,
                    question=q,
                    temperature=temperature,
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
