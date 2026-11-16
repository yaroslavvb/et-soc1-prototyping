# E200's data README: the form the card lane fills for each sitting's data commit (Q192, lanes kit-e200 and fix-e200; kitted, not run)

*Mon 16 Nov 2026 (week 46), PST, desk only, beside [KIT.md](KIT.md), in E197's form (`tools/claims-v3/e197/DATA-README-FORM-e197.md`,
unchanged beside it). This is the form of `README.md` in `docs/reports/data/<day>-e200-regfile-sitting-<1|2>-aifoundry2/`, written by
the card lane after step 11 (the collection) and before the data commit, for a sitting in which a block of `trains.tsv` began, in the
lab's data-README form: **results first, then registered against happened, then departures, each dated**. It is a form, not a result:
every `<...>` is filled from the sitting's own files (`facts-e200-<n>.json`, `session/session.log`, `session/summary.txt`,
`session/first/`, the runbook's log), and every number carries its label. The README lies beside the data and is not in its `SHA256SUMS`
(the collector made that list over the collected files). A sitting that ended before any block began has no data directory: step 11
collects it into a gate stop's record, whose README has the shorter form at the end of this file.*

**The rules for this file.** No number of the sealed forecast and no score against it (E200.md 0: the model session scores it,
privately, after the data commit; the lab knows it only by its sha256, the freeze line registered with E200). No lab user's login (the
collector's scrub already masked them in the data; write `<login>` if one must be named). No number from a private page. Times Pacific.
The interpreter named. A check not run is NOT RUN. The reduced prices are not in the data commit: step 13 (`rb/s24_reduce_e200.sh`) runs
E200's registered reduction after it, and the records lane commits its outputs beside the data in a later commit, with this README's
"Reduced" section filled then by a dated note.

---

```
# E200 sitting <1|2>, <day>, aifoundry2 card 0 under its governor (800 MHz under load) as found: <one line of what happened: RAN WHOLE
(<4 of 4 blocks | block E>) / STOPPED at <the stop's reason> after <k> of <n> blocks / CUT by the deadline in block <X> / ENDED WITHOUT A
REGISTERED STOP (a crash: run_session.sh rc <n>), its reduction decided by a dated note>

*<the day>, PST. The model session's proposal X02 on a second card: E197's registered protocol (<E197's landed registration and kit
commits>) run on aifoundry2 card 0 as E200 (<E200's landed registration commit>, its departures W1 and C1-C3; forecast sealed by sha256,
contents sealed), kitted (<the kit's landed commit>), verified (<the verifier's lane and verdict>) and readiness-checked (<lane,
verdict>); run on the owner's standing go (E200.md 12: his words of Sun 15 Nov 2026 at 10:05:42, 10:22:36 and 17:21:16 PST, "Try
again", and 21:51:09 PST). Sitting <1: blocks A-D, the <full|short> plan | 2: block E, the ext plan>. Nothing was set on the card.*

## Results (measured: the session's own records; the reduced prices follow after the data commit)

| what | value | label |
|---|---|---|
| the sitting's card-minutes, first card command (step 7's: fwgate's read or the config read) to "session end" | <facts: card_minutes_first_command_to_session_end> (cap <50|40|35>) | measured (the session's clock) |
| train blocks begun and complete | <session.log: "train blocks started: ... complete: ..."> | measured |
| train processes recorded (of the plan's <400|302|266>) and launch records | <facts: train_processes_recorded>; <facts: launch_records> | measured |
| how the sitting ended | <session.log's "stop:" line, and whether it names the card; or "the trains ended without a registered stop"; wrapper.rc> | measured |
| the runner's smoke gate and the kit's smoke check (with the smoke's clock, C3) | <session.log's two lines> | measured |
| the clock live (C3, the kit's watch) | <summary: "the clock (C3, the kit's watch): train processes judged ...; at 800 MHz ...; OFF ...; not judged ...; the longest OFF run ..."> | measured |
| THE DIE GATE (57 C, E200.md 9) | <session.log: "the die gate, read <k> ... minshire[0] <c> C: OK"; the seconds it waited> | measured |
| the deadline (a train skipped or cut) | <"the deadline: ..." lines, or none> | measured |
| a device process that outlived its timeout's TERM (the kit's hang watch) | <a "HUNG:" line, or none> | measured |
| telemetry samples: at 800 MHz, at 600 MHz, at other clocks, without a clock | <facts: telemetry.samples_at_800_mhz> / <...samples_at_600_mhz> / <...samples_at_other_clocks> / <...samples_without_a_clock> of <...samples> | measured |
| board power, peak; die, peak (minshire[0]); the latch, peak (minshire[2]) | <facts> W; <facts> C; <facts> C | measured |
| the configuration at the start (step 7) and at the end (the wrapper) | <session/first/config.out: TDP 65 W / 65 C / 600 MHz, minion_mv>; <session.log's "the configuration at the sitting's end" line> | measured (READs) |
| the firmware identity (THE REBOOT GATE, E200.md 8) | <fwgate's look: CONTINUITY, or NEEDS-READ and its read: EQUAL, with session/first/fwgate-aifoundry2-c0-<time>.json> | measured (READ) |
| the sampler | the plain sampler, `ettelem sample --seconds <CAP_S + 600> --every-ms 100`, through E200's guard (build/ettelem-hpl/ettelem at 77a46171...) | registered (E197.md 4; the kit) |

**Reading the checker's rail row (when the reduction's dated note fills it).** E197's REPORTED row "rail voltage samples beyond +-3 mV of
the session median in the train's spans" reads high by design on this card: every train process's span includes its climb, run at the
600 MHz point's lower voltage, so the count is no rail fault and never a gate (KIT.md 7; fix-e200, verify-e200's F8).

## Registered against happened

| registered (E200.md, E197.md by reference, KIT.md) | happened |
|---|---|
| aifoundry2 card 0 under its governor as found, nothing set (E200.md 3): TDP 65 W, threshold 65 C, 600 MHz at rest at the start | <step 7's config read; the end read> |
| THE REBOOT GATE: the lab's fwgate (E200.md 8) | <look CONTINUITY / NEEDS-READ and the read's verdict; step 9's guard line "identity: ... ok"> |
| the 40-minute rest before the sitting's first card command (E200.md 11) | <step 7's "rest:" line from the runbook log, and the first card command's time> |
| the window: G = the booking, last start G+1:30, last end G+3:30 (E200.md 12) | <the booking's time, the window.env lines, the first card command and the sampler's stop inside them> |
| the plan (sitting 1: full unless the window cannot hold it; sitting 2: ext) | <the plan step 7 logged> |
| THE DIE GATE: minshire[0] at or below 57 C, up to 10 minutes, in the cap | <the die gate's lines> |
| W1: every launch at --window 320000000; E200's runner at 8774027b... | <the dry pass's LISTING SAME lines (W1's window); ref/run_trains.py's sha256> |
| C1, THE CLOCK RULE (the reduction's), C2 (nothing read before 2.0 s): applied after the data commit | <step 13's "e200" line, filled by the dated note> |
| C3: the smoke's clock; three train processes in a row off 800 MHz end the sitting | <the kit's smoke check line; the summary's clock line; a C3 stop or none> |
| the smoke and its gate (the runner's), the kit's smoke check | <the two lines> |
| the blocks, trains, processes and orientations in trains.tsv's order (E197.md 5) | <the dry pass's LISTING SAME lines; the processes recorded> |
| the cap: <50|40|35> card-minutes from the first card command; the runner's deadline at the first card command + the cap - 120 s; the end-stop at the cap - 30 s | <the session's CAP_S line; whether a train was skipped or cut (T15 may be: E200.md 10); whether the end-stop fired> |
| the stops (E197.md 9 with C3 in the kit's clock stop's place; aifoundry2's 85 W and 80 C lines, E200.md 9) | <none fired / which, when, and whether it names the card> |
| departure D1: `timeout 10`, never a KILL | <every device process under `timeout 10`; a HUNG line or none> |
| THE QUIET DESK FLAG from the look to the copy-back (E200.md 12) | <its raise and lower times, the P2 count before the look and at the launch> |
| the second sitting's condition (sitting 2 only): sitting 1 ran its smoke and a train block with no stop naming the card, 40 minutes before | <sitting 1's SITTING-RESULT line; step 7's rest line> |
| <every other registered item the sitting touched> | <...> |

## Departures, dated

- <date, time PST>: <each departure from E200.md or KIT.md, what it touches, and the dated amendment or note that allowed it; "none" if none>
- the day's post: waived by the owner (his words, Sun 15 Nov 2026 10:22:36 PST: "don't worry about discord post, just use the machines,
  nobody is using them"), unless his go names a post

## Device commands sent

READs only (dmcmd_audit_v2 GO, KIT.md 6): fwgate's one `DM_CMD_GET_MODULE_FIRMWARE_REVISIONS` query when its look read NEEDS-READ (a READ
by the owner's rulings, Sun 15 Nov 2026: "Firmware revisions query was a false positive. It should have never been forbidden. Reading
operations and firmware are always allowed." at 15:07:01 PST, and "Yeah, fix the corresponding guards. I don't want to modify firmware, but
commands which read firmware should be fine." at 15:09:49 PST; the audit table v2's id 14 line), or none; step 7's and the end's `ettelem
config` (five READs each); the die gate's `ettelem sample --seconds 1 --every-ms 200` reads and the session's one `ettelem sample --every-ms
100` (six READs a sample), all through E200's guard; the host opened the ops node only; `et-who --check` sends no device command. No set,
no reset, no statistics reset, no firmware change, no KILL to any process.

## Files

| path | what |
|---|---|
| `session/` | the wrapper's files: session.log, first-card-command.txt, harness.txt, preflight.txt, ref-patch.txt, diegate-<k>.jsonl and .err, run_session.out, watch.jsonl, watch.out, summary.txt, config-end.out and .err, MANIFEST.sha256 (the box's), wrapper.rc |
| `session/first/` | step 7's folder: the config read's config.out and config.err (and each call's config-<time>.*), et-who after it, and fwgate's read record with its raw answer when one was made |
| `ref/` | the four files the session ran: E197's run_session.sh, stopwatch.py and trains.tsv byte for byte; E200's runner run_trains.py (E197's lab runner with W1, 8774027b...) |
| `run/` | the reference session's own files: runs.jsonl, marks.jsonl, stderr.txt, session.log, sampler.err, stopwatch.err, STOP and SESSION_DONE when there, telemetry.jsonl.gz (gzip, no name, mtime 0; its unpacked bytes are the box's manifest's) |
| `facts-e200-<n>.json` | the collector's facts (no reduced price) |
| `SHA256SUMS` | every collected file, paths beside it |

## Re-make it

From the top of the repository, nothing here opens a device; set D to this directory and R to an empty folder outside the repository
(the first line), then run the rest as they stand (sitting 1's own reduction; after sitting 2, step 13 pools both sittings):

    D=docs/reports/data/<day>-e200-regfile-sitting-1-aifoundry2; R=<an empty folder outside the repository>
    (cd "$D" && shasum -a 256 -c SHA256SUMS)
    mkdir -p "$R/sitting-1" && cp "$D/run/runs.jsonl" "$D/run/marks.jsonl" "$R/sitting-1/" && gzip -dc "$D/run/telemetry.jsonl.gz" > "$R/sitting-1/telemetry.jsonl"
    if [ -f "$D/run/STOP" ]; then cp "$D/run/STOP" "$R/sitting-1/"; fi
    for p in runs.jsonl marks.jsonl telemetry.jsonl; do [ "$(awk -v p="./run/$p" '$2 == p {print $1}' "$D/session/MANIFEST.sha256")" = "$(shasum -a 256 "$R/sitting-1/$p" | cut -d' ' -f1)" ] && echo "run/$p: the box's bytes" || echo "run/$p: not the box's bytes"; done
    /usr/bin/python3 -I -B tools/claims-v3/e200/reduce_e200.py "$R/sitting-1" --out "$R/regfile-e200-s1.json"
    /usr/bin/python3 -I -B tools/claims-v3/e200/check_e200.py checks "$R/regfile-e200-s1.json" --out "$R/checks.json"

They check every entry of `SHA256SUMS`; unpack the telemetry and set it, `run/runs.jsonl` and `run/marks.jsonl` against the box's own
manifest (`session/MANIFEST.sha256`: every line must say "the box's bytes"); run E200's registered reduction (`reduce_e200.py`, sha256
10a44034..., unchanged, never `--prediction`: it loads E197's reducer by path and sha256 and applies C1 and C2); and read E197.md 8's rows
with the kit's checker, the clock row by C1 with its tallies. Step 13 (`rb/s24_reduce_e200.sh <1|2>`) does the same from a runbook
directory whose window names the day; the runbook desk test runs these lines as written here on a committed stand-in data directory and
gets step 13's `regfile-e200-s1.json` byte for byte (KIT.md, the runbook's desk test, case CR5).

## Labels

Measured: every number above, from this sitting's own files. Registered: the protocol (E197.md by reference), W1 and C1-C3, the caps, the
stops, the die gate, the reduction (E200.md). Desk checks of code: the kit's tests (KIT.md). Not blind to: E200.md 16's list. Interpreter:
<the desk's /usr/bin/python3 and version>.
```

## The gate stop's record: its README's form

A sitting that ended before any block of `trains.tsv` began (a `GATE-STOP:` line in its session log, no "train blocks started" with a
count above 0: a refusal, the card not free, THE DIE GATE, the smoke gate, the kit's smoke check with the smoke's clock, a holder or the
lock before block A) is "no train block: no data" (E200.md 13). Step 11 collects it the same way (COPY-BACK EXACT, THE BOX-TREE GATE, the
scrub, k6's desk-path gate) into `docs/reports/gate-stops/<day>-e200-regfile-sitting-<n>-T<T0>-aifoundry2/`, never under
`docs/reports/data/` (step 2 reads every `docs/reports/data/*e200*` path as an E200 datum, and a gate stop is none), and it is never
reduced. Its `README.md`, committed with it (new files only) after the public-text scan:

```
# E200 sitting <1|2>, <day>, aifoundry2 card 0: GATE-STOPPED at <the gate>, no block began - no train block, no data (E200.md 13)

*<the day>, PST. E200 (<the registration's and the kit's landed commits>), on the owner's standing go (E200.md 12). The session's own
gate line, verbatim: "<the GATE-STOP line from session/session.log>".*

| what | value | label |
|---|---|---|
| a device opened by the session | <no: the line says "no device opened by the session" / only step 7's and the die gate's reads / yes: the sampler ran> | measured |
| step 7's first card command (fwgate's read or the config read) | <its time, the firmware verdict, and TDP / threshold / MHz> | measured (READ) |
| THE DIE GATE | <its lines, or not reached> | measured (READ) |
| card-minutes, first card command to "session end" | <facts; when it reads null (the session stopped before it wrote session/first-card-command.txt), from RB_OUT/e200-<n>-first.txt's FIRST and the log's "session end"> | measured |
| the smoke (when it ran): the runner's gate, the kit's check with the smoke's clock | <the lines> | measured |

**What happens next** (CARD-LANE-BRIEF.md 3): <after a holder, the lock or a refusal: the sitting is tried again in a new RB_OUT with its
own step 7, once the gate has cleared (the rest rule skips a session that opened no device) / after a smoke failure or the die gate: not
the same day>. No departure, no amendment: no train datum of the sitting exists.
```

SPDX-License-Identifier: Apache-2.0
