# Demo signing key

The demo JWTs in this recipe are signed by a throwaway RSA key and are accepted
**only** by the local static issuer at `http://127.0.0.1:9999`.

The private key itself is **not committed** — a private key does not belong in a
public repository, even a demo one. It is not needed to run the recipe: Spice
validates the pre-signed tokens in `../tokens.env` against the **public** JWKS in
`../jwks/jwks.json`, both of which are committed. So the recipe still runs with
no setup.

To regenerate the tokens, run `node ../generate-tokens.js`. With no private key
present it mints a fresh keypair, writes `demo-private-key.pem` here, and rewrites
`../jwks/jwks.json` and `../tokens.env` to match. The `.pem` stays gitignored.

**Never reuse a demo key, and never model a real deployment on a committed
signing key.** In production, tokens are signed by your identity provider and
Spice validates them against that provider's published JWKS.
