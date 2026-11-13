# The card lane's brief, dated note 4 (Fri 13 Nov 2026, before any E183 datum; Q170): E183's next day by its kit's dated note 5: step 2 is s03 v6, step 11 is s22 v3, and both older steps are never run alone

*Beside `CARD-LANE-BRIEF.md` (E183's copy, `6860643c`) and its dated notes 1 (`1e74546a`), 2 (`e8e9f4e1`) and 3 (`24b9b99e`), which it
edits nothing of. It is E183's alone. Written on aifoundry2, desk only, by the lane `fix-note5` of Q170 (begun at 12:20 PST Fri 13 Nov 2026
by the clock; its commit's own time is git's), answering the verifier `verify-note5`'s sixth finding: note 3's table still named step 2 v5 and
step 11 v2, so a lane reading the brief alone would run step 11 v2, which stops at its desk-path gate (16) on a desk whose home has the box
account's shape. The code is E183's kit note 5 ([`KIT.md.dated-note-5.md`](KIT.md.dated-note-5.md)). **It adds no rule, forecast, threshold,
plan, cap or stop.** No card was claimed, no device command was sent, no lab box was reached, nothing was posted.*

## 1. The order (note 3's section 2), two rows changed

| | step | file |
|---|---|---|
| 2 | the desk check | **`rb/s03_desk_e183_v6.sh`** (step 2 v5, then note 5's list at its 24 entries and its two desk tests' logs) |
| 11 | the release, then the collection | **`rb/s22_collect_e183_v3.sh`** (step 11 v2 with note 5's desk-path gate; it checks the gate's inputs first, before any copy) |

Every other row is note 3's.

## 2. Never run alone on that day (note 3's list, extended)

Note 3's list, and also: **step 2 v5** (`rb/s03_desk_e183_v5.sh`, which runs unchanged inside step 2 v6) and **step 11 v2**
(`rb/s22_collect_e183_v2.sh`).

## 3. Readings on the day (beside note 3's section 3)

- **Step 11 v3's first line** (`the desk-path gate's inputs (note 5): HOME is this account's home, and no entry of it is named 'aifoundry'`)
  comes before any copy. A 10 there means `HOME` is not this account's home: set it, and run step 11 v3 again (nothing was copied). A 16
  there means the desk's home holds an entry named `aifoundry`: move it aside, or collect from another desk.
- **Step 11 v3's gate** runs two reads over the output: nopath's (`no desk path in what was written`) and the spelling check's
  (`nopath_spell: ... CLEAN`). A 16 at either reads "a desk path reached what this step wrote" (the HIT lines above it name the file and
  the kind): commit nothing, fix the route, move `build/e183-raw` and the output aside, collect again.
- **The dry listing's "run on the Intel"** (k6's wording) means the desk: aifoundry2 when the card lane runs from there.
- **The anchor lines** the go names for note 5 (never written here, since this note is in the list they name): the commit that added note 5
  is an ancestor of the lab clone's HEAD; `SHA256SUMS-e183-kit-note5`'s own sha256 and its 24 entries each OK from the lab's top; the own
  sha256 of `rb/s03_desk_e183_v6.sh` (outside that list); and note 4's lines, still true.

SPDX-License-Identifier: Apache-2.0
