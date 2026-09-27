# Spice.ai Authorization: Multi-Tenancy, RLS, PII Masking, and RBAC

Works with `v2.2.0+`

> **Enterprise Feature:** Cedar authorization policies and OIDC/JWT identity are
> included in the Enterprise distribution of Spice.ai.
> [Learn more](https://docs.spice.ai/docs/enterprise).

This recipe secures a set of datasets with [Cedar](https://www.cedarpolicy.com/)
policies and shows four access-control patterns from a single Spicepod. Each
pattern is a distinct rule:

| Pattern | Rule | Demonstrated by |
| --- | --- | --- |
| **Multi-tenancy** | `tenant_id = current_org_id()` | Acme and Globex users see different rows of `customers` |
| **Row-level security (RLS)** | `owner = current_user_id()` | Two users in the *same* tenant see different rows of `deals`; an `admin` sees its whole tenant |
| **PII masking** | `@mask_email` / `@mask_ssn`, by role | Analysts see masked PII; a PII officer sees real values |
| **RBAC** | Role-gated dataset + deny-by-default | Only the `hr` role may read `salaries` |

Multi-tenancy isolates by **organization**; RLS isolates by **user**.

## Requirements

- Spice.ai runtime, **Enterprise distribution** - the OSS runtime has no
  `oidc` or `authorization` configuration and rejects this Spicepod (see
  [Step 2](#step-2-run-spice)).
  [Get Spice.ai Enterprise](https://docs.spice.ai/docs/enterprise)
- `python3` (standard library) to serve the JWKS
- `node` - only to regenerate the demo tokens

## Navigate to the `authorization` directory

```bash
git clone https://github.com/spiceai/cookbook.git
cd cookbook/authorization
```

## The demo identities

| Token | `sub` (user) | `org` (tenant) | `roles` |
| --- | --- | --- | --- |
| `TOKEN_ALICE` | `alice@acme` | `acme` | `analyst` |
| `TOKEN_DANA` | `dana@acme` | `acme` | `analyst`, `pii_officer` |
| `TOKEN_SAM` | `sam@globex` | `globex` | `analyst` |
| `TOKEN_HEBE` | `hebe@acme` | `acme` | `analyst`, `hr` |
| `TOKEN_MORGAN` | `morgan@acme` | `acme` | `analyst`, `admin` |

## Step 1: Start the identity provider

Start the JWKS server **first**. The identity provider is a small static file
server (`serve-jwks.py`, standard library only) that serves an OIDC discovery
document and a JWKS.


```bash
python3 serve-jwks.py
# Serving OIDC discovery + JWKS on http://127.0.0.1:9999
```

## Step 2: Run Spice

In a second terminal:

```bash
spice run
```

> **On the OSS runtime this looks like a success but is not.** The Spicepod is
> rejected, no datasets load, and the runtime still logs `All components are
> loaded. Spice runtime is ready!` - that line is printed either way, so it does
> **not** confirm the recipe is working. The warning below is the failure signal:
> if `spice run` prints it, stop here and install the Enterprise distribution,
> because every query below will fail with
> `table 'spice.public.customers' not found`:
>
> ```text
> WARN spiced: Starting in pods watcher mode without a valid spicepod.yaml. The runtime will load
> components once a valid spicepod.yaml is provided: Unable to load spicepod ...: Failed to parse
> spicepod.yaml: unknown field `oidc`, expected `api-key` or `api_key`
> ```

## Step 3: Load the demo tokens

In a third terminal:

```bash
set -a; . ./tokens.env; set +a
```

Queries below use `spice sql` and pass the JWT with `--api-key`.

## Step 4: Multi-tenancy + PII masking

An Acme analyst sees only Acme rows, with `email` and `ssn` masked:

```bash
echo 'select id, tenant_id, email, ssn from customers order by id;' \
  | spice sql --api-key "$TOKEN_ALICE"
```

```text
+-------+-----------+---------+-------------+
|   id  | tenant_id |  email  |     ssn     |
| int64 |  varchar  | varchar |   varchar   |
+-------+-----------+---------+-------------+
| 1     | acme      | ***@*** | ***-**-**** |
| 2     | acme      | ***@*** | ***-**-**** |
| 5     | acme      | ***@*** | ***-**-**** |
+-------+-----------+---------+-------------+
```

The same query as a Globex analyst returns Globex rows only - tenant isolation
from one filter:

```bash
echo 'select id, tenant_id, email, ssn from customers order by id;' \
  | spice sql --api-key "$TOKEN_SAM"
```

```text
+-------+-----------+---------+-------------+
|   id  | tenant_id |  email  |     ssn     |
| int64 |  varchar  | varchar |   varchar   |
+-------+-----------+---------+-------------+
| 3     | globex    | ***@*** | ***-**-**** |
| 4     | globex    | ***@*** | ***-**-**** |
+-------+-----------+---------+-------------+
```

## Step 5: Row-level security by ownership

`deals` is filtered by `owner = current_user_id()`. Alice owns two rows:

```bash
echo 'select id, tenant_id, owner, name, amount from deals order by id;' \
  | spice sql --api-key "$TOKEN_ALICE"
```

```text
+-------+-----------+------------+--------------+--------+
|   id  | tenant_id |    owner   |     name     | amount |
| int64 |  varchar  |   varchar  |    varchar   |  int64 |
+-------+-----------+------------+--------------+--------+
| 1     | acme      | alice@acme | Acme Renewal | 50000  |
| 2     | acme      | alice@acme | Acme Upsell  | 20000  |
+-------+-----------+------------+--------------+--------+
```

Dana is in the **same tenant** as Alice (`acme`), but sees only the row she
owns - RLS is per-user, not per-tenant:

```bash
echo 'select id, tenant_id, owner, name, amount from deals order by id;' \
  | spice sql --api-key "$TOKEN_DANA"
```

```text
+-------+-----------+-----------+----------------+--------+
|   id  | tenant_id |   owner   |      name      | amount |
| int64 |  varchar  |  varchar  |     varchar    |  int64 |
+-------+-----------+-----------+----------------+--------+
| 3     | acme      | dana@acme | Acme Expansion | 75000  |
+-------+-----------+-----------+----------------+--------+
```

`morgan` holds the `admin` role, which is exempt from the ownership filter and
granted a tenant-scoped read - an admin sees every deal in their own tenant
(`acme`), not just the ones they own, but still not another tenant's:

```bash
echo 'select id, tenant_id, owner, name, amount from deals order by id;' \
  | spice sql --api-key "$TOKEN_MORGAN"
```

```text
+-------+-----------+------------+-----------------+--------+
|   id  | tenant_id |    owner   |       name      | amount |
| int64 |  varchar  |   varchar  |     varchar     |  int64 |
+-------+-----------+------------+-----------------+--------+
| 1     | acme      | alice@acme | Acme Renewal    | 50000  |
| 2     | acme      | alice@acme | Acme Upsell     | 20000  |
| 3     | acme      | dana@acme  | Acme Expansion  | 75000  |
| 5     | acme      | hebe@acme  | Acme Onboarding | 30000  |
+-------+-----------+------------+-----------------+--------+
```

## Step 6: Role-conditional PII

`dana` holds the `pii_officer` role, so the mask does not apply - real values,
still only Acme rows:

```bash
echo 'select id, tenant_id, email, ssn from customers order by id;' \
  | spice sql --api-key "$TOKEN_DANA"
```

```text
+-------+-----------+--------------------+-------------+
|   id  | tenant_id |        email       |     ssn     |
| int64 |  varchar  |       varchar      |   varchar   |
+-------+-----------+--------------------+-------------+
| 1     | acme      | alice@acme.example | 111-11-1111 |
| 2     | acme      | aaron@acme.example | 222-22-2222 |
| 5     | acme      | amy@acme.example   | 555-55-5555 |
+-------+-----------+--------------------+-------------+
```

## Step 7: RBAC

The runtime denies by default, and no policy grants an analyst read on
`salaries`:

```bash
echo 'select * from salaries;' | spice sql --api-key "$TOKEN_ALICE"
```

```text
Query Error: Authorization denied: action 'query' on dataset 'salaries' is not permitted for this user
```

`hebe` holds the `hr` role, so the read is allowed, but still tenant-filtered:

```bash
echo 'select * from salaries order by id;' | spice sql --api-key "$TOKEN_HEBE"
```

```text
+-------+-----------+----------------+--------+
|   id  | tenant_id |    employee    | amount |
| int64 |  varchar  |     varchar    |  int64 |
+-------+-----------+----------------+--------+
| 1     | acme      | Alice Anderson | 120000 |
| 2     | acme      | Aaron Ackerman | 115000 |
+-------+-----------+----------------+--------+
```


## Regenerating the tokens

Edit the users or claims in `generate-tokens.js`, then:

```bash
node generate-tokens.js   # rewrites jwks/jwks.json, the discovery doc, and tokens.env
```

`keys/demo-private-key.pem` is a throwaway demo key (see `keys/README.md`) -
never reuse it or model a real deployment on a committed signing key.
