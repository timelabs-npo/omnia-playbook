CREATE TABLE _projection_meta (
    projection_name TEXT PRIMARY KEY,
    last_seq INTEGER NOT NULL CHECK (last_seq >= 0),
    last_digest TEXT,
    projector_version INTEGER NOT NULL,
    schema_version INTEGER NOT NULL
) WITHOUT ROWID;

CREATE TABLE evidence (
    event_id TEXT PRIMARY KEY,
    sequence INTEGER NOT NULL UNIQUE,
    observed_at TEXT NOT NULL,
    evidence_kind TEXT NOT NULL CHECK (
        evidence_kind IN ('observation', 'finding')
    ),
    status TEXT NOT NULL CHECK (status IN ('PASS', 'FAIL', 'UNKNOWN', 'ERROR')),
    source_adapter TEXT NOT NULL,
    subject_type TEXT NOT NULL,
    subject_ref TEXT NOT NULL,
    payload_json TEXT NOT NULL,
    event_digest TEXT NOT NULL UNIQUE
) WITHOUT ROWID;

CREATE INDEX evidence_subject_sequence
    ON evidence(subject_type, subject_ref, sequence);
