// Multi-tenancy (tenant isolation).
//
// Every authenticated user may read `customers`, but the row filter restricts
// the result to rows whose `tenant_id` equals the caller's `org` claim
// (exposed to SQL as current_org_id()). One filter isolates every tenant — no
// per-tenant policy needed. Row-level security by row ownership is a separate
// pattern; see deal-ownership.cedar.
@id("customers_tenant_isolation")
@row_filter("tenant_id = current_org_id()")
permit(
    principal,
    action == Spice::Action::"read",
    resource == Spice::Dataset::"customers"
);
