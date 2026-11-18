-- IT Service Desk Copilot: enterprise data the agent reads (a 300-person sample).
-- Portable SQL: PostgreSQL 14 or later, and SQLite 3.35 or later. All times are UTC.

CREATE TABLE regions (
    region        TEXT PRIMARY KEY,
    name          TEXT NOT NULL,
    support_hours TEXT NOT NULL,
    phone         TEXT NOT NULL,
    tech_bar      TEXT NOT NULL
);

CREATE TABLE offices (
    office TEXT PRIMARY KEY,
    code   TEXT NOT NULL UNIQUE,
    region TEXT NOT NULL REFERENCES regions (region)
);

CREATE TABLE employees (
    employee_id TEXT PRIMARY KEY,
    full_name   TEXT NOT NULL,
    email       TEXT NOT NULL UNIQUE,
    department  TEXT NOT NULL,
    job_title   TEXT NOT NULL,
    role        TEXT NOT NULL CHECK (role IN ('employee', 'analyst', 'admin')),
    is_manager  BOOLEAN NOT NULL,
    manager_id  TEXT REFERENCES employees (employee_id),
    office      TEXT NOT NULL REFERENCES offices (office),
    region      TEXT NOT NULL REFERENCES regions (region),
    start_date  DATE NOT NULL,
    status      TEXT NOT NULL
);

CREATE TABLE devices (
    asset_tag       TEXT PRIMARY KEY,
    device_type     TEXT NOT NULL CHECK (device_type IN ('laptop', 'phone')),
    model           TEXT NOT NULL,
    os              TEXT NOT NULL,
    os_version      TEXT NOT NULL,
    serial_number   TEXT NOT NULL UNIQUE,
    purchase_date   DATE NOT NULL,
    ram_gb          INTEGER,
    storage_gb      INTEGER NOT NULL,
    assigned_to     TEXT REFERENCES employees (employee_id),
    status          TEXT NOT NULL CHECK (status IN ('in use', 'in stock', 'in repair', 'lost', 'retired')),
    encrypted       BOOLEAN NOT NULL,
    compliant       BOOLEAN NOT NULL,
    last_patch_date DATE,
    pending_updates INTEGER NOT NULL
);

CREATE TABLE software_catalogue (
    app_id            TEXT PRIMARY KEY,
    name              TEXT NOT NULL UNIQUE,
    vendor            TEXT NOT NULL,
    category          TEXT NOT NULL,
    licence_type      TEXT NOT NULL CHECK (licence_type IN ('Free', 'Site', 'Named')),
    annual_charge_usd INTEGER NOT NULL,
    approval_rule     TEXT NOT NULL,
    platforms         TEXT NOT NULL,
    delivery          TEXT NOT NULL,
    restricted        BOOLEAN NOT NULL,
    seats_total       INTEGER
);

CREATE TABLE entitlements (
    employee_id TEXT NOT NULL REFERENCES employees (employee_id),
    app_id      TEXT NOT NULL REFERENCES software_catalogue (app_id),
    granted_at  DATE NOT NULL,
    last_used   DATE NOT NULL,
    PRIMARY KEY (employee_id, app_id)
);

CREATE TABLE role_profiles (
    profile_id  TEXT PRIMARY KEY,
    department  TEXT NOT NULL UNIQUE,
    name        TEXT NOT NULL,
    laptop_type TEXT NOT NULL
);

CREATE TABLE role_profile_apps (
    profile_id TEXT NOT NULL REFERENCES role_profiles (profile_id),
    app_id     TEXT NOT NULL REFERENCES software_catalogue (app_id),
    PRIMARY KEY (profile_id, app_id)
);

CREATE TABLE services (
    service     TEXT PRIMARY KEY,
    description TEXT NOT NULL
);

CREATE TABLE service_incidents (
    incident_id INTEGER PRIMARY KEY,
    service     TEXT NOT NULL REFERENCES services (service),
    region      TEXT NOT NULL,
    status      TEXT NOT NULL CHECK (status IN ('degraded', 'outage')),
    started_at  TIMESTAMP NOT NULL,
    resolved_at TIMESTAMP,
    message     TEXT NOT NULL
);

-- Seats in use and free for every licensed application.
CREATE VIEW licence_pool AS
SELECT c.app_id,
       c.name,
       c.seats_total,
       COUNT(e.employee_id) AS seats_used,
       c.seats_total - COUNT(e.employee_id) AS seats_free
FROM software_catalogue c
LEFT JOIN entitlements e ON e.app_id = c.app_id
WHERE c.seats_total IS NOT NULL
GROUP BY c.app_id, c.name, c.seats_total;

-- Status of every service in every region right now. No open incident means operational.
CREATE VIEW service_status AS
SELECT s.service,
       r.region,
       COALESCE(i.status, 'operational') AS status,
       i.started_at,
       i.message
FROM services s
CROSS JOIN regions r
LEFT JOIN service_incidents i
       ON i.service = s.service
      AND i.resolved_at IS NULL
      AND i.region IN (r.region, 'Global');
