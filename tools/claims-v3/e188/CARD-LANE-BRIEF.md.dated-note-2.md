# E188's card-lane brief, dated note 2: the lane run from aifoundry2 - steps 2, 10 and 11 from the kit's dated note 2 on, the lab's top read before step 1, the go's anchor lines, and what the day records (Q182, before any E188 datum)

*Sun 15 Nov 2026 (week 46), PST, on aifoundry2, in Q182 (lane `port-e188`; changed in place before its land by the lane `fix-port188` on
`verify-port188`'s findings, the kit's dated note 2, section 14), desk only: no card claimed, no device command sent, no lab box reached,
nothing posted. [`CARD-LANE-BRIEF.md`](CARD-LANE-BRIEF.md) (`726a6b64`) and its [dated note 1](CARD-LANE-BRIEF.md.dated-note-1.md)
(`16b41cf2`) stay as committed; where this note differs, this note governs. It goes with the kit's [dated note 2](KIT.md.dated-note-2.md).
**No E188 datum exists.** It changes no rule, forecast, threshold, plan, cap or stop. E188 runs only on the owner's go naming it.*

## 1. The steps that change (the brief's section 2 table, after note 1)

| # | the step from this note on | what to do with its exit |
|---|---|---|
| 1 | `rb/s02_window_e188.sh <day> <last start> <last end>`, unchanged, **right after** `/usr/bin/python3 -I -B tools/claims-v3/e188/rb/check_top_e188.py`, read from the lab clone's top (a read: it writes nothing). Step 1's window script runs with the lab's top first on its path, and the history check does not read the top (the check also reads E183's rb/ folder, which step 11 v2 brings into the day: the kit's note 2, section 14) | the read: `TOP OK`, else (`TOP REFUSED` names a module, byte-code or `.pth` file at the lab's top or in E183's rb/) no step that day; step 1's own exits as the brief's |
| 2 | `rb/s03_desk_e188_v3.sh` with `RB_GITLOCK` set to the lab-git lock the desk's commit helper takes, **never inside that lock** (read `uptime` first: the 1-minute load at or below 8). It takes the lock for its pull with `flock -w 600 -E 75` on aifoundry2 (`lockf -k -t 600` on the Intel), checks the forecast within its stated tolerance, reads the lab's top again after the history check (`check_top_e188.py`), pins every list (v1's, the kit's, note 1's two, A2's, note 2's) and names the desk's `/usr/bin/python3` in its last line. For its pull only, and in the environment (never a git config file), the lane may set `GIT_CONFIG_COUNT=1 GIT_CONFIG_KEY_0=url.https://github.com/.insteadOf GIT_CONFIG_VALUE_0=git@github.com:` | anything but 0: no box step that day, whatever it names (16 naming HEAD-moved: a co-owner committed meanwhile, run it again; 16 naming its pull with the lock tool's exit 75: it ran inside the lab-git lock; 16 naming `top`: a module, byte-code or `.pth` file at the lab's top or in E183's rb/, its `TOP REFUSED` line names it) |
| 10 | `rb/s20_wait_e188.sh`, unchanged, again while it says 17 | 0: ended with its MANIFEST.sha256 (read its printed lines); 16: a gate stop, its manifest written, still collected; 14: RUN-GONE (no session process and no session end) or MANIFEST-ABSENT: read the box read-only before anything; 10: RUN-UNKNOWN |
| 11 | the release (if the day has a post), then `rb/s22_collect_e188_v2.sh` | as step 11 v1, and before any copy: 10 (HOME is not this account's home) or 16 (the desk's home holds an entry named `aifoundry`); after the history check, before any scoring: 16 at the lab's top or E183's rb/ (`TOP REFUSED`; nothing scored, the raw copy kept); at the end 16 only for a real desk path |

Every other step, its order and its exits are the brief's section 2 with note 1's step 9 v2. The dry listing is
`rb/list_steps_e188_v3.sh`. **Never that day from aifoundry2:** step 2 v1 or v2 (they stop at the pull: no `/usr/bin/lockf` there), step 11
v1 (its gate stops on aifoundry3's own paths, which carry the desk's home as their prefix), step 9 v1, or `rb/rest_rule_e188.sh` by hand.

## 2. The go's anchor lines (the brief's section 1, fourth item; note 1's section 2)

The kit's and note 1's lines stay as they are. They gain six, in the order of the land's record, where their values are (a note cannot
hold its own list's sha256):

1. the kit's dated note 2's commit an ancestor of HEAD; `git show --name-status` on it: one line a file (23), all `A`, all under
  `tools/claims-v3/e188/`;
2. `SHA256SUMS-e188-kit-note2` and `rb/s03_desk_e188_v3.sh` unchanged since that commit (`git diff --quiet`);
3. `SHA256SUMS-e188-kit-note2` at the sha256 the go names, 23 entries, and `sha256sum -c` (or `shasum -a 256 -c`) reading every
  entry OK: 23 of 23; `SHA256SUMS-e188-a2` 1 of 1;
4. step 2 v3 at the sha256 the go names (it is outside the list), and its pin line for note 2's list naming that list's count (23)
  and sha256;
5. step 11 v2, `forecast_tol_e188.py` and `rb/check_top_e188.py` at the sha256s the go names (each also in the list);
6. no E188 datum in any ref before step 1 (`git log --all --oneline -- 'docs/reports/data/*e188*'` prints nothing): the kit's own
  line, read again with note 2's commit in place.

## 3. What the day records (beside the brief's)

- **The interpreter:** step 2 v3's last line names the desk's `/usr/bin/python3` (3.12.3 on aifoundry2). The collector and the scorer run
  under it; their printed figures may differ from a 3.9 run's in the last digits (the kit's note 2, section 1, item 5). Name it in the
  data README beside the verdicts.
- **The lab's top:** the read before step 1 and the two `TOP OK` lines (steps 2 and 11), as each printed it.
- **`USER` on the box** (the kit's note 2, section 7, a carried gap): E188's D1 rule reads `$USER`; on aifoundry3 the ssh login sets it, and
  the session inherits it from step 9's launch. Nothing gates it; the readiness check says whether the lane reads it.
- **No post, by the owner's standing waiver:** his words, Sun 15 Nov 2026 10:22:36 PST, "don't worry about discord post, just use the
  machines, nobody is using them", standing until he says otherwise (before them, his words of Fri 13 and Sat 14 Nov 2026 waived those
  days' posts). The post (step 3) and the release (step 11's first part) are skipped unless the day's go asks for them; every other
  etiquette check stays. The lane's result and the data README record it as a dated departure: "the owner waived the post: his words,
  Sun 15 Nov 2026 10:22:36 PST". (Corrected before the land by `fix-port188`, `verify-port188`'s finding 2: this item cited only the
  Friday and Saturday waivers.)

## 4. Labels

Every figure here is **registered** (E188.md with its amendments) or a **desk check of code** (the kit's dated note 2). Nothing here is
measured, blind, held out or post hoc.

SPDX-License-Identifier: Apache-2.0
