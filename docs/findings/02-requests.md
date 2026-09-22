# Requests: what was asked, and what each one produced

The work in this directory was driven by a sequence of requests from the repo owner, in one long session on
aifoundry2 between 19 and 22 September 2026. Each is recorded here because scope decisions explain why some
questions were answered thoroughly and others were left open. Cite as **Q1**...**Q20**.

| ID | Date | Request (condensed) | Produced |
|---|---|---|---|
| Q1 | 09-18 | Enable remote control on this session | — |
| Q2 | 09-18 | Clone `yaroslavvb/et-soc1-prototyping`, make sure the device works | Working tree on aifoundry2 |
| Q3 | 09-19 | Configure spacesheep so all future reports can be deployed with it | Node in `~/.local/node`, CLI signed in as @yaroslavvb |
| Q4 | 09-19 | Research fine-grained power and latency observability; break a memory access down by stage and by energy | E1, E2 → A1 |
| Q5 | 09-19 | Commit and push | commit `76085a3` |
| Q6 | 09-20 | Mini-report titled "Limits of Observability": what is observable now, what could be, can individual bit flips be tracked | E2 → A2 |
| Q7 | 09-20 | Proceed with implementation including a reflash, sequentially, minding quota | E3, E4 → A2 update. **Reflash not done**, see below |
| Q8 | 09-20 | What a debug-interface client unlocks for the power system; all the ways power and energy can be measured at every granularity | `tools/ettelem`, E5, E6 → A3 |
| Q9 | 09-20 | Find Horace He's blog post about random matrices using more power and reproduce it on ET-SoC-1; write it up as `horace-experiment` | E7 → A4 (first version) |
| Q10 | 09-20 | Rerun with the chip cooled to the same temperature first, to make runs comparable | E8 → A4 (second version) |
| Q11 | 09-21 | Rerun with strict temperature control; better visualisation with runs clustered by kind; fewer categories; **a model: transistor flips → power → temperature**, and explain the discrepancy; an animated GIF to repost | E9, E10, E11 → A4 (third version), A6, A7 |
| Q12 | 09-21 | Do those experiments for longer, and build a model that ties temperature to transistor flips | E12, E17 → A4 (fourth version), A8 |
| Q13 | 09-21 | *(mid-task)* Forget the 10-second rule for now; runs may be up to 10 minutes, whole session under 6 hours | Made E12 possible |
| Q14 | 09-21 | Explain why Esperanto chips are low power compared with A100s; research it, test what needs testing, publish | E15, R6, R7 → A5 |
| Q15 | 09-21 | *(mid-task)* Find other kinds of matrices beyond fully random and fully constant, such as kaleidoscope matrices; make custom workloads and infer how much heat they produce, for heat management | `make_tiles.py`, E13, E14, E15, E16, `predict_heat.py` |
| Q16 | 09-22 | How is overfitting controlled? Is there independent validation that is not part of the parameter estimation? | E17 → A4 (fifth version) |
| Q17 | 09-22 | Fix the report and commit | commit `75bb061` |
| Q18 | 09-22 | Summarise all findings as self-contained MD files with pointers on where to start; commit | This directory |
| Q19 | 09-22 | *(mid-task)* Add provenance: modularise experiments and artifacts so findings can be traced; structure the files around resources, requests, experiments and artifacts | This directory's structure |
| Q20 | 09-22 | Using David Kanter's notes, research the ET-SoC-1's DVFS loop and the leakage-suppressor transistors; validate experimentally if needed; turn into a brief | R9, E18, E19 → A11, [16-dvfs-and-leakage.md](16-dvfs-and-leakage.md) |
| Q21 | 09-22 | Try the other two cards: SSH into AI Foundry 1 and AI Foundry 3 | R10, E20, E21 |
| Q22 | 09-22 | Run the experiments on all three machines; integrate them into the public report and keep it public | E20, E21 → A4, A11, [14-card-behaviour.md](14-card-behaviour.md), [16-dvfs-and-leakage.md](16-dvfs-and-leakage.md) |
| Q23 | 09-22 | For formulas like the switching-power equation, use high-quality math (MathJax) instead of HTML | A12, all four report sources |
| Q24 | 09-22 | Clarify Ivan's Discord comment, "shire 0 got 6% of its fair share and finished only after the other 31"; deploy as another spacesheep artifact | R11, E22, E23 → A13, [17-hot-line.md](17-hot-line.md) |
| Q25 | 09-22 | Look at the paths around cache-line starvation; find a systolic-array application that beats main memory | R12, E24, E25 → A14, [18-on-chip-relay.md](18-on-chip-relay.md) |
| Q26 | 09-22 | *(mid-task)* Maybe systolic is a bad idea — find any computation where shire-to-shire communication beats the standard approach | The same; the relay is that computation |

## Scope decisions worth remembering

- **The reflash was not done (Q7).** The minion runtime and the service-processor bootloader are signed
  images: BL1 verifies BL2 and BL2 verifies the minion images against a public-key hash in OTP, and neither the
  signing tool nor a test key is in the open tree (R3). Whether this card would accept a rebuilt image is
  unknown, and a bad image can brick the boot path, so it is a lab-admin decision. Everything downstream of the
  reflash — enabling the SRAM ECC interrupt sources, the UltraSoC debug fabric, a PMU event-select syscall on
  silicon — therefore remains unmeasured. The counter-configure syscall was built and verified in `sys_emu`
  only (`patches/0003-pmc-configure-syscall-353f20e.patch`, `workloads/pmcsel`).
- **The debug-interface (MDI) client was not built.** Work on it was stopped and not resumed.
- **The 10-second hold limit was waived only for Q13's long runs.** Every other session on the card kept
  individual processes under 10 seconds.
- **aifoundry1's driver was not reinstalled, and aifoundry3's TDP was not changed (Q21, Q22).** Both are
  configuration changes to shared lab hardware that would silently alter other people's results: one replaces a
  kernel module, the other lifts a card's clock ceiling mid-experiment for everyone. Both are documented in
  [14-card-behaviour.md](14-card-behaviour.md) with everything the lab admin needs, and neither was applied.
- **No GPU was measured.** Every A100 number in this work is from R7 or R8. This was never in scope for the
  card time available, and it is the single largest caveat in [13-why-low-power.md](13-why-low-power.md).
