# Generative Visualizations

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

   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   pip install -r requirements.txt
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

In a new terminal, activate your virtual environment and run the main script:

```bash
source .venv/bin/activate
python main.py "How has per month sales trended?"
```

The script will:
1. Send your question to the `visualisation_and_sql` model
2. Execute the generated SQL query against Spice
3. Pass the results to the `summary_maker` model for analysis
4. Output the Chart.js HTML, SQL query, data, and summary

### Step 3: View the Visualization

The script outputs a Chart.js HTML snippet. To view it:

1. Copy the HTML output
2. Save it to a file (e.g., `chart.html`)
3. Open in a web browser

Or use this one-liner to open the visualization directly:

```bash
python main.py "How has sales changed over time?" 2>/dev/null | head -n 50 > chart.html && open chart.html
```

## Example Queries

Try these sample questions:

```bash
# Sales trends
python main.py "How has per month sales trended?"
python main.py "What are the top 5 products by total sales?"
python main.py "Show me quarterly revenue breakdown"

# Product analysis
python main.py "Which product lines have the highest sales?"
python main.py "Compare sales between different countries"
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
        // Chart configuration with line chart showing monthly sales trends
        ...
    </script>
</body>
</html>
```

**AI Summary:**

> Sales show a strong seasonal pattern with peaks in November. The data from 2003-2005 shows consistent growth year-over-year, with November typically exceeding $1M in sales.

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

**SQL query errors**

- The model uses tools to validate queries, but complex schemas may require refinement
- Try rephrasing your question or being more specific about the data you want
