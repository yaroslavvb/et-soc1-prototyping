# AGENT.md's changelog: older entries

*Moved verbatim from the Changelog at the end of [`AGENT.md`](../AGENT.md), which keeps its newest 15 entries (the
owner's rule of 10 October 2026 for agent instruction files). Newest first. Changes before 14 October 2026 are in
`git log -- AGENT.md`.*

- **2026-10-27 (Tue, week 44)** — Section 5's rule against changing a card's TDP, clocks, firmware or driver is amended:
  resets, PCIe retrains, firmware, OTA, flashing, PMIC commands, driver reloads and direct clock sets stay forbidden, but
  the owner may authorize a **governor move** (the static TDP level and the software temperature threshold) for one named
  run, which then follows the ET-SoC-1 firmware field manual (private; on the lab boxes in
  `~/claude/aifoundry-setup/field-manual/`) — its pre-flight gates with a change record, the card exclusive for the
  window, and the original values read first, restored and read back. *Why:* the owner's authorization of that day, with
  the field manual the lab lead handed him: the governor's cap had never been moved, so every claim that it causes the
  600/800 MHz gap was read from the governor's own log (Q128 §5, the knob test).
- **2026-10-14 (Wed, week 42)** — Section 4 gains "When a card goes out of service or comes back": a pointer to the
  checklist in `docs/lab-start/README.md` ("Keeping it current"), which now names the new-user page's Machine field,
  and to the check `docs/lab-start/make_page_data.py` runs on that field. This changelog starts. *Why:* the owner's ask
  that day (Q114): "update https://spacesheep.dev/@yaroslavvb/aifoundry-lab-start to include the aifoundry2 [...] this
  was missed during the maintenance check somehow, so update the note to include it next time". The page's Machine
  field had offered only aifoundry3 and aifoundry1 since 2 October.
