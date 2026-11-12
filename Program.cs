const long sampleRate = 48000;
const double durationSeconds = 0.1;

long[] testFrequencies =
{
    440,
    1100,
    2200,
    4400,
    8800
};

int sampleCount = (int)Math.Round(
    sampleRate * durationSeconds);

string projectDirectory = Path.GetFullPath(
    Path.Combine(
        AppContext.BaseDirectory,
        "..", "..", ".."));

string outputDirectory = Path.Combine(
    projectDirectory, "results");

Directory.CreateDirectory(outputDirectory);

foreach (long frequency in testFrequencies)
{
    if ((frequency * sampleCount) % sampleRate != 0)
    {
        throw new InvalidOperationException(
            $"Non-coherent frequency: {frequency} Hz");
    }

    var naive = new NaiveSawtooth(
        sampleRate, frequency);

    var polyBlep = new PolyBlepSawtooth(
        sampleRate, frequency);

    var additive = new BandLimitedSawtooth(
        sampleRate, frequency);

    double[] naiveSamples =
        naive.Generate(sampleCount);

    double[] polySamples =
        polyBlep.Generate(sampleCount);

    double[] additiveSamples =
        additive.Generate(sampleCount);

    string outputPath = Path.Combine(
        outputDirectory,
        $"oscillator_comparison_{frequency}Hz.csv");

    CsvExporter.Export(
        outputPath,
        naiveSamples,
        polySamples,
        additiveSamples);

    Console.WriteLine(
        $"f0 = {frequency,5} Hz | " +
        $"Harmonics = {additive.HarmonicCount,2} | " +
        $"Samples = {sampleCount}");

    Console.WriteLine($"Saved: {outputPath}");
}

Console.WriteLine(
    "\nAll frequency experiments completed.");

Console.WriteLine("\nStarting benchmark...");

OscillatorBenchmark.Run(projectDirectory);