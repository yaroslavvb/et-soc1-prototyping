# M11's scorer v3, dated note 1 (Fri 6 Nov 2026, before any E181 datum): its Builds on block, and the fault that v4 fixes

*Beside [`README-score-m11-v3.md`](README-score-m11-v3.md) (`33cdccf6`), which stays as committed. Written on the Intel, desk only, by the lane
fix-e181 of E181's kit round, for the E181 kit verifier's faults 9 and 4 (verify-e181, Fri 6 Nov 2026).*

## Builds on (the block v3's README opened without; section 45's rule)

1. **Checked.** The prior-work inventory (Q145's stock-take, private scratch), read Fri 6 Nov 2026 about 01:30 PST by the kit lane: public rows
   H07, H08, H12, H14, H24, H25 and L10, as E181's kit README (`33cdccf6`) lists them.
2. **Used.** M11's scorer v2 (`ebdbb35c`), imported unchanged; M11's A6 (`95c75047`), A7 (`65a93fbb`) and A8 (`80b92990`), read by its
   precedence and its gate reading; the footing law's FL1 (`c14e5f35`) and its dated note 1 (N1, `65a93fbb`), read by its FL5(c); E97's
   committed rests (`docs/reports/data/2026-11-01-e97-heat-low-power-steady/`) for FL5(c)'s check against N1's committed dry run (0.3196 against
   0.3106 W/°C, the same to the digit); E154's (`d037d82a`) and E176's (`5db7bcf7`) committed passes for its self-test. These were all named in
   E181's kit README's block, which covered v3 as a file of the kit.
3. **Not used.** An aifoundry2 reader (E177 is not built); anything of the NDA tier.
4. **Tiers.** Public tier only; no NDA-tier check, so no sha256 line.

## The fault v4 fixes

v3's `score()` calls v2's `score()`, which writes all three stages of the lines file, before v3's own check of the `start_gate` marks; so a
score v3 refuses leaves `scored-m11-lines.jsonl` in the data directory (the self-test's S-LIE workdir holds it). **Use M11's scorer v4**
([`score_m11_v4.py`](score_m11_v4.py), [`README-score-m11-v4.md`](README-score-m11-v4.md)): it reads every mark before anything is written,
and stages the lines file under a name it renames only after the whole score has succeeded. E181's runbook reaches v4 through
`../e181/score_e181_v2.sh` and step 22 v2 (E181's kit `README.md.dated-note-1.md`).

SPDX-License-Identifier: Apache-2.0
