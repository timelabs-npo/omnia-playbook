CREATE TABLE _projection_meta (
    projection_name TEXT PRIMARY KEY,
    last_seq INTEGER NOT NULL CHECK (last_seq >= 0),
    last_digest TEXT,
    projector_version INTEGER NOT NULL,
    schema_version INTEGER NOT NULL
) WITHOUT ROWID;

CREATE TABLE events (
    sequence INTEGER PRIMARY KEY,
    event_id TEXT NOT NULL UNIQUE,
    observed_at TEXT NOT NULL,
    kind TEXT NOT NULL CHECK (
        kind IN (
            'observation',
            'finding',
            'plan',
            'approval',
            'execution',
            'verification',
            'reversal'
        )
    ),
    status TEXT NOT NULL CHECK (status IN ('PASS', 'FAIL', 'UNKNOWN', 'ERROR')),
    source_adapter TEXT NOT NULL,
    subject_type TEXT NOT NULL,
    subject_ref TEXT NOT NULL,
    previous_digest TEXT,
    digest TEXT NOT NULL UNIQUE,
    event_json TEXT NOT NULL
);

CREATE INDEX events_kind_sequence ON events(kind, sequence);
CREATE INDEX events_status_sequence ON events(status, sequence);
