# Encryption in transit using TLS Recipe

This recipe demonstrates configuring Spice for encryption in transit using TLS and includes a sample client application that connects to the runtime securely. The Spice runtime is configured to use TLS for remote connections and to require TLS for its own HTTP and gRPC endpoints.

First a CA (Certificate Authority) will be created with OpenSSL. Then, certificates will be generated for the `spiced` service and a `postgres` instance and signed by the CA. `postgres` & `spiced` will be started with TLS enabled. The `spicepod.yaml` included in this sample will connect securely to `postgres`. Finally, the TLS connection will be verified using cURL and running a small Go application that connects and does a simple query to the `spiced` service.

## Requirements

- OpenSSL
  - macOS: `brew install openssl`
  - Ubuntu: `sudo apt-get install openssl`
  - Windows: [Download OpenSSL](https://slproweb.com/products/Win32OpenSSL.html)
- Spice.ai runtime
  - [Install Spice.ai](https://docs.spiceai.org/installation)
- cURL
- Docker
- Go (optional, for building the sample application)

## Navigate to the `tls` directory

The rest of the commands in this tutorial should be run from the `tls` directory.

```bash
git clone https://github.com/spiceai/samples.git
cd samples/tls
```

## Create a CA (Certificate Authority)

First, create a CA. This involves generating a private key and a self-signed certificate.

```bash
# Generate a private key and self-signed certificate for the CA
openssl genpkey -algorithm RSA -out ca.key -pkeyopt rsa_keygen_bits:2048
openssl req -new -x509 -key ca.key -out ca.pem -days 3650 -config ca.cnf
```

## Create a certificate signing request & private key for `spiced`

Next, create a private key and a CSR (Certificate Signing Request) for `spiced`.

```bash
# Generate a private key (ECDSA)
openssl ecparam -genkey -name prime256v1 -out spiced.key
# Generate a certificate signing request (CSR) for the private key
openssl req -new -key spiced.key -out spiced.csr -config spiced.cnf
```

### Sign the CSR with the CA (spiced)

Sign the CSR with the CA to generate a certificate for `spiced`.

```bash
# Sign the CSR with the CA
openssl x509 -req -in spiced.csr -CA ca.pem -CAkey ca.key -out spiced.crt -days 365 -copy_extensions copy
```

## Create a certificate signing request & private key for `postgres`

Similar to `spiced` create a private key and a CSR for `postgres`.

```bash
# Generate a private key (ECDSA)
openssl ecparam -genkey -name prime256v1 -out postgres.key
# Generate a certificate signing request (CSR) for the private key
openssl req -new -key postgres.key -out postgres.csr -config postgres.cnf
```

### Sign the CSR with the CA (postgres)

Sign the CSR with the CA to generate a certificate for `postgres`.

```bash
# Sign the CSR with the CA
openssl x509 -req -in postgres.csr -CA ca.pem -CAkey ca.key -out postgres.crt -days 365 -copy_extensions copy
```

## Start `postgres` with TLS

## Ubuntu: Change key file owner and permissions

On Ubuntu, permissions changes are required to allow the `postgres` Docker instance to accesss the key.

Set the owner to the UID `999` and GID `999`, which [match the UID and GID of the `postgres` user.](https://github.com/docker-library/postgres/blob/master/17/bullseye/Dockerfile#L10-L13)

```bash
sudo chown 999:999 postgres.key
sudo chmod 600 postgres.key
```

### Start `postgres`

Start a `postgres` instance with TLS enabled using Docker compose.

```bash
docker compose up -d
```

## Run `spiced` with TLS

With the certificate and key generated, run the `spiced` service with TLS enabled.

```bash
spice run -- --tls-enabled true --tls-certificate-file ./spiced.crt --tls-key-file ./spiced.key
```

```bash
2024-08-05T19:59:09.203647Z  INFO runtime::metrics_server: Spice Runtime Metrics listening on 127.0.0.1:9090
2024-08-05T19:59:09.203554Z  INFO runtime::flight: Spice Runtime Flight listening on 127.0.0.1:50051
2024-08-05T19:59:09.204194Z  INFO runtime: Initialized results cache; max size: 128.00 MiB, item ttl: 1s
2024-08-05T19:59:09.205240Z  INFO runtime: Endpoints secured with TLS using certificate: CN=spiced.localhost, OU=IT, O=Widgets, Inc., L=Seattle, S=Washington, C=US
2024-08-05T19:59:09.205622Z  INFO runtime::http: Spice Runtime HTTP listening on 127.0.0.1:8090
2024-08-05T19:59:09.211074Z  INFO runtime::opentelemetry: Spice Runtime OpenTelemetry listening on 127.0.0.1:50052
2024-08-05T19:59:09.286775Z  INFO runtime: Dataset customer_addresses registered (postgres:customer_addresses), results cache enabled.
```

## Verify the TLS connection

In a separate terminal, verify the TLS connection using cURL.

```bash
curl --cacert ca.pem https://localhost:8090/health
```

## Build and run the sample Go application

The sample Go application connects securely to the `spiced` service over TLS and does a simple query using the `flightsql` ADBC driver.

```bash
go run main.go
```

Output:

```bash
Successfully found Viv
```

## Use `spice sql` to securely connect to the `spiced` service

```bash
spice sql --tls-root-certificate-file ./ca.pem
```

Run a simple query to verify the connection.

```sql
SELECT * FROM customer_addresses LIMIT 5;
```

```bash
Welcome to the Spice.ai SQL REPL! Type 'help' for help.

show tables; -- list available tables
sql> SELECT * FROM customer_addresses LIMIT 5;
+----+------------+------------+----------------------------+----------------------+--------------------+--------------+---------------+--------------+--------------+
| id | first_name | last_name  | email                      | res_address          | work_address       | country      | state         | phone_1      | phone_2      |
+----+------------+------------+----------------------------+----------------------+--------------------+--------------+---------------+--------------+--------------+
| 3  | Viv        | Beeston    | vbeeston2@rambler.ru       | 4667 Acker Way       | 32443 Vidon Center | South Africa |               | 358-278-1801 | 964-452-4077 |
| 4  | Lauralee   | Eliesco    | leliesco3@fc2.com          | 1 Barnett Junction   | 8 Southridge Lane  | Sweden       | Stockholm     | 995-818-6419 | 878-774-6171 |
| 5  | Clari      | Smallpeice | csmallpeice4@earthlink.net | 35462 Schiller Trail | 959 Morrow Point   | Sweden       | Norrbotten    | 596-796-5104 | 616-603-2926 |
| 6  | Beau       | Manderson  | bmanderson5@godaddy.com    | 2732 Moulton Street  | 4012 School Point  | France       | Île-de-France | 128-371-3633 | 862-840-1982 |
| 7  | Ninnette   | Calvey     | ncalvey6@reddit.com        | 02 Arapahoe Park     | 5753 Quincy Street | Sweden       | Stockholm     | 941-515-1803 | 533-369-1830 |
+----+------------+------------+----------------------------+----------------------+--------------------+--------------+---------------+--------------+--------------+

Time: 0.013186875 seconds. 5 rows.
```

## Clean up

```bash
rm ca.key ca.pem spiced.key spiced.csr spiced.crt postgres.key postgres.csr postgres.crt
docker compose down
```

## Summary

This recipe covered how to configure the Spice runtime to connect to remote data sources securely using TLS, how to configure the Spice runtime to use TLS for its own endpoints, and how to create an application that connects to the runtime securely.
