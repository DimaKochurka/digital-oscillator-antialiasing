import csv
from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt


# EXPERIMENT CONFIGURATION

SAMPLE_RATE = 48000

TEST_FREQUENCIES = [
    440,
    1100,
    2200,
    4400,
    8800
]

RESULTS_DIRECTORY = (
    Path(__file__).resolve().parent.parent / "results"
)

PLOTS_DIRECTORY = (
    Path(__file__).resolve().parent.parent / "plots"
)

PLOTS_DIRECTORY.mkdir(parents=True, exist_ok=True)


# SPECTRAL METRICS

def analyze_spectrum(
    samples,
    reference,
    sample_rate,
    fundamental
):
    N = len(samples)

    if len(reference) != N:
        raise ValueError(
            "Signal and reference must have equal lengths."
        )

    # Check coherent sampling.
    cycles = fundamental * N / sample_rate

    if abs(cycles - round(cycles)) > 1e-9:
        raise ValueError(
            f"Non-coherent sampling: {fundamental} Hz"
        )

    # Compute FFT.
    spectrum = np.fft.rfft(samples)
    reference_spectrum = np.fft.rfft(reference)

    # Harmonics strictly below Nyquist.
    nyquist = sample_rate / 2

    harmonic_numbers = np.arange(
        1,
        int(np.ceil(nyquist / fundamental))
    )

    harmonic_frequencies = (
        harmonic_numbers * fundamental
    )

    harmonic_bins = np.rint(
        harmonic_frequencies * N / sample_rate
    ).astype(int)

    # One-sided energy weighting.
    weights = np.full(len(spectrum), 2.0)
    weights[0] = 1.0

    if N % 2 == 0:
        weights[-1] = 1.0

    energy = weights * np.abs(spectrum) ** 2

    # Separate desired and undesired components.
    desired_mask = np.zeros(
        len(spectrum),
        dtype=bool
    )

    desired_mask[harmonic_bins] = True

    undesired_mask = ~desired_mask
    undesired_mask[0] = False

    desired_energy = np.sum(
        energy[desired_mask]
    )

    undesired_energy = np.sum(
        energy[undesired_mask]
    )

    if desired_energy <= 0:
        raise ValueError(
            "Desired spectral energy is zero."
        )

    if undesired_energy > 0:
        asr_db = 10 * np.log10(
            undesired_energy / desired_energy
        )
    else:
        asr_db = -np.inf

    # Harmonic magnitude error relative to reference.
    amplitudes = np.abs(
        spectrum[harmonic_bins]
    )

    reference_amplitudes = np.abs(
        reference_spectrum[harmonic_bins]
    )

    if np.any(reference_amplitudes <= 0):
        raise ValueError(
            "Reference contains a zero harmonic amplitude."
        )

    hme_db = 20 * np.log10(
        amplitudes / reference_amplitudes
    )

    return {
        "asr_db": asr_db,
        "harmonic_numbers": harmonic_numbers,
        "harmonic_frequencies": harmonic_frequencies,
        "hme_db": hme_db
    }


# DATA ANALYSIS

asr_summary = []
hme_summary = []

for fundamental in TEST_FREQUENCIES:

    csv_path = (
        RESULTS_DIRECTORY
        / f"oscillator_comparison_{fundamental}Hz.csv"
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

    reference = signals["Additive BL"]

    print(f"\n{'=' * 55}")
    print(f"FUNDAMENTAL FREQUENCY: {fundamental} Hz")
    print(f"{'=' * 55}")

    for name, samples in signals.items():

        metrics = analyze_spectrum(
            samples,
            reference,
            SAMPLE_RATE,
            fundamental
        )

        asr_summary.append({
            "frequency_hz": fundamental,
            "algorithm": name,
            "asr_db": metrics["asr_db"]
        })

        print(
            f"{name:12} | "
            f"ASR = {metrics['asr_db']:9.2f} dB"
        )

        # Store individual harmonic magnitude errors.
        for k, freq, error in zip(
            metrics["harmonic_numbers"],
            metrics["harmonic_frequencies"],
            metrics["hme_db"]
        ):
            hme_summary.append({
                "fundamental_hz": fundamental,
                "algorithm": name,
                "harmonic": int(k),
                "harmonic_frequency_hz": float(freq),
                "hme_db": float(error)
            })


# EXPORT RESULTS

def export_csv(path, rows, fieldnames):

    with open(
        path,
        "w",
        newline="",
        encoding="utf-8"
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=fieldnames
        )

        writer.writeheader()
        writer.writerows(rows)


export_csv(
    RESULTS_DIRECTORY / "asr_summary.csv",
    asr_summary,
    [
        "frequency_hz",
        "algorithm",
        "asr_db"
    ]
)

export_csv(
    RESULTS_DIRECTORY / "hme_summary.csv",
    hme_summary,
    [
        "fundamental_hz",
        "algorithm",
        "harmonic",
        "harmonic_frequency_hz",
        "hme_db"
    ]
)

print("\nCSV summaries exported successfully.")


# ASR IMPROVEMENT TABLE

print("\nASR IMPROVEMENT: Naive vs PolyBLEP")
print("-" * 50)

for fundamental in TEST_FREQUENCIES:

    naive_asr = next(
        row["asr_db"]
        for row in asr_summary
        if row["frequency_hz"] == fundamental
        and row["algorithm"] == "Naive"
    )

    poly_asr = next(
        row["asr_db"]
        for row in asr_summary
        if row["frequency_hz"] == fundamental
        and row["algorithm"] == "PolyBLEP"
    )

    improvement = naive_asr - poly_asr

    print(
        f"{fundamental:5} Hz | "
        f"Improvement: {improvement:+8.2f} dB"
    )


# ASR VISUALIZATION

plt.figure(figsize=(11, 6))

colors = {
    "Naive": "tab:blue",
    "PolyBLEP": "tab:orange"
}

for algorithm, color in colors.items():

    rows = [
        row for row in asr_summary
        if row["algorithm"] == algorithm
    ]

    frequencies = [
        row["frequency_hz"] for row in rows
    ]

    asr_values = [
        row["asr_db"] for row in rows
    ]

    plt.plot(
        frequencies,
        asr_values,
        marker="o",
        linewidth=2,
        markersize=7,
        color=color,
        label=algorithm
    )

plt.xscale("log")

plt.xticks(
    TEST_FREQUENCIES,
    [str(f) for f in TEST_FREQUENCIES]
)

plt.xlabel("Fundamental Frequency (Hz)")
plt.ylabel("ASR (dB)")

plt.title(
    "Aliasing-to-Signal Ratio vs Fundamental Frequency"
)

plt.grid(
    True,
    which="both",
    alpha=0.3
)

plt.legend()
plt.tight_layout()

plot_path = (
    PLOTS_DIRECTORY / "asr_vs_frequency.png"
)

plt.savefig(
    plot_path,
    dpi=300,
    bbox_inches="tight"
)

plt.show()

print(f"\nPlot saved to: {plot_path}")
print("Analysis completed.")
