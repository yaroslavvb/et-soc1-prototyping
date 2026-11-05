# E172 on aifoundry1c1: the scale anchors' C status (score_p8_600_v2.py scale-c; dated note 1, N2)

Reported beside, never the verdict. The registered verdicts are the committed scorer's `build/e172-out/2026-11-05-e172-blind8-card1/scored.json` (46b4b4248b61); the check of C `build/e172-out/2026-11-05-e172-blind8-card1/ccheck/ccheck-session.json` (089ff1d019a5); the primary's s = 1.00798 from 6 anchors.

| anchor | from | in s | ratio | launches | PASS | C all PASS |
|---|---|---|---:|---:|---:|---|
| `fp32.randn` | M10's own list | yes | 1.01184 | 90 | 90 | yes |
| `fp16.randn` | M10's own list | yes | 1.00780 | 90 | 90 | yes |
| `fp32.anchor6_randn` | M10's own list | no |  | 0 | 0 | NO |
| `fp16.anchor6_randn` | M10's own list | no |  | 0 | 0 | NO |
| `fp32.anchor7_randn_a` | M10's own list | no |  | 0 | 0 | NO |
| `fp32.anchor7_randn_b` | M10's own list | no |  | 0 | 0 | NO |
| `fp16.anchor7_randn_a` | M10's own list | no |  | 0 | 0 | NO |
| `fp16.anchor7_randn_b` | M10's own list | no |  | 0 | 0 | NO |
| `fp16.anchor8_randn_a_8c7827` | pool 8's scale anchor | yes | 1.00628 | 30 | 30 | yes |
| `fp16.anchor8_randn_b_3a0fef` | pool 8's scale anchor | yes | 1.00600 | 30 | 30 | yes |
| `fp32.anchor8_randn_a_989b8a` | pool 8's scale anchor | yes | 1.01229 | 30 | 30 | yes |
| `fp32.anchor8_randn_b_833ac3` | pool 8's scale anchor | yes | 1.00817 | 30 | 30 | yes |

E78's other items, on which the reduction's footing rests (reported only):

| item | launches | PASS | C all PASS |
|---|---:|---:|---|
| `fp32.zeros` | 90 | 90 | yes |
| `fp16.zeros` | 80 | 80 | yes |
| `int8.zeros` | 90 | 90 | yes |
| `int8.full` | 90 | 90 | yes |
| `anchor_pi` | 60 | 60 | yes |

SCALE-C E172: 6 anchors in s, every one C all PASS: the arm c_clean_scale is the primary

