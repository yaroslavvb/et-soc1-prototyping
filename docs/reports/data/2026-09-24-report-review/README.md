# The 24 and 25 September 2026 reviews of the measurement reports

On 2026-09-24 the repo owner asked for every document the observability hub links
(<https://spacesheep.dev/@yaroslavvb/et-soc1-limits-of-observability>) to be checked for consistency, correct
cross-links, suspicious claims and readability. On 2026-09-25 the owner asked for a second, full validation of the
18 public pages: re-run the scripts, recheck the claims, remove redundancy, reorganise where needed and add
interactive visualisations. This directory is the record of both. The knowledge base summarises each in
[`docs/findings/04-artifacts.md`](../../../findings/04-artifacts.md) ("The 24 September review", "The 25 September
validation").

| File | What it is |
|---|---|
| `PLAN.md` | The 24 September fix plan: the overall assessment, the canonical value for every quantity stated on more than one page (D1–D20), the cross-linking scheme (X1–X5), conventions (C1–C7), the glossary text, the change list per page, the refuted and rejected findings, and the owner's open questions with how they were decided (the decisions are in the commit message of `49dd0c8` and below). A dated record: the 25 September validation added only notes, marked "Note (25 Sep)", under D2, D3, D4, D8 and D10–D13, and an erratum under D20. |
| `findings-verified.json.gz` | Every reviewer finding of 24 September (19 pages plus the knowledge base, a cross-page numbers ledger and a navigation review) with the independent verifier's verdict: 288 confirmed, 144 with a corrected fix, 2 refuted, plus 42 the verifiers found. Findings about a private memo are omitted. |
| `fix-results.json.gz`, `round2-results.json.gz` | What each page owner applied or skipped in the three fix passes of 24 September, the independent check-and-repair verdicts, and the final reviewers' remaining issues. |
| `PLAN2.md` | The 25 September plan: what the reproduction runs found (§1), the set-level decisions (§2: updated canonical values D2′, D10′–D13′, D20′, D21, D22 and addenda; the data-pipeline decisions DP-1–DP-12; one canonical home per repeated topic; the reorganisation; the shared chart toolkit and its API; the visualisation standard and portfolio), the work order of every file owner (§3), and what not to change and the questions for the owner (§4). |
| `PLAN2-actions.md.gz` | The verbatim texts PLAN2 refers to by ID (`hub-u-04`, `em-c1`, `M-dvfs-1`, `IA-07`, …, each under a heading `#### <ID>`): the problem, the fix to apply (the verifier's CORRECTED text where there is one), and the verifier's note. |
| `PLAN2-actions.json.gz` | The same texts as data, the source the Markdown was generated from: one key per page group (11), each with the lists `repro_problems` (86 in all: `problem`, `evidence`, `fix`), `findings` (310: `proposal`, the verifier's `verdict`, `verify_reason` and `corrected`), `missed` (44) and `refuted` (3); and `set`, the 23 findings of the structure review (the IA- and VIS- items), not separately verified. Every item has an `id` and a `problem`. |
| `manifest.tsv` | The 19 pages of 24 September: slug, space uuid, repo file. The validation of 25 September covers 18 of them; the private David Kanter notes are out of scope and unlinked. |
| `tools/check_page.sh` | Renders a page at 1280 and 390 px after its scripts run and reports JS errors, empty computed fields, sideways overflow, broken in-page anchors and images, headings without ids, and whether a contents list, a Related reports section and a hub link exist. Since 25 September it installs its error listener right after `<head>`, before any page script, so errors thrown while a page loads are caught (the 24 September version injected it before `</body>`, after the page's script had run, and missed them). `DARK=1` renders with `data-theme="dark"`, `DARK=os` emulates the OS dark preference; an informational `info` line lists SVG text under 11 px, charts or tables that scroll sideways, low-contrast SVG text and how many charts can take keyboard focus; `CHROME_HEADLESS` overrides the browser. |
| `tools/shot.sh` | Full-page screenshots after the scripts run, cut into pieces at most 1,400 px tall so each can be viewed; `DARK=1` or `DARK=os` as above. |
| `tools/render_text.sh`, `tools/final_links.py` | The rendered text and links of a page; the cross-page check of every link and anchor across the set (all 1,240 resolved on 24 September). |
| `tools/deploy_all.sh` | The redeploy: it refuses to overwrite a space whose live page differs from the version the review started from. Pass `--slug` together with `--title` on any update (see 04-artifacts.md, publishing notes). |

The tools need Chrome's headless shell (Playwright's `chrome-headless-shell`, or the browser `CHROME_HEADLESS`
names). `final_links.py` writes its output under `AUDIT_DIR` (default `/tmp/report-review`) and reads the page list
from `AUDIT_DIR/manifest.tsv` if there is one, else from the committed `manifest.tsv` here; `deploy_all.sh` still
reads `AUDIT_DIR`'s manifest and the pre-review live copies saved there.

Owner decisions taken during the 24 September review: the David Kanter notes, a personal memo, were made private
and are no longer linked; the hub now says its scouts and reviewers were AI agents; the L2 mainline-starvation brief
stays, corrected, with an update box pointing to the hot-line report; the unmetered fit is now a committed script
(`tools/ettelem/fit_unmetered.py`); the energy manual keeps its 1–8-hop wire fit with a note on 1–6 hops;
ridge points' energy balance is recomputed from the energy manual; the long idle before E19 is 20.6 hours by the
timestamps.

## The 25 September validation

**How it ran.** A workflow of AI agents ran, for 11 page groups, a local reproduction of every analysis that runs
without a card, a review of the pages, and an independent verification of each finding against the raw data, the
firmware source or the RTL; plus one review of the set's structure. `PLAN2.md` is the result; each file owner then
applied its work order. No lab card was used: nothing was run over ssh, and the simulator checks ran in a sandbox
with a private `/dev`, on a host (aifoundry2) that has a card attached.

**The checker, first (phase 0).** The fixed `check_page.sh` was run on all 18 pages as committed at `08076ae`, at
1280 and 390 px, in light, `data-theme` dark and the OS dark preference: 108 of 108 checks OK, no load-time errors.
Positive control: the DVFS page built from its `dvfs.json` without the `cards` block (175,680 characters) throws
`TypeError: Cannot read properties of undefined (reading 'config')`, which the fixed checker reports; the
24 September checker reported no error there, only the three empty fields (`spcount`, `cardswcap`, `scaletext`).

**The test drive's simulator claim, re-verified (M-msd-1).** `sgemm_host --sysemu -n 64 --shires 0x1 --reps 1
--sim-args -vpurf_warn`, run in a bwrap sandbox with a private `/dev` (no `/dev/et0_*`): PASS, 0 of 4,096
mismatches. `sysemu.log` holds 524,359 "VPURF workaround required for type A" warnings: 524,291 on compute shire S0,
59 on the master shire S32 and 9 on the service processor S254 (the firmware's 68). All 524,288 compute-shire operand
reads flagged come from the 16 `fmadd.s` instruction words, 32,768 each, two per execution (64³ = 262,144
`fmadd.s`), plus 3 from `fsw`.

**Recovered raw records.** The SP trace dumps behind E6 (`sp1.bin`, `sp2.bin`, `sp3.bin`) and E5's load log were
still in aifoundry2's build tree; they are committed, with checksums, in
[`../2026-09-20-power-aifoundry2/raw/`](../2026-09-20-power-aifoundry2/raw/README.md). The test drive's silicon SGEMM
printout was not found.

**Owner decisions** (PLAN2 §4.2): demote the L2 mainline-starvation brief to a pointer page (IA-07; the brief as
corrected on 24 September is in git at `49dd0c8`); regenerate the DDR-droop block from `fit_unmetered.py`; keep the
unmetered fit as published and explain the L1-store residual; adopt the measured rail filter (τ ≈ 1.15–1.22 s) and
keep the `/0.94` correction with its systematic stated; qualify 133 ms as aifoundry2's on the hub and in the
findings; commit the recovered raw records; keep the firmware-version caveat.

**Errata and conventions to PLAN2.**

- **D21, the refresh interval.** D21 writes "every 3.87 µs". That is the interval the memory controller is
  programmed for (tREFI); the refresh series measures 2,325 cycles at 600 MHz, 3.875 µs, printed as 3.88 µs. The set's
  convention: **3.88 µs measured, 3.87 µs programmed**; a page may quote either if it says which.
- **Anchors (§2.4).** The energy manual gained four heading ids that other pages may link to:
  `#the-sram-arrays-at-rest` (§1.1), `#where-the-current-flows` (§4.4), `#build-a-workload-s-energy` (§7.1, the
  calculator) and `#the-relay-priced-from-section-4` (§7.2); every old id is kept, and `#terms` is now on a
  `<details>` element. It links the hub's `#the-chain` and `#the-unmetered-remainder-attributed` and memory anatomy's
  `#how-long-a-row-stays-open`, so those ids must stay.
- **The record's location.** PLAN2 §3 (G12) names a new directory, `docs/reports/data/2026-09-25-validation/`;
  the record was kept here instead, beside the 24 September plan it amends.
- **Catalogue burst counts.** aifoundry2's catalogue has 1,176 bursts (392 configurations × 3 passes; 3 over the
  60 ms sampler rule), aifoundry3's 1,158; PLAN2-actions' "3 of 1,158" for aifoundry2 is aifoundry3's count.
- **D2′, the starved sampler.** D2′ writes "about 150 ms when an s ↔ s+16 ring starves the SP". The per-pass
  medians are 76, 138 and 146 ms (aifoundry2; aifoundry3 stays at 22 ms). The board reading is not "held for
  seconds": the longest unchanged value in those bursts is 0.84 s; the reading changes 1.5–2.4 times a second
  against 5.3–6.6 in the other rings (recomputed from `rl-pass*/telemetry.jsonl.gz`).
- **D7/D8, the L1.** 0.77 pJ/B and 6.2 TB/s are memhier's own loop (8 loads per iteration, a load every 3.2
  cycles). The energy manual's figure for an L1 byte is the catalogue's unrolled `flw.ps` loop (64 per iteration,
  one every 1.4 cycles): 0.54 pJ/B [0.51–0.56] at 14.2 TB/s. The hub's energy explorer and the memory-hierarchy
  page's A100 comparison use it.

## The final pass (25 September)

After the page owners' work orders and a last polish, the whole set was checked once more before it was deployed:

- Every page rebuilt from its generator reproduced the committed file byte for byte (the nine source-built pages
  with `scripts/build-report.py`, memory anatomy with `workloads/memprobe/build_report.py`, the matmul and test-drive
  embeds with `scripts/mmbench-report-data.py`); the chart toolkit is current in every standalone page
  (`scripts/paste-chartkit.py --check`); the hub's computed data is current (`sync_hub_data.py --check`).
- `final_links.py` on the 17 public pages: every link to a page of the set, every `#anchor` on the target page, every
  GitHub path in the working tree; 0 problems, and nothing links the private brief.
- `check_page.sh` on all 18 pages at 1280 and 390 px, in light and `data-theme` dark: all OK (no JS errors, no
  sideways page overflow, no empty computed field, no broken anchor or image; every chart can take keyboard focus).
  The info lines left are wide tables that scroll inside their own box at 390 px.
- The deploy (`tools/deploy_all.sh`) first confirmed that all 18 live pages were still the `08076ae` versions, then
  updated each space with `--slug` beside `--title`. Afterwards `spacesheep list` showed no slug or visibility
  changed, each public URL answered 200, the private brief was not served anonymously, the Horace space served its
  three GIFs, and every live page equalled its repo file once the host's `data-ss-id` attributes are removed.
