"""Visualize an exact wrong-polygon seed and its active certificate evidence."""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from toposense_sim.certificate import certify_observation, evaluate_baseline
from toposense_sim.field import synthesize_field
from toposense_sim.receiver import acquire_adaptive, acquire_uniform


ROOT = Path(__file__).resolve().parents[1]
SEED, FAMILY = 1004, "blur_crosstalk"


def main() -> None:
    plt.rcParams.update({"font.family": "serif", "font.serif": ["Times New Roman", "DejaVu Serif"], "font.size": 8, "savefig.dpi": 300})
    field = synthesize_field(SEED, FAMILY)
    uniform = acquire_uniform(SEED, FAMILY, field=field)
    adaptive = acquire_adaptive(SEED, FAMILY, field=field)
    polygon = evaluate_baseline(uniform, "polygon_unconditional")
    certificate = certify_observation(adaptive)
    fig = plt.figure(figsize=(6.75, 2.82))
    grid = fig.add_gridspec(1, 3, width_ratios=[1.0, 1.0, 1.1], wspace=0.36)

    ax = fig.add_subplot(grid[0], projection="3d")
    u = np.linspace(0, 2 * np.pi, 40); v = np.linspace(0, np.pi, 20)
    ax.plot_wireframe(np.outer(np.cos(u), np.sin(v)), np.outer(np.sin(u), np.sin(v)), np.outer(np.ones_like(u), np.cos(v)), color="#CBD5D1", alpha=0.18, linewidth=0.35)
    stride = 10
    ax.plot(*field.ideal_stokes[::stride].T, color="#0072B2", linewidth=1.6, label=f"ideal w={field.true_winding}")
    ax.plot(*field.received_stokes[::stride].T, color="#D55E00", linewidth=1.4, label=f"received w={field.received_dense_winding}")
    ax.scatter(*adaptive.stokes.T, color="#009E73", s=7, depthshade=False)
    ax.set_box_aspect((1, 1, 1)); ax.set_axis_off(); ax.view_init(24, 42)
    ax.set_title("a  Poincaré evidence", loc="left", pad=-2, fontweight="bold")
    ax.legend(loc="lower center", fontsize=6, frameon=False)

    ax = fig.add_subplot(grid[1])
    ideal_z = field.ideal_stokes[:, 0] + 1j * field.ideal_stokes[:, 1]
    received_z = field.received_stokes[:, 0] + 1j * field.received_stokes[:, 1]
    measured_z = uniform.stokes[:, 0] + 1j * uniform.stokes[:, 1]
    ax.plot(ideal_z.real, ideal_z.imag, color="#0072B2", linewidth=1.5, label="ideal dense")
    ax.plot(received_z.real, received_z.imag, color="#D55E00", linewidth=1.3, label="received dense")
    ax.plot(np.r_[measured_z.real, measured_z.real[0]], np.r_[measured_z.imag, measured_z.imag[0]], "o-", color="#6B7280", markersize=2, linewidth=0.7, label="32-point polygon")
    ax.scatter([0], [0], marker="+", s=45, color="black", linewidth=1)
    ax.axhline(0, color="#D6DDDA", linewidth=.5); ax.axvline(0, color="#D6DDDA", linewidth=.5)
    ax.set_aspect("equal"); ax.set_xlabel("S1"); ax.set_ylabel("S2")
    ax.set_title("b  Projected winding", loc="left", fontweight="bold")
    ax.legend(fontsize=5.8, frameon=False, loc="lower left")
    ax.text(0.02, .98, f"polygon releases {polygon.winding}\ntruth is {field.true_winding}", transform=ax.transAxes, va="top", color="#D55E00", fontsize=6.6, fontweight="bold")

    ax = fig.add_subplot(grid[2], projection="polar")
    initial = np.linspace(0, 2 * np.pi, 12, endpoint=False) + (SEED % 13) / 13 * 2 * np.pi / 12
    ax.scatter(initial, np.ones_like(initial), s=18, color="#8AA4B0", label="12 initial")
    extra_mask = np.array([np.min(np.abs((angle - initial + np.pi) % (2 * np.pi) - np.pi)) > 1e-6 for angle in adaptive.nominal_angles])
    ax.scatter(adaptive.nominal_angles[extra_mask], np.ones(np.sum(extra_mask)) * 0.72, s=18, color="#009E73", label="risk-directed additions")
    projected = adaptive.stokes[:, 0] + 1j * adaptive.stokes[:, 1]
    risk = 1.0 - np.clip(np.abs(projected), 0, 1)
    ax.scatter(adaptive.nominal_angles, 0.25 + 0.3 * risk, s=8, color="#E69F00", alpha=.75, label="observed risk")
    ax.set_rticks([]); ax.set_theta_zero_location("N"); ax.set_theta_direction(-1)
    ax.grid(alpha=.2); ax.spines["polar"].set_alpha(.25)
    ax.set_title("c  Equal-budget active sampling", loc="left", pad=7, fontweight="bold")
    ax.legend(loc="center left", bbox_to_anchor=(1.02, .48), fontsize=5.7, frameon=False)
    ax.text(.5, .5, f"{certificate.decision.value}\nmargin {certificate.certificate_margin:.3f}", transform=ax.transAxes, ha="center", va="center", fontsize=7, color="#7B4F00")

    fig.suptitle("Exact confirmatory seed 1004: integer-looking output is not self-certifying", fontsize=9.4, fontweight="bold", y=0.975)
    fig.subplots_adjust(top=0.80, bottom=0.17)
    fig.savefig(ROOT / "figures" / "fig_receiver_evidence.pdf", bbox_inches="tight")
    fig.savefig(ROOT / "figures" / "fig_receiver_evidence.png", dpi=300, bbox_inches="tight")
    plt.close(fig)


if __name__ == "__main__":
    main()
