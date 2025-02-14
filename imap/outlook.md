# Connecting to an Outlook mailbox

Follow these steps to get started with the IMAP Data Connector, connecting to an Outlook/Microsoft 365 mailbox.

## Pre-requisites

- An Outlook mailbox associated with a personal Microsoft account.
- Connecting to an Outlook mailbox via IMAP requires the use of OAuth2, and an associated Azure Enterprise Application. To learn more, refer to the Microsoft documentation.
  - [Authenticate an IMAP, POP or SMTP connection using OAuth](https://learn.microsoft.com/en-us/exchange/client-developer/legacy-protocols/how-to-authenticate-an-imap-pop-smtp-application-by-using-oauth)
  - The Azure Enterprise Application should be registered as a `web` application, and be configured with a Client Secret.
- This guide requires the use of a `consumer` Azure token and application, to connect to personal mailboxes. To connect to enterprise mailboxes, or mailboxes within an Azure directory, ensure the required token type is used (`single-tenant`, `multi-tenant`, etc).

## Steps

### 1. Acquire an OAuth Authorization Code

Login to the OAuth Application, to retrieve an OAuth Authorization Code. In this example, the OAuth Application redirects to `http://localhost:41440`. Replace `<OAUTH_CLIENT_ID>` with your Azure Enterprise Application Client ID:

```console
https://login.microsoftonline.com/consumers/oauth2/v2.0/authorize?client_id=<OAUTH_CLIENT_ID>&response_type=code&redirect_uri=http%3A%2F%2Flocalhost%3A41440&response_mode=query&scope=https%3A%2F%2Foutlook.office.com%2FIMAP.AccessAsUser.All
```

Example response:

```console
http://localhost:41440/?code=M.A123_BC1.1.A.12312312-a123-a1ab-1231-1231a12312ab
```

### 2. Exchange an OAuth Authorization Code for an Access Token

Using cURL, or a preferred method of making POST requests, exchange the OAuth Authorization Code for an OAuth Access Token.

The Access Token will be used as the password for the IMAP server connection.

Replace `<OAUTH_CLIENT_ID>`, `<OAUTH_CLIENT_SECRET>`, and `<OAUTH_AUTH_CODE>` with the values of the Enterprise Application and Authorization Code:

```console
curl -s -X POST "https://login.microsoftonline.com/consumers/oauth2/v2.0/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "client_id=<OAUTH_CLIENT_ID>" \
  -d "client_secret=<OAUTH_CLIENT_SECRET>" \
  -d "grant_type=authorization_code" \
  -d "code=<OAUTH_AUTH_CODE>" \
  -d "scope=https%3A%2F%2Foutlook.office.com%2FIMAP.AccessAsUser.All" \
  -d "redirect_uri=http%3A%2F%2Flocalhost%3A41440"
```

Example response:

```console
{
    "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiIsIng1dCI6Ik5HVEZ2ZEstZnl0aEV1Q...",
    "token_type": "Bearer",
    "scope": "https%3A%2F%2Foutlook.office.com%2FIMAP.AccessAsUser.All",
    ...
}
```

Copy the `access_token` property to use in the Spicepod

### 3. Spicepod setup

Edit the `spicepod.outlook.yaml` file in this directory, and replace the `<IMAP_EMAIL>` with the Outlook email address.

The OAuth access token for the IMAP connection will be used as the password, supplied as a secret via an environment variable.

Example `spicepod.yaml`:

```yaml
version: v1
kind: Spicepod
name: imap_outlook
datasets:
  - from: imap:mymail@outlook.com
    name: outlook_mailbox
    params:
      imap_access_token: ${secrets:IMAP_ACCESS_TOKEN}
```

### 4. Start Spice

Start Spice, supplying the OAuth Access Token as an environment variable.

For example, in an `.env` file:

```bash
IMAP_ACCESS_TOKEN="eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiIsIng1dCI6Ik5HVEZ2ZEstZnl0aEV1Q..."
```

Once started, the mailbox should be registered in the Spice Runtime logs:

```console
2025-02-02T23:25:23.876322Z  INFO runtime::opentelemetry: Spice Runtime OpenTelemetry listening on 127.0.0.1:50052
2025-02-02T23:25:23.876386Z  INFO runtime::flight: Spice Runtime Flight listening on 127.0.0.1:50051
2025-02-02T23:25:23.877307Z  INFO runtime::init::dataset: Initializing dataset outlook_mailbox
2025-02-02T23:25:23.877477Z  INFO runtime::init::results_cache: Initialized results cache; max size: 128.00 MiB, item ttl: 1s
2025-02-02T23:25:23.878156Z  INFO runtime::http: Spice Runtime HTTP listening on 127.0.0.1:8090
2025-02-02T23:25:23.887277Z  INFO runtime::init::dataset: Dataset outlook_mailbox registered (imap:mymail@outlook.com), results cache enabled.
```

### 5. Query your mail

Once the Spice Runtime is running, run `spice sql` to launch the Spice REPL and start querying your mail:

```sql
SELECT * FROM awesome_mailbox
```

```console
+-------------------------+------------+----------------+----------------------+----+-----+----------------+------------+-------------+
| date                    | subject    | from           | to                   | cc | bcc | reply_to       | message_id | in_reply_to |
+-------------------------+------------+----------------+----------------------+----+-----+----------------+------------+-------------+
| 1970-01-21T02:46:04.919 | Checking In | [awesome@example.com] | [mymail@outlook.com] |    |     | [awesome@example.com] |            |             |
+-------------------------+------------+----------------+----------------------+----+-----+----------------+------------+-------------+
```
