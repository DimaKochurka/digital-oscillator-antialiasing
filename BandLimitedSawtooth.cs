public sealed class BandLimitedSawtooth
{
    private readonly double sampleRate;
    private readonly double frequency;
    private readonly int harmonicCount;

    public int HarmonicCount => harmonicCount;

    public BandLimitedSawtooth(double sampleRate, double frequency)
    {
        if (!double.IsFinite(sampleRate) || sampleRate <= 0)
            throw new ArgumentOutOfRangeException(nameof(sampleRate));

        if (!double.IsFinite(frequency) ||
            frequency <= 0 || frequency >= sampleRate / 2)
            throw new ArgumentOutOfRangeException(nameof(frequency));

        this.sampleRate = sampleRate;
        this.frequency = frequency;

        // Strictly below the Nyquist frequency.
        harmonicCount = (int)Math.Ceiling(
            sampleRate / (2.0 * frequency)) - 1;
    }

    public double GenerateSample(long sampleIndex)
    {
        double sum = 0.0;

        for (int k = 1; k <= harmonicCount; k++)
        {
            double phase = 2.0 * Math.PI * k
                           * frequency * sampleIndex / sampleRate;

            sum += Math.Sin(phase) / k;
        }

        return -2.0 / Math.PI * sum;
    }

    public void GenerateInto(
        double[] buffer,
        long startSampleIndex = 0)
    {
        ArgumentNullException.ThrowIfNull(buffer);

        if (startSampleIndex < 0 ||
            startSampleIndex > long.MaxValue - buffer.Length)
        {
            throw new ArgumentOutOfRangeException(
                nameof(startSampleIndex));
        }

        for (int n = 0; n < buffer.Length; n++)
        {
            buffer[n] = GenerateSample(startSampleIndex + n);
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
}
