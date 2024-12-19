# Quickstart: Running Spice as a Docker Container

Quickstart demonstrates how to run Spice.ai OSS as a container. The quickstart uses [MySQL Sakila Sample Database](https://dev.mysql.com/doc/sakila/en/sakila-structure-tables.html) run as a container with Spice using Docker Compose configuration and Open AI model to perform vector search and natural language queries to the dataset.

## Prerequisites

- Update the `.env` file with your OpenAI API key. If the API key is not available, you can proceed and ignore the `Unable to load LLM` warning. Note that the Using Language Model section cannot be tested in this case.
- Docker is installed: [Install Docker Image](https://docs.docker.com/engine/install/)
- Spice CLI is installed: [Getting Started](https://docs.spiceai.org/getting-started)

## Run Spice as a Docker Container

Review Spice Docker image configuration:

```shell
cat Dockerfile
```

Output:

```shell
FROM spiceai/spiceai:latest-models

# Copy the Spicepod configuration file
COPY spicepod.yaml /app/spicepod.yaml

# Copy the .env.local & .env files
COPY .env* /app/

# Spice runtime start-up arguments
CMD ["--http","0.0.0.0:8090","--metrics", "0.0.0.0:9090","--flight","0.0.0.0:50051"]

EXPOSE 8090
EXPOSE 9090
EXPOSE 50051

# Start the Spicepod                                                                  

```

Use Docker Compose to build and run the Docker image:

```shell
docker-compose up --build
```

Output

```shell
 => [spiced internal] load build definition from Dockerfile                       0.0s

...

 ✔ Container spiceai-mysql-sakila  Created                                        0.0s 
 ✔ Container spiced-container      Created                                        0.0s 
Attaching to spiceai-mysql-sakila, spiced-container
spiceai-mysql-sakila  | 2024-12-19 01:36:24+00:00 [Note] [Entrypoint]: Entrypoint script for MySQL Server 8.1.0-1.el8 started.
spiceai-mysql-sakila  | '/var/lib/mysql/mysql.sock' -> '/var/run/mysqld/mysqld.sock'
spiceai-mysql-sakila  | 2024-12-19T01:36:24.416215Z 0 [System] [MY-015015] [Server] MySQL Server - start.
spiceai-mysql-sakila  | 2024-12-19T01:36:24.544874Z 0 [System] [MY-010116] [Server] /usr/sbin/mysqld (mysqld 8.1.0) starting as process 7
spiceai-mysql-sakila  | 2024-12-19T01:36:24.547827Z 1 [System] [MY-013576] [InnoDB] InnoDB initialization has started.
...
spiced-container      | 2024-12-19T01:36:24.772197Z  INFO runtime::opentelemetry: Spice Runtime OpenTelemetry listening on 127.0.0.1:50052
spiced-container      | 2024-12-19T01:36:24.772246Z  INFO runtime::metrics_server: Spice Runtime Metrics listening on 0.0.0.0:9090
spiced-container      | 2024-12-19T01:36:24.772267Z  INFO runtime::flight: Spice Runtime Flight listening on 0.0.0.0:50051
spiced-container      | 2024-12-19T01:36:24.772389Z  INFO runtime::http: Spice Runtime HTTP listening on 0.0.0.0:8090
spiced-container      | 2024-12-19T01:36:24.888666Z  INFO runtime::init::embedding: Embedding [hf_minilm] ready to embed
spiced-container      | 2024-12-19T01:36:24.888807Z  INFO runtime::init::dataset: Initializing dataset films
spiced-container      | 2024-12-19T01:36:24.888926Z  INFO runtime::init::model: Loading model [openai] from openai:gpt-4o...
spiced-container      | 2024-12-19T01:36:24.889476Z  INFO runtime::init::results_cache: Initialized results cache; max size: 128.00 MiB, item ttl: 1s
spiced-container      | 2024-12-19T01:36:24.904304Z  INFO runtime::init::dataset: Dataset films registered (mysql:film), acceleration (arrow), results cache enabled.
spiced-container      | 2024-12-19T01:36:24.905805Z  INFO runtime::accelerated_table::refresh_task: Loading data for dataset films
spiced-container      | 2024-12-19T01:36:28.185593Z  INFO runtime::init::model: Model [openai] deployed, ready for inferencing
```

Observe that the `films` dataset is loaded.

```shell
Dataset films registered (mysql:film), acceleration (arrow), results cache enabled.
```

You now have Spice running as a Docker container with Flight and HTTP ports exposed on ports `50051` and `8090`. Run `spice status` to access Spice.ai runtime information.

```shell
NAME          ENDPOINT        STATUS 
http          0.0.0.0:8090    Ready  
flight        0.0.0.0:50051   Ready  
metrics       0.0.0.0:9090    Ready  
opentelemetry 127.0.0.1:50052 Ready 
```

### SQL Search

Run `spice sql` and execute the following query to select the top 10 films with the highest average rental score.

```sql
SELECT 
  title, 
  AVG(rental_rate) AS avg_rental_rate
FROM films
GROUP BY title
ORDER BY avg_rental_rate DESC
LIMIT 5;
```

Output:

```shell
+---------------------+-----------------+
| title               | avg_rental_rate |
+---------------------+-----------------+
| ATTRACTION NEWTON   | 4.990000        |
| ALADDIN CALENDAR    | 4.990000        |
| ELEMENT FREDDY      | 4.990000        |
| BACKLASH UNDEFEATED | 4.990000        |
| DOGMA FAMILY        | 4.990000        |
+---------------------+-----------------+
```

### Intelligent search

Run `spice search`

```shell
search> animals
Rank 1, Score: 89.7, Datasets [spice.public.films]
A Beautiful Story of a Dog And a Technical Writer who must Outgun a Student in A Balloon

Rank 2, Score: 89.4, Datasets [spice.public.films]
A Epic Documentary of a Hunter And a Dog who must Outgun a Dog in A Balloon Factory

Rank 3, Score: 89.0, Datasets [spice.public.films]
A Boring Display of a Man And a Dog who must Redeem a Girl in A U-Boat

Rank 4, Score: 88.7, Datasets [spice.public.films]
A Insightful Story of a Boy And a Dog who must Redeem a Boy in Australia

Rank 5, Score: 88.6, Datasets [spice.public.films]
A Boring Story of a Womanizer And a Pioneer who must Face a Dog in California

Rank 6, Score: 88.5, Datasets [spice.public.films]
A Intrepid Saga of a Man And a Lumberjack who must Vanquish a Husband in The Outback

Rank 7, Score: 88.4, Datasets [spice.public.films]
A Thrilling Yarn of a Dog And a Dog who must Build a Husband in A Balloon

Rank 8, Score: 88.3, Datasets [spice.public.films]
A Fateful Story of a Husband And a Moose who must Vanquish a Boy in California

Rank 9, Score: 88.0, Datasets [spice.public.films]
A Intrepid Yarn of a Frisbee And a Dog who must Build a Astronaut in A Balloon Factory

Rank 10, Score: 87.9, Datasets [spice.public.films]
A Intrepid Reflection of a Waitress And a A Shark who must Kill a Squirrel in The Outback

Time: 32ms. 10 results.
```

Or using API: https://docs.spiceai.org/api/http/search

```shell
curl -X POST http://localhost:8090/v1/search \
  -H "Content-Type: application/json" \
  -d '{
  "text": "animals",
  "additional_columns": ["release_year", "title", "rental_rate"],
  "limit": 3
  }'
```

```shell
{
  "matches": [
  {
    "value": "A Beautiful Story of a Dog And a Technical Writer who must Outgun a Student in A Balloon",
    "score": 0.8974827855112448,
    "dataset": "spice.public.films",
    "metadata": {
    "rental_rate": 2.99,
    "release_year": 2006,
    "title": "POTLUCK MIXED"
    }
  },
  {
    "value": "A Epic Documentary of a Hunter And a Dog who must Outgun a Dog in A Balloon Factory",
    "score": 0.8941260610769606,
    "dataset": "spice.public.films",
    "metadata": {
    "title": "IGBY MAKER",
    "rental_rate": 4.99,
    "release_year": 2006
    }
  },
  {
    "value": "A Boring Display of a Man And a Dog who must Redeem a Girl in A U-Boat",
    "score": 0.8896955774714774,
    "dataset": "spice.public.films",
    "metadata": {
    "rental_rate": 0.99,
    "title": "TIMBERLAND SKY",
    "release_year": 2006
    }
  }
  ],
  "duration_ms": 30
}
```

### Using Language Model

Run `spice chat`

```shell
Using model: openai
chat> what datasets you have access to
I have access to the following dataset:

- **Films Dataset**: Available in the `spice.public.films` table.

chat> what is the average rental duration
The average rental duration is approximately 4.99 days.
```
