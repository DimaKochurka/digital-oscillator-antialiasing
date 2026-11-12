public sealed class PhaseAccumulator
{
    private readonly long sampleRate;
    private readonly long frequency;
    private long phasePosition;

    public double Increment =>
        (double)frequency / sampleRate;

    public double Phase =>
        (double)phasePosition / sampleRate;

    public PhaseAccumulator(
        long sampleRate,
        long frequency)
    {
        if (sampleRate <= 0)
            throw new ArgumentOutOfRangeException(
                nameof(sampleRate));

        if (frequency <= 0 ||
            frequency >= sampleRate / 2.0)
            throw new ArgumentOutOfRangeException(
                nameof(frequency));

        this.sampleRate = sampleRate;
        this.frequency = frequency;
        phasePosition = 0;
    }

    // Integer phase accumulation avoids cumulative floating-point drift.
    public void Advance()
    {
        phasePosition += frequency;

        if (phasePosition >= sampleRate)
            phasePosition -= sampleRate;
    }

    public void Reset()
    {
        phasePosition = 0;
    }
}
