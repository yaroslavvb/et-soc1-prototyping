# E197's data README: the form the card lane fills for each sitting's data commit (Q185, lane kit-e197; kitted, not run)

*Sun 15 Nov 2026 (week 46), PST, desk only, beside [KIT.md](KIT.md), in E193's form (`tools/claims-v3/e193/DATA-README-FORM-e193.md`).
This is the form of `README.md` in `docs/reports/data/<day>-e197-regfile-sitting-<1|2>-aifoundry3/`, written by the card lane after
step 11 (the collection) and before the data commit, for a sitting in which a block of `trains.tsv` began, in the lab's data-README
form: **results first, then registered against happened, then departures, each dated**. It is a form, not a result: every `<...>` is
filled from the sitting's own files (`facts-e197-<n>.json`, `session/session.log`, `session/summary.txt`, the runbook's log), and every
number carries its label. The README lies beside the data and is not in its `SHA256SUMS` (the collector made that list over the
collected files). A sitting that ended at a gate (no block began) has no data directory: step 11 collects it into a gate stop's record,
whose README has the shorter form at the end of this file.*

**The rules for this file.** No number of the sealed forecast and no score against it (E197.md 0: the model session scores it,
privately, after the data commit; the lab knows it only as sha256 `e8e1746e...`). No lab user's login (the collector's scrub already
masked them in the data; write `<login>` if one must be named). No number from a private page. Times Pacific. The interpreter named. A
check not run is NOT RUN. The reduced prices are not in the data commit: step 13 (`rb/s24_reduce_e197.sh`) runs the registered reducer
after it, and the records lane commits its outputs beside the data in a later commit, with this README's "Reduced" section filled then
by a dated note.

---

```
# E197 sitting <1|2>, <day>, aifoundry3 card 0 at 600 MHz as found: <one line of what happened: RAN WHOLE (<4 of 4 blocks | block E>) /
STOPPED at <the stop's reason> after <k> of <n> blocks / CUT by the deadline in block <X> / ENDED WITHOUT A REGISTERED STOP (a crash:
run_session.sh rc <n>), its reduction decided by a dated note>

*<the day>, PST. The model session's proposal X02 (request 1113-x02-regfile revision 3), registered as E197 (<the registration's landed
commit>) with its forecast sealed by sha256 (e8e1746e...; contents sealed), kitted (<the kit's landed commit>), verified (<the verifier's
lane and verdict>) and readiness-checked (<lane, verdict>); run on the owner's go of <date and time, his words or their record>. Sitting
<1: blocks A-D, the <full|short> plan | 2: block E, the ext plan>. Nothing was set on the card.*

## Results (measured: the session's own records; the reduced prices follow after the data commit)

| what | value | label |
|---|---|---|
| the sitting's card-minutes, first card command (step 7's config read) to "session end" | <facts: card_minutes_first_command_to_session_end> (cap <50|40|35>) | measured (the session's clock) |
| train blocks begun and complete | <session.log: "train blocks started: ... complete: ..."> | measured |
| train processes recorded (of the plan's <400|302|266>) and launch records | <facts: train_processes_recorded>; <facts: launch_records> | measured |
| how the sitting ended | <session.log's "stop:" line, and whether it names the card; or "the trains ended without a registered stop"; wrapper.rc> | measured |
| the runner's smoke gate and the kit's smoke check | <session.log's two lines> | measured |
| the deadline (a train skipped or cut) | <"the deadline: ..." lines, or none> | measured |
| a device process that outlived its timeout's TERM (the kit's hang watch) | <a "HUNG:" line, or none> | measured |
| telemetry samples, and those not at 600 MHz | <facts: telemetry.samples> / <facts: telemetry.samples_off_600_mhz> | measured |
| board power, peak; die, peak (minshire[0]) | <facts: telemetry.board_w_peak> W; <facts: telemetry.die_c_peak> C | measured |
| the sampler | the plain sampler, `ettelem sample --seconds <CAP_S + 600> --every-ms 100`, through E128's guard | registered (E197.md 4) |

## Registered against happened

| registered (E197.md, KIT.md) | happened |
|---|---|
| aifoundry3 card 0, 600 MHz as found, nothing set (E197.md 3) | <step 7's config read (TDP 0 W / 65 C / 600 MHz); the clock in every sample> |
| the 40-minute rest before the sitting's first card command (E197.md 6) | <step 7's "rest:" line from the runbook log, and the first card command's time> |
| the first card command: step 7's config read (KIT.md 4) | <RB_OUT/e197-<n>-first.txt; session/first-card-command.txt> |
| the plan (sitting 1: full unless the window cannot hold it; sitting 2: ext) | <the plan step 7 logged> |
| the smoke and its gate (the runner's), the kit's smoke check | <the two lines> |
| the blocks, trains, processes and orientations in trains.tsv's order (E197.md 5) | <the dry pass's LISTING SAME line; the processes recorded> |
| the cap: <50|40|35> card-minutes from the first card command; the runner's deadline at the first card command + the cap - 120 s; the end-stop at the cap - 30 s | <the session's CAP_S line; whether a train was skipped or cut; whether the end-stop fired> |
| the stops (E197.md 9: the proposal's, the runner's, the kit's) | <none fired / which, when, and whether it names the card> |
| departure D1: `timeout 10`, never a KILL | <every device process under `timeout 10`; a HUNG line or none> |
| the second sitting's condition (sitting 2 only): sitting 1 ran its smoke and a train block with no stop naming the card, 40 minutes before | <sitting 1's SITTING-RESULT line; step 7's rest line> |
| <every other registered item the sitting touched> | <...> |

## Departures, dated

- <date, time PST>: <each departure from E197.md or KIT.md, what it touches, and the dated amendment or note that allowed it; "none" if none>
- the day's post: waived by the owner (his words, Sun 15 Nov 2026 10:22:36 PST: "don't worry about discord post, just use the machines,
  nobody is using them"), unless his go names a post

## Device commands sent

READs only: step 7's `ettelem config` (five READs) and the session's one `ettelem sample --every-ms 100` (six READs a sample), both
through E128's guard (dmcmd_audit GO, KIT.md 6); the host opened the ops node only; `et-who --check` sends no device command. No set, no
reset, no statistics reset, no firmware query, no KILL to any process.

## Files

| path | what |
|---|---|
| `session/` | the wrapper's files: session.log, first-card-command.txt, harness.txt, preflight.txt, run_session.out, watch.jsonl, watch.out, summary.txt, MANIFEST.sha256 (the box's), wrapper.rc |
| `ref/` | the four registered files the session ran, byte for byte (run_session.sh, stopwatch.py, trains.tsv; the lab's run_trains.py, D1) |
| `run/` | the reference session's own files: runs.jsonl, marks.jsonl, stderr.txt, session.log, sampler.err, stopwatch.err, STOP and SESSION_DONE when there, telemetry.jsonl.gz (gzip, no name, mtime 0; its unpacked bytes are the box's manifest's) |
| `facts-e197-<n>.json` | the collector's facts (no reduced price) |
| `SHA256SUMS` | every collected file, paths beside it |

## Re-make it

From the top of the repository, nothing here opens a device; set D to this directory and R to an empty folder outside the repository
(the first line), then run the rest as they stand (sitting 1's own reduction; after sitting 2, step 13 pools both sittings):

    D=docs/reports/data/<day>-e197-regfile-sitting-1-aifoundry3; R=<an empty folder outside the repository>
    (cd "$D" && shasum -a 256 -c SHA256SUMS)
    mkdir -p "$R/sitting-1" && cp "$D/run/runs.jsonl" "$D/run/marks.jsonl" "$R/sitting-1/" && gzip -dc "$D/run/telemetry.jsonl.gz" > "$R/sitting-1/telemetry.jsonl"
    if [ -f "$D/run/STOP" ]; then cp "$D/run/STOP" "$R/sitting-1/"; fi
    for p in runs.jsonl marks.jsonl telemetry.jsonl; do [ "$(awk -v p="./run/$p" '$2 == p {print $1}' "$D/session/MANIFEST.sha256")" = "$(shasum -a 256 "$R/sitting-1/$p" | cut -d' ' -f1)" ] && echo "run/$p: the box's bytes" || echo "run/$p: not the box's bytes"; done
    /usr/bin/python3 -I -B tools/claims-v3/e197/proposal/src/reduce_regfile.py "$R/sitting-1" --out "$R/regfile-e197-s1.json"
    /usr/bin/python3 -I -B tools/claims-v3/e197/check_e197.py checks "$R/regfile-e197-s1.json" --out "$R/checks.json"

They check every entry of `SHA256SUMS`; unpack the telemetry and set it, `run/runs.jsonl` and `run/marks.jsonl` against the box's own
manifest (`session/MANIFEST.sha256`: every line must say "the box's bytes"); run the registered reducer (`proposal/src/reduce_regfile.py`,
sha256 f325bd0e..., unchanged, never `--prediction`); and read E197.md 8's rows with the kit's checker. Step 13
(`rb/s24_reduce_e197.sh <1|2>`) does the same from a runbook directory whose window names the day; the runbook desk test runs these lines
as written here on a committed stand-in data directory and gets step 13's `regfile-e197-s1.json` byte for byte (KIT.md, the runbook's
desk test, case CR5).

## Labels

Measured: every number above, from this sitting's own files. Registered: the kinds, the trains, the protocol, the caps, the stops, the
reduction (E197.md). Desk checks of code: the kit's tests (KIT.md). Not blind to: E197.md 13's list. Interpreter: <the desk's
/usr/bin/python3 and version>.
```

## The gate stop's record: its README's form

A sitting that ended before any block of `trains.tsv` began (a `GATE-STOP:` line in its session log, no "train blocks started" with a
count above 0) is "no sitting: no data" (E197.md 11). Step 11 collects it the same way (COPY-BACK EXACT, the scrub, the desk-path gate)
into `docs/reports/gate-stops/<day>-e197-regfile-sitting-<n>-T<T0>-aifoundry3/`, never under `docs/reports/data/` (step 2 reads every
`docs/reports/data/*e197*` path as an E197 datum, and a gate stop is none), and it is never reduced. Its `README.md`, committed with it
(new files only) after the public-text scan:

```
# E197 sitting <1|2>, <day>, aifoundry3 card 0: GATE-STOPPED at <the gate>, no block began - no sitting, no data (E197.md 11)

*<the day>, PST. E197 (<the registration's and the kit's landed commits>), on the owner's go of <date and time>. The session's own gate
line, verbatim: "<the GATE-STOP line from session/session.log>".*

| what | value | label |
|---|---|---|
| a device opened by the session | <no: the line says "no device opened by the session" / yes: the sampler ran> | measured |
| step 7's config read (the sitting's first card command) | <its time, and TDP / threshold / MHz> | measured (READ) |
| card-minutes, first card command to "session end" | <facts; when it reads null (the session stopped at its holder check, before it wrote session/first-card-command.txt), from RB_OUT/e197-<n>-first.txt's FIRST and the log's "session end"> | measured |
| the smoke (when it ran): the runner's gate, the kit's check | <the lines> | measured |

**What happens next** (CARD-LANE-BRIEF.md 3): <after a holder, the lock or a refusal: the sitting is tried again in a new RB_OUT with its
own step 7, once the gate has cleared (the rest rule skips a session that opened no device) / after a smoke failure: not the same day>.
No departure, no amendment: no train datum of the sitting exists.
```

SPDX-License-Identifier: Apache-2.0
