public sealed class PolyBlepSawtooth
{
    private readonly PhaseAccumulator accumulator;

    public PolyBlepSawtooth(long sampleRate, long frequency)
    {
        accumulator = new PhaseAccumulator(
            sampleRate, frequency);
    }

    private static double PolyBlep(double t, double dt)
    {
        if (t < dt)
        {
            double u = t / dt;
            return 2.0 * u - u * u - 1.0;
        }

        if (t > 1.0 - dt)
        {
            double v = (t - 1.0) / dt;
            return v * v + 2.0 * v + 1.0;
        }

        return 0.0;
    }

    public double GenerateSample()
    {
        double phase = accumulator.Phase;
        double dt = accumulator.Increment;

        double sample = 2.0 * phase - 1.0;

        sample -= PolyBlep(phase, dt);

        accumulator.Advance();

        return sample;
    }

    public void GenerateInto(double[] buffer)
    {
        ArgumentNullException.ThrowIfNull(buffer);

        for (int n = 0; n < buffer.Length; n++)
        {
            buffer[n] = GenerateSample();
        }
    }

    public double[] Generate(int sampleCount)
    {
        if (sampleCount < 0)
            throw new ArgumentOutOfRangeException(
                nameof(sampleCount));

        double[] samples = new double[sampleCount];

        GenerateInto(samples);

        return samples;
    }

    public void Reset()
    {
        accumulator.Reset();
    }
}
