# cURL Cloud Sample

Sample scripts for querying your Spice Cloud app using [cURL](https://curl.se/).

## Usage

### Query via HTTP

```bash
curl -X POST https://data.spiceai.io/v1/sql \
  -H "Content-Type: application/json" \
  -H "X-API-Key: <YOUR_API_KEY>" \
  -d '{"query": "SELECT * FROM my_dataset LIMIT 10"}'
```
