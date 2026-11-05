# Pool 8's frozen predictions (Q142(x)): what each file is, for the card lanes

*Thu 5 Nov 2026, desk only. The whole record, with the counts, the checks and the departures, is
[`docs/reports/data/2026-11-05-q142x-pool8-freeze/README.md`](../../../../docs/reports/data/2026-11-05-q142x-pool8-freeze/README.md); the sha256
of every file below is in that directory's `SHA256SUMS`. Nothing here is measured.*

| file | what |
|---|---|
| `MANIFEST`, `tiles/`, `RERUNS`, `real/`, `provenance-blind8.json`, `README.md`, `SHA256SUMS` | the pool, the designer's 90 files, unchanged (`DESIGN.md` and `make_blind8.py`, `153b720f`) |
| `DESIGN.md.dated-note-1.md` (A1), `blind8_json.py`, `roundtrip-blind7.json`, `a1_checks.py`, `a1-checks.txt` | dated note A1 and its files (`ebf68c52`, committed before any of the files below) |
| `blind8.json` | the pool's manifest in pool 7's JSON form, by `blind8_json.py convert` (A1-1), so that the frozen predictor reads the pool |
| `sets-blind8.json` | what the predictor reads from it before any count (A1-3): roles 3 / 6 / 3, N1 31 (11 / 8 / 12), F1 19, I1 12, RR 12, KA 2 |
| `predictions-pool8-aifoundry3.json`, `-aifoundry1c1.json` (+ `.md`) | 600 MHz: M10's per-op coefficient per tile (the primary is s x the measured rate x it, after the session's anchors), M10's a-priori arm (s = 1, the stated rate) and band, M9 beside, the 4.5 s heat, term b's N and e(N); the re-runs' LG references |
| `predictions-pool8-aifoundry2.json` (+ `.md`) | M10 carried by rule E through M9's aifoundry2 part, M9's part on M9's D beside, each tile's governed fallback block, and `admission_82w_out` (11 fp32 tiles out at 82 W) |
| `predictions-pool8-aifoundry1c0.json` (+ `.md`) | the same carried on to card 0 through E170's card term (κ0 0.9463), with the card-0 fallback block; E170's admission and stops apply there |
| `intervals-pool8.json` | every section-7 line at the planned n, and LG's block with its power at the pool's own design (`predict_pool8_a2.py intervals`) |

All four predictions files come from `docs/reports/data/2026-11-05-q142p-pool8-predictor/predict_pool8_a2.py predict` (never
`predict_pool8.py`) on the counts in `docs/reports/data/2026-11-05-q142x-pool8-freeze/bench/`, and a re-run writes them byte for byte.
At scoring, a 600 MHz session runs `scale`, then `primary`, on its own registered reduction; a governed session runs `burst` on its own
zeros-anchor reads and die starts (POOL8-REGISTRATION.md sections 3, 5 and 10).
