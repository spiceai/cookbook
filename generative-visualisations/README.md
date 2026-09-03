# Generative Visualizations

Works with `v1.8+`

This recipe demonstrates how to build an AI-powered data analyst that generates SQL queries and interactive Chart.js visualizations from natural language questions.

## What You'll Learn

- How to configure LLM models in Spice with structured JSON output
- How to use AI tools (`sql`, `list_datasets`, `table_schema`) to enable LLMs to explore and query data
- How to generate Chart.js visualizations dynamically from query results
- How to chain multiple AI models for different tasks (SQL generation vs. summarization)

## Prerequisites

**Required:**

1. **Install Spice CLI** - Follow the [Getting Started guide](https://docs.spiceai.org/getting-started) if you haven't already.

2. **Clone this repository:**

   ```bash
   git clone https://github.com/spiceai/cookbook.git  # Skip if already cloned
   cd cookbook/generative-visualisations
   ```

3. **Configure your environment:**

   Create a `.env` file with your OpenAI API key:

   ```bash
   echo "SPICE_OPENAI_API_KEY=your_openai_api_key_here" > .env
   ```

   Get an API key from [OpenAI Platform](https://platform.openai.com/api-keys)

4. **Set up Python environment:**

   This recipe uses [`uv`](https://docs.astral.sh/uv/) for dependency management. If you don't have it installed:

   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

   Then install dependencies (this will create the virtual environment automatically):

   ```bash
   uv sync
   ```

## How It Works

This recipe uses two AI models working together:

1. **`visualisation_and_sql`** (GPT-5.2) - Takes a natural language question and:
   - Explores available datasets using the `list_datasets` tool
   - Inspects table schemas using the `table_schema` tool
   - Generates a SQL query using the `sql` tool
   - Creates a Chart.js HTML snippet to visualize the results
   - Returns structured JSON with both the SQL and visualization code

2. **`summary_maker`** (GPT-5.2) - Takes the query results and:
   - Analyzes trends and patterns in the data
   - Generates a human-readable summary of insights

## Tutorial

### Step 1: Start the Spice Runtime

Start the Spice runtime in your terminal:

```bash
spice run
```

You should see output indicating that Spice is loading datasets and models:

```
2025-01-08T10:00:00.000Z  INFO runtime::init::dataset: Dataset sales registered...
2025-01-08T10:00:00.100Z  INFO runtime::init::model: Model [visualisation_and_sql] deployed...
2025-01-08T10:00:00.200Z  INFO runtime::init::model: Model [summary_maker] deployed...
```

**Keep this terminal open.** Open a new terminal for the next steps.

### Step 2: Run the Visualization Generator

In a new terminal, run the main script via `uv`:

```bash
uv run main.py "How has per month sales trended?"
```

The script will:

1. Send your question to the `visualisation_and_sql` model
2. Execute the generated SQL query against Spice
3. Pass the results to the `summary_maker` model for analysis
4. Output the Chart.js HTML, SQL query, data, and summary

### Step 3: View the Visualization

Pass `--output-html` to write a self-contained HTML file. The script runs the
generated SQL and embeds the results in the page, so the chart renders offline
with no further wiring:

```bash
uv run main.py "How has sales changed over time?" --output-html chart.html
```

Then open it in a browser (`open chart.html` on macOS, `xdg-open chart.html` on Linux).

Without `--output-html`, the script prints the Chart.js HTML to stdout alongside
the SQL, the query results, and the summary. That output is a human-readable
report — don't redirect it straight into a `.html` file, as the section headers
and the trailing sections are not valid HTML.

## Example Queries

Try these sample questions:

```bash
# Sales trends
uv run main.py "How has per month sales trended?"
uv run main.py "What are the top 5 products by total sales?"
uv run main.py "Show me quarterly revenue breakdown"

# Product analysis
uv run main.py "Which product lines have the highest sales?"
uv run main.py "Compare sales between different countries"
```

## Example Output

For the question "How has per month sales trended?", you'll get:

**Generated SQL:**

```sql
SELECT "year", "month", SUM("sales") as total_sales
FROM spice.public.sales
GROUP BY "year", "month"
ORDER BY "year", "month";
```

**Chart.js Visualization:**

```html
<html>
  <head>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
  </head>
  <body>
    <canvas id="salesTrendChart" width="600" height="400"></canvas>
    <script>
      // The model reads rows from `window.__DATA__`, which `--output-html`
      // defines from the query results before this script runs.
      const rows = window.__DATA__ || [];
      // Chart configuration with line chart showing monthly sales trends
      ...
    </script>
  </body>
</html>
```

**AI Summary:**

> Sales show a strong seasonal pattern with peaks in November. The data from 2003-2005 shows consistent growth year-over-year, with November typically exceeding $1M in sales.

## Command-Line Options

| Flag | Description |
| --- | --- |
| `--output-html FILE` | Write a self-contained HTML file with the chart and query results embedded |
| `--no-summary` | Skip the `summary_maker` step |

## Configuration

### Spicepod Configuration

The `spicepod.yaml` configures:

- **Dataset**: Sales data from S3 with acceleration enabled for faster queries
- **visualisation_and_sql model**: GPT-5.2 with SQL tools and structured JSON output
- **summary_maker model**: GPT-5.2 for data analysis and summarization

### Customizing the Models

You can modify the system prompts in `spicepod.yaml` to:

- Change the visualization library (e.g., D3.js, Plotly)
- Adjust the SQL generation behavior
- Customize the summary format

## Troubleshooting

**Error: Could not connect to the Spice API server**

- Ensure Spice is running (`spice run`) in another terminal
- Check that port 8090 is not in use by another application

**Error: SPICE_OPENAI_API_KEY not set**

- Verify your `.env` file exists and contains a valid OpenAI API key
- Make sure you're running from the `generative-visualisations` directory

**Every x-axis label is identical (e.g. all `YYYY-MM`)**

- Spice formats timestamps with strftime specifiers, so `to_char(ts, '%Y-%m')` is correct
  while the Postgres-style `to_char(ts, 'YYYY-MM')` is returned verbatim as a literal
  string rather than erroring. Re-run the question, or ask for the label built with
  `EXTRACT` and `LPAD`.

**The chart renders but the plot area is empty**

- Check the generated config for `parsing: false` on a `type: 'time'` axis. Chart.js only
  accepts numeric timestamps once parsing is disabled, so `Date` objects make the axis
  silently fall back to the current month, placing the data off-scale.

**SQL query errors**

- The model uses tools to validate queries, but complex schemas may require refinement
- Try rephrasing your question or being more specific about the data you want
