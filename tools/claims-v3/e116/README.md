# E116 (Q133): E88's split on a second card, aifoundry3 card 0, with C read back once per design — pre-registration

*On the kinds page, [section 11, what is still open](https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers#11-what-is-still-open) as of `1fe8377a18af`: the final critic's replicates (its item 8, "Replicates for the new sections": "E88's split itself … not re-run"), with item 6, "A power model across kinds" ("a new card without a scale": E88's frozen bands are scored here on a second card), and item 5's held fp32 sign (E88's `s_abs` on a second card).*

*Written Sun 1 Nov 2026 (week 44), ~16:50 PST, on the Intel, before the claim. The commit that adds this directory is the
registration; nothing in it changes after that commit. Data will go to
`docs/reports/data/2026-11-01-e116-split-replicate/`.*

## The question

[E88](../../../docs/reports/data/2026-10-31-e88-result-path/README.md) split a multiply-add's switching power three ways
on aifoundry1 card 1 at 600 MHz, from 13 designed tiles beside each format's zeros, random data and ones: **(i)** the lane
being clocked, **(iii)** the operand-side multiplier, **(ii)** the result path (fp32, random positive operands: 0.367 /
0.399 / 0.234 of 21.58 W; fp16 0.389 / 0.303 / 0.308; int8 0.257 / 0.472 / 0.271). Its README calls the shares the robust
result. They were measured on one card, and the card's C was never read back during E88 (E104 later read seven of its
tiles on card 1; int8 was never read). E116 asks:

1. **Do the shares replicate on a second card** (aifoundry3 card 0, the card E78 and E113 ran on)?
2. **Do the watts carry by E82's card scale?** E82 found D(aifoundry3) / D(card 1) = 1.030 (fp32), 1.033 (fp16), 1.027
   (int8) over the kinds matrix.
3. **Do E88's 32 registered verdicts repeat** on this card (13 mechanism rules, 19 frozen model bands)?
4. **Does every E88 design do on this card what the desk says it does?** One read of C per tile (22 tiles: the 13 designs
   and the 9 anchors) at n = 199,874 ops, every word of all 1,024 minions, against `accum.c`'s words frozen here. This is
   the first read-back on aifoundry3's card and the first of int8's E88 designs anywhere.

## What runs

- **The tiles:** E88's 22, byte for byte (`tools/claims-v3/rpath/tiles/`, sha256 in `e88.json`, checked before every
  pass), plus E78's built-in `anchor_pi` tie. No new tile.
- **The power passes:** E88's harness unchanged: `tools/claims-v3/rpath/block_e88.sh` (which already carries E60's
  departure D1 for aifoundry3: an idle login does not block; another user's device process or a holder of the card's
  node or lock does) and `queue_e88.sh`, with E78's runner `kinds/run_e78.py` and its launch protocol (heat to 59 °C,
  launch at 58 °C, 4 s runs, the quiet wait), E78's sampler (no `--reset-ms`). Per-pass order is E88's code, seeded
  `E88|aifoundry3|<pass>`. Pass numbers: the smoke 11601, the read-back 11602, the measured passes 11610 onward.
- **The read-back:** E104's one-flag host patch (`kinds/patch_host_e104.py`, unchanged: `--dump-c` writes C after each
  launch) built on aifoundry3 into `build/e116/b/` by `build_host_e116.sh` before the claim (no device access; the binary
  every power pass runs, `build/sparsity/host/sparsity_host`, is not touched). `readback_e116.py`: one launch of exactly
  n = 199,874 ops per tile (`--seconds 0`), under `timeout 10`, inside a lib.sh block that holds the card lock
  (`block_readback_e116.sh`); C compared on the spot with `expect-e116.json`. n is E104's, so the seven tiles E104 read
  at 199,874 on card 1 compare word for word across the two cards.
- **The expected words:** `make_predictions_e116.py` ran `build/e102-accum/accum` (`rtl-sim/fma_toggle_v2/accum.c`, the
  RTL's arithmetic: E104's reading, which equalled all 110 of E104's reads) on each tile at n = 199,874 and froze the 256
  words per tile in `expect-e116.json`. For the seven tiles E104 read at that n, accum.c's words here equal E104's
  recorded `rtl_hex` (and so E104's card-1 reads) in all seven.
- **The session** (`session_e116.sh`, detached on the box after the claim): et-who and a read-only `ettelem config`
  under the lock (`timeout 10`); the read-back; the smoke (`block_e88.sh 11601 --smoke`, unchanged) and its gate (every
  launch ok, cycles per op 546 / 546 / 318, the clock 550–650 MHz); then `queue_e88.sh 11610 7` with
  `E88_BUDGET_MIN = min(34, 38 − minutes since the session started)` and `E88_DEADLINE = 18:55`; then the closing
  `ettelem config` and et-who. **At most 40 card-minutes; every run ends by 19:00 PST; no session starts after 18:00.**
- **Nothing is set.** No governor, TDP, threshold or clock write, no reset, no `--reset-ms`, no PMIC command, no
  firmware work. aifoundry3 runs at 600 MHz by its boot-time TDP 0 (E78's frame); the config reads expect TDP 0 W and
  threshold 65 °C.

## The reduction (registered code)

`collect_e116.sh` runs, on the Intel over a copy of the raw passes:
1. `rpath/reduce_e88.py` **unchanged** (it runs `kinds/reduce_e78.py` unchanged inside it): launch-gap dips removed (E82
   A2's definition, E88's primary), leakage slope `auto`. On aifoundry3 the config gate is reduce_e78.py's own (TDP 0,
   65 °C); reduce_e88.py's card-1 substitution (65 W, 65 °C) never fires. Its output still says `"experiment": "E88"` and
   names card 1's substitution in its text: those are reduce_e88.py's fixed strings, not this card's.
2. E88's four arms: dips kept, leakage 0.545, 0.3803 and 0 W/°C.
3. `rpath/score_e88.py` **unchanged** on that reduction: E88's 32 rules with E88's frozen bands (card 1's, no scale).
4. `e116/score_e116.py`: E116's rules below. Self-test `selftest_e116.py` (output `selftest_e116.txt`): on E88's own data
   it reproduces E88's split exactly (7.922 / 8.614 / 5.042 W; 0.367 / 0.399 / 0.234) and gives S and W PASS, H 13 of 13,
   P 17 of 19; a changed word gives R0 FAIL; three passes give "not scored".

## The rules (frozen in `predictions-e116.json`)

The unit of replication is a pass. Intervals: 95%, t(0.975, n − 1) over kept passes, paired within a pass.
**At least 4 kept passes** (E88's minimum), or S, W, H, P and T are not scored and the numbers are reported as
exploratory.

| rule | what | PASS | FAIL | otherwise |
|---|---|---|---|---|
| **E116-R0** | the read-back: 22 reads, each equal to accum.c's 256 words on all 1,024 minions | 22 of 22 equal | any read differs anywhere | fewer than 22 reads: not scored |
| **E116-S** (per format) | the three shares of D(`r_walk`), per pass, against E88's card-1 shares | all three within ±0.04 (fp32, fp16) or ±0.08 (int8) | any part outside its band by more than its 95% half-width | INCONCLUSIVE |
| **E116-W** (per format) | the three parts' watts against E88's × E82's card scale (fp32 8.160 / 8.873 / 5.193 W; fp16 8.219 / 6.396 / 6.497; int8 1.757 / 3.230 / 1.858) | all three within max(0.6 W, 12%) | any part's interval wholly outside its band | INCONCLUSIVE |
| **E116-H** | E88's 13 mechanism rules (H1–H6) by `score_e88.py`, against E88's card-1 verdicts | 13 of 13 the same | 2 or more differ | one differs: INCONCLUSIVE |
| **E116-P** | E88's 19 frozen model bands by `score_e88.py` (card 1's bands, unscaled) | reported: the tally and each verdict beside card 1's | | |
| **E116-T** | the session tie: `fp32.randn`, `fp16.randn`, `int8.full` against E78 on aifoundry3 (24.725, 22.162, 7.056 W) | each within max(0.4 W, 3%) | any interval wholly outside | INCONCLUSIVE |

Reported beside the rules (no verdict): the parts as shares of each format's random anchor (E88's C1 form, with the
part the split does not place); the parts on every arm; the sign pair M32s (`s_abs` − `c_abs`) and R32s against E88's
card-1 values × 1.030 and against E92's `s_abs` − `c_abs` on aifoundry3 (2.377 ± 0.556 W, 2.520 ± 0.171 with dips
removed); the minion rail; pJ per MAC through the measured rate.

**What I expect, frozen:** R0 PASS (the arithmetic is digital, and the same chip); S PASS in all three formats; W PASS
in all three; H PASS, 13 of 13, with H4's first half failing again as on card 1 (`s_abs` − `c_abs` about 2.6 W against
its registered ≤ 1.0 W); P 18 of 19 — P-M32s fails as on card 1, and P-R32s, which missed its band by 0.003 W there,
passes once the 3% card scale lifts it; T PASS.

## Card budget and claim

At most 40 card-minutes: the opening config read and the read-back (about 2 min), the smoke (about 1 min), the queue
(at most 34 min; E88's passes took about 6 min each on card 1, so about five passes), the closing read. The claim in
`#community-lab`, one line, posted after this commit is pushed and before the first launch:
`<ai> **Claude says:** using aifoundry3 for 1 h, until ~HH:MM PST [doc](<https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers>)`,
edited at the release to append ` — released`. Before the claim: `#community-lab` read for any open aifoundry3 claim, and
et-who.

## Known in advance

- **Binaries:** aifoundry3's own build of the same host source (`build/sparsity/host/sparsity_host`, sha256 `20e760c2…`,
  the binary E78 and E113 ran there; kernel `sparsity.elf` `d521e432…`), not card 1's. The read-back host
  (`build/e116/b/host/sparsity_host`, `92d15e46…`) was built on aifoundry3 at 16:41 PST from the same `main.cpp`
  (`0f53a7d5…`) with E104's patch, before this registration; it opens no device until the session.
- **The other users' idle logins** on aifoundry3 (since 26 Oct) do not block, by E60's departure D1 as block_e88.sh
  carries it; nothing of theirs is named in any file.
- **Leakage:** E88's arms (0.545, 0.3803, 0) are card 1's and E71's slopes; the primary fits its own (`auto`).

## Files

`README.md` (this), `predictions-e116.json` (references, bands, expectations, harness sha256), `expect-e116.json`
(accum.c's words per tile), `make_predictions_e116.py`, `build_host_e116.sh`, `readback_e116.py`,
`block_readback_e116.sh`, `setup_e116.sh` (checks and dry runs, no device), `session_e116.sh`, `score_e116.py`,
`selftest_e116.py`, `selftest_e116.txt`, `collect_e116.sh`. Reused unchanged: `tools/claims-v3/rpath/` (E88), `kinds/run_e78.py`,
`kinds/reduce_e78.py`, `kinds/e78_common.py`, `kinds/kinds.json`, `kinds/patch_host_e104.py`, `lib.sh`.
