# Dated note 1 beside fw-q147's README (Thu 5 Nov 2026, about 23:35 PST, the same lane, before any verifier)

Two wordings in [`README.md`](README.md) (committed in `8060a8f5`, 23:25:41 PST) say more than their cited sources do. The text there
is left as committed; read it with these corrections. No number, verdict or file changes.

1. **Section 4, "Signatures":** "Three cards are recorded as running the maintainer's rebuilt images since 7-10 Oct (aifoundry3, E89;
   aifoundry2, E69; aifoundry1 card 0, E118's record)". As the sources word it: aifoundry3 runs the thermal build flashed on
   7 Oct that E89's registration calls "Roman's patch 0003" ([`../e89/E89.md`](../e89/E89.md) line 27); aifoundry1 card 0's image is
   "recorded in the maintainer's field manual as a thermal build on `836a4ab`" ([`../e118/CHANGE-RECORD.md`](../e118/CHANGE-RECORD.md),
   § Rule 8); aifoundry2's record names "the 10 Oct thermal-v2 update" without saying who made it
   ([E69's README](../../../docs/reports/data/2026-10-27-e69-governor-knob/README.md) line 212); card 1 reads BL2 0.22.0 where 0.18.0
   was on record (E82 A1). So the public record shows rebuilt, non-public 0.22.0 images booting on these cards, two of them named as
   the maintainer's; it does not by itself say who built aifoundry2's or card 1's. The conclusion it supports is unchanged: a
   signed vendor image is not the barrier E4 described on 20 Sep 2026; the update path and the reset are.
2. **Results first, item 2:** "no independent recovery path exists on the lab's cards". As E72's and E118's change records word
   it: no PMIC console, probe or programmer route **is established** for the lab's cards
   ([`../lq6/CHANGE-RECORD.md`](../lq6/CHANGE-RECORD.md), "Restore before risk"). Gate G1 needs one proved before any risk, so the
   gate reads FAIL either way.

Also checked for this note, and holding as written: the open RTL's zero gate masks the per-lane TensorFMA valids
(`ex_fma_gate_mask` into `ex_txfma_valid`, core-et `b38a1a3` `rtl/shire/minion/vpu/vpu_ctrl.v:837-839`), while the counter events
come from the instruction's control valid chain (`ex_ctrl_valid_qual` through `f8_ctrl_valid_qual`, `:772`, `:1565-1570`,
`:1681-1699`), so section 1's "the zero gate acts on the lanes below that" stands.
