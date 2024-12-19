from openai import Client
from openai.types.chat import ChatCompletion
from openai import APIConnectionError
from dotenv import load_dotenv
import os
import logging
import sys

load_dotenv()

# Uncomment the following line to enable debug logging
#logging.basicConfig(level=logging.DEBUG)

def create_chat_completion() -> ChatCompletion:
    # Replace the base_url with your local instance of the Spice HTTP API
    client = Client(api_key="anything", base_url="http://localhost:8090/v1")

    try:
        return client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": "What datasets do I have access to?",
                }
            ],
            model="openai",
        )
    except APIConnectionError as e:
        print("Error: Could not connect to the Spice API server.", file=sys.stderr)
        print("\nEnsure Spice is running locally (spice run) and retry.", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"An unexpected error occurred: {str(e)}", file=sys.stderr)
        sys.exit(1)

def main():
    chat_completion = create_chat_completion()
    print(chat_completion.choices[0].message.content)

if __name__ == "__main__":
    main()