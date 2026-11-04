# Dated note on E167's kit README `README.md` (Wed 4 Nov 2026, week 45, before any E167 data)

Written beside the README and not inside it, desk only, before any E167 data, claim or launch. [`README.md`](README.md) stays as committed
in `4f4e7620`. This note gives the box steps and the scoring as they now stand, after
[`E167.md.dated-note-2.md`](E167.md.dated-note-2.md): **X2**, the incomplete-window rule; RK3-c when G1Q does not run; the hottest-sensor
field is a latch; the 82 W admission is static; and the bounded collector.

## What changed on the card day

| README step | as committed | now |
|---|---|---|
| (new) **before the claim** | — | **The latch check** on aifoundry2, after E165's queue has ended: `python3 tools/claims-v3/e167/latch_check_e167.py --history ~/live/history/<UTC day>.jsonl` from `~/claude/et-soc1-prototyping` (a file read: the box's own 5 s history; no device command). **GO** (under 72 °C): go on. **NO-GO** (72 °C or more): do not claim or start E167 that day; every step's die line would fire at its first sample. **UNREADABLE** (a stale or missing history): go on; the smoke's first samples are then the check, and at 72 °C or more the queue ends there, before any hold |
| 2. check | `run_e167.sh check` (`frozen-e167.sha256` among its checks) | the same, plus `sha256sum -c tools/claims-v3/e167/frozen-e167-x2.sha256` (this fix pass's files) |
| 5. collect | `collect_e167.sh <data dir> <from> <to>` | **`collect_e167_bounded.sh <data dir> <from> <to>`**: the same copy, every rsync and ssh under `timeout`; exit 7 stops at once on a Tailscale check (section 9: append the line to the round's tailscale-needed file; the link goes to the owner) |
| 5. score | `score_e167.py <data dir> [--e165-anchors <file>] --json <data dir>/scored.json` | **`score_e167_x2.py <data dir> [--e165-anchors <file>] --json <data dir>/scored.json`**: `score_e167.py` unchanged inside it; the registered verdicts are its `verdicts` (X2), `score_e167.py`'s kept beside them as `verdicts_score_e167`. Run `sha256sum -c tools/claims-v3/e167/frozen-e167-x2.sha256` first |

Everything else in the README stands: the order (after E165, before E168), the 40-card-minute cap, the registered subset, the go gate,
the day's four gates, and the dry pass on the box.

## The scorer's self-test, again (before any E167 data)

`score_e167_x2.py --self-test` (`/usr/bin/python3` 3.9.6, numpy 1.26.4, about 2 minutes;
[`logs/selftest-e167-x2.txt`](logs/selftest-e167-x2.txt), `.json`) passes every check:
- `score_e167.py`'s own self-test, unchanged inside it, passes: E161's posthoc.json figures (G1Q +0.636 °C at 0.504 °C rms, G2Q −4.0 MHz),
  C3, the frozen arms byte for byte, the gate, RA1.2's edge 49.38 °C, E2, and reduce_e161's six registered verdicts on E161.
- On E161's committed data X2 reads both holds complete and changes no verdict.
- 16 session cases and 17 rule cases read as `E167.md.dated-note-2.md` registers them.

## Smaller points

- **The 82 W admission** is static, as E161's was. M8's 95% peaks are G1Q 53.33 W and G2Q 68.15 W, 13.85 W under 82 W at the closest.
  The README's "both admitted" is that desk check; no run-time admission code exists or is needed.
- **The hottest sensor at 70 °C** that the README's stops and E167.md quote for E161 is the shires' high latch, an upper bound (the
  amendment's § The hottest-sensor field is a latch).
- **Public text.** `queue_e167.py` line 55 carries E161's camera-phone health URL, a tailnet address that is already in 63 committed files.
  It is listed for Q141(r)'s public-text items and not repeated here. A real session reads it once a minute, as E161's did; the dry pass
  does not.
- **Device commands:** the three new scripts send none. `dmcmd_audit.py` reads GO with 0 send sites on `latch_check_e167.py`,
  `collect_e167_bounded.sh` and `score_e167_x2.py` ([`logs/dmcmd-audit-x2.txt`](logs/dmcmd-audit-x2.txt)). The kit's audit
  ([`logs/dmcmd-audit.txt`](logs/dmcmd-audit.txt), GO, 35 sites) is unchanged, because the queue's files are unchanged.
