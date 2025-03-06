from openai import Client as OpenAI
from openai.types.chat import ChatCompletion
from openai import APIConnectionError
from dotenv import load_dotenv
import os
import logging
import json
import sys
from dataclasses import dataclass
from typing import List
from typing import Dict
from spicepy import Client as SpiceClient

load_dotenv()

# Uncomment the following line to enable debug logging
#logging.basicConfig(level=logging.DEBUG)

@dataclass
class visualisation_and_sql:
    sql: str
    chart_js_html: str

@dataclass
class SummaryInput:
    user_question: str
    sql_query: str
    data: List[Dict]

def openai_client() -> OpenAI:
    return OpenAI(api_key="anything", base_url="http://localhost:8090/v1")

def create_visualisation_and_sql(user_question: str) -> "visualisation_and_sql":
    response = try_completion(openai_client(), "visualisation_and_sql", user_question)
    return visualisation_and_sql(**json.loads(response))

def create_summary(user_question: str, sql: str, data: SummaryInput) -> str:
    return try_completion(openai_client(), "summary_maker", json.dumps(data))

def get_data(sql: str) -> List[Dict]:
    return SpiceClient().query(sql).read_pandas().to_dict(orient="records")


def try_completion(client: OpenAI, model: str, msg: str) -> str:
    try:
        return client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": msg,
                }
            ],
            model=model,
        ).choices[0].message.content
    except APIConnectionError as e:
        print("Error: Could not connect to the Spice API server.", file=sys.stderr)
        print("\nEnsure Spice is running locally (spice run) and retry.", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"An unexpected error occurred: {str(e)}", file=sys.stderr)
        sys.exit(1)

def main():
    user_question = "How has per month sales trended over the last year?"
    visualisation_and_sql = create_visualisation_and_sql(user_question)
    print(visualisation_and_sql.chart_js_html)
    print(visualisation_and_sql.sql)

    data = get_data(visualisation_and_sql.sql)
    print(data)

    summary = create_summary(user_question, visualisation_and_sql.sql, SummaryInput(user_question, visualisation_and_sql.sql, []))

    print(summary)

if __name__ == "__main__":
    main()
