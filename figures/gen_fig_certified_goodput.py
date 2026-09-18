"""Generate the confirmatory safety/utility figure from the immutable summary."""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


ROOT = Path(__file__).resolve().parents[1]
SUMMARY = json.loads((ROOT / "artifacts" / "confirmatory" / "summary.json").read_text(encoding="utf-8"))
METHODS = [
    ("polygon_unconditional", "Polygon", "#B0BEC5"),
    ("margin_only", "Margin only", "#E69F00"),
    ("global_certificate", "Global cert.", "#0072B2"),
    ("uniform_support_certificate", "Uniform support", "#56B4E9"),
    ("adaptive_support_certificate", "Adaptive support", "#009E73"),
]
FAMILIES = ("blur_crosstalk", "low_photon_bias", "high_mode_na", "sector_dropout", "compound_shift")


def style() -> None:
    plt.rcParams.update(
        {
            "font.family": "serif",
            "font.serif": ["Times New Roman", "DejaVu Serif"],
            "font.size": 9,
            "axes.titlesize": 10,
            "axes.titleweight": "bold",
            "axes.spines.top": False,
            "axes.spines.right": False,
            "axes.grid": True,
            "grid.alpha": 0.15,
            "savefig.dpi": 300,
            "savefig.bbox": "tight",
        }
    )


def main() -> None:
    style()
    fig, axes = plt.subplots(1, 3, figsize=(6.75, 2.65), gridspec_kw={"width_ratios": [1.0, 0.95, 1.15]})
    overall = SUMMARY["overall"]

    ax = axes[0]
    offsets = {
        "polygon_unconditional": (-34, 6),
        "margin_only": (5, 6),
        "global_certificate": (3, 9),
        "uniform_support_certificate": (3, 21),
        "adaptive_support_certificate": (3, 33),
    }
    for key, label, color in METHODS:
        metrics = overall[key]
        ax.scatter(metrics["coverage"] * 100, metrics["false_release_probability"] * 100, s=45 if key == "adaptive_support_certificate" else 30, color=color, edgecolor="white", linewidth=0.6, zorder=3)
        ax.annotate(
            label,
            (metrics["coverage"] * 100, metrics["false_release_probability"] * 100),
            xytext=offsets[key],
            textcoords="offset points",
            fontsize=6.3,
            color="#34454E",
            arrowprops={"arrowstyle": "-", "color": "#A8B5B0", "linewidth": 0.55},
        )
    ax.axhspan(0, 1, color="#009E73", alpha=0.08)
    ax.axhline(1, color="#009E73", linestyle="--", linewidth=0.9)
    ax.set_xlim(0, 105)
    ax.set_ylim(-0.8, 40)
    ax.set_xlabel("Coverage (%)")
    ax.set_ylabel("False release / all trials (%)")
    ax.set_title("a  Safety–coverage plane", loc="left")
    ax.text(101, 1.65, "T2 PASS · upper 0.538%", color="#008A65", fontsize=6.6, ha="right")

    ax = axes[1]
    plot_methods = list(reversed(METHODS[1:]))
    values = [overall[key]["certified_goodput"] for key, _, _ in plot_methods]
    bars = ax.barh(np.arange(len(plot_methods)), values, color=[color for _, _, color in plot_methods], height=0.58)
    ax.set_yticks(np.arange(len(plot_methods)), [label for _, label, _ in plot_methods], fontsize=7)
    ax.set_xlabel("Correct released bits / acquisition")
    ax.set_xlim(0, max(values) * 1.28)
    ax.set_title("b  Certified goodput", loc="left")
    for bar, value in zip(bars, values, strict=True):
        ax.text(value + 0.01, bar.get_y() + bar.get_height() / 2, f"{value:.3f}", va="center", fontsize=7)
    ax.text(0.98, 0.04, "T3 PASS · +200%", transform=ax.transAxes, ha="right", color="#008A65", fontsize=7, fontweight="bold")

    ax = axes[2]
    x = np.arange(len(FAMILIES))
    width = 0.34
    global_values = [SUMMARY["by_family"][family]["global_certificate"]["certified_goodput"] for family in FAMILIES]
    adaptive_values = [SUMMARY["by_family"][family]["adaptive_support_certificate"]["certified_goodput"] for family in FAMILIES]
    ax.bar(x - width / 2, global_values, width, color="#8AA4B0", label="Global certificate")
    ax.bar(x + width / 2, adaptive_values, width, color="#009E73", label="Adaptive support")
    ax.set_xticks(x, ["blur ×\ncross", "photon ×\nbias", "mode ×\nNA", "sector\ndropout", "compound"], fontsize=6.2)
    ax.set_ylabel("Certified goodput")
    ax.set_title("c  Held-out compositions", loc="left")
    ax.legend(fontsize=6.5, loc="upper right")
    ax.text(0.98, 0.04, "T4 FAIL · 32 pp coverage cost", transform=ax.transAxes, ha="right", va="bottom", color="#D55E00", fontsize=6.5, fontweight="bold")

    fig.suptitle("TopoSense-Sim: adaptive certification improves goodput without a confirmatory wrong release", fontsize=9.6, fontweight="bold", y=0.965)
    fig.subplots_adjust(left=0.075, right=0.985, bottom=0.25, top=0.79, wspace=0.38)
    fig.savefig(ROOT / "figures" / "fig_certified_goodput.pdf")
    fig.savefig(ROOT / "figures" / "fig_certified_goodput.png", dpi=300)
    plt.close(fig)


if __name__ == "__main__":
    main()
