from openai import Client as OpenAI
from openai import APIConnectionError
from dotenv import load_dotenv
import argparse
import json
import sys
from dataclasses import dataclass
from typing import List, Dict
from spicepy import Client as SpiceClient
from dataclasses_json import dataclass_json

load_dotenv()


@dataclass_json
@dataclass
class VisualisationAndSql:
    """Response from the visualisation_and_sql model."""
    sql: str
    chart_js_html: str


@dataclass_json
@dataclass
class SummaryInput:
    """Input for the summary_maker model."""
    user_question: str
    sql_query: str
    data: List[Dict]


def openai_client() -> OpenAI:
    """Create an OpenAI client pointing to the local Spice runtime."""
    return OpenAI(api_key="anything", base_url="http://localhost:8090/v1")


def create_visualisation_and_sql(user_question: str) -> VisualisationAndSql:
    """Generate SQL and Chart.js visualization from a natural language question."""
    response = try_completion(openai_client(), "visualisation_and_sql", user_question)
    return VisualisationAndSql(**json.loads(response))


def create_summary(summary_input: SummaryInput) -> str:
    """Generate a summary of the data trends."""
    return try_completion(openai_client(), "summary_maker", summary_input.to_json())


def get_data(sql: str) -> List[Dict]:
    """Execute SQL query against Spice and return results as list of dicts."""
    return SpiceClient().query(sql).read_pandas().to_dict(orient="records")


def try_completion(client: OpenAI, model: str, msg: str) -> str:
    """Send a completion request to the Spice runtime."""
    try:
        return client.chat.completions.create(
            messages=[{"role": "user", "content": msg}],
            model=model,
        ).choices[0].message.content
    except APIConnectionError:
        print("Error: Could not connect to the Spice API server.", file=sys.stderr)
        print("\nEnsure Spice is running locally (spice run) and retry.", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"An unexpected error occurred: {str(e)}", file=sys.stderr)
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description="Generate SQL queries and Chart.js visualizations from natural language questions."
    )
    parser.add_argument(
        "question",
        nargs="?",
        default="How has per month sales trended?",
        help="The natural language question to analyze (default: 'How has per month sales trended?')"
    )
    parser.add_argument(
        "--no-summary",
        action="store_true",
        help="Skip generating the data summary"
    )
    args = parser.parse_args()

    user_question = args.question
    print(f"Question: {user_question}\n", file=sys.stderr)

    # Generate SQL and visualization
    print("Generating SQL and visualization...", file=sys.stderr)
    result = create_visualisation_and_sql(user_question)
    
    print("=" * 60)
    print("CHART.JS HTML:")
    print("=" * 60)
    print(result.chart_js_html)
    
    print("\n" + "=" * 60)
    print("SQL QUERY:")
    print("=" * 60)
    print(result.sql)

    # Execute query
    print("\nExecuting query...", file=sys.stderr)
    data = get_data(result.sql)
    
    print("\n" + "=" * 60)
    print("DATA:")
    print("=" * 60)
    print(json.dumps(data, indent=2))

    # Generate summary
    if not args.no_summary:
        print("\nGenerating summary...", file=sys.stderr)
        summary_input = SummaryInput(user_question, result.sql, data)
        summary = create_summary(summary_input)
        
        print("\n" + "=" * 60)
        print("SUMMARY:")
        print("=" * 60)
        print(summary)


if __name__ == "__main__":
    main()
