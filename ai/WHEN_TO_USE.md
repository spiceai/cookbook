# When to Use the AI SQL Function vs Other Spice Features

This guide helps you choose the right Spice feature for your AI needs.

## Quick Decision Tree

```
Need AI in your workflow?
    │
    ├─► Processing rows of data with AI?
    │   └─► ✅ Use AI SQL Function (this recipe!)
    │
    ├─► Converting natural language to SQL?
    │   └─► Use Text-to-SQL / NSQL endpoint
    │
    ├─► Building a chatbot or conversational AI?
    │   └─► Use Chat Completions API + Tools
    │
    ├─► Semantic/vector search?
    │   └─► Use Embeddings + Vector Search
    │
    └─► Evaluating LLM outputs?
        └─► Use LLM Evals / LLM as a Judge
```

## Feature Comparison

### AI SQL Function (`ai()` function)

**Use when:**

- Processing each row of a dataset with an LLM
- Text classification, sentiment analysis, categorization
- Data enrichment (generating descriptions, summaries)
- Transforming text data (translation, formatting)
- You want results as part of a SQL query

**Example:**

```sql
SELECT
  product_name,
  ai('Categorize this product: ' || description) as category
FROM products;
```

**Cookbook:** `ai/` (this recipe!)

---

### Text-to-SQL (NSQL)

**Use when:**

- Users ask questions in natural language
- Need to generate SQL from text queries
- Building query interfaces for non-technical users
- You want the SQL query itself, not the results

**Example:**

```bash
curl -XPOST "http://localhost:8090/v1/nsql" \
  -d '{"query": "Which vendors made the most trips?"}'
```

**Cookbook:** `text-to-sql/`

---

### Chat Completions API

**Use when:**

- Building conversational applications
- Need multi-turn conversations with context
- LLM needs to use tools (query data, call APIs)
- General Q&A about your data

**Example:**

```bash
curl -XPOST "http://localhost:8090/v1/chat/completions" \
  -d '{
    "model": "gpt-4o",
    "messages": [{"role": "user", "content": "What datasets do I have?"}]
  }'
```

**Cookbook:** `openai_sdk/`, `llm-memory/`

---

### Embeddings + Vector Search

**Use when:**

- Semantic search across text documents
- Finding similar items
- Recommendation systems
- Clustering or grouping by meaning

**Example:**

```sql
SELECT * FROM documents
WHERE cosine_distance(embedding,
  embed('search query', 'text-embedding-3-small')) < 0.2;
```

**Cookbook:** `vectors/`, `search/`, `search_github_files/`

---

### LLM Evaluations

**Use when:**

- Testing LLM performance
- Comparing different models
- Measuring accuracy, quality, etc.
- A/B testing prompts or models

**Example:**

```yaml
evals:
  - name: sentiment-accuracy
    model: gpt-4o-mini
    dataset: labeled_reviews
```

**Cookbook:** `evals/`, `llm-judge/`

---

## Side-by-Side Comparison

| Feature             | Input                     | Output               | Best For                 |
| ------------------- | ------------------------- | -------------------- | ------------------------ |
| **AI SQL Function** | SQL query with `ai()`     | Enriched SQL results | Row-by-row AI processing |
| **Text-to-SQL**     | Natural language question | SQL query + results  | Query generation         |
| **Chat API**        | Conversational messages   | AI response          | Chatbots, Q&A            |
| **Embeddings**      | Text content              | Vector embeddings    | Semantic search          |
| **Evals**           | Test cases + model        | Performance metrics  | Model evaluation         |

## Common Scenarios

### Scenario 1: Analyze Customer Feedback

**Goal:** Classify thousands of customer reviews by sentiment

**Solution:** ✅ **AI SQL Function**

```sql
SELECT
  review_id,
  review_text,
  ai('Classify as positive/negative/neutral: ' || review_text) as sentiment
FROM customer_reviews;
```

**Why:** Processing many rows, simple transformation, results in SQL

---

### Scenario 2: User Asks "What were our top products last month?"

**Goal:** Convert question to SQL and return results

**Solution:** ✅ **Text-to-SQL (NSQL)**

```bash
curl -XPOST "http://localhost:8090/v1/nsql" \
  -d '{"query": "What were our top products last month?"}'
```

**Why:** Natural language input, need SQL generation, one-shot query

---

### Scenario 3: Build a Data Assistant Chatbot

**Goal:** Multi-turn conversation that can query data

**Solution:** ✅ **Chat Completions API + Tools**

```python
client.chat.completions.create(
    model="gpt-4o",
    messages=conversation_history,
    tools="auto"  # Can query datasets
)
```

**Why:** Conversational, maintains context, needs tool use

---

### Scenario 4: Search Documentation by Meaning

**Goal:** Find relevant docs for "How do I deploy to production?"

**Solution:** ✅ **Embeddings + Vector Search**

```sql
SELECT title, content
FROM docs
WHERE cosine_distance(embedding,
  embed('deploy to production', 'text-embedding-3-small')) < 0.3
ORDER BY distance LIMIT 10;
```

**Why:** Semantic similarity, not keyword matching

---

### Scenario 5: Compare GPT-4 vs Claude Performance

**Goal:** Test which model is better for your use case

**Solution:** ✅ **LLM Evaluations**

```yaml
evals:
  - name: model-comparison
    models: [gpt-4o, claude-3-5-sonnet]
    dataset: test_cases
```

**Why:** Systematic testing, metrics, comparison

---

### Scenario 6: Translate Product Descriptions

**Goal:** Translate product descriptions from English to multiple languages

**Solution:** ✅ **AI SQL Function**

```sql
SELECT
  product_id,
  description as english,
  ai(concat_ws(' ', 'Translate to Spanish:', description), 'gpt-4o-mini') as spanish,
  ai(concat_ws(' ', 'Translate to French:', description), 'gpt-4o-mini') as french,
  ai(concat_ws(' ', 'Translate to German:', description), 'gpt-4o-mini') as german
FROM products
LIMIT 100;
```

**Why:** Row-by-row processing, multiple translations in parallel, results in SQL

---

## Combining Features

You can use multiple features together! Common combinations:

### AI SQL Function + Text-to-SQL

```python
# User asks a question
nsql_response = query_nsql("Show me negative reviews")

# Then enrich with AI UDF
sql = """
SELECT
  review,
  ai('Suggest improvement: ' || review) as suggestion
FROM reviews
WHERE sentiment = 'negative'
"""
```

### AI SQL Function + Vector Search

```sql
-- Find similar products
WITH similar AS (
  SELECT * FROM products
  WHERE vector_distance(embedding, query_embedding) < 0.3
)
-- Then enrich with AI
SELECT
  product_name,
  ai('Write marketing copy for: ' || product_name) as marketing_copy
FROM similar;
```

### Chat API + AI SQL Function

```python
# Chat interface generates query
chat_response = get_chat_response("Show data about X")

# Execute with AI enrichment
execute("""
  SELECT *, ai('Summarize: ' || description)
  FROM """ + chat_response.suggested_table
)
```

## Performance Considerations

| Feature         | Latency                 | Throughput      | Cost        |
| --------------- | ----------------------- | --------------- | ----------- |
| **AI UDF**      | Medium (1-3s per batch) | High (parallel) | Medium      |
| **Text-to-SQL** | Medium (2-5s)           | Medium          | Low         |
| **Chat API**    | Low-Medium (1-3s)       | Medium          | Medium-High |
| **Embeddings**  | Low (100ms)             | Very High       | Low         |

## When NOT to Use the AI SQL Function

❌ **Don't use the AI SQL function when:**

1. **You need real-time, sub-second responses**
   - AI calls take 1-2 seconds minimum
   - Use pre-computed results or caching

2. **Processing millions of rows**
   - 100 row batch limit
   - Consider batch processing offline

3. **Simple text operations**
   - Use SQL string functions instead
   - Example: Use `UPPER()` not `ai('make uppercase: ' || text)`

4. **Data already has labels/categories**
   - Query existing data
   - No need for AI if you have the answer

5. **Need deterministic results**
   - AI is non-deterministic (same input ≠ same output)
   - Use rules or SQL functions for consistency

## Quick Reference

| I want to...             | Use...        | Example                                        |
| ------------------------ | ------------- | ---------------------------------------------- |
| Process rows with AI     | AI UDF        | `SELECT ai('Classify: ' \|\| text) FROM table` |
| Ask questions in English | Text-to-SQL   | `nsql("What are top sales?")`                  |
| Build a chatbot          | Chat API      | `chat.completions.create(messages)`            |
| Search by meaning        | Vector Search | `WHERE distance(embed(query)) < 0.3`           |
| Test model quality       | Evals         | Define test cases and metrics                  |
| Generate embeddings      | Embeddings    | `embed(text, 'model-name')`                    |
| Store AI context         | Memory        | Configure memory in spicepod                   |

## Learn More

- **AI SQL Function** (this recipe): See [README.md](./README.md)
- **Text-to-SQL**: [../text-to-sql/README.md](../text-to-sql/README.md)
- **Chat & Tools**: [../openai_sdk/README.md](../openai_sdk/README.md)
- **Vector Search**: [../vectors/README.md](../vectors/) and [../search/README.md](../search/README.md)
- **Evaluations**: [../evals/README.md](../evals/README.md)
- **Memory**: [../llm-memory/README.md](../llm-memory/README.md)
