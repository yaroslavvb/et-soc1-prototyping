# The 24 September 2026 review of the measurement reports

On 2026-09-24 the repo owner asked for every document the observability hub links
(<https://spacesheep.dev/@yaroslavvb/et-soc1-limits-of-observability>) to be checked for consistency, correct
cross-links, suspicious claims and readability. This directory is the record of that review.

| File | What it is |
|---|---|
| `PLAN.md` | The fix plan: the overall assessment, the canonical value for every quantity stated on more than one page (D1–D20), the cross-linking scheme (X1–X5), conventions (C1–C7), the glossary text, the change list per page, the refuted and rejected findings, and the owner's open questions with how they were decided (the decisions are in the commit message of `49dd0c8` and below). |
| `findings-verified.json.gz` | Every reviewer finding (19 pages plus the knowledge base, a cross-page numbers ledger and a navigation review) with the independent verifier's verdict: 288 confirmed, 144 with a corrected fix, 2 refuted, plus 42 the verifiers found. Findings about a private memo are omitted. |
| `fix-results.json.gz`, `round2-results.json.gz` | What each page owner applied or skipped in the three fix passes, the independent check-and-repair verdicts, and the final reviewers' remaining issues. |
| `manifest.tsv` | The 19 pages: slug, space uuid, repo file. |
| `tools/check_page.sh` | Renders a page at 1280 and 390 px after its scripts run; reports JS errors, empty computed fields, sideways overflow, broken in-page anchors, headings without ids, and whether a contents list, a Related reports section and a hub link exist. |
| `tools/render_text.sh`, `tools/final_links.py` | The rendered text and links of a page; the cross-page check of every link and anchor across the set (all 1,240 resolved). |
| `tools/deploy_all.sh` | The redeploy: it refuses to overwrite a space whose live page differs from the version the review started from. Pass `--slug` together with `--title` on any update (see 04-artifacts.md, publishing notes). |

The tools need Chrome's headless shell (Playwright's `chrome-headless-shell`) and `AUDIT_DIR` pointing at a
scratch directory holding `manifest.tsv`.

Owner decisions taken during the review: the David Kanter notes, a personal memo, were made private and are no
longer linked; the hub now says its scouts and reviewers were AI agents; the L2 mainline-starvation brief stays,
corrected, with an update box pointing to the hot-line report; the unmetered fit is now a committed script
(`tools/ettelem/fit_unmetered.py`); the energy manual keeps its 1–8-hop wire fit with a note on 1–6 hops;
ridge points' energy balance is recomputed from the energy manual; the long idle before E19 is 20.6 hours by the
timestamps.
