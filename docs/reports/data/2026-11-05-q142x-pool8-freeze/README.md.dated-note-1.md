# Dated note 1 beside README.md (Thu 5 Nov 2026; Q142(x)'s fix pass, after its verifier) - on pool 8, A2-R2 can FAIL through A2-Bp but cannot PASS; card 1's N1 a-priori D starts at 4.16 W; two disclosures completed

*On the kinds page, [section 11, what is still open](https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers#11-what-is-still-open):
**item 6**, with items 8 and 9. Written on Thu 5 Nov 2026 from about 03:10 PST, desk only on the Intel, and committed at the time git
records. It answers the five minor faults that the verifier of Q142(x) found (desk only, 02:35-03:00 PST). That verifier re-derived
dated note A1 (`ebf68c52`) and the freeze (`4576fb90`) from the committed files and found no frozen number wrong.*

**What stays as committed:** every file of `ebf68c52` and `4576fb90`. [`README.md`](README.md) stays as written, and this note supersedes
only the lines it names below. No prediction, count, line, verdict or hash list changes. The four predictions files, `intervals-pool8.json`,
this directory's `SHA256SUMS` (160) and the pool's (89) are untouched.

## 1. A2-R2 on pool 8 (the verifier's fault 1)

README.md overstates A2-R2's status in two places:
- Results 6, lines 105-107: "so A2-R2 (rank 2 on M10 carried) is NOT SCORED too";
- What this cannot say, line 177: "(A2-G, A2-Bg, A2-F1, A2-W1, hence A2-R2)".

Read both as:

> **On aifoundry2, P8-A2-G, A2-Bg, A2-F1 and A2-W1 are NOT SCORED** at the planned n: their governed group holds 3 tiles, under its
> minimum of 8. **A2-R2 cannot PASS on pool 8. It reads FAIL if A2-Bp FAILs, else NOT SCORED.**

**Why.**
- R2's registered verdict is "PASS if G, Bg and Bp all PASS; FAIL if any FAILs; else NOT SCORED". It is in
  [`POOL8-REGISTRATION.md`](../../../../tools/claims-v3/m10/POOL8-REGISTRATION.md), section 7's aifoundry2 table, and A2-5 gives its
  meaning.
- The frozen file fixes the groups: a tile is governed if M10 carried predicts its burst below 795 MHz at the fallback and T_ref (A2-6(f)).
  The governed group therefore stays at 3, and G and Bg can never be scored on pool 8.
- A2-Bp is scored at the planned n: 21 pinned tiles (`intervals-pool8.json` › `cards.aifoundry2.rules.P8-A2-Bp`, `scored_at_planned_n`
  true).
- So on pool 8, R2 is a one-sided test. A failed Bp is a registered FAIL of rank 2 on M10 carried, and no session can make R2 pass.

**What was right as committed.** `intervals-pool8.json` gives `P8-A2-R2` the registered `verdict_form` and its three components, with no
planned-n reading. `4576fb90`'s message names only G, Bg, F1 and W1. README.md's "What it does to predicting power and heat" (lines
129-131) says pool 8 cannot test A2-G or A2-Bg, and that also holds. To it, add one clause: rank 2 on M10 carried can still fail on the
pinned bursts.

**For E173's scorer** (the next round's (kg) lane): compute A2-R2 from the registered form, using the session's own G, Bg and Bp verdicts.
Never hard-code it as NOT SCORED.

## 2. Card 1's N1 range of M10's a-priori D (fault 3)

Results 4, line 75, gives card 1's range as "4.17-24.11 W". The committed minimum is 4.16496 W, on `int8.u8_sparseq_58e6e0`
(`predictions-pool8-aifoundry1c1.json` › `tiles` › `M10.D_stated_w`). So the range is **4.16-24.11 W**; the maximum, 24.1097 W, is
`fp32.u8_lognorm_62af49`.

The other ranges in that sentence were re-read here from the same files and are right: aifoundry3's 4.33-25.08 W, and the 4.5 s rises
of 0.82-3.24 °C on aifoundry3 and 0.78-3.09 °C on card 1.

## 3. The counting corrections, as the records should quote them (fault 2)

Results 2's list of seven is right. These are three-point minus N-point averages, in W of D at M9's float prices
(`predictions-pool8-aifoundry3.json` › `tiles` › `recount.three_point_minus_N_w`):

| tile | correction (W) |
|---|---:|
| `fp32.s8_onebit_b18` | +0.495 |
| `fp32.b_onebit_b20_one` | +0.374 |
| `fp16.s8_onebit_b7` | −0.337 |
| `fp16.s8_onebit_b10` | +0.219 |
| `fp32.s8_onebit_b19` | −0.207 |
| `fp32.s8_onebit_b13` (A 0x40080727) | −0.149 |
| `fp16.b_onebit_b8_pi` | −0.134 |

Every other float tile is within ±0.055 W (next: `fp32.u8_bimodal` +0.055). One summary outside this tree, the lane's return record,
listed only five of the seven and said "others within 0.055". The records quote the seven above.

## 4. Compute, completed (fault 4)

README.md's Compute section names, on the Intel, 18 jobs through the round's local slot and, beside them, "git, hashing, the public-text
scan and bounded copies to and from the mini". Python also ran on the Intel **outside the slot**, which the round's compute rule asks
Python jobs to use.

Each of those runs was a read of committed or scratch JSON, or a comparison of two counts files, taking about a second on one core. They
were:
- an interpreter probe;
- seven reads made for A1's facts, before A1's commit: `blind6.json`, `blind7.json` and their counts, E153's and E157's records and C
  checks, and the designer's provenance files;
- the bench driver's point-set self-check;
- the chunk check, which the step scripts ran before and after each chunk, and the plan summary, once per step;
- Q141(t2)'s committed `extract_point.py` and `compare_points.py`, plus one inline read. These wrote the build checks' and check D's
  records (`bench/check-b1.json`, `check-i1.json`, `check-d-*.json`, `point-*.json`). The verifier re-derived those records: 184 of 184
  leaves equal, and the int8 floor's 142 leaves at each of its three points;
- the check of the 12 earlier hash lists;
- the public-text scan;
- the summary scripts that wrote this README's tables and the lane's return record.

None of these runs counted, fitted or predicted.

On the mini, beside the 10 bench calls, the staging made the lane's directories, copied the tree and ran `bench_pool8.py check-build`,
which hashed the reused build's binaries against the build's record. Each of these steps ran with a connect timeout and a time limit,
and none prompted.

## 5. What the public-text scan covered (fault 5)

The privacy table is absent on the Intel. So the lane's scan, like this note's, used three things:
- `sanitize_extracts.py`'s fixed list;
- the lane's own extra patterns: home paths, private network addresses, host names, foundry and EDA names, credential words, private
  page ids and scratch paths;
- a read by eye.

Lab users' logins were therefore not checked against the table. A1-5 states this limit for the designer's scan, but README.md did not
state it for the lane's own scan.

The verifier also ran its own scan over all 161 committed files and both commit messages, and found nothing private. Its only hits were
two already accounted for: the pool's 14 disclosed language-model words for a text position, and the standard attribution line in each
message.

## What it does to predicting power and heat

Nothing measured or predicted changes. Read correctly, pool 8 tests rank 2 on M10 carried one-sided on aifoundry2. The pinned bursts can
show it failing (A2-Bp), but no pool-8 session can show it passing, because the governed clock and board (A2-G, A2-Bg) cannot be scored.
Every 600 MHz rule, every line in Results 6 and LG's power stand as committed.

## Compute (this note)

The Intel only. Every Python run went through the round's local slot, one job at a time, each under a minute: the reads behind sections 1-3,
this note's public-text scan, and the hash lists after the commit. Beside them: git, grep and a JSON reader. No lab box, no mini job,
no card, no device command, no post.
