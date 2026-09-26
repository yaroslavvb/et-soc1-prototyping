# AGENT.md: start here

The entry point for an AI agent, or a person, starting from a fresh clone of
<https://github.com/yaroslavvb/et-soc1-prototyping>. Read it once from top to bottom (about fifteen minutes), then use
it as the map. [`CLAUDE.md`](CLAUDE.md) holds the same rules in short. Written on 2026-09-25.

**The rule behind everything here: this repository is the ground truth.** Every result, the experiment behind it,
its raw data, the tool that produced it and every lesson learned live here. The reports on spacesheep.dev are the
human-facing mirror of files in this repository and must equal them. An agent's per-machine memory is invisible to
the next agent, so a lesson that is only in memory is lost: write it here (section 10). The repository is public, so
nothing security-sensitive goes in it.

---

## 1. What this project is, and where it stands

The ET-SoC-1 is Esperanto's RISC-V accelerator, open-sourced by AI Foundry (AINekko): 1,088 small in-order cores
("minions") with vector and tensor units, grouped in 34 "shires" of which 32 run kernels, on a mesh network, with
32 GB of LPDDR4X on a PCIe card. Roman Shaposhnik (AI Foundry) invited this work: prototype workloads on the `sys_emu` simulator, then on the real
cards in the AI Foundry lab, and share what was learned. It became a measurement study: what a workload's data does to
the chip's power and temperature, what every operation costs in joules, what the meters can and cannot see, and
where the chip could beat a GPU.

**Status on 2026-09-25:**

- **19 published measurement pages**: the hub,
  [Limits of observability](https://spacesheep.dev/@yaroslavvb/et-soc1-limits-of-observability#reports), and the 18
  pages it indexes, plus two pages about the lab machines. All are listed in [`docs/reports/MIRROR.md`](docs/reports/MIRROR.md).
- **The knowledge base** in [`docs/findings/`](docs/findings/README.md) traces every claim to its experiment and raw
  file. It was validated twice (24 and 25 September).
- **Version 3 of the claims check is running**: every claim of the pages re-tested on three cards with
  pre-registered predictions ([`docs/reports/data/2026-09-25-claims-v3/`](docs/reports/data/2026-09-25-claims-v3/README.md),
  code in [`tools/claims-v3/`](tools/claims-v3)). Its queues hold aifoundry1's card 1, aifoundry2 and aifoundry3 for
  hours at a time. A later pass revises the pages with its results.
- **The lab has four working cards** since 25 September (section 4). One of them overheats.

The live status is kept in [`docs/getting-started.md`](docs/getting-started.md), "Where things stand". Read it next.

## 2. Repository map

```
AGENT.md                this file: the map and the rules
CLAUDE.md               Claude Code's standing instructions: the rules in short
README.md               the human front page: every report with its tools, data and address
Makefile, package.json  gp-sdk builds (make, make run-hello, make mmbench-check, make bench-power); mathjax-full 3.2.1
docs/
  findings/             the knowledge base: findings, claims ledger, experiments, artifacts, card behaviour (README.md first)
  energy-manual/        the energy manual as markdown, generated from its data (README.md, sections 1-9)
  reports/              every published page (HTML), MIRROR.md, sources/ (page sources), data/<date>-<name>-<host>/ (raw data)
  report/               the 18 September test-drive page (index.html)
  research/             sourced notes: counters and DRAM, power telemetry, why the chip is low power
  getting-started.md    status, setup, connecting to the lab, rerunning and republishing everything
  lab-access.md         accounts, Tailscale SSH, and the shared tools on the lab machines
  et-soc1-notes.md      the architecture and programming guide: read it before writing kernels
kernels/                gp-sdk device code: hello, mmbench (the tensor-unit matmul benchmark)
launchers/              gp-sdk host programs: hello, mmbench, tools
workloads/              standalone lab workloads (et-testdrive style): enercat (the energy catalogue), memhier,
                        memprobe, nocbench (mesh, hot line), onchip (the relay), pmcsel, sgemm, sparsity, traceprof
tools/
  claims-v3/            the measurement framework: lib.sh, queue.sh, schedules, one directory per experiment
  ettelem/              the telemetry client (C++) and the analysis and page-data scripts of the power work
  etcfg/                a read-only driver query: TDP, boot clock, shire mask, cache sizes
  g3log-race/           a card-free reproduction of the runtime's log-level race (aifoundry3's host crashes)
scripts/                VM setup, lab deploys, page building (build-report.py, paste-chartkit.py), check-mirror.py
rtl-sim/                Verilator benches on the original RTL: fma_toggle (switching activity), pmu_carry (a counter bug)
patches/                local fixes to et-platform and to the lab's gp-sdk (README.md explains each)
external/               upstream clones, gitignored (scripts/clone-upstream.sh)
build/                  build outputs and raw data not yet committed, gitignored
```

| You want | Go to |
|---|---|
| A number you can quote | [`docs/findings/05-claims.md`](docs/findings/05-claims.md) |
| How to run a card without fooling yourself | [`docs/findings/14-card-behaviour.md`](docs/findings/14-card-behaviour.md) |
| What an operation costs in joules | [`docs/energy-manual/README.md`](docs/energy-manual/README.md) |
| What an experiment ran, and where its data is | [`docs/findings/03-experiments.md`](docs/findings/03-experiments.md) |
| Every published page: space, file, visibility, build | [`docs/reports/MIRROR.md`](docs/reports/MIRROR.md) |
| A page's history, the tools, the commits, the publishing traps | [`docs/findings/04-artifacts.md`](docs/findings/04-artifacts.md) |
| How to rebuild a page from its data | [`docs/getting-started.md`](docs/getting-started.md) §8, and MIRROR.md |
| The version-3 plan, predictions and amendments | [`docs/reports/data/2026-09-25-claims-v3/`](docs/reports/data/2026-09-25-claims-v3/README.md) |
| The architecture | [`docs/et-soc1-notes.md`](docs/et-soc1-notes.md); the manuals in `external/et-man` |

## 3. The knowledge base, and how to use it

[`docs/findings/README.md`](docs/findings/README.md) is the index: the findings in brief, a glossary (minion, hart,
shire, scratchpad, SP, PMIC), a "where to look" table, and the provenance scheme. Four kinds of ID:

| ID | What | File |
|---|---|---|
| R1–R14 | resources that existed before any measurement: manuals, RTL, firmware source, papers, the machines | [`01-resources.md`](docs/findings/01-resources.md) |
| Q1–Q43 | the owner's requests and what each produced (25 September's requests are not numbered yet; getting-started lists them) | [`02-requests.md`](docs/findings/02-requests.md) |
| E1–E34, E49 | experiments: command, time, card, raw files. The version-3 experiments carry suggested numbers (E35–E48) in PLAN3 and their READMEs, and are recorded in their own data directory until registered; E49 is the card-free g3log race test | [`03-experiments.md`](docs/findings/03-experiments.md) |
| A1–A19 | published artifacts: pages, images, tools, commits | [`04-artifacts.md`](docs/findings/04-artifacts.md) |

- **To answer a question:** the "where to look" table → the topic file (10–20) → the number in
  [`05-claims.md`](docs/findings/05-claims.md), whose kind says what it is (measured, simulated, fitted, predicted,
  derived, read from source, external, **assumed**) → the experiment in 03 → the raw file. Quote only numbers that
  are in the claims ledger, with their kind.
- **Before measuring:** [`14-card-behaviour.md`](docs/findings/14-card-behaviour.md) (the governor, the telemetry, the
  protocol, the four cards, the traps) and [`19-observability-and-the-unmetered.md`](docs/findings/19-observability-and-the-unmetered.md)
  (what the meters miss).
- **The energy manual** ([`docs/energy-manual/`](docs/energy-manual/README.md), page
  [et-soc1-energy-manual](https://spacesheep.dev/@yaroslavvb/et-soc1-energy-manual)) is generated: its markdown and
  page are rebuilt from `docs/reports/data/2026-09-23-energy-manual/manual.json` (04-artifacts.md, A16). Edit the
  builders, never the markdown.
- **Known stale spots (2026-09-25).** The findings files, README.md and the tool comments were corrected on
  25 September. These still say that aifoundry1 cannot be used, that the cause was a `srcversion` mismatch, or that
  aifoundry3's zero TDP is flashed, until their next revision: the DVFS page, the energy manual's `00-structure.md`
  and `08-cards.md` (generated: fix `tools/ettelem/render_energy_manual.py`), and
  `docs/reports/data/2026-09-25-claims-v3/firmware.md` (a dated record). `tools/claims-v3/lib.sh` still says
  aifoundry3 has no system numpy (it has, since 25 September). Trust 14-card-behaviour.md and this file.

## 4. The machines

**The simulator.** On a Mac, all ET tooling runs in the Lima VM `et` (`scripts/create-vm.sh`), and every build or run
command is prefixed with `scripts/vm`. On any other Ubuntu 24.04 box, `scripts/clone-upstream.sh && scripts/provision-vm.sh`
builds the same `/opt/et` natively (the README's setup section). **Never run `provision-vm.sh` on a lab machine**: its
`/opt/et` is the lab's. `sys_emu` is functional only: it checks correctness, never speed.

**The lab.** Three x86_64 Ubuntu 24.04 machines on AI Foundry's Tailscale tailnet, four cards:

| Card | Firmware | Clock policy | Notes |
|---|---|---|---|
| aifoundry2 | 1.3.1 | the firmware's DVFS: 600–800 MHz, above 600 only on a die below about 68 °C | the main card; the git checkout is `~/claude/et-soc1-prototyping` here |
| aifoundry3 | 1.3.1 | **pinned at 600 MHz**: a boot service sets a 0 W TDP at every boot | compare switching power over idle, never absolute watts; about 1 host launch in 100 crashes at 1.08 s unless the program registers libetrt's log levels first (`registerRuntimeLogLevels()`, 14-card-behaviour.md) |
| aifoundry1 card 0 | 1.4.1 | DVFS; idles at 300 MHz | **overheats (115–117 °C): no sustained work on it**; excluded from the campaign |
| aifoundry1 card 1 | 1.2.0 | DVFS; idles at 600 MHz | fine; select a card on this host with `ET_DEVICES=<n>` |

The hosts also differ in CPU, RAM and ET runtime build, which matters for host-side timing:
[14-card-behaviour.md](docs/findings/14-card-behaviour.md#the-lab-machines-and-their-four-cards-are-not-interchangeable).
The trees on aifoundry1 and aifoundry3 (`~/nekko`) are rsynced copies without git: edit in a git checkout, then sync.

**Access.** Ask the repo owner for tailnet membership and accounts on the machines; our account is `yaroslavvb`.
Logins use Tailscale SSH in **check mode**: `ssh aifoundryN` prints a `login.tailscale.com` URL that a person must
approve in a browser signed in to the tailnet, while the `ssh` waits; one approval lasts about 12 hours, and a URL that
answers 404 needs a sign-out and sign-in at login.tailscale.com first ([`docs/lab-access.md`](docs/lab-access.md)).
From aifoundry2, name the other machines by their full tailnet names, or `ssh` goes over the LAN.

**Steps only a person can do** (ask, then wait): approving the Tailscale check; `spacesheep login` (a browser
approval); anything that needs a GitHub key, such as a push; any admin action on a lab machine (accounts, drivers,
card resets, services), which is the lab admin's; any change to a page's visibility, which is the owner's; and
claiming a machine on the AI Foundry Discord (#community-lab: "using aifoundryN", then "released"), the lab's own norm
(getting-started.md §2).

## 5. The lab's etiquette, and why

The owner's rules (CLAUDE.md, getting-started.md §2), the lab's norms and the lessons behind them, each with its
reason:

| Rule | Why |
|---|---|
| Ask which machine (and card) to use; stay off machines other sessions use | the cards are shared with other people, CI runners (aifoundry1, aifoundry2), a demo (aifoundry3) and our own campaign queues |
| Look first: `et-who`, `who`, `uptime`; hold card N's lock for your run (`flock -n /run/lock/etsoc-shire<N>.lock <cmd>`, which fails at once if someone holds it) | the management node is single-opener, and a second user of a card corrupts both measurements |
| Never hold a device for more than 10 s: `timeout 10` on every launch | long holds block everyone else, and a card that hangs needs a power cycle only the lab admin can do |
| Stop tools with Ctrl-C or a plain `kill`, never `kill -9` | a sampler killed mid-request poisons the card's management queue for the next user |
| Never reset a card or change its TDP, clocks, firmware or driver | a software reset can hang a card, and a configuration change silently alters other people's runs |
| Keep disk and memory small: sources only, `nice -j4` builds | the machines are shared, and aifoundry1's disk is nearly full |
| An agent that only writes code never reaches a card: `V3_DRY=1`, then check `et-who` | on 25 September a code-only agent ran a real block because a `cd` in a backgrounded chain did not apply |

## 6. The traps, in brief

Each links to the full entry in [14-card-behaviour.md](docs/findings/14-card-behaviour.md).

- **The governor is thermal first**: above 65 °C a card sits at 600 MHz, below it a busy card steps up to 800. On
  aifoundry2, heat the die past 68 °C before any power burst, and check `mhz.minion` in every sample
  ([the governor](docs/findings/14-card-behaviour.md#the-clock-governor-is-thermal-first)).
- **Firmware 1.4.1 idles at 300 MHz**: idle brackets and bursts sit at different operating points on aifoundry1's
  card 0 (same section).
- **The telemetry lies in specific ways**: whole-degree die readings, rails that are a PMIC running average
  (τ ≈ 1.2 s), a 133 ms refresh on aifoundry2 and 250 ms on aifoundry3, and some workloads starve the meter: check
  `took_ms` ([telemetry](docs/findings/14-card-behaviour.md#the-telemetry-and-what-each-number-really-is)).
- **Heat carries over between runs**: launch every run from the same die temperature, and budget three to eight
  times more wall-clock than card time ([protocol](docs/findings/14-card-behaviour.md#the-measurement-protocol-that-made-results-repeatable)).
- **Cards are compared on switching power over idle**, never absolute watts
  ([comparing cards](docs/findings/14-card-behaviour.md#comparing-cards-use-switching-power-not-watts)).
- **Host timing changed on 25 September** (power profile, pending reboot): host-side numbers before and after are
  not comparable. Record `et-lab-manifest` with every run
  ([host changes](docs/findings/14-card-behaviour.md#host-changes-of-25-september-and-what-stays-comparable)).
- **Kernel code that traps**: `double`, 64-bit integer-to-float, `fdiv`/`fsqrt`/`fsin`/`frsq` and `cycle` in U-mode,
  scratchpad offset 0, a global atomic through a scratchpad address, spinning on one global atomic; also the
  non-coherent L1, tensor ops on hart 0 only, and one TensorSend ready bit per minion
  ([traps](docs/findings/14-card-behaviour.md#traps-that-cost-time-here)).
- **Tools and hosts**: the poisoned management queue, `ettelem sample` failing to start one time in three, aifoundry3's
  1.08 s host crash (a g3log race in libetrt; call `registerRuntimeLogLevels()` first in every new host `main`), misleading health checks, the 8 s `sparsity_host --budget`, a memory pattern with no buffer
  writing to address 0, identical code from the three toolchains (compare `.text` hashes), and never editing or
  `scp`-ing over a running script (same section).

## 7. How to measure

**Build.** Standalone workloads (`workloads/<name>/`) build on the lab host itself, against its own `/opt/et`, and
their host program has its kernel's path compiled in. Each workload's `README.md` gives its flags and its runs.

- **While the campaign's queues run, never rebuild into a build directory their blocks use**: `build/<name>/` for
  enercat, memhier, memprobe, nocbench, onchip, sparsity and sgemm, `build/enercat_v2/`, `build/enercat_gs/` (the
  gathers-and-scatters queue that follows), `build/ettelem/`, `build/claims-v3-bin/`, `build/memprobe-data/`, and on
  aifoundry2 also `build/memprobe-v3/` and `build/sparsity_t2/` (most are named at the top of
  `tools/claims-v3/lib.sh`; `grep -oh 'build/[A-Za-z0-9_.-]*' tools/claims-v3/lib.sh tools/claims-v3/*/*.{sh,py} |
  sort -u` lists them all). The next block would run a different binary than its code hash records. Build into a
  directory of your own, with a name no block uses.
- **For the same reason, do not run `scripts/deploy-lab.sh` or `scripts/deploy-lab-gpsdk.sh` against a host whose
  queue runs.** Both write into `~/nekko` there, which is the campaign's tree on aifoundry1 and aifoundry3:
  `deploy-lab.sh` rebuilds `build/<name>/`, and `deploy-lab-gpsdk.sh` copies every source file over the tree and
  deletes and rebuilds `build/kernels` and `build/launchers`, which the `mmb` blocks run on every host. When no
  queue runs, they are the way to build on another host (from a machine with a clone). gp-sdk kernels (`kernels/`)
  need `deploy-lab-gpsdk.sh`, which installs the patched gp-sdk `06605ab`.
- After an rsync, build with `--clean-first`: rsync keeps the source's modification times.

**Run one workload on a card by hand** (in the host's tree: the checkout on aifoundry2, `~/nekko` elsewhere):

```bash
cmake -S workloads/sgemm -B build/sgemm-mine -DCMAKE_PREFIX_PATH=/opt/et -Wno-dev && nice cmake --build build/sgemm-mine -j4
et-who                                            # nobody on the card? (and ask first: section 5)
et-lab-manifest > build/sgemm-mine/manifest.txt   # the machine facts, saved with the data
flock -n /run/lock/etsoc-shire0.lock timeout 10 build/sgemm-mine/host/sgemm_host -n 512 --reps 3
```

On aifoundry1, add `ET_DEVICES=1` before the program and take `etsoc-shire1.lock` (card 1; never sustained work on
card 0). The telemetry client builds the same way (`cmake -S tools/ettelem -B build/<dir> …`); build it on each host,
so that on aifoundry1 it honours `ET_DEVICES`. `tools/etcfg/` is one C file: `gcc -O2 -I/opt/et/include -o etcfg
tools/etcfg/etcfg.c`.

**The framework: [`tools/claims-v3/`](tools/claims-v3).** New card work that anyone will quote goes through it, not
through ad-hoc scripts.

- **`lib.sh`**, sourced by every block, enforces the rules: no start while another user or device process (or a CI
  job) is present, or, on a two-card host, while anyone else holds the card (`others_present`); every device call
  capped at 10 s (`hold10`); the sampler started with retries and stopped with SIGTERM only, with one queue drain on a
  failed start; the die heated to the registered temperature on cards whose governor is free (`heat_to`); the card
  lock held for the whole block and the sha256 of the code that ran recorded (`block_begin`, `code.sha256`,
  `block.json`); `V3_DEVICE=<n>` selecting a card through `ET_DEVICES`.
- **One directory per experiment**: `block.sh <pass> [--smoke]` runs one pass; `reduce.py` holds the pre-registered
  decision code (`idle/reduce.py` also takes `--check-pass` for a smoke); `README.md` lists where the code departs
  from the plan's command lines, and why. `idle/` is the fullest example; `gs/` (E48) shows an experiment added after
  the plan, with its rules fixed in its README before any data.
- **`--smoke`** is the smallest real check of every component (about 30 s of card time). **`V3_DRY=1`** runs a block
  with no device access at all: device calls are printed, the die reads 80 °C, and data goes to `build/claims-v3-dry/`.
  Run a new block dry first, then smoke, then for real, from the tree's root (`lib.sh` refuses an unknown host, and
  on aifoundry1 a missing `V3_DEVICE`):

  ```bash
  V3_DRY=1 bash tools/claims-v3/<exp>/block.sh 1          # no device access; then check et-who
  bash tools/claims-v3/<exp>/block.sh 1 --smoke           # about 30 s of card time (V3_DEVICE=1 first on aifoundry1)
  ```
- **`queue.sh schedule-<card>.txt`** runs the blocks of one card unattended, in order: each schedule line is
  `<exp> <pass>`, `sleep <s>` or `end`; it re-reads the schedule before every block (lines can be appended), skips a
  pass whose `block.json` says ok, waits while the card is busy, retries a block that found someone else (exit 3),
  and stops at the next block boundary when `build/claims-v3/STOP` exists. Start it detached:
  `setsid nohup tools/claims-v3/queue.sh tools/claims-v3/schedule-<card>.txt > build/claims-v3/queue-<card>.log 2>&1 < /dev/null &`.
- **Raw data** goes to `build/claims-v3/<card>/<exp>/p<pass>/` and is collected into `docs/reports/data/` for commit.
- **Pre-registration.** The plan, its predictions and decision rules are committed before the first run
  ([`PLAN3.md`](docs/reports/data/2026-09-25-claims-v3/PLAN3.md)). Any change is an amendment in
  [`AMENDMENTS.md`](docs/reports/data/2026-09-25-claims-v3/AMENDMENTS.md), written before any data it touches. A failed
  prediction is reported as failed. The unit of replication is an independent pass, session or card, never samples
  inside one burst.

**Long runs** start detached (`setsid nohup … < /dev/null &` over `ssh`): the agent harness kills a foreground command
at its timeout, and the hosts' Wi-Fi drops now and then. A `pgrep -f` over `ssh` matches its own command line.

**Recording.** Commit raw data under `docs/reports/data/<date>-<name>-<host>/` with a README that says what ran,
when, on which card, with which command, plus the `et-lab-manifest` output. Register the experiment in 03, its
numbers in 05, the request in 02, and any published artifact in 04 and MIRROR.md.

## 8. How to publish

1. **Edit the source**, never generated HTML: `docs/reports/sources/<name>.{body.html,script.js,meta.json}` plus a
   data JSON for the source-built pages; the prose in the HTML for the standalone pages. Every page's source and
   final build command are in [MIRROR.md](docs/reports/MIRROR.md#how-each-page-is-built).
2. **Build** with `python3 scripts/build-report.py <name> <data.json> <page.html>` (needs `npm ci` once for the
   build-time math), or the page's `--embed` script and then `python3 scripts/paste-chartkit.py PAGE`. Charts use
   the toolkit's card registry (`CK.card`, `CK.cardsIn`, `CK.cardSeg`, `CK.pick`): take the cards from the data,
   never hard-code two, so a new card appears when its data does. `CK.sortTable` makes a table sortable.
   Changing many pages at once (26 September's visualization pass): work in a `git worktree` on a branch, so main
   keeps matching the live pages, then merge, deploy every changed page and run `check-mirror.py` together; with
   several agents in one worktree, commit named files only (`commit -a` sweeps up the others' half-done edits).
3. **Check** with `docs/reports/data/2026-09-24-report-review/tools/check_page.sh PAGE` (JS errors, empty fields,
   sideways overflow, anchors; at 1280 and 390 px; `DARK=1` and `DARK=os` for the dark themes). It looks for
   Playwright's `chromium_headless_shell-1243` under `~/.cache/ms-playwright`; on another machine set
   `CHROME_HEADLESS` to any headless Chrome binary. `final_links.py` beside it checks the links across the set, but
   its page list is still the 24 September manifest, so it reports the hub's link to the influence-functions page as
   a problem: expect that one line until the manifest is updated.
4. **Deploy** from a directory of its own, with `--space <uuid>`, and with `--slug` whenever you pass `--title`
   ([MIRROR.md, "Deploying one page"](docs/reports/MIRROR.md#deploying-one-page)). A new space starts private;
   making it public is the owner's decision. Check `spacesheep --version`: the pages up to 25 September were deployed
   with 1.5.1; 1.9.1 (npm's latest from the evening of 25 September) reads them back the same, and a 1.9.1 redeploy
   of an existing space keeps its slug, title and visibility (tested 25 Sep, 23:40). An older CLI (npm's latest was
   1.2.1 until then) may not. Never put the CLI's key in the repository.
5. **Verify**: `spacesheep list` (visibility and address unchanged), then `python3 scripts/check-mirror.py --only <slug>`.
6. **Commit** the page, its sources and data, and MIRROR.md together.

A page written for one person, or one with sensitive content, stays private and is never mirrored here.

## 9. The spacesheep mirror index

[`docs/reports/MIRROR.md`](docs/reports/MIRROR.md) lists every page of the set: title and address, space uuid,
visibility, repo file, deploy form, how it is built, and the private pages with the reason each is not mirrored.
`python3 scripts/check-mirror.py` compares every public page with its file: through `spacesheep read` when a key is
configured (and then also each page's visibility and slug against the account's listing), otherwise anonymously over
HTTPS. It exits non-zero on any difference. On 2026-09-25 all 21 mirrored public pages were equal to their files,
both ways.

## 10. Where new lessons go

| The lesson is about | Write it in |
|---|---|
| A new result about the chip | the topic file in [`docs/findings/`](docs/findings/README.md) (10–20, or a new `NN-topic.md`), its line in the README's "findings in brief", its numbers in 05 with their kind |
| A card, its firmware or a host; a measurement trap | [`docs/findings/14-card-behaviour.md`](docs/findings/14-card-behaviour.md), dated, under the right section or "Traps" |
| Access, accounts, the machines' shared tools | [`docs/lab-access.md`](docs/lab-access.md) |
| Setup, workflow, the current state of the work | [`docs/getting-started.md`](docs/getting-started.md) ("Where things stand", §7 gotchas) |
| Publishing and the host | [`docs/findings/04-artifacts.md`](docs/findings/04-artifacts.md), "Publishing notes"; each page's row in [`MIRROR.md`](docs/reports/MIRROR.md) |
| A number, an experiment, a request | [`05-claims.md`](docs/findings/05-claims.md), [`03-experiments.md`](docs/findings/03-experiments.md), [`02-requests.md`](docs/findings/02-requests.md) |
| One workload's quirks | `workloads/<name>/README.md` |
| How agents should work here | this file, and the short form in `CLAUDE.md` |

**Never in this repository:** access paths or credentials of any kind (keys, tokens, root or admin routes), sudo, ACL
or SSH-policy details, which accounts have which privileges, IP addresses, other people's accounts or files, other
people's names beyond the few already public and needed (who invited the work, the lab admin), and anything from a
private page. Those belong in the owner's private notes or a private page. When a lesson lands in an agent's memory,
copy it here too.

## 11. The first hour

1. Read this file, `CLAUDE.md`, and getting-started.md's "Where things stand".
2. `git log --oneline | head -20` and `git status`: what changed last, and whether anything is uncommitted.
3. Skim the findings in brief and the glossary ([`docs/findings/README.md`](docs/findings/README.md)), then
   [`14-card-behaviour.md`](docs/findings/14-card-behaviour.md) end to end.
4. Find out where you are (section 4). On a lab machine, look without touching: `et-who`, `who`,
   `pgrep -af queue.sh`, and the tail of `build/claims-v3/queue-*.log` in the campaign's tree
   (`~/claude/et-soc1-prototyping` on aifoundry2, `~/nekko` on aifoundry1 and aifoundry3).
5. Ask the owner what to work on, which machine and card you may use, and whether the campaign's queues must be left
   alone (assume they must).
6. Ask a person for the steps only a person can do, when you reach them: the Tailscale approval, `spacesheep login`,
   a push.
7. Run `python3 scripts/check-mirror.py` (read-only) to see that the published pages still match the repository.
8. Before any card work: a dry run, a smoke, `timeout 10`, the card lock, and `et-lab-manifest` saved with the data.
9. Write each lesson into the repository as you learn it (section 10), and keep getting-started's status current.
