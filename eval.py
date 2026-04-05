#!/usr/bin/env python3
"""
LIMO-SFT Evaluation Script

Evaluates LLMs on math reasoning benchmarks with:
- OpenAI-compatible API (vLLM / dashscope / etc.)
- Config-driven benchmarks, prompts, and inference params
- CoT and Direct inference modes
- Robust answer extraction and grading
- Async concurrent evaluation with resume support

Usage:
    python eval.py                                  # use default config
    python eval.py --config configs/eval_config.yaml
    python eval.py --benchmarks math500 aime_2025   # run specific benchmarks
    python eval.py --model qwen-turbo               # override model
    python eval.py --mode direct                    # override inference mode
"""

import argparse
import asyncio
import json
import logging
import time
from datetime import datetime
from pathlib import Path

import yaml

from lib.client import LLMClient, InferenceConfig
from lib.loader import load_benchmark
from lib.extractor import extract_answer
from lib.grader import grade

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)


def build_prompt(problem: str, instruction: str) -> str:
    """Build the user prompt from problem text and instruction."""
    return f"{instruction}\n\n{problem}"


def load_existing_results(result_path: Path) -> dict[str, dict]:
    """Load previously saved results for resume support."""
    if not result_path.exists():
        return {}
    results = {}
    with open(result_path) as f:
        for line in f:
            entry = json.loads(line)
            key = str(entry.get("idx", ""))
            results[key] = entry
    return results


async def evaluate_benchmark(
    bench_name: str,
    bench_cfg: dict,
    client: LLMClient,
    mode: str,
    output_dir: Path,
    save_responses: bool,
    resume: bool,
) -> dict:
    """Evaluate a single benchmark and return metrics."""
    logger.info(f"=== Evaluating {bench_cfg['name']} ({bench_name}) ===")

    # Load data
    data = load_benchmark(bench_cfg)
    if not data:
        logger.error(f"No data loaded for {bench_name}, skipping")
        return {}

    logger.info(f"  Loaded {len(data)} problems")

    # Select instruction based on mode
    instruction_key = f"instruction_{mode}"
    instruction = bench_cfg.get(instruction_key, bench_cfg.get("instruction_cot", ""))
    system_prompt = bench_cfg.get("system_prompt", "")
    answer_type = bench_cfg["answer_type"]

    # Output files
    bench_output_dir = output_dir / bench_name
    bench_output_dir.mkdir(parents=True, exist_ok=True)
    result_path = bench_output_dir / "results.jsonl"
    metrics_path = bench_output_dir / "metrics.json"

    # Resume: load existing results
    existing = load_existing_results(result_path) if resume else {}
    if existing:
        logger.info(f"  Resuming: {len(existing)} problems already evaluated")

    # Build prompts for unevaluated problems
    to_eval = []
    for item in data:
        key = str(item["idx"])
        if key not in existing:
            to_eval.append(item)

    if not to_eval:
        logger.info(f"  All problems already evaluated, loading cached results")
    else:
        logger.info(f"  Evaluating {len(to_eval)} problems (mode={mode})")

        # Generate responses
        prompts = [
            (system_prompt, build_prompt(item["problem"], instruction))
            for item in to_eval
        ]
        responses = await client.generate_batch(prompts)

        # Process results and append to file
        with open(result_path, "a") as f:
            for item, response in zip(to_eval, responses):
                predicted = extract_answer(response, answer_type)
                correct = grade(predicted, item["answer"], answer_type)

                entry = {
                    "idx": item["idx"],
                    "problem": item["problem"][:200] + "..." if len(item["problem"]) > 200 else item["problem"],
                    "gold_answer": item["answer"],
                    "predicted": predicted,
                    "correct": correct,
                }
                if save_responses:
                    entry["response"] = response

                # Include metadata
                for key in bench_cfg.get("metadata_keys", []):
                    if key in item:
                        entry[key] = item[key]

                f.write(json.dumps(entry, ensure_ascii=False) + "\n")
                existing[str(item["idx"])] = entry

    # Compute metrics
    all_results = list(existing.values())
    total = len(all_results)
    correct = sum(1 for r in all_results if r.get("correct", False))
    accuracy = correct / total if total > 0 else 0.0

    metrics = {
        "benchmark": bench_cfg["name"],
        "total": total,
        "correct": correct,
        "accuracy": accuracy,
        "accuracy_pct": f"{accuracy * 100:.1f}%",
        "mode": mode,
        "model": client.model,
    }

    # Per-category breakdown if metadata available
    for meta_key in bench_cfg.get("metadata_keys", []):
        categories = {}
        for r in all_results:
            cat = r.get(meta_key, "unknown")
            if cat not in categories:
                categories[cat] = {"total": 0, "correct": 0}
            categories[cat]["total"] += 1
            if r.get("correct", False):
                categories[cat]["correct"] += 1
        if categories:
            breakdown = {}
            for cat, counts in sorted(categories.items()):
                acc = counts["correct"] / counts["total"] if counts["total"] > 0 else 0
                breakdown[cat] = f"{counts['correct']}/{counts['total']} ({acc*100:.1f}%)"
            metrics[f"breakdown_by_{meta_key}"] = breakdown

    # Save metrics
    with open(metrics_path, "w") as f:
        json.dump(metrics, f, indent=2, ensure_ascii=False)

    logger.info(f"  Result: {correct}/{total} = {accuracy*100:.1f}%")
    return metrics


async def main():
    parser = argparse.ArgumentParser(description="LIMO-SFT Math Benchmark Evaluation")
    parser.add_argument("--config", default="configs/eval_config.yaml", help="Path to config YAML")
    parser.add_argument("--benchmarks", nargs="*", help="Specific benchmarks to run (keys from config)")
    parser.add_argument("--model", help="Override model name")
    parser.add_argument("--mode", choices=["cot", "direct"], help="Override inference mode")
    parser.add_argument("--base-url", help="Override API base URL")
    parser.add_argument("--api-key", help="Override API key")
    parser.add_argument("--max-tokens", type=int, help="Override max tokens")
    parser.add_argument("--temperature", type=float, help="Override temperature")
    parser.add_argument("--max-concurrency", type=int, help="Override max concurrency")
    parser.add_argument("--no-resume", action="store_true", help="Disable resume, re-evaluate all")
    args = parser.parse_args()

    # Load config
    with open(args.config) as f:
        config = yaml.safe_load(f)

    # Apply CLI overrides
    api_cfg = config["api"]
    inf_cfg = config["inference"]
    eval_cfg = config["eval"]

    if args.model:
        api_cfg["model"] = args.model
    if args.mode:
        inf_cfg["mode"] = args.mode
    if args.base_url:
        api_cfg["base_url"] = args.base_url
    if args.api_key:
        api_cfg["api_key"] = args.api_key
    # Fallback to environment variable
    import os
    if api_cfg.get("api_key", "").startswith("your-"):
        api_cfg["api_key"] = os.environ.get("OPENAI_API_KEY", api_cfg["api_key"])
    if args.max_tokens:
        inf_cfg["max_tokens"] = args.max_tokens
    if args.temperature is not None:
        inf_cfg["temperature"] = args.temperature
    if args.max_concurrency:
        inf_cfg["max_concurrency"] = args.max_concurrency
    if args.no_resume:
        eval_cfg["resume"] = False

    mode = inf_cfg["mode"]

    # Build run tag for output directory
    model_tag = api_cfg["model"].replace("/", "_")
    run_tag = f"{model_tag}_{mode}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    output_dir = Path(eval_cfg["output_dir"]) / run_tag
    output_dir.mkdir(parents=True, exist_ok=True)

    # Save run config
    with open(output_dir / "config.yaml", "w") as f:
        yaml.dump(config, f, default_flow_style=False, allow_unicode=True)

    logger.info(f"Model: {api_cfg['model']}")
    logger.info(f"Mode: {mode}")
    logger.info(f"Output: {output_dir}")

    # Initialize client
    inf = InferenceConfig(
        max_tokens=inf_cfg["max_tokens"],
        temperature=inf_cfg["temperature"],
        top_p=inf_cfg.get("top_p", 1.0),
        n_samples=inf_cfg.get("n_samples", 1),
        timeout=inf_cfg.get("timeout", 120),
        max_concurrency=inf_cfg.get("max_concurrency", 8),
        max_retries=inf_cfg.get("max_retries", 3),
    )
    client = LLMClient(
        base_url=api_cfg["base_url"],
        api_key=api_cfg["api_key"],
        model=api_cfg["model"],
        config=inf,
    )

    # Select benchmarks to run
    all_benchmarks = config["benchmarks"]
    if args.benchmarks:
        selected = {k: v for k, v in all_benchmarks.items() if k in args.benchmarks}
    else:
        selected = {k: v for k, v in all_benchmarks.items() if v.get("enabled", True)}

    logger.info(f"Benchmarks: {list(selected.keys())}")

    # Run evaluations
    all_metrics = {}
    start_time = time.time()

    for bench_name, bench_cfg in selected.items():
        metrics = await evaluate_benchmark(
            bench_name=bench_name,
            bench_cfg=bench_cfg,
            client=client,
            mode=mode,
            output_dir=output_dir,
            save_responses=eval_cfg.get("save_responses", True),
            resume=eval_cfg.get("resume", True),
        )
        if metrics:
            all_metrics[bench_name] = metrics

    elapsed = time.time() - start_time

    # Print summary table
    print("\n" + "=" * 70)
    print(f"  Evaluation Summary — {api_cfg['model']} ({mode})")
    print("=" * 70)
    print(f"  {'Benchmark':<25} {'Correct':>8} {'Total':>6} {'Accuracy':>10}")
    print("-" * 70)

    total_correct = 0
    total_problems = 0
    for name, m in all_metrics.items():
        print(f"  {m['benchmark']:<25} {m['correct']:>8} {m['total']:>6} {m['accuracy_pct']:>10}")
        total_correct += m["correct"]
        total_problems += m["total"]

    if total_problems > 0:
        avg_acc = total_correct / total_problems
        print("-" * 70)
        print(f"  {'OVERALL':<25} {total_correct:>8} {total_problems:>6} {avg_acc*100:>9.1f}%")

    print("=" * 70)
    print(f"  Time: {elapsed:.1f}s | Output: {output_dir}")
    print()

    # Save summary
    summary = {
        "model": api_cfg["model"],
        "mode": mode,
        "timestamp": datetime.now().isoformat(),
        "elapsed_seconds": round(elapsed, 1),
        "overall": {
            "correct": total_correct,
            "total": total_problems,
            "accuracy": round(total_correct / total_problems, 4) if total_problems > 0 else 0,
        },
        "benchmarks": all_metrics,
    }
    with open(output_dir / "summary.json", "w") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)


if __name__ == "__main__":
    asyncio.run(main())
