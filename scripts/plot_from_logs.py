"""
Plot training curves from REAL per-step lines emitted by the running HF Job.

Every datapoint below appears verbatim in the live job log stream
(https://huggingface.co/jobs/testingaccc/69ecfb45d70108f37acdeb50).
Nothing is interpolated, smoothed in, or fabricated.

Once the final metrics.json uploads at end of training, prefer
scripts/plot_from_metrics.py — it reads the full per-step history
straight from the model repo.
"""
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

# (step, reward, accuracy_percent) — REAL log lines, in order.
DATA = [
    (0, -2.50, 50.00), (1, -3.74, 37.50), (2, 5.43, 62.50),
    (3, 1.50, 37.50), (4, -2.74, 25.00),
    (10, -1.20, 37.50), (20, -2.25, 25.00), (30, -1.27, 37.50),
    (40, -2.50, 50.00), (50, 0.56, 50.00), (60, 5.10, 37.50),
    (70, -2.94, 25.00), (80, 0.25, 62.50), (90, -7.15, 12.50),
    (100, -3.45, 37.50), (110, 0.38, 37.50), (120, -4.83, 12.50),
    (130, -1.62, 50.00), (140, -4.38, 37.50), (150, -3.99, 37.50),
    (160, -3.34, 25.00), (170, 1.38, 50.00), (180, -8.07, 12.50),
    (190, 0.50, 50.00), (200, 2.62, 62.50), (210, -2.99, 25.00),
    (220, -2.00, 25.00), (230, -7.99, 12.50), (240, 1.50, 50.00),
    (250, 11.63, 62.50), (260, -2.47, 25.00), (280, -1.21, 37.50),
    (290, 5.50, 62.50), (300, -2.33, 25.00), (310, -4.12, 37.50),
    (320, 5.31, 50.00), (330, -2.45, 50.00), (340, 0.81, 50.00),
    (350, 3.23, 62.50), (360, -0.62, 62.50), (370, 2.62, 37.50),
    (380, 8.62, 62.50), (390, 8.85, 62.50), (400, 3.55, 50.00),
    (410, -3.25, 37.50), (420, -6.20, 25.00), (430, 1.78, 37.50),
    (440, -5.33, 25.00), (450, 2.40, 62.50),
    (1200, 1.82, 37.50), (1210, -1.38, 37.50), (1220, -0.10, 25.00),
    (1230, -1.35, 37.50), (1240, -3.06, 25.00), (1250, -3.19, 25.00),
    (1260, -7.88, 12.50), (1270, 1.88, 37.50), (1280, 3.92, 50.00),
    (1290, -3.24, 25.00), (1300, 6.70, 50.00), (1310, -3.17, 25.00),
    (1320, 5.65, 62.50), (1330, 2.50, 62.50), (1340, -6.25, 25.00),
    (1350, -6.25, 25.00), (1360, -6.25, 25.00), (1370, 2.25, 62.50),
    (1380, -4.88, 25.00), (1390, -6.15, 25.00), (1400, 0.86, 25.00),
    (1410, 3.62, 50.00), (1420, -1.38, 37.50), (1430, -6.17, 25.00),
    (1710, -4.38, 37.50), (1720, -7.75, 12.50), (1730, -0.48, 37.50),
    (1740, -1.25, 37.50), (1750, -1.25, 37.50), (1760, -0.35, 37.50),
    (1770, 8.77, 62.50), (1780, 2.51, 62.50), (1790, 0.06, 25.00),
    (1800, 0.76, 50.00), (1810, 5.68, 62.50), (1820, 1.50, 50.00),
    (1830, -7.03, 12.50), (1840, 0.62, 50.00), (1850, -7.79, 12.50),
    (1860, 0.48, 50.00), (1870, -2.88, 25.00), (1880, 0.75, 50.00),
    (1890, -9.93, 0.00), (1900, -5.12, 25.00), (1910, -2.38, 25.00),
    (1920, -1.25, 37.50), (1930, -3.11, 25.00), (1940, 11.91, 62.50),
    (1950, -9.92, 0.00), (1960, -1.52, 37.50),
]


def rolling_mean(arr, window):
    arr = np.asarray(arr, dtype=float)
    if len(arr) < window:
        return arr
    out = np.empty_like(arr)
    cs = np.cumsum(np.insert(arr, 0, 0))
    for i in range(len(arr)):
        lo = max(0, i - window + 1)
        out[i] = (cs[i + 1] - cs[lo]) / (i - lo + 1)
    return out


def plot(out_path: str = "training_curves.png"):
    steps = np.array([r[0] for r in DATA])
    rewards = np.array([r[1] for r in DATA])
    accs = np.array([r[2] for r in DATA])

    plt.style.use("dark_background")
    fig, axes = plt.subplots(2, 2, figsize=(14, 9))
    fig.suptitle(
        f"Conflict Arbitration Agent - GRPO training (real per-step data, n={len(steps)})",
        fontsize=14, fontweight="bold", color="#e6e6f0",
    )

    # 1. Reward over time
    ax = axes[0, 0]
    ax.scatter(steps, rewards, alpha=0.5, c="#8be9d6", s=30, label="per-step reward")
    if len(rewards) >= 5:
        ax.plot(steps, rolling_mean(rewards, 5), color="#ff79c6", linewidth=2.5,
                label="rolling avg (window=5)")
    ax.axhline(0, color="#666", linestyle="--", linewidth=1, alpha=0.7)
    ax.set_title("Average reward over training step", color="#e6e6f0")
    ax.set_xlabel("Training step")
    ax.set_ylabel("Reward (mean of 8 GRPO rollouts)")
    ax.legend(loc="lower right", framealpha=0.3)
    ax.grid(True, alpha=0.15)

    # 2. Accuracy over time
    ax = axes[0, 1]
    ax.scatter(steps, accs, alpha=0.5, c="#50fa7b", s=30, label="per-step accuracy")
    if len(accs) >= 5:
        ax.plot(steps, rolling_mean(accs, 5), color="#f1fa8c", linewidth=2.5,
                label="rolling avg (window=5)")
    ax.axhline(33.3, color="#ff5555", linestyle="--", linewidth=1.5, alpha=0.7,
               label="random baseline (33.3%)")
    ax.set_title("Arbitration accuracy over training step", color="#e6e6f0")
    ax.set_xlabel("Training step")
    ax.set_ylabel("Accuracy (%)")
    ax.set_ylim(-5, 105)
    ax.legend(loc="lower right", framealpha=0.3)
    ax.grid(True, alpha=0.15)

    # 3. Reward distribution: early vs late
    ax = axes[1, 0]
    early_mask = steps <= 500
    late_mask = steps >= 1700
    bins = np.linspace(rewards.min() - 0.5, rewards.max() + 0.5, 16)
    ax.hist(rewards[early_mask], bins=bins, alpha=0.6, color="#ff5555",
            label=f"early steps 0-450 (n={int(early_mask.sum())})")
    ax.hist(rewards[late_mask], bins=bins, alpha=0.6, color="#50fa7b",
            label=f"late steps 1710-1960 (n={int(late_mask.sum())})")
    ax.axvline(rewards[early_mask].mean(), color="#ff5555", linestyle="--", linewidth=2,
               label=f"early mean = {rewards[early_mask].mean():+.2f}")
    ax.axvline(rewards[late_mask].mean(), color="#50fa7b", linestyle="--", linewidth=2,
               label=f"late mean  = {rewards[late_mask].mean():+.2f}")
    ax.set_title("Reward distribution: early vs late training", color="#e6e6f0")
    ax.set_xlabel("Reward")
    ax.set_ylabel("Frequency")
    ax.legend(loc="upper left", framealpha=0.3, fontsize=9)
    ax.grid(True, alpha=0.15)

    # 4. Summary stats
    ax = axes[1, 1]
    ax.axis("off")
    early_r = rewards[early_mask]
    late_r = rewards[late_mask]
    early_a = accs[early_mask]
    late_a = accs[late_mask]
    pos = int((rewards > 0).sum())
    above_chance = int((accs > 33.3).sum())
    text = f"""TRAINING SUMMARY (real log data, no interpolation)
{'='*46}
Datapoints logged:        {len(steps)}
Step range covered:       {steps[0]} -> {steps[-1]}
Curriculum phase:         1 throughout
Hardware:                 A10G-small via HF Jobs
Job ID:                   69ecfb45d70108f37acdeb50

REWARD
  Early (steps 0-450):       mean {early_r.mean():+.2f}
  Late  (steps 1710-1960):   mean {late_r.mean():+.2f}
  Improvement (late-early):  {late_r.mean() - early_r.mean():+.2f}
  Best step:                 {rewards.max():+.2f} (step {steps[int(np.argmax(rewards))]})
  Worst step:                {rewards.min():+.2f} (step {steps[int(np.argmin(rewards))]})
  Positive-reward steps:     {pos}/{len(rewards)} ({100*pos/len(rewards):.0f}%)

ACCURACY
  Early (steps 0-450):       mean {early_a.mean():.1f}%
  Late  (steps 1710-1960):   mean {late_a.mean():.1f}%
  Best:                      {accs.max():.1f}%
  Random baseline:           33.3%
  Above-chance steps:        {above_chance}/{len(accs)} ({100*above_chance/len(accs):.0f}%)

NOTES
  - High reward variance is expected: 8 stochastic rollouts/step
    at temperature 0.9 with sparse, contrastive reward.
  - Curriculum did not advance to phase 2; threshold was 70%.
  - Final per-step metrics.json will overwrite this on completion.
"""
    ax.text(0.0, 0.98, text, transform=ax.transAxes, fontsize=9,
            verticalalignment="top", fontfamily="monospace", color="#c8c8e8")

    plt.tight_layout()
    plt.savefig(out_path, dpi=150, bbox_inches="tight", facecolor="#0a0a14")
    print(f"saved {out_path}  ({len(steps)} real datapoints)")

    # CLI summary
    print(f"early reward mean: {early_r.mean():+.3f}")
    print(f"late  reward mean: {late_r.mean():+.3f}")
    print(f"early acc mean:    {early_a.mean():.2f}%")
    print(f"late  acc mean:    {late_a.mean():.2f}%")
    print(f"random baseline:   33.30%")


if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else "training_curves.png"
    plot(out)
