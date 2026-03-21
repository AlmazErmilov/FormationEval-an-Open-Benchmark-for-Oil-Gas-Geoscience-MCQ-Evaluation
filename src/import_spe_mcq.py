"""
Import the public SPE MCQ dataset into the FormationEval imported MCQ track schema.
"""

from __future__ import annotations

import argparse
import json
from datetime import date
from pathlib import Path
from typing import Any
from urllib.request import Request, urlopen


PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_ROWS_URL = (
    "https://datasets-server.huggingface.co/rows"
    "?dataset=ynuwara/spe_mcq_dataset&config=default&split=train&offset=0&length=100"
)
DEFAULT_DATASET_URL = "https://huggingface.co/datasets/ynuwara/spe_mcq_dataset"
DEFAULT_OUTPUT = PROJECT_ROOT / "data/benchmark/formationeval_spe_mcq_v0.3.json"
DEFAULT_MANIFEST_OUTPUT = PROJECT_ROOT / "data/benchmark/formationeval_v0.3_manifest.json"
DEFAULT_ASSETS_DIR = (
    PROJECT_ROOT / "data/benchmark/assets/formationeval_spe_mcq_figures"
)
MCQ_PATH = PROJECT_ROOT / "data/benchmark/formationeval_v0.1.json"
QA_PATH = PROJECT_ROOT / "data/benchmark/formationeval_diskos_qa_v0.2.json"
USER_AGENT = "FormationEval/0.3 (+https://www.formationeval.no)"

PETROPHYSICS_NUMBERS = {34, 48, 85, 97, 98}
DRILLING_NUMBERS = set(range(1, 14)) | {15} | set(range(51, 64)) | {73, 74}
PRODUCTION_NUMBERS = (
    {14}
    | set(range(16, 31))
    | set(range(64, 81))
)


def read_json(path: Path) -> Any:
    return json.loads(path.read_text())


def write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n")


def fetch_json(url: str) -> Any:
    request = Request(url, headers={"User-Agent": USER_AGENT})
    with urlopen(request, timeout=30) as response:
        return json.load(response)


def fetch_rows(rows_url: str) -> list[dict[str, Any]]:
    payload = fetch_json(rows_url)
    rows = [entry["row"] for entry in payload["rows"]]
    if len(rows) != 100:
        raise ValueError(f"Expected 100 upstream SPE rows, got {len(rows)}")
    return rows


def resolve_domains(number: int) -> list[str]:
    if number in PETROPHYSICS_NUMBERS:
        return ["Petrophysics"]
    if number in DRILLING_NUMBERS:
        return ["Drilling Engineering"]
    if number in PRODUCTION_NUMBERS:
        return ["Production Engineering"]
    return ["Reservoir Engineering"]


def build_sources(retrieved_at: str) -> list[dict[str, Any]]:
    return [
        {
            "source_id": "spe_mcq_huggingface_2025",
            "source_title": "SPE MCQ Dataset",
            "source_url": DEFAULT_DATASET_URL,
            "source_type": "open_data",
            "year": 2025,
            "license": "MIT (as tagged in upstream Hugging Face metadata)",
            "attribution": "Yohanes Nuwara",
            "retrieved_at": retrieved_at,
            "notes": (
                "Imported external MCQ track from the public Hugging Face dataset. "
                "The upstream dataset card says the MCQ bank is originally from the "
                "Study Guide for the SPE Petroleum Engineering Certification "
                "Examination (4th ed., 2011). See THIRD_PARTY_NOTICES.md."
            ),
        },
        {
            "source_id": "spe_petroleum_engineering_certification_guide_2011",
            "source_title": (
                "Study Guide for the SPE Petroleum Engineering Certification "
                "Examination (4th ed.)"
            ),
            "source_url": None,
            "source_type": "manual",
            "year": 2011,
            "license": "Origin noted in the upstream dataset card, see THIRD_PARTY_NOTICES.md",
            "attribution": "Society of Petroleum Engineers",
            "retrieved_at": retrieved_at,
            "notes": (
                "The upstream Hugging Face dataset card identifies this study guide as "
                "the original source context for the MCQ bank."
            ),
        },
    ]


def download_figure(url: str, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    request = Request(url, headers={"User-Agent": USER_AGENT})
    with urlopen(request, timeout=30) as response:
        destination.write_bytes(response.read())


def build_figure(number: int, upstream_figure: dict[str, Any], assets_dir: Path) -> dict[str, Any]:
    filename = f"formationeval_v0.3_spe_mcq_{number:03d}.png"
    output_path = assets_dir / filename
    download_figure(upstream_figure["src"], output_path)
    return {
        "path": f"data/benchmark/assets/formationeval_spe_mcq_figures/{filename}",
        "filename": filename,
        "alt": f"Upstream figure for imported SPE MCQ item {number:03d}.",
        "width": int(upstream_figure["width"]),
        "height": int(upstream_figure["height"]),
    }


def build_record(row: dict[str, Any], retrieved_at: str, assets_dir: Path) -> dict[str, Any]:
    number = int(row["number"])
    answer_key = str(row["correct_answer"]).strip().upper()
    if answer_key not in {"A", "B", "C", "D"}:
        raise ValueError(f"Unexpected answer key for item {number}: {answer_key}")

    choices = [str(row[key]).strip() for key in ("A", "B", "C", "D")]
    figure = None
    if row.get("figure"):
        figure = build_figure(number, row["figure"], assets_dir)

    return {
        "id": f"formationeval_v0.3_spe_mcq_{number:03d}",
        "version": "formationeval_v0.3",
        "domains": resolve_domains(number),
        "topics": [],
        "difficulty": "unknown",
        "language": "en",
        "question": str(row["question"]).strip(),
        "choices": choices,
        "answer_index": ord(answer_key) - ord("A"),
        "answer_key": answer_key,
        "rationale": "",
        "sources": build_sources(retrieved_at),
        "derivation_mode": "external_open_benchmark",
        "metadata": {
            "calc_required": None,
            "contamination_risk": None,
        },
        "figure": figure,
    }


def build_manifest(spe_count: int) -> dict[str, Any]:
    mcq_count = len(read_json(MCQ_PATH))
    qa_count = len(read_json(QA_PATH))
    return {
        "suite_id": "formationeval_v0.3",
        "release_date": "2026-03-21",
        "summary": (
            "FormationEval v0.3 keeps the evaluated MCQ track frozen and expands the "
            "public suite with imported DISKOS-QA and SPE MCQ tracks."
        ),
        "pending_note": (
            "Added March 2026. FormationEval now also includes the imported DISKOS-QA "
            "and SPE MCQ tracks. The public leaderboard and quiz still reflect the "
            "505-question MCQ v0.1 track. The original model-comparison goal of the "
            "project was already addressed with that benchmark. A full rerun on the "
            "expanded suite is pending because this is a self funded one person project "
            "and expanded suite evaluation requires materially more token spend."
        ),
        "contact": {
            "email": "almaz.ermilov@gmail.com",
            "note": (
                "Collaboration, compute support, and professional opportunities are welcome."
            ),
        },
        "tracks": [
            {
                "track_id": "mcq_v0.1",
                "config_name": "default",
                "question_format": "mcq",
                "file": "formationeval_v0.1.json",
                "version": "formationeval_v0.1",
                "item_count": mcq_count,
                "evaluated": True,
                "current_public_leaderboard": True,
                "license_note": (
                    "FormationEval-authored MCQ track. Project-authored materials remain "
                    "under CC BY 4.0. See LICENSE."
                ),
                "source_urls": [
                    "https://huggingface.co/datasets/AlmazErmilov/FormationEval",
                    "https://www.formationeval.no",
                ],
            },
            {
                "track_id": "diskos_qa_v0.2",
                "config_name": "diskos_qa",
                "question_format": "qa",
                "file": "formationeval_diskos_qa_v0.2.json",
                "version": "formationeval_v0.2",
                "item_count": qa_count,
                "evaluated": False,
                "current_public_leaderboard": False,
                "license_note": (
                    "Contains data under the Norwegian Licence for Open Government Data "
                    "(NLOD) distributed by the DISKOS-QA benchmark project, as stated in "
                    "the upstream README. See THIRD_PARTY_NOTICES.md."
                ),
                "source_urls": [
                    "https://github.com/georgeghon/DISKOS-QA",
                    "https://zenodo.org/records/10775273",
                ],
            },
            {
                "track_id": "spe_mcq_v0.3",
                "config_name": "spe_mcq",
                "question_format": "mcq",
                "file": "formationeval_spe_mcq_v0.3.json",
                "version": "formationeval_v0.3",
                "item_count": spe_count,
                "evaluated": False,
                "current_public_leaderboard": False,
                "license_note": (
                    "Imported external MCQ content from the public SPE MCQ Dataset on "
                    "Hugging Face. Upstream metadata tags the dataset as MIT, while the "
                    "upstream dataset card says the MCQ bank is originally from the Study "
                    "Guide for the SPE Petroleum Engineering Certification Examination "
                    "(4th ed., 2011). See THIRD_PARTY_NOTICES.md."
                ),
                "source_urls": [
                    DEFAULT_DATASET_URL,
                ],
            },
        ],
    }


def clear_assets_dir(assets_dir: Path) -> None:
    assets_dir.mkdir(parents=True, exist_ok=True)
    for path in assets_dir.glob("formationeval_v0.3_spe_mcq_*.png"):
        path.unlink()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--rows-url", default=DEFAULT_ROWS_URL, help="HF rows API URL")
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT,
        help="Output path for normalized SPE MCQ JSON",
    )
    parser.add_argument(
        "--manifest-output",
        type=Path,
        default=DEFAULT_MANIFEST_OUTPUT,
        help="Output path for suite manifest JSON",
    )
    parser.add_argument(
        "--assets-dir",
        type=Path,
        default=DEFAULT_ASSETS_DIR,
        help="Directory where figure assets will be stored",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    retrieved_at = date.today().isoformat()
    rows = fetch_rows(args.rows_url)
    clear_assets_dir(args.assets_dir)
    records = [build_record(row, retrieved_at, args.assets_dir) for row in rows]

    write_json(args.output, records)
    write_json(args.manifest_output, build_manifest(len(records)))

    figure_count = sum(1 for record in records if record["figure"] is not None)
    print(f"Wrote {len(records)} SPE MCQ records to {args.output}")
    print(f"Downloaded {figure_count} figure assets to {args.assets_dir}")
    print(f"Wrote manifest to {args.manifest_output}")


if __name__ == "__main__":
    main()
