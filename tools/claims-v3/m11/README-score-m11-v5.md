# M11's scorer v5 (E185's kit, Sat 7 Nov 2026): v4 unchanged, plus A10's reading as the primary and E185's rules

*Desk only, on the Intel, before any E185 datum. [`score_m11.py`](score_m11.py), v2, v3 and [`score_m11_v4.py`](score_m11_v4.py) stay as committed;
[`score_m11_v5.py`](score_m11_v5.py) imports v4 unchanged, and every reading v4 makes is printed by v5 unchanged (its self-test checks this on
E181's committed score). It carries M11's amendment A10 ([`REGISTRATION.md.dated-note-A10.md`](REGISTRATION.md.dated-note-A10.md), `5e708747`) and
E185's registration ([`../e185/E185.md`](../e185/E185.md), `98fe28b7`) section 6, for the kinds page's
[section 11](https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers#11-what-is-still-open), items 9 and 8. E185's step 22
(`../e185/rb/s22_collect_e185.sh`) runs it through `../e185/score_e185.sh`, only after every gate.*

## Builds on

1. **Checked.** The prior-work inventory (Q145's stock-take, private scratch), read Sat 7 Nov 2026 at about 20:00 PST: public rows H14, H19 and
   H25 (opaque pointers).
2. **Used.**
   - **M11's scorer v4** (`dc35a540`), imported unchanged: its score (stages 1-6 of the lines file), its arm contexts (`arm_contexts`), and
     v2's staged reader and decision code (`_context`, `_read`, `_a2_line`, `_a4_line`, `_session_dict`, `decide_card_kind`), all unchanged.
   - **A10** (`5e708747`): the two-pass reading is M11's from E185 on; a session A9-1 refuses is read on the measured pass alone, named.
   - **E185's registration** (`98fe28b7`): `arms_e185.py`'s readers (`load`, `read_holds`, `rail_rows`) unchanged, and the frozen two-pass
     gains of `arms-e185-train.json` (G_B 1.02678, G_Rl 1.19380).
   - *The same quantities, earlier:* on E176 and E181 v5's printed v4 readings equal E181's committed `scored-m11.json`; v5's A10 readings
     equal its committed A9 arm's, decision by decision; E185's readers on E181's holds give `arms-e185-e181.json`'s two-pass held-out misses
     (difference 0.0 °C).
3. **Not used.** An aifoundry2 reader (none is built); anything of the NDA tier.
4. **Tiers.** Public tier only. No NDA-tier check is used, so there is no sha256 line.

## What v5 adds

| item | what |
|---|---|
| A10 | every session that passed its start gate read on A10's reading (the arm's session where A9-1 reads it, else the measured pass alone, named), staged as the lines file's stages 7-9 (A4-8's form), then the registered decision code on those points: `A10` › `readings`. v4's registered readings are printed beside under `measured_pass_alone_reported (A10)` |
| E185 | on the pass `--e185` names: every hold on A10's reading with the three arms (F, B, Rl), the frozen gains, the cool-down misses over [b + 120, b + 360) s and the rail share; E185-RF, -BF, -RB and -BEST (τ = 0.0884 / √n; SCORED only with 4 or more holds all three arms score, a fp32.randn and an int8.neg_ones hold among them); E185-C per arm (n_c ≥ 3); the per-kind means; H_E2's \|e\| / R; the one-pass arms beside; the precedence of A10 and E185's registration over the pass's first launch record |
| rail rows | a hold whose rail readings miss its anchor or plateau window (under 5 readable rows a second) is not scored for Rl, and leaves the three-arm rules |

## The self-test ([`selftest-score-m11-v5.txt`](selftest-score-m11-v5.txt), `.json`): 14 of 14 PASS

- **V1-V3:** on E176 and E181 (committed, with E181's smoke named), v4's readings equal E181's committed score; A10's readings equal its
  committed A9 arm's readings, decision by decision; the lines file holds stages 1-9 and no staging file is left.
- **V4-V6:** E185's readers on E181's five holds give the registration's two-pass held-out misses (max difference 0.0 °C) and rms (F 0.2963, B
  0.2312, Rl 0.1978 °C); on E181 the rules read (held out, labelled so) RF BETTER, BF BETTER, RB NOT RESOLVED, BEST NOT SEPARATED (B, Rl),
  E185-C NOT SCORED (two big holds with a cool-down window); the reading is labelled post hoc for A10 and E185's registration, both
  committed after E181's first launch.
- **V7-V11 (synthetic holds):** R at arm F's, B's or Rl's P reads BEST F, B or Rl; a cool-down 0.10 °C under the plateau reads THE SHAPE MISSES
  (cooler), one equal to it THE SHAPE HOLDS; no int8.neg_ones hold, or its rail rows missing, reads NOT SCORED.
- **V12:** with no smoke named, A10-3 reads E181 on the measured pass alone, named, and its HM-LG is the registered one.

These are checks of the code on committed and synthetic data, never a reading of a session.

    /usr/bin/python3 -B tools/claims-v3/m11/score_m11_v5.py --self-test --workdir <a new scratch dir> --json <out>

SPDX-License-Identifier: Apache-2.0
