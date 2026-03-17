"""
Import the public DISKOS-QA CSV into the FormationEval QA track schema.
"""

from __future__ import annotations

import argparse
import ast
import csv
import io
import json
import re
from datetime import date
from pathlib import Path
from urllib.request import urlopen


PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_SOURCE_URL = (
    "https://raw.githubusercontent.com/georgeghon/DISKOS-QA/main/benchmark/dataset/"
    "FORCE_QA_public_final.csv"
)
DEFAULT_QA_OUTPUT = PROJECT_ROOT / "data/benchmark/formationeval_diskos_qa_v0.2.json"
DEFAULT_MANIFEST_OUTPUT = PROJECT_ROOT / "data/benchmark/formationeval_v0.2_manifest.json"


def slugify_topic(value: str) -> str:
    slug = value.lower()
    slug = re.sub(r"[\s\-\/]+", "_", slug)
    slug = re.sub(r"[^a-z0-9_]", "", slug)
    slug = re.sub(r"_+", "_", slug).strip("_")
    return slug


def parse_literal_list(value: str) -> list[str]:
    parsed = ast.literal_eval(value)
    if not isinstance(parsed, list):
        raise ValueError(f"Expected list literal, got {type(parsed).__name__}")
    return [str(item) for item in parsed]


def build_sources(retrieved_at: str) -> list[dict]:
    return [
        {
            "source_id": "diskos_qa_benchmark_2026",
            "source_title": "DISKOS-QA benchmark",
            "source_url": "https://github.com/georgeghon/DISKOS-QA",
            "source_type": "open_data",
            "year": 2026,
            "license": "NLOD 2.0 (as stated in upstream README)",
            "attribution": "DISKOS-QA, FORCE industry collaboration",
            "retrieved_at": retrieved_at,
            "notes": (
                "Imported external QA benchmark track from the public DISKOS-QA repository. "
                "See THIRD_PARTY_NOTICES.md for licensing notes."
            ),
        },
        {
            "source_id": "diskos_underlying_corpus_zenodo_10775273",
            "source_title": (
                "Large Oil and Gas industry text dataset from Norwegian, UK and Dutch "
                "public oil and gas documents"
            ),
            "source_url": "https://zenodo.org/records/10775273",
            "source_type": "open_data",
            "year": 2024,
            "license": "CC BY 4.0",
            "attribution": "FORCE and collaborators",
            "retrieved_at": retrieved_at,
            "notes": "Underlying public corpus provenance referenced by DISKOS-QA.",
        },
    ]


def build_record(row: dict[str, str], retrieved_at: str) -> dict:
    chunk_ids = parse_literal_list(row["Chunk_IDs"])
    chunk_texts = parse_literal_list(row["Content"])
    topic = row["Topic"].strip()
    topic_slug = slugify_topic(topic)
    qid = row["Question_ID"].strip()

    if len(chunk_ids) != len(chunk_texts):
        raise ValueError(
            f"Chunk mismatch for Question_ID={qid}: {len(chunk_ids)} ids vs {len(chunk_texts)} snippets"
        )

    context_snippets = [
        {
            "chunk_index": index,
            "chunk_id": chunk_id,
            "text": snippet.strip(),
        }
        for index, (chunk_id, snippet) in enumerate(zip(chunk_ids, chunk_texts), start=1)
    ]

    return {
        "id": f"formationeval_v0.2_diskos_{topic_slug}_{qid[:12]}",
        "version": "formationeval_v0.2",
        "question_format": "qa",
        "language": "en",
        "topics": [topic],
        "question": row["Question"].strip(),
        "answer_text": row["Answer"].strip(),
        "context_snippets": context_snippets,
        "sources": build_sources(retrieved_at),
        "derivation_mode": "external_open_benchmark",
        "metadata": {
            "diskos": {
                "question_id": qid,
                "chunk_ids": chunk_ids,
                "well_names": row["Well_names"].strip(),
                "wellbore_names": row["Wellbore_names"].strip(),
                "field_names": row["Field_names"].strip(),
                "formation_names": row["Formation_names"].strip(),
                "filter_type": row["Filter_type"].strip(),
                "filter_name": row["Filter_name"].strip(),
                "topic": topic,
                "evolutions": row["Evolutions"].strip(),
                "document_id": row["Document_id"].strip(),
                "document_name": row["Document_name"].strip(),
                "entailed": row["Entailed"].strip().lower() == "true",
            }
        },
    }


def fetch_rows(source_url: str) -> list[dict[str, str]]:
    with urlopen(source_url) as response:
        content = response.read().decode("utf-8")
    return list(csv.DictReader(io.StringIO(content)))


def build_manifest(row_count: int) -> dict:
    return {
        "suite_id": "formationeval_v0.2",
        "release_date": "2026-03-17",
        "summary": (
            "FormationEval is now a split benchmark suite with a frozen evaluated MCQ "
            "track and an imported DISKOS-QA track."
        ),
        "pending_note": (
            "Added March 2026. FormationEval now also includes DISKOS-QA. The public "
            "leaderboard and quiz still reflect the 505-question MCQ v0.1 track. That "
            "benchmark already answered the original model-comparison goal of the project. "
            "A full rerun on the expanded suite is pending because this is a self funded one "
            "person "
            "project and QA evaluation requires materially more token spend."
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
                "item_count": 505,
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
                "item_count": row_count,
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
        ],
    }


def write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-url", default=DEFAULT_SOURCE_URL, help="Raw DISKOS-QA CSV URL")
    parser.add_argument(
        "--qa-output",
        type=Path,
        default=DEFAULT_QA_OUTPUT,
        help="Output path for normalized QA JSON",
    )
    parser.add_argument(
        "--manifest-output",
        type=Path,
        default=DEFAULT_MANIFEST_OUTPUT,
        help="Output path for suite manifest JSON",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    retrieved_at = date.today().isoformat()
    rows = fetch_rows(args.source_url)
    records = [build_record(row, retrieved_at) for row in rows]

    write_json(args.qa_output, records)
    write_json(args.manifest_output, build_manifest(len(records)))

    print(f"Wrote {len(records)} QA records to {args.qa_output}")
    print(f"Wrote manifest to {args.manifest_output}")


if __name__ == "__main__":
    main()
