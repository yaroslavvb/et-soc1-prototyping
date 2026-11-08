# The card lane's brief for the card day of E182 and E184: look before the post, the order on the shared box, step 6's re-run rule, and the words the records use (Q154; E182's kit, dated note 2)

*Sat 7 Nov 2026 (week 45), first written 17:37 PST on the Intel, desk only (Q154, lane `e182n2`): no card was claimed, no device command
was sent, no lab box was reached, nothing was posted. It sits in E182's kit beside [KIT.md.dated-note-2.md](KIT.md.dated-note-2.md), which
lists it. It is for the card lane of the day the owner's go names, and it is read before either runbook. It restates what the two kits
register and adds no rule: **no rule, forecast, threshold, statistic, power figure, plan, cap or stop changes.** Where a kit's own text puts
the day's post before the look, or says nothing of the other run on its box, this brief's order binds; everything else is each kit's.*

The runbooks: **E182** by its kit's [dated note 2, section 6](KIT.md.dated-note-2.md) (steps 2 and 6 v3, note 1's v2 steps, k6's look and
reads); **E184** by its latest committed kit note, now [`../e184/KIT.md.dated-note-1.md`](../e184/KIT.md.dated-note-1.md) section 3
(`eab0c70e`). If a later E184 note changes E184's steps, its table governs those steps, and this brief's order still binds. Box step numbers
below are each KIT.md's.

## 1. Before anything

- **His go:** the day and one window (the last start and the last end, in PST), and fresh network approvals for aifoundry3 and aifoundry1.
  Nothing below runs without both.
- `git pull --ff-only` in the lab clone.
- **One `RB_OUT` per runbook and arm** (E182; E184 arm S; E184 arm B), each outside the repo, and one `RB_LOCK` for all three. Each one's
  box step 1 (its `s02_window`) comes first; each step 2 refuses without it.
- **E182's step 2 is v3** (`rb/s03_desk_e182_v3.sh`): its four hash lists are checked against pinned counts, 32, 79, 50 and 49. E184's step
  2 pins its own four (11, 44, 6 and 45).
- A printed login link stops the step (11) and appends `<HH:MM:SS> <host> needs a check` to `RB_LOCK`. No retry loop: after the approval,
  the same step is run again.

## 2. The order on the boxes

| | aifoundry3 card 0, 600 MHz pinned | aifoundry1 card 1 only |
|---|---|---|
| first | **E182 FULL**, steps 1-11 | **E184 arm B**, at any time in the day (best while E182's session runs) |
| then | **E184 arm S**, from its look (its box step 4), only after E182's step 11 copy-back has ended | — |

1. **E182 first on aifoundry3.** E184 arm S's look starts only after E182's step 11 (`rb/s22_collect_e182_v2.sh`) has copied E182's
   raw files back to the Intel. Either order would be valid (both runs are registered and blind, and neither reads the other's data); E182
   goes first because it is shorter and answers the multiplication question if the day is cut short (the Q153 readiness critic's day plan).
2. **Never E182's step 6 while a session of ours runs on aifoundry3.** Step 6 v3 refuses it by code (k6's `ours_live`; the v3 desk test's
   case O): its start, its checks and its fallback each stop with 10 beside a session of ours, and its start and its fallback also stop
   beside any runbook job still running (a dry pass, E184's build). Step 6 belongs before E182's own session (steps 5-8), never during
   E184 arm S.
3. **One session of ours per box, and never two of ours on aifoundry1.** E184 arm B is our only session on aifoundry1: card 1 only
   (`V3_DEVICE=1`, `ET_DEVICES=1`, lock `etsoc-shire1`), **never card 0**. It runs only if aifoundry1 has not rebooted since E82's firmware
   read (31 Oct 2026 13:45:24 PDT): otherwise the look (16) and the launch guard stop it, and the firmware is never queried.
4. **The window gates each launch:** a launch needs its cap before the last end (E182 FULL 6,000 s, PASSES 2,400 s; E184 S 8,100 s, B
   1,500 s), and no session starts after the last start. If E184 S cannot fit after E182, it waits for another day; the Q153 critic's plan
   for a go after about 11:30 PST is two days (E182 and E184 B on the first, E184 S on the second).

## 3. Look before the post, in both runbooks

Both kits list the day's post (box step 3) before the look (box step 4). **Run them the other way round, for every card:** the look
(`tools/claims-v3/q141k-runbook/k6/s05_look_k6.sh <box>`, then `--wait` while the card is held, at most 30 minutes in all, then skip that
card) reads FREE; only then does the day's post name that card; then the box steps. A post made before the look claims a card that may be
held. No code changes for this: E182's dry listing v3 already lists the look first, and the card day of 6 Nov ran its look before its
post (post hoc: the Q153 readiness critic's reading of that day's runbook log; the post was created at 09:36:40 PST).

## 4. The day's one post

The lab's one-post-a-day rule: find the day's post first; every reservation and release rewrites that one post (never a second post, and
never an earlier day's). One line, opening with `<ai> **Claude says:** `, then one clause for each card held now, `; `-separated:

| run | the clause |
|---|---|
| E182 FULL | `using aifoundry3 for 2 h, until ~HH:MM PST [doc](<https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers>)` |
| E182 PASSES (the fallback) | the same with `for 1 h` |
| E184 arm S | `using aifoundry3 for 2.5 h, until ~HH:MM PST [doc](<...>)` |
| E184 arm B | `using aifoundry1 card 1 for 1 h, until ~HH:MM PST [doc](<...>)` |

The day's sequence: after aifoundry3's look reads FREE, the post (E182's clause); if E182 falls back to PASSES before its launch, its
clause is rewritten to PASSES' `for 1 h` (KIT.md's table gives each plan's clause); after aifoundry1's look reads FREE, arm B's clause is
added, and it is dropped at arm B's release; at E182's session end aifoundry3's clause stays until E184 S's look, then becomes E184 S's
clause (or is dropped if E184 S does not start that day); the last release appends ` — released` to whatever the post then says, every
word kept.

## 5. E182's step 6, the train host's build: the re-run rule

`rb/s08_a3_preflight_e182_v3.sh start`, then `... wait`, again while it says 17. The build runs on the box as one detached job under its
own 500 s bound; each check after it is its own 60 s read.

- **TRAIN-HOST-BUILT, then NOTE1 FILES OK 10, HARNESS OK 73, GO and the verify:** go on to step 7 (k6's reads).
- **A build that failed, overran its own bound or was lost** (TRAIN-HOST-BUILD-FAILED, TRAIN-HOST-BUILD-OVERRAN or JOB-LOST; exit 16): the
  step says "build 1 of at most 2 today". Run `start` and `wait` **once more**: the one re-run.
- **If that build fails too, or `start` says "no third":** the registered fallback, as the step names it: `rb/s08_a3_preflight_e182_v3.sh
  --no-trains`, k6's reads, `rb/s10_a3_dry_e182_v2.sh start --no-trains` and `wait --no-trains`, `rb/s11_a3_session_e182_v2.sh PASSES no`,
  the wait, the release and step 11. PASSES' cap is 40 card-minutes; every train rule reads NOT SCORED (E182.md section 7).
- **TRAIN-HOST-INPUTS-DIFFER (16):** note 1's rule: step 5 v2 once more, then step 6 v3 `start`; if the inputs differ again, the fallback.
- **11, 12 or 13 on a step-6 call** is the network's (the build is a detached job and never sits inside a call): run the same
  sub-command again. The box counts the builds started there today (`build/e182-build-attempts.txt`), so a cut call neither adds nor hides
  one.
- The data README states step 6's outcome: TRAIN-HOST-BUILT and the day's build count, or the fallback and why.

## 6. The stops, the commands and the caps (registered; unchanged)

| run | card | expected card-minutes | cap | stops on a live sample |
|---|---|---|---|---|
| E182 FULL | aifoundry3 card 0 | about 83-93 | 100 | board at or above 65 W, or `minshire[0]` at or above 70 C |
| E182 PASSES | aifoundry3 card 0 | about 31 | 40 | the same |
| E184 arm S | aifoundry3 card 0 | about 125 | 135 | the same |
| E184 arm B | aifoundry1 card 1 | about 18 | 25 | board at or above 66 W, or any `minshire` at or above 72 C |

- **Every device command is a READ.** The one WRITE is the statistics reset in E184 arm B's pass 18441 (the owner's ruling of 31 October
  2026). No governor, TDP, threshold or clock set; no firmware, PMIC, reset or power cycle; no firmware-revisions query.
- A stop ends that run's queue; nothing is retried.

## 7. After the day, and the words the records use

- Each run's data verifier, then a critic, then ONE records round.
- **E182-W-int8's verdict is `size_P`**, its SIZE word against P (E182.md.dated-note-1.md section 2). `score_e182.py`'s
  `rules["E182-W-int8"]["verdict"]` field, and the verdict column of results.md for that one rule, carry `size_E`, which is arm E's reading:
  quote `size_P` as the verdict and `size_E` beside it as arm E's. Step 11 v2's last line says the same.
- A train's forecast half-width is 0.0051 W (doubled, about 0.0102 W), never 0.0049 (E182.md.dated-note-1.md section 1).

*Labels: every plan, cap, stop, clause and verdict word above is **registered** (E182.md, its notes and E184's kit); the 6 Nov post time is
**post hoc**; the day plan's order and its two-day form are the Q153 readiness critic's; nothing here is blind or held out.*

SPDX-License-Identifier: Apache-2.0
