# Using OpenAI's Responses API with Spice

This recipe shows how Spice integrates with [OpenAI's Responses API](https://platform.openai.com/docs/api-reference/responses), OpenAI's most advanced interface for generating model responses, supporting both hosted and custom tool calls. This recipe also covers how to use the OpenAI SDK's support for the Responses API to connect to compatible models running on Spice.

## Prerequisites

-   Spice is installed (see the [Getting Started](https://docs.spiceai.org/getting-started) documentation)
-   `OPENAI_API_KEY` is set in `.env`. To acquire an OpenAI API Key, see [OpenAI's Guide](https://platform.openai.com/account/api-keys).
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

```console
2025-08-25T23:34:30.324620Z  INFO spiced: Starting runtime v1.6.0-unstable-build.54c06a350-dev+models
2025-08-25T23:34:30.325913Z  INFO runtime::init::caching: Initialized results cache; max size: 128.00 MiB, item ttl: 1s
2025-08-25T23:34:30.326072Z  INFO runtime::init::caching: Initialized search results cache;
2025-08-25T23:34:31.163684Z  INFO runtime::flight: Spice Runtime Flight listening on 127.0.0.1:50051
2025-08-25T23:34:31.164965Z  INFO runtime::init::dataset: Dataset taxi_trips initializing...
2025-08-25T23:34:31.165957Z  INFO runtime::init::model: Loading model [gpt-4o-responses] from openai:gpt-4o...
2025-08-25T23:34:31.163684Z  INFO runtime::opentelemetry: Spice Runtime OpenTelemetry listening on 127.0.0.1:50052
2025-08-25T23:34:31.177013Z  INFO runtime::http: Spice Runtime HTTP listening on 127.0.0.1:8090
2025-08-25T23:34:31.992304Z  INFO runtime::init::dataset: Dataset taxi_trips registered (s3://spiceai-demo-datasets/taxi_trips/2024/), acceleration (arrow, 10s refresh), results cache enabled.
2025-08-25T23:34:31.993720Z  INFO runtime::accelerated_table::refresh_task: Loading data for dataset taxi_trips
2025-08-25T23:34:34.491656Z  INFO runtime::init::model: Model [gpt-4o-responses] deployed, ready for inferencing
2025-08-25T23:34:42.538074Z  INFO runtime::accelerated_table::refresh_task: Dataset taxi_trips received 2,358,416 records
2025-08-25T23:34:46.359978Z  INFO runtime::accelerated_table::refresh_task: Loaded 2,964,624 rows (399.41 MiB) for dataset taxi_trips in 14s 366ms.
2025-08-25T23:34:46.453673Z  INFO runtime: All components are loaded. Spice runtime is ready!
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
Arrr, I be havin' access to a dataset of taxi voyages, aye! It be called "taxi_trips" in the public spice database. What be yer next command, matey?
```

Ask the model to query the dataset for the 5 most expensive taxi trips, functionality provided by Spice's `sql` tool.

```
In the taxi trips dataset, what are the 5 most expensive taxi trips by fare?
```

```
Arrr matey, here be the five most expensive taxi voyages by fare:

1. **Fare:** 5000.0 doubloons
   - **Pickup:** 2024-01-20T11:19:33
   - **Dropoff:** Same as pickup
   - **Passenger Count:** 0
   - **VendorID:** 1

2. **Fare:** 5000.0 doubloons
   - **Pickup:** 2024-01-20T11:18:47
   - **Dropoff:** Same as pickup
   - **Passenger Count:** 0
   - **VendorID:** 1

3. **Fare:** 2500.0 doubloons
   - **Pickup:** 2024-01-20T11:20:15
   - **Dropoff:** Same as pickup
   - **Passenger Count:** 0
   - **VendorID:** 1

4. **Fare:** 2500.0 doubloons
   - **Pickup:** 2024-01-24T13:44:43
   - **Dropoff:** Same as pickup
   - **Passenger Count:** 0
   - **VendorID:** 1

5. **Fare:** 2500.0 doubloons
   - **Pickup:** 2024-01-20T11:27:48
   - **Dropoff:** Same as pickup
   - **Passenger Count:** 0
   - **VendorID:** 1

These voyages be costin' a pretty penny, aye!
```

Verify this output by, in a separate terminal, starting an interactive SQL query session against the Spice runtime

```console
spice sql
```

Then, query using SQL the `taxi_trips` dataset for the titles of the five most recently created PRs.

```sql
SELECT fare_amount, tpep_pickup_datetime, tpep_dropoff_datetime, passenger_count, VendorID FROM taxi_trips ORDER BY fare_amount DESC LIMIT 5;
```

```
+-------------+----------------------+-----------------------+-----------------+----------+
| fare_amount | tpep_pickup_datetime | tpep_dropoff_datetime | passenger_count | VendorID |
+-------------+----------------------+-----------------------+-----------------+----------+
| 5000.0      | 2024-01-20T11:19:33  | 2024-01-20T11:19:33   | 0               | 1        |
| 5000.0      | 2024-01-20T11:18:47  | 2024-01-20T11:18:47   | 0               | 1        |
| 2500.0      | 2024-01-20T11:20:15  | 2024-01-20T11:20:15   | 0               | 1        |
| 2500.0      | 2024-01-24T13:44:43  | 2024-01-24T13:44:43   | 0               | 1        |
| 2500.0      | 2024-01-20T11:27:48  | 2024-01-20T11:27:48   | 0               | 1        |
+-------------+----------------------+-----------------------+-----------------+----------+

Time: 0.115921584 seconds. 5 rows.
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
Arrr, matey! I've got me hands on the "taxi trips" dataset from yonder S3 seas. Would ye like to explore it, or be there more treasures ye seek?
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
Arrr, matey! I've got me hands on the "taxi trips" dataset from yonder S3 seas. Would ye like to explore it, or be there more treasures ye seek?
```

## Learn More

-   [OpenAI Model Provider Documentation](https://spiceai.org/docs/components/models/openai)
-   [OpenAI's Responses API](https://platform.openai.com/docs/api-reference/responses)
