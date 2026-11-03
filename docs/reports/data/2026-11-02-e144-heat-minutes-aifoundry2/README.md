# E144b data: heat over minutes on aifoundry2 under its own governor, Q138(t)'s frozen holds scored blind (Q138, Mon 2 Nov 2026)

*On the kinds page, [section 11, what is still open](https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers#11-what-is-still-open):
**item 9**, "A steady state for heat", and **item 8**, "The heat path drifts between sessions". This is E144's aifoundry2 arm. E144's
aifoundry3 arm is a separate lane.*

*Pre-registered in [`tools/claims-v3/e144b/E144b.md`](../../../../tools/claims-v3/e144b/E144b.md), committed as **`71645e59`** at
21:58:22 PST and pushed before the claim and before any device access. The frozen inputs are Q138(t)'s files at amendment A1's commit
**`c2f9920d`** ([`../2026-11-02-q138t-heat-model/`](../2026-11-02-q138t-heat-model/README.md)), which was on origin/main before the claim.
[`reduce_e144b.py`](../../../../tools/claims-v3/e144b/reduce_e144b.py) checked their sha256 before scoring. Nothing was refitted or tuned.*

*The session, on aifoundry2 card 0 only:*
- *Claimed at 22:00:25 PST by rewriting the day's one `#community-lab` post (message `1566837317765963987`).*
- *The detached queue had started at 21:58:33 and waited for the go. The go came over ssh at 22:00:53 (`GO`). At that moment the box's
  copies of the runner, the queue and the seven protocols matched origin/main byte for byte.*
- *Card runs 22:00:53–23:10:07 PST: **39.22 card-minutes of 40**.*
- *`ettelem config` read 65 W / 65 °C (low_power, 600 MHz, 519 mV) at every read, from the session-start read (22:00:53) to the
  session-end read (23:10:07). Nothing was set, and **every command sent was a READ**. The residency read was answered unsent 22 times
  and never sent.*
- *Released at 23:10:53 PST: this card's clause was dropped from the post and the aifoundry3 clause kept word for word.*
- *The lab's Tailscale approval lapsed from about 22:04 to 22:08 PST. The queue ran on, detached, and the protocol of section 9 was
  followed (one line in the orchestrator's `tailscale-needed.txt`, probes every 3 minutes). The first probe answered at 22:08:28.*

## Results first

**Six of the scorer's seven registered readings PASS blind, and so does this registration's clock rule (E144b-K1).** The seventh is G1's
frozen t63 rule. It has no FAIL band, and amendment A1.8 had said, before the run, that it would read NOT PASS even if the model is right.
It read NOT PASS. A1.8's closed-loop reference beside it reads PASS ([`results.json`](results.json) `score`, `K1`;
[`reduce.txt`](reduce.txt)).

| hold | rest die | arm | measured | frozen prediction | error | band | verdict | M6 as frozen, beside |
|---|---|---|---|---|---|---|---|---|
| **G1**: int8 −1s, 800 MHz, 15.0 min | 46.00 °C | (a) the chain on the measured board | rms **0.762 °C**; plateau error **+0.724** | — | — | PASS: rms ≤ 1.20, \|plateau\| ≤ 1.30 | **PASS** | rms 1.593; plateau +0.626 |
| | | (b) the planned power | plateau rise **12.923 °C** | 11.833 °C | **+1.090** | PASS within ±1.30 | **PASS** | 11.933: +0.990 |
| | | (c) rise per board W, last 300 s | **0.711** | [0.62, 0.74] | — | PASS inside | **PASS** | — |
| | | (c) t63 | 79.1 s | 49.6 s open loop (A1.8: 76.0 s closed) | ×1.59 (A1.8: ×1.04) | PASS within ×0.75–1.33 | NOT PASS, as A1.8 expected (A1.8: **PASS**) | — |
| | | **E144b-K1**: share at ≥ 790 MHz, last 300 s | **0.962** (mean 792.7 MHz) | "800 MHz, the governor never trips" | — | PASS ≥ 0.90 | **PASS** | — |
| **G2**: fp32 random, governed, 15.2 min | 46.00 °C | (a) the chain on the measured board | rms **0.369 °C**; plateau error **+0.123** | — | — | as G1 | **PASS** | rms 2.198; plateau −0.053 |
| | | (b) the trip rule: max(rest + 21.49, 65.9) | plateau **67.288 °C**, regime **floor** (600 MHz in 1.000 of the last 300 s) | **67.493 °C, floor** (the rest die is 1.6 °C above the 44.41 °C edge) | **−0.205** | PASS within ±0.60 and the regime as predicted | **PASS** | floor only: 67.884, −0.596 |

1. **The heat path holds on a third session, blind.** Q138(t)'s chain (R 0.663 °C per board W, five stages, t63 50 s) was fitted on
   E111 (1 Nov) and E133 (2 Nov, morning). Given tonight's measured board trace, it follows the die through both 15-minute holds to
   **0.76 °C rms (int8 −1s) and 0.37 °C rms (fp32 random)**. M6's frozen step response, scaled by 0.675, misses by 1.59 and 2.20 °C.
2. **The governor's regime was predicted from the rest die alone, and the prediction held.** Tonight's free card idled at 46 °C, two
   degrees above E133's morning. The trip rule therefore put G2 in the floor regime: the clock steps to 600 MHz once the die reads 66 and
   stays there while the die settles at rest + 21.49 °C. That is what happened. The die first read 66 at 59.5 s. The last sample above
   610 MHz came at 129.9 s, and after it the clock read 600 MHz to the end, with the plateau at 67.29 °C, 0.21 °C under the rule
   ([`posthoc.txt`](posthoc.txt) § G2). Altogether the clock spent 19.6 s at 800 MHz. The board peaked at 87.98 W at 62.9 s, with the clock
   at 700 MHz.
3. **What is left is a level, and it depends on the kind.** int8 −1s heats the die about 7% more per board watt than the chain's 0.663:
   0.711 tonight, against 0.675 for fp32 random in the same session. So G1's plateau sits 0.72 °C over the chain given its own board
   watts, and 1.09 °C over the planned-power arm. Of that 1.09 °C, only about 0.2 °C comes from the board: it rose 18.17 W against the
   planned 17.84 W, because the rest was warmer ([`posthoc.txt`](posthoc.txt) § G1). At every checkpoint G1's rise ran 0.54–1.05 °C over
   the frozen curve (60 s, 2, 5 and 10 min: +0.68, +1.05, +0.54, +0.86 °C), inside (b)'s ±1.30 band at each one.
4. **Item 8, between sessions.** By the scorer's metric over the last 300 s, the int8 hold reads 0.7096 (E111, 1 Nov), 0.7134 (E133,
   2 Nov morning) and **0.7111** tonight. The idle die meanwhile moved from 44 to 46 °C. Read like for like, though, the windows differ:
   tonight's last 300 s run 600–903 s, and over that same window E111 and E133 read 0.685 and 0.689 (Q138(t) A1 `C8`). So tonight reads
   3–4% higher, about 0.4 °C at this power. That is the size of the session-to-session move item 8 names, and no model term carries it.
5. **Safety.** No stop fired in either hold. G1 peaked at 41.27 W with the die at 60 °C. G2 peaked at **87.98 W**, with 79 samples over
   85 W and none over 90 W; its die reached 68 °C and the hottest sensor's running maximum 70 °C. The stops were 72 °C and 93 W on 3
   samples. G2 is the same hold as E111's (88.04 W) and E133's (88.65 W), and like them it raised no alarm. The stop path was tested on
   live samples in the smoke, before either hold. The die stop tripped 62 ms after the first live line at or above 30 °C, before any
   launch. The board stop tripped 62 ms after the third live line over 30 W, inside the launch, and the launch ended 186 ms later
   ([`queue.jsonl`](queue.jsonl) `stoptest_detail`).

## What this does to predicting power and heat

**The term tested:** the time-resolved heat path on a governed card, which is Q138(t)'s chain from board watts to the die, together with
the governor's trip rule that decides where the die settles. It was tested blind, on a session neither was fitted on.

| what is predicted | before: the desk's out-of-sample error (Q138(t), `cv-q138t.json`, A1 `A1_7_before_after`) | after: E144b, blind, a third session |
|---|---|---|
| **The die through a governed hold, given its board trace** (arm a) | the chain, fitted on one day and scored on the other: 0.44–1.16 °C rms, mean 0.79; M6's F(t) × 0.675 used as a chain: 0.47–1.28, mean 1.01; one pole of 89 s: 0.91–1.21, mean 0.99 | **the chain: 0.76 °C (int8 −1s), 0.37 °C (fp32 random)**; plateau +0.72 / +0.12 °C. M6 as frozen: 1.59 / 2.20 °C |
| **The plateau from the planned power only** (arm b) | G1: no blind reading (in sample, E133's W1B reads +0.47 °C by the same rule); G2's rule back-checked on E111 (+0.71, floor) and E133 (−0.08, trip), in sample | **G1 +1.09 °C** (M6 +0.99); **G2 −0.21 °C**, the floor regime predicted and found (M6, which has no governor term, −0.60) |
| **Where the governor holds fp32 random** (G2's regime) | the rule max(rest + 21.49, 65.9): the regime edge at a rest die of 44.41 °C | correct from a 46 °C rest: the floor, with 600 MHz in 1.000 of the last 300 s |

So the die's trajectory over a quarter hour on this card can now be quoted at **about 0.4–0.8 °C rms given the board's watts**, and its
plateau at **about 1 °C from the planned power**. That error is now a level, not a shape. The next term is a per-kind heat coefficient
(int8 −1s 0.711, fp32 random 0.675 °C per board W, against the chain's single 0.663), which would take most of G1's +0.7–1.1 °C.
The rest, about 0.4 °C between sessions with nothing changed, needs an inlet temperature, which the lab does not record.

## The session, step by step

| step | ran (PST) | card-min | result |
|---|---|---|---|
| SMOKE | 22:00:53–22:01:36 | 0.72 | exit 0, three launches rc 0, config 65 W / 65 °C: smoke check passed |
| STOPTEST-DIE | 22:01:36–22:01:38 | 0.03 | exit 4 `safety:die 69 C >= 30 C` (the hottest sensor's carried 69 °C; the die mean 46), 62 ms after the first live line, no launch: passed |
| STOPTEST-BOARD | 22:01:38–22:01:42 | 0.07 | exit 4 `safety:board 36.5 W > 30 W on 3 samples`, 62 ms after the third live line over 30 W, inside the launch, which ended 186 ms later: passed |
| rest | 22:01:42–22:16:42 | — | E98's rule, 15 min |
| **G1** | 22:16:42–22:33:47 | 17.09 | REST 120 s (46 °C, 21.94 W), then 107 of 107 processes of int8 −1s from 22:18:45 (the 57 °C gate passed at 46 °C) |
| END | 22:33:47–22:35:49 | 2.03 | G1's cool-down: 55 → 48 °C |
| rest | 22:35:49–22:50:50 | — | 15 min |
| **G2** | 22:50:50–23:08:05 | 17.25 | REST 120 s (46 °C, 21.91 W), then 106 of 106 processes of fp32 randn from 22:52:52 |
| END2 | 23:08:05–23:10:07 | 2.03 | G2's cool-down: 62 → 49 °C |

No other user was logged in to aifoundry2 at any check ([`idle_logins.jsonl`](idle_logins.jsonl), counts only), and `et-who` showed the
card free before the go and after the end.

## Departures (dated)

- **D1–D4, registered before any data** ([`E144b.md`](../../../../tools/claims-v3/e144b/E144b.md#departures-from-q138ts-plan-dated-before-any-data)):
  END and END2 ran right after their holds; the stop-path tests and the go gate were added; the holds were set as process counts; and
  E144b-K1 was added.
- **D5 (Mon 2 Nov 2026, 23:15 PST, after the data): the reducer's descriptive "first step down" says nothing.** It reads the first busy
  sample at or under 610 MHz. On G1 that was a sample at a process boundary (24.7 s, die 51 °C). On G2 it was the launch's own first
  sample. Neither marks a step by the governor. [`posthoc.txt`](posthoc.txt) reads G2's clock properly, post hoc: the first sample at
  800 MHz, the first step down after it, the die's first 66, and the last sample above the floor. No verdict uses any of it.
- **D6: the Tailscale lapse**, 22:04–22:08 PST, during the rest before G1. The queue needs no ssh, so it had no effect.
- **D7: the go came over ssh** (`GO`, 22:00:53). The fallback marker `tools/claims-v3/e144b/CLAIMED` was never needed and never committed.

## Device commands sent

Every one was a READ, and no WRITE of any kind was sent, not even the statistics reset. The registration has the full table
([`E144b.md` § Device commands sent](../../../../tools/claims-v3/e144b/E144b.md#device-commands-sent)), and the audit
([`logs/dmcmd-audit.txt`](../../../../tools/claims-v3/e144b/logs/dmcmd-audit.txt)) read GO: 35 send sites, with E133's two reviewed
exceptions. The counts below come from the records ([`posthoc.txt`](posthoc.txt) § 5).

| command | sent by, when | count | class (et-platform `836a4ab`, BL2 0.22.0) |
|---|---|---|---|
| `ettelem sample` (no `--reset-ms`): `GET_MODULE_POWER`, `GET_SP_STATS`, `GET_MODULE_CURRENT_TEMPERATURE`, `GET_ASIC_FREQUENCIES` | the sampler, every 100 ms through every run | 23,447 sampler lines | READ (RAM copies; PVT and PLL registers read) |
| `ettelem sample`: `GET_ASIC_VOLTAGE` (2 PMIC voltage-register reads), `GET_MODULE_VOLTAGE` (9) | the sampler, every sample | as above | READ (the owner's allowed read-only PMIC voltage reads, 2 Nov 2026) |
| `ettelem config`: `GET_MODULE_STATIC_TDP_LEVEL`, `GET_MODULE_TEMPERATURE_THRESHOLDS`, `GET_MODULE_POWER_STATE`, `GET_ASIC_FREQUENCIES`, `GET_ASIC_VOLTAGE` | `run_hpl.py` after every run and at each session's ends; the queue at each step's ends; the session-end read the queue's 14; the 12 session start and end query sets; one after every run; the session-end read | READ |
| `ettelem sptrace` | `run_hpl.py`, with every query set | as the query sets | READ (an MMIO copy of the SP trace region; no SP command) |
| `ettelem residency 2 3 4 5 6` (`run_hpl.py:622`) | — | 22 answered unsent | **NOT SENT** (`e144b-not-sent.jsonl` in each step) |
| `dev_mngt_service -m DM_CMD_GET_MODULE_POWER` | `run_hpl.py`'s drain, only if a sampler fails | 0 | READ |
| `sparsity_host` (E80's binary, sha256 `7adadf4f…`, checked by the runner) | every launch | 3 (smoke) + 1 (board stop test) + 107 + 106 processes | not device management (the ops node only) |
| any WRITE | — | **0** | **NONE SENT** |

## Files

| file | what |
|---|---|
| `README.md` | this |
| `results.json`, `reduce.txt` | `reduce_e144b.py`'s output: the frozen inputs' hashes, `score_e144.py a2 G1 G2` as committed at `c2f9920d`, E144b-K1, and the clock and safety readings |
| `posthoc_e144b.py`, `posthoc.txt` | post hoc readings, no verdict: G1's checkpoints, the board against the planned trace, G2's clock timeline, the idles, and the command counts |
| `SMOKE/`, `STOPTEST-DIE/`, `STOPTEST-BOARD/`, `G1/`, `END/`, `G2/`, `END2/` | each step's session: `tel/*.jsonl.gz` (the 10 Hz sampler), `launches.jsonl.gz`, `runs.jsonl`, `marks.jsonl`, `queries.jsonl`, `end.json`, `e144b.json` (hashes), `e144b-not-sent.jsonl`, the queue's `snapshot-*`, `config-*` and `sensors-*`, `sp/` (the SP trace ring) |
| `queue.jsonl`, `queue.out`, `schedule.json`, `status.json`, `GO`, `idle_logins.jsonl`, `phone.jsonl` | the queue's records, the go, the idle-login decisions (counts only) and the camera phone's health (descriptive) |
| `config-session-end.txt` | the session-end `ettelem config` (23:10:07 PST) |
| `history/` | the three boxes' own 5 s history over the session, numbers only |

## How to reproduce

```bash
/usr/bin/python3 tools/claims-v3/e144b/reduce_e144b.py docs/reports/data/2026-11-02-e144-heat-minutes-aifoundry2 > docs/reports/data/2026-11-02-e144-heat-minutes-aifoundry2/reduce.txt
/usr/bin/python3 docs/reports/data/2026-11-02-e144-heat-minutes-aifoundry2/posthoc_e144b.py > docs/reports/data/2026-11-02-e144-heat-minutes-aifoundry2/posthoc.txt
```

These need numpy 1.26.4 (the desk's system Python 3.9). The scorer is Q138(t)'s `score_e144.py`, unchanged.
