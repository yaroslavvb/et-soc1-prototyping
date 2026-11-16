# E202's ledger v3 note: ledger v3's forecast of E202's load, frozen before any E202 datum, REPORTED beside the registered v2 forecasts (Q193, fix-e202)

*Mon 16 Nov 2026 (week 47), PST, at the desk on aifoundry2: no card claimed, no device opened, no simulator run, nothing posted. Q193's
lane `fix-e202`, answering verify-e202's finding 3. A dated note beside [E202.md](E202.md), as its section 4.4 registered before any
datum: "If v3 lands before E202's card day, its forecast of the same load is frozen in a dated note beside this file **before any E202
datum** and scored REPORTED beside v2; the verdicts stay v2's." Ledger v3 landed at `50795847` (Mon 16 Nov 2026 06:26:27 PST; its freeze
line `tools/ledger/frozen-v3.json`, sha256 `4b43f510...`), after E202's registration was frozen (03:0x PST the same morning) and before
any E202 datum. **No E202 datum exists. Nothing here changes a registered forecast, band, rule, threshold or verdict:** E202's verdicts
are `score_e202.py`'s, on the v2 forecasts in `forecast-e202.json` (sha256 `d1dc7679...`).*

## The v3 forecast (forecast of code, frozen; REPORTED, never a verdict)

Per pass of the 60,000-image training split, R = 96, aifoundry3 card 0 at 600 MHz (`v3note-e202.json`, `v3note-e202.txt`):

| configuration | J over idle [band] | J with the card at rest, v3 [band] | the same, v2 as registered [band] | v3 / v2 - 1 |
|---|---|---|---|---|
| trained, scp (scored) | 0.4942 [0.4041, 0.6427] | **1.2365** [0.9339, 2.0000] | 1.2920 [0.9678, 1.9996] | -4.30% |
| random, scp (scored) | 0.5119 [0.4202, 0.6532] | **1.2548** [0.9504, 2.0116] | 1.3104 [0.9843, 2.0112] | -4.24% |
| trained, dram (the fallback) | 0.4977 [0.3998, 0.8098] | **1.2401** [0.9295, 2.1827] | 1.2956 [0.9634, 2.1823] | -4.29% |
| random, dram (the fallback) | 0.5154 [0.4159, 0.8204] | **1.2584** [0.9460, 2.1944] | 1.3140 [0.9799, 2.1940] | -4.23% |

Per image, with the card at rest (v3): trained scp 20.61 uJ, random scp 20.91 uJ; per multiply-add issued 1.848 and 1.875 pJ. The seconds
are v2's: 0.03126 s a pass [0.02361, 0.04776]; a launch of 96 passes 3.0005 s, and 3.0020 s on the wall with v3's 1.5 ms a launch.

## The route: ledger v3's own function for a v2 load

Ledger v3 (`tools/ledger/ledger_v3.py`, sha256 `339aa642...`) forecasts a ledger v2 load with `predict_v2load()`: v2's prices unchanged;
**rule 5** moves the forecast die from v2's 55 C [52, 60] to 50 C [48, 60] and adds 1.5 ms a launch to the card at rest; **rule 7** adds a
governed card's clock-state base, zero on aifoundry3 (pinned at 600 MHz; v3 has no governed-base entry for it); in v3's own words, "Rules
1-4 and 6 have nothing to change in a v2 load". E202's load is such a load: `forecast_e202.py` builds it for `ledger_v2.predict()` from
E202's counted events, with E202's kinds rule (the tensor-data price, E202.md 4.2) and the catalogue's class rows (4.3) added in memory to
the frozen v2 constants. [`v3note_e202.py`](v3note_e202.py) runs `predict_v2load`, all seven rules on, on exactly that load and those
constants (v3's module is handed E202's constants in place of the plain `frozen-v2.json` it would read; nothing is edited on disk), at
E202's own seconds (its cycle model, which v3 does not touch), with E202.md's own band construction: the point at the point seconds and
v3's die; the J-over-idle band over the fast and slow seconds; the J-with-rest band over the fast seconds at 48 C and the slow seconds at
60 C; the dram stage's band top from its dram-top arm.

## What v3 changes here, and what it does not (desk checks of code, printed by `--check`)

- **J over idle:** v2's exactly (difference 0 at the point; the band within forecast-e202.json's six digits, 1.5e-6 relative).
- **The seconds:** v2's (E202's cycle model; rules 1 and 2 are about the ledger's own seconds of scalar and memory code, which E202's
  forecast does not use).
- **The given-seconds readings** (E202.md 6, the scorer's `given()`): v2's exactly (difference 0 J at five bursts per configuration): at a
  measured die and wall time, rule 5's forecast die and launch overhead do not enter. So **v3's S1, S1T and S2 read as v2's verdicts**.
- **J with the card at rest at the frozen point** moves, about 4.2-4.3% down: the card at rest at 50 C instead of 55 C (aifoundry3's
  idle law, about 1.8 W lower there), and the 1.5 ms a launch. **S2T-v3** is the one v3 reading that can differ from v2's.
- **What v3 does not add here:** rule 3's lines past a 512 B L1 apply to a plain program built from the counter's per-mnemonic counts and
  an L1 model of its own accesses; v3 prices a v2 load without them, so E202's stack and table traffic stays at v2's L2 price (E202.md 11:
  its level is unknown). Any later reading of that term is post hoc.

## How it is scored (REPORTED, after the data commit only)

`/usr/bin/python3 -I -B tools/claims-v3/e202/v3note_e202.py --score DATA --out FILE`, beside step 13's frozen scorer: the bursts counted by
the scorer's own `read_burst()` and `smoke_gate()` (imported unchanged); **S2T-v3: |e| <= 15%** (E202-S2T's threshold), e = (the mean of
v3's point at each counted burst's R) / (the mean measured J with the card at rest a pass) - 1, for each configuration with at least two
good bursts; S1, S1T and S2 recomputed through v3's route and printed beside (equal to the scorer's: the runner's end-to-end desk test
checks it to 1e-5). REPORTED, never a verdict.

## Files and pins

| file | sha256 |
|---|---|
| `v3note_e202.py` (the route, `--check`, `--score`) | in `SHA256SUMS-e202-kit` |
| `v3note-e202.json` (every number above, and v3's point at each allowed R) | in `SHA256SUMS-e202-kit` |
| `v3note-e202.txt` | in `SHA256SUMS-e202-kit` |
| pinned inputs (refused if different) | `ledger_v3.py` `339aa642...`, `frozen-v3.json` `4b43f510...`, `forecast_e202.py` `89a7616d...`, `forecast-e202.json` `d1dc7679...`, `score_e202.py` `31ac8e90...` |

Step 2 (`rb/s03_desk_e202.sh`) reads ledger v3 in HEAD and then requires this note's four files in HEAD and `--check` PASS, else it stops
the day (16): no E202 datum before this note.

## Labels

Every number here is a **forecast of code**, frozen before any E202 datum, REPORTED; the comparisons with v2 are **desk checks of code**.
`/usr/bin/python3` 3.12.3 wrote the files (named in them). Not blind to the lab's earlier card results: rule 5's 50 C die and its 1.5 ms a
launch were read on the blind days (E189 on aifoundry3, E191 on aifoundry1 card 1), as ledger v3's own records label them (post hoc, input
conditions, not prices). Blind to every E202 datum (none exists).

SPDX-License-Identifier: Apache-2.0
