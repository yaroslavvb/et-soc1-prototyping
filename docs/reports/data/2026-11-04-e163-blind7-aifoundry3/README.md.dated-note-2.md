# Dated note 2 beside README.md, Wed 4 Nov 2026 (week 45), about 19:4x PST: when D1 was written (the card half's records)

*This note sits beside [`README.md`](README.md), not inside it: the README stays as committed in `4293d151` (16:54:31 PST), and so
does the first dated note, [`README.md.dated-note.md`](README.md.dated-note.md) (`3b102b85`, 17:42:42 PST). It records a fault the
card half's critic found after that note, the same class as E164's D1, which E164's dated note corrected
([`../2026-11-04-e164-blind7-card1/README.md.dated-note.md`](../2026-11-04-e164-blind7-card1/README.md.dated-note.md) § 2). Desk
only: no verdict, number, band, prediction, rule or frozen file changes, no device command is involved, and nothing here was
registered. It answers the same items as the README: the kinds page's
[section 11](https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers#11-what-is-still-open) item 6, and Q140's final critic's
ranks 1, 4, 9, 7 and 11.*

## D1 was written down after the reduction

The README's § Registered against what happened, row "departures", says: *"**D1, the collection route** (dated here, Wed 4 Nov 2026,
before the registered reduction ran)"*.

**What happened.**
- **The route was set before the session.** The lane's collection script (not in the repo) was last written at 14:31:31 PST, before
  the session began at 15:35:54. It copies the raw files into this directory's `aifoundry3/` and runs the registered collector,
  `collect_e163.sh`, over that repo-relative copy, with Q141(t)'s aifoundry3 arm.
- **The collection** ran 16:38:11–16:48:57 PST. The registered primary reduction wrote `e163.json` at 16:48:10 and `scored.json` at
  16:48:56 (the collector's output directory, `build/e163-out/2026-11-04-e163-blind7-aifoundry3/`, which is not committed).
- **D1's text came later.** The README was assembled from three drafts. Two hold no departures table: the one holding § Registered
  before any data (14:53:43 PST) and the tail (16:42:14). The only draft holding D1 was last written at 16:53:42, after the
  reduction. The README was committed at 16:54:31.

So D1 is a departure recorded after the reduction ran, not one dated before it.

**As it should read:** *"**D1, the collection route** (written after the reduction, Wed 4 Nov 2026, about 16:53 PST; the route, the
registered collector over this directory's repo-relative copy, was set in the lane's script at 14:31:31 PST, before the session)"*.
The rest of D1 stands. D1 changes no data choice: the registered collector, its arguments, the registered code and the reading of
"results.md written" are unchanged, and the copy it read is the raw data this directory commits.

## How this note was checked

- The drafts' and the script's times: the lane's own files (modification times read at about 19:30 PST, Wed 4 Nov 2026); the one
  draft whose text holds "D1, the collection route" is the one last written at 16:53:42.
- The reduction's times: the collector's outputs in `build/e163-out/2026-11-04-e163-blind7-aifoundry3/` (`e163.json` 16:48:10,
  `scored.json` 16:48:56) and the lane's collection log (16:38:11–16:48:57).
- The commit: `git log -1 --format=%ci 4293d151` (16:54:31 PST).
- No file in this directory was edited or re-made.

SPDX-License-Identifier: Apache-2.0
