# Version 3 of the claims check: proven effects only, both cards (25 September 2026)

On 2026-09-25 the repo owner asked for "another check (version 3) on the claims in the report, making sure to test
them on both machines, not just one, and remove things possibly caused by randomness", narrowed "to effects that can
be proven, doing a full sweep". This directory is the record. It is committed **before the first card run**, so the
predictions it holds predate the data that will test them.

| File | What it is |
|---|---|
| `PLAN3.md` | The plan. §1: every claim on the 18 pages (1,372) with its verdict under the standard below, and what each page does now (drop, qualify, per-card values, one card). §2: 13 experiments that test the rest on both cards, each with pre-registered predictions and decision rules. §3: the code needed. §4: the owner's decisions. §5: risks. |
| `plan3.json.gz` | The same as data: claims, experiments with their predictions, schedule, decisions. |
| `inventory/<group>.verified.json.gz` | The 11 page groups' claim inventories after an independent skeptic recomputed them: for each claim, the data, the cards, n, the effect, the noise, the test and the verdict. |
| `firmware.md` | The firmware on both cards (queried read-only on 25 Sep), its place in the et-platform history (about mid-May 2024), and how the governor in that build differs from the December 2025 source the findings read. |

**The standard.** The unit of replication is an independent repeat (a pass, a session, a card), never samples or
launches inside one burst. A claim is *proven* when it holds on each card with at least three independent repeats
(a 99% interval that excludes the null, or a deterministic value identical in every run) and the cards agree in
sign; the magnitude either agrees or is stated per card. Picking the best of many configurations is corrected for.
A prediction for a new run is written here before the run; a failed prediction is reported as failed, and the page
takes the measured value.

**Owner decisions** (PLAN3 §4; taken with the plan's recommendations, the owner having asked for the sweep to
proceed): D1, the 10 s device-hold rule stands, so the Horace long runs are labelled one card, one session; D2, the
Horace speed effect (a cool-die result that only aifoundry2 can show) leaves the lede and is labelled with its n;
D3, the idle law's leakage split is given as a range, led by the measured slope; D4, the MUST experiments run first,
then the SHOULD ones; D5, this record is committed before the runs.

sha256 of the working copies committed here: `plan3.json` 3677aba155a527002bebb5e56c0302906d705e7b7e1ddcf6c61a4f2270e95327,
`PLAN3.md` 1793e772a6196ff38b035c7643746b6b355624a2fb3811577edd76ae9a805c71.
