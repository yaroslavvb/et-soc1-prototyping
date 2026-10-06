# Getting started on a new machine

> For the **results** rather than the machinery, read [findings/](findings/README.md): the findings from
> 18–24 September 2026, with a claim index that traces every number back to the experiment and the raw file
> it came from.

This page covers everything needed to pick the work up somewhere else: clone, connect to the lab, rebuild,
rerun, and republish. Claude Code's memory for this project lives outside the repo, on each machine, so this
page, [`AGENT.md`](../AGENT.md) (the entry point for an agent) and `CLAUDE.md` carry the context.

## Where things stand (2026-10-06)

The repository is the source of truth: every result, the experiment that produced it and the raw data are here,
and `docs/findings/` traces each claim to its file. If a session is lost, resume from this page.
Work in progress that is not committed yet is in `~/claude/work/<topic>/` on aifoundry2, never only in `/tmp` or the
Claude session scratchpad, which every boot clears: the power cycle of 30 September (about 15:07 PDT) cleared `/tmp`
on all three machines, and about 19 GB of our agents' working files on aifoundry2 with it
([`AGENT.md`](../AGENT.md) §7, "Working files").

- **The lab, 6 October.** aifoundry2's card is **back in service**. Every fan in its BIOS (Smart Fan 6) now runs at full
  speed, so the case fans no longer slow down when the host's CPU idles. Idle, the card holds at about 64 °C and 27 W
  (on 2 October it ran away to 138 °C); the 8-minute sgemm burst test peaks at 76 °C; at full load on every minion it
  still reaches 90 °C, after 37 s instead of 19–27 s, so keep the 90 °C cap
  ([the 6 October page](https://spacesheep.dev/@yaroslavvb/aifoundry-lab-6-october),
  `docs/reports/data/2026-10-06-fan-fix-aifoundry2/`). The dashboard's "hottest" figure is the highest reading since the card's
  statistics were last reset, not a live one.
- **The lab, 2 October.** aifoundry2's card was **out of service** from 2 to 6 October: its cooling failed. It fell off the PCIe bus while
  idle on 1 October (09:42 PDT); a full-reset power cycle at 06:45 on 2 October brought it back, and it dropped off
  again at 07:42 (126 °C, 103 W). A plain warm reboot at 10:47 did not bring it back; the full reset at 10:53 did, and
  idle, with nothing on it, it heated from 45 °C and 21.9 W to 95 °C and 48 W in 56 minutes, then ran away to a 138 °C
  mean (hottest sensor 144 °C) and 134 W at 12:02:01 and dropped off the bus; no firmware cut-off acted. The fit
  (`docs/reports/data/2026-10-02-idle-runaway-aifoundry2/`: `records.jsonl`, `fit.py`, `fit.txt`): 13.6 W plus a
  leakage part that doubles every 23 °C, cooled into air at about 51 °C through about 0.9 °C/W, where aifoundry3's
  identical card sees about 31 °C; heating and cooling meet near 97 °C, a tipping point. After a full reset the card
  looks healthy for about an hour while it heats. The lab fixed the air reaching it on 6 October (lab
  report SH5; [findings/14-card-behaviour.md](findings/14-card-behaviour.md)); the machine itself stayed up and kept
  the git checkout. **aifoundry1's card 0 is back in service**: its broken fan was replaced on site (host up 12:59), and
  the owner put it back in service at about 13:30. It idles at 49 °C (hottest sensor 53 °C, 19.6 W), and 8 minutes of
  sgemm bursts (8 s of `-n 1024` under the lock, 2.5 s gaps, 44 bursts) held it at 52–53 °C, hottest 56 °C; card 1,
  the same test just before, ran at 59–60 °C, hottest 63 °C (`docs/reports/data/2026-10-02-fan-fix-aifoundry1/`,
  `1674298`). So three cards are in service: aifoundry3's and aifoundry1's two. Select one of aifoundry1's with
  `ET_DEVICES=<N>` and `/run/lock/etsoc-shire<N>.lock`. Two people may work there at once, one per card;
  `et-who --check` there counts both cards (exit 1 if anyone holds either), so a script for one card looks for its own
  card's holder lines (those starting `/dev/et<N>_` or `lock:etsoc-shire<N>.lock`) and stops on exit 2
  ([lab-access.md](lab-access.md)). The new-user brief, [`lab-start/START.md`](lab-start/START.md), is at its seventh
  edition (14:30, `607a44e`): card order aifoundry3, then aifoundry2 (back in service since 6 October), then aifoundry1's card 1, then its card 0; a
  card is free only if its PCIe link is up (sysfs `current_link_speed`, not `Unknown`: a card that fell off the bus
  keeps its `/dev` node), `et-who` shows no line for it, no queue or other card program of another user is in the way,
  and nobody has claimed it. `tools/lab/et-lab-start` in the repository is the fourth version (2 October: `--card N`,
  down-card detection, per-card logic); the copies installed in `/usr/local/bin` on the three hosts are still the
  30 September third version, and the installed login banners (`/etc/motd`) predate 2 October: both need root to
  update, which is not done yet. A live monitor (`tools/lab/live/live-collector.py`, a systemd user service on each
  machine) reads every free card's temperature once a second with `ettelem temp`, only while `et-who --check` exits 0
  on that machine; the [lab dashboard](https://spacesheep.dev/@yaroslavvb/aifoundry-lab-dashboard) has a Live section
  and a [History page](https://spacesheep.dev/@yaroslavvb/aifoundry-lab-history).
- **Sparse parity (Q66, E59): done on aifoundry3's card, 29 September (04:15–11:40 PDT).** Noisy sparse parity
  solved as an int8 tensor GEMM on 1,024 minions, checked by two closed-form checksums and a CPU oracle: L1
  (512, 4, 0.3, 448) 0.131 s, L2 (512, 4, 0.4, 1,850) 0.323 s, (256, 5, 0.4, 1,925) 1.52 s (with the two-stage
  screen); 7.8–12× one core, 1.1–1.6× six tuned AVX-512 threads. Board energy per solve with the idle, measured on
  the one-stage scan: 5.0, 16.6 and 89 J; the board alone, 2.5–7.7× below the CPU's assumed package energy at
  125–251 W (1.6–6.1× with the host that drives the card). The page is public
  ([et-soc1-sparse-parity](https://spacesheep.dev/@yaroslavvb/et-soc1-sparse-parity), deployed on 29 September and made
  public at the owner's word, Q67). The code, its runs and the builds are in `workloads/sparseparity/README.md`, the
  design in `docs/research/sparse-parity/DESIGN.md`, the data in
  `workloads/sparseparity/data/2026-09-29-aifoundry3-{card,card-m4,m5-energy}/`, the page in
  `docs/reports/2026-09-29-sparse-parity.html` (A21). Next steps (cooperative B loads, resident A, a faster row
  generator, more cards): [`reports/TODO.md`](reports/TODO.md), part D.
- **The major pass of 28–29 September (Q65, 20:40 PDT on 28 September to 01:10 PDT on 29 September; DV2's validation
  and the third card's runs ended on the evening of 29 September).**
  - **DV2's validation ran on aifoundry2 and is reduced** (E51, the frozen `PREREG-VAL.md`): 28 September 20:45:39 PDT
    to 29 September 16:56:46 PDT, on the full schedule (the owner accepted a replication on the same card), reduced that
    evening (`e4d894d`). TH3, TH4 and TH8 survived, TH7 fell and the owner's two questions stayed untested (the DV2
    bullet below).
  - **Four pre-registered experiments on the hub's rungs**, each developed on aifoundry1's card 1, frozen, then
    validated on aifoundry3 (28 Sep 23:47 – 29 Sep 01:06 PDT); pcie2, nocr and memp2 also ran on aifoundry2 as a third
    card after DV2 ended (29 Sep 16:59–17:38 PDT, the same frozen locks; `b1198cb`); what survived:
    - pcie2 (E55, rungs 34, 35): two host-to-card DMA commands in flight in one stream move 0.49 of one at 64 MB, but
      one in each of two streams loses nothing (T35-S); a host write lands in the L3 (T34-A). aifoundry2 gave the same
      verdicts. `docs/reports/data/2026-09-29-pcie2/`.
    - nocr (E56, rungs 31, 32): read replies go y first and write requests x first, on all three cards, and the chip
      diagram now draws replies y first (fact L104, measured); links saturate near 92 GB/s. An ESR call costs 1,557 + 35.9
      cycles per hop on aifoundry3 and on aifoundry2 (rms 4.7 and 4.47 cycles, over the frozen rule's 4, so the places
      that rest on a direct call are not decided on either; in development on card 1 the master shire placed at (0,3)).
      `docs/reports/data/2026-09-29-nocr/`.
    - memp2 (E57, rungs 33, 36, 43, energy-manual-102): the L50 bank and row map holds on aifoundry3 (and card 1 in
      development), and on aifoundry2 in 14 of 15 conditions: two lines that differ only in PA[17], a column bit in the
      map, read as a row conflict there (not explained); the refresh domain is the controller on aifoundry3 and
      aifoundry2 (not established on card 1, where R33b failed in development); the L2 keeps TensorLoad lines (a second
      load 199 cycles, on all three cards); no theory of the 128 B per cycle cap survives, on any card; stride-256 reads
      get 0.665 of the bandwidth, at +42 to +50 pJ per 64 B on aifoundry3 (on aifoundry2 the extra energy was not
      resolved: +31 to +36, intervals that include 0).
      `docs/reports/data/2026-09-29-memp2/`.
    - tau (E58, rung 4): the rails' filter has a time constant of 1.01–1.06 s on aifoundry3 (in development card 1's
      SRAM rail read 0.54 s); `tools/ettelem/deconv.py` undoes it. `docs/reports/data/2026-09-29-tau-aifoundry3/` and
      `-aifoundry1-c1/`. Not run on aifoundry2: its `PREREG.md` requires an amendment for that card first.
  - **NV (E54)**, the owner's NoC validation of Q63's voltage explanation: its predictions are frozen and aifoundry3
    was probed read-only (NoC at 485 mV, 400 MHz), but its first voltage write has not run: the session's permission
    check refused it, so it waits for the owner. Its validation is on aifoundry2, after development on aifoundry3
    (`tools/claims-v3/nv/`); aifoundry2's card is back in service since 6 October 2026 (first bullet).
  - **The lab.** aifoundry1 got four of the lab report's fixes at 20:51 PDT on 28 September (owner-approved; logged
    on the host); the other items wait for the owner (`reports/TODO.md`, part 0). aifoundry1's `build/sparsity` was
    rebuilt with the g3log fix. `et-lab-health` rev 3 and `et-reset` were written then; they are installed on all
    three hosts since 30 September ([lab-access.md](lab-access.md)).
  - **The session timeline** page, data and tools are in the repository (`6bbf0f3`, `tools/timeline/`).
  - Open from this pass: [`reports/TODO.md`](reports/TODO.md), part 0 (the owner's: the lab fixes, NV's first
    write), part B (`lib.sh`, which the heat-placement lock holds) and part C (tau on aifoundry2 after its amendment, and
    the open results).
- **aifoundry2 runs kernels again: its card was restored at 08:32 PDT on 28 September** (owner-approved; since
  2 October 2026 its card is out of service, first bullet). Its Master Minion had hung at 02:50:53 PDT during E51's
  development session p6041: a heater launched 0.6 s after the previous one, as the governor's idle reset took the
  clock from 800 to 600 MHz, ran its short calibration kernel and then never completed the next kernel, and every
  launch after it failed with "Couldn't use the HPSQ. Perhaps the Master Minion is hanged?"; the cause is not
  established. The sysfs per-card reset (06:39) re-attached the device but did not recover the Master Minion (launches
  at 06:40 and 06:47 failed the same way); the management reset (`dev_mngt_service -m DM_CMD_RESET_ETSOC -n 0`,
  08:32:45) did, and a 1-minion test at 08:33 ran 3 launches, each ok, at 600 MHz. From 20:45 PDT that evening to
  16:57 PDT on 29 September it ran DV2's validation (above), then the third card's pcie2, nocr and memp2
  (16:59–17:38). Evidence: `docs/findings/14-card-behaviour.md`, "aifoundry2's Master Minion hung on 28 September",
  and `docs/reports/data/2026-09-28-dvfs2-aifoundry2/incident/recovery.txt`.
- **DV2, the DVFS-and-heat experiments (Q59, E51): development and the frozen validation done, reduced on
  29 September.** The owner's questions: does voltage-frequency scaling act on the average temperature or on one hot
  die (Q1), and can the same computation run longer before throttling in some places on the chip (Q2)? The development
  night on aifoundry2 (28 September, 00:33–02:54 PDT; `docs/reports/data/2026-09-28-dvfs2-aifoundry2/`, tools in
  `tools/claims-v3/dv2/`) set the parameters of a validation plan frozen afterwards (`plan/PREREG-VAL.md` there,
  SHA-256 `e150ce16…`; its runner `tools/claims-v3/dv2v/`). The validation replicated it on the same card, the owner
  having accepted that (aifoundry3's governor is latched by its zero TDP and aifoundry1's card 1's never raises the
  clock, so neither can stand in): 378 read-only idle cycles and three heating sessions, 28 September 20:45 PDT to
  29 September 16:57 PDT, reduced that evening by the frozen reducer (`validation/verdicts-dv2val.json`, `e4d894d`).
  Verdicts: no dead band (TH3), the Master Minion's heartbeat sets the launch and end latencies (TH4) and the
  residency counter adds whole episodes (TH8) survived; "an idle exit is followed at once by the idle reset" (TH7) fell,
  1 of 52 exits; the mean against the hottest sensor (TH1, busy and idle), the 0.20.0 loop (TH2) and placement (Q2) are
  untested (INSUFFICIENT). What that answers: Q1 leans to the average but is not settled by the frozen rules: in 17
  runs the clock held 800 MHz for a second or more with the hottest sensor at 67 °C or more (G1-H PASS), and none of
  the 9 runs that tell the rules apart stepped with the hottest sensor, but 7 of 9 fitted the mean where G1-T asks for
  80%, and 4 idle cycles separated the two where I1 asks for 5; the answer rests on the firmware source (the integer
  mean of the 34 sensors). Q2 is open: the perimeter held 800 MHz 1.16–1.52 times as long as the interior in each of
  the 4 blocks with both placements measured, but G4-S needs 6 (99% interval of the log ratio −0.11 to +0.61). Why:
  the card idled at 71–76 °C for most of the 20 hours (327 of 378 cycles), so at rest it seldom crossed the 65 °C
  threshold, and the three heating sessions the plan allows could start (at 60 °C or less) only in an evening cool
  spell, 21:39–23:18 PDT, and each ended when the warming card no longer cooled back to its 62 °C starting edge, after
  1, 2 and 4 blocks begun, leaving 4 complete placement blocks of the 6 needed. A cooler rest would be needed to reach
  the counts. The Master Minion did not hang. The DVFS page's §8 gives the verdicts and the two answers
  (`docs/findings/03-experiments.md`, E51; `docs/findings/16-dvfs-and-leakage.md`). The DV2 lock (`tools/claims-v3/dv2v/LOCK.sha256`, 19 files) held for every pass and was
  checked again before the reduction; its files stay as they ran. `tools/claims-v3/lib.sh` and `queue.sh` are also in
  the heat-placement lock (next bullet), whose reducer re-checks them, so `a745199`'s `lib.sh` comment and part B's
  other `lib.sh` items wait for the owner's decision on that lock ([`reports/TODO.md`](reports/TODO.md)).
- **Heat placement (Q60, E52): development, validation and verdicts done (28 September).** The owner's question of
  27 September: does the same work run longer before the thermal trip in some parts of the chip? Developed on
  aifoundry3 (27 September, 16:52–22:11 PDT): from the same 61 °C start, 512 minions on the 16 perimeter shires took
  1.62 [1.51–1.73] times as long as on the 16 interior shires to bring the mean to 66 °C, in 9 of 9 blocks, at equal
  power (development only). Card 1 of aifoundry1 was calibrated (V0), the predictions frozen at 22:50
  (`tools/claims-v3/hp/prereg/PREREG.md`, SHA-256 `a1bdc4e4…`: PLACE-t and PLACE-tS, both SIGN+), and the validation
  ran there on 27–28 September (the queue ended at 07:49:40 PDT on 28 September; card 1 is free of it). Verdicts
  (`val.json`, `reduce.py --val`, the lock held for all 10 blocks): short bursts PLACE-tS **PASS** (the perimeter
  2.04 [1.73–2.42] times as long, 5 of 5 blocks); sustained heating PLACE-t **INSUFFICIENT** (7 of its 10 runs, 10 of
  all 15 Tier L runs, cut off by the 150 s cap before the trip); transfer H11 INSUFFICIENT; by the frozen table no theory survived and none was
  refuted. Data: `docs/reports/data/2026-09-28-heat-placement/README.md`; the page "Where the work sits"
  ([et-soc1-heat-placement](https://spacesheep.dev/@yaroslavvb/et-soc1-heat-placement), public since 28 September) opens with the summary of which
  theories survived. **The heat-placement lock:** every file `PREREG.md`'s lock lists (in `tools/claims-v3/hp/`: `block.sh`,
  `hplib.sh`, `hplib.py`, `probe.sh`, `reduce.py`, `sptrace_events.py`, `placements.json`, `run_queue.sh`,
  `ettelem-hp/ettelem.cpp`, `prereg/`, `params/params-val-aifoundry1-c1.json`; and `tools/claims-v3/lib.sh`,
  `queue.sh`, `tools/ettelem/ettelem.cpp`, `tools/ettelem/flip_thermal_model.py`) stays byte for byte as frozen, and
  aifoundry1's `build/sparsity/` (the frozen heater) was not rebuilt until the verdicts were reduced (it was rebuilt
  at 20:56 PDT on 28 September, the frozen copy kept as `build/sparsity.frozen-hp-20260922`); the lock files
  stay as frozen, since `reduce.py --val` re-checks them to reproduce `val.json`. Q1's answer (the
  mean) rests on the source and E51: no on-card clock test could run here (both probes SILENT, aifoundry2 resting at
  66–67 °C).
- **The effect of overheating (Q61, E53): done and published (28 September).** The owner's questions of that morning
  (what temperatures processors are built for and why; whether a limit should watch the average or the hottest spot;
  whether heat changes switching speed; why a hot chip stops and then works again) are answered from outside research
  (60 sources) and checked on the ET-SoC-1: its firmware's limits per card build (only aifoundry2's 0.20.0 rule acts; on
  the 0.20.0 and 0.18.0 cards nothing limits the die at 600 MHz), the existing record re-read, and E53, two
  pre-registered experiments on aifoundry3 and aifoundry1's card 1 (10:11–12:05 PDT; `tools/claims-v3/oh/`; frozen at
  10:11, two amendments before the data they touch): the hottest sensor ran 1–3 °C above the 34-sensor mean (at most
  +4), 663 exact-checked launches up to an 81 °C mean computed nothing wrong, and cycles per operation stayed within
  0.05% of rest; 20 of 21 verdicts PASS (card 1's work-per-cycle test INSUFFICIENT: it never passed a 76 °C mean). Data:
  `docs/reports/data/2026-09-28-overheating/README.md`; the page
  [et-soc1-effect-of-overheating](https://spacesheep.dev/@yaroslavvb/et-soc1-effect-of-overheating)
  (`docs/reports/2026-09-28-effect-of-overheating.html`, public). Open: its asks, on the hub as rungs 45 and 46 and
  in rungs 13, 24 and 42; a hotter card-1 run and the rule readings E52 and E53 used, both for the owner (the data
  README, "Rules and their reading").

- **The lab, 25 September (evening).** Four cards work, on three firmware releases: aifoundry2 and aifoundry3 (1.3.1)
  and, since 15:02 that day, aifoundry1's two cards (card 0 on 1.4.1, card 1 on 1.2.0). aifoundry1's cards had been
  refused because its driver module had an empty version string; the fix and the report are in
  `docs/reports/data/2026-09-25-aifoundry1/`. **aifoundry1's card 0 overheated, and took no sustained work until its
  fan was replaced on 2 October 2026** (back in service since; first bullet). aifoundry3's 0 W TDP is set at every
  boot by a service, not flashed. Between 16:14 and 16:27 the three hosts were brought to one configuration
  (performance power profile, chrony, core dumps, `et-who`, card locks, a login banner, `et-lab-manifest`); a full
  upgrade is installed and the reboot into kernel 7.0.0-34 is still pending. What that does to comparability, and
  every card's quirks: `docs/findings/14-card-behaviour.md`. The machines' shared tools: `docs/lab-access.md`.
- **Version 3 of the claims check is finished** (26 September, 06:55). Pre-registered in
  `docs/reports/data/2026-09-25-claims-v3/` (`PLAN3.md`, and `AMENDMENTS.md` A1–A5, each written before the data it
  touches; C1 and C2 are post-data notes), with its code in `tools/claims-v3/`; its queues (`queue.sh` with
  `schedule-<card>.txt`) ran unattended on aifoundry1's card 1, aifoundry2 and aifoundry3 (E35–E47). The results are
  in `docs/reports/data/2026-09-25-claims-v3/results/` (one `<exp>.json` per experiment, each item with its registered
  and all-cards outcome, and `pagemap.md`, every page claim with the items that test it), the raw data in its `raw/`.
  The pages carry its results since 26 September: each tested claim says what the three cards showed, each page
  carries a dated note, and the generators gained version-3 options (`docs/findings/04-artifacts.md`, "Rebuilding the
  version-3 data"). On 27 September they were merged with the review's chart and collapsible-depth passes (below);
  MIRROR.md's "Last check" says whether the live pages equal these files. The gathers and scatters that ran on each
  of the three cards after its campaign blocks (E48, 26 September 03:19–09:22, `tools/claims-v3/gs/`) are reduced
  (`results/gs.json`, `gs-full.json`) and registered, and since 27 September they are on the energy manual (§3.1,
  §4.3, §4.4, §6), memory hierarchy ("Irregular access"), influence functions (S3) and the hub's chart of events (Q52;
  03-experiments.md, E48, "Report").
  To reduce again:
  `tools/claims-v3/collect.sh <dir>` then `tools/claims-v3/reduce_all.sh <dir> <out>` (all-cards outcomes over the
  three campaign cards, `tools/claims-v3/campaign.py`, per amendment A4). Before any card work, check `et-who`: a
  queue stops at the next block boundary when `build/claims-v3/STOP` exists in its tree, and while one runs do not
  rebuild the binaries it uses or run `scripts/deploy-lab*.sh` against its host ([`AGENT.md`](../AGENT.md) §7).
- **aifoundry3's host crash is understood** (25 September, late): a race in the runtime's logging set-up, reproduced
  without a card (E49, `tools/g3log-race/`). Every host program now registers the log levels first in `main`. On 26
  September the fixed gather/scatter build ran 641 host processes on aifoundry3 with no crash (6.4 expected at the old
  rate; E49), and aifoundry2's and aifoundry3's other host builds were rebuilt with the fix after their queues ended.
  On aifoundry1 six were rebuilt with it on 28 September at 07:52, after card 1's heat-placement queue ended
  (enercat, memhier, memprobe, nocbench, onchip, sgemm), and `build/sparsity` at 20:56 (host `e0fbecce…`, the kernel
  unchanged). `build/enercat_v2`, the campaign's catalogue host, stays unfixed on purpose, as on aifoundry3: its cat
  blocks record its hash (`tools/claims-v3/gs/README.md`).
- **The visualization pass (26 September):** charts and controls on 13 pages, the chart toolkit's card registry (a
  third card appears when its data does) and sortable tables; no number changed. Record:
  `reports/data/2026-09-26-visualization-pass/` and `findings/04-artifacts.md`.
- **The review of 26 September:** eight AI review agents read every published page and the repository for
  inconsistencies, room to be more concise and charts worth adding. Repository-only fixes went in with its record;
  its charts were built in the chart pass (26–27 September, 17 pages), and each page's detail was folded into
  collapsible sections (27 September, 20 pages; both in `findings/04-artifacts.md`). The page changes still open wait
  in [`reports/TODO.md`](reports/TODO.md), which starts with items for the owner (two public aifoundry1 pages and a
  committed transcript name other people's home directories). On 26 September at 23:26, before the merge with the
  version-3 pages, the live pages equalled their files (22 of 22, `check-mirror.py`).
- **New pages, 25 September:** [Influence functions on the ET-SoC-1](https://spacesheep.dev/@yaroslavvb/et-soc1-influence-functions)
  (exploratory, no card run; `docs/reports/data/2026-09-25-influence-on-et/`),
  [What is broken on aifoundry1](https://spacesheep.dev/@yaroslavvb/aifoundry1-troubleshooting) and its
  [fix log](https://spacesheep.dev/@yaroslavvb/aifoundry1-fix), and a report on the lab's problems for the lab lead,
  which is not in the repository (public since 26 September, the owner's decision; MIRROR.md).
- **The repository pass of 25 September:** [`AGENT.md`](../AGENT.md) (the map and the rules for an agent starting
  from a clone), [`reports/MIRROR.md`](reports/MIRROR.md) (every published page with its space, file and
  visibility) and `scripts/check-mirror.py` (live equals repo). Lessons that had lived only in per-machine memory
  moved into `findings/14-card-behaviour.md`, `lab-access.md`, this page and `findings/04-artifacts.md`.
- **The pages and the results.** Every published page with its code and raw data is in the
  [README](../README.md#the-published-pages)'s table; its space, visibility and build command in
  [`reports/MIRROR.md`](reports/MIRROR.md), which also says how to deploy one page (`python3 scripts/check-mirror.py`
  checks that each live page equals its file). Every space the hub links is public (Q40). The results, with every
  number traced to its experiment and raw file: [`findings/README.md`](findings/README.md) and
  [`findings/05-claims.md`](findings/05-claims.md) (the energy manual's bars and the unmetered attribution in
  `findings/19-observability-and-the-unmetered.md`, heat per millimetre in `findings/20-heat-per-mm.md`, the traps in
  `findings/14-card-behaviour.md`). The energy manual's rebuild, in order: `findings/04-artifacts.md`, A16; the
  reviews and validations of 24–26 September: `findings/04-artifacts.md` and `reports/data/2026-09-24-report-review/`.
- **Next:** tau (E58) on aifoundry2, whose card is back in service since 6 October 2026, after the
  amendment its `PREREG.md` requires for that card (a heat step, its own start temperature, a D burst that does not
  starve its sampler and its own calibration, written before any aifoundry2 data); NV's first write and validation,
  the owner's; and, for DV2's two questions, a new pre-registered run whose heating sessions start from a cooler rest
  than aifoundry2's 71–76 °C (pcie2, nocr, memp2 and DV2's reduction are done). The ladder's next undone rungs:
  calibrating the per-shire IR-drop map from the SP DEBUG trace into a spatial current map, and a PCIe riser with
  shunts for millisecond board power (rung 4, the rails' filter, was done by E58). The earlier "next" items below (a
  real GEMM, prefetching, Discord) still stand.

## Earlier work (18–21 September), and where it stood

- **Goal.** Roman Shaposhnik (AI Foundry / AINekko) invited us to prototype a workload on the ET-SoC-1, first
  on the `sys_emu` simulator and then on the real cards in their lab. He would like the experience shared on the
  AI Foundry Discord. The long-term workload has not been picked yet.
- **Done** (18–21 September): the simulator environment and the hello worlds (the README's Setup and Run),
  `workloads/sgemm` on aifoundry3 (scalar fp32, 127 GFLOP/s), and the first measurement pages (matmul efficiency,
  memory hierarchy, on-chip communication, sparse compute, memory anatomy, the observability survey and its tools,
  power and temperature, the Horace experiment, why low power, ridge points): each is a row of the README's table, its
  numbers (re-measured on three cards on 26 September) are in [findings/05-claims.md](findings/05-claims.md), their
  summaries in [et-soc1-notes.md](et-soc1-notes.md), and what they taught about running a card (the thermal-first
  governor, heat that carries over, a temperature cap on long runs, never editing a running script) in
  [findings/14-card-behaviour.md](findings/14-card-behaviour.md). Why no firmware was flashed for the counter
  syscall: `patches/README.md`; where Verilator is built on aifoundry2: `rtl-sim/pmu_carry/README.md`.
- **Next:**
  - A real GEMM, tiling through the L2 scratchpad with cooperative tensor loads. (FOSDEM's 10.25 TFLOP/s came from
    software-pipelining the tensor unit's inner loop, overlapping the next A-load with the current FMA.)
  - Hart 1 prefetching with `TensorLoadL2Scp`.
  - A vector-unit fp32 baseline.
  - Posting the results on Discord.
  - From the sparsity report: run the batch-1 layer on an A100 for a measured comparison, and try the spiking
    microcircuit (PD14), where the chip's 2.3 us hardware allreduce could beat a GPU's per-step kernel launches.

## 1. Clone

```bash
gh repo clone yaroslavvb/et-soc1-prototyping nekko      # public repo
cd nekko
scripts/clone-upstream.sh
```

`clone-upstream.sh` puts et-platform, et-man (the manuals), core-et, et-testdrive and etTopoScan in `external/`. Keep
et-platform's full history, because `scripts/deploy-lab-gpsdk.sh` exports an older gp-sdk from it.

For the local simulator, run `scripts/create-vm.sh` on a Mac. On Ubuntu 24.04, run `scripts/provision-vm.sh`.
The [README](../README.md) has the details. The lab machines don't need any of this: they already have the ET stack.

## 2. Connect to the lab machines

The lab machines are on AI Foundry's Tailscale tailnet. We are a member as `yaroslavvb@gmail.com`, through the
invite Roman sent. On a new machine, install Tailscale, sign in with that account, and check that the machines show up (`tailscale status | grep
aifoundry`). Logins are Tailscale SSH, with no keys or passwords, as user `yaroslavvb` on every machine (if your local
name differs, add `User yaroslavvb` for `Host aifoundry1 aifoundry2 aifoundry3` in `~/.ssh/config`). Check mode, the
URL a person must approve (an agent hands it over and waits), the 404 fix and the full tailnet names to use from
aifoundry2 are in [lab-access.md](lab-access.md), "How access works" and "First login".

`/opt/et/bin` is on PATH in login shells on every machine since 25 September; nothing to add to `.bashrc`.

Four cards on three machines: aifoundry2 (the git checkout, `~/claude/et-soc1-prototyping`; its card, the main card
until 2 October, is **out of service since 2 October 2026**: its cooling failed, and idle it heats until it drops off the
PCIe bus), aifoundry3 (held at 600 MHz; compare switching power over idle, never absolute watts) and aifoundry1's two
cards (select one with `ET_DEVICES=<n>` and its lock, `etsoc-shire<n>.lock`; card 0 overheated until its fan was
replaced on 2 October 2026 and is back in service). So three cards are in service. Their firmware, clock policy, idle
power and quirks, and how the hosts differ: AGENT.md §4 and
[findings/14-card-behaviour.md](findings/14-card-behaviour.md), "The lab machines and their four cards are not
interchangeable".

All three are x86_64 Ubuntu 24.04 with RISC-V GCC 15.1 and `sys_emu` in `/opt/et`, but not the same runtime:
aifoundry2 has et-platform `353f20e` (Dec 2025, runtime 0.19.0), aifoundry3 the same with a patched `libetrt.so`, and
aifoundry1 a fork build whose device layer takes `ET_DEVICES` (§9). All are older than the gp-sdk that upstream
documents; see section 4. Admin work on the machines (accounts, drivers, resets) is for the lab admin;
[docs/lab-access.md](lab-access.md) covers accounts for other people.

**Etiquette.** The cards are shared. The owner's rules, each with the reason behind it, are in
[AGENT.md](../AGENT.md) §5 and, in short, in `CLAUDE.md`: ask which machine (and card) to use; look first (`et-who`,
`who`, `uptime`) and hold the card's lock (`flock -n /run/lock/etsoc-shire<N>.lock <command>`); never hold a device
for more than 10 s (`timeout 10`); stop tools with Ctrl-C or a plain `kill`, never `kill -9`; keep builds small
(`nice`, `-j4`); never reset a card. The management node is single-opener: while someone runs `et-powertop`,
`dev_mngt_service`, et-testdrive and the power logger fail with "Device or resource busy". Others use the cards too: CI runners on aifoundry1 and aifoundry2, a demo service
on aifoundry3, and `tools/claims-v3` queues that hold a card for hours.

**Lab norms from the AI Foundry Discord** (#community-lab, read on 2026-09-18):

- People claim a machine by posting "using aifoundry2" there, and "released" when they are done (since 2 October the
  brief's form is "using `<host>` card `<N>`", START.md step 2).
- **Don't reset a card yourself.** On 2026-07-17 the lab admin, Afonso Oliveira, asked people not to reset the
  ET-SoC-1 cards, because a software reset can hang one. If a card hangs, ping him and he will power-cycle it. We
  reset aifoundry2 twice on 2026-09-18 with `dev_mngt_service -m DM_CMD_RESET_ETSOC -n 0`, both times with the user's
  approval and before we had seen his request. It worked both times, but ask him first. On 2026-09-28, with the owner's
  approval, it recovered aifoundry2's hung Master Minion after the sysfs per-card reset
  (`echo 1 > /sys/bus/pci/devices/0000:02:00.0/soc_reset/reinitiate`) had re-attached the device without recovering it
  (`docs/findings/14-card-behaviour.md`).
- You can tell a card is wedged when every launch fails with `KernelLaunchCmIfaceMulticastFailed`, or with "Couldn't use
  the HPSQ. Perhaps the Master Minion is hanged?".

## 3. Hello world

On a lab machine, with nothing to build (aifoundry3 and aifoundry2 as written; on aifoundry1 put `ET_DEVICES=<N>` before `flock` and take `etsoc-shire<N>.lock`, or the program opens both
cards):

```bash
/opt/et/bin/it_test_code_loading                           # simulator: 3 tests pass in about 110 s
et-who                                                     # nobody on the card? (and ask first: section 2)
flock -n /run/lock/etsoc-shire0.lock timeout 10 /opt/et/bin/it_test_code_loading --mode=pcie   # the card: under 1 s
```

marty1885's et-testdrive, from the laptop (on aifoundry3 or aifoundry2):

```bash
rsync -a --exclude .git --exclude build external/et-testdrive/ aifoundry3:et-testdrive/
ssh aifoundry3 et-who                                        # nobody on the card?
ssh aifoundry3 'cd et-testdrive && cmake -B build -DCMAKE_PREFIX_PATH=/opt/et -Wno-dev > /dev/null &&
  nice cmake --build build -j4 > /dev/null &&
  flock -n /run/lock/etsoc-shire0.lock timeout 10 build/host/hello_host build/kernel/hello.elf | tail -3'
```

It should print "Hello World from hart N" from all 64 harts of shire 0. Add `-DET_SYSEMU=ON` to the first
`cmake` for a simulator build.

## 4. The matmul energy benchmark

gp-sdk kernels (`kernels/`, `launchers/`) need gp-sdk pinned to `06605ab` plus
`patches/lab-gp-sdk-06605ab.patch` on the lab machines. `patches/README.md` explains why. Without the patch, every
kernel faults at PC `0x40`. The deploy script sets this up (on aifoundry3 here: aifoundry2's card is out of
service since 2 October 2026; never while a `tools/claims-v3` queue runs on the host, [AGENT.md](../AGENT.md) §7):

```bash
scripts/deploy-lab-gpsdk.sh aifoundry3       # from the laptop: sources, patched gp-sdk, nice -j4 build (~10 s)
ssh aifoundry3
cd ~/nekko
et-who                                       # nobody on the card? (and ask first: section 2)
flock -n /run/lock/etsoc-shire0.lock make mmbench-check DEVICE=silicon   # every mode checked exactly; ~1 s of card time, timeout 10 per launch
flock -n /run/lock/etsoc-shire0.lock make bench-power                    # about 1 min; every launcher is capped at 10 s on the card
```

- **The kernel.** Hart 0 of each of the 1,024 minions runs back-to-back `tensor_fma` ops: 16×16×K tiles in fp32,
  fp16→fp32 or int8→int32. A is double-buffered in the L1 scratchpad, and B streams through TenB.
- **Checking.** The host checks every minion's result exactly against its own computation.
- **Power.** `scripts/et-power-log.sh` samples board power from the service processor about 8 times a second (a new
  reading about every 133 ms on aifoundry2 and 224 ms on aifoundry3; 156 and 263 ms while ettelem samples at 10 Hz, E41).
  `scripts/mmbench-power.py` averages it over each workload's launch windows.
- **Output.** `build/mmbench-power/`: `power.csv`, `runs.jsonl` and `results.json`.

On the simulator, run `scripts/vm make mmbench-check` on the laptop, or `make mmbench-check` on a lab machine. It
uses one shire and takes about 40 s per mode. The simulator's timings are meaningless because `sys_emu` is
functional only, so measure speed on a card.

## 5. Updating the report

```bash
rsync -a <host>:nekko/build/mmbench-power/ docs/reports/data/<date>-<host>/
scripts/mmbench-report-data.py docs/reports/data/<date>-<host> \
    --manual docs/reports/data/2026-09-23-energy-manual/manual.json \
    --embed docs/reports/2026-09-18-et-soc1-matmul-efficiency.html --ladder docs/report/index.html
scripts/paste-chartkit.py docs/reports/2026-09-18-et-soc1-matmul-efficiency.html docs/report/index.html
```

This prints the table numbers, % of peak and A100 ratios, and refreshes the power chart. The prose and tables
in the HTML are hand-written, so edit them to match. To publish, follow [`reports/MIRROR.md`](reports/MIRROR.md),
"Deploying one page" (the matmul page is space `590752c1-17a8-4f5d-97ef-bcf33fd6a3e7`): `spacesheep login` once per
machine needs a person to approve it in the browser, and AGENT.md §8 says which CLI versions read the pages back the
same. The key lives in `~/.config/spacesheep/`: never copy it into the repository.

## 6. What is already on the lab machines

- **aifoundry2** (`~yaroslavvb`):
  - `~/claude/et-soc1-prototyping`: **the git checkout** the work is done in. The version-3
    campaign ran from here, with its raw data in `build/claims-v3/aifoundry2/` (committed under
    `docs/reports/data/2026-09-25-claims-v3/raw/`).
  - `~/nekko`: the gp-sdk deploy tree (`scripts/deploy-lab-gpsdk.sh`; `MMBENCH_DIR` in `tools/claims-v3/lib.sh`),
    built. The 18 Sep runs are in `build/mmbench-power`, `build/memhier` (chases), `build/memhier-energy*` and
    `build/nocbench-data`. The outputs the reports use are committed under `docs/reports/data/`.
  - `~/et-testdrive`: built.
  - `~/et-hello`: scratch from the first session, superseded by `~/nekko`. Safe to delete.
- **aifoundry3:** `~/nekko` (deployed for E20 onward; the campaign ran from it) and the `workloads/sgemm` build.
  See [workloads/sgemm/README.md](../workloads/sgemm/README.md).
- **aifoundry1:** `~/nekko` since 25 September (the campaign on card 1 ran from it; `ettelem` is built there
  against the host's own `/opt/et`, so it honours `ET_DEVICES`).

The `~/nekko` trees on aifoundry1 and aifoundry3 are **rsynced copies without git**: edit in the checkout on
aifoundry2 (or a clone), then rsync the changed files. Their `.venv` or `pylib/` numpy fallbacks are no longer needed
(the system numpy is installed everywhere since 25 September). Home directories are local to each machine.

## 7. Gotchas from the first session

- **gp-sdk versus the lab install.** Three problems:
  - The Erbium components are missing: pinning gp-sdk to `06605ab`, the last version before it required them,
    avoids this (`scripts/deploy-lab-gpsdk.sh`).
  - The simulator runs without firmware and writes GBs of log (fixed by `patches/lab-gp-sdk-06605ab.patch`).
  - Kernels fault at PC `0x40` without `--emit-relocs` (fixed by the same patch).
- **`pkill -f <pattern>` over `ssh` kills your own session,** because the remote command line contains the
  pattern. Kill by PID instead.
- **The Mac has no `timeout` by default.** Run capped commands on the lab machine.
- **Board power creeps up as the chip warms,** by about 3 W over 12 s. Compare runs of the same length.
- **A hung transfer outlives the kernel abort.** If a TensorSend, TensorRecv or blocking credit wait (`csrw fcc`)
  never completes, the stalled hart ignores the firmware's abort. The card then refuses launches until it is
  power-cycled. Every wait must have a partner that answers it. When credits cross shires, poll `fccnb` with a
  bailout first, as `workloads/nocbench` does.
- **TensorSend has one "ready" bit per minion.** A minion must never have two partners that could both be ready at
  once. Change partners only across a barrier. `sys_emu` tracks each partner separately, so a schedule that passes
  on the simulator can still hang silicon. See `docs/et-soc1-notes.md`, "On-chip communication".

**Gotchas from the long runs (22–25 September):**

- **Start long runs detached:** `ssh host 'cd <tree> && setsid nohup <cmd> > <log> 2>&1 < /dev/null &'`. A plain
  `nohup` keeps the `ssh` session open, and the agent harness's command timeout then kills it. The hosts are on
  Wi-Fi, so a dropped connection must not take a run with it.
- **Polling with `pgrep -f <script>` over `ssh` matches itself,** because the `ssh` command line that runs `pgrep`
  names the script too. Match on something only the target has, or check the log.
- **Copying scripts:** an `scp` over a running script corrupts it (bash reads by offset), and an `scp` to a new
  path drops the executable bit. Copy to a temporary name and `mv` it into place, then `chmod +x`.
- **rsync keeps the source's modification times,** so `make` or `cmake --build` on the lab host may not rebuild
  after a sync. Use `cmake --build <dir> --clean-first`.
- **A code-only agent must not reach a card.** On 25 September an agent told to write code only ran a real block:
  a `cd` inside a backgrounded `&&` chain did not apply. Test block scripts with `V3_DRY=1` (no device access at all),
  from an absolute path, and check `et-who` afterwards.
- **The three hosts' compilers generate the same code,** but the ELF files differ in their `.comment` section, so
  compare `.text` hashes, not file md5s ([findings/14-card-behaviour.md](findings/14-card-behaviour.md), "Traps").

## 8. Reproducing each report

Each report is one HTML file in `docs/reports/`, with its raw measurements in `docs/reports/data/`. Reports from
18–19 September are hand-written HTML whose charts read JSON an analysis script embeds; on 2026-09-18 each script
regenerated its committed page byte for byte from the committed data. Later reports are assembled by
`scripts/build-report.py` from `docs/reports/sources/` (see `docs/findings/04-artifacts.md`), and several compute
every number from their data. The GPU and A100 columns come from the sourced notes in `docs/reports/sources/`, not
from our measurements.

**Build prerequisites.** Python 3 with numpy, and node: `scripts/build-report.py` renders TeX to SVG with
mathjax-full, which `package.json` pins to 3.2.1; run `npm ci` once at the repo root (in a git worktree without its own
`node_modules`, set `NODE_PATH` to a checkout's). **Charts.** Every page's charts use the shared toolkit
`docs/reports/sources/chartkit.js` (the global `CK`). `build-report.py` inlines it into the source-built pages at
`__CHARTKIT__`, with its CSS in `report.template.html` between `chartkit:css:begin` and `chartkit:css:end`. The
standalone pages (the 18–19 September reports, the test drive, the spatial brief) carry a copy between
`<!-- chartkit:begin -->` and `<!-- chartkit:end -->`: after editing `chartkit.js` or that CSS, or after an
`--embed` run, refresh them with `scripts/paste-chartkit.py PAGE` (`--check` reports a stale copy); the memory-anatomy
page gets it from its template. Edit a standalone page's prose in the HTML, outside those markers.

Since 26 September most pages also carry the version-3 check's three cards, through options on the generators below
(`--v3`, `--v3-rl`, `--wire3`, `--claims-v3`, `--cards`). The commands in this table are the one-card forms: run them
as [`findings/04-artifacts.md`](findings/04-artifacts.md), "Rebuilding the version-3 data", and
[`reports/MIRROR.md`](reports/MIRROR.md), "How each page is built", give them, or the three cards drop out of the page.

| Report | Code | Measure (on a lab machine) | Raw data | Regenerate the page |
|---|---|---|---|---|
| Matmul efficiency, and the test drive's ladder | `kernels/mmbench`, `launchers/mmbench` | section 4 | `docs/reports/data/2026-09-18-aifoundry2` | `python3 scripts/mmbench-report-data.py DATA --manual docs/reports/data/2026-09-23-energy-manual/manual.json --embed HTML --ladder docs/report/index.html` |
| Memory hierarchy | `workloads/memhier` | `workloads/memhier/README.md`: the chases, then `run_energy.py` | `docs/reports/data/2026-09-18-memhier-aifoundry2` | `python3 workloads/memhier/analyze.py DATA --embed HTML` |
| On-chip communication | `workloads/nocbench` | `run_lab.sh`, then `run_energy.py` twice, the second time with `--only` in reverse order | `docs/reports/data/2026-09-18-nocbench-aifoundry2` | `python3 workloads/nocbench/analyze.py DATA --memhier docs/reports/data/2026-09-18-memhier-aifoundry2 --search --embed HTML` |
| Memory anatomy | `workloads/memprobe` | `gen_ops.py` programs, `run_power.py` (`workloads/memprobe/README.md`) | `docs/reports/data/2026-09-19-memprobe-aifoundry2` | `python3 workloads/memprobe/analyze_power.py DATA/power --json DATA/power/summary.json`, `python3 workloads/memprobe/analyze.py --data DATA --out DATA/summary.json`, then `python3 workloads/memprobe/build_report.py DATA/summary.json docs/reports/data/2026-09-23-energy-manual/manual.json HTML` (E1) |
| Power and temperature, spatial brief | `tools/ettelem/run_thermal.sh`, `run_horace.sh` | E5–E8 in `docs/findings/03-experiments.md` | `docs/reports/data/2026-09-20-power-aifoundry2` (with `raw/`: the SP trace dumps and the load log) | `python3 tools/ettelem/summarize_power_session.py DATA --out DATA/summary.json`, then `scripts/build-report.py power-temperature DATA/summary.json HTML`; the brief's constants from `python3 tools/ettelem/host_temp_fields.py` (`--check PAGE`) |
| Horace experiment, why low power | `tools/ettelem` (`run_horace_*.sh`, `run_ablation.sh`) | the commands of E9–E17 and E20 in `docs/findings/03-experiments.md` | `docs/reports/data/2026-09-21-horace-aifoundry2`, `2026-09-22-horace-aifoundry3` | `tools/ettelem/finish_horace.sh` |
| DVFS and leakage | `tools/ettelem/analyze_dvfs.py` | E10, E18, E19 in `docs/findings/03-experiments.md` | `docs/reports/data/2026-09-22-dvfs-aifoundry2` (the wake-up probe, the 20-hour idle), `2026-09-21-horace-aifoundry2` (`cold1`, `cold2`, `long2`, `model.json`, `ablation.json`), `2026-09-22-horace-aifoundry3` (`cards.json`, `transfer.json`, `leakage_crosscard.json`), `2026-09-22-cards` | three steps, in order (E19 gives them in full): `analyze_dvfs.py … --out dvfs.json`; `build_cards_data.py … --merge dvfs.json`, which adds the three-machine block that sections 3 and 6 need (`analyze_dvfs.py` keeps it on a later rerun, and `build-report.py` refuses to build without it); `scripts/build-report.py dvfs-leakage dvfs.json HTML` |
| Hot line, on-chip relay, heat per mm | `workloads/nocbench`, `workloads/onchip`, `workloads/enercat/run_wire.py` | the commands of E22–E25 and E31–E32 in `docs/findings/03-experiments.md` | `docs/reports/data/2026-09-22-hotline-*` (with the hand-kept `context.json`), `-onchip-*`, `2026-09-24-wire*` | the same entries (the hot line's `analyze_hotline.py` takes `--context` and `--barrier`), then `scripts/build-report.py` (the exact final commands are in [`reports/MIRROR.md`](reports/MIRROR.md), "How each page is built") |
| Energy manual, catalogue | `workloads/enercat` | `run_catalogue.py DATA --passes 3` on each card (2.6 h each; keep the die warm on aifoundry2) | `docs/reports/data/2026-09-23-catalogue-aifoundry2`, `-aifoundry3`, `-aifoundry2-rows` | `analyze_catalogue.py A2 A3 A2_ROWS --out catalogue.json`, `fit_unmetered.py --out unmetered_fit.json --overwrite`, then `tools/ettelem/build_energy_manual.py`, `render_energy_manual.py`, `render_catalogue.py`, `scripts/build-report.py energy-manual manual.json HTML` (`docs/findings/04-artifacts.md`, A16, gives the full order) |
| Energy manual, reruns | `tools/ettelem/run_reruns_warm.sh`, `run_rings_levels_power.sh` | 3 passes each of relay, hot line, rings, levels per card; preheat aifoundry2 | `docs/reports/data/2026-09-23-reruns-aifoundry2-warm`, `-aifoundry3` | `tools/ettelem/analyze_reruns.py DIRS --out reruns.json` (bursts off 600 MHz dropped) |
| Limits of observability | `docs/reports/sources/limits-of-observability.*` | reads the firmware and the catalogue; no card time | `docs/reports/data/2026-09-23-energy-manual/` (`unmetered_fit.json`, `catalogue.json`, `manual.json`, `reruns.json` and the rerun directories it names), `docs/reports/data/2026-09-22-dvfs-aifoundry2/dvfs.json`, `2026-09-24-wire-energy/report.json`, `2026-09-21-horace-aifoundry2/model.json` and `report.json`, and the version-3 check's `plan3.json.gz`, `results/` and V3-CATFULL telemetry (`2026-09-25-claims-v3/`) | `python3 tools/ettelem/sync_hub_data.py` (writes the data file's computed blocks; `--check` exits 1 if they are stale; rerun it after regenerating any of those files), then `python3 scripts/build-report.py limits-of-observability docs/reports/sources/limits-of-observability.data.json HTML` |
| Sparsity | `workloads/sparsity` | `run_lab.sh`, then `run_energy.py` twice, the second time with `--only` in reverse order (`workloads/sparsity/README.md`) | `docs/reports/data/2026-09-18-sparsity-aifoundry3` | `python3 workloads/sparsity/analyze.py DATA --embed HTML` (the three-card check through `--claims-v3`, by default) |
| Ridge points | `scripts/ridge-points.py` | nothing: derived from the four 2026-09-18 reports | their four data directories, and the energy manual's `manual.json` | `python3 scripts/ridge-points.py --embed HTML` (`docs/findings/04-artifacts.md`, A19, gives the input chain) |

- **Measuring.** Build on the machine with `scripts/deploy-lab.sh <host> workloads/<name>` (aifoundry3, aifoundry2 or
  aifoundry1), or `scripts/deploy-lab-gpsdk.sh` for `kernels/`. Follow
  the etiquette above, then copy the outputs back into a new dated directory under `docs/reports/data/`. The runs
  print JSON lines that the analysis scripts read. Workloads also run on the simulator with `--sysemu` (small sizes),
  which checks correctness but not speed.
- **Analysis.** You need Python 3. The on-chip communication analysis also needs numpy. It prints every number
  the page quotes, including the one-hop ring and the mesh-time decomposition.
- **Publishing.** Every space the hub links is public (Q40). Update one in place with its uuid from
  [`reports/MIRROR.md`](reports/MIRROR.md), which also gives each page's final build command. You can use the CLI
  (section 5) or the spacesheep MCP: `stage_begin`, then `curl -X PUT` the file, then `deploy` with the uuid.
  Afterwards run `spacesheep list`, compare the visibility with MIRROR.md, and run `python3 scripts/check-mirror.py`.
- **What will differ.** Another card can have a different shire map if a different shire is fused off. It can
  also run at another clock: the governor moves between 600 and 800 MHz (three points: 600, 700, 800), and time on the mesh is fixed in ns. And
  it can idle at a different power, depending on its temperature and on other users. All of our runs are timestamped,
  and those at 600 MHz say so in the data.

## 9. Upstream versions

| Component | Version used | Pinned in |
|---|---|---|
| et-platform: firmware, runtime, `sys_emu`, gp-sdk | `836a4ab` plus `patches/et-platform-*.patch` | `scripts/clone-upstream.sh`; built by `scripts/provision-vm.sh` |
| RISC-V GCC 15.2 (aifoundry-org/riscv-gnu-toolchain, branch `et`) | `b4f9cd5` | `scripts/provision-vm.sh` (`TOOLCHAIN_REF`) |
| et-man: PRM, datasheet, errata | `5fe80a3` | `scripts/clone-upstream.sh` |
| core-et, branch erbium: RTL and design docs | `b38a1a3` | `scripts/clone-upstream.sh` |
| et-testdrive | `c2035c5` | `scripts/clone-upstream.sh` |
| etTopoScan | `ee3e9f2` | `scripts/clone-upstream.sh` |
| gp-sdk on the lab machines | `06605ab` plus `patches/lab-gp-sdk-06605ab.patch` | `scripts/deploy-lab-gpsdk.sh` |
| `/opt/et` on aifoundry2 | et-platform `353f20e` (Dec 2025): runtime 0.19.0, GCC 15.1 | installed by the lab |
| `/opt/et` on aifoundry3 | the same, except `libetrt.so`: a patched Release `-O3` build of `836a4ab` (2026-07-23) | installed by the lab |
| `/opt/et` on aifoundry1 | a build of an et-platform fork (May 2026): its runtime and device layer differ, and the device layer honours `ET_DEVICES=<n>`; `libDM.so`, `dev_mngt_service`, `et-powertop` and GCC 15.1 as on the others | installed by the lab |
| Card firmware | 1.3.1 on aifoundry2 and aifoundry3 (a build of about mid-May 2024); 1.4.1 and 1.2.0 on aifoundry1's cards 0 and 1 | flashed by the lab; read with `dev_mngt_service -m DM_CMD_GET_MODULE_FIRMWARE_REVISIONS` (`docs/reports/data/2026-09-25-claims-v3/firmware.md` for aifoundry2 and aifoundry3, `AMENDMENTS.md` A2 there for aifoundry1) |

`UPSTREAM_LATEST=1 scripts/clone-upstream.sh` and `TOOLCHAIN_REF=et scripts/provision-vm.sh` build the branch tips
instead of the pins.
