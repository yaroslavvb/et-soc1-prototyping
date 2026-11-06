# E181: M11's session 2 on aifoundry3, its first scored session - the start gate passed, five holds complete, every stop clear; one session, so nothing enters M11 (HM-E144 REPEATS, HM-CAL NOT RESOLVED, HM-CAL-I8 BETTER as a candidate, FL5(c) PASS)

*On the kinds page, [section 11, what is still open](https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers#11-what-is-still-open):
**items 9 and 8, heat over minutes and the heat path between sessions**. E181 is M11's session 2 (H_E, Z, L1, S, L2), as
[`REGISTRATION.md`](../../../../tools/claims-v3/m11/REGISTRATION.md) section 13 and its dated amendments A1-A9 register it and as
[`e181/README.md`](../../../../tools/claims-v3/e181/README.md) with its [dated note 1](../../../../tools/claims-v3/e181/README.md.dated-note-1.md)
kits it. Session 1 (E176, Thu 5 Nov 2026) was refused at its start gate and scored nothing, so this is M11's first scored session: **k = 1,
and by REGISTRATION.md section 6 nothing enters M11**. Every reading below is reported, labelled "one session", as a candidate for the next
session.*

*Fri 6 Nov 2026 (week 45), the card day Q149, aifoundry3 card 0 at 600 MHz pinned (TDP 0 W, 65 °C, max_power, 600 MHz, 523 mV read at the
session's start and end, nothing set). Registered before any E181 datum, one ancestry chain: M11's registration `3c31a91d` (Thu 07:41:57
PST), A1 `f49b7ddd` (08:44:59), A2 `d3d97fe2` (10:07:42), A3 `ed24bc6e` (11:07:48), A4 `0b554d25` (12:16:24), A5 `9b084c66` (13:46:11), A6
`95c75047` (23:11:50), the footing law `c14e5f35` (22:46:56), A7 `65a93fbb` (Fri 00:28:50), A8 `80b92990` (01:40:25), E181's kit `33cdccf6`
(02:20:39), A9 `cd5bed77` (03:22:30), and the kit's dated note 1 with M11's scorer v4 `dc35a540` (03:54:55). The readiness critic read E181
READY at about 04:18 PST. The owner's go for the card day came at about 09:20 PST, with the lab boxes' fresh network approvals. The window,
recorded by step 2 at 09:33:05: no session starts after 15:30 PST and every run ends by 17:00 PST. The run followed the kit's dated note 1
runbook, never README.md's v1 steps 3, 11 or 22. The box's tree was synced at `ddf09718` (09:45:13 PST: the box list's 30 entries OK, the
device-command preflight GO with 38 send sites and 0 disallowed, the runner's tile list with no problem), step 9 read the config through E128's
guard (TDP 0 W, 65 °C, 600 MHz) with et-who clean, and step 10's dry job ended rc 0 (09:45:32-09:46:01). The day's one `#community-lab` post
(message 1568318213618540726) named aifoundry3 from 09:36:40 PST ("using aifoundry3 for 2 h, until ~11:36 PST") and was rewritten at E181's
end, 11:06:55 PST, to the next run's clause ("using aifoundry3 for 1.5 h, until ~12:36 PST"), every other word kept.*

## The answer

Blind: every registration and amendment commit (the registration and A1-A9) precedes the measured pass's first launch record (09:55:33.020
PST), checked by the scorer by git and the launch records' times (`scored-m11.json` › `sessions` › `S2:p18120` › `precedence`).

| what | reading | line or rule | verdict |
|---|---|---|---|
| **A6-1, the floor F0** | **50.303 °C**, the 34-sensor mean over the smoke's first 3 s (30 samples; firmware 49 °C, board 23.20 W) | at most 53.9 °C, before the smoke's first launch | the smoke runs |
| **G0-A6 with A8-4, the start gate** | R0's room **50.817 °C** (firmware 50.0 °C); the residue, room less F0, **0.513 °C**; less A8's frozen 0.414 °C, **+0.099 °C** | room at most 53.9 °C, and residue less 0.414 °C at most 0.50 °C | **PASSED**; the room is under 51.5 °C, so H_E ran the **cool pattern** (E144's H_H: 3.20 s every 7.56 s) |
| **the five holds** (each 600 s, complete by E166's X1, scored) | the chain's rise P and the measured rise R, in °C, and **e = R − P**: H_E 14.127 / 14.088 / **−0.039**; Z 0.705 / 1.050 / **+0.345**; L1 9.485 / 9.738 / **+0.253**; S 3.471 / 3.463 / **−0.008**; L2 8.242 / 8.738 / **+0.496** | REGISTRATION.md section 1 (Q138(t)'s frozen chain, open loop on the measured board, anchored over each rest's last 120 s) | rms 0.293 °C over the five; 0.322 °C over the three large rises |
| **HM-LG** at df (1, 3) | F_slope 0.272 and F_level 2.082, against F(1, 3)'s point 10.128; the null F 1.833 against 9.552 | section 3 | **NOT SEPARATED** (k 1). The session's two-term fit: a +0.300 °C [−0.362, +0.963], g −0.0126 [−0.0896, +0.0644]; the level alone rms 0.206 °C, the gain alone 0.256 °C |
| **HM-E144** | \|e(H_E)\| / R = 0.039 / 14.088 = **0.28%** | at most 1.5% (RK3-c) | **REPEATS** |
| **HM-HE** | e(H_E) inside the 95% prediction interval of the two-term fit on the other four holds (t at 2 df, 4.303) | section 3, reported | does not depart |
| **HM-CAL (A2)**, the pair H_E and Z read on L1, S and L2 | the pair's line a +0.365 °C, g −0.0286; RMS_c **0.280 °C** [0.159, 1.043] against RMS_u **0.322 °C**; **D −0.042 °C** | BETTER at D ≤ −τ, τ = 0.0884 / √3 = 0.051 °C | **NOT RESOLVED**. Beside it: the floor the premise implies 0.111 °C; the ×1.032 arm 0.154 °C over the same holds; A2-4's reported arms, the pair's level alone 0.226, the pair's gain alone 0.332 and H_E's gain alone 0.340 °C |
| **HM-CAL-I8 (A4)**, the int8 pair L1 and S read on L2 | the pair's line a −0.159 °C, g +0.0434 (span 6.014 °C, L2's w 0.793); e_c(L2) **+0.297 °C** against e(L2) **+0.496 °C**; **D_I8 −0.199 °C** | BETTER at D ≤ −τ, τ = 0.0884 °C with one later hold | **BETTER**, and by A4-3 **nothing enters: one session (E5 needs two)**, so it is a candidate. E4′: X² 39.72 against χ²'s 7.81 at 3 df (the chain misses the int8 holds). Beside it: A2's line on L2 alone 0.367 °C; the ×1.032 arm on L2 0.232 °C; the floor 0.114 °C |
| **A5's agreement readings**, HM-CAL-AG and HM-I8-AG | the session's lines (H_E-Z: a +0.365 °C, g −0.0286; L1-S: a −0.159 °C, g +0.0434) | two or more read sessions | **NOT SCORED** (k 1) |
| **what M11 carries** | A1-4's path as the scorer prints it: "nothing: NOT SEPARATED", with the ×1.032 arm "retired"; A2-3: "nothing from A2: NOT RESOLVED"; A4-3: "nothing from A4: one session (a candidate)" | section 6's one-session rule; A1-4, A2-3, A4-3 and A5-3 unchanged | **nothing: one session** (the readings are a candidate for the next session) |
| **FL5(c)**, the footing law's first blind check (A6-5 with A7-1), reported | the rests after the holds (R1-R5, rule F, 6,962 samples): **0.3231 W/°C** per whole firmware degree at 52-60 °C against FL1's **0.3166** by the same estimator and weights, **+0.0065** | within ±0.02 W/°C, never a gate | **PASS**. Beside it, on the 34 codes in E97's 0.5 °C bins against E97's law: 0.3230 against 0.3248, −0.0018, PASS; the degrees 52-58 alone: 0.3197 against 0.3111, +0.0086, PASS |
| **A9's arm**, the chain over the smoke and the measured pass, reported (A9): never a verdict, an entry or what M11 carries | Δe(H_E) **+0.140 °C** (A9-5 expected near +0.15 °C); Z, L1, S and L2 0.000 °C; the gap between the passes 2.517 s; every grid point inside the measured pass the registered reading's own, R the registered R | A9-1 to A9-4 | read on the arm: HM-E144 REPEATS (e_2p +0.101 °C, 0.72%); HM-HE does not depart; HM-CAL BETTER (D −0.077 °C, RMS_c 0.245 against RMS_u 0.322 °C). **The registered reading decides (A9-3): HM-CAL stays NOT RESOLVED** |
| **A6-5, the host's own sensors**, reported | the NVMe composite 35.85 → 36.85 °C (whole kelvins), the coretemp 2-9 mean 30.64 → 31.86 °C, at step 12's windows (09:47:02-09:49:02 and 11:04:25-11:06:26 PST) | never a gate | |
| **the check of C** | `CCHECK-DONE … 5757 launches, PASS 5757, ROUNDING 0, UNMODELLED 0, FAIL 0, all_pass True` (fp32 1,920, int8 3,837); `COUNT-OK p18120: 5700 checked launches in 407 processes`; `COUNT-OK p18101: 57 checked launches in 7 processes` | every launch the marks record was checked for C (no registered rule reads a C FAIL for M11's holds) | 5,757 of 5,757 computed correctly (all_pass True) |

Sources: [`scored-m11.json`](scored-m11.json) and [`scored-m11.md`](scored-m11.md) (M11's scorer v4, run by step 22 v2 after every gate),
[`scored-m11-lines.jsonl`](scored-m11-lines.jsonl) (the staged lines, stages 1-6), the measured pass's
[`aifoundry3/e181/p18120/marks.jsonl`](aifoundry3/e181/p18120/marks.jsonl) (kinds `room`, `start_gate`, `hold`), the smoke's
[`aifoundry3/e181-smoke/p18101/marks.jsonl`](aifoundry3/e181-smoke/p18101/marks.jsonl) (kind `floor`), [`ccheck/ccheck-all.json`](ccheck/ccheck-all.json)
and [`ccheck/ccheck.txt`](ccheck/ccheck.txt), [`logs/host-start.out`](logs/host-start.out) and [`logs/host-end.out`](logs/host-end.out).

## The readings, labelled

Everything in this table is measured on the card in this session, except the rows marked **post hoc**, which were read afterwards and decide
nothing.

| what | reading | source |
|---|---|---|
| card-minutes | **74.9** of a 76 cap (4,560 s from T0): config reads at 09:49:14 and 11:04:07 PST; session start (T0) 09:49:14, the smoke 09:49:15-09:50:27, the measured pass 09:50:29-11:04:07 (its deadline T0 + 4,500 s, 11:04:14) | `logs/config-session-start.json.time`, `logs/config-session-end.json.time`, `logs/session.log` |
| the timeline of pass 18120 | R0 09:50:32-09:55:32 (300 s); H_E 09:55:33-10:05:33 (80 launches); R1 6 min; Z 10:11:33-10:21:33 (84); R2 2 min; L1 10:23:33-10:33:33 (81); R3 6 min; S 10:39:33-10:49:33 (81); R4 2 min; L2 10:51:33-11:01:33 (81); R5 150 s, to 11:04:03. Each hold ended on time; none was gated or stopped | `aifoundry3/e181/p18120/marks.jsonl`, `run.log` |
| the five stop tests (the smoke) | the gate line at 1 °C: 0 launches; the hold die and hold board lines: the holds ended with 0 launches; the in-launch board line at 27.75 W ended the launch in flight (board read 49.54 W); the session line at 1 °C ended the block with exit 6 (die 51 °C, 34-sensor mean 52.12 °C, board 23.78 W) | `logs/smoke-gate.json` (GO, no problems); `aifoundry3/e181-smoke/p18101/marks.jsonl` (kind `stoptest`, all_pass true) |
| peaks, pass 18120 | H_E: board 56.09 W, firmware 66 °C, 34-sensor mean 67.26 °C at a 50.82 °C room (the plan's in-launch peak at a 51.2 °C room: 68.13 °C on A1-2's exact grid, 67.79 °C on the 0.2 s grid); L1 36.82 W, 61 / 62.21 °C; L2 36.91 W, 62 / 62.45 °C; S 29.21 W, 55 / 55.62 °C; Z 26.28 W, 52 / 53.09 °C. The stops: no launch at a firmware reading of 70 °C or more, a hold ends at 72 °C or 65 W, the pass ends at 74 °C; none was reached (the closest, 4.7 °C under the hold line) | `aifoundry3/e181/p18120/telemetry.jsonl.gz` |
| peaks, the smoke | board 50.43 W, firmware 54 °C, 34-sensor mean 54.97 °C | `aifoundry3/e181-smoke/p18101/telemetry.jsonl.gz` |
| clock and statistics | 600 MHz in 44,879 of 44,879 samples (712 + 44,167); `since_reset_ms` −1 in every sample (no statistics reset); the service processor's running board maximum 68.9 W, unchanged (set before today) | the two `telemetry.jsonl.gz` |
| config at both ends | TDP 0 W, threshold 65 °C, max_power, 600 MHz, 523 mV at the session's start and end | `logs/config-session-start.json`, `logs/config-session-end.json` |
| the room's drift over R0 | −0.815 °C per 10 min (the 34-sensor mean's least-squares slope over R0's last 240 s: the die still cooling from the smoke) | `scored-m11.json` › `sessions` › `S2:p18120` › `room_drift_over_R0_C_per_10min` |
| the residue against A8's prediction, **post hoc** | measured 0.513 °C against A8-1's frozen 0.414 °C (miss +0.099 °C) and A8-2's expectation of about 0.33 °C (sd 0.13; this reads +1.4 sd). Under A6-2's own second clause (residue at most 0.50 °C) the gate would have refused this settled card by 0.013 °C; A8-4, registered before any E181 datum, passed it with 0.40 °C to spare | `aifoundry3/e181/p18120/marks.jsonl` (kind `start_gate`); `tools/claims-v3/m11/REGISTRATION.md.dated-note-A8.md` |
| the rest before the session | 981 minutes since E176's session end (Thu 5 Nov 17:27:38 PST), by step 11 v2's rest rule | step 11 v2's output (the lane's runbook log) |

## The shape of the misses (post hoc, one session, decides nothing)

The frozen chain read the duty-cycled fp32 hold H_E to 0.28% of its rise, as it read E144's H_H (+0.10%), while every int8 hold after it
and the zeros hold Z ran warmer than the chain (Z +0.345, L1 +0.253, L2 +0.496 °C; S −0.008 °C). That is the case REGISTRATION.md section 0.1
showed and A3 named (H_E read by the chain while the other holds miss), and the registered readings sort it the way A3 and A4 anticipated:
the fp32 pair's line (HM-CAL) does not carry to the later holds, and the int8 pair's line (HM-CAL-I8) reads L2 better. With one session, none
of this enters M11.

## Who checked it

The lane ran step 22 v2's gates in order, each passing: the files as committed (six lists); the collector v2 (both pass directories present,
the session-written files kept by the session's last block, 0 set aside); the session's own gates (`GATES-PASSED: the smoke's floor mark True;
p18120's start gate True`); the session log's own stops (none before the measured pass); the check of C finished (`ccdone: 1 of 1 C checks
finished`); the launch gate (`cclaunch: 2 pass(es) with a C log read against their marks; 0 problem(s): OK`); the login scrub in every
directory; the desk-path gate; no scored file before the score; then M11's scorer v4 (`score rc=0`) and the desk-path gate on its files. No
data verifier has read this directory yet: the card day's verifier and fix pass for E181 follow its data commit.

## Privacy and the public-text scan (before the commit)

- **Logins.** E164's `scrub_etwho_e164.py --check` (unchanged; it rewrites nothing; `--owner` the box login of this repository's owner), run by
  step 22 v2's `rb/scrub_all_e181.py` in **every** directory of this one, with each `.gz` unpacked outside the repository: 8 directories and 4
  `.gz` files, all CLEAN. The session log's et-who readings say "No process holds an ET-SoC-1 device node or card lock". Other accounts' idle
  terminals on the box (idle logins do not block, by the owner's ruling of 1 November 2026) are named in no file.
- **The public-text scan** (`tools/timeline/sanitize_extracts.py`'s fixed list, plus the private-network, Mac-home and e-mail patterns) over
  every text file and the text inside every `.gz` of step 22's collection: 48 text files and 4 `.gz` files, 26,375 matches. 26,372 are the
  owner's own box home path and 2 the configs' tree key that names it, the reviewed class E166's, E171's and E176's committed data carry. The
  last one is the scan's private-network port pattern matching a telemetry counter value inside `aifoundry3/e181/p18120/telemetry.jsonl.gz`
  (the field `cmd_mismatch` reading 8792 in one sample, a command-mismatch count), not a network address: reviewed, a false positive, and
  the file is kept as collected. This README and `SHA256SUMS` were scanned on their own afterwards (0 matches). The lab's private name table is absent on the
  Intel, so names were checked against the fixed list only (a stated coverage limit).

## Files

All files of step 22 v2's collection and score are here as step 22 left them, plus this README and [`SHA256SUMS`](SHA256SUMS), which pins
every file but this README and itself.

| path | what |
|---|---|
| `aifoundry3/e181-smoke/p18101/` | the smoke as the box wrote it: `block.json`, `configs.json`, `marks.jsonl` (with A6-1's `floor` mark), `runs.jsonl`, `run.log`, `telemetry.jsonl.gz`, `c-log.jsonl`, the config reads at both ends, the `STOP` and `HOLDSTOP` files of its stop tests, the binary, code and generator hashes, `manifest.txt`, the sampler's files |
| `aifoundry3/e181/p18120/` | the measured pass: R0, the start gate and the five holds (`marks.jsonl`, `runs.jsonl`, `run.log`, `telemetry.jsonl.gz`, `c-log.jsonl`, `block.json`, the config reads, the hashes, the sampler's files) |
| `ccheck/` | the check of C: `ccheck-all.json`, `ccheck.txt` and the two passes' C logs as `.gz` (`c-log-p18101.jsonl.gz`, `c-log-p18120.jsonl.gz`; the collector's copies of each pass's `c-log.jsonl`, which E166's records moved here and which step 22 leaves in the pass directories too) |
| `logs/` | `session.log` (the real session only: step 10's V3_DRY session writes its own log, collected beside it as `session-dry.log`, 09:45 PST), `smoke-gate.json`, `dmcmd-preflight.txt` (the box's device-command audit, GO), the config reads with their times and stderr, `host-start.out` and `host-end.out` (step 12's windows), `session.out` |
| `scored-m11.json`, `scored-m11.md`, `scored-m11-lines.jsonl` | M11's scorer v4 output, written after every gate: the registered readings, A9's arm beside them, A6-5's host readings and FL5(c) |

## What it does to predicting power and heat

- **Heat over minutes, blind given the watts, on aifoundry3:** Q138(t)'s chain unscaled missed E181's five 10-minute holds by −0.04, +0.35,
  +0.25, −0.01 and +0.50 °C: **0.29 °C rms over the five and 0.32 °C over the three large rises**, against the 0.49 °C rms over nine large rises
  that was the largest open heat error. One session, so nothing enters M11 and no frozen figure changes.
- **What the next session tests:** HM-CAL-I8 read BETTER (the int8 pair's own line took L2's miss from +0.496 to +0.297 °C); HM-CAL did not
  resolve; HM-E144 repeated. These are candidates, and A9's arm's fate is owed before session 3's first datum (the readiness critic's fault 5):
  on the arm, HM-CAL reads BETTER where the registered reading reads NOT RESOLVED.
- **The leakage law's first blind check passes:** FL5(c) reads the rests' slope at 0.323 W/°C against FL1's 0.317 W/°C at the same degrees
  (+0.0065, within ±0.02).
- **The power side** is unchanged: no power figure is read or scored here.

SPDX-License-Identifier: Apache-2.0
