"""
MCQ Generator using OpenAI API
Generates multiple-choice questions from chapter text.
"""

import json
import os
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI

# Paths relative to this script
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent

# Load environment variables from .env file in project root
load_dotenv(PROJECT_ROOT / ".env")

# Load system prompt
PROMPT_PATH = SCRIPT_DIR / "prompts" / "mcq_generator_system_prompt.txt" # example, draft v1

def load_system_prompt() -> str:
    """Load the system prompt from file."""
    with open(PROMPT_PATH, "r") as f:
        return f.read()

def extract_usage_stats(usage) -> dict:
    """Extract token usage statistics from API response as a dictionary."""
    if not usage:
        return {}

    input_tokens = getattr(usage, 'input_tokens', 0)
    output_tokens = getattr(usage, 'output_tokens', 0)
    total_tokens = getattr(usage, 'total_tokens', 0)

    # Get detailed breakdowns
    input_details = getattr(usage, 'input_tokens_details', None)
    output_details = getattr(usage, 'output_tokens_details', None)

    cached_tokens = 0
    reasoning_tokens = 0

    if input_details:
        cached_tokens = getattr(input_details, 'cached_tokens', 0)
    if output_details:
        reasoning_tokens = getattr(output_details, 'reasoning_tokens', 0)

    return {
        'input_tokens': input_tokens,
        'output_tokens': output_tokens,
        'total_tokens': total_tokens,
        'cached_tokens': cached_tokens,
        'reasoning_tokens': reasoning_tokens,
        'visible_tokens': output_tokens - reasoning_tokens
    }


def print_usage_stats(usage_or_dict, model: str = "", reasoning_effort: str = ""):
    """Print token usage statistics.

    Args:
        usage_or_dict: Either API response usage object or dict from extract_usage_stats()
        model: Model name for display
        reasoning_effort: Reasoning effort level for display
    """
    if isinstance(usage_or_dict, dict):
        stats = usage_or_dict
    else:
        stats = extract_usage_stats(usage_or_dict)

    if not stats:
        print("  Token usage: Not available")
        return

    input_tokens = stats.get('input_tokens', 0)
    output_tokens = stats.get('output_tokens', 0)
    total_tokens = stats.get('total_tokens', 0)
    cached_tokens = stats.get('cached_tokens', 0)
    reasoning_tokens = stats.get('reasoning_tokens', 0)
    visible_tokens = stats.get('visible_tokens', output_tokens - reasoning_tokens)

    header = "Token Usage"
    if model:
        header += f" ({model}"
        if reasoning_effort:
            header += f", reasoning={reasoning_effort}"
        header += ")"

    print(f"\n  {header}:")
    print(f"    Input:     {input_tokens:,} tokens" + (f" ({cached_tokens:,} cached)" if cached_tokens else ""))
    print(f"    Output:    {output_tokens:,} tokens")
    if reasoning_tokens:
        pct = 100 * reasoning_tokens / output_tokens if output_tokens else 0
        print(f"      - Reasoning: {reasoning_tokens:,} tokens ({pct:.1f}%)")
        print(f"      - Visible:   {visible_tokens:,} tokens ({100-pct:.1f}%)")
    print(f"    Total:     {total_tokens:,} tokens")


def generate_mcqs(
    chapter_text: str,
    num_questions: str | int = "5-15",
    source_info: str = "",
    model: str = "gpt-5.2",
    reasoning_effort: str = "high",
    print_stats: bool = True,
    return_usage: bool = False
) -> list[dict] | tuple[list[dict], dict]:
    """
    Generate MCQs from chapter text using OpenAI Responses API.

    Args:
        chapter_text: The chapter content to generate questions from
        num_questions: Number of questions - can be int (e.g., 10) or range string (e.g., "5-15")
        source_info: Optional source metadata (book title, chapter, etc.)
        model: OpenAI model to use (gpt-5.2, gpt-5.2-mini, etc.)
        reasoning_effort: Reasoning effort level (none, low, medium, high)
        print_stats: Whether to print token usage stats (default: True)
        return_usage: Whether to return usage stats dict along with questions (default: False)

    Returns:
        List of MCQ dictionaries, or tuple of (questions, usage_stats) if return_usage=True
    """
    client = OpenAI()

    system_prompt = load_system_prompt()

    # Format question count instruction
    if isinstance(num_questions, str) and "-" in num_questions:
        question_instruction = f"between {num_questions.replace('-', ' and ')} questions"
    else:
        question_instruction = f"exactly {num_questions} questions"

    user_message = f"""Generate {question_instruction} from the following chapter.

{f"Source: {source_info}" if source_info else ""}

Aim for a mix of difficulties:
- ~30% easy (BSc level)
- ~50% medium (MSc level)
- ~20% hard (PhD level)

---

CHAPTER TEXT:

{chapter_text}

---

Generate {question_instruction} as a JSON array. Choose the exact number based on how much quality content the chapter provides - prefer more questions for content-rich chapters."""

    response = client.responses.create(
        model=model,
        reasoning={"effort": reasoning_effort},
        input=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ]
    )

    # Extract usage stats
    usage_stats = extract_usage_stats(getattr(response, 'usage', None))

    # Print token usage stats
    if print_stats:
        print_usage_stats(usage_stats, model, reasoning_effort)

    # Parse JSON response
    content = response.output_text

    # Handle potential markdown code blocks
    if "```json" in content:
        content = content.split("```json")[1].split("```")[0]
    elif "```" in content:
        content = content.split("```")[1].split("```")[0]

    questions = json.loads(content.strip())

    if return_usage:
        return questions, usage_stats
    return questions


def add_metadata(
    questions: list[dict],
    source_id: str,
    source_title: str,
    source_url: str = "",
    license: str = "",
    chapter_ref: str = ""
) -> list[dict]:
    """
    Add source metadata to generated questions.

    Args:
        questions: List of MCQ dictionaries
        source_id: Unique identifier for the source
        source_title: Title of the source book/document
        source_url: URL to the source
        license: License type (e.g., "CC BY-NC-SA 4.0")
        chapter_ref: Chapter reference string

    Returns:
        Questions with added metadata
    """
    for i, q in enumerate(questions):
        q["id"] = f"formationeval_v0_{source_id}_{i:04d}"
        q["version"] = "formationeval_v0.1"
        q["language"] = "en"
        q["derivation_mode"] = "concept_based"
        q["sources"] = [{
            "source_id": source_id,
            "source_title": source_title,
            "source_url": source_url,
            "license": license,
            "chapter_ref": chapter_ref
        }]

    return questions


def save_questions(questions: list[dict], output_path: str, format: str = "json"):
    """Save questions to file.

    Args:
        questions: List of MCQ dictionaries
        output_path: Output file path
        format: Output format - "json" (array, pretty-printed) or "jsonl" (one per line)
    """
    with open(output_path, "w", encoding="utf-8") as f:
        if format == "jsonl":
            for q in questions:
                f.write(json.dumps(q, ensure_ascii=False) + "\n")
        else:  # json array format (default, matches existing benchmark)
            json.dump(questions, f, indent=4, ensure_ascii=False)
    print(f"Saved {len(questions)} questions to {output_path}")


# Example usage
if __name__ == "__main__":
    # Example, generate from a text file
    import sys

    if len(sys.argv) < 2:
        print("Usage: python generate_mcq.py <chapter_file.txt> [num_questions]")
        print("       Set OPENAI_API_KEY environment variable first.")
        sys.exit(1)

    chapter_file = sys.argv[1]
    num_questions = int(sys.argv[2]) if len(sys.argv) > 2 else 10

    with open(chapter_file, "r") as f:
        chapter_text = f.read()

    print(f"Generating {num_questions} questions from {chapter_file}...")

    questions = generate_mcqs(
        chapter_text=chapter_text,
        num_questions=num_questions,
        source_info=chapter_file
    )

    # Add basic metadata, example
    questions = add_metadata(
        questions,
        source_id="test",
        source_title="Test Source",
        chapter_ref=chapter_file
    )

    # Save to output
    output_path = chapter_file.replace(".txt", "_mcqs.jsonl")
    save_questions(questions, output_path)
