# Web Search Using Perplexity
This recipe demonstrates how to configure and use Perplexity web search within Spice AI.

## Prerequisites

- Ensure you have the Spice CLI installed. Follow the [Getting Started](https://docs.spiceai.org/getting-started) guide if you haven't done so.
- Populate `.env` in your working directory with the required secrets:
  - `SPICE_PERPLEXITY_AUTH_TOKEN`: A valid authentication token for the Perplexity API. Obtain it from [Perplexity's Getting Started guide](https://docs.perplexity.ai/guides/getting-started).
  - `SPICE_OPENAI_API_KEY`: A valid OpenAI API key (or equivalent).

## Using Perplexity for internet-informed conversations.
1. Start the Spice runtime:

```shell
spice run
```

2. In a separate terminal, start a chat session:

```shell
spice chat
```

3. Select `perp`
```shell
Use the arrow keys to navigate: ↓ ↑ → ←
? Select model:
    openai-w-internet
  ▸ perp
```

4. Ask a question

```shell
spice chat
```
```shell
Using model: perp
chat>  What's the weather in Korea this week?
Here's a summary of the weather in Seoul, South Korea, for this week:

- **Current Weather**: Light snow with mostly cloudy conditions. The temperature is around 0°C (32°F) with a feels-like temperature of -2°C (28°F)[1].

- **Forecast for the Week**:
  | Day        | High Temperature | Low Temperature | Conditions                  |
  |------------|------------------|-----------------|-----------------------------|
  | Fri, Feb 7 | -6°C (21°F)      | -13°C (9°F)     | Light snow early, morning clouds[2] |
  | Sat, Feb 8 | -4°C (25°F)      | -11°C (12°F)    | Sunny                        |
  | Sun, Feb 9 | -1°C (30°F)      | -9°C (16°F)     | Sunny                        |
  | Mon, Feb 10| 4°C (39°F)       | -3°C (27°F)     | Scattered clouds             |
  | Tue, Feb 11| 1°C (34°F)       | -5°C (23°F)     | Afternoon clouds             |
  | Wed, Feb 12| 4°C (39°F)       | -2°C (28°F)     | Snow changing to rain        |

The weather will transition from cold and snowy to clearer conditions by the weekend, with temperatures gradually rising towards the end of the week[2][3][5].

Time: 5.02s (first token 1.50s). Tokens: 345. Prompt: 35. Completion: 310 (88.28/s).
```

5. Check the citations used by the model
```shell
spice sql
```
```sql
SELECT captured_output
FROM runtime.task_history
WHERE task='citations'
ORDER BY end_time DESC
LIMIT 1;
```
```json
[
  "https://www.timeanddate.com/weather/south-korea/seoul",
  "https://www.timeanddate.com/weather/south-korea/seoul/ext",
  "https://www.accuweather.com/en/kr/seoul/226081/weather-forecast/226081",
  "https://www.theweathernetwork.com/en/city/kr/seoul/seoul/14-days",
  "https://www.accuweather.com/en/kr/seoul/226081/daily-weather-forecast/226081"
]
```


## Using the Web search tool
Web search engines, like Perplexity, can be used by other models to enable internet-informed conversations.

1. Start the Spice runtime:

```shell
spice run
```

2. Call the web search tool directly (named `the_internet` in the `spicepod.yaml`).
```shell
curl -XPOST http://127.0.0.1:8090/v1/tool/the_internet \
  --data '{"query": "What is the surf like today?"}'
```

## Let the LLM use the web search tool

1. Start the Spice runtime:

```shell
spice run
```

2. In a separate terminal, start a chat session:

```shell
spice chat
```
3. Select `openai-w-internet`
```shell
Use the arrow keys to navigate: ↓ ↑ → ←
? Select model:
  ▸ openai-w-internet
    perp
```

4. Ask a question

```shell
>>> spice chat
Using model: openai-w-internet
chat> Where should I surf in California today?
```
```shell
Today's surf conditions in California appear to be quite minimal. Here's a summary from a few key locations:

### Ventura County
- **Surf Height**: Ankle high or less
- **Conditions**: Semi glassy in the morning; light sideshore texture in the afternoon
- **Tides**: Low at 5:43 AM, High at 12:18 PM, Low at 4:47 PM, High at 10:49 PM
- **Sunrise/Sunset**: 5:52 AM / 8:12 PM

### Trestles
- **Surf Height**: Currently reported as 1 ft (some sources indicate it could be 2-4 ft)
- **Conditions**: Clean with nearby winds at NNE
- **Tides**: High at 12:05 PM, Low at 3:51 AM

Overall, surf conditions are generally flat across these regions, making it less than ideal for surfing today. You may wish to check more specific spots or potentially consider inland activities or relaxing on the beach.

For more detailed local conditions, you can check:
- [Ventura Surf Forecast](https://www.swellinfo.com/surf-forecast/ventura-california)
- [Orange County Surf Forecast](https://www.swellinfo.com/surf-forecast/orange-county-california-south)
- [Trestles Forecast](https://surfcaptain.com/forecast/trestles-california)

Time: 18.28s (first token 10.02s). Tokens: 183. Prompt: 160. Completion: 23 (2.78/s).
```

5. Check that the LLM did use the internet
```shell
spice trace ai_chat
```
```shell
[0c239b47bcb03b01] (18276.11ms) ai_chat
  ├── [1f4e0a007afdbbd7] (18274.71ms) ai_completion
  ├── [f21d61726384a63f] (    0.33ms) tool_use::websearch
  ├── [cce69b405aeb931b] (17364.89ms) ai_completion
  ├── [a47dfed093941255] ( 6299.55ms) tool_use::websearch
  │ └── [4632753af5cbb6be] ( 6299.06ms) citations
  └── [5020a8af033160e0] (10066.56ms) ai_completion
```
