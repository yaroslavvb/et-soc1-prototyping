# The review of the heat-per-millimetre report (24 September 2026)

Before the report was published, a six-agent workflow (`workflow.js`) re-derived its numbers and tried to refute
its claims: two independent re-analyses of the raw bursts ([A] `indep/`, a tail-window reduction; [B] `methodB/`,
an explicit model of the service processor's filter with Theil–Sen fits), three skeptics (measurement artifacts
`artifacts/`, physics and interpretation `physics/`, arithmetic, units and sources `arith/`), and a synthesis
(`combine/`, `VERDICT.md`). Nothing ran on the cards. `workflow-result.json` holds every agent's structured return.

The scripts were run from a scratch directory against the uncompressed raw files; to re-run them, gunzip
`../../2026-09-24-wire*-aifoundry*/{telemetry,runs}.jsonl.gz` in place and adjust the paths at the top of each.

**Verdict: publish after corrections.** The measurements reproduced: three independent reductions agree with the
pipeline within 1–3% on the mesh rail and about 7% on board power. What failed were sentences built on the numbers.

## What was applied

Every correction in `VERDICT.md`, items 1–11 and the minor ones, is on the page, with these changes of form:

- **Numbers come from the pipeline, not from the verdict's text.** `workloads/enercat/analyze_wire.py` now computes
  what the corrections needed (`wire.json` → `checks`: link sharing per configuration from the recorded
  reader>target maps, readers, per-reader bandwidth, the four-hop point off the line, the exit step, the 256 B
  excess; `sensitivity`: the model refitted without the leakage correction), and the page's sentences are filled
  from `wire.json` by `heat-per-mm.script.js`.
- **The free-link headline uses 1–4 hops** (`wsep_d1_4`), the same distances as the loaded set:
  mesh rail 24.6 + 11.7 = 36.2 fJ/mm, board 32.7 + 14.0 = 46.7 (`tools/ettelem/build_wire_report.py`).
- **The hop range is 3.64–3.74 mm**; the literature entries carry the corrected quotes (AHA 2023 "~0.5V",
  CACM 2020's 14 nm paragraph, VLSI 2018 "in present day chips"); only mesh-rail numbers are V²-scaled.
- **Repository fixes:** `analyze_wire.py` labels the six aifoundry2 bursts "service processor starved" (it checks
  the meter's latency before the sample count); `research/lit/first-principles-estimate.md` is now the estimate
  (it was a copy of OpenROAD's manual); `research/SYNTHESIS.md` and its README say its measured numbers are superseded.

## Where the pipeline's checks differ from the verdict's numbers

| Verdict | Pipeline (`wire.json`) | On the page |
|---|---|---|
| All ones costs 5–9% more per hop than random | slope ratio over 1–6 hops: 7–9% (both meters) | 7–9% |
| Without the leakage correction the board coefficients are 4–7% higher in v2, up to 16% for v1's *a* | `sensitivity.no_leak_correction`: 4–9% (v2 *a* 160 against 151; v1 *a* 151 against 139) | 4–9%, and the reviewers' 3%/7% agreement quoted as theirs |
| The 256 B excess is the same fraction of a full flip at 1, 3 and 6 hops (0.52, 0.48, 0.53 on the mesh rail) | per-hop increments of the excess: 0.35 pJ/B from 1 to 3 hops, 0.45 from 3 to 6 (mesh rail); 0.46 and 0.94 on board power | "does not fall as more of the links are shared", with the increments |
| Board watts per mesh-rail watt rise with load, 1.22–1.27 at 1–2 hops to 1.36–1.37 at 4–6, so board contrasts are ~10% inflated | not reproduced under three definitions: (E(d) − E(0)) ratio 1.98 → 1.58; board over all three rails 1.04 → 1.17; per-distance regression across *P* 3.5 → 1.8 | kept qualitative: "part of it is the regulator's loss, which grows with load" |
| aifoundry3's y-only three-hop readings up to 0.55 s | 0.50 s inside the analysed window (the first 0.5 s of a burst is excluded) | 0.5 s |
