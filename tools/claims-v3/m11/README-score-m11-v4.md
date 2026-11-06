# M11's scorer v4 (E181's kit fix, Fri 6 Nov 2026): v3 unchanged, plus nothing written before the gates, A9's reported arm, A6-5's host readings and A6-3's pattern edge

*Desk only, on the Intel, before any E181 datum. [`score_m11.py`](score_m11.py) (`03582d2f`), [`score_m11_v2.py`](score_m11_v2.py) (`ebdbb35c`)
and [`score_m11_v3.py`](score_m11_v3.py) (`33cdccf6`) stay as committed; [`score_m11_v4.py`](score_m11_v4.py) imports v3 unchanged, and every
registered reading and decision v3 makes is v4's, unchanged (its self-test checks this). It answers the E181 kit verifier's faults 1, 3, 4 and
8 (verify-e181, Fri 6 Nov 2026), with M11's amendment A9 ([`REGISTRATION.md.dated-note-A9.md`](REGISTRATION.md.dated-note-A9.md),
`cd5bed77`), for the kinds page's [section 11](https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers#11-what-is-still-open), items 9
and 8. E181's step 22 v2 (`../e181/rb/s22_collect_e181_v2.sh`) runs it through `../e181/score_e181_v2.sh`, only after every gate.*

## Builds on

1. **Checked.** The prior-work inventory (Q145's stock-take, private scratch), read Fri 6 Nov 2026 about 03:10 PST: public rows H14, H19 and
   H25 (opaque pointers).
2. **Used.**
   - **M11's scorers v1-v3** (`03582d2f`, `ebdbb35c`, `33cdccf6`), imported unchanged: v2's staged reader and its lines functions
     (`_order_from_records`, `_read`, `_a2_line`, `_a4_line`, `_session_dict`) and decision code (`decide_card_kind`); v3's `gate_reading`.
   - **A9's arm** (`a9_posthoc.two_pass`, `cd5bed77`), imported unchanged, on Q138(t)'s chain as Q139(e) froze it (the inventory's H14).
   - **E154's committed session** (`d037d82a`, its holds renamed to M11's by v2's own stand-in) and its smoke pass (`p15401`), and **E176's
     committed passes** (`5db7bcf7`), for the self-test (the inventory's H19 and H25). *The same quantity earlier:* the arm's shift of H_E on
     E154's renamed pass is +0.131 °C, A9's post hoc +0.131 °C for E154's H_M by Q138(t)'s own reader.
   - **E176's lane's host windows** (`room-rule/hostwin-*.out`, `5db7bcf7`): the form of A6-5's host readings.
3. **Not used.** An aifoundry2 reader (E177 is not built); anything of the NDA tier.
4. **Tiers.** Public tier only. No NDA-tier check is used, so there is no sha256 line.

## What v4 adds

| item | from | what |
|---|---|---|
| W | the verifier's fault 4 | every pass's `start_gate` mark read by v3's `gate_reading` **before anything is read or written**: a mark that disagrees with its own numbers refuses with no file written. The lines file is written as `<lines>.staging` (v2's three stages, each appended and fsync'd before the next stage reads anything, as A4-8 asks; then the arm's three) and renamed to its own name only after the whole score has succeeded; a refusal or an error removes it. So a refused score leaves no scored file |
| A9 | the verifier's fault 1; A9 (`cd5bed77`) | the reported arm: each session that passed its gate and names its smoke (`--smoke`) read again with the chain over both passes; per hold e_2p and its shift (R the registered R exactly, or the arm refuses itself); the registered decision code, unchanged, on the arm's points, so HM-E144, HM-HE and HM-CAL are printed under `arm_A9`; the arm's own lines staged (stages 4-6). Never a verdict, an entry or what M11 carries (A9-3) |
| H | the verifier's fault 3; A6-5 | the host windows of E181's step 12 (`logs/host-start.out`, `logs/host-end.out`, `--host`): the NVMe composite and the coretemp 2-9 mean at the session's start and end, and their change. Reported, never a gate |
| E | the verifier's fault 8 | `A6_3_pattern_edge`: a session whose start gate passed while its room mark carries no H_E pattern (a room in (53.9, 53.9 + 10⁻⁹] °C: `run_e181.py` reads the room line with its 10⁻⁹ °C tolerance and A6-3's pattern without it) is flagged, so a record names it. No reading changes |
| P | A9 | the blind precedence counts A9 beside the registration and A1-A8 |

## The self-test ([`selftest-score-m11-v4.txt`](selftest-score-m11-v4.txt), `.json`; 75 s): 12 of 12 PASS

- **W1-W3:** a lying mark refused before any file (no lines file, no staging file); a refusal after v2's stages leaves no file; a passing
  session's lines file holds stages 1-6 under its own name, no staging file left.
- **A1-A4:** every registered reading is v3's on the same pass; the arm on E154's pass with its smoke reads SCORED, R the registered R in all
  five holds, H_E's shift +0.131 °C (A9's post hoc), the later holds' under 0.001 °C; with no smoke named, or a smoke a day away, the arm reads
  NOT SCORED with its reason and the registered readings are v3's; E176's pass beside it is excluded and the arm is not read there.
- **H1, E1, P1, L1:** the host windows parsed (the change 1.0 and 1.5 °C on synthetic windows); the pattern edge flagged, and not for a
  pattern or a refused gate; the precedence counts A9 (a launch now reads blind, one second before A9's commit post hoc); v4's two lists read
  before any import.

These are checks of the code on seen and synthetic data, never a reading of a session.

    /usr/bin/python3 -B tools/claims-v3/m11/score_m11_v4.py --self-test --workdir <a new scratch dir> --json <out>

SPDX-License-Identifier: Apache-2.0
