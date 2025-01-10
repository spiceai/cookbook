# Building a Real-Time Data Access Pattern Analyzer with Spice.ai

This guide will demonstrate how to build an intelligent security system that monitors database query patterns to detect potential data exfiltration or insider threats. Unlike simple rule-based systems, this analyzer uses AI to understand query context and identify subtle patterns that could indicate security risks.

## What We'll Build

A system leveraging Spice.ai that:

- Monitors database query logs in real-time
- Analyzes query patterns using AI
- Detects potential data exfiltration attempts
- Provides context-aware security recommendations

## Prerequisites

- Basic SQL knowledge
- PostgreSQL database for storing query logs
- Spice.ai installed ([Installation instructions](https://docs.spiceai.org/getting-started))
- OpenAI API key for the LLM component
- `uv` installed for running Python scripts ([Installation instructions](https://docs.astral.sh/uv/getting-started/installation/))

## Step 1: Set Up the Project

```bash
# Create a new Spice project
spice init query-pattern-analyzer
cd query-pattern-analyzer
```

## Step 2: Create Query Audit Log Tables

First, let's create tables in PostgreSQL to store query audit logs and analysis results:

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

## Step 3: Configure the Spicepod

Create a `spicepod.yaml` file:

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

models:
  - name: security-analyzer
    from: openai:gpt-4
    params:
      openai_api_key: ${env:OPENAI_API_KEY}
      system_prompt: |
        You are a database security expert analyzing SQL query patterns for potential security risks. 
        You have access to historical expert feedback on past incidents through the historical_feedback view.
        
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
        - Past expert feedback on similar patterns
        
        When analyzing patterns:
        1. First check the historical_feedback view for similar patterns
        2. Consider expert feedback when assessing new patterns
        3. If experts have marked similar patterns as 'expected', adjust severity accordingly
        4. Pay special attention to patterns similar to confirmed 'incidents'
        
        Provide specific, actionable recommendations and clear explanations of risks, referencing relevant historical feedback when available.
      tools: sql, table_schema

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

## Step 4: Set Up Environment Variables

Create a `.env` file:

```bash
PG_USER=your_postgres_user
PG_PASS=your_postgres_password
PG_DB=your_postgres_database
PG_HOST=localhost
PG_PORT=5432
OPENAI_API_KEY=your_openai_api_key
```

## Step 5: Create the Pattern Analyzer Script

Create `analyzer.py`:

```python
# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "psycopg2-binary",
#     "requests",
#     "python-dotenv",
# ]
# ///
import psycopg2
import requests
import json
import time
from datetime import datetime, timedelta
from dotenv import load_dotenv
import os

class QueryPatternAnalyzer:
    def __init__(self):
        # Load environment variables from .env file
        load_dotenv()
        
        # Build connection string from environment variables
        db_params = {
            'dbname': os.getenv('PG_DB'),
            'user': os.getenv('PG_USER'),
            'password': os.getenv('PG_PASS'),
            'host': os.getenv('PG_HOST'),
            'port': os.getenv('PG_PORT')
        }
        
        self.conn = psycopg2.connect(**db_params)
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
        Analyze the recent query patterns in the user_query_patterns view for suspicious activity.
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

## Step 6: Start the System

1. Start the Spice runtime:

```bash
spice run
```

2. In a new terminal, start the analyzer:

```bash
uv run analyzer.py
```

## Step 7: Testing the System

Let's simulate some suspicious query patterns:

```sql
-- Simulate normal user behavior
INSERT INTO query_audit_logs (user_id, query_text, database_name, schema_name, rows_affected, query_type)
VALUES 
('alice', 'SELECT * FROM employees WHERE department_id = 5', 'hr_db', 'public', 10, 'SELECT');

-- Simulate suspicious pattern: Large data extraction
INSERT INTO query_audit_logs (user_id, query_text, database_name, schema_name, rows_affected, query_type)
VALUES 
('bob', 'SELECT * FROM employees', 'hr_db', 'public', 5000, 'SELECT');

-- Simulate suspicious pattern: Accessing multiple schemas
INSERT INTO query_audit_logs (user_id, query_text, database_name, schema_name, rows_affected, query_type)
VALUES 
('charlie', 'SELECT * FROM finance.salary_data', 'hr_db', 'finance', 100, 'SELECT'),
('charlie', 'SELECT * FROM hr.employee_reviews', 'hr_db', 'hr', 200, 'SELECT'),
('charlie', 'SELECT * FROM security.access_logs', 'hr_db', 'security', 300, 'SELECT');

-- Simulate suspicious pattern: Sequential sensitive data access
INSERT INTO query_audit_logs (user_id, query_text, database_name, schema_name, rows_affected, query_type)
VALUES 
('dave', 'SELECT email FROM customers WHERE region = ''West''', 'sales_db', 'public', 50, 'SELECT'),
('dave', 'SELECT phone FROM customers WHERE region = ''East''', 'sales_db', 'public', 50, 'SELECT'),
('dave', 'SELECT address FROM customers WHERE region = ''South''', 'sales_db', 'public', 50, 'SELECT');
```

## Example Analysis Output with Learning

Here's what the AI analysis might look like for the test data:

```plaintext
Based on the recent query patterns, the following suspicious activity has been detected:

1. User 'dave' has been running similar queries on the 'customers' table targeting different data fields (email, phone, address) and different regions (West, East, South). While the query in itself is not unusual, the pattern could indicate data harvesting attempt, particularly as these operations were performed sequentially.

    **Severity level:** Medium
    
    **Recommendations:** 
    - Monitor 'dave''s future queries on the 'customers' table.
    - Check if 'dave' needed to access this information as part of his role.
    - Flag 'dave''s repetitive queries fetching personally identifiable information (PII) from different regions for reviewing by the security team.

2. User 'bob' made a single query on the 'employees' table, retrieving a large amount of data (5000 rows).

    **Severity level:** High
  
    **Recommendations:** 
    - Investigate the reasons behind 'bob' needing to access such a large volume of data at once.
    - Check if accessing all fields of the 'employees' table is a requirement of 'bob''s role. 
    - Evaluate whether the user's role has access to this amount of records and possibly restrict access in case it's found unnecessary.

3. User 'charlie' executed the same query three times on highly sensitive tables 'finance.salary_data', 'hr.employee_reviews', and 'security.access_logs'. Accessing such diverse and sensitive data in quick succession might be indicative of an insider threat.

    **Severity level:** High
    
    **Recommendations:**
    - Investigate 'charlie''s activity across the system as there's potential for an insider threat.
    - If these queries are not relevant to his role, consider restricting 'charlie''s access to sensitive tables.
    - Maintain a log of 'charlie''s activities to support further investigation if required.
  
Considering the detected patterns, it is crucial to validate these activities with the respective users and roles and consider enhancing security measures where necessary.
```

## Enhancing the System

Currently the system is not learning from feedback. An improvement would be to add a table to store expert feedback on previous query patterns and whether they are expected or were incidents.
A new `historical_feedback` table could be created that Spice can query, which the AI can use to learn from past incidents.
