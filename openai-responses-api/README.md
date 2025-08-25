# Using OpenAI's Responses API with Spice

This recipe shows how Spice integrates with [OpenAI's Responses API](https://platform.openai.com/docs/api-reference/responses), OpenAI's most advanced interface for generating model responses, supporting both hosted and custom tool calls. This recipe also covers how to use the OpenAI SDK's support for the Responses API to connect to compatible models running on Spice.

## Prerequisites

-   Spice is installed (see the [Getting Started](https://docs.spiceai.org/getting-started) documentation)
-   `GITHUB_TOKEN` is set in `.env`. To acquire a GitHub token, see [GitHub's Guide](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens?utm_cta=website-homepage-industry-card-public-sector%3Fwtime).
-   `SPICE_OPENAI_API_KEY` is set in `.env`. To acquire an OpenAI API Key, see [OpenAI's Guide](https://platform.openai.com/account/api-keys).
-   Python >= 3.10
-   Python package manager (`pip` or `uv`)

## How to run

Clone this cookbook repo locally and navigate to the `openai-responses-api` directory:

```bash
git clone https://github.com/spiceai/cookbook.git
cd cookbook/openai-responses-api
```

Start the Spice runtime and ensure each component is initialized:

```console
spice run
```

```
2025-08-25T21:07:56.310687Z  INFO spiced: Starting runtime v1.6.0-unstable-build.54c06a350-dev+models
2025-08-25T21:07:56.312044Z  INFO runtime::init::caching: Initialized results cache; max size: 128.00 MiB, item ttl: 1s
2025-08-25T21:07:56.312203Z  INFO runtime::init::caching: Initialized search results cache;
2025-08-25T21:07:56.713547Z  INFO runtime::init::dataset: Dataset pulls initializing...
2025-08-25T21:07:56.713539Z  INFO runtime::flight: Spice Runtime Flight listening on 127.0.0.1:50051
2025-08-25T21:07:56.713746Z  INFO runtime::opentelemetry: Spice Runtime OpenTelemetry listening on 127.0.0.1:50052
2025-08-25T21:07:56.714782Z  INFO runtime::init::model: Loading model [gpt-4o-responses] from openai:gpt-4o...
2025-08-25T21:07:56.719827Z  INFO runtime::http: Spice Runtime HTTP listening on 127.0.0.1:8090
2025-08-25T21:08:02.040909Z  INFO runtime::init::dataset: Dataset pulls registered (github:github.com/spiceai/spiceai/pulls), acceleration (arrow), results cache enabled.
2025-08-25T21:08:02.042245Z  INFO runtime::accelerated_table::refresh_task: Loading data for dataset pulls
2025-08-25T21:08:03.209625Z  INFO runtime::init::model: Model [gpt-4o-responses] deployed, ready for inferencing
2025-08-25T21:08:06.452241Z  INFO runtime::accelerated_table::refresh_task: Loaded 100 rows (491.41 kiB) for dataset pulls in 4s 409ms.
2025-08-25T21:08:06.470565Z  INFO runtime: All components are loaded. Spice runtime is ready!
```

## Using OpenAI-hosted tools

In a separate terminal, start a chat session against the Spice runtime with the Responses API enabled:

```
spice chat --responses
```

Ask the model to retrieve today's news via web search, one of OpenAI's hosted tools.

```
What's the latest news today? Use web search and provide links to your sources.
```

```
Ahoy, matey! Here's the latest news as of August 25, 2025:

**International News**

- **U.S. and South Korea Strengthen Ties**: President Donald Trump hosted South Korean President Lee Jae Myung at the White House. President Lee praised Trump and proposed his involvement in Korean peace efforts, even suggesting the construction of a Trump Tower in North Korea. Trump expressed support and reminisced about his past diplomatic engagements with North Korea. ([apnews.com](https://apnews.com/article/263c5333cab2e0bc86283b15ed02c44f?utm_source=openai))

- **Russia Accuses Ukraine of Drone Attacks**: Russia has accused Ukraine of launching drone attacks that sparked a fire at a nuclear power plant in its western Kursk region. The strikes coincided with Ukraine's Independence Day celebrations. ([timesofindia.indiatimes.com](https://timesofindia.indiatimes.com/india/india-international-breaking-news-today-august-25/amp_liveblog/123491478.cms?utm_source=openai))

**U.S. News**

- **Federal Reserve Signals Potential Rate Cut**: Federal Reserve Chair Jerome Powell indicated a possible interest rate cut in September during the Jackson Hole Economic Symposium. This shift comes amid concerns about a weakening labor market and muted inflation pressures. ([ft.com](https://www.ft.com/content/aa226632-ec28-4068-a465-e7ad8d603964?utm_source=openai))

- **Stock Market Decline**: Wall Street stocks declined, pulling back after last week's rally driven by hopes of interest rate cuts. The S&P 500 dropped 0.4%, the Dow Jones fell 0.8%, and the Nasdaq declined 0.2%. ([apnews.com](https://apnews.com/article/7828c93e839335f2e911f3a7fdcfec26?utm_source=openai))

**Technology**

- **Windows 11 Update**: The August 2025 Security Update for Windows 11 introduces significant new features alongside security enhancements for version 24H2. Key updates include new capabilities for Windows Recall, AI functions for Click to Do, and an AI agent in the Settings app. ([windowscentral.com](https://www.windowscentral.com/microsoft/windows-11/8-new-features-arriving-with-the-august-2025-security-update-for-windows-11?utm_source=openai))

**Science**

- **Origami-Inspired Engineering**: A young engineering student at Brigham Young University has discovered a new class of origami design, offering applications in compacted satellite arrays and microtechnologies. The pattern can be folded flat and then expand radially to "bloom" like a flower. ([csmonitor.com](https://www.csmonitor.com/Daily/2025/20250825?utm_source=openai))

**Health**

- **Kenya Eliminates Sleeping Sickness**: Kenya received official recognition from the World Health Organization for eliminating sleeping sickness as a public health concern, marking a significant milestone in the battle against neglected tropical diseases. ([allafrica.com](https://allafrica.com/stories/202508250103.html?utm_source=openai))

**Sports**

- **US Open Begins**: The 2025 US Open has commenced in New York with a record $90 million prize purse, the highest player compensation in tennis history. ([leverageedu.com](https://leverageedu.com/discover/school-education/school-assembly-news-headlines-25-august-2025/?utm_source=openai))

For more detailed information, you can refer to the provided sources.
```

Ask the model to run the following code snippet using its code interpreter, another one of OpenAI's hosted tools.

```python
# Prompt: Run the following code using your code interpreter and output its result
import hashlib, math, random

def scramble(n):
    s = str(n).encode()
    h = hashlib.sha256(s).hexdigest()
    nums = [int(h[i:i+2], 16) for i in range(0, len(h), 2)]
    random.seed(sum(nums))
    random.shuffle(nums)
    return sum(int(math.sin(x) * 1000) for x in nums[:10])

def main():
    base = 123456789
    result = scramble(base)
    print(result)

if __name__ == '__main__':
    main()
```

```console
Arrr, matey! The code be runnin' smooth as silk, and the result be \(1562\)! 🏴‍☠️
```

## Using Spice-Hosted Tools

In the same chat session with the Responses API enabled, ask the model to list what datasets it has access to, which uses the `list_datasets` tool that Spice provides.

```
What datasets do you have access to?
```

```
Arrr, I’ve got me hands on a dataset named **pulls**. What would ye like to do with it, matey? ⚓️
```

Ask the model to query the dataset for the 5 most recently created PRs, functionality provided by another one of Spice's tools.

```
In the pulls dataset, what are the titles of the 5 most recently created PRs?
```

```
Arrr, matey! Here be the titles of the five most recent pull requests:

1. **README updates** - [Link](https://github.com/spiceai/spiceai/pull/161)
2. **Update support for arm64** - [Link](https://github.com/spiceai/spiceai/pull/160)
3. **Make versions compile time constants** - [Link](https://github.com/spiceai/spiceai/pull/158)
4. **Fix acknowledgements not being served** - [Link](https://github.com/spiceai/spiceai/pull/157)
5. **Update version to v0.1.0-alpha-rc** - [Link](https://github.com/spiceai/spiceai/pull/155)

If ye be needin' more details, just let me know, and I'll haul 'em up for ye! ⚓️
```

Verify this output by, in a separate terminal, starting an interactive SQL query session against the Spice runtime

```console
spice sql
```

Then, query using SQL the `pulls` dataset for the titles of the five most recently created PRs.

```sql
SELECT title FROM pulls ORDER BY created_at DESC LIMIT 5;
```

```
+---------------------------------------+
| title                                 |
+---------------------------------------+
| README updates                        |
| Update support for arm64              |
| Make versions compile time constants  |
| Fix acknowledgements not being served |
| Update version to v0.1.0-alpha-rc     |
+---------------------------------------+

Time: 0.025712291 seconds. 5 rows.
```

## Client prerequisites

These steps only need to be done once. Use a Python `virtualenv` to keep projects isolated.

### Using pip

1. Create the virtual environment:

```
python -m venv .venv
```

2. Activate the virtual environment:

```
source .venv/bin/activate
```

3. Install the required packages:

```
pip install openai
```

Run the client. Ensure the Spice runtime is running.

```
python openai_responses_api_with_spice.py
```

Observe the model's response to the `What datasets do you have access to?` question:

```console
Arrr, matey! I be havin' access to a dataset called "pulls." But it seems I can't run a document search on it. Yarrr! What be ye wishin' to do with it?
```

### Using uv

1. Create the virtual environment

```
uv venv
```

2. Activate the virtual environment:

```
source .venv/bin/activate
```

3. Ensure the packages are installed:

```
uv pip install openai
```

Run the client. Ensure the Spice runtime is running.

```
python openai_responses_api_with_spice.py
```

Observe the model's response to the `What datasets do you have access to?` question:

```console
Arrr, matey! I be havin' access to a dataset called "pulls." But it seems I can't run a document search on it. Yarrr! What be ye wishin' to do with it?
```

## Learn More

-   [OpenAI Model Provider Documentation](https://spiceai.org/docs/components/models/openai)
-   [OpenAI's Responses API](https://platform.openai.com/docs/api-reference/responses)
