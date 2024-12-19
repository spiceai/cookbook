CREATE TABLE users (
    email        TEXT NOT NULL PRIMARY KEY,
    username     TEXT NOT NULL,
    items_bought BIGINT NOT NULL,
    last_login   TIMESTAMP NOT NULL,
    created_at   TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at   TIMESTAMP NOT NULL
);

-- Create the trigger function to update the updated_at column
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create the trigger
CREATE TRIGGER set_updated_at
BEFORE UPDATE ON users
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();

-- Trigger for inserts
CREATE TRIGGER set_created_at
BEFORE INSERT ON users
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();