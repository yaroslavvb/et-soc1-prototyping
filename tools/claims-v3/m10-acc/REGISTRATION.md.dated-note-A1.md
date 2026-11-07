# Dated amendment A1 beside REGISTRATION.md (Sat 7 Nov 2026, written about 11:20-11:35 PST; Q153(m10acc)) - a second reading of "the accumulator's toggles per micro-op": the accumulator words a lane's datapath takes in from one micro-op to the next, registered after the primary's result and before this form's first output

*REGISTRATION.md (`b5586759`, 10:56:49 PST), the code (`b48cf669`, 11:02:22) and every output of the registered fit stay as committed.
This amendment adds one candidate form, **ACC-L**. It is written after the registered fit's output was read (11:13 PST: the primary
form does not enter in either family) and after one post hoc reading of it (`posthoc_m10acc.py`: the single-bit lists' measured steps
do not follow the step of the accumulator register's toggles, r −0.03 over 70 steps, while x_acc's step is about 0 a micro-op). So
ACC-L's form was **chosen after one look** at the primary's held-out result; its own held-out errors are computed after this file is
committed, by code committed with it.*

## A1-1. What the primary counted, and what it did not

REGISTRATION.md § 2.1's x_acc counts, for each accumulator element, the Hamming distance between the word written at one step and the
word the same element held before: the register entry's own toggles. In the PRM's order a lane does not take the same element twice
in a row. For B row k it takes C[i][l], then C[i][8 + l], then C[i + 1][l], ... (floats: two micro-ops of 8 lanes for each A row i;
int8: slot s takes C[i][s] for each i). So the accumulator word entering a lane's FMA (its C operand, `opc`; int8's `tenc_rd_data`),
and the result leaving it, change at every micro-op from one element's value to the next element's. When the two elements a lane
alternates between hold equal words (every one-number kind), that change is the step's own change, once a k-pass; when they differ
(a single high B bit makes C[i][l] and C[i][8 + l] accumulate two different words), the lane's operand word toggles at every
micro-op by the Hamming distance between two accumulators. x_acc does not see that, and it is the accumulator's activity a datapath
sees per micro-op.

## A1-2. The feature x_lane

For a tile of format φ and a launch of N ops: all 256 elements are stepped together, op by op, with `accum.c`'s arithmetic and zero
gate (REGISTRATION.md § 2.1, unchanged). Within each op, in the PRM's issue order (floats: for k, for i, for h = 0, 1, lane l takes
element (i, 8h + l); int8: for k, for i, slot s takes element (i, s)), each lane's C operand is the element's word before its update
at that step. **x_lane(tile, N)** = the mean over ops 1..N−1 of the sum, over the lanes (8; int8 16 slots) and the op's micro-ops, of
the Hamming distance between the C operand word a lane takes and the one it took at its previous active slot (a gated slot, an A or B
word of 0, keeps the lane's previous word and adds nothing; op 0 left out, as in § 2.1): toggles per op. For a one-number kind it
equals `flipmodel_e178.c`'s `c_in` class (8 or 16 lanes × the step's Hamming distance, once a k-pass). Per micro-op it is
x_lane / 512 (floats) or / 256 (int8). N is § 2.3's.

**The code:** `tools/claims-v3/m10-acc/acctrace_m10acc_a1.c` (a new file; `accum.c` included unchanged), which also prints x_acc,
so that **check A1-T1** can require it to equal the committed `features-m10acc.json` on every tile; and **check A1-T2**: for E178's
40 kinds x_lane at `N_LAUNCH` equals `forecast-e178.json` › `flips_i.launch_mean.c_in` to 0.001 a op. Either failing stops the fit.
The traces run on the mini as § 8 says.

## A1-3. The form ACC-L, its fit and its rule

- **M10-ACC-L's D = M10's D + s × c × rate × (τ_L,φ × x_lane + τ_bth × x_bth)**, x_bth as § 2.2 (floats; 0 for int8); one price per
  family, as § 4.
- **Rows, response, estimator, leave one run out, uncertainty, arms (ACC-L1 without x_bth; strict), forecasts and post hoc readings:**
  exactly REGISTRATION.md §§ 3-7 with x_lane in place of x_acc, by `fit_m10acc_a1.py` (a new file that imports `fit_m10acc.py`'s rows,
  checks, estimator and rule unchanged). The same seeds.
- **The entry rule is § 5's R1-R3, unchanged.** If ACC-L meets them in a family, it is M10's candidate for that family for the next
  blind pool **with this note's disclosure** (its form chosen after one look at the primary's result), scored there as P9-ACC; the
  primary ACC's verdict (it does not enter) stands either way. If ACC-L does not meet them, M10 stays as frozen, and ACC-L is a reported
  arm beside ACC in the next pool and in E182.
- **Its frozen file:** `m10acc-a1.json`, beside `m10acc.json`, which is never edited; the E182 grid forecasts beside the primary's, in
  `forecasts-e182-m10acc-a1.json`. `predict_m10acc.py` is unchanged; ACC-L's predictor is `predict_m10acc_a1.py`, a new file.

## A1-4. Tiers and what stays

Public tier only, as REGISTRATION.md's Builds on block: the lab's committed data and code, the open RTL and the PRM's order. Every
committed file stays as committed, and the primary's verdict stands.

SPDX-License-Identifier: Apache-2.0
