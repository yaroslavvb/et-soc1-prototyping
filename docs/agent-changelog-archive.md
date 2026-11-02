# AGENT.md's changelog: older entries

*Moved verbatim from the Changelog at the end of [`AGENT.md`](../AGENT.md), which keeps its newest 15 entries (the
owner's rule of 10 October 2026 for agent instruction files). Newest first. Changes before 14 October 2026 are in
`git log -- AGENT.md`.*

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
  *Dated note, Mon 2 Nov 2026 (week 45), Q134's records, the text above unedited: that query is not read-only. At
  et-platform `836a4ab` it writes the PMIC's firmware-management command register twice (E114's C1), a PMIC command by E85
  C1's standard, which section 5 forbids. Re-check the cards' firmware by each card's module uptime
  (`DM_CMD_GET_MODULE_UPTIME`, service-processor RAM) against the time of section 4's committed read: an image takes
  effect only through a reset, so an unbroken uptime carries the identity (E77, E118, E120). Send the query only with the
  owner's and the firmware maintainer's authorization.*
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
