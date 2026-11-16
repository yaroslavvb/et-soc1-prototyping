# E194's data README form (step 12): what the card lane writes beside the collected files, before the data commit

*Q183, the kit, Sun 15 Nov 2026, after E194's registration (`E194.md`, its list `SHA256SUMS-e194-registration` sha256 `788af7da...`) and
before any E194 datum. E191's form (`tools/claims-v3/e191/rb/data-readme-form-e191.md`, unchanged beside it: the lab's form, results first,
registered against happened, departures dated, with E189's incidents 1 and 2 made part of it), with aifoundry2's card, its clock and the
host's line. The card lane writes `docs/reports/data/<day>-e194-blind-day-aifoundry2/README.md` from this form, NEVER edits a collected
file, and runs `rb/readme_check_e194.py` on the README before the public-text scan and the commit.*

The README holds these sections, in this order (each heading as written here; the checker reads them):

1. **`# E194: ...`** a title line naming E194, aifoundry2 card 0 and the day, then one paragraph: registered in `<the registration's
   commit>` (E194.md), kitted in `<the kit's commit>` (KIT.md), both before any E194 datum; the session's T0, its start and end in PST,
   its card-minutes; what ran; "reads only"; **the post: "the owner waived the post: his words, Sun 15 Nov 2026 10:22:36 PST"** ("don't
   worry about discord post, just use the machines, nobody is using them"; the checker requires the words and the time).
2. **`## What ran (measured)`**: the session; the identity lines as the session log reads them (identity (a): /dev/et0_mgmt, device ID 0,
   minion_mv; identity (b); each smoke host's card); **THE CLOCK RULE, pass by pass** (the session log's "the clock ok / off / unread (n
   samples)", the passes set aside by it (queue.json `off_clock_passes`), whether a second one stopped the session, the windows with no
   live sample (queue.json `unread_clock_passes`)) and the clock in the idle samples (600 MHz, read, not checked); the peaks against the
   stops (65 W, 70 C; aifoundry2's 85 W on 3 samples, 80 C on minshire[0] or the latch minshire[2]); the config at both ends (TDP 65 W /
   65 C / 600 MHz at rest, minion_mv); every stop, gate, skip, SHORT burst and FAILED RUN by its pass (the session log's reading words);
   **every host's line read by reassembly** (run.json and smoke.json `host_line`: the method and each dropped span, verbatim, and whether
   it is a runtime line seen before; on aifoundry2's runtime none is expected); the holder rule's re-reads at the start (queue.json
   `holder_reads_at_start`); any BOUND line and the lock after it (queue.json `bound`); any "the sampler is not live" line and restart;
   every pass flagged "the sampler was not live during this pass"; an early stop (queue.json `early_stop`) or an early stop at the gate;
   **the runner's exit status** (`session/runner.rc`, written by session_e194.sh after the runner exits; step 10 and step 11 print it): 0 at
   an ordinary end, 16 at a gate; any other value is a runner fault after the gate (named here with runner.out's last lines; fix-e194,
   verify-e194's finding 3; the checker requires `runner.rc` named in this section when FILES.txt lists it).
3. **`## The passes (measured; ...)`**: one row per pass (the reducer's J over idle and J with the card at rest a launch, t_k at 800 MHz,
   t_w, T0, the clock rule's verdict, flags), means as desk arithmetic, never verdicts. The four rules' words come from the scorer, after the
   data commit, not here.
4. **`## Registered against happened`**: a table, registered (E194.md and the kit) beside measured.
5. **`## Departures and notes (dated ...)`**: each departure dated; THE QUIET DESK FLAG's span (raised, lowered) and the P2 counts before
   the look and before the launch; the go as given (his words and their time).
6. **`## Device commands sent`**: the kit's READs only (dmcmd_audit GO at step 2, on the box after the build, in the session); no set,
   reset, statistics reset, firmware-revisions query, power cycle; no governor move; ET_DEVICES and V3_DEVICE unset for every device process.
7. **`## Privacy and the public-text scan`**: THE BOX-TREE GATE (every path under the account's home in the session's files inside the box
   tree; no scratch root), the collector's scrub (the box home to `~`, the box login to `<login>`), k6's desk-path gate, the public-text
   scan's result over this directory and the commit message; the unchanged reducer's fixed note "assumed package power (RAPL is root-only)"
   in every `energy.json`, kept as collected and named here with its count (E189's incident 2).
8. **`## Files`**: a table with one row per directory or file kind; every file name `FILES.txt` lists must be named in it by its basename
   or its directory's row (E189's incident 1), `host-stdout.txt` and sparse parity's `host.rec` among them; `rb/readme_check_e194.py`
   refuses a README whose table misses one.
9. **`## Next`**: the scorer after the data commit (s24), its output committed by a later lane.

A sample Files table that passes the checker for a whole session (copy it, then correct it to what was collected):

| path | what |
|---|---|
| `passes/<configuration>/p<k>/` | one pass (E194.md 8.1): `telemetry.jsonl.gz` (the sampler's lines: THE CLOCK RULE reads their minion clock), `host.json` (the reducer's input: the ledger host's line through the adapter, or sparse parity's own line, as read), `host-raw.json` (the ledger host's own line, as read), `host-stdout.txt` (the host's raw stdout, kept), `host.rec` (sparse parity's records), `host.err` (the host's stderr: its device-layer block names card 0), `run.json`, `pass.json`, `energy.json` and `energy.txt` (the reducer's output) |
| `session/` | the session directory as copied back (COPY-BACK EXACT), scrubbed: `session.log`, `queue.json`, `identity.json`, `config-start.json`, `config-start.err`, `config-end.json`, `config-end.err`, `etwho-before.txt`, `etwho-identity.txt`, `commands.jsonl`, `stop-path.json`, `anchors.json`, `smoke/<run>/` (`stdout.txt`, `host.err`, `smoke.json`), `sampler.err`, `telemetry.jsonl.gz`, `runner.out`, `runner.rc`, `MANIFEST.sha256`, and `STOP` only when an early stop was asked for (an empty file) |
| `SHA256SUMS` | the collector's: every file but this README, itself and FILES.txt |
| `FILES.txt` | the collector's list of every file, by path |

SPDX-License-Identifier: Apache-2.0
