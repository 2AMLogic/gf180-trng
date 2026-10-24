# Stored-evidence manifests

One `<stem>.manifest.json` per recorded simulation point, written by
`sim/run_corners.py` through `klt artifact put`. The raw output of that point
(decks, logs, input snapshots) lives in the artifact store; git keeps only the
manifest and the record `sim/records/<stem>.md`, whose `stored_evidence` table
repeats each object's name, size and sha256.

- Every entry `uri` starts with `artifact:`. A manifest names objects by
  content hash; it never names a bucket, an account or a broker URL.
- Manifests are append-only (`npm run check:evidence-history`).
- `npm run check:artifact-manifests` validates the schema and fails if the
  bytes of a stored object are also committed.
- To re-check the stored bytes themselves, run `klt artifact verify <manifest>`
  on a fleet worker (it needs the broker, so CI does not).

Records written before this convention keep their raw output under
`sim/records/raw/<stem>/`; they are not migrated. See
`spec/decision-records/DR-0032-stored-evidence-for-new-sim-runs.md`.
