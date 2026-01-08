# Hybrid Search & Real Time Indexing

In today's hyper-connected digital ecosystem, social media represents an untapped goldmine of actionable intelligence for organizations. Beyond traditional metrics, these platforms offer unprecedented visibility into market dynamics, consumer sentiment trajectories, demographic clustering patterns, and emergent behavioral signals that can fundamentally transform go-to-market strategies and competitive positioning.

Spice AI revolutionizes this paradigm by enabling organizations to harness real-time data streams at the edge, creating a sophisticated indexing and search infrastructure that transforms raw social signals into strategic insights. Our hybrid search architecture combines the precision of lexical matching with the nuanced understanding of semantic vector embeddings, powered by advanced Reciprocal Rank Fusion (RRF) algorithms that intelligently weigh and merge multiple search modalities.

This cookbook demonstrates these transformative capabilities through a comprehensive implementation that indexes and analyzes real-time Bluesky social media streams, showcasing how modern organizations can build intelligent, responsive data architectures that scale from edge to enterprise.

## Step 1. Set up

Clone this repository:

```bash
git clone https://github.com/spiceai/cookbook.git
cd cookbook/search
```

Install `websocat` and set up Python:

```bash
brew install websocat
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Step 2. Preview and capture data

We can read real-time posts using [Bluesky's Jetstream relay service](https://docs.bsky.app/blog/jetstream). Use `websocat` to preview the stream and ensure that the relay is functional:

```bash
websocat wss://jetstream2.us-east.bsky.network/subscribe\?wantedCollections=app.bsky.feed.post | jq

{
  "did": "did:plc:ei3py27iy2orpykshoudxnls",
  "time_us": 1758813540806266,
  "kind": "commit",
  "commit": {
    "rev": "3lzoas6yujs2z",
    "operation": "create",
    "collection": "app.bsky.feed.post",
    "rkey": "3lzoas6nbhs2e",
    "record": {
      "$type": "app.bsky.feed.post",
      "createdAt": "2025-09-25T15:19:00.163Z",
      "langs": [
        "ja"
      ],
      "text": "🧐🧐🧐🧐🧐"
    },
    "cid": "bafyreighkijp5zyclu6qdjtfskmr65ttvxvedvqmfvwgfyf6iaq4jfdje4"
  }
}
...

^C
```

Let's convert this stream into a Parquet file that Spice AI can read. Let this run for a little while, until satisfied with the total number collected. Run again at any time to resume appending:

```bash
websocat wss://jetstream2.us-east.bsky.network/subscribe\?wantedCollections=app.bsky.feed.post | ./generate_parquet.py
[info] boot!
[info] INSERTED 250 ROWS; TOTAL 250
[info] INSERTED 250 ROWS; TOTAL 500
```

## Step 3. Start Spice and Search!

_In a new terminal_, start Spice. It will embed, full-text index, and ingest the latest data. Additionally, the `file` connector is using fsnotify to watch it for updates, to eagerly ingest data.

```bash
spice run
```

You should see this output:

```bash
2025-09-26T15:21:38.154354Z  INFO spiced: Starting runtime v1.8.0-unstable-build.71ac09ff2+models.metal
2025-09-26T15:21:38.225135Z  INFO runtime::init::caching: Initialized results cache; max size: 128.00 MiB, item ttl: 1s
2025-09-26T15:21:38.229824Z  INFO runtime::init::caching: Initialized search results cache; max size: 128.00 MiB, item ttl: 1s
2025-09-26T15:21:38.230575Z  INFO runtime::init::caching: Initialized embeddings cache; max size: 128.00 MiB, item ttl: 1s
2025-09-26T15:21:38.658824Z  INFO runtime::opentelemetry: Spice Runtime OpenTelemetry listening on 127.0.0.1:50052
2025-09-26T15:21:38.658888Z  INFO runtime::flight: Spice Runtime Flight listening on 127.0.0.1:50051
2025-09-26T15:21:38.678694Z  INFO runtime::http: Spice Runtime HTTP listening on 127.0.0.1:8090
2025-09-26T15:21:47.550688Z  INFO runtime::init::embedding: Embedding Model potion_128m ready
2025-09-26T15:21:47.659106Z  INFO runtime::init::dataset: Dataset bluesky_posts initializing...
2025-09-26T15:21:47.730735Z  INFO runtime::dataconnector::file: Watching changes to bluesky_posts.parquet
2025-09-26T15:21:47.730999Z  INFO runtime::init::dataset: Dataset bluesky_posts registered (file://bluesky_posts.parquet), acceleration (duckdb:file, append), results cache enabled.
2025-09-26T15:21:47.740354Z  INFO runtime::accelerated_table::refresh_task: Loading data for dataset bluesky_posts
2025-09-26T15:21:57.885819Z  INFO runtime::accelerated_table::refresh_task: Dataset bluesky_posts received 38,101 records
2025-09-26T15:21:58.507599Z  INFO runtime::accelerated_table::refresh_task: Loaded 38,101 rows (54.72 MiB) for dataset bluesky_posts in 10s 775ms.
2025-09-26T15:21:58.550191Z  INFO runtime: All components are loaded. Spice runtime is ready!
2025-09-26T15:22:20.335633Z  INFO runtime::accelerated_table::refresh_task: Loading data for dataset bluesky_posts
2025-09-26T15:22:21.960722Z  INFO runtime::accelerated_table::refresh_task: Loaded 251 rows (339.49 kiB) for dataset bluesky_posts in 1s 656ms.
```

_In a new terminal_, start the Spice SQL REPL:

```bash
spice sql
```

### Basic Hybrid Search

Combine exact text matching with semantic similarity for comprehensive results:

```sql
-- Find posts about space travel using both exact text and semantic search
select fused_score, text, created_at, langs
from rrf(
    text_search(bluesky_posts, 'space travel'),
    vector_search(bluesky_posts, 'space travel')
) order by fused_score desc limit 10;
```

### Weighted Ranking

Boost specific search strategies using `rank_weight` to prioritize different result types:

```sql
-- Heavily prioritize semantic similarity over exact text matches
select fused_score, text, rkey
from rrf(
    text_search(bluesky_posts, 'artificial intelligence', rank_weight => 50.0),
    vector_search(bluesky_posts, 'AI machine learning', rank_weight => 200.0)
) order by fused_score desc limit 15;

-- Prioritize exact mentions while including semantic results
select fused_score, text, created_at
from rrf(
    text_search(bluesky_posts, 'climate change', rank_weight => 300.0),
    vector_search(bluesky_posts, 'environmental sustainability', rank_weight => 100.0)
) order by fused_score desc limit 20;
```

### Recency-Boosted Search

Use temporal information to surface recent content with exponential or linear decay:

```sql
-- Recent posts get higher scores with exponential decay
select fused_score, text, created_at, rkey
from rrf(
    text_search(bluesky_posts, 'breaking news'),
    vector_search(bluesky_posts, 'latest updates'),
    time_column => 'created_at',
    recency_decay => 'exponential',
    decay_constant => 0.05,
    decay_scale_secs => 3600  -- 1 hour scale
) order by fused_score desc limit 10;

-- Linear decay for trending topics over the last day
select fused_score, text, created_at
from rrf(
    text_search(bluesky_posts, 'trending now'),
    vector_search(bluesky_posts, 'viral popular'),
    time_column => 'created_at',
    recency_decay => 'linear',
    decay_window_secs => 86400  -- 24 hours
) order by fused_score desc limit 15;
```

### Advanced Parameter Tuning

Fine-tune the RRF algorithm using the smoothing parameter `k`:

```sql
-- Lower k value for more aggressive ranking differences
select fused_score, text, langs
from rrf(
    text_search(bluesky_posts, 'technology innovation'),
    vector_search(bluesky_posts, 'tech startups'),
    k => 20.0  -- More aggressive than default 60.0
) order by fused_score desc limit 12;

-- Higher k for smoother score distribution
select fused_score, text, created_at
from rrf(
    text_search(bluesky_posts, 'social media'),
    vector_search(bluesky_posts, 'online platforms'),
    k => 120.0  -- Smoother than default 60.0
) order by fused_score desc limit 10;
```

### Multi-Language and Content Analysis

Combine vector search queries across languages for similar concepts:

```sql
-- Find posts about "breaking news" with semantic query in Spanish, but keyword match in English
select fused_score, text, langs, created_at
from rrf(
    vector_search(bluesky_posts, 'ultimas noticias', rank_weight => 100),
    text_search(bluesky_posts, 'news'),
    time_column => 'created_at',
    recency_decay => 'exponential',
    decay_constant => 0.05,
    decay_scale_secs => 3600  -- 1 h
) where trim(text) != '' order by fused_score desc limit 15;

-- Find posts about breaking news using two semantic queries in Spanish, but filter results for English
select fused_score, text, langs, created_at
from rrf(
    vector_search(bluesky_posts, 'ultimas noticias'),
    vector_search(bluesky_posts, 'noticias de ultima hora'),
    time_column => 'created_at',
    recency_decay => 'exponential',
    decay_constant => 0.05,
    decay_scale_secs => 3600  -- 1 h
) where langs like '%en%' and trim(text) != '' order by fused_score desc limit 15;
```

## Step 4. Enable agentic support

Stop Spice, and go to `spicepod.yml` and uncomment the `models` block. Update the `.env` file with your OpenAI key. Then start Spice again.

```bash
spice run
```

Afterwards, begin a chat session:

```bash
spice chat
```

Try to query for insights using natural language:

```bash
chat> Can you see how many posts there are in the last day about photography?
There were 676 posts about photography in the last day on the Bluesky platform. If you have any further questions or need additional insights, feel free to ask!

Time: 10.12s (first token 9.50s). Tokens: 1635. Prompt: 1588. Completion: 47 (75.62/s).

chat> Can you show me a breakdown by language?
Here's a breakdown of the posts about photography in the last day by language:

1. **English (en):** 596 posts
2. **German (de):** 41 posts
3. **Finnish (fi):** 20 posts
4. **Unspecified:** 17 posts
5. **English, Hebrew, Sanskrit (en, he, sa):** 1 post
6. **Dutch (nl):** 1 post

If you need further analysis or details, feel free to ask!
```
