import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

sample_rate = 48000
fundamental = 4400
nyquist = sample_rate / 2

project_root = Path(__file__).resolve().parent.parent

csv_path = (
    project_root
    / "results"
    / f"oscillator_comparison_{fundamental}Hz.csv"
)

output_dir = project_root / "plots"
output_dir.mkdir(parents=True, exist_ok=True)

output_path = (
    output_dir
    / f"spectral_comparison_{fundamental}Hz.png"
)

data = np.genfromtxt(
    csv_path,
    delimiter=",",
    names=True,
    encoding="utf-8-sig"
)

signals = {
    "Naive": data["naive"],
    "PolyBLEP": data["polyblep"],
    "Additive BL": data["additive"]
}

N = len(data)
frequencies = np.fft.rfftfreq(
    N,
    d=1 / sample_rate
)

harmonic_frequencies = np.arange(
    fundamental,
    nyquist,
    fundamental
)

colors = {
    "Naive": "tab:blue",
    "PolyBLEP": "tab:orange",
    "Additive BL": "tab:green"
}

fig, axes = plt.subplots(
    3, 1,
    figsize=(14, 10),
    sharex=True,
    sharey=True,
    constrained_layout=True
)

for ax, (name, samples) in zip(axes, signals.items()):

    spectrum = np.fft.rfft(samples)
    amplitude = np.abs(spectrum) / N

    if N % 2 == 0:
        amplitude[1:-1] *= 2
    else:
        amplitude[1:] *= 2

    db = 20 * np.log10(
        np.maximum(amplitude, 1e-12)
    )

    # Plot local spectral peaks instead of every FFT bin.
    peak_mask = np.zeros(
        len(db),
        dtype=bool
    )

    peak_mask[1:-1] = (
        (db[1:-1] > db[:-2]) &
        (db[1:-1] >= db[2:]) &
        (db[1:-1] > -115)
    )

    peak_mask[0] = db[0] > -115
    peak_mask[-1] = db[-1] > -115

    ax.vlines(
        frequencies[peak_mask],
        -120,
        db[peak_mask],
        color=colors[name],
        linewidth=0.9
    )

    # Mark the expected harmonics below Nyquist.
    for freq in harmonic_frequencies:
        ax.axvline(
            freq,
            color="gray",
            linestyle="--",
            linewidth=0.6,
            alpha=0.4
        )

    ax.set_title(name, fontsize=11)
    ax.set_ylabel("Magnitude (dB)")
    ax.set_ylim(-120, 5)
    ax.grid(True, alpha=0.2)

harmonics = np.arange(1, 6)
harmonic_freqs = harmonics * fundamental

tick_positions = np.concatenate((
    [0],
    harmonic_freqs,
    [nyquist]
))

tick_labels = (
    ["0"] +
    [
        f"H{k}\n{f / 1000:.1f}k"
        for k, f in zip(harmonics, harmonic_freqs)
    ] +
    ["24k"]
)

axes[-1].set_xticks(tick_positions)
axes[-1].set_xticklabels(tick_labels)

axes[-1].set_xlim(0, nyquist)
axes[-1].set_xlabel("Frequency (Hz)")

fig.suptitle(
    "Sawtooth Oscillator Spectral Comparison "
    f"(f0 = {fundamental} Hz, Fs = {sample_rate} Hz)",
    fontsize=14
)

fig.savefig(
    output_path,
    dpi=300,
    bbox_inches="tight"
)

print(f"Spectral comparison saved to: {output_path}")

plt.show()
