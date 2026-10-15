# Mutual TLS (mTLS) Authentication

Works with `v2.0+`

> **Enterprise Feature:** mTLS (client certificate authentication) is included in the Enterprise distribution of Spice.ai. [Learn more](https://docs.spice.ai/docs/enterprise).

This recipe demonstrates configuring Spice for mutual TLS (mTLS), where the server verifies the client's certificate in addition to the client verifying the server's certificate. This ensures that only trusted clients can connect to the Spice runtime.

mTLS builds on top of standard TLS. If you are not familiar with TLS in Spice, see the [TLS recipe](../tls/) first.

## Requirements

- OpenSSL
  - macOS: `brew install openssl`
  - Ubuntu: `sudo apt-get install openssl`
  - Fedora: `sudo dnf install openssl`
  - Windows: [Download OpenSSL](https://slproweb.com/products/Win32OpenSSL.html)
- Spice.ai runtime (Enterprise)
  - [Install Spice.ai](https://docs.spiceai.org/installation)
- cURL

## Navigate to the `mtls` directory

```bash
git clone https://github.com/spiceai/cookbook.git
cd cookbook/mtls
```

## Overview

In standard TLS, the client verifies the server's identity. In mTLS, the server also verifies the client's identity using a client certificate signed by a trusted CA.

This recipe creates:

1. A **CA** (Certificate Authority) to sign both server and client certificates.
2. A **server certificate** for the Spice runtime.
3. A **client certificate** for authenticating callers (e.g. cURL, another Spice runtime, an application).

## Step 1: Create a CA (Certificate Authority)

Generate a private key and self-signed certificate for the CA. This CA will sign both the server and client certificates.

```bash
openssl genpkey -algorithm RSA -out ca.key -pkeyopt rsa_keygen_bits:2048
openssl req -new -x509 -key ca.key -out ca.pem -days 3650 -config ca.cnf
```

## Step 2: Create a server certificate

Generate a key and certificate signing request (CSR) for the Spice runtime, then sign it with the CA.

```bash
# Generate the server private key (ECDSA)
openssl ecparam -genkey -name prime256v1 -out server.key

# Generate a CSR
openssl req -new -key server.key -out server.csr -config server.cnf

# Sign with the CA
openssl x509 -req -in server.csr -CA ca.pem -CAkey ca.key -CAcreateserial \
  -out server.crt -days 365 -sha256 -extfile server.cnf -extensions req_ext
```

## Step 3: Create a client certificate

Generate a key and certificate for a client, signed by the same CA.

```bash
# Generate the client private key (ECDSA)
openssl ecparam -genkey -name prime256v1 -out client.key

# Generate a CSR
openssl req -new -key client.key -out client.csr -config client.cnf

# Sign with the CA
openssl x509 -req -in client.csr -CA ca.pem -CAkey ca.key -CAcreateserial \
  -out client.crt -days 365 -sha256 -extfile client.cnf -extensions req_ext
```

## Step 4: Run the Spice runtime with mTLS

The included `spicepod.yaml` configures the runtime with:

- TLS enabled using the server certificate and key
- `client_auth_mode: required` — clients must present a valid certificate signed by the CA
- `client_auth_ca_file` — the CA bundle used to verify client certificates

```yaml
runtime:
  tls:
    enabled: true
    certificate_file: ./server.crt
    key_file: ./server.key
    client_auth_mode: required
    client_auth_ca_file: ./ca.pem
```

Start the runtime:

```bash
spice run
```

Expected output:

```
INFO runtime: Endpoints secured with TLS using certificate: CN=spiced.localhost, OU=IT, O=Widgets, Inc., L=Seattle, S=Washington, C=US
INFO runtime::http: Spice Runtime HTTP listening on 127.0.0.1:8090
INFO runtime::flight: Spice Runtime Flight listening on 127.0.0.1:50051
```

## Step 5: Verify mTLS with cURL

### Successful request (with client certificate)

In a separate terminal, make a request with the client certificate:

```bash
curl --cacert ca.pem --cert client.crt --key client.key https://localhost:8090/v1/sql -d 'SELECT * FROM sample_data'
```

Expected output:

```json
[{"id":1,"name":"alpha","value":100},{"id":2,"name":"bravo","value":200},{"id":3,"name":"charlie","value":300}]
```

### Health check (without client certificate)

Kubernetes probes and health checks work without a client certificate:

```bash
curl --cacert ca.pem https://localhost:8090/health
```

### Rejected request (no client certificate on a protected endpoint)

A request to a protected endpoint without a client certificate is rejected with HTTP 401:

```bash
curl --cacert ca.pem https://localhost:8090/v1/sql -d 'SELECT 1'
```

Expected output:

```text
client certificate required
```

### Rejected request (untrusted client certificate)

A client certificate from a different CA is rejected at the TLS handshake:

```bash
# Create a separate "foreign" CA
openssl genpkey -algorithm RSA -out foreign-ca.key -pkeyopt rsa_keygen_bits:2048
openssl req -new -x509 -key foreign-ca.key -out foreign-ca.pem -days 365 -subj "/CN=Foreign CA"

# Create a client cert signed by the foreign CA
openssl ecparam -genkey -name prime256v1 -out foreign-client.key
openssl req -new -key foreign-client.key -out foreign-client.csr -subj "/CN=foreign-client"
openssl x509 -req -in foreign-client.csr -CA foreign-ca.pem -CAkey foreign-ca.key \
  -out foreign-client.crt -days 365 -sha256

# Try to connect — rejected at the TLS handshake
curl --cacert ca.pem --cert foreign-client.crt --key foreign-client.key \
  https://localhost:8090/v1/sql -d 'SELECT 1'
```

Expected: the connection fails with a TLS error (e.g. `SSL alert: unknown CA`).

## Step 6: Use `spice sql` with mTLS

The Spice CLI supports client certificates via the `--client-tls-certificate-file` and `--client-tls-key-file` flags:

```bash
spice sql --tls-root-certificate-file ./ca.pem \
  --client-tls-certificate-file ./client.crt \
  --client-tls-key-file ./client.key
```

Run a simple query to verify the connection:

```sql
SELECT * FROM sample_data;
```

```
+----+---------+-------+
| id | name    | value |
+----+---------+-------+
| 1  | alpha   | 100   |
| 2  | bravo   | 200   |
| 3  | charlie | 300   |
+----+---------+-------+
```

## The three client auth modes

| Mode | Behavior |
|------|----------|
| `none` *(default)* | Standard one-way TLS. No client certificate is requested. |
| `request` | The server requests a client certificate but does not require one. Presented certificates are verified against the CA. Useful for migration, audit-only, or mixed environments. |
| `required` | The server requires a valid client certificate for all non-probe endpoints. `/health` and `/v1/ready` remain accessible without a certificate so Kubernetes probes work. The Flight (gRPC) listener rejects connections without a certificate at the TLS handshake. |

## Clean up

```bash
rm -f ca.key ca.pem ca.srl \
  server.key server.csr server.crt \
  client.key client.csr client.crt \
  foreign-ca.key foreign-ca.pem \
  foreign-client.key foreign-client.csr foreign-client.crt
```

## Summary

This recipe covered:

- Creating a CA and issuing server and client certificates with OpenSSL
- Configuring the Spice runtime for mutual TLS with `client_auth_mode: required`
- Verifying that authenticated clients can query data while unauthenticated requests are rejected
- How health check endpoints remain accessible for Kubernetes probes
- The three `client_auth_mode` options: `none`, `request`, and `required`

For more details, see the [TLS documentation](https://docs.spiceai.org/api/tls).
