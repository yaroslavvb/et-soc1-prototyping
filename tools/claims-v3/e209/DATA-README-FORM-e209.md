# E209 session {{SESSION}}, {{DAY}}: the blind matmul day on aifoundry2 card 0 under its governor (rgm136, MM1-v2's frozen forecasts), the session's records

*Written by the card lane's collection (`tools/claims-v3/e209/collect_e209.py`, runbook step 11) from the session's own records; the card lane adds
its dated departures and notes below before the data commit. **E209** is registered in `tools/claims-v3/e209/E209.md` (its freeze line: MM1-v2's
forecasts pushed in `3ca4b717` at 01:44:48 PST Tue 17 Nov 2026) and kitted in `tools/claims-v3/e209/KIT.md`. This directory holds the measured
records and the lab's desk checks of them; **no score is here**: the registered reducer and the frozen scorer run after this data commit (runbook
step 13) and a later lane commits their outputs beside it.*

**Labels.** Everything under `session/` is **measured** (the card's own records, written by E208's registered runner, unchanged, on its real path);
the schedule, the run forms, the windows, the stop lines and the reduction's rules are **registered** (E209.md, E208's kit at its sha256s);
`checks-e209.*` is **the lab's desk check of the records** (E208's data lane's checker, unchanged); `facts-e209.json` is the collection's
reading of the records; `neverrun-e209-card.txt` and `ranbefore-e209.json` are the never-run search repeated right before the first card command
(**desk**, REPORTED). The desk steps ran under `/usr/bin/python3` 3.12.3 on aifoundry2.

## The session (from its records)

| | |
|---|---|
| card | aifoundry2 card 0 under its own governor, as found (read, never set) |
| session | `{{SESSION}}`, T0 {{T0}}; runner rc {{RUNNERRC}} |
| the window | G {{G}}; last start {{LASTSTART}}; last end {{LASTEND}} (G + 1:30 and G + 3:30, rounded up) |
| the reboot gate (step 7) | stamp {{FIRST}}, `{{FWGATE}}` (the record in `session/first/`) |
| the end | {{CLOSE}}; **{{CARDMIN}} card-minutes** from the session's config read (the runner's count) |
| runs | {{RAN}} of 62 ran; not run: {{NOTRUN}} |
| stop | {{STOP}} |
| the lab's checks | {{CHECKS}} |
| never-run (step 6n) | {{NEVERRUN}} |

## Departures and notes, dated (the card lane writes these before the data commit)

1. **The go**: the owner's standing words of Sun 15 Nov 2026 and of Mon 16 Nov 2026 (E209.md section 6), with E209's
   registered items as their defaults; G = the booking on its day; **the post waived** (his words of 10:22:36 PST Sun 15 Nov 2026); **the host's
   package counter not read**; the desk aifoundry2 with Python 3.12.3 (`/usr/bin/python3`).
2. (the card lane: every departure from the go lines, every stop, gate, dropped run or cut point, with its time)

## Files

| file | what | label |
|---|---|---|
| `session/` | the session's folder as E208's runner wrote it, byte for byte (its `MANIFEST.sha256` lists every file but itself, `runner.out` and `runner.rc`); `first/` holds step 7's reboot-gate record | measured |
| `checks-e209.json`, `checks-e209.txt` | E208's data lane's checks C0-C8 (unchanged checker) | desk check of the records |
| `build-record-aifoundry2.json` | the box root's build record of the day, byte for byte | record |
| `facts-e209.json` | the collection's facts | desk reading |
| `neverrun-e209-card.txt`, `ranbefore-e209.json` | step 6n's search and its labels (the scorer's `--labels` form) | desk, REPORTED |
| `SHA256SUMS` | every file here but itself | - |
