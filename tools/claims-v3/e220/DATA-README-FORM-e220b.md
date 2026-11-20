# E220 session {{SESSION}}, {{DAY}}: arm B of MM1-v3.2's card-transfer blind day on aifoundry2 card 0 under its governor at 799 MHz (route c) (rgm136; family G on rgm211's host), the session's records

*Written by the card lane's collection (`tools/claims-v3/e220/collect_e220b.py`, runbook step 11) from the session's own records; the card lane adds
its dated departures and notes below before the data commit. **E220** is registered in `tools/claims-v3/e220/E220.md` (its freeze line: the
registration's commit, which froze every forecast E220 scores) and kitted in `tools/claims-v3/e220/KIT.md`. This directory holds the measured
records and the lab's desk checks of them; **no score is here**: E208's registered reducer and the frozen scorer `score_e220.py` run after this
data commit (runbook step 13) and a later lane commits their outputs beside it.*

**Labels.** Everything under `session/` is **measured** (the card's own records, written by `src/run_e220b.py` - E208's registered runner,
unchanged and imported, with E220's registered stop lines and family G - on its real path), but for one line of fwgate's read record in
`session/first/` whose box home is written as `~` (THE MASK, registered in E220's kit before any datum; the collection printed both sha256);
the schedule, the run forms, the windows, the stop lines and the reduction's rules are **registered** (E220.md, E208's kit at its sha256s);
`checks-e220b.*` is **the lab's desk check of the records** (E208's data lane's checker, unchanged); `facts-e220b.json` is the collection's
reading of the records; `neverrun-e220b-card.txt` and `ranbefore-e220b.json` are the never-run search repeated right before the first card command
(**desk**, REPORTED). The desk steps ran under `/usr/bin/python3` 3.12.3 on aifoundry2.

## The session (from its records)

| | |
|---|---|
| card | aifoundry2 card 0 under its own governor, as found (read, never set) |
| session | `{{SESSION}}`, T0 {{T0}}; runner rc {{RUNNERRC}} |
| the window | G {{G}}; last start {{LASTSTART}}; last end {{LASTEND}} (G + 1:30 and G + 3:30, rounded up) |
| the reboot gate (step 7) | stamp {{FIRST}}, `{{FWGATE}}` (the record in `session/first/`) |
| the end | {{CLOSE}}; **{{CARDMIN}} card-minutes** from the session's config read (the runner's count) |
| runs | {{RAN}} of 103 ran (s01 E208's three smoke arms; t01 at 1 and 86; s03 at 87; the G block 88-103, last); not run: {{NOTRUN}} |
| stop | {{STOP}} |
| the lab's checks | {{CHECKS}} |
| never-run (step 6n) | {{NEVERRUN}} |

## Departures and notes, dated (the card lane writes these before the data commit)

1. **The go**: the owner's standing words of Sun 15 Nov 2026, Mon 16 Nov 2026 and Tue 17 Nov 2026 and his words relayed since (E220.md
   section 6), with E220's registered items as their defaults; G = the booking on its day; **the post waived** (his words of 10:22:36 PST Sun 15
   Nov 2026); **the host's package counter not read**; the desk aifoundry2 with Python 3.12.3 (`/usr/bin/python3`).
2. (the card lane: every departure from the go lines, every stop, gate, kernel stop, dropped run or cut point, with its time; THE QUIET DESK
   FLAG's raise and lower times beside the other card lanes' launches)

## Files

| file | what | label |
|---|---|---|
| `session/` | the session's folder as the runner wrote it, byte for byte but for THE MASK's one line (its `MANIFEST.sha256` lists every file but itself, `runner.out` and `runner.rc`); `first/` holds step 7's reboot-gate record; `gates.jsonl` every process's identity gate | measured |
| `checks-e220b.json`, `checks-e220b.txt` | E208's data lane's checks C0-C8 (unchanged checker) | desk check of the records |
| `build-record-aifoundry2.json`, `build-record-e220b-aifoundry2.json` | the box root's two build records of the day (E208's build and E220's rgm211 host), byte for byte | record |
| `facts-e220b.json` | the collection's facts | desk reading |
| `neverrun-e220b-card.txt`, `ranbefore-e220b.json` | step 6n's search and its labels (the scorer's `--labels` form) | desk, REPORTED |
| `SHA256SUMS` | every file here but itself | - |
