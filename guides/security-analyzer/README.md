# Building an Intelligent Security Copilot: Real-Time Data Access Pattern Analysis with Spice.ai

Data breaches often occur not through dramatic hacks, but through subtle patterns of seemingly legitimate database access. While traditional security tools focus on obvious threats like failed login attempts or known malware signatures, they often miss sophisticated insider threats or clever data exfiltration attempts that hide within normal-looking database queries.

In this guide, we'll build an intelligent security copilot using Spice.ai that can detect these subtle patterns. Unlike traditional rule-based systems, our solution will use AI to understand the context of database queries and identify potentially malicious patterns that might slip past conventional security tools.

## Why Database Query Pattern Analysis Matters

Consider this scenario: An engineer with legitimate database access begins running a series of seemingly innocent queries. Each query is valid and returns a reasonable amount of data. However, when analyzed together, these queries are systematically extracting sensitive customer information piece by piece. Traditional security tools might miss this because each individual query looks normal.

This is where AI-powered pattern analysis becomes crucial. By understanding the context and relationships between queries, we can detect:

- Sequential queries that piece by piece extract sensitive data
- Unusual access patterns for a user's role
- Subtle changes in query behavior that might indicate compromised credentials
- Complex data extraction attempts that stay just below traditional alerting thresholds

## Architecture Overview

Our solution will use Spice.ai to:

1. Ingest and process database query logs in real-time
2. Use AI to analyze query patterns and their context
3. Generate human-readable security insights

Let's build this step by step.

## Setting Up the Foundation

First, let's create a new Spice.ai project:

```bash
spice init query-pattern-analyzer
cd query-pattern-analyzer
```

## Designing the Data Model

We need to store query audit logs that capture all database activity. This can be setup using tools like `pgAudit`, but for this guide we'll just create a simple table.

```sql
-- Table for query audit logs
CREATE TABLE query_audit_logs (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    user_id TEXT,
    query_text TEXT,
    database_name TEXT,
    schema_name TEXT,
    client_ip TEXT,
    session_id TEXT,
    rows_affected INTEGER,
    execution_time_ms INTEGER,
    query_type TEXT
);

-- Create an index on timestamp for better query performance
CREATE INDEX idx_query_audit_timestamp ON query_audit_logs(timestamp);
```

Each field serves a specific purpose:

- `timestamp` tracks when queries occur, helping identify temporal patterns
- `user_id` and `session_id` help correlate related queries
- `query_text` allows analysis of the actual SQL being executed
- `rows_affected` helps identify bulk data extractions
- `schema_name` helps detect unusual cross-schema access patterns

## Configuring Spice.ai for Real-Time Analysis

The heart of our system is the Spice.ai configuration. We'll create a `spicepod.yaml` that defines:

- How to connect to our query logs
- How to process the data in real-time
- How to analyze patterns using AI

```yaml
version: v1
kind: Spicepod
name: query-pattern-analyzer

datasets:
  - from: postgres:query_audit_logs
    name: query_audit_logs
    time_column: timestamp
    time_format: timestamptz
    description: "Database query audit logs containing user activity"
    acceleration:
      enabled: true
      refresh_mode: append
      refresh_check_interval: 5s
      retention_check_enabled: true
      retention_period: 30d
    params:
      pg_host: ${env:PG_HOST}
      pg_port: ${env:PG_PORT}
      pg_db: ${env:PG_DB}
      pg_user: ${env:PG_USER}
      pg_pass: ${env:PG_PASS}
      pg_sslmode: disable
```

Let's break down these configuration choices:

- `refresh_mode: append` optimizes for real-time log ingestion by only appending new data based on the `time_column`
- `refresh_check_interval: 5s` provides near-real-time analysis
- `retention_period: 30d` keeps a month of history for pattern analysis

## Adding AI-Powered Analysis

The real power comes from our AI configuration. We'll use GPT-4 through Spice.ai's AI gateway, giving it specific security expertise:

```yaml
models:
  - name: security-analyzer
    from: openai:gpt-4o
    params:
      openai_api_key: ${env:OPENAI_API_KEY}
      tools: auto
      system_prompt: |
        You are a database security expert analyzing SQL query patterns for potential security risks. 
        
        Focus on detecting:
        1. Potential data exfiltration attempts
        2. Suspicious query patterns that could indicate insider threats
        3. Unusual data access patterns for user roles
        4. Sequential queries that together could extract sensitive data
        
        Consider factors like:
        - Query complexity and size of data accessed
        - Historical patterns for users/roles
        - Temporal patterns (time of day, frequency)
        - Combinations of queries that could bypass security controls
        
        Provide specific, actionable recommendations and clear explanations of risks.
```

This configuration tells Spice.ai to:

- Instruct the LLM to use tools to run SQL queries and get the schema of the datasets. This is what enables the LLM controlled access to the data it needs to analyze.
- Sets the `system_prompt` to provide the LLM with specific instructions and context for its analysis.

## Adding Pattern Analysis Views

To help our AI analyze patterns effectively, we'll create a view that aggregates user behavior:

```yaml
views:
  - name: user_query_patterns
    sql: |
      WITH user_stats AS (
        SELECT 
          user_id,
          COUNT(*) as query_count,
          AVG(rows_affected) as avg_rows,
          MAX(rows_affected) as max_rows,
          COUNT(DISTINCT schema_name) as schema_count
        FROM query_audit_logs
        WHERE timestamp > NOW() - INTERVAL '1 hour'
        GROUP BY user_id
      )
      SELECT 
        us.*,
        ql.query_text,
        ql.timestamp
      FROM user_stats us
      JOIN query_audit_logs ql ON us.user_id = ql.user_id
      WHERE ql.timestamp > NOW() - INTERVAL '1 hour'
```

This view provides critical context by:

- Calculating query patterns per user
- Tracking the scope of data access
- Identifying cross-schema access patterns
- Maintaining hourly statistics for baseline comparison

## Building the Analysis Engine

Now let's create the Python script that ties everything together. This script will:

1. Monitor query patterns in real-time
2. Request AI analysis through Spice.ai
3. Process and report security insights

Here's our `analyzer.py`:

```python
# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "requests"
# ]
# ///
import requests
import json
import time
from datetime import datetime, timedelta
import os

class QueryPatternAnalyzer:
    def __init__(self):
        self.spice_url = "http://localhost:8090"
    
    def analyze_patterns(self):
        while True:
            try:
                # Get recent query patterns for analysis
                analysis_prompt = self.build_analysis_prompt()
                
                print("Analyzing patterns...")
                # Ask Spice.ai's LLM to analyze the patterns
                response = requests.post(
                    f"{self.spice_url}/v1/chat/completions",
                    json={
                        "model": "security-analyzer",
                        "messages": [
                            {"role": "user", "content": analysis_prompt}
                        ]
                    }
                )
                
                analysis = response.json()
                self.handle_analysis_results(analysis)
                
            except Exception as e:
                print(f"Error during analysis: {e}")
            
            time.sleep(30)  # Run analysis every 30 seconds
    
    def build_analysis_prompt(self):
        return """
        Analyze the recent query patterns in the user_query_patterns table for suspicious activity.
        Consider the following:
        1. Users accessing unusually large amounts of data
        2. Users querying tables they don't normally access
        3. Sequential patterns that could indicate data harvesting
        4. Queries running at unusual times
        
        Provide your analysis with:
        1. Description of any suspicious patterns
        2. Severity level (low, medium, high)
        3. Specific recommendations for security team
        """
    
    def handle_analysis_results(self, analysis):
        try:
            content = analysis['choices'][0]['message']['content']
            print(content)
            
        except Exception as e:
            print(f"Error handling analysis results: {e}")

if __name__ == "__main__":
    print("Starting Query Pattern Analyzer")
    analyzer = QueryPatternAnalyzer()
    analyzer.analyze_patterns()
```

## Testing the System

To see our security copilot in action, let's simulate some suspicious patterns:

```sql
-- Normal query - single department access
INSERT INTO query_audit_logs (user_id, query_text, database_name, schema_name, rows_affected, query_type)
VALUES 
('alice', 'SELECT * FROM employees WHERE department_id = 5', 'hr_db', 'public', 10, 'SELECT');

-- Suspicious: Large data extraction
INSERT INTO query_audit_logs (user_id, query_text, database_name, schema_name, rows_affected, query_type)
VALUES 
('bob', 'SELECT * FROM employees', 'hr_db', 'public', 5000, 'SELECT');

-- Suspicious: Cross-schema access
INSERT INTO query_audit_logs (user_id, query_text, database_name, schema_name, rows_affected, query_type)
VALUES 
('charlie', 'SELECT * FROM finance.salary_data', 'hr_db', 'finance', 100, 'SELECT'),
('charlie', 'SELECT * FROM hr.employee_reviews', 'hr_db', 'hr', 200, 'SELECT'),
('charlie', 'SELECT * FROM security.access_logs', 'hr_db', 'security', 300, 'SELECT');

-- Suspicious: Sequential data harvesting
INSERT INTO query_audit_logs (user_id, query_text, database_name, schema_name, rows_affected, query_type)
VALUES 
('dave', 'SELECT email FROM customers WHERE region = ''West''', 'sales_db', 'public', 50, 'SELECT'),
('dave', 'SELECT phone FROM customers WHERE region = ''East''', 'sales_db', 'public', 50, 'SELECT'),
('dave', 'SELECT address FROM customers WHERE region = ''South''', 'sales_db', 'public', 50, 'SELECT');
```

Our AI analysis provides rich context about these patterns:

```plaintext
Based on the recent query patterns, several concerning behaviors have been identified:

1. Sequential Data Harvesting (High Severity)
   User 'dave' is systematically extracting customer PII (email, phone, address) across different regions.
   While each query appears legitimate, the pattern suggests a methodical data gathering operation.
   
   Recommendations:
   - Implement controls to detect cross-region PII access patterns
   - Review dave's role requirements for customer data access
   - Consider implementing aggregate-only views for customer data

2. Bulk Data Access (Medium Severity)
   User 'bob' extracted 5000 employee records in a single query.
   This could be legitimate ETL work but requires verification.
   
   Recommendations:
   - Verify if this is a scheduled data export
   - Implement row-level security if bulk access isn't required
   - Add rate limiting for large data retrievals

3. Cross-Schema Access (High Severity)
   User 'charlie' accessed sensitive tables across finance, HR, and security schemas.
   This unusual access pattern could indicate privilege escalation or credential compromise.
   
   Recommendations:
   - Immediately review charlie's role permissions
   - Investigate if this access combines to expose sensitive relationships
   - Implement schema-level access monitoring
```

## Future Enhancements

This system could be enhanced in several ways:

1. Use structured output to generate results in a format that could be inserted into another table
2. Implement automated responses for high-severity incidents
3. Add security expert feedback loops to improve detection
4. Integrate with existing security tools and ticketing systems

## Conclusion

By combining Spice.ai's real-time data processing with AI-powered analysis, we've built a sophisticated security copilot that can detect subtle patterns of potentially malicious database access. This system demonstrates how modern AI can enhance security beyond traditional rule-based approaches, providing rich context and actionable insights for security teams.
