# AI SQL Function Quick Start

Get started with the AI SQL function in under 2 minutes!

## Setup (30 seconds)

```bash
# Navigate to the recipe
cd cookbook/ai

# Add your OpenAI API key
echo "SPICE_OPENAI_API_KEY=your_key_here" > .env

# Start Spice
spice run
```

## Your First Query (30 seconds)

In a new terminal:

```bash
# Open SQL REPL
spice sql
```

Try this query:

```sql
SELECT ai('Hello! Introduce yourself in one sentence.', 'gpt-4o-mini') as response;
```

## Try Something Useful (1 minute)

Categorize NYC taxi zones:

```sql
SELECT
  Zone,
  ai('Categorize this NYC location in one word: ' || Zone, 'gpt-4o-mini') as category
FROM taxi_zones
LIMIT 5;
```

Translate zone names:

```sql
SELECT
  Zone,
  ai(concat_ws(' ', 'Translate to Spanish:', Zone), 'gpt-4o-mini') as spanish_name
FROM taxi_zones
LIMIT 3;
```

## What's Next?

- Check out [example_queries.sql](./example_queries.sql) for 20+ ready-to-use examples
- Run [examples.sh](./examples.sh) to see all examples: `./examples.sh`
- Read the full [README.md](./README.md) for detailed documentation

## Function Syntax

```sql
-- Use default model (when only one configured)
ai('your prompt here')

-- Specify model explicitly
ai('your prompt here', 'model_name')
```

## Common Patterns

**Text Classification:**

```sql
SELECT ai('Classify as [options]: ' || text_column) FROM table;
```

**Data Enrichment:**

```sql
SELECT column, ai('Generate [something] for: ' || column) FROM table;
```

**Question Answering:**

```sql
SELECT ai('Question about the data?') as answer;
```

## Tips

- Use `LIMIT` when testing to avoid long waits
- Be specific in your prompts for better results
- Check `runtime.task_history` to see AI call history
- Use `LEFT()` to truncate long responses

Need help? See the full [README.md](./README.md)!
