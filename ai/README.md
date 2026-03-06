# AI SQL Function

This recipe demonstrates how to use the `ai()` SQL function to invoke large language models (LLMs) directly within SQL queries for AI-powered text generation.

The `ai()` function enables you to integrate AI capabilities into your data workflows without external APIs or complex integrations—simply call a function in your SQL query!

## What You'll Learn

- How to configure LLM models in Spice
- How to use the `ai()` function in SQL queries
- How to process data with AI in parallel for better performance
- Real-world examples like sentiment analysis and text categorization

## Prerequisites

- Spice CLI installed. Follow the [Getting Started](https://docs.spiceai.org/getting-started) guide if needed.
- An OpenAI API key (or another supported LLM provider like Anthropic, xAI, etc.)

## Quick Start

### Step 1: Clone and Navigate

```bash
git clone https://github.com/spiceai/cookbook.git  # Skip if already cloned
cd cookbook/ai
```

### Step 2: Configure Your API Key

Create a `.env` file with your OpenAI API key:

```bash
echo "SPICE_OPENAI_API_KEY=your_openai_api_key_here" > .env
```

Or manually create `.env`:

```env
SPICE_OPENAI_API_KEY=your_openai_api_key_here
```

### Step 3: Start Spice

```bash
spice run
```

You should see output indicating the model is ready:

```shell
2025-10-06T10:30:00.123456Z  INFO runtime::init::model: Loading model [gpt-4o-mini] from openai:gpt-4o-mini...
2025-10-06T10:30:01.234567Z  INFO runtime::init::model: Model [gpt-4o-mini] deployed, ready for inferencing
2025-10-06T10:30:02.345678Z  INFO runtime::init::dataset: Dataset taxi_zones registered...
```

### Step 4: Try Your First AI Query

Open the Spice SQL REPL in a new terminal:

```bash
spice sql
```

Wait until the runtime reports that it is ready before proceeding.

## Example Queries

### Example 1: Simple Text Generation

Ask the AI a question:

```sql
SELECT ai('What is the capital of France?') as answer;
```

### Example 2: Categorize Data

Categorize NYC taxi zones using AI:

```sql
SELECT
  LocationID,
  Zone,
  ai(concat('Categorize this location in one word: ', Zone), 'gpt-4o-mini') as category
FROM taxi_zones
LIMIT 5;
```


### Example 3: Sentiment Analysis

Analyze customer feedback sentiment:

```sql
SELECT
  feedback,
  ai('Classify this feedback as positive, negative, or neutral: ' || feedback, 'gpt-4o-mini') as sentiment
FROM customer_feedback
LIMIT 3;
```


### Example 4: Data Enrichment

Generate descriptions for locations:

```sql
SELECT
  Zone,
  Borough,
  ai('Write a one-sentence description of ' || Zone || ' in ' || Borough, 'gpt-4o-mini') as description
FROM taxi_zones
WHERE Borough = 'Manhattan'
LIMIT 3;
```

### Example 5: Translation

Translate text to different languages:

```sql
SELECT
  Zone as original,
  ai(concat_ws(' ', 'Translate to Spanish:', Zone), 'gpt-4o-mini') as spanish,
  ai(concat_ws(' ', 'Translate to French:', Zone), 'gpt-4o-mini') as french
FROM taxi_zones
WHERE Borough = 'Manhattan'
LIMIT 5;
```


## Understanding the Configuration

The `spicepod.yaml` file configures the LLM model:

```yaml
models:
  - name: gpt-4o-mini
    from: openai:gpt-4o-mini
    params:
      openai_api_key: ${secrets:SPICE_OPENAI_API_KEY}
```

**Key Points:**

- `name`: The identifier you use in `ai(message, 'model_name')`
- `from`: The model provider and model name
- `params`: Configuration like API keys (loaded from `.env`)

## How It Works

### Function Signatures

The `ai()` function has two forms:

1. **Default Model** (when only one model configured):

   ```sql
   ai('your message here')
   ```

2. **Specific Model**:

   ```sql
   ai('your message here', 'model_name')
   ```

### Parallel Processing

The `ai()` function executes **asynchronously**, meaning when you query multiple rows, Spice processes the AI calls in parallel for better performance:

```sql
-- This processes 10 AI calls in parallel!
SELECT Zone, ai('Categorize: ' || Zone) as category
FROM taxi_zones
LIMIT 10;
```

### Limits

- Maximum batch size: 100 rows per query
- Maximum message size: 1 MB per message

### Error Handling

If an AI call fails, the function returns `NULL` and logs the error. You can check the logs or task history for details.

## Advanced Usage

### Combining with Other Functions

The `ai()` function works seamlessly with SQL:

```sql
-- Uppercase the AI response
SELECT upper(ai('say hello')) as loud_greeting;

-- Get first 20 characters of response
SELECT left(ai('Write a long story'), 20) as preview;

-- Use in WHERE clauses
SELECT * FROM products
WHERE ai('Is this a tech product? Answer yes or no: ' || description) = 'yes';
```

## Using Different Model Providers

Spice supports multiple LLM providers! Here's how to configure different ones:

### Anthropic Claude

Add to `spicepod.yaml`:

```yaml
models:
  - name: sonnet-4-5
    from: anthropic:claude-4-5-sonnet
    params:
      anthropic_api_key: ${secrets:ANTHROPIC_API_KEY}
```

### xAI Grok

```yaml
models:
  - name: grok-4-1-fast
    from: xai:grok-4-1-fast-non-reasoning
    params:
      xai_api_key: ${secrets:XAI_API_KEY}
```

Then use in queries:

```sql
SELECT
  ai('Hello!', 'gpt-4o-mini') as openai_response,
  ai('Hello!', 'sonnet-4-5') as claude_response,
  ai('Hello!', 'grok-4-1-fast-non-reasoning') as grok_response;
```

## Real-World Use Cases

1. **Content Moderation**: Classify user-generated content
2. **Data Cleaning**: Standardize messy text data
3. **Entity Extraction**: Extract structured info from unstructured text
4. **Translation**: Translate text in your database
5. **Summarization**: Generate summaries of long text fields
6. **Classification**: Categorize products, tickets, or documents
7. **Search Enhancement**: Generate better search terms

## Tips and Best Practices

1. **Be Specific**: Clear, specific prompts get better results

   ```sql
   -- Good
   ai('Classify as positive/negative/neutral: ' || text)

   -- Less effective
   ai('What about: ' || text)
   ```

2. **Limit Results**: Use `LIMIT` for testing to avoid long waits and costs

   ```sql
   SELECT ai('...') FROM large_table LIMIT 10;  -- Test first!
   ```

3. **Use Cheaper Models**: For simple tasks, use `gpt-4o-mini` or similar

4. **Handle NULL**: AI calls can fail, so handle NULL responses

   ```sql
   SELECT coalesce(ai('...'), 'Error or no response') as result;
   ```

## Troubleshooting

### "No model configured" error

Make sure your `spicepod.yaml` has a model defined and Spice has restarted.

### API key errors

Check that your `.env` file is in the correct directory and properly formatted.

### Slow queries

- Reduce the number of rows with `LIMIT`
- Consider using a faster/cheaper model for simple tasks
- Check your internet connection and API rate limits

### NULL results

Check the Spice logs for error messages:

```bash
# In the terminal where `spice run` is running
# Look for errors related to the AI model
```

## Learn More

- [AI Functions Documentation](https://docs.spiceai.org/reference/sql/ai)
- [Large Language Models in Spice](https://docs.spiceai.org/features/large-language-models)
- [Model Providers](https://docs.spiceai.org/components/models)
- [SQL Reference](https://docs.spiceai.org/reference/sql)

## Next Steps

- Explore the [text-to-sql](../text-to-sql) cookbook for natural language to SQL
- Check out [vector search](../vectors) for semantic search capabilities
- Try [embeddings](../search) for similarity search
- Learn about [LLM tools](https://docs.spiceai.org/features/large-language-models/tools) for more advanced AI integration
