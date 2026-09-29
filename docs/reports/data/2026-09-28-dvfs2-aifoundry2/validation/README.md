# DV2 validation (E51): the frozen replication on aifoundry2, 28 September 20:45 PDT - 29 September 16:57 PDT

Frozen plan: `tools/claims-v3/dv2v/PREREG-VAL.md` (sha256 `e150ce16…`), lock `tools/claims-v3/dv2v/LOCK.sha256` (19
files, checked by every pass and again before the reduction: all OK). Run from the `et-soc1-dvfs2` worktree with the
full schedule (`schedule-dv2val-aifoundry2.txt`), after the owner accepted a same-card replication (28 Sep evening).

- `raw/`: the VZ cycles (`p91xx-p94xx`, read-only, 180 s apart), the VN candidates (`p95xx`) and the three frozen
  NAT-4 replication sessions (`p6051` 22:13-22:30, 1 T-block; `p6052` 22:42-23:06, 2; `p6053` 23:19-23:56, 4). Large
  logs and SP dumps are gzipped. `queue-dv2val-aifoundry2.log.gz`: the queue's log. The 20 h window closed at 16:45;
  the remaining passes were skipped by rule.
- `verdicts-dv2val.json`: `python3 tools/claims-v3/dv2v/reduce_val.py --data <raw> --out verdicts-dv2val.json`.

**Verdicts** (378 VZ cycles; PREREG-VAL §2's rule: a theory survives if every registered item under it passes,
falls if any fails, and is otherwise untested):

| Item | Verdict | Counts |
|---|---|---|
| I1 (TH1-idle) | INSUFFICIENT | 334 clean cycles, 4 separating the hottest shire from the mean |
| I2 (TH3) | PASS | 51 enters, 52 exits, 0 off-rule |
| I3 (TH7) | FAIL | 52 exits, 1 not followed at once by the idle reset |
| I4 (TH2) | INSUFFICIENT | 46 intervals, 2 off the 0.4053 s grid |
| I5 (TH2 context) | PASS | 51 idle enters |
| I6 (TH8) | PASS | 6 intervals, 0 outside 5 ms |
| G1-T (TH1-busy) | INSUFFICIENT | 9 separating runs in 5 blocks: 7 fit the mean, 0 the hottest shire (the rule needs >= 80% fitting the mean) |
| G1-H (TH1-busy) | PASS | 17 holds at 800 MHz with the hottest sensor >= 67 C, in 6 blocks |
| G4-S (Q2) | INSUFFICIENT | 4 complete blocks (6 needed); L = 0.248, 99% CI [-0.112, 0.607] |
| G4 (TH5, reported) | not registered | L_P 0.219 against L_pred 0.28 |
| G2-C (TH2) | PASS | 67 climbs, all with 700 MHz in <= 1 sample |
| G2-D (TH2) | INSUFFICIENT | 16 descents (20 needed), all in band, 0.5 s dwell |
| G2-U (TH3) | PASS | 92 up-steps, all read <= 65 before |
| G3-L (TH4) | PASS | 22 launches, median 0.67 s, max 1.2 s |
| G3-I (TH4) | PASS | 12 runs, max 1.09 s |

**Theories:** TH3 (no hysteresis: enter at 66, exit at 65), TH4 (the launch and end latencies come from the Master
Minion's heartbeat) and TH8 (the THERMAL_DOWN counter adds whole episodes) **survived**; TH7 (an idle exit is followed
at once by the idle reset) **fell** (1 of 52); TH1-busy, TH1-idle, TH2 and Q2 are **untested** (INSUFFICIENT: too few
qualifying cycles or blocks), though no run fitted the hottest shire (G1-T 0 of 9) and 17 holds at 800 MHz with a
sensor >= 67 C passed G1-H. The card idled at 71-76 C for most of the window, so only three heating sessions could
start (the plan's maximum, below 60 C at night); the Master Minion did not hang in any of them.
