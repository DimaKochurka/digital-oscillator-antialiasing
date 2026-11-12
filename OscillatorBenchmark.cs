using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Globalization;
using System.IO;
using System.Linq;

public static class OscillatorBenchmark
{
    private const long SampleRate = 48000;

    private const int SampleCount = 48000;
    private const int WarmupRounds = 30;
    private const int MeasuredRounds = 100;

    private static readonly long[] TestFrequencies =
    {
        440, 1100, 2200, 4400, 8800
    };


    private sealed class BenchmarkCase
    {
        public long Frequency { get; }
        public string Algorithm { get; }
        public double[] Buffer { get; }

        public Action Prepare { get; }
        public Action Generate { get; }

        public List<double> Measurements { get; } = new();

        public BenchmarkCase(
            long frequency,
            string algorithm,
            double[] buffer,
            Action prepare,
            Action generate)
        {
            Frequency = frequency;
            Algorithm = algorithm;
            Buffer = buffer;
            Prepare = prepare;
            Generate = generate;
        }
    }


    public static void Run(string projectDirectory)
    {
        string resultsDirectory = Path.Combine(
            projectDirectory, "results");

        Directory.CreateDirectory(resultsDirectory);

        string outputPath = Path.Combine(
            resultsDirectory, "benchmark_results.csv");

        var cases = CreateCases();

        Console.WriteLine("Warming up all oscillators...");

        for (int round = 0; round < WarmupRounds; round++)
        {
            foreach (var testCase in cases)
            {
                testCase.Prepare();
                testCase.Generate();
            }
        }

        Console.WriteLine("Measuring core DSP processing...");

        var random = new Random(42);

        for (int round = 0; round < MeasuredRounds; round++)
        {
            // Randomize case order to reduce systematic timing bias.
            var shuffled = cases
                .OrderBy(_ => random.Next())
                .ToList();

            foreach (var testCase in shuffled)
            {
                testCase.Prepare();

                long start = Stopwatch.GetTimestamp();

                testCase.Generate();

                long end = Stopwatch.GetTimestamp();

                double elapsedNs =
                    (end - start) * 1_000_000_000.0
                    / Stopwatch.Frequency;

                double nsPerSample =
                    elapsedNs / SampleCount;

                testCase.Measurements.Add(nsPerSample);

                GC.KeepAlive(testCase.Buffer);
            }
        }

        using var writer = new StreamWriter(outputPath);

        writer.WriteLine(
            "frequency_hz,algorithm,median_ns_per_sample");


        Console.WriteLine();
        Console.WriteLine(
            "Frequency | Algorithm   | Median ns/sample");

        foreach (var testCase in cases)
        {
            var values = testCase.Measurements
                .OrderBy(x => x)
                .ToArray();

            int middle = values.Length / 2;

            double median = values.Length % 2 == 0
                ? (values[middle - 1] + values[middle]) / 2.0
                : values[middle];

            writer.WriteLine(
                $"{testCase.Frequency}," +
                $"{testCase.Algorithm}," +
                $"{median.ToString(CultureInfo.InvariantCulture)}");

            Console.WriteLine(
                $"{testCase.Frequency,5} Hz | " +
                $"{testCase.Algorithm,-11} | " +
                $"{median,10:F2}");
        }


        Console.WriteLine(
            $"\nBenchmark saved to: {outputPath}");
    }


    private static List<BenchmarkCase> CreateCases()
    {
        var cases = new List<BenchmarkCase>();

        foreach (long frequency in TestFrequencies)
        {
            var naive = new NaiveSawtooth(
                SampleRate, frequency);

            var naiveBuffer = new double[SampleCount];

            cases.Add(new BenchmarkCase(
                frequency,
                "Naive",
                naiveBuffer,
                () => naive.Reset(),
                () => naive.GenerateInto(naiveBuffer)));

            var poly = new PolyBlepSawtooth(
                SampleRate, frequency);

            var polyBuffer = new double[SampleCount];

            cases.Add(new BenchmarkCase(
                frequency,
                "PolyBLEP",
                polyBuffer,
                () => poly.Reset(),
                () => poly.GenerateInto(polyBuffer)));

            var additive = new BandLimitedSawtooth(
                SampleRate, frequency);

            var additiveBuffer = new double[SampleCount];

            cases.Add(new BenchmarkCase(
                frequency,
                "Additive BL",
                additiveBuffer,
                () => { },
                () => additive.GenerateInto(
                    additiveBuffer, 0)));
        }

        return cases;
    }

}
