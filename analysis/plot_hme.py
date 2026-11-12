import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

results_dir = (
    Path(__file__).resolve().parent.parent / "results"
)

plots_dir = (
    Path(__file__).resolve().parent.parent / "plots"
)

plots_dir.mkdir(parents=True, exist_ok=True)

data = np.genfromtxt(
    results_dir / "hme_summary.csv",
    delimiter=",",
    names=True,
    encoding="utf-8-sig",
    dtype=None
)

test_frequencies = [
    440, 1100, 2200, 4400, 8800
]

plt.figure(figsize=(12, 7))

for fundamental in test_frequencies:

    mask = (
        (data["fundamental_hz"] == fundamental)
        & (data["algorithm"] == "PolyBLEP")
    )

    harmonic_frequencies = (
        data["harmonic_frequency_hz"][mask]
    )

    errors = data["hme_db"][mask]

    plt.plot(
        harmonic_frequencies,
        errors,
        marker="o",
        markersize=4,
        linewidth=1.8,
        label=f"f0 = {fundamental} Hz"
    )

plt.axhline(
    0,
    color="gray",
    linestyle="--",
    linewidth=1
)

plt.xlabel("Harmonic Frequency (Hz)")
plt.ylabel("Harmonic Magnitude Error (dB)")

plt.title(
    "PolyBLEP Harmonic Magnitude Error vs Frequency"
)

plt.xlim(0, 24000)
plt.xticks(np.arange(0, 24001, 2000))

plt.grid(True, alpha=0.3)
plt.legend()
plt.tight_layout()

plot_path = plots_dir / "hme_vs_frequency.png"

plt.savefig(
    plot_path,
    dpi=300,
    bbox_inches="tight"
)

plt.show()

print(f"Plot saved to: {plot_path}")

sample_rate = 48000

plt.figure(figsize=(12, 7))

for fundamental in test_frequencies:

    mask = (
        (data["fundamental_hz"] == fundamental)
        & (data["algorithm"] == "PolyBLEP")
    )

    freqs = data["harmonic_frequency_hz"][mask]
    measured_hme = data["hme_db"][mask]

    normalized_freq = freqs / sample_rate

    # Compare measured HME with the squared-sinc reference in dB.
    theoretical_hme = 40 * np.log10(
        np.abs(np.sinc(normalized_freq))
    )

    deviation = measured_hme - theoretical_hme

    plt.scatter(
        freqs,
        deviation,
        s=22,
        label=f"f0 = {fundamental} Hz"
    )

plt.axhline(
    0,
    color="gray",
    linestyle="--",
    linewidth=1
)

plt.xlabel("Harmonic Frequency (Hz)")
plt.ylabel("Measured - Theoretical HME (dB)")

plt.title(
    "PolyBLEP HME Deviation from Theoretical Response"
)

plt.xlim(0, 24000)
plt.xticks(np.arange(0, 24001, 2000))

plt.grid(True, alpha=0.3)
plt.legend()
plt.tight_layout()

deviation_path = (
    plots_dir / "hme_theoretical_deviation.png"
)

plt.savefig(
    deviation_path,
    dpi=300,
    bbox_inches="tight"
)

plt.show()

print(f"Deviation plot saved to: {deviation_path}")