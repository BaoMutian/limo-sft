"""Dataset loaders for various benchmark formats."""

import csv
import json
import logging
import random
from pathlib import Path

logger = logging.getLogger(__name__)


def load_jsonl(path: str, problem_key: str, answer_key: str, metadata_keys: list[str] | None = None) -> list[dict]:
    items = []
    with open(path) as f:
        for i, line in enumerate(f):
            raw = json.loads(line)
            item = {
                "idx": i,
                "problem": raw[problem_key],
                "answer": str(raw[answer_key]),
            }
            for key in (metadata_keys or []):
                if key in raw:
                    item[key] = raw[key]
            items.append(item)
    return items


def load_parquet(path: str, problem_key: str, answer_key: str, metadata_keys: list[str] | None = None) -> list[dict]:
    import pyarrow.parquet as pq

    table = pq.read_table(path)
    df = table.to_pydict()
    n = len(df[problem_key])
    items = []
    for i in range(n):
        item = {
            "idx": df.get("problem_idx", list(range(n)))[i],
            "problem": df[problem_key][i],
            "answer": str(df[answer_key][i]),
        }
        for key in (metadata_keys or []):
            if key in df:
                item[key] = df[key][i]
        items.append(item)
    return items


def load_gpqa(path: str, metadata_keys: list[str] | None = None, seed: int = 42) -> list[dict]:
    """Load GPQA CSV with option shuffling.

    Shuffles the 4 options per question with a fixed seed for reproducibility,
    then records which letter (A-D) is correct.
    """
    rng = random.Random(seed)
    items = []
    with open(path) as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader):
            question = row["Question"]
            correct = row["Correct Answer"]
            options = [
                correct,
                row["Incorrect Answer 1"],
                row["Incorrect Answer 2"],
                row["Incorrect Answer 3"],
            ]
            rng.shuffle(options)
            correct_idx = options.index(correct)
            correct_letter = "ABCD"[correct_idx]

            labels = ["A", "B", "C", "D"]
            options_text = "\n".join(f"({labels[j]}) {opt}" for j, opt in enumerate(options))
            full_problem = f"{question}\n\n{options_text}"

            item = {
                "idx": i,
                "problem": full_problem,
                "answer": correct_letter,
            }
            for key in (metadata_keys or []):
                if key in row:
                    item[key] = row[key]
            items.append(item)
    return items


def load_mcqa_jsonl(path: str, metadata_keys: list[str] | None = None) -> list[dict]:
    """Load multiple-choice QA in JSONL format (e.g., MedQA).

    Expects each line to have: question, options (dict {A:..., B:..., ...}), answer_idx (letter).
    """
    items = []
    with open(path) as f:
        for i, line in enumerate(f):
            raw = json.loads(line)
            question = raw["question"]
            options = raw["options"]  # dict like {A: "...", B: "...", ...}
            answer_letter = raw["answer_idx"]

            labels = sorted(options.keys())
            options_text = "\n".join(f"({lbl}) {options[lbl]}" for lbl in labels)
            full_problem = f"{question}\n\n{options_text}"

            item = {
                "idx": i,
                "problem": full_problem,
                "answer": answer_letter,
            }
            for key in (metadata_keys or []):
                if key in raw:
                    item[key] = raw[key]
            items.append(item)
    return items


def load_benchmark(bench_cfg: dict) -> list[dict]:
    """Load a benchmark dataset based on its configuration."""
    fmt = bench_cfg["data_format"]
    path = bench_cfg["path"]

    if not Path(path).exists():
        logger.error(f"Dataset not found: {path}")
        return []

    kwargs = {
        "path": path,
        "problem_key": bench_cfg["problem_key"],
        "answer_key": bench_cfg["answer_key"],
        "metadata_keys": bench_cfg.get("metadata_keys"),
    }

    if fmt == "jsonl":
        return load_jsonl(**kwargs)
    elif fmt == "parquet":
        return load_parquet(**kwargs)
    elif fmt == "gpqa_csv":
        return load_gpqa(path, metadata_keys=bench_cfg.get("metadata_keys"))
    elif fmt == "mcqa_jsonl":
        return load_mcqa_jsonl(path, metadata_keys=bench_cfg.get("metadata_keys"))
    else:
        raise ValueError(f"Unknown data format: {fmt}")
