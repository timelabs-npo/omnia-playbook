CREATE TABLE _projection_meta (
    projection_name TEXT PRIMARY KEY,
    last_seq INTEGER NOT NULL CHECK (last_seq >= 0),
    last_digest TEXT,
    projector_version INTEGER NOT NULL,
    schema_version INTEGER NOT NULL
) WITHOUT ROWID;

CREATE TABLE workflow_events (
    event_id TEXT PRIMARY KEY,
    sequence INTEGER NOT NULL UNIQUE,
    observed_at TEXT NOT NULL,
    workflow_kind TEXT NOT NULL CHECK (
        workflow_kind IN (
            'plan',
            'approval',
            'execution',
            'verification',
            'reversal'
        )
    ),
    status TEXT NOT NULL CHECK (status IN ('PASS', 'FAIL', 'UNKNOWN', 'ERROR')),
    subject_type TEXT NOT NULL,
    subject_ref TEXT NOT NULL,
    payload_json TEXT NOT NULL,
    event_digest TEXT NOT NULL UNIQUE
) WITHOUT ROWID;

CREATE INDEX workflow_subject_sequence
    ON workflow_events(subject_type, subject_ref, sequence);
