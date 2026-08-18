#!/usr/bin/env node
/*
 * Generates the static OIDC fixtures for this cookbook recipe:
 *   - keys/demo-private-key.pem        RSA private key (DEMO ONLY — see README)
 *   - jwks/jwks.json                   public JWKS served to Spice
 *   - jwks/.well-known/openid-configuration   minimal OIDC discovery document
 *   - tokens.env                       one signed JWT per demo user
 *
 * No external dependencies — uses only Node's built-in `crypto`.
 * Re-run after changing users, claims, issuer, or audience:
 *   node generate-tokens.js
 */

const crypto = require("crypto");
const fs = require("fs");
const path = require("path");

const ISSUER = "http://127.0.0.1:9999";
const AUDIENCE = "spice-cookbook";
const KID = "spice-cookbook-key";
// Fixed timestamps keep the committed fixtures reproducible (no wall clock).
const IAT = 1704067200; // 2024-01-01T00:00:00Z
const EXP = 4102444800; // 2100-01-01T00:00:00Z — long-lived demo tokens

// Demo users. `org` -> current_org_id(), `roles` -> current_user_has_role(...).
const USERS = [
  { name: "alice",  sub: "alice@acme",   org: "acme",   roles: ["analyst"] },
  { name: "dana",   sub: "dana@acme",    org: "acme",   roles: ["analyst", "pii_officer"] },
  { name: "sam",    sub: "sam@globex",   org: "globex", roles: ["analyst"] },
  { name: "hebe",   sub: "hebe@acme",    org: "acme",   roles: ["analyst", "hr"] },
  { name: "morgan", sub: "morgan@acme",  org: "acme",   roles: ["analyst", "admin"] },
];

const dir = __dirname;
const keyPath = path.join(dir, "keys", "demo-private-key.pem");

// Load a committed key if present so the JWKS and tokens stay stable across
// runs; otherwise mint a fresh keypair.
let privateKeyPem;
if (fs.existsSync(keyPath)) {
  privateKeyPem = fs.readFileSync(keyPath, "utf8");
} else {
  const { privateKey } = crypto.generateKeyPairSync("rsa", { modulusLength: 2048 });
  privateKeyPem = privateKey.export({ type: "pkcs8", format: "pem" });
  fs.writeFileSync(keyPath, privateKeyPem);
}
const privateKey = crypto.createPrivateKey(privateKeyPem);
const publicKey = crypto.createPublicKey(privateKey);

// Public JWKS: export the RSA public key as a JWK and annotate it.
const jwk = publicKey.export({ format: "jwk" });
jwk.kid = KID;
jwk.alg = "RS256";
jwk.use = "sig";
fs.writeFileSync(
  path.join(dir, "jwks", "jwks.json"),
  JSON.stringify({ keys: [jwk] }, null, 2) + "\n",
);

// Minimal OIDC discovery document. Spice reads `issuer` and `jwks_uri`.
const discovery = {
  issuer: ISSUER,
  jwks_uri: `${ISSUER}/jwks.json`,
  response_types_supported: ["id_token"],
  subject_types_supported: ["public"],
  id_token_signing_alg_values_supported: ["RS256"],
};
fs.writeFileSync(
  path.join(dir, "jwks", ".well-known", "openid-configuration"),
  JSON.stringify(discovery, null, 2) + "\n",
);

const b64url = (buf) =>
  Buffer.from(buf).toString("base64").replace(/\+/g, "-").replace(/\//g, "_").replace(/=+$/, "");

function sign(claims) {
  const header = { alg: "RS256", typ: "JWT", kid: KID };
  const signingInput =
    b64url(JSON.stringify(header)) + "." + b64url(JSON.stringify(claims));
  const signature = crypto.sign("RSA-SHA256", Buffer.from(signingInput), privateKey);
  return signingInput + "." + b64url(signature);
}

const lines = [
  "# Signed demo JWTs — source with `set -a; . ./tokens.env; set +a` or copy a value.",
  "# Regenerate with: node generate-tokens.js",
  "",
];
for (const u of USERS) {
  const token = sign({
    iss: ISSUER,
    aud: AUDIENCE,
    sub: u.sub,
    org: u.org,
    roles: u.roles,
    iat: IAT,
    exp: EXP,
  });
  lines.push(`# ${u.sub}  org=${u.org}  roles=[${u.roles.join(", ")}]`);
  lines.push(`TOKEN_${u.name.toUpperCase()}=${token}`);
  lines.push("");
}
fs.writeFileSync(path.join(dir, "tokens.env"), lines.join("\n"));

console.log("Wrote jwks/jwks.json, jwks/.well-known/openid-configuration, tokens.env");
for (const u of USERS) console.log(`  ${u.name.padEnd(6)} ${u.sub}  org=${u.org}  roles=[${u.roles.join(", ")}]`);
