"""Dataset loaders for various benchmark formats."""

import json
import logging
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
    else:
        raise ValueError(f"Unknown data format: {fmt}")
