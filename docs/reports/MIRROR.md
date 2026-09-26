# The spacesheep mirror: every published page and its file here

The repository is the ground truth. spacesheep.dev is where people read the pages. Every public page below is a
committed file in this repository, and the live page must equal that file. The only allowed difference is what the
host adds when it serves the page: `data-ss-id` attributes on elements and, on the raw address, its viewer scripts just
before `</body>`. Private pages are listed but not mirrored.

- **Check:** `python3 scripts/check-mirror.py` compares every public page with its file and exits non-zero on any
  difference (see [Checking that live equals repo](#checking-that-live-equals-repo)).
- **Keep this file current.** Add a row when a page is created, and edit it when a page moves, is deleted or changes
  visibility. `scripts/check-mirror.py` reads the tables between the `mirror:begin` and `mirror:end` markers: one row
  per space, the uuid in backticks, the repo file in backticks (or "not mirrored").
- **Addresses.** `https://spacesheep.dev/@yaroslavvb/<slug>` is the viewer (the page framed, with comments).
  `https://<space-uuid>.spacesheep.app/` is the raw page, and a folder deploy serves each of its files at
  `https://<space-uuid>.spacesheep.app/<file>`. A private space answers both anonymously with a sign-in step only.
- The per-page history (what each version changed, the A-numbers, the reviews) is in
  [`docs/findings/04-artifacts.md`](../findings/04-artifacts.md). The review's `manifest.tsv` in
  `data/2026-09-24-report-review/` is a dated record of 24 September; this file supersedes it.

## The pages (as of 2026-09-25)

<!-- mirror:begin -->

### The measurement set: the pages the hub indexes

| Page | Space | Visibility | Repo file | Deploy |
|---|---|---|---|---|
| [Limits of observability · ET-SoC-1 reports hub](https://spacesheep.dev/@yaroslavvb/et-soc1-limits-of-observability) (A2) | `2ea37420-67b9-484e-9d4c-581e8a9f0323` | public | `docs/reports/2026-09-20-et-soc1-limits-of-observability.html` | file |
| [The energy manual](https://spacesheep.dev/@yaroslavvb/et-soc1-energy-manual) (A15) | `cc3cb1d6-51cf-420b-a165-7d8629904d97` | public | `docs/reports/2026-09-23-energy-manual.html` | file |
| [Heat per millimetre](https://spacesheep.dev/@yaroslavvb/et-soc1-heat-per-mm) (A17) | `5602ff62-878f-4db6-b703-02061000d9ce` | public | `docs/reports/2026-09-24-heat-per-mm.html` | file |
| [The DVFS loop and its leakage](https://spacesheep.dev/@yaroslavvb/et-soc1-dvfs-leakage) (A11) | `171dcd4a-5b6d-49d3-aca0-db4980fabfa5` | public | `docs/reports/2026-09-22-dvfs-leakage.html` | file |
| [Power and temperature telemetry](https://spacesheep.dev/@yaroslavvb/et-soc1-power-temperature) (A3) | `acee5c6d-56c0-45e7-aa97-ce11af37bdd8` | public | `docs/reports/2026-09-20-et-soc1-power-temperature.html` | file |
| [The Horace experiment](https://spacesheep.dev/@yaroslavvb/et-soc1-horace-experiment) (A4) | `da445a93-7be3-42c2-b9be-4992fa4a3b62` | public | `docs/reports/2026-09-20-horace-experiment.html` | folder: `index.html` + `horace-heating.gif` `horace-heating-6.gif` `horace-long.gif` |
| [Why is it low power?](https://spacesheep.dev/@yaroslavvb/et-soc1-why-low-power) (A5) | `baede20c-57d9-4e01-8157-2014670dd8cf` | public | `docs/reports/2026-09-21-why-low-power.html` | file |
| [One hot line stops a shire](https://spacesheep.dev/@yaroslavvb/et-soc1-hot-line) (A13) | `ac439287-4503-42c7-88e7-b5d3e3b64b06` | public | `docs/reports/2026-09-22-hot-line.html` | file |
| [Hand it to the next shire: on-chip relay vs DRAM](https://spacesheep.dev/@yaroslavvb/et-soc1-on-chip-relay) (A14) | `8678d49d-3f0c-49be-b08a-5528de8ece3c` | public | `docs/reports/2026-09-22-on-chip-relay.html` | file |
| [Anatomy of a memory access](https://spacesheep.dev/@yaroslavvb/et-soc1-memory-anatomy) (A1) | `2bf74fd1-fd7f-4e19-8e35-6168ae42657c` | public | `docs/reports/2026-09-19-et-soc1-memory-anatomy.html` | file |
| [Memory hierarchy](https://spacesheep.dev/@yaroslavvb/et-soc1-memory-hierarchy) | `4b6e0a37-808d-4fc9-8001-555125733c46` | public | `docs/reports/2026-09-18-et-soc1-memory-hierarchy.html` | file |
| [On-chip communication](https://spacesheep.dev/@yaroslavvb/et-soc1-on-chip-communication) | `ab8e1b2b-de17-44f4-8645-006fa960e349` | public | `docs/reports/2026-09-18-et-soc1-on-chip-communication.html` | file |
| [Matmul efficiency](https://spacesheep.dev/@yaroslavvb/et-soc1-matmul-efficiency) | `590752c1-17a8-4f5d-97ef-bcf33fd6a3e7` | public | `docs/reports/2026-09-18-et-soc1-matmul-efficiency.html` | file |
| [Sparse compute](https://spacesheep.dev/@yaroslavvb/et-soc1-sparse-compute) | `5abf6014-8de0-4e82-8744-5676bac6453e` | public | `docs/reports/2026-09-18-et-soc1-sparsity.html` | file |
| [Ridge points](https://spacesheep.dev/@yaroslavvb/et-soc1-ridge-points) (A19) | `dd341b0b-a52e-4e23-b8b3-101a83119133` | public | `docs/reports/2026-09-18-et-soc1-ridge-points.html` | file |
| [Test drive](https://spacesheep.dev/@yaroslavvb/et-soc1-testdrive) | `16732875-c03e-434d-a643-7a432586c7f7` | public | `docs/report/index.html` | file (`docs/report/` holds only this file) |
| [Spatial temperature: a brief](https://spacesheep.dev/@yaroslavvb/et-soc1-spatial-temperature-brief) | `bc391cfe-64e2-4f36-884c-9bbfcb267de8` | public | `docs/reports/2026-09-22-et-soc1-spatial-temperature-brief.html` | file |
| [L2 mainline starvation: a brief](https://spacesheep.dev/@yaroslavvb/2026-09-22-et-soc1-l2-mainline-starvation) (a pointer page) | `49ca367f-886f-4c0a-b472-12d8fc449300` | public | `docs/reports/2026-09-22-et-soc1-l2-mainline-starvation.html` | file |
| [Influence functions on the ET-SoC-1](https://spacesheep.dev/@yaroslavvb/et-soc1-influence-functions) (exploratory, 25 Sep) | `55ae9267-3fc8-42a4-8621-4102fd7c97f7` | public | `docs/reports/2026-09-25-influence-on-et.html` | file |

### The lab machines

| Page | Space | Visibility | Repo file | Deploy |
|---|---|---|---|---|
| [What is broken on aifoundry1](https://spacesheep.dev/@yaroslavvb/aifoundry1-troubleshooting) (25 Sep) | `a2d70512-f892-474e-aca6-0568176cb092` | public | `docs/reports/2026-09-25-aifoundry1-troubleshooting.html` | file |
| [aifoundry1 is fixed](https://spacesheep.dev/@yaroslavvb/aifoundry1-fix) (25 Sep, the fix log) | `31e35ba7-36f4-486e-b6f3-687f7c7ad3a0` | public | `docs/reports/2026-09-25-aifoundry1-fix.html` | file |

### Public, not mirrored

| Page | Space | Visibility | Repo file | Why |
|---|---|---|---|---|
| [Lab machine accounts](https://spacesheep.dev/@yaroslavvb/aifoundry-lab-accounts) (18 Sep) | `5bcb11cb-7e1f-4cf2-bde3-c375c904b3a9` | public | not mirrored | A standalone copy of an older [`docs/lab-access.md`](../lab-access.md) with `scripts/add-lab-user.sh` built in, written by hand on 18 September. The machines' login banners link it. It is older than `lab-access.md`, which is the current text. |

### Private: listed, not mirrored

| Page | Space | Visibility | Repo file | Why |
|---|---|---|---|---|
| Notes of a conversation with David Kanter (R9, 20 Sep) | `f3533740-5ad9-45e1-927c-098dbbe5c210` | private | not mirrored | A personal memo quoting a private conversation; private and unlinked since 24 September (the owner's decision). The DVFS page and R9 describe it in words. |
| The lab problems report for the lab lead (25 Sep) | — | private | not mirrored | Written for the lab lead about the lab machines; it stays out of this public repository (`38f6b02`), and its source is gitignored (`docs/reports/2026-09-25-lab-problems.html`). Its visibility is the owner's decision. |

<!-- mirror:end -->

The account also holds spaces that are not part of this work (plans, notes, other projects). They are not listed.

## How each page is built

Edit the source named here, never the generated HTML. The source-built pages share
`docs/reports/sources/report.template.html` and the chart toolkit `docs/reports/sources/chartkit.js`; the
standalone pages carry a pasted copy of the toolkit (`python3 scripts/paste-chartkit.py PAGE`, and `--check`). The
build prerequisites are in [`docs/getting-started.md`](../getting-started.md) §8 (Python 3 with numpy, and `npm ci`
once for mathjax-full).

| Page | Source | Final build step (from the repository root) | Earlier steps |
|---|---|---|---|
| Hub (A2) | `sources/limits-of-observability.*` (text and data) | `python3 tools/ettelem/sync_hub_data.py`, then `python3 scripts/build-report.py limits-of-observability docs/reports/sources/limits-of-observability.data.json docs/reports/2026-09-20-et-soc1-limits-of-observability.html` | rerun `sync_hub_data.py` after regenerating any file it reads (`--check` exits 1 if stale) |
| Energy manual (A15) | `sources/energy-manual.*` | `python3 scripts/build-report.py energy-manual docs/reports/data/2026-09-23-energy-manual/manual.json docs/reports/2026-09-23-energy-manual.html` | 04-artifacts.md A16, "Rebuilding the energy data, in order" |
| Heat per mm (A17) | `sources/heat-per-mm.*` | `python3 scripts/build-report.py heat-per-mm docs/reports/data/2026-09-24-wire-energy/report.json docs/reports/2026-09-24-heat-per-mm.html` | 04-artifacts.md A18: `analyze_wire.py`, `build_wire_report.py` |
| DVFS (A11) | `sources/dvfs-leakage.*` | `python3 scripts/build-report.py dvfs-leakage docs/reports/data/2026-09-22-dvfs-aifoundry2/dvfs.json docs/reports/2026-09-22-dvfs-leakage.html` | E19 in 03-experiments.md: `analyze_dvfs.py`, then `build_cards_data.py --merge` |
| Power and temperature (A3) | `sources/power-temperature.*` | `python3 scripts/build-report.py power-temperature docs/reports/data/2026-09-20-power-aifoundry2/summary.json docs/reports/2026-09-20-et-soc1-power-temperature.html` | `tools/ettelem/summarize_power_session.py DATA --out DATA/summary.json` |
| Horace (A4), Why low power (A5) | `sources/horace-experiment.*`, `sources/why-low-power.*` | `tools/ettelem/finish_horace.sh` (its last two lines build both pages from `docs/reports/data/2026-09-21-horace-aifoundry2/report.json` and `lowpower-report.json`) | the whole Horace line, inside the script; the GIFs too |
| Hot line (A13) | `sources/hot-line.*` | `python3 scripts/build-report.py hot-line docs/reports/data/2026-09-22-hotline-aifoundry2/hotline.json docs/reports/2026-09-22-hot-line.html` | 04-artifacts.md A16: `analyze_hotline_power.py`, `analyze_hotline.py --context --barrier` |
| On-chip relay (A14) | `sources/on-chip-relay.*` | `python3 scripts/build-report.py on-chip-relay docs/reports/data/2026-09-22-onchip-aifoundry2/onchip.json docs/reports/2026-09-22-on-chip-relay.html` | `workloads/onchip/analyze_onchip.py` (E25) |
| Influence functions | `sources/influence-on-et.*` | `python3 scripts/build-report.py influence-on-et docs/reports/data/2026-09-25-influence-on-et/analysis.json docs/reports/2026-09-25-influence-on-et.html` | `python3 docs/reports/data/2026-09-25-influence-on-et/make_analysis.py` |
| Memory anatomy (A1) | `workloads/memprobe/report_template.html` | `python3 workloads/memprobe/build_report.py docs/reports/data/2026-09-19-memprobe-aifoundry2/summary.json docs/reports/data/2026-09-23-energy-manual/manual.json docs/reports/2026-09-19-et-soc1-memory-anatomy.html` | E1 in 03-experiments.md |
| Memory hierarchy, On-chip communication, Matmul efficiency and the Test drive's ladder, Sparse compute, Ridge points | the prose in the HTML; an `--embed` script rewrites only the embedded JSON | the commands in 04-artifacts.md, "Rebuilding the standalone pages", then `python3 scripts/paste-chartkit.py PAGE` | none |
| Spatial temperature brief, L2 mainline-starvation brief | the HTML, by hand | none (`python3 tools/ettelem/host_temp_fields.py --check docs/reports/2026-09-22-et-soc1-spatial-temperature-brief.html` tests the brief's two constants) | none |
| The two aifoundry1 pages | the HTML, by hand (standalone) | none | the evidence is in `docs/reports/data/2026-09-25-aifoundry1/` |

On 2026-09-25 each of the ten `build-report.py` steps above rebuilt its committed page byte for byte from the
committed data (hub, energy manual, heat per mm, DVFS, power and temperature, Horace, why low power, hot line,
on-chip relay, influence functions). 04-artifacts.md, "The 25 September validation", records the same for the rest.

## Deploying one page

The rules behind each line are in 04-artifacts.md, "Publishing notes, learned the hard way".

```bash
P=docs/reports/2026-09-22-hot-line.html; UUID=ac439287-4503-42c7-88e7-b5d3e3b64b06; SLUG=et-soc1-hot-line
D=$(mktemp -d); cp "$P" "$D/index.html"     # the Horace page: also copy its three GIFs into $D
spacesheep deploy "$D" --space "$UUID" -m "<what changed>"   # pass --slug "$SLUG" whenever you pass --title
rm -rf "$D"                                  # takes the .spacesheep.json pin file with it
spacesheep list | grep "$SLUG"               # visibility and address unchanged?
python3 scripts/check-mirror.py --only "$SLUG"
```

- Deploy from a directory of its own, never from `docs/reports/` itself: the CLI writes a `.spacesheep.json` pin file
  into the deployed directory, and a stale pin once published one report over another (22 September).
- Always pass `--space` on an update. Passing `--title` without `--slug` re-slugs the space and breaks its address.
- A new page: pass `--title`, `--slug`, `--emoji` and `--description` on the first deploy. The space starts
  private. Make it public (`spacesheep share <uuid> --visibility public`) only when the owner says so, then add its
  row here with the uuid from `spacesheep list --json`.
- A deploy can change a space's visibility. Visibility is the owner's call: compare `spacesheep list` with this file
  after every deploy.
- Commit the page file and this file together with the deploy, so the repository and the live page never disagree
  for long.

## Checking that live equals repo

```bash
python3 scripts/check-mirror.py                  # every page; exit 0 only if every public page is equal
python3 scripts/check-mirror.py --only et-soc1-hot-line --via https
```

For each public page it fetches the live `index.html` and compares it with the repo file after removing the host's
`data-ss-id` attributes. With a spacesheep key configured (`spacesheep login`, or `SPACESHEEP_KEY`) it reads the
stored file with `spacesheep read <uuid> index.html -o <dir>`. It also reads the account's `spacesheep list --json` and
compares every row's visibility and slug with this file, and warns about any public space whose slug starts like
this set's (`et-soc1`, `etsoc1`, `aifoundry`, `2026-09-22-et-soc1`) that is not listed here as public. Without a key it fetches the raw page
anonymously over HTTPS (`https://<uuid>.spacesheep.app/`) and also removes what the host inserts just before
`</body>` (its print style, print mark and viewer scripts), after checking that the insertion holds only `<style>` and
`<script>` blocks and the host's own `ss-` elements, and that it is the same on every page. Folder files (the
Horace GIFs) are always fetched over HTTPS and compared byte for byte, because `spacesheep read` returns binary files
mangled. For every private row with a uuid it checks that neither address serves the page anonymously. Exit status: 0 when
everything matches, 1 on any difference (content, visibility or a private page served anonymously), 2 when a page
could not be reached and nothing else was wrong.

**Last check: 2026-09-25, 21:46 PDT**, against the files at `bde52e0`, run both ways (read-only):

| | Through `spacesheep read` (key configured) | Anonymously over HTTPS |
|---|---|---|
| Mirrored public pages equal to their files | 21 of 21 | 21 of 21 (the host's insertion, 16,757 B, identical on every page) |
| The Horace GIFs | 3 of 3 equal | 3 of 3 equal |
| Viewer addresses answering 200 anonymously | 22 of 22 public rows | 22 of 22 |
| Visibility and slug as listed here (`spacesheep list --json`) | every row with a uuid | (read in the same run) |
| The private memo | not served anonymously | not served anonymously |
| Exit status | 0 | 0 |

Rerun at 21:57 PDT through `spacesheep read` with CLI 1.9.1 (the CLI on aifoundry2 was updated from 1.5.1 at 21:52),
and anonymously from a fresh clone with no key: the same result, 21 of 21 equal, exit 0.

The first run warned about two public spaces in the account whose slugs start like this set's but that this file does
not list as public; they are for the owner to decide on. Negative controls, run the same day on altered copies of
three pages, were all caught: a one-character change (`differs`, with the line), an extra element before `</body>`, an
extra `<script>` at the end of the body (over HTTPS, by the insertion's hash), a changed GIF byte, a public page listed
as private (`SERVED ANONYMOUSLY` and a visibility mismatch) and a wrong slug (a 302 and a slug mismatch).
