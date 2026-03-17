"""
Validate the FormationEval suite structure for MCQ v0.1 and DISKOS-QA v0.2.
"""

from __future__ import annotations

import argparse
import ast
import csv
import hashlib
import io
import json
import re
from pathlib import Path
from urllib.request import urlopen


PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_DISKOS_URL = (
    "https://raw.githubusercontent.com/georgeghon/DISKOS-QA/main/benchmark/dataset/"
    "FORCE_QA_public_final.csv"
)
MCQ_PATH = PROJECT_ROOT / "data/benchmark/formationeval_v0.1.json"
QA_PATH = PROJECT_ROOT / "data/benchmark/formationeval_diskos_qa_v0.2.json"
MANIFEST_PATH = PROJECT_ROOT / "data/benchmark/formationeval_v0.2_manifest.json"
EXPECTED_MCQ_SHA256 = "6401cd577f06de5ef473ad21a2d9bb05c9f337bc8b7f10076a483ad3a49943e3"
QA_ID_PATTERN = re.compile(r"^formationeval_v0\.2_diskos_[a-z0-9_]+_[0-9a-f]{12}$")
QUESTION_ID_PATTERN = re.compile(r"^[0-9a-f]{40}$")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def fetch_diskos_rows(source_url: str) -> list[dict[str, str]]:
    with urlopen(source_url) as response:
        content = response.read().decode("utf-8")
    return list(csv.DictReader(io.StringIO(content)))


def assert_condition(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def validate_mcq() -> list[dict]:
    questions = json.loads(MCQ_PATH.read_text())
    assert_condition(sha256(MCQ_PATH) == EXPECTED_MCQ_SHA256, "MCQ v0.1 file hash changed")
    assert_condition(len(questions) == 505, f"Expected 505 MCQ items, got {len(questions)}")
    return questions


def validate_manifest(qa_count: int) -> None:
    manifest = json.loads(MANIFEST_PATH.read_text())
    assert_condition(manifest["suite_id"] == "formationeval_v0.2", "Unexpected suite_id")
    tracks = {track["track_id"]: track for track in manifest["tracks"]}
    assert_condition(tracks["mcq_v0.1"]["item_count"] == 505, "Manifest MCQ count mismatch")
    assert_condition(
        tracks["diskos_qa_v0.2"]["item_count"] == qa_count,
        "Manifest QA count mismatch",
    )


def validate_qa(source_url: str) -> list[dict]:
    remote_rows = fetch_diskos_rows(source_url)
    qa_rows = json.loads(QA_PATH.read_text())

    assert_condition(
        len(remote_rows) == len(qa_rows),
        f"QA count mismatch: remote={len(remote_rows)} local={len(qa_rows)}",
    )

    qa_ids: set[str] = set()
    question_ids: set[str] = set()

    for index, (remote_row, qa_row) in enumerate(zip(remote_rows, qa_rows), start=1):
        parsed_chunk_ids = ast.literal_eval(remote_row["Chunk_IDs"])
        parsed_content = ast.literal_eval(remote_row["Content"])
        assert_condition(isinstance(parsed_chunk_ids, list), f"Row {index}: Chunk_IDs is not a list")
        assert_condition(isinstance(parsed_content, list), f"Row {index}: Content is not a list")
        assert_condition(
            len(parsed_chunk_ids) == len(parsed_content),
            f"Row {index}: Chunk_IDs and Content length mismatch",
        )

        qa_id = qa_row["id"]
        question_id = qa_row["metadata"]["diskos"]["question_id"]

        assert_condition(qa_id not in qa_ids, f"Duplicate QA id: {qa_id}")
        qa_ids.add(qa_id)
        assert_condition(
            bool(QA_ID_PATTERN.fullmatch(qa_id)),
            f"Row {index}: invalid QA id format: {qa_id}",
        )

        assert_condition(question_id not in question_ids, f"Duplicate upstream Question_ID: {question_id}")
        question_ids.add(question_id)
        assert_condition(
            bool(QUESTION_ID_PATTERN.fullmatch(question_id)),
            f"Row {index}: invalid upstream Question_ID format: {question_id}",
        )

        assert_condition(question_id == remote_row["Question_ID"], f"Row {index}: Question_ID mismatch")
        assert_condition(qa_row["question_format"] == "qa", f"Row {index}: wrong question_format")
        assert_condition(qa_row["version"] == "formationeval_v0.2", f"Row {index}: wrong version")
        assert_condition(
            qa_row["derivation_mode"] == "external_open_benchmark",
            f"Row {index}: wrong derivation_mode",
        )
        assert_condition(len(qa_row["sources"]) == 2, f"Row {index}: expected 2 sources")
        assert_condition(
            len(qa_row["context_snippets"]) == len(parsed_content),
            f"Row {index}: context snippet count mismatch",
        )

    validate_manifest(len(qa_rows))
    return qa_rows


def validate_cross_track_ids(mcq_rows: list[dict], qa_rows: list[dict]) -> None:
    mcq_ids = {row["id"] for row in mcq_rows}
    qa_ids = {row["id"] for row in qa_rows}
    overlap = mcq_ids & qa_ids
    assert_condition(not overlap, f"Cross-track id collisions found: {sorted(overlap)[:5]}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-url", default=DEFAULT_DISKOS_URL, help="Raw DISKOS-QA CSV URL")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    mcq_rows = validate_mcq()
    qa_rows = validate_qa(args.source_url)
    validate_cross_track_ids(mcq_rows, qa_rows)
    print("FormationEval suite validation passed.")


if __name__ == "__main__":
    main()
