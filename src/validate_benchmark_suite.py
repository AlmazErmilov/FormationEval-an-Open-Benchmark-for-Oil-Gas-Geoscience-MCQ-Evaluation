"""
Validate the FormationEval public suite for MCQ v0.1, DISKOS-QA v0.2, and SPE MCQ v0.3.
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
from typing import Any
from urllib.request import Request, urlopen


PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_DISKOS_URL = (
    "https://raw.githubusercontent.com/georgeghon/DISKOS-QA/main/benchmark/dataset/"
    "FORCE_QA_public_final.csv"
)
DEFAULT_SPE_ROWS_URL = (
    "https://datasets-server.huggingface.co/rows"
    "?dataset=ynuwara/spe_mcq_dataset&config=default&split=train&offset=0&length=100"
)
MCQ_PATH = PROJECT_ROOT / "data/benchmark/formationeval_v0.1.json"
QA_PATH = PROJECT_ROOT / "data/benchmark/formationeval_diskos_qa_v0.2.json"
SPE_PATH = PROJECT_ROOT / "data/benchmark/formationeval_spe_mcq_v0.3.json"
MANIFEST_PATH = PROJECT_ROOT / "data/benchmark/formationeval_v0.3_manifest.json"
SPE_FIGURES_DIR = PROJECT_ROOT / "data/benchmark/assets/formationeval_spe_mcq_figures"
EXPECTED_MCQ_SHA256 = "6401cd577f06de5ef473ad21a2d9bb05c9f337bc8b7f10076a483ad3a49943e3"
QA_ID_PATTERN = re.compile(r"^formationeval_v0\.2_diskos_[a-z0-9_]+_[0-9a-f]{12}$")
QUESTION_ID_PATTERN = re.compile(r"^[0-9a-f]{40}$")
SPE_ID_PATTERN = re.compile(r"^formationeval_v0\.3_spe_mcq_\d{3}$")
USER_AGENT = "FormationEval/0.3 (+https://www.formationeval.no)"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def fetch_text(source_url: str) -> str:
    request = Request(source_url, headers={"User-Agent": USER_AGENT})
    with urlopen(request, timeout=30) as response:
        return response.read().decode("utf-8")


def fetch_json(source_url: str) -> Any:
    request = Request(source_url, headers={"User-Agent": USER_AGENT})
    with urlopen(request, timeout=30) as response:
        return json.load(response)


def fetch_diskos_rows(source_url: str) -> list[dict[str, str]]:
    return list(csv.DictReader(io.StringIO(fetch_text(source_url))))


def fetch_spe_rows(source_url: str) -> list[dict[str, Any]]:
    payload = fetch_json(source_url)
    return [entry["row"] for entry in payload["rows"]]


def assert_condition(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def validate_mcq() -> list[dict[str, Any]]:
    questions = json.loads(MCQ_PATH.read_text())
    assert_condition(sha256(MCQ_PATH) == EXPECTED_MCQ_SHA256, "MCQ v0.1 file hash changed")
    assert_condition(len(questions) == 505, f"Expected 505 MCQ items, got {len(questions)}")
    return questions


def validate_manifest(qa_count: int, spe_count: int) -> None:
    manifest = json.loads(MANIFEST_PATH.read_text())
    assert_condition(manifest["suite_id"] == "formationeval_v0.3", "Unexpected suite_id")
    tracks = {track["track_id"]: track for track in manifest["tracks"]}
    assert_condition(tracks["mcq_v0.1"]["item_count"] == 505, "Manifest MCQ count mismatch")
    assert_condition(
        tracks["diskos_qa_v0.2"]["item_count"] == qa_count,
        "Manifest DISKOS count mismatch",
    )
    assert_condition(
        tracks["spe_mcq_v0.3"]["item_count"] == spe_count,
        "Manifest SPE count mismatch",
    )
    assert_condition(
        tracks["spe_mcq_v0.3"]["config_name"] == "spe_mcq",
        "Manifest SPE config mismatch",
    )


def validate_qa(source_url: str) -> list[dict[str, Any]]:
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

    return qa_rows


def validate_spe(source_url: str) -> list[dict[str, Any]]:
    remote_rows = fetch_spe_rows(source_url)
    spe_rows = json.loads(SPE_PATH.read_text())
    assert_condition(
        len(remote_rows) == len(spe_rows) == 100,
        f"SPE count mismatch: remote={len(remote_rows)} local={len(spe_rows)}",
    )

    spe_ids: set[str] = set()
    figure_refs: set[Path] = set()
    remote_figure_count = 0

    for index, (remote_row, spe_row) in enumerate(zip(remote_rows, spe_rows), start=1):
        number = int(remote_row["number"])
        expected_id = f"formationeval_v0.3_spe_mcq_{number:03d}"
        answer_key = str(remote_row["correct_answer"]).strip().upper()

        assert_condition(
            bool(SPE_ID_PATTERN.fullmatch(spe_row["id"])),
            f"Row {index}: invalid SPE id format: {spe_row['id']}",
        )
        assert_condition(spe_row["id"] == expected_id, f"Row {index}: unexpected SPE id")
        assert_condition(spe_row["id"] not in spe_ids, f"Duplicate SPE id: {spe_row['id']}")
        spe_ids.add(spe_row["id"])
        assert_condition(spe_row["version"] == "formationeval_v0.3", f"Row {index}: wrong version")
        assert_condition(
            spe_row["derivation_mode"] == "external_open_benchmark",
            f"Row {index}: wrong derivation_mode",
        )
        assert_condition(spe_row["topics"] == [], f"Row {index}: SPE topics should be empty")
        assert_condition(
            spe_row["difficulty"] == "unknown",
            f"Row {index}: SPE difficulty should be unknown",
        )
        assert_condition(
            isinstance(spe_row["metadata"], dict),
            f"Row {index}: metadata should be an object",
        )
        assert_condition(
            spe_row["metadata"].get("calc_required") is None,
            f"Row {index}: calc_required should be null for imported SPE items",
        )
        assert_condition(
            spe_row["metadata"].get("contamination_risk") is None,
            f"Row {index}: contamination_risk should be null for imported SPE items",
        )
        assert_condition(len(spe_row["choices"]) == 4, f"Row {index}: expected 4 choices")
        assert_condition(
            spe_row["choices"] == [remote_row["A"], remote_row["B"], remote_row["C"], remote_row["D"]],
            f"Row {index}: choice text mismatch",
        )
        assert_condition(spe_row["answer_key"] == answer_key, f"Row {index}: answer_key mismatch")
        assert_condition(
            spe_row["answer_index"] == ord(answer_key) - ord("A"),
            f"Row {index}: answer_index mismatch",
        )
        assert_condition(spe_row["rationale"] == "", f"Row {index}: rationale should be empty")
        assert_condition(len(spe_row["sources"]) == 2, f"Row {index}: expected 2 sources")

        figure = spe_row.get("figure")
        if remote_row.get("figure") is None:
            assert_condition(figure is None, f"Row {index}: unexpected figure reference")
            continue

        remote_figure_count += 1
        assert_condition(figure is not None, f"Row {index}: missing figure reference")
        figure_path = PROJECT_ROOT / figure["path"]
        assert_condition(figure_path.is_file(), f"Row {index}: missing local figure asset")
        assert_condition(
            figure_path.parent == SPE_FIGURES_DIR,
            f"Row {index}: figure stored outside SPE figure directory",
        )
        assert_condition(figure["filename"] == figure_path.name, f"Row {index}: filename mismatch")
        assert_condition(int(figure["width"]) > 0, f"Row {index}: invalid figure width")
        assert_condition(int(figure["height"]) > 0, f"Row {index}: invalid figure height")
        figure_refs.add(figure_path)

    local_assets = set(SPE_FIGURES_DIR.glob("formationeval_v0.3_spe_mcq_*.png"))
    assert_condition(
        len(figure_refs) == remote_figure_count == 10,
        f"SPE figure count mismatch: remote={remote_figure_count} local_refs={len(figure_refs)}",
    )
    assert_condition(
        figure_refs == local_assets,
        "SPE figure asset set does not match figure references in JSON",
    )

    return spe_rows


def validate_cross_track_ids(
    mcq_rows: list[dict[str, Any]],
    qa_rows: list[dict[str, Any]],
    spe_rows: list[dict[str, Any]],
) -> None:
    mcq_ids = {row["id"] for row in mcq_rows}
    qa_ids = {row["id"] for row in qa_rows}
    spe_ids = {row["id"] for row in spe_rows}
    overlap = (mcq_ids & qa_ids) | (mcq_ids & spe_ids) | (qa_ids & spe_ids)
    assert_condition(not overlap, f"Cross-track id collisions found: {sorted(overlap)[:5]}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--diskos-url", default=DEFAULT_DISKOS_URL, help="Raw DISKOS-QA CSV URL")
    parser.add_argument(
        "--spe-rows-url",
        default=DEFAULT_SPE_ROWS_URL,
        help="Hugging Face rows API URL for SPE MCQ",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    mcq_rows = validate_mcq()
    qa_rows = validate_qa(args.diskos_url)
    spe_rows = validate_spe(args.spe_rows_url)
    validate_cross_track_ids(mcq_rows, qa_rows, spe_rows)
    validate_manifest(len(qa_rows), len(spe_rows))
    print("FormationEval suite validation passed.")


if __name__ == "__main__":
    main()
