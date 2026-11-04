# AGENT.md's changelog: older entries

*Moved verbatim from the Changelog at the end of [`AGENT.md`](../AGENT.md), which keeps its newest 15 entries (the
owner's rule of 10 October 2026 for agent instruction files). Newest first. Changes before 14 October 2026 are in
`git log -- AGENT.md`.*

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
