# BAL v0.4.0 Observation Data Schema

A fitting dataset is a UTF-8 CSV or JSON array of records with these fields:

| Field | Meaning | Domain |
|---|---|---|
| a | normalized DDS/formulation input | [0, 1] |
| m | first-pass metabolism fraction | [0, 1) |
| b | positive tolerance/feedback state | > 0 |
| y | observed normalized availability response | >= 0 |

All values must be finite numbers. Each row should correspond to a documented
experimental condition and response measurement. Keep units, assay method,
timepoint, replicate identifier and provenance in accompanying metadata.

Example synthetic record (not experimental data):
```json
{"a": 0.5, "m": 0.2, "b": 0.4, "y": 0.79}
```
The response above is illustrative only; calculate y from the declared model and
parameters when constructing a synthetic test fixture.
