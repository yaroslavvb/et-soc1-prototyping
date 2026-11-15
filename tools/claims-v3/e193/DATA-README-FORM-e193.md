# E193's data README: the form the card lane fills for each sitting's data commit (Q177, lane kit-e193; kitted, not run)

*Sat 14 Nov 2026 (week 46), PST, desk only, beside [KIT.md](KIT.md); fixed in place before the land (fix-e193, the same day: the direct
re-make commands, verify-e193's finding 7; a crash's title line, finding 5; the gate stop's record form below, finding 2). This is the
form of `README.md` in `docs/reports/data/<day>-e193-x04-clock-sitting-<a|b>-aifoundry3/`, written by the card lane after step 11 (the
collection) and before the data commit, for a sitting whose main run started, in the lab's data-README form (E183's and E189's):
**results first, then registered against happened, then departures, each dated**. It is a form, not a result: every `<...>` is filled
from the sitting's own files (`facts-e193-<a|b>.json`, `session/session.log`, the runbook's log), and every number carries its label.
The README lies beside the data and is not in its `SHA256SUMS` (the collector made that list over the collected files). A sitting that
ended at a gate has no data directory: step 11 collects it into a gate stop's record, whose README has the shorter form at the end of
this file.*

**The rules for this file.** No forecast number of the sealed forecasts and no score against them (E193.md 0: the model session scores
them, privately, after the data commit). No lab user's login (the collector's scrub already masked them in the data; write `<login>` if
one must be named). No number from a private page. Times Pacific. The interpreter named. A check not run is NOT RUN. The reduced prices
are not in the data commit: step 13 (`rb/s24_reduce_e193.sh`) runs the registered reducer after it, and the records lane commits its
outputs beside the data in a later commit, with this README's "Reduced" section filled then by a dated note.

---

```
# E193 sitting <A|B>, <day>, aifoundry3 card 0 at 600 MHz as found: <one line of what happened: RAN WHOLE / STOPPED at <reason> after <k>
of 9 passes / ENDED WITHOUT A REGISTERED STOP (a crash: <the runner's last line>) after <k> of 9 passes, its reduction decided by a dated
note>

*<the day>, PST. The model session's proposal X04 (request 1113-x04-clock revision 2), registered as E193 (<the registration's landed
commit>) with its two forecasts sealed by sha256 (d6ac4fb9... top-down, f7dc8210... from a gate-level simulation; contents sealed),
kitted (<the kit's landed commit>), verified (<the verifier's lane and verdict>) and readiness-checked (<lane, verdict>); run on the
owner's go of <date and time, his words or their record>. Sitting <A: blocks S, D, W, T | B: block C>. Nothing was set on the card.*

## Results (measured: the session's own records; the reduced prices follow after the data commit)

| what | value | label |
|---|---|---|
| the sitting's card-minutes, first card command to "session end" | <facts: card_minutes_first_command_to_session_end> (cap <60|50>) | measured (the session's clock) |
| device processes of the main run, by exit status | <facts: runner_calls.x04.exit_codes> | measured |
| passes run (pass 0 the registered warm-up, set aside by the reduction) | <0..8, from runner_calls.x04.passes_seen> | measured |
| launches, and how many were ok | <launches> / <launches_ok> | measured (the host's X04 lines) |
| how the main run ended | <runner_calls.x04.stop>; the session's own line ("main run end", "main run stopped" or "main run ended without a registered stop") and session.rc (0, 1 or 4) | measured |
| the smoke (10 device processes, --blocks S,D,W,T,C) and its gate | <SMOKE GO line from session.log> | measured |
| telemetry samples of the main run, and those not at 600 MHz | <telemetry_samples> / <telemetry_off_600> | measured |
| board power, peak; die, peak (minshire[0]) | <board_max_w> W; <die_max_c> C | measured |
| idle-down waits; card waits; short trains; incomplete launches | <idle_down_waits>; <card_waits>; <short_trains>; <incomplete> | measured |
| the start and closing config reads | <TDP / threshold / MHz at start; at the close> | measured (READ) |

## Registered against happened

| registered (E193.md, KIT.md) | happened |
|---|---|
| aifoundry3 card 0, 600 MHz as found, nothing set (E193.md 3) | <the config reads; the clock in every sample> |
| the 40-minute rest before the sitting (E193.md 6) | <step 9's "rest:" line from the runbook log> |
| the smoke with --blocks S,D,W,T,C and the kit's gate (E193.md 5) | <the gate line> |
| 9 passes, the seeded order (E193.md 5) | <passes run; the order as the runner drew it: runs.jsonl> |
| the cap: <60|50> card-minutes; the runner's deadline = first card command + cap - 120 s, never past the window's last end - 180 s | <deadline line; whether it fired> |
| the stops (E193.md 9) | <none fired / which, when> |
| the one sampler a runner call, through E128's guard; no statistics reset | <calls in session.log; dmcmd_audit GO> |
| per-sensor codes not recorded (E193.md 4) | not recorded |
| the post-launch credit barrier on the card's build | UNCONFIRMED (E193.md 14; the kit found no worker firmware source to read: KIT.md section 8) |
| <every other registered item the sitting touched> | <...> |

## Departures, dated

- <date, time PST>: <each departure from E193.md or KIT.md, what it touches, and the dated amendment or note that allowed it; "none" if none>
- the day's post: <made, with its id / waived by the owner: his words and their date>

## Device commands sent

READs only: the session's start and closing `ettelem config` and each runner call's `ettelem sample --every-ms 100`, all through E128's
guard (dmcmd_audit GO, KIT.md section 6); the host opened the ops node only; `et-who --check` sends no device command. No set, no reset,
no statistics reset, no firmware query.

## Files

| path | what |
|---|---|
| `session/` | session.log, the two config reads, the holder check's output, the first card command's time, the binaries' hashes, the harness and preflight outputs, the smoke's runner output and gate, the main runner's output, MANIFEST.sha256 (the box's), session.rc |
| `smoke/`, `x04/` | each runner call's run.log, events.jsonl, runs.jsonl, device-stdout.txt, device-stderr.txt (and any stderr-*.txt, STOPPED), telemetry.jsonl.gz (gzip, no name, mtime 0; its unpacked bytes are the box's manifest's) |
| `facts-e193-<a|b>.json` | the collector's facts (no reduced price) |
| `SHA256SUMS` | every collected file, paths beside it |

## Re-make it

From the top of the repository, nothing here opens a device; set D to this directory and R to an empty folder outside the repository
(the first line), then run the rest as they stand:

    D=docs/reports/data/<day>-e193-x04-clock-sitting-<a|b>-aifoundry3; R=<an empty folder outside the repository>
    (cd "$D" && shasum -a 256 -c SHA256SUMS)
    mkdir -p "$R/x04" && cp "$D/x04/runs.jsonl" "$R/x04/" && gzip -dc "$D/x04/telemetry.jsonl.gz" > "$R/x04/telemetry.jsonl"
    for p in runs.jsonl telemetry.jsonl; do [ "$(awk -v p="x04/$p" '$2 == p {print $1}' "$D/session/MANIFEST.sha256")" = "$(shasum -a 256 "$R/x04/$p" | cut -d' ' -f1)" ] && echo "x04/$p: the box's bytes" || echo "x04/$p: not the box's bytes"; done
    /usr/bin/python3 -I -B tools/claims-v3/e193/proposal/src/reduce_x04.py "$R/x04" --out "$R/x04.json"
    /usr/bin/python3 -I -B tools/claims-v3/e193/check_e193.py checks "$R/x04.json" "$R/x04" --out "$R/checks.json"

They check every entry of `SHA256SUMS`; unpack the main run's telemetry and set it and `x04/runs.jsonl` against the box's own manifest
(`session/MANIFEST.sha256`: both lines must say "the box's bytes"); run the registered reducer (`proposal/src/reduce_x04.py`, sha256
98bbc174..., unchanged, no `--pvt`, no `--keep-warmup`); and read E193.md 8's nine checks with the kit's checker. Step 13
(`rb/s24_reduce_e193.sh <A|B>`) does the same from a runbook directory whose window names the day of the sitting; the runbook desk test
runs these lines as written here on a committed stand-in data directory and gets step 13's `x04.json` byte for byte (KIT.md, the runbook's desk test, case CR5).

## Labels

Measured: every number above, from this sitting's own files. Registered: the arms, the protocol, the caps, the stops, the reduction
(E193.md). Desk checks of code: the kit's tests (KIT.md). Not blind to: E193.md 13's list. Interpreter: <the desk's /usr/bin/python3 and
version>.
```

## The gate stop's record: its README's form (fix-e193)

A sitting that ended at a gate (`GATE-STOP:` in its session log, no main run, session.rc 3) is "no sitting: no data" (E193.md 11). Step
11 collects it the same way (COPY-BACK EXACT, the scrub, the desk-path gate) into
`docs/reports/gate-stops/<day>-e193-x04-clock-sitting-<a|b>-T<T0>-aifoundry3/`, never under `docs/reports/data/` (step 2 reads every
`docs/reports/data/*e193*` path as an E193 datum, and a gate stop is none), and it is never reduced. Its `README.md`, committed with it
(new files only) after the public-text scan:

```
# E193 sitting <A|B>, <day>, aifoundry3 card 0: GATE-STOPPED at <the gate>, no main run - no sitting, no data (E193.md 11)

*<the day>, PST. E193 (<the registration's and the kit's landed commits>), on the owner's go of <date and time>. The session's own gate
line, verbatim: "<the GATE-STOP line from session/session.log>".*

| what | value | label |
|---|---|---|
| the gate, and whether a device was opened | <the line; "(no device opened)" or the start config read / the smoke> | measured (the session's log) |
| card-minutes, first card command to "session end" | <facts: card_minutes_first_command_to_session_end, or none> | measured |
| the smoke, if it ran: its gate line and its stop | <the SMOKE line; runner_calls.smoke.stop> | measured; never reduced |
| the config reads | <start; closing, if any> | measured (READ) |

**What follows (the card-lane brief, section 3):** the sitting is tried again with no amendment (no pass of it ran): after a gate before
the sampler, when the gate has cleared, with the 40-minute rest after any session of ours that opened the card (step 9 reads it); after
the smoke gate, not the same day (step 9 refuses). The day's post, or the owner's waiver: <...>. Interpreter: <...>.
```

SPDX-License-Identifier: Apache-2.0
