# AGENT.md's changelog: older entries

*Moved verbatim from the Changelog at the end of [`AGENT.md`](../AGENT.md), which keeps its newest 15 entries (the
owner's rule of 10 October 2026 for agent instruction files). Newest first. Changes before 14 October 2026 are in
`git log -- AGENT.md`.*

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
