# Spice with the OpenAI SDK

One of Spice's best features is to act in place of the OpenAI API. Even better, you don't even have to be running OpenAI behind Spice! You can run OpenAI, Anthropic or HuggingFace models over your data and use existing tools that are compatible with the OpenAI API.

## Prerequisites

1. Python >= 3.10
2. Python package manager (`pip` or `uv`)
3. Spice [installed](https://docs.spiceai.org/getting-started)
4. OpenAI API Key

## Starting Spice

The first step is to get the Spice instance up and running.

```bash
git clone https://github.com/spiceai/cookbook # Skip if already cloned
cd cookbook/openai_sdk
# Add your OpenAI API key to the .env file
echo "SPICE_OPENAI_API_KEY=your_openai_api_key" > .env
# Start Spice
spice run
```

Wait until the runtime reports it is ready before running the client.

Spice will use your OpenAI API key to communicate with OpenAI on your client code's behalf.

## Client prerequisites

Install dependencies and run the client:

```bash
python -m pip install openai python-dotenv
python spice_openai_sdk.py
```

## About the client

The client is fairly simple, but it demonstrates how to integrate existing tooling with Spice's AI Gateway.

First, construct the client:

```python
client = Client(api_key="anything", base_url="http://localhost:8090/v1")
```

Notice that we can use any string we want for the `api_key`, because it's Spice that's responsible for communicating with the OpenAI API, not our client code, meaning less secrets to have to store and manage for your client application.

```python
chat_completion = client.chat.completions.create(
    messages=[
        {
            "role": "user",
            "content": "What datasets do I have access to?",
        }
    ],
    model="openai",
)
```

Here we're using the chat completions API to ask a question. Notice that we're asking a question about our Datasets. This is a question that only Spice can answer, and that's exactly what it does:

```python
print(chat_completion.choices[0].message.content)
```
