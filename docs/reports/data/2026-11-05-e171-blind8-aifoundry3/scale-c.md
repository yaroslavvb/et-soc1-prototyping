# E171 on aifoundry3: the scale anchors' C status (score_p8_600_v2.py scale-c; dated note 1, N2)

Reported beside, never the verdict. The registered verdicts are the committed scorer's `build/e171-out/2026-11-05-e171-blind8-aifoundry3/scored.json` (f3deaf08fa6b); the check of C `build/e171-out/2026-11-05-e171-blind8-aifoundry3/ccheck/ccheck-all.json` (3e1d60dd8423); the primary's s = 1.00615 from 6 anchors.

| anchor | from | in s | ratio | launches | PASS | C all PASS |
|---|---|---|---:|---:|---:|---|
| `fp32.randn` | M10's own list | yes | 1.00781 | 120 | 120 | yes |
| `fp16.randn` | M10's own list | yes | 1.00348 | 120 | 120 | yes |
| `fp32.anchor6_randn` | M10's own list | no |  | 0 | 0 | NO |
| `fp16.anchor6_randn` | M10's own list | no |  | 0 | 0 | NO |
| `fp32.anchor7_randn_a` | M10's own list | no |  | 0 | 0 | NO |
| `fp32.anchor7_randn_b` | M10's own list | no |  | 0 | 0 | NO |
| `fp16.anchor7_randn_a` | M10's own list | no |  | 0 | 0 | NO |
| `fp16.anchor7_randn_b` | M10's own list | no |  | 0 | 0 | NO |
| `fp16.anchor8_randn_a_8c7827` | pool 8's scale anchor | yes | 1.00531 | 40 | 40 | yes |
| `fp16.anchor8_randn_b_3a0fef` | pool 8's scale anchor | yes | 1.00521 | 40 | 40 | yes |
| `fp32.anchor8_randn_a_989b8a` | pool 8's scale anchor | yes | 1.00699 | 40 | 40 | yes |
| `fp32.anchor8_randn_b_833ac3` | pool 8's scale anchor | yes | 1.00800 | 40 | 40 | yes |

E78's other items, on which the reduction's footing rests (reported only):

| item | launches | PASS | C all PASS |
|---|---:|---:|---|
| `fp32.zeros` | 120 | 120 | yes |
| `fp16.zeros` | 120 | 120 | yes |
| `int8.zeros` | 120 | 120 | yes |
| `int8.full` | 120 | 120 | yes |
| `anchor_pi` | 80 | 80 | yes |

SCALE-C E171: 6 anchors in s, every one C all PASS: the arm c_clean_scale is the primary

