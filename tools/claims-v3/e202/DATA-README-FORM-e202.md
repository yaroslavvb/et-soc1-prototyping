# E202's data README: the form the card lane fills for the data commit (Q193, lane kit-e202; kitted, not run)

*Mon 16 Nov 2026 (week 47), PST, desk only, beside [KIT.md](KIT.md). E196's form ([../e196/DATA-README-FORM-e196.md](../e196/DATA-README-FORM-e196.md))
with E202's files and E202.md 7.1's data form. This is the form of `README.md` in `docs/reports/data/<day>-e202-mnist-int8-aifoundry3/`,
written by the card lane after step 11 (the collection) and before the data commit, for a session in which at least one burst ran, in the
lab's data-README form: **results first, then registered against happened, then departures, each dated**. It is a form, not a result:
every `<...>` is filled from the session's own files (`session-facts-e202.json`, `session/session.log`, `session/queue.json`, the
runbook's log), and every number carries its label. The README lies beside the data and is not in its `SHA256SUMS` (the collector made
that list over the collected files). A session that ran no burst has no data directory: step 11 collects it into a gate stop's record,
whose README has the shorter form at the end of this file. The scorer runs after the data commit (step 13): its words are not in this
README at the commit; the records lane adds them in a dated note beside it.* *fix-e202 (verify-e202's nit 10, finding 2 and note 12):
the REPORTED one-pass latency row, the runner's exit status with a crash, the ledger v3 note's REPORTED line, and a word for the reader of
S1T.*

**The rules for this file.** No number from the owner's private checkpoint of Wed 11 Nov 2026 or his A100 report, and no side-by-side with
the A100 (E202.md 11: it stays on his private pages). No lab user's login (the collector's scrub masked ours; write `<login>`). No
credential or access path. Times Pacific. The interpreter named. A check not run is NOT RUN.

---

```
# E202, <day>, aifoundry3 card 0 at 600 MHz as found: one pass over MNIST in int8: <RAN WHOLE (the smoke, the scored <scp|dram> pair
T Z Z T T Z Z T<, the dram pair REPORTED>) / STOPPED at <the stop> after <k> bursts / ...>

*<the day>, PST. E202, registered before any datum (<the registration's landed commit>; forecasts frozen in forecast-e202.json,
sha256 d1dc7679...), on the program commit (<landed commit>, workloads/mnistmlp), kitted (<the kit's landed commit>), verified
(<lane, verdict>) and readiness-checked (<lane, verdict>); run on the owner's go (<his words and their times, or their record>). The
lab's own network (784-1792-1792-1792-1792-10, int8), the trained and the random weight configurations (E202.md 2), every label and
checksum checked bit for bit by the host on the card. Nothing was set on the card.*

## Results (measured: the session's own records; the scorer's words follow after the data commit)

| what | value | label |
|---|---|---|
| card-minutes, the session's first card command to its close | <facts: card_minutes_first_command_to_close> (cap 35; no burst after 33); step 7's config read at <RB_OUT/e202-step7.txt>, reported apart | measured (the session's clock) |
| the smoke: T-scp, Z-scp, T-dram, Z-dram, ACC | <facts: smoke: core / logits / status of each>; the gate: <facts: smoke_gate> | measured (the host's own --out files) |
| the on-card test accuracy (ACC, the trained network on the 10,000-image test split) | <correct> of <scored> = <%> (it must equal the model's 98.49%: every label is checked against the model's expected file) | measured |
| the R rule, each arm from its own R = 1 smoke | <facts: R>; the registered rule's R where the host's timeout cap took a smaller one: <facts: R_registered_rule> (KIT.md 4, item 23) | measured (the cycle counter) and registered (the rule) |
| one pass alone (R = 1), each smoke process: kernel seconds | <smoke/<arm>/host-raw.json: hart0_cycles.max / 600 MHz, for T-scp, Z-scp, T-dram, Z-dram, ACC> (E202.md 5: about 34 ms forecast, REPORTED only, never scored) | measured (the cycle counter), REPORTED |
| bursts run, set aside, and each arm's end | <facts: bursts_ran>; <set_aside>; <any "the arm ... ends" line> | measured |
| how the session ended | <"session end"; queue.json stop: none / the stop's words>; runner.rc <0 the queue ran / 3 a gate stop / 1 a crash, its "CRASH: <type>: <message>" line and queue.json's crash quoted (fix-e202)> | measured |
| telemetry samples, and those at 600 MHz | <facts: telemetry_samples> / <samples_at_600_mhz>; off the clock: <facts: off_clock> | measured |
| board power, peak; minshire[0], peak | <facts: peak_board_w> W; <facts: peak_minshire0_c> C (stops 65 W, 70 C; band-top forecast peaks 54.9 W scp, 62.0 W dram) | measured |
| the opening and closing configuration reads | <config_start>; <config_end, or "not read: et-who did not read the card free"> | measured (READ) |
| per burst: kernel seconds (hart0_cycles.max / 600 MHz), wall seconds, J over idle and J with the card at rest a launch | <the table from bursts/*/energy.json and host-raw.json, per pass = per launch / R> | measured (the reducer, energy_reduce.py, unchanged) |

## The meter's absolute scale (stated before the data, E202.md 11)

**Every number here is against the card's own meter, whose absolute scale is one fixed gain for every board, never set beside an outside
meter** (E184's arm S, the test of the meter itself, is pending). The joules over idle and with the card at rest carry that gain; a later
calibration would move every one by the same factor.

## Registered against happened

| registered (E202.md, plan-e202.json, KIT.md) | happened |
|---|---|
| aifoundry3 card 0 at 600 MHz as found, nothing set; the start config TDP 0 W / 65 C / 600 MHz (KIT.md 4) | <the config reads; the clock in every sample> |
| after E201 and the 40-minute rest; step 7 after the rest (E202.md 3, 10) | <whether E201 ran first (it was paused on Mon 16 Nov 2026 by the owner's matmul focus: if it never ran, say so here and in the departures); the box's last session of ours before E202 and its end; step 7's and step 9's "rest:" lines from the runbook log> |
| the window from G = the booking: last start G + 1:30, last end G + 3:30 (E202.md 10) | <G; the window; the session's start and end inside it> |
| the smoke's five processes and its gate on core_status (E202.md 7.2, 8.2) | <the gate line; any logits-only failure, recorded> |
| the R rule per arm, R 96 unless the 6 s ceiling binds (E202.md 8.3) | <R per arm; where the host's timeout cap (KIT.md 4, item 23) took a smaller R than the registered rule's, both Rs and a departure line> |
| K = 4 each, T Z Z T T Z Z T; the dram pair K = 2 REPORTED when scp is scored (E202.md 8.4-8.5) | <the bursts in order, from queue.json> |
| each burst: the die gate (60 C, 10 minutes), 8 s at rest, one host process under timeout 10, 10 s at rest (E202.md 8.4) | <die starts; gate waits; any burst below 52 C, labelled> |
| the stops: 65 W, 70 C, the clock, a line older than 1 s; K1 (KIT.md 4) | <none fired / which, when> |
| one sampler, `ettelem sample --every-ms 100` through E128's guard; no statistics reset | <the sampler's start line; dmcmd_audit_v2 GO> |
| the cap: no burst after 33 card-minutes from the first card command, the session ended by 35 | <the last burst's start and the close against the first card command> |
| the post waived; the package counter not read (E202.md 10) | the owner's words of Sun 15 Nov 2026 10:22:36 PST; not read |
| <every other registered item the session touched> | <...> |

## Departures, dated

- <date, time PST>: <each departure from E202.md or KIT.md, what it touches, and the dated amendment or note that allowed it; "none" if none>
- ledger v3: in HEAD at step 2, and E202's v3 note with it (step 2's line "ledger v3 in HEAD yes, E202's v3 note in HEAD yes (V3NOTE
  CHECK PASS)"); its REPORTED readings come after the data commit from `v3note_e202.py --score` (S2T-v3; S1, S1T and S2 equal v2's by
  construction), beside the scorer's words, never a verdict.
- the desk: aifoundry2; the interpreter: `/usr/bin/python3` 3.12.3 at the desk (the collection, the reducer with numpy 1.26.4); the box's
  `python3` 3.12.3 ran the session (the runner uses its own modules only).

## Device commands sent

READs only: the session's opening and closing `ettelem config` and the one `ettelem sample --every-ms 100`, all through E128's guard
(dmcmd_audit_v2 GO, every send site a READ: KIT.md section 5), and k6's step 7 config read through the same guard; the mnistmlp host opened
the ops node only (`createPcieDeviceLayer(true, false)`; the runtime's creation aborts the submission queues of the card it enumerates, as
every lab host's does: harmless on a card held alone, et-who empty and card 0's lock held); `et-who` sends no device command. No set, no
reset, no statistics reset, no firmware write, no PMIC write.

## Files

| path | what |
|---|---|
| `smoke/<arm>/` | each smoke process: `host-raw.json` (the host's own --out file), `labels.bin` (the kernel's label lines, 64 B each), `smoke.json` (the runner's record and the R rule's inputs), `stdout.txt`, `host.err` |
| `bursts/<config>/b<k>/` | each burst (E202.md 7.1): `host-raw.json` (the host's own --out file), `host.json` (the adapter's), `burst.json` (the runner's marks: config, k, order index, R, set aside), `run.json`, `telemetry.jsonl.gz` (the session's samples over the burst), `stdout.txt`, `host.err`, `energy.json` and `energy.txt` (the reducer's output and its printed lines) |
| `session/` | `session.log`, `config-start.json`, `config-end.json`, `stop-path.json`, `etwho-before.txt`, `queue.json`, `telemetry.jsonl.gz` (the whole session), `runner.out`, `runner.rc`, `MANIFEST.sha256` (the box's), `sampler.err` |
| `session-facts-e202.json` | the collector's summary of the session's own files (measured) |
| `SHA256SUMS` | every file above but this README |

## Labels

Measured: the session's records. Registered: E202.md and its files. Desk check of code: the kit's tests. Nothing here is blind to the
forecasts' authors' earlier card results (E202.md's label), and the scorer's words are the frozen scorer's, after the data commit.

For the reader of the scores (verify-e202's note 12): E202-S1T's 10% (registered) weighs the card at rest, about 60% of J with the card
at rest at the forecast point, so a miss in J over idle moves S1T by about 0.4 of its size (E202.md 7.4's self-test B: J over idle 25%
high gives S1T e -0.087); S1 is the joules-over-idle test.
```

---

**The gate stop's form** (`docs/reports/gate-stops/<day>-e202-mnist-int8-T<T0>-aifoundry3/README.md`):

```
# E202, <day>, aifoundry3 card 0: a gate stop, no burst ran: <the runner's GATE-STOP or "refused, no device opened" line>

*<the day>, PST. E202 (<registration commit>; kit <commit>) on the owner's go (<his words>). No burst ran, so no datum exists and nothing
is scored (E202.md 7.2: no data, never a failed forecast). Card-minutes: <first card command to close, or 0 when no device was opened>.*

- what stopped it: <the line, and the files that show it: session.log, queue.json, smoke/*/host-raw.json if the smoke ran>; for a crash
  (fix-e202): its "CRASH: <type>: <message>" line, queue.json's crash and runner.rc (1), and step 11's words "a crash's record";
- the smoke, if it ran: <each arm's core / logits / status; the gate line>;
- device commands sent: <none (refused before any card command) / the opening config read, the sampler, the smoke's host processes>;
- the meter's absolute-scale caveat (above) applies to any watts quoted;
- what next: <tried again the same day (a launch that opened no device, once) / not the same day (the card opened) / a dated kit note and
  amendment before any burst datum (a kit defect; the UA = 0 fallback)>.
```

SPDX-License-Identifier: Apache-2.0
