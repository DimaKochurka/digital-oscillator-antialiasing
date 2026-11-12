public sealed class NaiveSawtooth
{
    private readonly PhaseAccumulator accumulator;

    public NaiveSawtooth(long sampleRate, long frequency)
    {
        accumulator = new PhaseAccumulator(
            sampleRate, frequency);
    }

    public double GenerateSample()
    {
        double phase = accumulator.Phase;

        double sample = 2.0 * phase - 1.0;

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
        {
            throw new ArgumentOutOfRangeException(
                nameof(sampleCount));
        }

        double[] samples = new double[sampleCount];

        GenerateInto(samples);

        return samples;
    }

    public void Reset()
    {
        accumulator.Reset();
    }
}
