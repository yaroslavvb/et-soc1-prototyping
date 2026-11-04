# E166 (Q141(h)): the heat replicate on aifoundry3 card 0 - the run kit, ready for the card day

*Desk preparation, Wed 4 Nov 2026 (week 45), on the Intel: no card, no device command, no ssh to a lab box, no Discord, no Modal, no
archive. The card session needs the owner's go and fresh approvals; nothing here has touched a card. It answers Q139's final critic
**rank 3** ("Heat over minutes from the bits, a second session per card"), as Q140's final critic left it (`card_half[3]`, `desk_next` 3
and 7); on the kinds page, [section 11](https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers#11-what-is-still-open) **items 9, 8
and 6**.*

## What is registered, and where

| commit | time (PST) | what |
|---|---|---|
| `2b450e66` | 09:16:36 | **the registration** [`E166.md`](E166.md), [`e166-registration.json`](e166-registration.json), and the slope rule's derivation [`slope_rule_e166.py`](slope_rule_e166.py) → [`slope_rule_e166.json`](slope_rule_e166.json), before any E166 data |
| `f830b9e2` | 09:31:08 | the scorer [`score_e166.py`](score_e166.py) and its self-test ([`logs/selftest-e166.txt`](logs/selftest-e166.txt), `.json`); the dated note [`E166.md.dated-note.md`](E166.md.dated-note.md) (the header's writing time) |
| this commit | | the run kit, its hash list, the device-command audit, the desk dry pass, the self-test again with the kit present ([`logs/selftest-e166-kit.txt`](logs/selftest-e166-kit.txt)), and this README |

It descends from Q140(e)'s frozen predictions and rules (registration `11174d20`, frozen `c9aaf179`, RA1 `a4fe976d`, `ac06c9be`) and from
E154 (`8c23853c`, `d037d82a`, corrections `d37c787e`). **Nothing new is predicted.** E166.md adds three rules Q140(e) left to E166: **G0**, the
start gate (R0's room at or under 53.0 °C, else no hold starts); **X1**, the incomplete-window rule (a heat-line truncation counts against;
any other truncation is excluded and never flips a decided outcome); **SL**, a decision on arm A's 300-600 s slope of K_OL beside G_A,
SEEN at **0.430 °C per 10 min** (a 5.0% false-positive rate under C10's seven-hold null) and NOT SEEN at **0.147** (a slow stage of the
frozen scenarios' size reads NOT SEEN at most 5% of the time).

## The scorer's self-test (before any E166 data)

`score_e166.py --self-test` (`/usr/bin/python3` 3.9.6, numpy 1.26.4, about 8 s): **every check passes.**
- On E154's committed pass the scorer's readers give back Q140(e)'s `posthoc.json` E154 figures **exactly**: the room 51.4097 °C; per hold
  the kernel duty, the measured rise, arm E's plateau error and checkpoints' rms for M8, M7, M6 and E153's S, arm A's error and its fraction
  (K_O +0.360 °C at 0.315 °C rms, arm A +0.536 °C, +4.64%); RK3-a 1 of 4 (FAIL), RK3-c FAIL, the session's 0.37 °C. And corrections.json
  C10's 300 s slopes, to the third decimal (K_S +0.513, K_O +0.418 °C per 10 min). The first process starts in its hold mark's own
  millisecond on all five holds, so R3's t0 and the post hoc pass's agree.
- On E166's planned records at 51.2 °C the readers give back the frozen plateaus (K_S 14.775, K_Q 6.103, K_L 3.530, K_O's window 11.156,
  K_OL 11.855 °C), and the slow-stage scenarios' G_A (within 0.001 °C of the frozen numbers, whose inputs are frozen at 4 decimals) and
  their slopes (exact): an extra stage reads SLOW STAGE SEEN and SLOPE SEEN, the gain scenario NOT SEEN and SLOPE NOT SEEN.
- 37 of 37 cases of the decision functions on their edges (RK3-a's I/F/X reading, RK3-c with and without exclusions, G_A, SL, the bands),
  the constants against the registration and the frozen predictions, and the runner's copy of K_OL's room table against
  `predictions-q140e.json` (equal).

## The run kit (E154's, ported)

| file | from E154's | what changed |
|---|---|---|
| [`run_e166.py`](run_e166.py) | `run_e154.py` | Q140(e)'s R5 design (no H_M, K_OL 25 min); G0 (exit 7 at R0's end); K_OL's room rule from the copied table; the smoke's four tiles; a dry-only room override (`E166_DRY_ROOM_C`) |
| [`block_e166.sh`](block_e166.sh) | `block_e154.sh` | the runner; exit 7 → block status "gate"; gen.sha256 without `int8.full`; `E166_DESK=1` (dry only) lists the box-only binaries |
| [`session_e166.sh`](session_e166.sh) | `session_e154.sh` | the day's gates from the launch, no defaults; 76 card-minutes from T0, no subset (else exit 8 before any device); pass numbers 16601 / 16620 |
| [`smoke_gate_e166.py`](smoke_gate_e166.py) | `smoke_gate_e154.py` | the four hold tiles (K_S, K_Q, K_L, K_OL); E154's checks unchanged |
| [`preflight_e166.sh`](preflight_e166.sh) | `preflight_e154.sh` | E166's session files in E154's list |
| [`frozen-e166.sha256`](frozen-e166.sha256) | `frozen-e154.sha256` | 30 files: E166's five card files, the reused chain, the four tiles, the C-check files, the audit, the host source and the three box binaries; the 25 it shares with E154's list are byte-identical to it |
| [`collect_e166.sh`](collect_e166.sh) | `collect_e154.sh` | E166's names; the data directory is an argument; the C check at `--jobs 2` |

**The stops** (Q138(t)'s, E154's): no launch at a firmware reading ≥ 70 °C; a hold ends at ≥ 72 °C (firmware or 34-sensor mean) or ≥ 65 W;
the pass ends at ≥ 74 °C; E97's guards. The runner refuses a looser line. The smoke tests all five stop paths on live samples on K_S's tile.

**Device commands** ([`dmcmd-audit.txt`](dmcmd-audit.txt), [`dmcmd-audit.md`](dmcmd-audit.md)): `dmcmd_audit.py` through
`preflight_e166.sh`, E144's table, E154's one reviewed exception (lib.sh:154, never called): **GO, 38 send sites, 0 disallowed, no WRITE
allowed** - every command a READ, the two PMIC voltage-register reads the owner's allowed reads of 2 November 2026, no statistics reset.
Against Q136(w)'s stock table with no exception ([`dmcmd-audit-bare.txt`](dmcmd-audit-bare.txt)) it reads NO-GO at exactly E154's two sites
(command 74, UNCLASSIFIED there; lib.sh:154).

**The desk dry pass** ([`logs/dry.txt`](logs/dry.txt), 09:39-09:40 PST, `V3_DRY=1 E166_DESK=1` in a scratch copy of the committed tree with
these files; E97's toy card; no device opened, no ssh; shims for GNU `date`, the box's hostname and `/usr/bin/python3`):
- the session script: the gates, the hash check (27 repo files as registered; the three box binaries listed as box-only), the preflight
  (GO), the smoke and its five stop tests, the smoke gate. Four stop tests pass; the in-launch board test cannot trip on a toy card whose
  board never rises, so the dry smoke exits 1 and the gate reads NO-GO, as E154's dry pass did on the box;
- the gates refuse before any device: no gates set (exit 8), T0 + 76 minutes past the end gate (exit 8), `E166_DESK` without `V3_DRY` (exit 2);
- the measured pass through the block: the full design, **73.0 minutes of plan**, K_S 137 launches at 4.37 s start to start, K_Q and K_L 85
  each, K_OL 1500 s with 211 launches, a `start_gate` mark (passed); at a 53.4 °C room the gate ends the pass with **exit 7** and block status
  "gate", no hold run; at 52.5 °C K_S runs the warm-room period, 4.97 s (121 launches).

## On the card day

**Card-minutes:** 73.0 of plan plus about 1.4 for the smoke and its stop tests (E154's), about **74.4 of the 76-minute envelope**, counted
from the session-start config read to the session-end one. **No subset.** **The order on aifoundry3: E166 first, on a rested card**, then E163
(E163's protocol heats to 59 °C before each launch, so it needs no rest; E166's room gate does). If the card was busy, at least about
40 minutes of rest first (E154's room read 51.41 °C 41 minutes after E153 ended).

**The box steps that wait for the approvals** (nothing else is left):
1. The day's one `#community-lab` post with this card's clause (`using aifoundry3 for 1.5 h, until ~HH:MM PST [doc](<…>)`; section 15's
   rules).
2. Sync the committed `tools/claims-v3/e166/` (and the unchanged reused files) into `aifoundry3:aifoundry/` from the pushed commit, never from
   a draft (E154's C14).
3. On the box: `sha256sum -c tools/claims-v3/e166/frozen-e166.sha256` (all 30, the three binaries included), `bash
   tools/claims-v3/e166/preflight_e166.sh` (GO), `et-who` (no other holder of card 0), `et-lab-manifest` (aifoundry3 runs a non-public
   thermal build since 7 Oct), `ettelem config` through the guard (TDP 0 W, threshold 65 °C, 600 MHz).
4. A dry pass on the box: `V3_DRY=1 E166_T0=$(date +%s) E166_LATEST_START=… E166_END_GATE=… bash tools/claims-v3/e166/session_e166.sh`
   (no `E166_DESK`: every file is checked).
5. The session, detached, in a script file run by `ssh aifoundry3 'bash -s'`, from `~/aifoundry`:
   `E166_T0=$(date +%s) E166_LATEST_START='YYYY-MM-DD HH:MM PST' E166_END_GATE='YYYY-MM-DD HH:MM PST' setsid nohup bash
   tools/claims-v3/e166/session_e166.sh > build/e166/session.out 2>&1 < /dev/null &`. The end gate must leave 76 minutes after T0.
6. After it, on the Intel: `bash tools/claims-v3/e166/collect_e166.sh docs/reports/data/<date>-e166-heat-replicate-aifoundry3` (the C check
   and the scorer), then the write-up.

## What this does to predicting power and heat

Nothing yet: no frozen prediction changes, and no out-of-sample error moves until E166 runs. E166 then scores, in a second session on this
card, the whole path from a tile's bits to its die over minutes (M8's S, Q138(t)'s chain, E97's idle law) on Q140(e)'s duty convention; the
chain's gain given the watts on large rises (whether E154's 3.1-4.6% deficit repeats, RK3-c); and whether heat keeps growing past
10 minutes (G_A and SL on the 25-minute K_OL), with a stated false-positive rate. Before: E154's 0.370 °C rms over four 10-minute plateaus
from the bits, 1 of 4 inside the critic's per-hold rule.
