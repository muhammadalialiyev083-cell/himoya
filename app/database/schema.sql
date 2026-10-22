CREATE TABLE admin (
 id INTEGER PRIMARY KEY CHECK(id=1), username TEXT NOT NULL UNIQUE,
 salt TEXT NOT NULL, password_hash TEXT NOT NULL, iterations INTEGER NOT NULL
);
CREATE TABLE organization (
 id INTEGER PRIMARY KEY CHECK(id=1), name TEXT NOT NULL CHECK(length(trim(name))>0),
 industry TEXT NOT NULL DEFAULT '', description TEXT NOT NULL DEFAULT '', responsible TEXT NOT NULL DEFAULT ''
);
CREATE TABLE department (
 id INTEGER PRIMARY KEY, organization_id INTEGER NOT NULL DEFAULT 1 REFERENCES organization(id) ON DELETE RESTRICT,
 name TEXT NOT NULL CHECK(length(trim(name))>0), responsible TEXT NOT NULL DEFAULT '', UNIQUE(organization_id,name)
);
CREATE TABLE business_process (
 id INTEGER PRIMARY KEY, code TEXT NOT NULL UNIQUE CHECK(length(trim(code))>0),
 name TEXT NOT NULL CHECK(length(trim(name))>0), description TEXT NOT NULL DEFAULT '',
 department_id INTEGER NOT NULL REFERENCES department(id) ON DELETE RESTRICT,
 responsible TEXT NOT NULL DEFAULT '', resources TEXT NOT NULL DEFAULT '', it_dependency TEXT NOT NULL DEFAULT '',
 status TEXT NOT NULL DEFAULT 'Faol'
);
CREATE TABLE bia_assessment (
 id INTEGER PRIMARY KEY, process_id INTEGER NOT NULL UNIQUE REFERENCES business_process(id) ON DELETE CASCADE,
 financial REAL NOT NULL CHECK(financial BETWEEN 0 AND 5), operational REAL NOT NULL CHECK(operational BETWEEN 0 AND 5),
 reputational REAL NOT NULL CHECK(reputational BETWEEN 0 AND 5), compliance REAL NOT NULL CHECK(compliance BETWEEN 0 AND 5),
 mtpd REAL NOT NULL CHECK(mtpd>0), rto REAL NOT NULL CHECK(rto>0 AND rto<=mtpd), rpo REAL NOT NULL CHECK(rpo>=0)
);
CREATE TABLE risk (
 id INTEGER PRIMARY KEY, title TEXT NOT NULL CHECK(length(trim(title))>0),
 process_id INTEGER NOT NULL REFERENCES business_process(id) ON DELETE RESTRICT,
 threat TEXT NOT NULL DEFAULT '', vulnerability TEXT NOT NULL DEFAULT '',
 likelihood INTEGER NOT NULL CHECK(likelihood BETWEEN 1 AND 5), impact INTEGER NOT NULL CHECK(impact BETWEEN 1 AND 5),
 mitigation TEXT NOT NULL DEFAULT '', owner TEXT NOT NULL DEFAULT '', action TEXT NOT NULL DEFAULT '', status TEXT NOT NULL DEFAULT 'Ochiq'
);
CREATE TABLE recovery_strategy (
 id INTEGER PRIMARY KEY, name TEXT NOT NULL CHECK(length(trim(name))>0),
 process_id INTEGER NOT NULL REFERENCES business_process(id) ON DELETE RESTRICT,
 actions TEXT NOT NULL DEFAULT '', resources TEXT NOT NULL DEFAULT '', responsible TEXT NOT NULL DEFAULT '',
 priority INTEGER NOT NULL CHECK(priority BETWEEN 1 AND 5)
);
CREATE TABLE continuity_plan (
 id INTEGER PRIMARY KEY, code TEXT NOT NULL UNIQUE CHECK(length(trim(code))>0), name TEXT NOT NULL CHECK(length(trim(name))>0),
 process_id INTEGER NOT NULL REFERENCES business_process(id) ON DELETE RESTRICT,
 risk_id INTEGER REFERENCES risk(id) ON DELETE SET NULL, strategy_id INTEGER REFERENCES recovery_strategy(id) ON DELETE SET NULL,
 responsible TEXT NOT NULL DEFAULT '', objectives TEXT NOT NULL DEFAULT '', resources TEXT NOT NULL DEFAULT '',
 review_date TEXT NOT NULL, status TEXT NOT NULL DEFAULT 'Loyiha'
);
CREATE TABLE recovery_step (
 id INTEGER PRIMARY KEY, plan_id INTEGER NOT NULL REFERENCES continuity_plan(id) ON DELETE CASCADE,
 position INTEGER NOT NULL CHECK(position>0), instruction TEXT NOT NULL CHECK(length(trim(instruction))>0),
 completed INTEGER NOT NULL DEFAULT 0 CHECK(completed IN (0,1)), UNIQUE(plan_id,position)
);
CREATE TABLE scenario (
 id INTEGER PRIMARY KEY, name TEXT NOT NULL CHECK(length(trim(name))>0), description TEXT NOT NULL DEFAULT '',
 duration REAL NOT NULL CHECK(duration>=0), resources TEXT NOT NULL DEFAULT '', actions TEXT NOT NULL DEFAULT ''
);
CREATE TABLE scenario_affected_process (
 scenario_id INTEGER NOT NULL REFERENCES scenario(id) ON DELETE CASCADE,
 process_id INTEGER NOT NULL REFERENCES business_process(id) ON DELETE RESTRICT, PRIMARY KEY(scenario_id,process_id)
);
CREATE TABLE scenario_plan (
 scenario_id INTEGER NOT NULL REFERENCES scenario(id) ON DELETE CASCADE,
 plan_id INTEGER NOT NULL REFERENCES continuity_plan(id) ON DELETE CASCADE, PRIMARY KEY(scenario_id,plan_id)
);
CREATE TABLE scenario_result (
 id INTEGER PRIMARY KEY, scenario_id INTEGER NOT NULL REFERENCES scenario(id) ON DELETE CASCADE,
 evaluated_at TEXT NOT NULL, result_json TEXT NOT NULL
);
CREATE INDEX risk_process ON risk(process_id);
CREATE INDEX plan_process ON continuity_plan(process_id);
PRAGMA user_version=1;
