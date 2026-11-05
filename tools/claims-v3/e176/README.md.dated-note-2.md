# Dated note 2 beside E176's kit README (Thu 5 Nov 2026; Q143(k)'s fix pass, before any E176 data): the collection by step 22 v2 with M11's scorer v2, what an entry means after A5, and the second session's own run number

*Written on the Intel from about 14:50 PST on Thu 5 Nov 2026, desk only: no card, no device command, no lab box, no post. No E176 or E177
datum is in any ref. [`README.md`](README.md) (lab `03582d2f`) and [`README.md.dated-note-1.md`](README.md.dated-note-1.md) (lab `6ecab3c5`)
stay as committed. No file of the kit's box list (`frozen-e176.sha256`, 29), no stop, hold, order, cap or card-minute figure changes. This
note answers the verifier of Q143(k) (Thu 5 Nov 2026, about 12:52-13:30 PST): its fault 2 (the collection's C gate), fault 8 (the second
session) and fault 7 (wording), with M11's amendment A5 (lab `9b084c66`). For the kinds page's
[section 11](https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers#11-what-is-still-open), items 9 and 8.*

## 1. The collection (the README's box step 6)

- **E176 is collected by the q143k runbook's step 22 v2,** [`../q143k-runbook/s22_collect_q143k_v2.sh`](../q143k-runbook/s22_collect_q143k_v2.sh),
  never by `collect_e176.sh` or `s22_collect_q143k.sh`. The step calls [`collect_e176_v2.sh`](collect_e176_v2.sh), which is
  `collect_e176.sh` with M11's scorer v2 ([`../m11/score_m11_v2.py`](../m11/score_m11_v2.py), lab `ebdbb35c`) and its lines file. The scorer
  v2 imports `score_m11.py` unchanged, and adds A5's readings, A4-3's two NOT SCORED reasons and the lines written before the later holds.
- **The C gate.** Dated note 1's row "the cc_gate: applies" was not enough. With p17620's C log missing, v1's step checked the smoke alone
  and said "collected and scored". Step 22 v2 adds the launch gate, `../q143k-runbook/cclaunch_q143k.py`. It requires p17620's C log,
  and p17601's whenever its marks show a launch, and it counts the checked launches against the `records` of every launch mark, process by
  process. The runbook's dated note 1 gives the rule and its desk test (24 of 24, the real collector end to end among them).
- **The command, after the session has ended and the card has been released:**
  `bash tools/claims-v3/q143k-runbook/s22_collect_q143k_v2.sh` (with `RB_OUT` and `RB_LOCK`, as every step), then the login scrubs and the
  public-text scan before any data commit.

## 2. What an entry means, read with A5

The README's "With the second session" says "a per-session calibration (A2's or A4's) enters at **81.0%** in § 0.1's case". That figure
stands as the rate at which a calibration enters. But **an entry no longer means that heat over minutes is set per session** (A5-1). It
means the session's own pair line carries to its later holds, blind given the watts, in its scope. M11 states "per session" only where the
entering calibration's agreement reading reads DIFFER (A5-3):
- in § 0.1's case on the likeliest pattern, in **66.4%** of draws (81.9% of the entries);
- where one line is common to both sessions, in at most **4.5%**.

Otherwise it states "common to the sessions, or not separated".

With today's one session, HM-CAL-AG and HM-I8-AG read NOT SCORED. Nothing enters, as before.

**Wording (the verifier's fault 7).** HM-CAL-I8's blind error is on **L2 alone**: the line through L1 and S, read on L2 (A4-2's scope, int8
holds on E97's natural chain inside the session's L1-S span; at the plan L2 is L1's own kind at w 0.788). It is not an error on every later
hold. The README's "HM-CAL and HM-CAL-I8 each give a blind error for the session's later holds" holds for HM-CAL (L1, S and L2). For
HM-CAL-I8 it is read as L2 alone. In § 0.1's case, A1-4 carries a common **gain** in at most 1.3% of draws (1.3, 0.2 and 0.0% at 2.35, 3.20
and 4.52%; A4-7's table, `design-power-heat-a4.json`). A common level is carried far more often (40.7-97.0% at 0.15-0.40 °C). So with two
sessions M11 reads one of three things: a common term (mostly a level), a calibration stated per session, or a calibration stated "common
or not separated". The result's "decides whether M11 carries a common gain, a common level or a per-session calibration" is read that way.

## 3. The second session (the verifier's fault 8)

**E176's kit runs one session.** The second M11 session on aifoundry3, on another day, gets **its own run number and its own kit**. That kit
is registered and kitted before it runs, from this one, with new pass numbers. It is never E176's kit again with p17601 and p17620:
- `lib.sh`'s `block_begin` (`../lib.sh` line 181) reads p17620's `block.json` as "already done" and exits 0, so no measured pass would run;
- step 11 refuses p17601 without `--later-try`, and `--later-try` moves only the smoke aside (p17601 → p17601.try1, once).

Its scoring names E176's committed pass directory as an earlier M11 aifoundry3 pass, because HM-LG, HM-CAL, HM-CAL-I8 and A5's readings read
a card kind's sessions together (REGISTRATION.md § 3). Its precedence check covers every registration and amendment commit, A5's among them.

## What it does to predicting power and heat

Nothing to any number. E176's one session is collected only if every measured launch was checked for C. Its readings are stated as A5
words them, so a "per session" heat term is claimed only where the sessions' pair lines differ.

SPDX-License-Identifier: Apache-2.0
