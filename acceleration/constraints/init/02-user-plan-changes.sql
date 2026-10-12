-- Append-only history: each plan change is a new row, so an email appears once per change.
-- Rows are inserted out of time order on purpose.
CREATE TABLE user_plan_changes (
    email      TEXT NOT NULL,
    plan       TEXT NOT NULL,
    changed_at TIMESTAMP NOT NULL
);

INSERT INTO user_plan_changes (email, plan, changed_at)
VALUES
    ('alice@sample.com',     'free',       '2024-06-01 10:00:00'),
    ('alice@sample.com',     'enterprise', '2024-06-01 12:00:00'),
    ('alice@sample.com',     'pro',        '2024-06-01 11:00:00'),
    ('bob@umbrellacorp.com', 'pro',        '2024-06-01 09:00:00');
