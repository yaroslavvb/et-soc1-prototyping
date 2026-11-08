# E186's kit, dated note 2: records lines for the verifier's nits 3-7 on A1 and kit note 1 (the provisional counts in two of note 1's logs, the scale route's refusal at scoring, the host's hash named exactly, A1's power with its Monte Carlo error, E186-PAIR a check of the records present) (Q158; before any datum)

*Sun 8 Nov 2026 (week 45), PST, on the Intel, desk only (Q158, lane `fix-fx`, begun at 11:31 PST by the clock; its commit's own time is
git's): no card was claimed, no device command was sent, no lab box was reached, nothing was posted. **No E186 datum exists** (`git log
--all` shows no `docs/reports/data/*e186*`). It answers the adversarial verifier of E186's dated amendment A1 (`17cf100f`, git 10:18:16 PST)
and of the kit's dated note 1 (`88750359`, git 10:28:34 PST) (`verify-fx`, Sun 8 Nov 2026 10:42-11:3x PST: **holds with fixes**, 2 minor
faults and 6 nits, none blocking). Its two minor faults are the day-2 check's (E185's kit note 4,
[`../e185/KIT.md.dated-note-4.md`](../e185/KIT.md.dated-note-4.md)); its nit 8 is the day-2 brief's. Its nits 3-7 are E186's, and each
asks for a records line: they are here. **New file only, and no code:** [`KIT.md`](KIT.md), [`KIT.md.dated-note-1.md`](KIT.md.dated-note-1.md),
[`E186.md.dated-amendment-A1.md`](E186.md.dated-amendment-A1.md) and every kit file stay as committed. **No rule's statistic, threshold or
words change, and no forecast, plan, cap, stop, gate or device command changes;** each line below says how a committed sentence or figure
is to be read.*

## 1. Kit note 1's history and runbook logs hold a provisional tree's counts (nit 3)

Kit note 1's lane made `logs/selftest-history-e186-v2.txt` and `logs/selftest-rb-e186-v2.txt` while its own list was provisional, so their
counts are that tree's, not the committed one's. Re-run by this lane on a scratch clone at `88750359` (Sun 8 Nov 2026 12:00:29-12:02:35 PST,
through the round's slot): **every PASS line is the same** (SELFTEST-HISTORY-E186-V2 9 of 9, SELFTEST-RB-E186-V2 13 of 13, the PASS texts
equal to the committed logs'), and the counts read:

| log | line | committed | at `88750359` |
|---|---|---:|---:|
| `selftest-history-e186-v2.txt` | entries in `SHA256SUMS-e186-note1` | 13 | 40 |
| | files added since `a41408d9` | 76 | 82 |
| | files tracked in the clone | 55,691 | 55,697 |
| `selftest-rb-e186-v2.txt` | files committed in the scratch repository | 2,072 | 2,074 |
| | files the sync sent | 128 | 129 |

The verifier found the same. **Read those lines as the provisional tree's;** the PASS lines, and every reading the logs support, stand.

## 2. A change on the scale route stops the scorer at scoring: it never reads "s not read" (nit 4)

Kit note 1 section 4 says that a committed change to a listed file of the session scale's route, made with its list line, "was refused only
by the predictor's own check, at scoring: s not read, the four ladder trains' SIZE words, E186-GB and E186-GA NOT SCORED". **That is not
what happens.** Pool 8's predictor refuses with `stop()`, which raises `SystemExit`; `score_e186.read_scale` catches `Exception` only, so
the refusal is not read as an unread s: `score_e186.py` stops (exit 1, "POOL8 STOPPED: inputs differ ...") and `score_e186_v2.py` exits 9
("REFUSED (9)"), each with no scored file. Re-run by this lane at `88750359` on a synthetic FULL session (the verifier's, read only), with
M10's `m10.json` one byte longer and not committed: the intact tree scores (rc 0, s read); the changed one reads rc 1 and rc 9, no scored
file; and the history check v2 on that tree reads 16, as step 11 v2 runs it before any scoring, so the case is refused first, the raw copy
kept. **A1-1's branch ("s not read") is the scale reading no anchor**, A1-1b's case; a refusal on the route's inputs is a stop, never that
branch.

## 3. The pairing's hash, named exactly (nit 5)

A1-2, [`pairing_e186.py`](pairing_e186.py) and kit note 1 call the C record's hash "FNV-1a 64". The lab's function, in the C-logging host
(`tools/claims-v3/ccheck/patch_host_ccheck.py` line 46, `ccFnv`), the check of C (`tools/claims-v3/ccheck/ccheck.py` line 85, `fnv64`) and
the pairing (`pairing_e186.fnv64`), has FNV-1a's form (each byte xored in, then a multiply by the 64-bit prime 1099511628211) with the
offset basis **1469598103934665603**, not FNV-1a's standard 14695981039346656037. Host and desk use the same constant, so the pairing holds
(E182's committed trains: 5,712 of 5,712 launch records, post hoc). **Read it as "the C-logging host's FNV-1a-form 64-bit hash, offset
basis 1469598103934665603"**; a re-implementation from the standard basis pairs none of them.

## 4. A1's power, with its Monte Carlo error (nit 6)

A1's shares are Monte Carlo estimates from **1,000 sessions a case** (`power-e186-a1.json`, its `draws`). Each carries a binomial error;
at plus or minus 2 standard errors (2 sqrt(p(1-p)/1000)), E186-M over the five trains when s is not read (A1-1, its registered power) reads:

| noise | M12 holds | M12, with its parameter uncertainty | M12, H16 at the fp16-scaled arm | M10 holds |
|---|---|---|---|---|
| REGISTERED | 0.988 +- 0.007 | 0.953 +- 0.013 | 0.980 +- 0.009 | 0.927 +- 0.016 |
| MEASURED | 0.981 +- 0.009 | 0.950 +- 0.014 | 0.983 +- 0.008 | 0.913 +- 0.018 |
| DOUBLED | 0.954 +- 0.013 | 0.920 +- 0.017 | 0.952 +- 0.014 | 0.938 +- 0.015 |

(the two H16-scaled cases at MEASURED and DOUBLED noise are the JSON's; A1's table shows the other ten). **A1's "0.91-0.99 in every case"
reads 0.895-0.995 with the error kept** (its lowest share 0.913 less 0.018; its highest 0.988 plus 0.007). The registered nine-train shares A1 sets beside them carry the same
order of error (plus or minus 0.003 to 0.019). The verifier's own desk re-simulation (20,000 sessions a case, numpy only; not committed,
reported) lands within about 2 standard errors of each, 0.928-0.985. A1's figures and words stand as registered; only their error is added.

## 5. E186-PAIR is a check of the records present (nit 7)

`pairing_e186.check_block` reads every launch record a train block holds, and only those. It does not require every planned process and
launch to be there (completeness is the trains' reduction's 13-launch rule and E186-C's); it passes a record with no `type` field (A1-2's
"where the record names one"); and in the fallback (PASSES), which runs no train block, **E186-PAIR reads PASS over none: quote it as "no
train block read"**, never as a pairing that passed. On E182's committed trains (post hoc, the verifier's own count) every planned process
and launch is there once, 5,712 records, none without a type. **Read E186-PAIR as "every launch record present pairs with the registered
schedule, type and tile bytes".**

## 6. What stays as it was

- Outside the core directories E186's history check v2 does not see an untracked file (kit note 1 section 4, a limit kept from v1; the
  verifier's case U4, an untracked `json.py` in pool 8's predictor's directory, reads 0). This note changes no E186 check. The day-2 check v2
  (E185's kit note 4) reads untracked modules in every directory of its perimeter; that is the form a later E186 note can take, before any
  datum.
- Note M2 (later versions' forecasts and v4's on M12's set) is the arms lane's: additions only, its own reader, a gate in a step 11 v3.

## 7. Builds on (the stock-take's rule for lanes, MAP section 3)

1. **Checked:** the stock-take's INVENTORY.md, read Sun 8 Nov 2026 at 11:58:12 PST. Public rows read: H07, H08, H09, H24, H25, H28. Newer
   pieces by commit: A1 (`17cf100f`) and kit note 1 (`88750359`).
2. **Used** (unchanged; sha256 in [`SHA256SUMS-e186-note2`](SHA256SUMS-e186-note2)): kit note 1's two logs, A1's power JSON, the pairing,
   the scorers v1 and v2, kit note 1's and A1's lists. *Check against the same operation:* the two desk tests re-run at `88750359` give the
   committed PASS lines word for word (section 1).
3. **Not used:** any card time; any rule, forecast or figure not named above; the october-forecast-model's notes.
4. **Tiers:** public tier; it cites public pieces only.
5. **Readiness:** a verifier checks this block against INVENTORY.md and the cited commits.

## Labels

A1's power figures are **registered** (by simulation); the errors beside them are a desk computation from A1's own committed JSON. The
pairing on E182's committed trains is **post hoc**, a check of code deciding nothing; the verifier's re-simulation is **reported**. Every
re-run here is a check of code at the desk, not a measurement: nothing is **blind** or **held out**, and no E186 datum exists.

SPDX-License-Identifier: Apache-2.0
