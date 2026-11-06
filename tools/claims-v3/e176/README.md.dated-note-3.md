# Dated note 3 beside E176's kit README (Thu 5 Nov 2026; the records round Q143(r), after the session): E176 was refused at G0, nothing is scored, the room rule the lane wrote for its later try, and why its collection is committed

*Written on the Intel from about 19:50 PST on Thu 5 Nov 2026, desk only: no card, no device command, no lab box, no post. [`README.md`](README.md)
(lab `03582d2f`), [`README.md.dated-note-1.md`](README.md.dated-note-1.md) (`6ecab3c5`) and
[`README.md.dated-note-2.md`](README.md.dated-note-2.md) (`6b013ad9`) stay as committed, and no file of the kit's box list
(`frozen-e176.sha256`, 29) changes. This note records E176's outcome for the kit, as the evening round's critic (18:51-19:20 PST) asked.
For the kinds page's [section 11](https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers#11-what-is-still-open), items 9 and 8.*

## 1. The outcome: refused at G0, not a failed prediction

E176 ran on Thu 5 Nov 2026 on the owner's go of that day (about 11:15 PST), on aifoundry3 card 0 at 600 MHz pinned: the session started at
17:21:15 PST (launched 17:21:20) and ended at 17:27:38, **6.4 card-minutes** of its 76. The smoke ran with its five stop tests on live samples
(gate GO; C 57 of 57 PASS), then pass 17620's R0. **G0 refused at 17:27:34 PST**: R0's room, the 34-sensor mean over its last 120 s, read
**53.582 °C** (firmware 52.999 °C) against the README's line of 53.0 °C (its section "The run kit (E166's, ported)": "G0: R0's room ≤ 53.0 °C, else no hold,
exit 7"). So no hold ran, and every M11 reading is NOT SCORED. This is a gate working as registered, **not a failed prediction**. Nothing was
set: no governor, TDP, threshold or clock; no statistics reset; no firmware-revisions query; the PMIC voltage reads only; every command a
READ. The card's idle floor at the session's start was already 53.202 °C (after 4 h 46 min of rest since E171), above the line.

## 2. The room rule for the one later try, as the lane wrote it

The README's section "Card-minutes, the order, and the box steps" allows one later try after a G0 refusal (`--later-try`, the
smoke moved aside once). The card's temperature can
be read only inside a session, so the E176 lane wrote its rule for "the room has cooled" at **17:34:16 PST**, after the host baseline
(17:31:50-17:33:50) and before its comparison window (18:05:40-18:07:40). The rule, in full in
[`room-rule/room-rule.txt`](../../../docs/reports/data/2026-11-05-e176-m11-holds-aifoundry3/room-rule/room-rule.txt): the host's NVMe
composite (`nvme temp1`) at least 0.5 °C under its baseline's 38.850 °C over a 13-sample window, and the host's `coretemp` temp2-temp9 mean
no more than 1.0 °C above the baseline's. It read 38.850 °C in every sample of five windows, so no later try ran, and never a third. Post hoc
(the critic): that sensor reports whole kelvins, so the rule could only show a cooling of 1 °C or more.

## 3. Why the collection is committed after step 22 v2's exit 14

Step 22 v2 stopped at NO-LAUNCH (exit 14, 18:08:55 PST), by design: p17620's marks record no launch, so nothing is scored. Following the code
verifier's fix to its fault 2 ("on any exit 14 or 16 from step 22 v2, the E176 lane commits nothing and removes the data directory"), the lane
committed nothing and moved the collection (652 KB, 48 files) out of the lab clone. That fix keeps an unscored session from looking scored.
It does not forbid the record: every figure above would otherwise rest on an uncommitted scratch copy and the box. So the records round
commits the collection unchanged as
[`docs/reports/data/2026-11-05-e176-m11-holds-aifoundry3/`](../../../docs/reports/data/2026-11-05-e176-m11-holds-aifoundry3/README.md), headed
"G0-REFUSED: no hold ran, nothing scored, not a failed prediction", after E164's login scrub `--check` in every directory (8 of 8, 0 left)
and the public-text scan (only the owner's own box path, a reviewed class). Its `scored-m11.*` files are the scorer's NOT SCORED output,
written before the gates and kept as written; their "post hoc" label comes from the absent first launch record, not from commit order.
Exit 14 means "do not score", not "do not record".

## 4. The next M11 session

E176's kit is not run again (dated note 2, section 3: the second session gets its own run number and kit). Before that session, one
registration question is answered by a dated amendment, before any data: G0's fixed 53.0 °C line against aifoundry3's idle floor, which
moved 50.98-53.20 °C this week (post hoc), with G0 read after the smoke about 0.4 °C above the floor. Move G0 or the warm pattern, or plan
the session for a cool hour (the firmware read 49 °C at 11:38 today). The kit v4 items are in the runbook's dated note 2.

## What it does to predicting power and heat

Nothing to any number: no hold ran. M11's in-session calibration of heat over minutes stays unmeasured, and the chain's 0.49 °C blind given
the watts stays the largest open heat error.

SPDX-License-Identifier: Apache-2.0
