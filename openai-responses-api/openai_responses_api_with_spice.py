from openai import OpenAI

def main():
    # Replace the base_url with your local instance of the Spice HTTP API
    client = OpenAI(base_url="http://localhost:8090/v1", api_key="anything")

    response = client.responses.create(
        model="gpt-4o-responses",
        input="What datasets do you have access to?",
    )

    print(response.output_text)

if __name__ == "__main__":
    main()