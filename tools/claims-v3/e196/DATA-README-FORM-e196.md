# E196's data README: the form the card lane fills for the data commit (Q185, lane kit-e196; kitted, not run)

*Sun 15 Nov 2026 (week 46), PST, desk only, beside [KIT.md](KIT.md). E193's form ([../e193/DATA-README-FORM-e193.md](../e193/DATA-README-FORM-e193.md)),
with E196's files. This is the form of `README.md` in `docs/reports/data/<day>-e196-zeroshare-aifoundry3/`, written by the card lane
after step 11 (the collection) and before the data commit, for a session in which a train or pass block ran, in the lab's data-README form:
**results first, then registered against happened, then departures, each dated**. It is a form, not a result: every `<...>` is filled from
the session's own files (`facts-e196.json`, `session/session.log`, `run/session.log`, the runbook's log), and every number carries its
label. The README lies beside the data and is not in its `SHA256SUMS` (the collector made that list over the collected files). A session
that ended at a gate (no train and no pass block) has no data directory: step 11 collects it into a gate stop's record, whose README has the
shorter form at the end of this file.*

**The rules for this file.** No forecast number of the sealed forecast and no score against it (E196.md 0: the model session scores it,
privately, after the data commit). No lab user's login (the collector's scrub already masked them in the data; write `<login>` if one must
be named). No number from a private page. Times Pacific. The interpreter named. A check not run is NOT RUN. The
reduced prices are not in the data commit: step 13 (`rb/s24_reduce_e196.sh`) runs the registered reduction after it, and the records lane
commits its outputs beside the data in a later commit, with this README's "Reduced" section filled then by a dated note.

---

```
# E196, <day>, aifoundry3 card 0 at 600 MHz as found: <one line of what happened: RAN WHOLE (the smoke, T1, T2, <6|7> passes) / STOPPED at
<reason> after <trains k of 2, passes k of 7> / ENDED WITHOUT A REGISTERED STOP (a crash: <the port's last line>), its reduction decided by
a dated note>

*<the day>, PST. The model session's proposal X14 (request 1113-x14-zeroshare version 3), registered as E196 (<the registration's landed
commit>) with its forecast sealed by sha256 (5c5acc16...; contents sealed), kitted (<the kit's landed commit>), verified (<the verifier's
lane and verdict>) and readiness-checked (<lane, verdict>); run on the owner's go of <date and time, his words or their record>. The
passes and the train anchors on the lab's unchanged sparsity host, the trains on the request's x14_host (E196.md section 3). Nothing was
set on the card.*

## Results (measured: the session's own records; the reduced prices follow after the data commit)

| what | value | label |
|---|---|---|
| card-minutes, first card command to "session end" | <facts: card_minutes_first_command_to_session_end> (cap 60) | measured (the session's clock) |
| the cut order at the start | <the wrapper's "the cut order: M = ..." line> | measured (the clock at the first card command) |
| blocks complete | <facts: blocks_after; the wrapper's "trains complete: k of 2; passes complete: k of 7" line> | measured |
| device processes; pass launch records; train launch records; read-backs of C (X14CHECK) and those not ok | <device_processes>; <pass_launch_records>; <train_launch_records>; <x14check_records> / <x14check_not_ok> | measured |
| how the session ended | <the wrapper's line: ended / "session stopped: ...; the blocks done stand" / "session ended without a registered stop">; session.rc <0, 1 or 4>; STOP <facts: stop> | measured |
| the smoke (the heater check; four arms on each host; two T1 processes) and its gate | <facts: smoke_gate; run/session.log's "smoke gate passed"> | measured |
| runtime lines dropped from the hosts' stdout; host outputs that could not be read (no record written) | <runtime_lines_dropped>; <unreadable_host_outputs> | measured (run_block_e196.py's marks) |
| telemetry samples, and those not at 600 MHz | <telemetry_samples> / <samples_off_600_MHz> | measured |
| board power, peak; die, peak (minshire[0]), with how many samples read it and the first | <board_w_peak>; <die_c_peak> | measured |
| the opening and closing configuration reads | <TDP / threshold / MHz at the start; at the close> | measured (READ) |

## Registered against happened

| registered (E196.md, KIT.md) | happened |
|---|---|
| aifoundry3 card 0, 600 MHz as found, nothing set; the opening read TDP 0 W and 600 MHz (E196.md 4 and 6) | <the configuration reads; the clock in every sample> |
| the 40-minute rest before the session (E196.md 10), after E195's | <step 9's "rest:" line from the runbook log; step 7's time against it> |
| the host assignment (E196.md 3) | <the records' "binary" counts: sparsity_host for every pass run and train anchor, x14_host for the trains and premise runs> |
| the smoke with both hosts, its gate and the kit's stop K1 (E196.md 6; KIT.md 4) | <the gate line> |
| T1 and T2: 24 processes each, 13 launches after the calibration launch, SFFS and FSSF alternating (E196.md 2 and 6) | <processes and launches per train; the anchors> |
| passes 0-5 and 6 if it fits, the written order for aifoundry3 (E196.md 6) | <passes run; the order: the plan marks against desk/order-e196-aifoundry3.txt> |
| the cut order (E196.md 6) | <M; DROP_ARMS or none> |
| the cap: 60 card-minutes; DEADLINE = first card command + 58 minutes or the last end - 2 minutes; the end-stop at the cap - 60 s | <DEADLINE and end-stop lines; whether either acted> |
| the stops (E196.md 9: the lab's 65 W and 70 C, stopwatch.py's, the block's, the hosts' budgets) | <none fired / which, when> |
| one sampler, `ettelem sample --every-ms 100` through E128's guard; no statistics reset | <the sampler's start line; dmcmd_audit GO> |
| every unchanged-host launch record "readback": "none"; ops = iters x minions (E196.md 7) | <counts from run/runs.jsonl> |
| <every other registered item the session touched> | <...> |

## Departures, dated

- <date, time PST>: <each departure from E196.md or KIT.md, what it touches, and the dated amendment or note that allowed it; "none" if none>
- the day's post: none, by the owner's standing waiver ("don't worry about discord post, just use the machines, nobody is using them", Sun
  15 Nov 2026 10:22:36 PST), as E196.md 12 registers it.
- the desk: aifoundry2; the interpreter: `/usr/bin/python3` 3.12.3 at the desk; the box's `python3` <version, from build/BUILD-E196.txt's
  PYTHON line> ran the port and its stops on aifoundry3.

## Device commands sent

READs only: the session's opening and closing `ettelem config` and the one `ettelem sample --every-ms 100`, all through E128's guard
(dmcmd_audit GO, 11 send sites, every one a READ: KIT.md section 6); both hosts opened the ops node only (`createPcieDeviceLayer(true,
false)`); `et-who --check` sends no device command. No set, no reset, no statistics reset, no firmware query, no PMIC command.

## Files

| path | what |
|---|---|
| `session/` | the wrapper's files: session.log, the first card command's time, et-who's holder count at the start, hashes.txt (both hosts, both kernels, the sampler), the pins and the preflight's output, the port's output, MANIFEST.sha256 (the box's manifest), session.rc |
| `run/` | the port's OUT as the box wrote it: session.log, config-start.json, config-end.json, runs.jsonl, train.jsonl, checks.jsonl, marks.jsonl, stderr.txt (the hosts'), sampler.err, stopwatch.err, stops.err, gen_check.json, gen/ (arms.json and the tiles the session generated), STOP (when one was written), SESSION_DONE, and telemetry.jsonl.gz (gzip, no name, mtime 0; its unpacked bytes are the box's: MANIFEST.sha256) |
| `facts-e196.json` | the collector's facts (no reduced price) |
| `SHA256SUMS` | every collected file, paths beside it |

## Re-make it

From the top of the repository, nothing here opens a device; set D to this directory and R to an empty folder outside the repository,
then run the rest as they stand:

    D=docs/reports/data/<day>-e196-zeroshare-aifoundry3; R=<an empty folder outside the repository>
    (cd "$D" && shasum -a 256 -c SHA256SUMS)
    mkdir -p "$R/run/gen" && cp "$D"/run/runs.jsonl "$D"/run/train.jsonl "$D"/run/checks.jsonl "$D"/run/marks.jsonl "$R/run/" && cp "$D/run/gen/arms.json" "$R/run/gen/"
    [ -f "$D/run/STOP" ] && cp "$D/run/STOP" "$R/run/"
    gzip -dc "$D/run/telemetry.jsonl.gz" > "$R/run/telemetry.jsonl"
    for p in runs.jsonl train.jsonl checks.jsonl marks.jsonl telemetry.jsonl; do grep -q "$(shasum -a 256 "$R/run/$p" | cut -d' ' -f1)  ./run/$p" "$D/session/MANIFEST.sha256" && echo "run/$p: the box's bytes" || echo "run/$p: NOT the box's bytes"; done
    cmp "$D/run/gen/arms.json" tools/claims-v3/e196/proposal/src/arms.json && echo "arms.json: the registered table"
    /usr/bin/python3 -I -B tools/claims-v3/e196/reduce_e196.py "$R/run" --readback-none-ok --json "$R/x14-e196.json"
    /usr/bin/python3 -I -B tools/claims-v3/e196/check_e196.py "$R/run" "$R/x14-e196.json" --out "$R/checks-e196.json"

The reduction is `reduce_e196.py` at its registered sha256 (`c58c6690...`), run as E196.md section 7 writes it; step 13 ran exactly these
lines and committed their outputs with the records (no score).
```

---

## The gate stop's record (a session with no train and no pass block)

`docs/reports/gate-stops/<day>-e196-zeroshare-T<T0>-aifoundry3/README.md`: E196.md 11's "no session: no data" (a gate before the
sampler, the opening configuration read, the smoke's heater check or its gate, the smoke's lock), never reduced, never under
`docs/reports/data/`.

```
# E196, <day>, aifoundry3 card 0: GATE-STOPPED at <the gate> (T0 <T0>), no train and no pass block: no data

*<the day>, PST. E196 (the registration and the kit as above) on the owner's go of <...>. The session <opened no device ("no device opened")
| opened the card (the opening configuration read<, the sampler, the smoke>)> and stopped at <the gate>; nothing was set on the card.*

| what | value |
|---|---|
| the wrapper's GATE-STOP or refusal line | <session/session.log> |
| the port's gate line | <run/session.log, if the port ran> |
| card-minutes from the first card command | <facts: card_minutes_first_command_to_session_end, or none> |
| the smoke gate's problems | <facts: smoke_gate, or "the smoke did not run"> |
| device commands sent | <READs only: the configuration read, the sampler; or none> |

When E196 may be tried again: CARD-LANE-BRIEF.md section 3 (no device opened: once more the same day after the look reads FREE; a gate
after the card opened: not the same day).
```

SPDX-License-Identifier: Apache-2.0
