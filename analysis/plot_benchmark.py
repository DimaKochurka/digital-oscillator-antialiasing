from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt

PROJECT_ROOT = Path(__file__).resolve().parent.parent
RESULTS_DIR = PROJECT_ROOT / "results"
PLOTS_DIR = PROJECT_ROOT / "plots"

PLOTS_DIR.mkdir(exist_ok=True)

data = np.genfromtxt(
    RESULTS_DIR / "benchmark_results.csv",
    delimiter=",",
    names=True,
    dtype=None,
    encoding="utf-8"
)

frequencies = np.unique(data["frequency_hz"])

def get_times(algorithm):
    rows = data[data["algorithm"] == algorithm]
    rows = np.sort(rows, order="frequency_hz")
    return rows["median_ns_per_sample"]

naive = get_times("Naive")
polyblep = get_times("PolyBLEP")
additive = get_times("Additive BL")

fig, (ax1, ax2) = plt.subplots(
    2, 1, figsize=(10, 8), sharex=True
)

ax1.plot(frequencies, naive, "o-", label="Naive")
ax1.plot(frequencies, polyblep, "s-", label="PolyBLEP")

ax1.set_title("Computational Cost vs Fundamental Frequency")
ax1.set_ylabel("Time per sample (ns)")
ax1.grid(True, alpha=0.3)
ax1.legend()

ax2.plot(
    frequencies, additive,
    "^-", label="Additive BL", color="green"
)

ax2.set_xlabel("Fundamental frequency (Hz)")
ax2.set_ylabel("Time per sample (ns)")
ax2.grid(True, alpha=0.3)
ax2.legend()

plt.tight_layout()
plt.savefig(
    PLOTS_DIR / "computational_cost.png",
    dpi=300
)
plt.show()

poly_vs_naive = polyblep / naive
additive_vs_poly = additive / polyblep

fig, (ax1, ax2) = plt.subplots(
    2, 1, figsize=(10, 8), sharex=True
)

ax1.plot(frequencies, poly_vs_naive, "o-")
ax1.set_title("Relative Computational Cost")
ax1.set_ylabel("PolyBLEP / Naive")
ax1.grid(True, alpha=0.3)

ax2.plot(frequencies, additive_vs_poly, "s-", color="green")
ax2.set_xlabel("Fundamental frequency (Hz)")
ax2.set_ylabel("Additive BL / PolyBLEP")
ax2.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig(
    PLOTS_DIR / "relative_computational_cost.png",
    dpi=300
)
plt.show()

print("Benchmark plots saved successfully.")
