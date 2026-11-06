# The bench's dated note 1: its register files are the open RTL's, not the silicon's (Fri 6 Nov 2026, week 45; written about 03:49 PST)

*A dated note beside [`README.md`](README.md). It changes nothing in the bench, its counts or any figure computed from them. It records
a public fact about what the bench can see. It was owed since Q145's stock-take, and
[term S's dated note 2](../../tools/claims-v3/m10-s/REGISTRATION.md.dated-note-2.md) (item 6 (d)) names it.*

**What the bench simulates.** It simulates core-et's open RTL (`external/core-et` at `b38a1a31`). It instantiates `vpu_top` whole, and
`vpu_top` holds all eight `vpu_lane`s with their register files (README, "What it is"). So the toggles the bench counts include the
register files as the open RTL writes them:
- `vpu_64x32_3r2w_vpurf`, the vector register file of each lane. `tb_vpu.sv` writes C into it through a back door, lines 80-83;
- `vpu_tensorb_rf` (`rtl/shire/minion/vpu/vpu_tensorb_rf.v`);
- `rf_latch_1r_1w` (`rtl/libs/rf_latches/`).

All three appear in the committed counts files, for example
`docs/reports/data/2026-11-01-q132-rtl-bench/counts-hl.json`.

**What the silicon has instead.** Ditzel's "Esperanto Retrospective" (Cool Chips Hot Takes, 25 August 2026, as AI Foundry's blog
publishes its slides) has a side note on slide 12. It says that the ET-SoC-1 silicon's timing bug, which cut its clock rate in half,
came from integrating a **full-custom register file**: "We were too tricky trying to integrate full custom register file, so this won't
affect open sourced RTL." So the silicon's register file is a full-custom design that the open-sourced RTL does not carry.

**What follows for this bench.** The bench's register-file toggles, and any price fitted on them, describe the open RTL's register files,
not the silicon's.
- If the silicon's full-custom cells spend more or less per toggled bit than a fitted price says, the bench cannot see it. That holds by
  construction, not by measurement.
- Term S's registration (`tools/claims-v3/m10-s/REGISTRATION.md` § 1) cites this as the public reason the bench may be blind to single
  high B bits. E178 (§ 4 and § 11) cites the same slide.
- **What the slide does not say:** which of the chip's register files is full custom, or how its energy per toggled bit compares with the
  open RTL's.

SPDX-License-Identifier: Apache-2.0
