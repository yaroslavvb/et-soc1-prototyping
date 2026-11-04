# Dated note on E156's registration `README.md` (Tue 3 Nov 2026, week 45, E156's corrections after verification)

Written beside the registration and not inside it. [`README.md`](README.md) is E156's frozen registration (`d55744a5`), so its bytes stay as
registered.

- **Its first line gives the wrong time.** It says "Pre-registered Tue 3 Nov 2026 (week 45), about 05:55 PST".
  - `d55744a5` was committed at **05:46:30 PST** (`git show -s d55744a5`) and pushed at **05:46:34 PST** (GitHub's record of the push, 13:46:34
    UTC).
  - Both precede the claim (05:47:41-05:47:55 PST), the first device open (05:48:01, the opening `ettelem config`) and the first launch (a
    heater burn-in at 05:48:24, `passes/p15601/marks.jsonl` in the data dir).
  - So the order the registration states holds: frozen before the card post named aifoundry1 card 1 and before the first launch. Only the
    clock time is wrong.
- **N1 reads the critic's rule as price × count.** The registration quotes rank 15 exactly: "the frozen +0.185 W per image predicts within
  0.05 W". It calls N1 "the critic's rule", but N1 applies the 0.05 W line to E139's frozen price × each image's count × the line rate (+0.152 W
  for `E7`, 0 for `E32`), not to a fixed +0.185 W per image. That was registered before any pass, and it stays. Read literally, both new images
  would fail (−0.068 and −0.215 W), and E139's own images would pass (+0.014, −0.016 W).
- **Its item 5, Budget and gates, projected six headline passes** ("about seven passes (the warm-up and six headline)"). Nine ran, as the queue's registered
  rule allowed: three more, not the two the data README's D1 first said.

The corrections are in the data README,
[§ Corrections after verification](../../../docs/reports/data/2026-11-03-e156-memory-images-card1/README.md#corrections-after-verification-tue-3-nov-2026)
(C4, C7), with their numbers in that dir's `posthoc/corrections.txt`.
