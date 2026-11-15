# E191's data README form (step 12): what the card lane writes beside the collected files, before the data commit

*Q178, the kit, Sat 14 Nov 2026, after E189's data commit fa9098c4 and before any E191 datum. The form of E189's data README (the lab's
form: results first, registered against happened, departures dated), with the two items E189's card lane reported about its own README
(its incidents 1 and 2) made part of the form. The card lane writes `docs/reports/data/<day>-e191-blind-day-aifoundry1-c1/README.md` from
this form, NEVER edits a collected file, and runs `rb/readme_check_e191.py` on the README before the public-text scan and the commit.*

The README holds these sections, in this order (each heading as written here; the checker reads them):

1. **`# E191: ...`** a title line naming E191, aifoundry1 card 1 and the day, then one paragraph: registered in `300d76e4` (E191.md), its
   dated note 1 `8c8f825f`, kitted in `<the kit's commit>` (KIT.md), all before any E191 datum; the session's T0, its start and end in PST,
   its card-minutes; what ran; "reads only"; the post as that day's go says it (made, or waived in his words with their date).
2. **`## What ran (measured)`**: the session, the identity lines as the session log reads them (identity (a) and (b), each smoke host's
   card), the clock (600 MHz in n of n samples), the peaks against the stops (65 W, 70 C), the config at both ends (TDP 65 W / 65 C / 600
   MHz, minion_mv), every stop, gate, skip, SHORT burst and FAILED RUN by its pass (the session log's reading words), any BOUND line
   (and, after it, how long card 1's lock was held while that host ran, or that it was released with the host still running: queue.json
   `bound`), any "the sampler is not live" line and restart (each host's `sample_age_s_at_host_start` in run.json), and an early stop
   (the stop file or a SIGTERM: queue.json `early_stop`) - the kit's fixes after its verifier (fix-e191k); and, after its second verifier
   (fix-e191k2), every pass flagged "the sampler was not live during this pass" (run.json's `live_gap_s_pass`, `live_gap_s_host`,
   `live_samples_host` and the three ages; queue.json's `passes_sampler_not_live`: reported beside the pass, which is kept and scored as
   registered), the count of the reader's lines without a stop line's reading (queue.json `sampler_lines_not_live`), and an early stop at
   the gate by its own line ("... before / during the stop-path test: the gate, no launch").
3. **`## The passes (measured; ...)`**: one row per pass (the reducer's J over idle and J with the card at rest a launch, t_k, t_w, T0,
   flags), means as desk arithmetic, never verdicts. The four rules' words come from the scorer, after the data commit, not here.
4. **`## Registered against happened`**: a table, registered (E191.md and the kit) beside measured.
5. **`## Departures and notes (dated ...)`**: each departure dated and named before the session where it was set by the go (the post,
   the desk, the interpreter), the rest after the collection, said so.
6. **`## Device commands sent`**: the kit's READs only (dmcmd_audit GO at step 2, on the box after the build, in the session); no set, reset,
   statistics reset, firmware-revisions query, power cycle; card 0 never opened (ET_DEVICES=1 for every device process).
7. **`## Privacy and the public-text scan`**: the collector's scrub (the box home to `~`, the box login to `<login>`), the desk-path gate,
   the public-text scan's result over this directory and the commit message. **E189's incident 2, now part of the form:** the unchanged
   reducer writes into every `energy.json` its fixed note "assumed package power (RAPL is root-only)" (energy_reduce.py), which a scan's
   root pattern matches; such hits are kept as collected (a collected file is never edited) and named here with their count.
8. **`## Files`**: a table with one row per directory or file kind. **E189's incident 1, now checked:** every file name `FILES.txt` lists
   (the collector writes it: every file under the directory) must be named in this table by its basename or its directory's row, sparse
   parity's `host.rec` among them, the session's `config-*.err`, `identity.json`, `etwho-identity.txt` and `commands.jsonl` among them;
   `rb/readme_check_e191.py` refuses a README whose table misses one.
9. **`## Next`**: the scorer after the data commit (s24), its output committed by a later lane.

A sample Files table that passes the checker for a whole session (copy it, then correct it to what was collected):

| path | what |
|---|---|
| `passes/<configuration>/p<k>/` | one pass (E191.md 8.1): `telemetry.jsonl.gz`, `host.json` (the reducer's input: the ledger host's line through the adapter, or sparse parity's own line), `host-raw.json` (the ledger host's own line), `host.rec` (sparse parity's records), `host.err` (the host's stderr: its device-layer block names card 1), `run.json`, `pass.json`, `energy.json` and `energy.txt` (the reducer's output) |
| `session/` | the session directory as copied back (COPY-BACK EXACT), scrubbed: `session.log`, `queue.json`, `identity.json`, `config-start.json`, `config-start.err`, `config-end.json`, `config-end.err`, `etwho-before.txt`, `etwho-identity.txt`, `commands.jsonl`, `stop-path.json`, `anchors.json`, `smoke/<run>/` (`stdout.txt`, `host.err`, `smoke.json`), `sampler.err`, `telemetry.jsonl.gz`, `runner.out`, `runner.rc`, `MANIFEST.sha256`, and `STOP` only when an early stop was asked for (an empty file) |
| `SHA256SUMS` | the collector's: every file but this README, itself and FILES.txt |
| `FILES.txt` | the collector's list of every file, by path |

SPDX-License-Identifier: Apache-2.0
