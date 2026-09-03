// PII masking, conditioned on role.
//
// The first policy masks the `email` and `ssn` columns for everyone reading
// `customers` — UNLESS the caller holds the `pii_officer` role. The second
// policy lets a `pii_officer` read the same dataset with no mask annotation.
//
// Masks are collected only from the permit policies that grant a read, so a
// pii_officer trips the `unless` (the masking policy does not apply to them)
// and is instead granted by the annotation-free policy — seeing real values.
// The row filter from tenant-isolation.cedar still applies to both.
@id("customers_mask_pii")
@mask_email("'***@***'")
@mask_ssn("'***-**-****'")
permit(
    principal,
    action == Spice::Action::"read",
    resource == Spice::Dataset::"customers"
)
unless { principal in Spice::Role::"pii_officer" };

@id("customers_pii_officer_unmasked")
permit(
    principal in Spice::Role::"pii_officer",
    action == Spice::Action::"read",
    resource == Spice::Dataset::"customers"
);
