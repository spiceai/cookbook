using Spice;
using System.Linq;
using Apache.Arrow;
using System.Text;

// Top-level statements
var client = new SpiceClientBuilder()
            .Build();

var result = await client.Query("show tables;");
var enumerator = result.GetAsyncEnumerator();
while (await enumerator.MoveNextAsync())
{
    var batch = enumerator.Current;
    Console.WriteLine(batch.Dump());
}

// Extension method to dump RecordBatch to string
public static class ArrowDebug
{
    public static string Dump(this RecordBatch batch)
    {
        var sb = new StringBuilder();

        // print header
        sb.AppendLine(string.Join("\t", batch.Schema.FieldsList.Select(f => f.Name)));

        // print rows
        for (int row = 0; row < batch.Length; row++)
        {
            var values = new string[batch.ColumnCount];
            for (int col = 0; col < batch.ColumnCount; col++)
            {
                var arr = batch.Column(col);

                values[col] = arr switch
                {
                    StringArray sa   => sa.GetString(row) ?? "null",
                    Int32Array ia    => ia.GetValue(row)?.ToString() ?? "null",
                    Int64Array la    => la.GetValue(row)?.ToString() ?? "null",
                    DoubleArray da   => da.GetValue(row)?.ToString() ?? "null",
                    FloatArray fa    => fa.GetValue(row)?.ToString() ?? "null",
                    BooleanArray ba  => ba.GetValue(row)?.ToString() ?? "null",
                    _                => "?"
                };
            }
            sb.AppendLine(string.Join("\t", values));
        }

        return sb.ToString();
    }
}