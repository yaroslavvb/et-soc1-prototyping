# Dated note 1 beside README.md, Thu 5 Nov 2026 (week 45), about 14:40 PST: the verifier's four corrections (E174's route, D1 chosen after the stop, the boot's zone, two sentences as the records should quote them), and what M1's paired difference is made of (post hoc)

*This note sits beside [`README.md`](README.md), not inside it: the README stays as committed in `ed8b5761` (12:47:48 PST) and `571d0482`
(12:51:14 PST). It answers the verifier of E173's card lane (`verify-card-a2-e173`, Thu 5 Nov 2026, about 12:55-13:42 PST), whose verdict
was "holds with fixes" with four minor faults. Desk only. **No number, line, rule, verdict, prediction, data file or frozen file changes, and
nothing is re-scored.** The verifier's own re-score through the registered `score_e173.py` gave `results.json` and `score.txt` byte for byte.
The figures below come from [`posthoc_note1_e173.py`](posthoc_note1_e173.py), which reads only [`results.json`](results.json) and imports no
scorer, with its output in [`posthoc-note1-e173.txt`](posthoc-note1-e173.txt). The note answers the same items as the README: the kinds
page's [section 11](https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers#11-what-is-still-open) item 6, with items 8 and 9.*

## 1. E174's collector has the same two lines, but not the same stop (fault 1)

The README's D1 ends: "E174's collector (`collect_e174.sh` lines 34 and 38) has the same route." It has the same two lines: it tees the
C-log list and copies it into its data dir's `logs/`. The outcome is not the same:
- **E174's driver hands its collector the relative `build/e174-raw`** (`box/step_e174_v3.sh` lines 36-37). Its list reads
  `REQUIRED s1 build/e174-raw/cc/ccheck-s1.json` ([E174's `logs/cclist.txt`](../2026-11-05-e174-blind8-card0/logs/cclist.txt)), and its
  collection passed the desk-path gate at 13:18:58 PST (rc 0, in the card day's runbook log, outside the repo).
- **The absolute raw path is E173's driver's** (`box/step_e173_v3.sh` line 24, `RAW=$RB_OUT/e173-raw`) **and E175's**
  (`box/step_e175_v3.sh` line 187, kit `16b3d6e3`). Both collectors tee the list at line 86 and copy `logs/` into the data dir at line 96.

The records quote: "E174's driver passes the relative build/e174-raw, and its collection passed the desk-path gate (13:18:58); the absolute
raw path is E173's driver's (and E175's)."

## 2. D1 was a remedy chosen after the stop (fault 2)

**D1's mask was registered nowhere before the stop.**
- The gate's own message at 12:30:54 read "commit nothing; fix the route, remove the outputs, collect again".
- E173's lane neither changed the route nor collected again. After the stop, it chose to replace the scratch prefix in `logs/cclist.txt` by
  `<RB_OUT>` and to re-run the two gates.

The README discloses it, but does not say it was unregistered. **It is mask-only, and no score depends on it.** The verifier found the copy
as collected, with that prefix replaced by `<RB_OUT>`, equal to the committed [`logs/cclist.txt`](logs/cclist.txt) byte for byte (sha256
`48807990…` as collected, `5273aabd…` committed). Its re-score of the committed session was byte-identical.

**For later runs it is now a registered rule, before any E175 data:** the q142kg runbook's
[dated note 3](../../../../tools/claims-v3/q142kg-runbook/README.md.dated-note-3.md) (lab `d85d1e0f`, 14:41:14 PST), with its code and a
desk test. That test replays this D1 from the committed files, and the rule's output equals this `logs/cclist.txt` byte for byte (13 of 13
PASS).

The records quote: "E173's D1 was an unregistered remedy chosen after the stop: disclosed, mask-only, and with no effect on any score; it is
registered as a rule for later collections in the q142kg runbook's dated note 3."

## 3. The host booted at 15:13:03 PDT, not PST (fault 3)

"What ran" (look first) says the host booted "2026-10-26 15:13:03 PST". The box's `uptime -s` prints its local time with no zone, and on
26 Oct that zone was PDT. **The boot was 2026-10-26 15:13:03 PDT (14:13:03 PST, 22:13:03 UTC).** Three reads agree:
- E69's [`err_events.txt`](../2026-10-27-e69-governor-knob/err_events.txt) records the host's boot epoch as `2026-10-26T15:13:03.080007-07:00`;
- the look's own uptime line (11:36:02 PST, "up 9 days, 21:22", in the lane's step log, outside the repo) gives about 15:14 PDT;
- the records already corrected this label for the card half (`docs/findings/05-claims.md`: "the hosts' boots are PDT").

**The continuity verdict is unchanged.** The boot is 22.72 h before E69's firmware read of 2026-10-27 13:56:26 PDT (21.72 h if it were read
as PST). The records quote PDT.

## 4. Two sentences of the lane's summary, as the records should quote them (fault 4)

The lane's summary, outside the repo, said "M10's refit (term b's counts, the session scale) helps in sign only (0.05 W)". **Rule E carries
M10's D to aifoundry2 at s = 1, so term a, the session scale, is not tested here.** E173.md ("What it does to predicting power and heat")
reads "D600 on aifoundry3's footing at the nominal rate with s = 1 (a governed burst session runs no 600 MHz anchor)". Only the zeros
anchors reach the primary's anchors input. The records quote: "M10's refit of D with term b's counts (rule E at s = 1, so term a is not
tested on aifoundry2) is better than M9's part by 0.05 W rms in sign only, not resolved." The README's own line, "M10's refit carries in
sign, not resolved", is right as it stands.

The same summary gave the governor's dips the whole of three tiles' errors ("pulling three tiles 1.8-2.3 W low"). Pass by pass, against M10
carried (W; `results.json` › `run_rows`, `score.reported.tiles`):

| tile | passes (MHz) | error, all three passes | the 800 MHz passes alone | the dipped passes' share |
|---|---|---|---|---|
| `fp16.r8_granite_l3_pv_e993b7` | 800, 800, 752.9 | −1.841 | −0.663 | −1.178 |
| `int8.l8_flip_d2p2c16_231d` | 800, 779.6, 752.9 | −2.042 | −0.172 | −1.870 |
| `int8.u8_ar_k_0a9fe5` | 800, 750, 800 | −2.295 | −0.797 | −1.498 |
| `int8.r8_granite_l4_actdown_b076f2` (the fourth tile with a dipped pass) | 796, 800, 800 | −0.601 | −0.938 | +0.337 |

The records quote: "the dipped passes take three tiles 1.84-2.30 W low on average; at 800 MHz the same tiles read 0.17-0.80 W low." The
README's sentence ("three tiles whose passes dipped below 800 MHz read −1.84 to −2.30 W below it") is accurate as it stands. Beside it, the
pinned clock's rms is 0.073 MHz over the 17 pinned tiles with no dipped pass (7.012 MHz over all 21, F2 as scored).

## 5. What M1's paired difference is made of here (post hoc, beside fault 4)

**Why ask.** The verifier of E175's kit (`verify-desk-q143g-e175-governed`, its fault 1) found that on E175's tiles M10 carried's board
predictions sit below M9's part's by a near-constant offset. A paired rms difference then follows the session's board level, not D. E173's
M1 is the same paired form, so the same question applies to its 24 tiles.

**On E173 the answer is no.** Take d = M10 carried − M9's part, per tile, on the board:
- d has mean +0.026 W and sd 0.218 W, from −0.559 to +0.681 W, with 12 tiles below zero and 12 above;
- its largest values are single high bits (class S: |d| up to 0.681 W). On the other 16 tiles |d| is at most 0.102 W.

**The paired difference is made of those per-tile changes.** rms(a)² − rms(b)² is −0.106 W², where a and b are the measured board less M10
carried and less M9's part. With every d set to its mean, it would be +0.003 W²: the part a constant offset gives, through the session's mean
error against M9's part (−0.0501 W over the 24 tiles).

So E173's M1 (−0.050 W [−0.161, +0.037], NOT RESOLVED) is not a reading of the session's board level. It reads M10's per-tile changes, the
largest on the single high bits (the class whose counts term b changes), under the part's own error of about 1 W on those tiles (class S
reads +1.06 W above M10 carried on average, the README's figure). The README's reading ("The part's own
error (about 1 W) hides the D difference") stands. This is post hoc: no rule was registered for it, and no verdict changes.

SPDX-License-Identifier: Apache-2.0
