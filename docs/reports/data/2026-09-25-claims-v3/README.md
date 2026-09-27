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
| `AMENDMENTS.md` | Added after this record: amendments A1–A5, each committed before the data it touches (A2 added aifoundry1's card 1, A4 excluded its card 0), the implementation notes, and the post-data notes C1 and C2. |
| `raw/<card>/<exp>/p<N>/` | Added after the runs: every block of the three cards (aifoundry2, aifoundry3, aifoundry1-c1), as `tools/claims-v3/collect.sh` gathered them, with `queue-state.jsonl` per card. |
| `results/` | Added after the runs: `<exp>.json` and `<exp>.log` per experiment from `tools/claims-v3/reduce_all.sh`, each item with its registered and all-cards outcome; `pagemap.json` and `pagemap.md`, every page claim with the items that test it; `gs.json` and `gs-full.json`, the gathers and scatters that followed (E48). |

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

**How it went** (added 27 September). The campaign ran unattended on aifoundry2, aifoundry3 and aifoundry1's card 1
from 25 September 17:23 to 26 September 06:53 and was complete at 06:55: 197 blocks, three of them failed and run
again. V3-COOL was not scheduled and V3-LONG (E47) not run (D1). The experiments are registered as E35–E47 in
[`docs/findings/03-experiments.md`](../../../findings/03-experiments.md), their values in
[`05-claims.md`](../../../findings/05-claims.md), "Version 3: the three-card check"; the pages carry the results since
26 September. The gathers and scatters (E48) ran on each of the three cards once its campaign queue had ended, 26 September
03:19–09:22.
