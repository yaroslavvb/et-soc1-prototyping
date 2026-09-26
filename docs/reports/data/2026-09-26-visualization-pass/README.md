# The visualization pass (26 September 2026)

The owner asked for another look through the published pages for "compelling visualizations or interactive
elements". `plan.md` is the survey (25 Sep, late): what each of the 19 measurement pages already had, one to three
opportunities per page with verified data paths, and a ranked top 12. It was written before the pass and is kept as
written.

What was built (commits `be72084`–`7f0e7d2` on the `pages-v3` branch, merged into main):

- **The toolkit** (`docs/reports/sources/chartkit.js`): a card registry (one colour, mark and label per card:
  aifoundry2 `--c1` dot, aifoundry3 `--c2` ring, aifoundry1-c1 `--c3` diamond; `CK.cardSeg` keeps every card
  selector on a page in step; `CK.pick` reads `{mean, se, n, per_card}` and never draws a missing card as zero) and
  `CK.sortTable` (sortable, filterable tables with `aria-sort`).
- **Every new chart takes its cards from the data**, so the version-3 campaign's third card (aifoundry1-c1) shows up
  when the data is regenerated, with no code change. Each page was also built from a scratch copy of its data with a
  fake third card to prove it (the fake data was never committed).
- Top-12 items 1–12 of `plan.md` were all built:
  1. DVFS: every idle session's offset from the law, per card.
  2. Energy manual: one card selector for the page, driving the workload calculator (which now names whose numbers
     it prices with) and a compare-cards view; the registry's colours on the idle and SRAM charts.
  3. Hub: a claim-status scoreboard per page (before the campaign; the after-campaign status slots in as a second
     series); the session map's lanes and the power scatter's card choice now come from the data.
  4. Heat per mm: per-card views of the distance and contention charts.
  5. On-chip communication: shade the mesh map by any of four latencies (the memory flag's r² is 0.003).
  6. On-chip relay: the stages and shires sweeps charted per card (`analyze_onchip.py` adds `by_card` rows).
  7. Why low power: the A100 comparison as a ratio chart.
  8. Ridge points: the A100's roofs over the roofline.
  9. Hot line: a step-through drawing of the starved host shire, sharing N and P with the §3 sliders.
  10. Heat per mm: a route-and-payload calculator (its default route reproduces the §8 prose).
  11. Memory anatomy: a physical-address decoder.
  12. Memory hierarchy: energy per byte by level, per card (`analyze.py --embed` adds `energy_levels`).
- Also: the hot line's energy per operation charted, busy drift per card on the power page, and sortable tables on
  the long data tables of nine pages.

**Checks.** Every page passes `docs/reports/data/2026-09-24-report-review/tools/check_page.sh` at 1280 and 390 px in
light and dark (no JS errors, no text under 11 px, no low-contrast text, every chart keyboard-reachable), and a
sentence diff of each page's static text against the version before the pass found no prose removed.

**Caught in review.** The first ratio chart on Why low power computed energy per FLOP as ET ÷ A100 while every other
bar was A100 ÷ ET, so it showed the ET card "ahead" on energy per FLOP, the opposite of the page's own table
(1.3 pJ against 7.0 pJ). It was fixed before publishing, and the chart no longer names a "winner": it shows which
chip's value is the larger, coloured by kind (size, power, throughput, energy per FLOP).
