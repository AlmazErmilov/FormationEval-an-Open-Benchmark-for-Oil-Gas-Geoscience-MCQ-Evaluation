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

def generate_mcqs(
    chapter_text: str,
    num_questions: int = 10,
    source_info: str = "",
    model: str = "gpt-5.2",
    reasoning_effort: str = "high"
) -> list[dict]:
    """
    Generate MCQs from chapter text.

    Args:
        chapter_text: The chapter content to generate questions from
        num_questions: Number of questions to generate
        source_info: Optional source metadata (book title, chapter, etc.)
        model: OpenAI model to use
        reasoning_effort: Reasoning effort level (low, medium, high)

    Returns:
        List of MCQ dictionaries
    """
    client = OpenAI()

    system_prompt = load_system_prompt()

    user_message = f"""Generate {num_questions} multiple-choice questions from the following chapter.

{f"Source: {source_info}" if source_info else ""}

Aim for a mix of difficulties:
- ~30% easy (BSc level)
- ~50% medium (MSc level)
- ~20% hard (PhD level)

---

CHAPTER TEXT:

{chapter_text}

---

Generate {num_questions} questions as a JSON array."""

    response = client.responses.create(
        model=model,
        reasoning={"effort": reasoning_effort},
        input=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ]
    )

    # Parse JSON response
    content = response.output_text

    # Handle potential markdown code blocks
    if "```json" in content:
        content = content.split("```json")[1].split("```")[0]
    elif "```" in content:
        content = content.split("```")[1].split("```")[0]

    questions = json.loads(content.strip())

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


def save_questions(questions: list[dict], output_path: str):
    """Save questions to JSONL file."""
    with open(output_path, "w") as f:
        for q in questions:
            f.write(json.dumps(q) + "\n")
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
