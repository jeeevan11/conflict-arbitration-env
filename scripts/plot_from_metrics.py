"""
Plot training curves from a real metrics.json produced by training/train.py.

Usage:
    python3 scripts/plot_from_metrics.py [metrics.json] [output.png]

Defaults: ./metrics.json -> ./training_curves.png

The metrics.json schema (see training/metrics.py) is:
{
    "step": [...],
    "arbitration_accuracy": [...],
    "merge_success_rate": [...],
    "avg_reward": [...],
    "curriculum_phase": [...],
    "conflict_detection_rate": [...],
    "false_alarm_rate": [...],
    "wrong_agent_rate": [...]
}
"""
import json
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


def rolling_mean(arr, window):
    arr = np.asarray(arr, dtype=float)
    if len(arr) == 0:
        return arr
    if len(arr) < window:
        return arr
    out = np.empty_like(arr)
    cumsum = np.cumsum(np.insert(arr, 0, 0))
    for i in range(len(arr)):
        lo = max(0, i - window + 1)
        out[i] = (cumsum[i + 1] - cumsum[lo]) / (i - lo + 1)
    return out


def main(metrics_path: str = "metrics.json", out_path: str = "training_curves.png"):
    if not Path(metrics_path).exists():
        sys.exit(f"metrics.json not found at {metrics_path}")
    with open(metrics_path) as f:
        h = json.load(f)

    steps = np.asarray(h.get("step", []))
    if len(steps) == 0:
        sys.exit("metrics.json is empty (no step entries yet)")

    accs = np.asarray(h.get("arbitration_accuracy", [])) * 100
    rewards = np.asarray(h.get("avg_reward", []))
    merge = np.asarray(h.get("merge_success_rate", [])) * 100
    phases = np.asarray(h.get("curriculum_phase", []))

    plt.style.use("dark_background")
    fig, axes = plt.subplots(2, 2, figsize=(14, 9))
    fig.suptitle(
        f"Conflict Arbitration Agent - Training Progress  ({len(steps)} steps logged)",
        fontsize=14, fontweight="bold", color="#e6e6f0",
    )

    # 1. Reward
    ax = axes[0, 0]
    ax.scatter(steps, rewards, alpha=0.3, c="#8be9d6", s=15, label="per-step reward")
    if len(rewards) >= 20:
        ax.plot(steps, rolling_mean(rewards, 20), color="#ff79c6", linewidth=2.5,
                label="rolling avg (window=20)")
    ax.axhline(0, color="#444", linestyle="--", linewidth=1, alpha=0.6)
    ax.set_title("Average reward over time", color="#e6e6f0")
    ax.set_xlabel("Training step")
    ax.set_ylabel("Reward")
    ax.legend(loc="lower right", framealpha=0.3)
    ax.grid(True, alpha=0.15)

    # 2. Accuracy
    ax = axes[0, 1]
    ax.scatter(steps, accs, alpha=0.3, c="#50fa7b", s=15, label="per-step accuracy")
    if len(accs) >= 20:
        ax.plot(steps, rolling_mean(accs, 20), color="#f1fa8c", linewidth=2.5,
                label="rolling avg (window=20)")
    ax.axhline(33.3, color="#ff5555", linestyle="--", linewidth=1.5, alpha=0.7,
               label="random baseline (33.3%)")
    ax.set_title("Arbitration accuracy over time", color="#e6e6f0")
    ax.set_xlabel("Training step")
    ax.set_ylabel("Accuracy (%)")
    ax.set_ylim(-5, 105)
    ax.legend(loc="lower right", framealpha=0.3)
    ax.grid(True, alpha=0.15)

    # 3. Merge success rate
    ax = axes[1, 0]
    if len(merge) > 0:
        ax.scatter(steps, merge, alpha=0.3, c="#bd93f9", s=15, label="per-step")
        if len(merge) >= 20:
            ax.plot(steps, rolling_mean(merge, 20), color="#ffb86c", linewidth=2.5,
                    label="rolling avg (window=20)")
        ax.set_title("Merge success rate", color="#e6e6f0")
        ax.set_xlabel("Training step")
        ax.set_ylabel("Success (%)")
        ax.set_ylim(-5, 105)
        ax.legend(loc="lower right", framealpha=0.3)
        ax.grid(True, alpha=0.15)
    else:
        ax.axis("off")

    # 4. Summary stats
    ax = axes[1, 1]
    ax.axis("off")
    n = len(steps)
    head = max(1, min(100, n // 4))
    tail = max(1, min(100, n // 4))

    head_r = float(np.mean(rewards[:head]))
    tail_r = float(np.mean(rewards[-tail:]))
    head_a = float(np.mean(accs[:head]))
    tail_a = float(np.mean(accs[-tail:]))
    pos = int((rewards > 0).sum())
    above = int((accs > 33.3).sum())

    phase_summary = ""
    if len(phases) > 0:
        unique, counts = np.unique(phases, return_counts=True)
        phase_summary = "\nPHASE TIME\n" + "\n".join(
            f"  Phase {int(p)}: {int(c)} steps  ({100*c/n:.0f}%)"
            for p, c in zip(unique, counts)
        )

    text = f"""TRAINING SUMMARY
{'='*40}
Steps logged:       {n}
First step / Last:  {int(steps[0])} / {int(steps[-1])}

REWARD
  First {head} mean:  {head_r:+.2f}
  Last {tail} mean:   {tail_r:+.2f}
  Improvement:        {tail_r - head_r:+.2f}
  Best:               {float(rewards.max()):+.2f} (step {int(steps[int(np.argmax(rewards))])})
  Positive steps:     {pos} / {n}  ({100*pos/n:.0f}%)

ACCURACY
  First {head} mean:  {head_a:.1f}%
  Last {tail} mean:   {tail_a:.1f}%
  Best:               {float(accs.max()):.1f}%
  Above-chance:       {above} / {n}  ({100*above/n:.0f}%)
  Random baseline:    33.3%
{phase_summary}
"""
    ax.text(0.02, 0.98, text, transform=ax.transAxes, fontsize=10,
            verticalalignment="top", fontfamily="monospace", color="#c8c8e8")

    plt.tight_layout()
    plt.savefig(out_path, dpi=150, bbox_inches="tight", facecolor="#0a0a14")
    print(f"Saved {out_path}")
    print(f"\nFirst-{head} reward: {head_r:+.3f}   Last-{tail} reward: {tail_r:+.3f}   delta: {tail_r-head_r:+.3f}")
    print(f"First-{head} acc:    {head_a:.2f}%   Last-{tail} acc:    {tail_a:.2f}%   delta: {tail_a-head_a:+.2f}pp")


if __name__ == "__main__":
    metrics = sys.argv[1] if len(sys.argv) > 1 else "metrics.json"
    out = sys.argv[2] if len(sys.argv) > 2 else "training_curves.png"
    main(metrics, out)
