# Dated note on E157's registration `README.md` (Tue 3 Nov 2026, week 45, E157's corrections after verification)

Written beside the registration and not inside it. [`README.md`](README.md) is E157's frozen registration (`01676499`, committed and pushed
at 16:17:57 PST), so its bytes stay as registered. Nothing here changes a rule, a prediction, a reduction or a verdict.

- **§ Device commands sent says "Card 1 runs release 1.4.0 (BL2 0.22.0; E156's session read it this morning)".** Nobody read card 1's build
  on 3 Nov.
  - The build named is the one card 1 has reported since 31 Oct 2026: release 1.4.0, BL1 and BL2 0.22.0, PMIC 1.3.0, minions 0.25.1. It
    was read by E82 at 13:45:24 PDT that day (`docs/reports/data/2026-10-31-e82-kinds-aifoundry1/ident/firmware_pre.txt`, its A1), and E129's
    dated note C1 and `AGENT.md`'s card table carry it.
  - E156's registration cites that record, not a read of its own (`tools/claims-v3/e156/README.md`, § Device commands sent).
  - A read on the day would have taken the firmware-revisions query, which writes the PMIC's firmware-management command register and is not
    allowed under the owner's rules of 2 November 2026. Neither E156 nor E157 sent it.
  - Nothing in these rounds resets or flashes a card, so the classification at et-platform `836a4ab` (BL2 0.22.0) stands, every command a
    READ.
- **The C reference's domain bullet says the 36 first-read tiles' launches "are the first silicon read of their value range".** For 30 of
  the 36 they were not.
  - E160 had launched those 30 on aifoundry2 at 06:41:50–07:12:39 PST with every launch's C logged. Its check, 2,620 of 2,620 launches
    bit-exact, was committed in `6a330635` at 16:31:18 PST, during E157's session.
  - E157's launches are the first checked reads of those ranges on card 1. They are the first anywhere only for the six E160 did not run
    (K1's five pool-5 tiles and `fp32.anchor6_randn`), beside E153's on aifoundry3 the same evening.
  - What the bullet registers is unaffected: a FAIL on a first-read tile could be the reference's, and PC counts it as not checked. No
    launch failed.

The corrections are in the data README,
[§ Corrections after verification](../../../docs/reports/data/2026-11-03-e157-blind6-card1/README.md#corrections-after-verification-tue-3-nov-2026)
(C2, C3), with their numbers in that dir's `posthoc/corrections.txt`.
