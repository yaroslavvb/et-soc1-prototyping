# E170's data README, dated note 2 (Thu 5 Nov 2026; the records round Q143(r)): the login scrub reads one directory level, and its check now runs in every directory (0 left)

*Written on the Intel at about 19:55 PST on Thu 5 Nov 2026, desk only. [`README.md`](README.md) (lab `81178664`) and
[`README.md.dated-note.md`](README.md.dated-note.md) (`708a0a04`) stay as committed; no number, rule or verdict changes. This answers the
pool-8 card day's critic, whose records list asked for the scrub's wording here. For the kinds page's
[section 11](https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers#11-what-is-still-open), item 6.*

The README's section "Card and post" says that the collector's scrub (`scrub_etwho_e164.py`, "over this whole directory with the owner's login:
0 files rewritten") and its `--check`, "run again on `logs/` and on the whole directory", leave no other account's login in any file.
**Read it so:** the scrub and its `--check` read only the text files directly in the directory they are given, one level, so "the whole
directory" meant its top level, with `logs/` run separately. The fix pass of E172 and E174 (lab `04159d14`, 15:29:02 PST) then ran the
unchanged `--check`, with the owner's box login, in **every** directory of this data, in a copy with each `.gz` unpacked: **16 directories,
0 left**; box home paths: the owner's 5,671, another login's 0 (147 `.gz` unpacked, 144 `.bin` tiles left out;
[`../2026-11-05-e174-blind8-card0/posthoc-note1-e174.txt`](../2026-11-05-e174-blind8-card0/posthoc-note1-e174.txt), section 6). So the
README's conclusion holds, now on every directory: no other account's login is in any file here.

SPDX-License-Identifier: Apache-2.0
