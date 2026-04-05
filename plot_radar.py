#!/usr/bin/env python3
"""Plot radar chart comparing model performance across benchmarks."""

import json
import sys
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path


def load_results(path: str) -> dict:
    with open(path) as f:
        return json.load(f)


def plot_radar(results_list: list[tuple[str, dict]], output_path: str = "radar.png"):
    """Plot radar chart from one or more result summaries.

    Args:
        results_list: List of (label, summary_dict) tuples.
        output_path: Where to save the figure.
    """
    # Collect all benchmark names (use first result as reference)
    bench_keys = list(results_list[0][1]["benchmarks"].keys())
    bench_names = [results_list[0][1]["benchmarks"][k]["benchmark"] for k in bench_keys]

    n = len(bench_names)
    angles = np.linspace(0, 2 * np.pi, n, endpoint=False).tolist()
    angles += angles[:1]  # close the polygon

    fig, ax = plt.subplots(figsize=(8, 8), subplot_kw=dict(polar=True))

    colors = ["#2563eb", "#dc2626", "#16a34a", "#f59e0b", "#8b5cf6"]

    for i, (label, summary) in enumerate(results_list):
        values = []
        for k in bench_keys:
            if k in summary["benchmarks"]:
                values.append(summary["benchmarks"][k]["accuracy"] * 100)
            else:
                values.append(0)
        values += values[:1]  # close

        color = colors[i % len(colors)]
        ax.plot(angles, values, "o-", linewidth=2, label=label, color=color)
        ax.fill(angles, values, alpha=0.1, color=color)

    ax.set_thetagrids(np.degrees(angles[:-1]), bench_names, fontsize=10)
    ax.set_ylim(0, 100)
    ax.set_yticks([20, 40, 60, 80, 100])
    ax.set_yticklabels(["20%", "40%", "60%", "80%", "100%"], fontsize=8, color="grey")
    ax.set_rlabel_position(30)

    # Add value labels
    for i, (label, summary) in enumerate(results_list):
        values = []
        for k in bench_keys:
            if k in summary["benchmarks"]:
                values.append(summary["benchmarks"][k]["accuracy"] * 100)
            else:
                values.append(0)
        for angle, val in zip(angles[:-1], values):
            ax.annotate(
                f"{val:.1f}",
                xy=(angle, val),
                fontsize=7,
                ha="center",
                va="bottom",
                color="grey",
            )

    ax.legend(loc="upper right", bbox_to_anchor=(1.3, 1.1), fontsize=10)
    ax.set_title("Math Reasoning Benchmark Evaluation", y=1.08, fontsize=14, fontweight="bold")

    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches="tight")
    print(f"Saved to {output_path}")


if __name__ == "__main__":
    result_paths = sys.argv[1:] if len(sys.argv) > 1 else list(Path("results").glob("*/summary.json"))

    results_list = []
    for p in result_paths:
        p = Path(p)
        summary = load_results(p)
        label = summary.get("model", p.parent.name)
        results_list.append((label, summary))

    if not results_list:
        print("No results found. Pass summary.json paths as arguments or put them in results/*/summary.json")
        sys.exit(1)

    plot_radar(results_list, "results/radar.png")
