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

**Where it stands** is kept in one place, [`docs/getting-started.md`](docs/getting-started.md), "Where things
stand": read it next. The published pages (the hub,
[Limits of observability](https://spacesheep.dev/@yaroslavvb/et-soc1-limits-of-observability#reports), and the pages
it indexes, plus the lab-machine pages) are listed with their spaces, files and builds in
[`docs/reports/MIRROR.md`](docs/reports/MIRROR.md), whose "Last check" says whether the live pages equal their files;
the page changes waiting for the next pass, the owner's items first, are in
[`docs/reports/TODO.md`](docs/reports/TODO.md). Which cards work is in §4 below, and the knowledge base's known stale
spots in §3.

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
  lab/                  the lab machines' shared tools: et-who, et-lab-health, et-lab-manifest, the banners (installed);
                        et-lab-health rev 3, its daily timer and et-reset (written, not installed)
  timeline/             the session-timeline page's extraction, privacy scan and build
scripts/                VM setup, lab deploys, page building (build-report.py, paste-chartkit.py), check-mirror.py
rtl-sim/                Verilator benches on the original RTL: fma_toggle_v2 (the fixed bench: build with -fno-dfg), fma_toggle and
                        fma_toggle_formats (the old ones, kept as the record), pmu_carry (a counter bug)
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
| Q1–Q135 | the owner's requests and what each produced (Q44–Q66: 25–28 September; Q67–Q135: 29 September – 1 November 2026) | [`02-requests.md`](docs/findings/02-requests.md) |
| E1–E125 | experiments: command, time, card, raw files. E35–E47 are the version-3 three-card check (25–26 September; its plan, results and raw data are in `docs/reports/data/2026-09-25-claims-v3/`), E48 the gathers and scatters on the same three cards (26 September), E49 the g3log race, reproduced without a card on 25 September, the fixed build checked on aifoundry3's card on 26 September, E50 the host link on the three cards (27 September), E51 DV2 on aifoundry2 (development 28 September; the frozen validation from 20:45 PDT that day to 16:57 PDT on 29 September, reduced that evening), E52 the heat placement (27–28 September, development and a frozen validation), E53 the overheating experiments (28 September, pre-registered, aifoundry3 and aifoundry1's card 1), E54 NV, the mesh rail's voltage step (predictions frozen; its first write waits for the owner), E55–E58 the major pass's pcie2, nocr, memp2 and tau (28–29 September: developed on aifoundry1's card 1, validated on aifoundry3; E55–E57 also on aifoundry2 as a third card on the evening of 29 September), E59 the sparse parity solver on aifoundry3's card (29 September, an engineering benchmark, not pre-registered), E60–E76 the October campaign (Q119–Q129: the bit-flip ladder, the deterministic flips, the heat movies, the camera ladder, Horace's power limit, the bit-price lists, the stage map, the governor moved, the saturation ladder, the idle slopes, 600 MHz, the camera's heat path, the register file, the memory path, the trapping instructions), E77 the rail at one temperature (reserved by Q129; registered and run on 1 November under Q133's governor moves; recorded by Q134's records after its verification, beside E120, its redesign), E78–E91 Q130's (31 October: the kinds energy matrix, the fp16 and int8 bit prices and the DRAM pattern on aifoundry3, the kinds' speed under aifoundry2's own governor, the matrix on aifoundry1's card 1, a speed replicate on aifoundry1's card 0 and the camera per kind, and the evening round's real GPT-2 tiles' energy and speed, the result path's share, heat below 12 W, sign patterns and tile spread, and the real tiles on card 1, not scored), E92–E106 Q132's (1 November: where a sign's cost goes and C read back, the zero gate on silicon, tile spread, more real tensors, heat below 12 W and a settled plateau, the drift, the DRAM mechanism, the idle reset, a matmul that streams and its layout, balanced bit prices, the model's blind test, held signs on one card), E107–E118 Q133's (1 November: a large GEMM's placement, a sign's rest located, int8 zeros, the memory path's width, a steady coefficient on aifoundry2, replicates on second cards, card 0's fp16 and int8 sustained cells re-run on the same card, the A side's form, the power model's blind pool, E72 on card 0 by a governor move; E117 not run), E119–E125 Q134's (the evening of 1 November: what a clock gap buys in seven of E107's arms on aifoundry2, E77 redesigned by a governor move (E120), E93's zero gate, E108's sign designs and E94's † rows on aifoundry3, E109's int8 zeros and E113's A side on aifoundry1's card 1) | [`03-experiments.md`](docs/findings/03-experiments.md) |
| A1–A25 | published artifacts: pages, images, tools, commits (A20 the session timeline, A21 the sparse parity page, A22 the heatsink study, A23 the transistor-heat timeline, A24 the matmul-to-transistor chain, A25 the kinds-of-numbers page) | [`04-artifacts.md`](docs/findings/04-artifacts.md) |

- **To answer a question:** the "where to look" table → the topic file (10–20) → the number in
  [`05-claims.md`](docs/findings/05-claims.md), whose kind says what it is (measured, simulated, fitted, predicted,
  derived, read from source, external, **assumed**) → the experiment in 03 → the raw file. Quote only numbers that
  are in the claims ledger, with their kind.
- **Before measuring:** [`14-card-behaviour.md`](docs/findings/14-card-behaviour.md) (the governor, the telemetry, the
  protocol, the four cards, the traps) and [`19-observability-and-the-unmetered.md`](docs/findings/19-observability-and-the-unmetered.md)
  (what the meters miss).
- **The energy manual** ([`docs/energy-manual/`](docs/energy-manual/README.md), page
  [et-soc1-energy-manual](https://spacesheep.dev/@yaroslavvb/et-soc1-energy-manual)) is mostly generated: sections
  01–06, 08, 03a and 04a, two card lines of 00, and the page are rebuilt from
  `docs/reports/data/2026-09-23-energy-manual/manual.json` (since 26 September built from the version-3 check's three
  cards; 04-artifacts.md, A16). Edit the builders, never that markdown; the README, the rest of 00, 07 and 09 are
  written by hand.
- **Known stale spots (2026-10-02).** Where a page and `docs/findings/` differ, the page holds. The pages carry each
  tested claim's three-card result (26 September; every claim with the items that test it:
  `docs/reports/data/2026-09-25-claims-v3/results/pagemap.md`), and `05-claims.md` gives the three-card values in
  "Version 3: the three-card check"; the topic files (10–19; 20-heat-per-mm.md has the third run) and README.md were
  corrected on 25–27 September but not rewritten for the three cards (leakage at 80 °C, for one: 20–29 W on the pages, a best fit of 23.3 W in older
  text). What the review of 26 September found and is not yet fixed is in [`docs/reports/TODO.md`](docs/reports/TODO.md)
  (part A pages, part B the repository). A page that still says aifoundry1 cannot be used, blames `srcversion`, or
  calls aifoundry3's zero TDP flashed or set by firmware is stale: a boot service sets it at every boot.
  `docs/reports/data/2026-09-25-claims-v3/firmware.md` is a dated record. A page or file that calls aifoundry1's
  card 1 governed ("firmware DVFS") is stale too: its clock never moved in the campaign (27 September). Text that
  describes the governor as one table step per pass that acts only while a kernel runs describes the `353f20e`
  source, a BL2 0.22.0, the version all four cards report since 27–31 October 2026 (E69, E79, E82 A1, E84 A1): no
  card exposes a BL2 git hash, so which 0.22.0 they run is not established (14-card-behaviour.md's residuals), but the
  one-pass governor and the removal of both loops date from 0.21.0 (et-platform `60b40c10`), so those hold for any
  0.22.0; text that gives a card the blocking thermal loop, the never-exiting power-down loop or the latch describes
  BL2 0.20.0, which no card is known to run now (14-card-behaviour.md, "The governor's two knobs"; Q130(d),
  `docs/reports/data/2026-10-31-q130-governor-thermal-branch/`). The overheating page (28 September) carries corrections that 05-claims.md lists at the end of "The effect of
  overheating" and that 14-card-behaviour.md and the topic files do not yet: aifoundry1's card 0's highest readings are
  its service processor's standing statistics (a 119 °C mean, a 123 °C sensor), not only the host's 115–117 °C of
  25 September; E51 and E52 recorded the sensors' mean and anonymous peak-holds, not a series per sensor; aifoundry2's
  catalogue launches at a 90–103 °C mean checked no arithmetic (the hottest checked launch is mmbench's, at 97 °C); the
  SRAM rail is 0.70–0.75 V by card. Otherwise trust 14-card-behaviour.md and this file. Since 2 October 2026
  (aifoundry1's card 0 back in service after its fan was replaced), text that forbids card 0 because it overheats is
  stale; so, since 9 October 2026 (aifoundry2's card back in service, cooled by a two-fan 92 mm PCI-slot bracket in the
  slot beside it; out of service 7–9 October, and 2–6 October), is text that forbids aifoundry2's card, or treats it as
  the main card or the one to run on. Two kinds of text stay as they are: the
  dated record of 25 September to 9 October, and the frozen or
  pre-registered experiment code (`tools/claims-v3/*`, `workloads/pciebench`), whose card-0 refusals stay;
  `workloads/sparseparity`'s scripts also use only card 1 on aifoundry1. The workload READMEs' `aifoundry2` commands
  reproduce that card's September data, and since 9 October it runs cooler than it did then: compare with care.
  On 2 October the `et-lab-start` installed
  in `/usr/local/bin` on the three hosts was still the 30 September third version, and the installed `/etc/motd`
  banners predated 2 October (both need root to update): where they differ from `docs/lab-start/START.md`, the brief
  holds.

## 4. The machines

**The simulator.** On a Mac, all ET tooling runs in the Lima VM `et` (`scripts/create-vm.sh`), and every build or run
command is prefixed with `scripts/vm`. On any other Ubuntu 24.04 box, `scripts/clone-upstream.sh && scripts/provision-vm.sh`
builds the same `/opt/et` natively (the README's setup section). **Never run `provision-vm.sh` on a lab machine**: its
`/opt/et` is the lab's. `sys_emu` is functional only: it checks correctness, never speed.

**The lab.** Three x86_64 Ubuntu 24.04 machines on AI Foundry's Tailscale tailnet, four cards, all four in service
(aifoundry2's again since 9 October 2026, with a two-fan bracket at the card; it was out 7–9 October and 2–6 October):

| Card | Firmware | Clock policy | Notes |
|---|---|---|---|
| aifoundry2 | 1.4.0 (BL2 0.22.0; read 27 Oct 2026, E69) | the firmware's DVFS: 600–800 MHz, above 600 only on a die below about 68 °C; it still runs at 600 in about 99% of samples since 9 Oct, though the die now idles at 51 °C | **back in service since 9 Oct**, when the stalling 120 mm fan clipped under the card was taken out and a two-fan 92 mm PCI-slot bracket was fitted in the slot beside it (on site, 14:55–15:17 PDT; the card is passive, and the bracket blows straight across its heatsink): it idles at 51 °C and 23.2 W (aifoundry3's twin card 53 °C and 24.3 W), levels off at 62–63 °C under 8 minutes of sgemm bursts, and ran the heavy run's full 600 s at 75 °C and 59 W with no stop and no driver or PCIe errors ([the 9 October page](https://spacesheep.dev/@yaroslavvb/aifoundry-lab-9-october), `docs/reports/data/2026-10-09-fan-swap-aifoundry2/`). Keep a temperature stop (85–90 °C) on long full-load runs, as the lab's scripts already do: by a one-node steady-state model the idle card has no resting temperature from 1.9 times worse cooling, and under sustained full load from 1.2 times. **Never power it without the bracket:** with no fan at all the idle card heated by 4.4 °C a minute (44 → 87 °C on 9 Oct, booted before the bracket was back in). Out of service 7–9 Oct: idle and with nothing on it, it ran away and dropped off the PCIe bus at 16:46 on 7 Oct, at a 138 °C mean (hottest sensor 144 °C) and 133 W, as on 2 Oct (138 °C, 144 °C, 134 W). With every fan at full speed in the BIOS since 6 Oct it had idled at 63–69 °C and 27–30 W through the night; at 03:55 on 7 Oct, with the host idle and the host's own sensors unchanged, the cooling at the card got worse in one step (64 → 78 °C by 04:50), again at about 14:25, and it ran away from about 16:25. Its power followed the 2 Oct leakage law within 0.25 W rms over the day, so the card did not change; the air reaching it did (by the 2 Oct model, from about 39–42 °C to about 51 °C). Fan speeds are not visible from Linux here, and the stalling fan was found only on site, on 9 Oct ([the 7 October page](https://spacesheep.dev/@yaroslavvb/aifoundry2-idle-runaway-7-october), `docs/reports/data/2026-10-07-idle-runaway-aifoundry2/`). Brought back on 8 Oct at 14:47, the idle card crept up from about 71 °C and ran away again at 19:36–19:49 (138 °C, 134 W), and stopped answering. In service 6–7 Oct: it idled at about 64 °C and 27 W, peaked at 76 °C under 8 minutes of sgemm bursts, and at full load on every minion reached 90 °C after 37 s instead of 19–27 s ([the 6 October page](https://spacesheep.dev/@yaroslavvb/aifoundry-lab-6-october), `docs/reports/data/2026-10-06-fan-fix-aifoundry2/`). Out of service 2–6 Oct: its cooling failed. It dropped off the PCIe bus while idle on 1 Oct (09:42); after a full (cold) reset at 10:53 on 2 Oct it heated, idle and with nothing on it, from 45 °C to a 138 °C mean (134 W) in 69 minutes and dropped off again, and no firmware cut-off acted (`docs/reports/data/2026-10-02-idle-runaway-aifoundry2/`). Until then it was the main card. The machine is up, and the git checkout is `~/claude/et-soc1-prototyping` here. Its Master Minion hung at 02:50 PDT on 28 Sep; the management reset restored it at 08:32 (owner-approved; the sysfs per-card reset had not), and it ran kernels again (14-card-behaviour.md). DV2's validation ran there from 20:45 PDT on 28 Sep to 16:57 PDT on 29 Sep, then the third card's pcie2, nocr and memp2 (16:59–17:38) |
| aifoundry3 | 1.4.0 (BL2 0.22.0; read 31 Oct 2026, E79) | **pinned at 600 MHz**: a boot service sets a 0 W TDP at every boot. At BL2 0.22.0 that is a reversible pin at the 600 MHz floor, not a latch (section 5): the clock never steps, and only writing the TDP back — a governor move, which needs the owner's authorization — would release it | compare switching power over idle, never absolute watts; about 1 host launch in 100 crashes at 1.08 s unless the program registers libetrt's log levels first (`registerRuntimeLogLevels()`, 14-card-behaviour.md) |
| aifoundry1 card 0 | 1.4.0 (BL2 0.22.0, PMIC 1.6.1; read 31 Oct 2026, E84 A1 — not the 1.4.1 / BL2 0.21.2 on record before) | DVFS under BL2 0.22.0, the version aifoundry2 reports: TDP 65 W / 65 °C, and read idle at 600 MHz / 519 mV on 31 Oct where this table said it idles at 300 MHz under a 0.21.x governor that acts only while a kernel runs. 🛑 Its PMIC's 75 W over-power alarm is a third limit: fp32 random data at 800 MHz (72–75 W on the board) trips it and drops the card to a 300 MHz safe state about once a second (E84; 14-card-behaviour.md) | **back in service since 2 Oct**, when its broken fan was replaced: 49 °C idle (hottest sensor 53 °C), 52–53 °C (hottest 56 °C) under 8 minutes of sgemm bursts, cooler than card 1 under the same test (59–60 °C, hottest 63 °C; `docs/reports/data/2026-10-02-fan-fix-aifoundry1/`). From 25 Sep until then it overheated (115–117 °C on the host on 25 Sep; its service processor's statistics held a 119 °C mean and a 123 °C sensor) and took no sustained work; excluded from the campaign |
| aifoundry1 card 1 | 1.4.0 (BL2 0.22.0, PMIC 1.3.0; read 31 Oct 2026, E82 A1 — not the 1.2.0 / BL2 0.18.0 on record before) | 600 MHz in every sample since 25 Sep, cool or hot, busy or idle — still so under BL2 0.22.0 at TDP 65 W / 65 °C (E82: all 375 smoke samples at 600 MHz at up to 56.8 W): its governor never raises the clock, and why is not established (asked the lab) | fine; select a card on this host with `ET_DEVICES=<n>` and take its lock, `etsoc-shire<n>.lock` (one person per card) |

**When a card goes out of service or comes back**, change everything that states it in one commit:
[`docs/lab-start/README.md`](docs/lab-start/README.md#keeping-it-current), "Keeping it current", lists the files and
pages, the new-user page's Machine field among them. That field is why (14 October 2026, Q114): it never offered
aifoundry2 after the card came back on 6 and 9 October, because neither update listed it. `docs/lab-start/make_page_data.py`
now refuses to rebuild the page while the field and the brief disagree.

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
card resets, services), which is the lab admin's; any change to an existing page's visibility, which is the owner's (new report pages are published public by default,
the owner's rule of 29 September; §8); and
claiming a machine on the AI Foundry Discord (#community-lab: "using aifoundryN", then "released"), the lab's own norm
(getting-started.md §2). **The owner's agents make at most one card post a day, and every later reservation that day
edits it** (the owner's rule of 1 November 2026: *"only post at most once per day when I'm reserving things. If
multiple times I'm reserving, just edit that message with reservation (erasing the previous one)"*). It is `<ai>` plus
one short clause per card held, naming the box, with at most one small link to the public spacesheep page that
describes the run, **and how long they hold the card**: `<ai> **Claude says:** using aifoundry3 for 1.5 h, until
~14:30 PST [doc](<https://spacesheep.dev/@yaroslavvb/…>)`, the duration in digits after `for` (`for 2 h`, `for 1.5 h`;
the reservation reader parses that form and misses `~2 h` or `about 2 h`) and the clock time it ends, in the zone
`date +%Z` prints (PST from 1 November 2026). The day's first reservation posts it. Every later change rewrites that
post with the Intel's `edit_replace.mjs` under `EXPECT_TEXT`, which refuses (exit 7) if another session rewrote it first.
A new reservation's text is the clauses of the cards still held plus its own, `; ` between them, so a released one is
erased; a card released while another is held drops its clause; the last card held gets ` — released` appended,
keeping its words. A clause's `for <N> h` counts from its hold's start (the post, or the edit that added it), in a
re-estimate too: a run that will overrun by more than 15 minutes rewrites its clause, so a hold from 13:00 that will
now end at 15:30 reads `for 2.5 h, until ~15:30`, never the time left. The lab dashboard's reservation reader keeps each
version of the post: a hold starts where its clause appears and ends at the edit that releases or drops it, so a
re-worded clause loses its span. No plan, numbers or progress in the channel, and no second post that day: the page
holds it (the owner's rules of 28 October 2026; the estimate since 31 October; one post a day since 1 November). The
owner's two newest card posts in the channel (today's and yesterday's) stay, and each older one is deleted once its
card is released, except one that a record cites by id (this repo's data READMEs and findings, the owner's research
log), which stays so the citation still opens (the owner's rule of 31 October 2026). Only the Intel deletes them, through the Discord client with its
`delete_msg.mjs`; an agent here never deletes a post.

## 5. The lab's etiquette, and why

The owner's rules (CLAUDE.md, getting-started.md §2), the lab's norms and the lessons behind them, each with its
reason:

| Rule | Why |
|---|---|
| Ask which machine (and card) to use; stay off cards other sessions use (aifoundry1: one person per card) | the cards are shared with other people, CI runners (aifoundry1, aifoundry2), a demo (aifoundry3) and our own campaign queues |
| Look first: `et-who`, `who`, `uptime`; hold card N's lock for your run (`flock -n /run/lock/etsoc-shire<N>.lock <cmd>`, which fails at once if someone holds it) | the management node is single-opener, and a second user of a card corrupts both measurements |
| Never hold a device for more than 10 s: `timeout 10` on every launch (per device-opening process; release the card lock between sub-tests) | long holds block everyone else, and a card that hangs needs a power cycle only the lab admin can do |
| Stop tools with Ctrl-C or a plain `kill`, never `kill -9` | a sampler killed mid-request poisons the card's management queue for the next user |
| Never reset a card, retrain or re-speed its PCIe link, or touch its firmware, driver or clocks — no OTA, no flashing, no PMIC commands except the samplers' statistics reset (`ettelem sample --reset-ms`, which the SP forwards to the PMIC: allowed by the owner's ruling of 31 October 2026, and left out of any run that tests the governor's power loop, since it restarts the PMIC's running average), no `SET_FREQUENCY`. **The governor is the one exception:** the owner may authorize a governor move — the static TDP level and the software temperature threshold — for one named run, and it then follows the ET-SoC-1 firmware field manual (private; on the lab boxes in `~/claude/aifoundry-setup/field-manual/`): its pre-flight gates **cover a governor move too**, with a change record (PASS / FAIL / UNKNOWN per gate, UNKNOWN never PASS) **committed with the run's data directory**, the card exclusive for the window, and the original values read first, restored afterwards and read back. **The envelope the owner set (Tue 27 Oct 2026; the manual itself carries no numbers):** static TDP ≤ 75 W (the firmware accepts 0–75 W, [review-governor.md](docs/reports/data/2026-09-28-dvfs2-aifoundry2/plan/review-governor.md)); a *raised* software threshold ≤ 70 °C, aborting at a die ≥ 72 °C or board power ≥ 85 W; lowering either is the safe direction thermally — but a TDP at or below a pattern's own 600 MHz power pins the clock at the 600 MHz floor. At BL2 0.22.0, the build all four cards report since 27–31 October 2026, that pin is **reversible**: the power check is one pass per DM-task pass that steps one VMIN point and returns (`thermal_pwr_mgmt.c:864-926`), its 1.05 × TDP guardband macros are defined and never used, and POWER_UP is always allowed, so there is no power-down loop and nothing latches; writing the original TDP back releases the clock on the next pass (E72: 600 → 700 → 800 MHz inside one 6 s launch, no reset), and at the floor, where the firmware's power arm has no step left, the host harness's own power abort is the guard that acts. aifoundry3 sits pinned that way at the TDP of 0 its boot service sets at every boot; the never-exiting loop and the latch are BL2 0.20.0's ([14-card-behaviour.md](docs/findings/14-card-behaviour.md), "The governor's two knobs"; [V3-KNOB](tools/claims-v3/knob/README.md)). **Before any set,** read the firmware source of the *exact running build* and show that `SET_MODULE_STATIC_TDP_LEVEL` and `SET_MODULE_TEMPERATURE_THRESHOLDS` write no flash or persistent configuration in that build — else NO-GO: one older BL2 build wrote every NoC voltage set to flash where the lab's current build does not ([05-claims.md](docs/findings/05-claims.md) § NV) | a software reset can hang a card; a link retrain on aifoundry1 on 30 Sep hung the whole host until someone power-cycled it on site; a configuration change silently alters other people's runs — so an authorized governor move is a measurement with a receipt and an owner, never a setting left behind, and a clock is reached only through the governor, never set directly. The abort bounds are tighter than the 85–90 °C stop used on ordinary full-load runs because raising the software threshold is exactly what removes the card's own brake, and this card has an idle-runaway history (section 4) |
| Keep disk and memory small: sources only, `nice -j4` builds | the machines are shared, and aifoundry1's `/home` is one pool with the system that filled up once (99% until 30 September; 116 GB free since) |
| An agent that only writes code never reaches a card: `V3_DRY=1`, then check `et-who` | on 25 September a code-only agent ran a real block because a `cd` in a backgrounded chain did not apply |

## 6. The traps, in brief

Each links to the full entry in [14-card-behaviour.md](docs/findings/14-card-behaviour.md).

- **The governor is thermal first**: above 65 °C a card sits at 600 MHz, below it a busy card steps up to 800. On
  aifoundry2, heat the die past 68 °C before any power burst, and check `mhz.minion` in every sample
  ([the governor](docs/findings/14-card-behaviour.md#the-clock-governor-is-thermal-first)).
- **aifoundry1 card 0's PMIC alarm**: on fp32 random data at 800 MHz its PMIC's 75 W over-power alarm drops the clock
  to a 300 MHz safe state about once a second (E84: in every fp32 random run, no other); under release 1.4.0 / BL2
  0.22.0 the card idles at 600 MHz, not at the 300 MHz recorded under 1.4.1 in September. On the other three cards no
  measurement here shows a PMIC alarm acting: host-side aborts are the guard
  ([the alarm](docs/findings/14-card-behaviour.md#aifoundry1-card-0s-pmic-over-power-alarm-a-third-speed-limit-31-october-2026-e84)).
- **A hot start does not hold the clock down**: at the 65 °C trip aifoundry2's clock cycles 600–800 MHz about once a second, and
  the matmul benchmark's fp16 random data read 101.15 W on its board, over E101's 97 W stop, and random fp32 with tiles that fit the
  L2 sits at that stop (E105). Keep a board stop on a streaming kernel, and estimate a cell from its own kind's S on a pinned card,
  never a lower kind's rho ([the entry](docs/findings/14-card-behaviour.md#a-hot-start-does-not-hold-the-clock-down-and-a-real-kernel-can-read-over-100-w-aifoundry2-1-november-2026-e101)).
- **No host compute on any box beside a card run**, your own lane's included: a settled reading needs the room quiet and an
  inlet read beside it (E97, not shown causal; [the trap](docs/findings/14-card-behaviour.md#traps-that-cost-time-here)).
- **A desk emulation is not a read-back**: E88's and E92's fp16 "frozen" sums walk on silicon (E104). Read C back before
  registering a state of C (`--dump-c`, `tools/claims-v3/kinds/patch_host_e104.py`). And build the RTL benches with
  `-fno-dfg`: Verilator 5.052's optimiser miscompiles the multiply-add (`rtl-sim/fma_toggle_v2/`, Q132(b)).
- **The telemetry lies in specific ways**: whole-degree die readings, rails that are a PMIC running average
  (τ 1.01–1.06 s on aifoundry3 and 1.08 s on aifoundry1's card 1, published one SP pass late; 0.54 s on card 1's SRAM
  rail: E58), a board value that changes once per service-processor pass (133 ms on aifoundry2, 135 on aifoundry1's
  card 1, 224 on aifoundry3 with nothing polling; under ettelem at 10 Hz 156, 158 and 263 ms: E41), and some workloads
  starve the meter: check `took_ms` ([telemetry](docs/findings/14-card-behaviour.md#the-telemetry-and-what-each-number-really-is)).
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

- **While a `tools/claims-v3` queue runs, never rebuild into a build directory its blocks use**: `build/<name>/` for
  enercat, memhier, memprobe, nocbench, onchip, sparsity and sgemm, `build/enercat_v2/`, `build/enercat_gs/` (the
  gathers and scatters, E48), `build/ettelem/`, `build/claims-v3-bin/`, `build/memprobe-data/`, and on
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
- **The DV2 validation lock (28 September until that validation ended, at 16:57 PDT on 29 September on aifoundry2;
  reduced that evening, `e4d894d`).** `tools/claims-v3/dv2v/LOCK.sha256`
  pins 19 files, and every validation pass runs `sha256sum -c` on it and refuses to start on any difference: in
  `tools/claims-v3/dv2v/` `block.sh`, `val.json`, `vn_check.py`, `reduce_val.py`, `prereg-val.json`; in
  `tools/claims-v3/dv2/` `block.sh`, `dv2lib.sh`, `dv2lib.py`, `dv2obs.py`, `sptrace_events.py`, `placements.json`,
  `reduce_dv2.py`; the shared framework `tools/claims-v3/lib.sh` and `tools/claims-v3/queue.sh`; both validation
  schedules, `tools/claims-v3/schedule-dv2val-aifoundry2.txt` and `schedule-dv2val-idle-aifoundry2.txt`; and the
  binaries `build/ettelem-dv2/ettelem`, `build/sparsity_t2/host/sparsity_host` and
  `build/sparsity_t2/kernel/sparsity.elf`. Edit none of them, rebuild none of those binaries, and merge nothing into
  the checkout that runs the validation that touches them, until it ends; run `sha256sum -c
  tools/claims-v3/dv2v/LOCK.sha256` after every merge. A merge of main once broke it (`a745199`, a comment in
  `lib.sh`): the branch `dvfs2` keeps `lib.sh` at the locked bytes (`d884e53`'s), so merging `dvfs2` into main reverts
  that comment. The validation has ended, so this lock holds nothing back now, but `lib.sh` and `queue.sh` are also in
  the heat-placement lock (`tools/claims-v3/hp/prereg/PREREG.md`), whose `reduce.py --val` refuses to reproduce
  `val.json` on any changed byte: they stay as frozen, and `a745199`'s comment waits, until the owner decides about
  that lock (`docs/reports/TODO.md`, part B).

**Run one workload on a card by hand** (in the host's tree, `~/nekko` on aifoundry3 and aifoundry1, the repository's `build/` on aifoundry2):

```bash
cmake -S workloads/sgemm -B build/sgemm-mine -DCMAKE_PREFIX_PATH=/opt/et -Wno-dev && nice cmake --build build/sgemm-mine -j4
et-who                                            # nobody on the card? (and ask first: section 5)
et-lab-manifest > build/sgemm-mine/manifest.txt   # the machine facts, saved with the data
flock -n /run/lock/etsoc-shire0.lock timeout 10 build/sgemm-mine/host/sgemm_host -n 512 --reps 3
```

On aifoundry1, add `ET_DEVICES=<n>` before the program and take `etsoc-shire<n>.lock` for the card `<n>` you were
given (1 or 0; card 0 is back in service since its fan was replaced on 2 October 2026, and the other card may be
someone else's: one person per card). There `et-who` and `et-who --check` count both cards, so look for your card's own
lines (`/dev/et<n>_…`, `lock:etsoc-shire<n>.lock`). aifoundry2's card is back in service since 9 October (it was out
7–9 October, and 2–6 October).
The telemetry client builds the same way (`cmake -S tools/ettelem -B build/<dir> …`); build it on each host,
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
at its timeout, and the hosts' Wi-Fi drops now and then. A `pgrep -f` over `ssh` matches its own command line: use a
bracketed pattern (`pgrep -af '[q]ueue.sh'`).

**Recording.** Commit raw data under `docs/reports/data/<date>-<name>-<host>/` with a README that says what ran,
when, on which card, with which command, plus the `et-lab-manifest` output. Register the experiment in 03, its
numbers in 05, the request in 02, and any published artifact in 04 and MIRROR.md.

**Working files: never only in `/tmp` (30 September).** Anything worth more than a few minutes of work (results, raw
data, logs, briefs, specs, plans, screenshots you will cite, test runs) goes in the repository, committed, or in
`~/claude/work/<topic>/` on aifoundry2 (persistent, outside the repository, not public), never only in `/tmp` or in the
Claude session scratchpad (`/tmp/claude-<uid>/…`), which a reboot or a power cycle clears. Claude Code tells an agent
to keep intermediate results in that scratchpad; here it is only for throwaway files (a render directory deleted right
after, a lock). A subagent's brief names the persistent directory it writes to. A long run writes its log under the
home directory (`build/` in the tree, or the topic's directory), since the harness keeps a background command's output
in `/tmp` too. On aifoundry1 and aifoundry3 work stays in `~/nekko` and comes back to aifoundry2 or the repository;
aifoundry1's `/home` shares one pool with the system (99% full until 30 September, 116 GB free since). Why: the
power cycle of 30 September at about 15:07 PDT, after the link retrain of section 5 hung aifoundry1, cleared `/tmp`
on all three machines, and with it about 19 GB of our agents' working files on aifoundry2 (an earlier copy kept
what was there at 06:37 on 28 September; everything written after it was lost). The repository and the home
directories were intact.

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
   ([MIRROR.md, "Deploying one page"](docs/reports/MIRROR.md#deploying-one-page)). A new report page is deployed
   with `--visibility public` (the owner's rule of 29 September: the experiments are for sharing; the CLI's default
   is private), unless it holds something §10 keeps out of public view. Public by default covers reports, never operational pages: anything with addresses, host or tailnet names, ssh, root or sudo steps, accounts or instructions for an agent is deployed `--visibility private` (on 1 October an agent-instructions page went out public with two tailnet addresses and root steps; check-mirror's "public space not listed" warning caught it and it was set private). Check `spacesheep --version`: the pages up
   to 25 September were deployed with 1.5.1; 1.9.1 (npm's latest from the evening of 25 September) reads them back the same, and a 1.9.1 redeploy
   of an existing space keeps its slug, title and visibility (tested 25 Sep, 23:40). An older CLI (npm's latest was
   1.2.1 until then) may not. Never put the CLI's key in the repository.
5. **Verify**: `spacesheep list` (visibility and address unchanged), then `python3 scripts/check-mirror.py --only <slug>`.
   An animated page (the chip diagram, the memory levels): after a change to its motion, measure it frame by frame with
   [`tools/pagemotion/`](tools/pagemotion/README.md) (late frames, and the camera's velocity from frame to frame),
   before and after, one run at a time with a kept Chrome profile.
6. **Commit** the page, its sources and data, and MIRROR.md together.
7. **A lab page joins the dashboard's Worklog** (the owner's asks of 7 and 8 October 2026: dashboard > worklog >
   page, each linking up). Right under the page's title goes
   `<p data-ss-id="nav-lab-dashboard" data-ss-react="off"><a href="https://spacesheep.dev/@yaroslavvb/aifoundry-lab-dashboard">← AI Foundry lab dashboard</a> › <a href="https://spacesheep.dev/@yaroslavvb/aifoundry-lab-dashboard#worklog">Worklog</a></p>`
   (HTML, not a markdown link: a converter styles the first plain paragraph as the lede), and the page gets one line
   under its day in the Worklog of `tools/lab/dashboard/page/body.html` (its `TO ADD A DAY` comment). The Worklog
   reaches the live page only when the collecting machine's checkout is pulled and `update.sh now` runs; an edit made
   on the live page is overwritten by the next deploy, within the hour. The 2 and 7 October pages went out without the
   line, written by sessions that never saw the rule.

A page written for one person, or one with sensitive content, stays private and is never mirrored here.

## 9. The spacesheep mirror index

[`docs/reports/MIRROR.md`](docs/reports/MIRROR.md) lists every page of the set: title and address, space uuid,
visibility, repo file, deploy form, how it is built, and the private pages with the reason each is not mirrored.
`python3 scripts/check-mirror.py` compares every public page with its file: through `spacesheep read` when a key is
configured (and then also each page's visibility and slug against the account's listing), otherwise anonymously over
HTTPS. It exits non-zero on any difference. MIRROR.md's "Last check" records the latest run.

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
   `pgrep -af '[q]ueue.sh'`, and the tail of `build/claims-v3/queue-*.log` in the campaign's tree
   (`~/claude/et-soc1-prototyping` on aifoundry2, `~/nekko` on aifoundry1 and aifoundry3). Keep the brackets: over
   `ssh` an unbracketed `pgrep -f` matches its own command line, because the processes that run a remote command
   carry the whole command (Tailscale SSH's `tailscaled be-child ssh … --cmd=<the command>`, and `bash -c`). In a
   script, use `et-who --check` (installed on all three hosts since 28 September: exit 0 free, 1 held, 2 failed; on
   aifoundry1 it counts both cards, and since 2 October 2026 other people use card 0 too, so a script for one card
   looks for its own card's lines, `/dev/et<N>_…` or `lock:etsoc-shire<N>.lock`, and stops on exit 2), or keep only
   `et-who`'s lines that start with `/dev/et` or `lock:`.
5. Ask the owner what to work on, which machine and card you may use, and whether any running queue must be left
   alone (assume it must).
6. Ask a person for the steps only a person can do, when you reach them: the Tailscale approval, `spacesheep login`,
   a push.
7. Run `python3 scripts/check-mirror.py` (read-only) to see that the published pages still match the repository.
8. Before any card work: a dry run, a smoke, `timeout 10`, the card lock, and `et-lab-manifest` saved with the data.
9. Write each lesson into the repository as you learn it (section 10), and keep getting-started's status current.

## Changelog

*Every edit to this file adds one line here, newest first, in the same commit, and the newest 15 stay here; older
entries move verbatim to [`docs/agent-changelog-archive.md`](docs/agent-changelog-archive.md) (the owner's rule of
10 October 2026 for agent instruction files). It starts on 14 October 2026; earlier changes are in
`git log -- AGENT.md`.*

- **2026-11-01 (Sun, week 44, Q134 records)** — Section 3's index reads Q1–Q135 and E1–E125, where it read Q1–Q133 and
  E1–E118: E119–E125 are Q134's seven card experiments, E120 among them a governor move; E77's line says it is recorded
  beside E120, its redesign, where it said "recorded after its verification". The 27 October entry, the oldest of 16,
  moved verbatim to [`docs/agent-changelog-archive.md`](docs/agent-changelog-archive.md). *Why:* constraint — Q134's
  records add E119–E125 and E77's corrected result to `docs/findings/03-experiments.md`, and
  `docs/findings/02-requests.md` already cites Q1...Q135 (Q135, another session's request, recorded in `fbcc6803`);
  re-check: the last entry heading of 03-experiments.md and the "Cite as" line of 02-requests.md. And preference — the
  owner's rule of 10 October 2026 for agent instruction files, which keeps the newest 15 entries inline.
- **2026-11-01 (Sun, week 44, Q133 records, corrections after verification)** — Section 3's index says E114 re-ran
  card 0's fp16 and int8 sustained cells on the same card, where it counted them among the replicates on second cards.
  The changelog keeps its newest 15 entries here, and 14 October's moved verbatim to
  [`docs/agent-changelog-archive.md`](docs/agent-changelog-archive.md). *Why:* constraint — E114 ran on aifoundry1's
  card 0, the card E84 ran on, as the Q133 records' verifier found; re-check: the headers of
  `docs/reports/data/2026-11-01-e114-card0-replicates/README.md` and E84's data README. And preference — the owner's
  rule of 10 October 2026 for agent instruction files, which keeps the newest 15 entries inline.
- **2026-11-01 (Sun, week 44, Q133 records)** — Section 3's index reads Q1–Q133 and E1–E118, where it read Q1–Q132
  and E1–E106: E107–E116 are Q133's ten card experiments, E117 the governor move it did not run and E118 the one it
  made on aifoundry1's card 0; E77's line says it was registered and run on 1 November and is recorded after its
  verification. *Why:* constraint — Q133's lanes committed E107–E118's data and their corrections after verification that
  day; re-check: the data READMEs under `docs/reports/data/2026-11-01-e1*/` and the last rows of
  `docs/findings/02-requests.md` and `03-experiments.md`. And preference — the owner's ask that morning, *"continue
  filling out the missing parts (Esperanto only) found by the critics"*.
- **2026-11-01 (Sun, week 44)** — Section 4: the owner's agents make at most one card post a day in #community-lab.
  The day's first reservation posts it, and every later change rewrites it with the Intel's `edit_replace.mjs` under
  `EXPECT_TEXT`. It names every card held, one `; ` clause each: a new reservation erases the released ones, a card
  released while another is held drops its clause, and the last one gets " — released" appended. A clause's `for <N> h`
  counts from its hold's start, and today's and yesterday's posts are the two that stay. *Why:* preference — the owner's
  words that evening, *"only post at most once per day when I'm reserving things. If multiple times I'm reserving, just
  edit that message with reservation (erasing the previous one)"*, after his agents had made 27 card posts that day;
  constraint — the reservation reader kept only a post's latest text and started every hold at the post's time, so it
  now keeps each version, and two sessions sharing one post can overwrite each other; re-check: flush-util
  `test_lab_reservations` (its section 7) and `EXPECT_TEXT` in `edit_replace.mjs`.
- **2026-11-01 (Sun, week 44, Q132 records, E105 and E106)** — Section 3's index reads E1–E106, where it read E1–E104, with E105
  (the port's layout) and E106 (held signs on one card). Section 6's hot-start trap adds that random fp32 with tiles that fit the L2
  sits at the 97 W stop, and that a cell's power is estimated from its own kind's S on a pinned card, never a lower kind's rho.
  *Why:* constraint — E105's power rule admitted the one cell it existed to catch: estimated 87.83 W, read 95.2 W, peaked at 96.25 W;
  re-check: `docs/reports/data/2026-11-01-e105-gemm-layout/README.md`, "The power rule did not do what it was for",
  `aifoundry2/admission.json`, and the last rows of `docs/findings/03-experiments.md`.
- **2026-11-01 (Sun, week 44, Q132 records)** — Section 3's index reads Q1–Q132 and E1–E104, where it read Q1–Q131 and E1–E91
  (E92–E104 are the night's thirteen card experiments; A1–A25 is unchanged, and E105 and E106 are not in yet). Section 2's
  map names `rtl-sim/fma_toggle_v2` and `-fno-dfg`. Section 6 adds three traps: a hot start does not hold the clock down
  (E101), no host compute on any box beside a card run (E97), a desk emulation is not a read-back with `-fno-dfg` beside it
  (E102, E104, Q132(b)), and card 0's trap says no measurement shows a PMIC alarm acting on the other three cards. *Why:*
  constraint — E101's 101.15 W stop, E97's plateau moves (cause not established), E104's read-back and Q132(b)'s optimiser
  fault; re-check: `docs/reports/data/2026-11-01-e101-real-matmul/README.md` session 2,
  `docs/reports/data/2026-11-01-e97-heat-low-power-steady/corrections-check.txt` [C2], `.../2026-11-01-e104-c-readback/scored.json`
  `readback.rows`, `rtl-sim/fma_toggle_v2/verilator_dfg_reproducer.sv`, and the last rows of `docs/findings/02-requests.md` and
  `03-experiments.md`.

- **2026-10-31 (Sat, week 44, Q130 addendum fixes)** — Section 5's rule carves the samplers' statistics reset
  (`ettelem sample --reset-ms`, which the SP forwards to the PMIC) out of "no PMIC commands": it is allowed, and left
  out of any run that tests the governor's power loop, since it restarts the PMIC's running average; every other PMIC
  command stays forbidden. Section 6's trap "Firmware 1.4.1 idles at 300 MHz" is replaced by card 0's PMIC alarm (a
  300 MHz safe state about once a second on fp32 random data at 800 MHz, E84) and its 600 MHz idle under 1.4.0 / BL2
  0.22.0, which section 4's card 0 row already said. *Why:* preference — the owner's ruling that evening, asked after
  E85 (C1) found the camera runner's once-a-second reset reaching the PMIC: *"Yes, you can do the statistics reset."*;
  constraint — the Q130 records' verifier found section 6 contradicting section 4; re-check:
  `docs/reports/data/2026-10-31-e84-speed-aifoundry1-card0/corrections-check.txt` [C6] (every run's idle at 600 MHz,
  300 MHz only in the alarm runs) and `posthoc/pmic.json` (the alarm lines).
- **2026-10-31 (Sat, week 44, Q130 addendum)** — Section 3's index reads Q1–Q131, E1–E91 and A1–A25, where it read
  Q1–Q130, E1–E85 (E84 and E85 in progress) and A1–A24: E84–E91 are recorded (the afternoon's speed replicate on
  aifoundry1's card 0 and the camera per kind; the evening round's real-tensor energy and speed, result path,
  low-power heat, signs and spread, and the real tiles on card 1, not scored), Q131 is the chip diagram's first-visit
  pass, and A25 is the kinds-of-numbers page. Its note on governor text, and section 4's card 0 row, now call the
  cards' BL2 0.22.0 a version, not the build of the `353f20e` source: no card exposes a BL2 git hash, so which 0.22.0
  they run is not established, while the one-pass governor and the removal of both loops date from 0.21.0
  (et-platform `60b40c10`) and hold for any 0.22.0. Section 4's card 0 row adds its PMIC's 75 W over-power alarm, which
  drops fp32 random data at 800 MHz to a 300 MHz safe state about once a second (E84). *Why:* constraint — the Q130
  records' verifier found that the earlier wording dropped 14-card-behaviour.md's residual (no BL2 git hash is
  exposed, and 0.22.0 is an open development line whose `[Unreleased]` changelog carries SW-21990 and SW-22147), and
  E84's trace rings logged the alarm; re-check: in et-platform, `git show 60b40c10:device-bootloaders/CMakeLists.txt`
  declares VERSION 0.21.0, `git merge-base --is-ancestor 60b40c10 ce729715` holds (`ce729715` starts 0.22.0), and no
  commit in `ce729715..836a4ab` adds a loop to `thermal_pwr_mgmt.c`; the alarm lines are in
  `docs/reports/data/2026-10-31-e84-speed-aifoundry1-card0/posthoc/pmic.json`; the last rows of
  `docs/findings/02-requests.md` and `03-experiments.md` are Q131 and E91.
- **2026-10-31 (Sat, week 44)** — Section 4: the owner's two newest card posts in #community-lab stay, and each
  older one is deleted once its card is released, except one a record cites by id (this repo's data READMEs and
  findings, the owner's research log); only the Intel deletes them, through the Discord client. *Why:* preference —
  the owner's words at 16:42 that day, *"delete the older ones because it's just spamming the chat"*, correcting the
  reservation rule written earlier that day; constraint — this repo's data READMEs cite card posts by id as claim
  times, and a deleted post's link no longer opens; re-check: `git grep -n -F <post id> -- docs` names a post's
  citations, and the Intel's `delete_msg.mjs --plan` gives each kept post's reason.
- **2026-10-31 (Sat, week 44)** — Section 4: the reservation post's clock time is written in the zone `date +%Z`
  prints (PST from 1 November 2026), and a re-estimate's `for <N> h` is still counted from the post's own time, never
  the time left. *Why:* preference — the owner's words that morning, *"estimate when I'm, holding the card until, and
  then update it"*; constraint — Pacific time leaves daylight saving at 02:00 on Sun 1 Nov 2026, and the reservation
  reader draws a hold as the post's time plus its stated hours, so a re-estimate written as the time left shows the
  card free while it is still held; re-check: `TZ=America/Los_Angeles date -d '2026-11-01 12:00' +%Z` prints PST, and
  the reader's `parse()` sets a claim's limit to its post time plus the stated duration.
- **2026-10-31 (Sat, week 44, Q130 records)** — Section 3's index reads Q1–Q130, E1–E85 (E77 reserved and not
  registered; E84 and E85 in progress when recorded) and A1–A24, where it read Q1–Q66, E1–E59 and A1–A21,
  and its note on governor text now says the `353f20e` description is the cards' own BL2 0.22.0 and the loops and
  the latch are 0.20.0's. Section 4's firmware column carries each card's fresh read — all four report release 1.4.0 /
  BL2 0.22.0 (aifoundry2 on 27 Oct, E69; aifoundry3, aifoundry1's card 1 and card 0 on 31 Oct, E79, E82 A1, E84 A1),
  where it read 1.3.1, 1.3.1, 1.2.0 and 1.4.1 — and aifoundry3's clock policy says its boot-time TDP of 0 is a
  reversible pin, not a latch. Section 5's governor envelope says the same: at BL2 0.22.0 a TDP at or below a
  pattern's own 600 MHz power pins the clock at the floor with no power-down loop to trap it, and writing the TDP back
  releases it. *Why:* constraint — the BL2 0.22.0 source (the single-pass check at `thermal_pwr_mgmt.c:864-926`, its
  guardband macros unused; 14-card-behaviour.md, "The governor's two knobs"; Q130(d)), E72's measured release of a
  TDP-0 pin, and the firmware revisions read on all four cards between 27 and 31 Oct 2026; re-check: the read-only
  `DM_CMD_GET_MODULE_FIRMWARE_REVISIONS` on each card under its lock, and that section of 14-card-behaviour.md.
- **2026-10-31 (Sat, week 44)** — Section 4: a card reservation post says how long the card is held, as `for <N> h`
  in digits plus the clock time it ends (`using aifoundry3 for 1.5 h, until ~14:30 PDT`), is re-estimated in place if
  the run will overrun by more than 15 minutes, and carries the owner's "Claude says:" marking. *Why:* preference — the
  owner's words that day, *"when reserving cards, add an estimate of when it's reserved until"*; constraint — the
  dashboard's reservation reader reads a stated duration only as `for/next/in <number> h|min`, and draws an unreleased
  claim without one for 3 h; re-check: the reader's duration pattern.
- **2026-10-28 (Wed, week 44, correction)** — Section 4: the release is an edit of the reservation post appending
  " — released", not a second post. *Why:* preference — the owner's words minutes after the entry below: *"No, instead
  of posting a second time, it should edit the original post to know that it's been released."*
- **2026-10-28 (Wed, week 44)** — Section 4: the owner's agents post exactly twice per card in #community-lab, a
  one-line reservation and a separate one-line release, each naming the box, with at most one small link to the public
  spacesheep page that describes the run; no detail in the channel and no edit of the reservation. *Why:* preference —
  the owner's words that day, *"I basically just want you to post when you reserve the card and when you release it, and
  each post may have a small link to the spacesheep doc, which describes what you're doing"*, after he deleted four Q129
  claims of 27 October *"because they were too wordy"*.
- **2026-10-27 (Tue, week 44, correction)** — Section 5's governor exception gains what a reader could not find in it:
  the numeric envelope the owner set (TDP ≤ 75 W; a raised software threshold ≤ 70 °C; abort at a die ≥ 72 °C or board
  power ≥ 85 W; lowering safe thermally, but a TDP at or below a pattern's own 600 MHz power latches the governor, as
  on aifoundry3), the duty to read the exact running build's firmware source and show the two DM sets write no flash
  before any set, that the manual's gates cover a governor move rather than sitting beside it, and that the change
  record is committed with the run's data directory. *Why:* the Q129 verifier found the rule as first written carried
  no ceiling, no abort condition and no commit step, on the card with an idle-runaway history; the envelope is the
  owner's own, from his Q129 brief of the same afternoon, and the manual carries no numbers of its own.
