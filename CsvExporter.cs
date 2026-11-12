using System.Globalization;
using System.Text;

public static class CsvExporter
{
    public static void Export(
        string filePath,
        double[] naive,
        double[] polyBlep,
        double[] additive)
    {
        if (naive.Length != polyBlep.Length ||
            naive.Length != additive.Length)
        {
            throw new ArgumentException(
                "Signal arrays must have equal lengths.");
        }

        using var writer = new StreamWriter(
            filePath, false, Encoding.UTF8);

        writer.WriteLine("sample,naive,polyblep,additive");

        for (int n = 0; n < naive.Length; n++)
        {
            writer.WriteLine(
                $"{n}," +
                $"{naive[n].ToString("G17", CultureInfo.InvariantCulture)}," +
                $"{polyBlep[n].ToString("G17", CultureInfo.InvariantCulture)}," +
                $"{additive[n].ToString("G17", CultureInfo.InvariantCulture)}");
        }
    }
}
