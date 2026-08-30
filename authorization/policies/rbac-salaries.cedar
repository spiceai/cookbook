// Role-based access control (RBAC).
//
// Only members of the `hr` role may read `salaries`; the row filter further
// restricts them to their own tenant. Because the runtime default is `deny`,
// any caller without the `hr` role (for example an `analyst`) is denied — no
// explicit forbid policy is required.
@id("salaries_hr_only")
@row_filter("tenant_id = current_org_id()")
permit(
    principal in Spice::Role::"hr",
    action == Spice::Action::"read",
    resource == Spice::Dataset::"salaries"
);
