#!/usr/bin/env python3
"""
Generate articles.parquet — sample data for the Spice search engine example.

Usage:
  pip install pandas pyarrow faker
  python generate_data.py [--rows N] [--out PATH]
"""

import argparse
import random
from itertools import product

import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
from faker import Faker

# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------
parser = argparse.ArgumentParser()
parser.add_argument("--rows", type=int, default=100)
parser.add_argument("--out", default="articles.parquet")
args = parser.parse_args()

TARGET_ROWS = args.rows
OUT_PATH = args.out

fake = Faker()
random.seed(42)
Faker.seed(42)

# ---------------------------------------------------------------------------
# Taxonomy
# ---------------------------------------------------------------------------
TOPICS = [
    {
        "category": "machine_learning",
        "subtopics": [
            "neural networks",
            "deep learning",
            "gradient descent",
            "backpropagation",
            "transformer models",
            "attention mechanisms",
            "fine-tuning",
            "transfer learning",
            "reinforcement learning",
            "generative adversarial networks",
            "diffusion models",
            "contrastive learning",
            "self-supervised learning",
            "few-shot learning",
            "model pruning",
            "knowledge distillation",
            "hyperparameter tuning",
            "AutoML",
            "federated learning",
            "meta-learning",
        ],
        "title_templates": [
            "A Practical Guide to {sub}",
            "{sub} Explained: From Theory to Production",
            "How {sub} Is Transforming AI Applications",
            "Deep Dive: {sub} in Modern ML Pipelines",
            "Benchmarking {sub} Across Popular Frameworks",
            "Common Pitfalls in {sub} and How to Avoid Them",
            "Scaling {sub} to Billions of Parameters",
            "{sub}: State of the Art in {year}",
            "Understanding {sub} Through Mathematical Intuition",
            "Implementing {sub} Without a PhD",
        ],
    },
    {
        "category": "search_engines",
        "subtopics": [
            "BM25 ranking",
            "inverted indexes",
            "vector similarity search",
            "semantic search",
            "full-text search",
            "dense retrieval",
            "sparse retrieval",
            "hybrid search",
            "reciprocal rank fusion",
            "embedding models",
            "approximate nearest neighbor",
            "HNSW graphs",
            "product quantization",
            "query expansion",
            "relevance feedback",
            "learning to rank",
            "query rewriting",
            "cross-encoder reranking",
            "bi-encoder retrieval",
            "knowledge graph search",
        ],
        "title_templates": [
            "How {sub} Powers Modern Search",
            "{sub} Under the Hood: Architecture and Trade-offs",
            "Building Production-Ready {sub} Systems",
            "Evaluating {sub}: Metrics That Matter",
            "{sub} at Scale: Lessons from the Field",
            "Comparing {sub} Approaches in {year}",
            "A Developer's Guide to {sub}",
            "When to Use {sub} vs Traditional Keyword Search",
            "Optimising {sub} for Low-Latency Workloads",
            "Open-Source Tools for {sub}",
        ],
    },
    {
        "category": "data_engineering",
        "subtopics": [
            "Apache Parquet",
            "columnar storage",
            "data pipelines",
            "ETL workflows",
            "stream processing",
            "Apache Kafka",
            "data lakes",
            "schema evolution",
            "Apache Iceberg",
            "Delta Lake",
            "data mesh",
            "data contracts",
            "change data capture",
            "Apache Spark",
            "dbt transformations",
            "data quality checks",
            "lineage tracking",
            "metadata management",
            "batch ingestion",
            "real-time ingestion",
        ],
        "title_templates": [
            "{sub}: The Definitive Overview",
            "Why {sub} Is Essential for Modern Data Teams",
            "Getting Started with {sub} in {year}",
            "{sub} Best Practices for Large-Scale Workloads",
            "Migrating to {sub}: A Step-by-Step Guide",
            "Debugging {sub} in Production",
            "{sub} vs Traditional Approaches: A Comparison",
            "How {sub} Reduces Engineering Toil",
            "Monitoring {sub} Pipelines at Scale",
            "Cost Optimisation Strategies for {sub}",
        ],
    },
    {
        "category": "databases",
        "subtopics": [
            "SQL query optimisation",
            "index design",
            "ACID transactions",
            "NoSQL modelling",
            "vector databases",
            "distributed databases",
            "replication strategies",
            "sharding",
            "MVCC",
            "write-ahead logging",
            "B-tree indexes",
            "LSM-tree storage",
            "columnar databases",
            "time-series databases",
            "graph databases",
            "in-memory databases",
            "NewSQL",
            "CockroachDB",
            "FoundationDB",
            "database connection pooling",
        ],
        "title_templates": [
            "{sub} for High-Throughput Applications",
            "A Deep Dive into {sub}",
            "{sub}: Concepts Every Engineer Should Know",
            "Production Lessons from Running {sub} at Scale",
            "Choosing Between {sub} and Alternatives",
            "How {sub} Impacts Query Performance",
            "{sub} Internals Explained",
            "Migrating from Legacy Systems to {sub}",
            "Benchmarking {sub} in Cloud Environments",
            "Debugging Slow Queries with {sub}",
        ],
    },
    {
        "category": "cloud_infrastructure",
        "subtopics": [
            "Kubernetes orchestration",
            "container deployments",
            "service meshes",
            "auto-scaling",
            "observability stacks",
            "OpenTelemetry",
            "cost optimisation",
            "serverless functions",
            "GitOps workflows",
            "infrastructure as code",
            "zero-trust networking",
            "secrets management",
            "multi-cloud strategies",
            "disaster recovery",
            "chaos engineering",
            "FinOps",
            "edge computing",
            "platform engineering",
            "developer portals",
            "SLO management",
        ],
        "title_templates": [
            "{sub} in Practice: Real-World Patterns",
            "How {sub} Enables Reliable Systems",
            "{sub} for Platform Engineers",
            "Scaling {sub} in Enterprise Environments",
            "Automating {sub} with Modern Tooling",
            "{sub}: A Comprehensive Tutorial for {year}",
            "Common Mistakes with {sub} and How to Fix Them",
            "Security Considerations for {sub}",
            "How We Cut Costs by Optimising {sub}",
            "Building Self-Service Infrastructure with {sub}",
        ],
    },
    {
        "category": "software_engineering",
        "subtopics": [
            "clean code principles",
            "design patterns",
            "microservices architecture",
            "domain-driven design",
            "event sourcing",
            "CQRS",
            "API design",
            "test-driven development",
            "continuous integration",
            "code review practices",
            "technical debt",
            "refactoring strategies",
            "distributed tracing",
            "circuit breakers",
            "rate limiting",
            "idempotency",
            "concurrency models",
            "async programming",
            "type systems",
            "compiler design",
        ],
        "title_templates": [
            "Applying {sub} in Real Projects",
            "{sub}: From Basics to Advanced Techniques",
            "How {sub} Improves System Reliability",
            "A Pragmatic Guide to {sub}",
            "Interview Questions on {sub} and How to Answer Them",
            "{sub} Patterns Every Senior Engineer Should Know",
            "Refactoring Legacy Code with {sub}",
            "When {sub} Makes Sense (and When It Doesn't)",
            "{sub} in Distributed Systems",
            "Teaching {sub} to Junior Developers",
        ],
    },
    {
        "category": "security",
        "subtopics": [
            "zero-trust architecture",
            "OAuth 2.0",
            "JWT authentication",
            "supply chain security",
            "SBOM",
            "vulnerability scanning",
            "penetration testing",
            "secrets rotation",
            "mTLS",
            "RBAC",
            "OWASP top 10",
            "runtime security",
            "SAST and DAST",
            "CVE management",
            "encryption at rest",
            "key management",
            "phishing prevention",
            "incident response",
            "threat modelling",
            "compliance automation",
        ],
        "title_templates": [
            "Understanding {sub} in Cloud-Native Environments",
            "Implementing {sub} Without Slowing Down Development",
            "{sub} for Distributed Systems",
            "How {sub} Reduces Your Attack Surface",
            "A Practical Guide to {sub} in {year}",
            "Auditing {sub} Configurations at Scale",
            "Automating {sub} in CI/CD Pipelines",
            "{sub}: Myths and Realities",
            "Responding to {sub} Incidents Effectively",
            "Open-Source Tools for {sub}",
        ],
    },
    {
        "category": "developer_experience",
        "subtopics": [
            "developer portals",
            "internal developer platforms",
            "CLI tooling",
            "IDE extensions",
            "local development environments",
            "devcontainers",
            "debugging techniques",
            "profiling tools",
            "documentation-as-code",
            "API mocking",
            "feature flags",
            "trunk-based development",
            "monorepo tooling",
            "dependency management",
            "build caching",
            "test parallelisation",
            "code generation",
            "linting and formatting",
            "onboarding automation",
            "developer productivity metrics",
        ],
        "title_templates": [
            "Improving {sub} Across Engineering Teams",
            "{sub}: Building a Great Developer Experience",
            "How {sub} Speeds Up Delivery",
            "Measuring the Impact of {sub}",
            "Setting Up {sub} from Scratch",
            "{sub} Tooling in {year}: What Works",
            "How We Adopted {sub} at Our Company",
            "The Case for Investing in {sub}",
            "{sub} for Remote Engineering Teams",
            "Automating {sub} to Eliminate Toil",
        ],
    },
]

CROSS_TOPIC_SEEDS = [
    {
        "title": "Vector Search Inside PostgreSQL with pgvector",
        "category": "databases",
        "keywords": ["vector databases", "BM25 ranking", "SQL query optimisation", "embedding models"],
    },
    {
        "title": "Running Elasticsearch on Kubernetes: Lessons Learned",
        "category": "cloud_infrastructure",
        "keywords": ["Kubernetes orchestration", "observability stacks", "inverted indexes"],
    },
    {
        "title": "ETL Pipelines for Machine Learning Feature Stores",
        "category": "data_engineering",
        "keywords": ["Apache Parquet", "data pipelines", "transformer models", "fine-tuning"],
    },
    {
        "title": "Securing ML Model Serving Endpoints",
        "category": "security",
        "keywords": ["zero-trust architecture", "mTLS", "neural networks", "API design"],
    },
    {
        "title": "Observability for Real-Time Data Pipelines",
        "category": "data_engineering",
        "keywords": ["OpenTelemetry", "Apache Kafka", "distributed tracing", "SLO management"],
    },
    {
        "title": "Cost-Aware AutoML on Kubernetes",
        "category": "machine_learning",
        "keywords": ["AutoML", "Kubernetes orchestration", "cost optimisation", "hyperparameter tuning"],
    },
    {
        "title": "Hybrid Search with Elasticsearch and pgvector",
        "category": "search_engines",
        "keywords": ["hybrid search", "reciprocal rank fusion", "vector databases", "inverted indexes"],
    },
    {
        "title": "Developer Portals Powered by LLMs",
        "category": "developer_experience",
        "keywords": ["developer portals", "transformer models", "API design", "documentation-as-code"],
    },
    {
        "title": "Zero-Trust Networking for Microservices",
        "category": "security",
        "keywords": ["zero-trust architecture", "service meshes", "mTLS", "microservices architecture"],
    },
    {
        "title": "DuckDB as an Embedded Analytics Engine",
        "category": "databases",
        "keywords": ["columnar databases", "Apache Parquet", "SQL query optimisation", "data lakes"],
    },
]

# ---------------------------------------------------------------------------
# Content generation
# ---------------------------------------------------------------------------
INTRO_TEMPLATES = [
    "{title} has become one of the most discussed topics among practitioners in {year}. "
    "This article examines core ideas around {kw1}, {kw2}, and {kw3}.",
    "Few subjects generate as much debate as {title}. "
    "In this post we take a structured look at {kw1} and its relationship to {kw2}.",
    "The rise of {kw1} has put {title} firmly on the radar of engineering teams worldwide. "
    "Here we break down the key concepts, starting with {kw2} and {kw3}.",
    "If you have ever struggled to understand {title}, you are not alone. "
    "We will demystify {kw1} and explain why {kw2} matters more than ever.",
    "In {year}, {title} continues to evolve rapidly. "
    "This comprehensive guide covers {kw1}, {kw2}, and practical guidance on {kw3}.",
]

BODY_SENTENCE_POOLS = [
    "One of the most important considerations when working with {kw} is understanding its performance implications at scale.",
    "Teams that have adopted {kw} report significant improvements in both reliability and developer velocity.",
    "The relationship between {kw} and system latency is often underappreciated.",
    "Recent benchmarks suggest that {kw} outperforms legacy approaches by up to an order of magnitude in read-heavy workloads.",
    "Choosing the right abstraction for {kw} requires a clear understanding of your consistency and availability requirements.",
    "A common misconception about {kw} is that it requires specialised hardware—in practice, commodity cloud instances suffice.",
    "Observability tooling plays a critical role when debugging issues related to {kw} in production.",
    "The open-source ecosystem around {kw} has matured considerably since its initial release.",
    "Engineers often underestimate the operational overhead of {kw} when evaluating it for the first time.",
    "Pair {kw} with a solid CI/CD pipeline to catch regressions early.",
    "Security implications of {kw} are frequently discussed but rarely acted on systematically.",
    "Integrating {kw} into an existing architecture typically requires incremental migration rather than a big-bang rewrite.",
    "Documentation quality is a persistent challenge in the {kw} ecosystem.",
    "Load testing is essential before relying on {kw} in a high-traffic environment.",
    "Proper indexing strategy is inseparable from any discussion of {kw}.",
]

CLOSING_TEMPLATES = [
    "In conclusion, mastering {kw} is increasingly a prerequisite for engineers working on {category} problems. "
    "We encourage you to experiment with the techniques described here and share your findings with the community.",
    "As the field of {category} advances, {kw} will only grow in importance. "
    "The patterns outlined in this article provide a solid foundation for further exploration.",
    "Understanding {kw} deeply—not just at the API surface—will set you apart as a practitioner in {category}. "
    "We hope this guide serves as a useful reference.",
    "The journey into {kw} is long but rewarding. "
    "Start small, measure rigorously, and iterate—that is the path to production-grade {category} systems.",
]


def make_body(title: str, keywords: list[str], category: str, year: int) -> str:
    kws = keywords[:]
    random.shuffle(kws)
    kw1, kw2, kw3 = (kws + kws)[:3]

    intro = random.choice(INTRO_TEMPLATES).format(
        title=title, year=year, kw1=kw1, kw2=kw2, kw3=kw3
    )

    sentences = []
    for _ in range(random.randint(2, 3)):
        kw = random.choice(keywords)
        tmpl = random.choice(BODY_SENTENCE_POOLS)
        sentences.append(tmpl.format(kw=kw))

    sentences += fake.sentences(nb=1)
    random.shuffle(sentences)

    closing_kw = random.choice(keywords)
    closing = random.choice(CLOSING_TEMPLATES).format(
        kw=closing_kw, category=category
    )

    return " ".join([intro, " ".join(sentences), closing])


# ---------------------------------------------------------------------------
# Build seed pool
# ---------------------------------------------------------------------------
seed_pool: list[dict] = []
year = 2025

for topic in TOPICS:
    for sub, tmpl in product(topic["subtopics"], topic["title_templates"]):
        title = tmpl.format(sub=sub.title(), year=year)
        seed_pool.append(
            {
                "title": title,
                "category": topic["category"],
                "keywords": topic["subtopics"],
                "primary_kw": sub,
            }
        )

random.shuffle(seed_pool)

# ---------------------------------------------------------------------------
# Generate records
# ---------------------------------------------------------------------------
records = []

for i, seed in enumerate(CROSS_TOPIC_SEEDS, start=1):
    kws = seed["keywords"]
    records.append(
        {
            "id": i,
            "title": seed["title"],
            "category": seed["category"],
            "content": make_body(seed["title"], kws, seed["category"], year),
        }
    )

doc_id = len(CROSS_TOPIC_SEEDS) + 1
remaining = TARGET_ROWS - len(CROSS_TOPIC_SEEDS)
pool_cycle = (seed_pool * ((remaining // len(seed_pool)) + 2))[:remaining]

for seed in pool_cycle:
    kws = seed["keywords"]
    title = seed["title"]

    qualifiers = ["", "", "", "How to Use ", "Why ", "When to Use ", ""]
    q = random.choice(qualifiers)
    if q and not title.startswith(("How", "Why", "When", "A ", "Building", "Running")):
        title = q + title[0].lower() + title[1:]

    records.append(
        {
            "id": doc_id,
            "title": title,
            "category": seed["category"],
            "content": make_body(title, kws, seed["category"], year),
        }
    )
    doc_id += 1

# ---------------------------------------------------------------------------
# Write Parquet
# ---------------------------------------------------------------------------
df = pd.DataFrame(records)

schema = pa.schema(
    [
        pa.field("id", pa.int32()),
        pa.field("title", pa.string()),
        pa.field("category", pa.string()),
        pa.field("content", pa.string()),
    ]
)

table = pa.Table.from_pandas(df, schema=schema, preserve_index=False)
pq.write_table(table, OUT_PATH, compression="snappy")

print(f"Wrote {len(records):,} records to {OUT_PATH}")
print(df["category"].value_counts().to_string())
