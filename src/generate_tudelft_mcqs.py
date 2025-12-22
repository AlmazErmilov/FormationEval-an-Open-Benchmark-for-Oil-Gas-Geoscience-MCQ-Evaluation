"""
MCQ Generator for TU Delft Petroleum Geology Open CourseWare.
Generates questions lecture by lecture.

Source: TU Delft OCW - Petroleum Geology (AES3820)
License: CC BY-NC-SA 4.0
URL: https://ocw.tudelft.nl/courses/petroleum-geology/

Location: src/generate_tudelft_mcqs.py
"""

import json
import sys
from pathlib import Path

# Script paths
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent

# Add src folder to path for imports
sys.path.insert(0, str(SCRIPT_DIR))

from generate_mcq import generate_mcqs, save_questions

# Paths
LECTURES_DIR = PROJECT_ROOT / "data/sources/open/Petroleum Geology - TU Delft OCW"
OUTPUT_DIR = PROJECT_ROOT / "data/benchmark"

# Source metadata
SOURCE_INFO = {
    "source_id": "tudelft_petroleum_geology_ocw",
    "source_title": "Petroleum Geology (AES3820) - TU Delft Open CourseWare",
    "source_url": "https://ocw.tudelft.nl/courses/petroleum-geology/",
    "source_type": "lecture_slides",
    "year": 2008,
    "license": "CC BY-NC-SA 4.0",
    "attribution": "Prof. Dr. Stefan M. Luthi, TU Delft",
    "retrieved_at": "2025-12-22"
}

# Lecture mapping (file -> lecture reference and topic)
LECTURES = {
    "PGeo_L1_Petroleum_Geology_-_Lecture_1_08.md": {
        "ref": "Lecture 1 - Introduction",
        "topic": "Introduction to Petroleum Geology"
    },
    "PGeo_L2_Petroleum_Geology_-_Lecture_2_08.md": {
        "ref": "Lecture 2 - Carbon Cycle and Maturation",
        "topic": "The Carbon Cycle, Organic Matter and Maturation"
    },
    "PGeo_L3_Petroleum_Geology_-_Lecture_3_08.md": {
        "ref": "Lecture 3 - Composition of Oil and Gas",
        "topic": "Composition of Oil and Gas"
    },
    "PGeo_L4_Petroleum_Geology_-_Lecture_4_08.md": {
        "ref": "Lecture 4 - Migration",
        "topic": "Migration from Source to Reservoir"
    },
    "PGeo_L5_Petroleum_Geology_-_Lecture_5_08.md": {
        "ref": "Lecture 5 - Reservoir Rock Properties",
        "topic": "Reservoir Rock Properties"
    },
    "PGeo_L6_Petroleum_Geology_-_Lecture_6_08.md": {
        "ref": "Lecture 6 - Trapping",
        "topic": "Hydrocarbon Trapping"
    },
    "PGeo_L7_Petroleum_Geology_-_Lecture_7_08.md": {
        "ref": "Lecture 7 - Basin Types and Exploration",
        "topic": "Basin Types and Exploration"
    },
}


def generate_for_lecture(
    lecture_file: str,
    num_questions: str | int = "2-10",
    model: str = "gpt-5.2",
    reasoning_effort: str = "high"
) -> tuple[list[dict], dict]:
    """Generate MCQs for a single lecture.

    Returns:
        Tuple of (questions list, usage stats dict)
    """

    lecture_path = LECTURES_DIR / lecture_file
    lecture_info = LECTURES.get(lecture_file, {"ref": lecture_file, "topic": "Unknown"})
    lecture_ref = lecture_info["ref"]

    print(f"\n{'='*60}")
    print(f"Processing: {lecture_ref}")
    print(f"File: {lecture_file}")
    print(f"{'='*60}")

    # Read lecture text
    with open(lecture_path, "r", encoding="utf-8") as f:
        lecture_text = f.read()

    print(f"Lecture length: {len(lecture_text):,} characters")

    # Build source info string for the prompt
    source_info_str = f"""## Source Information
- source_id: {SOURCE_INFO['source_id']}
- source_title: {SOURCE_INFO['source_title']}
- source_url: {SOURCE_INFO['source_url']}
- source_type: {SOURCE_INFO['source_type']}
- year: {SOURCE_INFO['year']}
- license: {SOURCE_INFO['license']}
- attribution: {SOURCE_INFO['attribution']}
- retrieved_at: {SOURCE_INFO['retrieved_at']}

## Lecture Information
- lecture_ref: {lecture_ref}
- topic: {lecture_info['topic']}

Note: This content is from university lecture slides. Focus on testable technical concepts, not course logistics or references."""

    # Generate MCQs
    q_display = num_questions if isinstance(num_questions, str) else f"{num_questions}"
    print(f"Generating {q_display} MCQs with {model} (reasoning: {reasoning_effort})...")

    questions, usage_stats = generate_mcqs(
        chapter_text=lecture_text,
        num_questions=num_questions,
        source_info=source_info_str,
        model=model,
        reasoning_effort=reasoning_effort,
        return_usage=True
    )

    print(f"Generated {len(questions)} questions")

    # Add/update source metadata in each question
    for q in questions:
        q["sources"] = [{
            "source_id": SOURCE_INFO["source_id"],
            "source_title": SOURCE_INFO["source_title"],
            "source_url": SOURCE_INFO["source_url"],
            "source_type": SOURCE_INFO["source_type"],
            "year": SOURCE_INFO["year"],
            "license": SOURCE_INFO["license"],
            "attribution": SOURCE_INFO["attribution"],
            "lecture_ref": lecture_ref,
            "retrieved_at": SOURCE_INFO["retrieved_at"],
            "notes": q.get("sources", [{}])[0].get("notes", f"Concept-based item from {lecture_ref}")
        }]

    return questions, usage_stats


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Generate MCQs from TU Delft Petroleum Geology lectures")
    parser.add_argument("lecture", nargs="?", help="Lecture file name or 'all'")
    parser.add_argument("-n", "--num-questions", default="2-10", help="Number of questions - int or range (default: 2-10)")
    parser.add_argument("-m", "--model", default="gpt-5.2", help="OpenAI model to use")
    parser.add_argument("-r", "--reasoning", default="high", choices=["none", "low", "medium", "high"], help="Reasoning effort")
    parser.add_argument("-o", "--output", help="Output file path (default: auto-generated)")
    parser.add_argument("--list", action="store_true", help="List available lectures")

    args = parser.parse_args()

    # Parse num_questions - can be int or range string
    num_q = args.num_questions
    if isinstance(num_q, str) and num_q.isdigit():
        num_q = int(num_q)

    if args.list:
        print("Available lectures:")
        for i, (file, info) in enumerate(LECTURES.items(), 1):
            print(f"  {i}. {file}")
            print(f"     -> {info['ref']}: {info['topic']}")
        return

    if not args.lecture:
        parser.print_help()
        print("\nExample usage:")
        print("  python src/generate_tudelft_mcqs.py PGeo_L1_Petroleum_Geology_-_Lecture_1_08.md")
        print("  python src/generate_tudelft_mcqs.py PGeo_L2_Petroleum_Geology_-_Lecture_2_08.md -n 5")
        print("  python src/generate_tudelft_mcqs.py all")
        print("  python src/generate_tudelft_mcqs.py --list")
        return

    all_questions = []
    total_usage = {
        'input_tokens': 0,
        'output_tokens': 0,
        'total_tokens': 0,
        'cached_tokens': 0,
        'reasoning_tokens': 0,
        'visible_tokens': 0
    }

    if args.lecture.lower() == "all":
        # Generate for all lectures
        for lecture_file in LECTURES.keys():
            questions, usage = generate_for_lecture(
                lecture_file,
                num_questions=num_q,
                model=args.model,
                reasoning_effort=args.reasoning
            )
            all_questions.extend(questions)
            for key in total_usage:
                total_usage[key] += usage.get(key, 0)
    else:
        # Single lecture
        if args.lecture not in LECTURES:
            print(f"Error: Unknown lecture '{args.lecture}'")
            print("Use --list to see available lectures")
            return

        questions, usage = generate_for_lecture(
            args.lecture,
            num_questions=num_q,
            model=args.model,
            reasoning_effort=args.reasoning
        )
        all_questions.extend(questions)
        for key in total_usage:
            total_usage[key] += usage.get(key, 0)

    # Determine output path
    if args.output:
        output_path = Path(args.output)
    else:
        if args.lecture.lower() == "all":
            output_path = OUTPUT_DIR / "tudelft_all_mcqs.json"
        else:
            lecture_name = args.lecture.replace(".md", "")
            output_path = OUTPUT_DIR / f"tudelft_{lecture_name}_mcqs.json"

    # Save questions
    output_path.parent.mkdir(parents=True, exist_ok=True)
    save_questions(all_questions, str(output_path))

    # Summary
    print(f"\n{'='*60}")
    print(f"Summary:")
    print(f"  Total questions: {len(all_questions)}")
    print(f"  Output file: {output_path}")

    # Difficulty distribution
    difficulties = {}
    for q in all_questions:
        d = q.get("difficulty", "unknown")
        difficulties[d] = difficulties.get(d, 0) + 1
    print(f"  Difficulty distribution:")
    for d, count in sorted(difficulties.items()):
        print(f"    {d}: {count} ({100*count/len(all_questions):.1f}%)")

    # Answer distribution
    answers = {}
    for q in all_questions:
        a = q.get("answer_key", "?")
        answers[a] = answers.get(a, 0) + 1
    print(f"  Answer distribution:")
    for a in "ABCD":
        count = answers.get(a, 0)
        print(f"    {a}: {count} ({100*count/len(all_questions):.1f}%)")

    # Token usage summary
    if total_usage.get('total_tokens', 0) > 0:
        print(f"\n  Total Token Usage:")
        print(f"    Input:     {total_usage['input_tokens']:,} tokens", end="")
        if total_usage['cached_tokens']:
            print(f" ({total_usage['cached_tokens']:,} cached)")
        else:
            print()
        print(f"    Output:    {total_usage['output_tokens']:,} tokens")
        if total_usage['reasoning_tokens']:
            pct = 100 * total_usage['reasoning_tokens'] / total_usage['output_tokens']
            print(f"      - Reasoning: {total_usage['reasoning_tokens']:,} tokens ({pct:.1f}%)")
            print(f"      - Visible:   {total_usage['visible_tokens']:,} tokens ({100-pct:.1f}%)")
        print(f"    Total:     {total_usage['total_tokens']:,} tokens")
        print(f"    Tokens/question: {total_usage['total_tokens'] / len(all_questions):,.0f}")


if __name__ == "__main__":
    main()
