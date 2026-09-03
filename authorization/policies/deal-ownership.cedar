// Row-level security (RLS) by row ownership, with an admin override.
//
// The first policy lets any authenticated user read `deals`, but the row filter
// restricts the result to rows the caller owns — rows whose `owner` column
// equals the caller's user id (the `sub` claim, exposed to SQL as
// current_user_id()). It does NOT apply to the `admin` role (the `unless`).
//
// The second policy grants the `admin` role a read filtered only by tenant, so
// an admin sees every deal in their own org — not just the ones they own, but
// still not another tenant's. This mirrors the PII-officer override in
// pii-masking.cedar: a role is excluded from the restrictive policy and granted
// by a separate policy, so the owner filter is not collected for it.
//
// This is finer-grained than tenant isolation: two non-admin users in the SAME
// tenant see different rows, because ownership is per-user, not per-org.
// Multitenancy (tenant-isolation.cedar) filters by current_org_id(); this
// filters by current_user_id().
@id("deals_owner_rls")
@row_filter("owner = current_user_id()")
permit(
    principal,
    action == Spice::Action::"read",
    resource == Spice::Dataset::"deals"
)
unless { principal in Spice::Role::"admin" };

@id("deals_admin_tenant")
@row_filter("tenant_id = current_org_id()")
permit(
    principal in Spice::Role::"admin",
    action == Spice::Action::"read",
    resource == Spice::Dataset::"deals"
);
