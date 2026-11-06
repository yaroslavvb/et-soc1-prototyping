# Dated note 4 beside E176's kit README (Fri 6 Nov 2026, week 45): a file the runner reads that the box list never named

*Beside [`README.md`](README.md) (`03582d2f`) and its dated notes [1](README.md.dated-note-1.md), [2](README.md.dated-note-2.md) and
[3](README.md.dated-note-3.md), none of which it edits; `frozen-e176.sha256` and `kit-e176.sha256` stay as committed. Written by the
records round after E181's kit round (Q148(r)), desk only, from a defect E181's kit lane found and its verifier confirmed.*

**The defect (the E174 class: a file the run reads that the box list does not carry).** [`run_e176.py`](run_e176.py) calls E97's
`check_reused()` ([`../e97/e97_common.py`](../e97/e97_common.py), line 110), which checks the sha256 of eight reused files against E97's
frozen harness block. One of the eight, [`tools/claims-v3/e89/reduce_e89.py`](../e89/reduce_e89.py), is in neither E176's box list
([`frozen-e176.sha256`](frozen-e176.sha256), 29 entries) nor the q143k runbook's step 7 sync. E176's session ran only because aifoundry3
kept a matching copy from earlier sessions, so the check passed on the box.

**How it was found.** E181's kit, ported from this one, ran its Intel dry pass (DRY-INTEL) in a tree built from step 7's sync list alone,
and the pass stopped on `reduce_e89.py` at once. **E181's box list names it** (30 entries: 27 repo files and three box binaries; its
sha256 equals E97's freeze, as do the other seven), so E181's step 7 syncs it and step 8 checks it
([`../e181/README.md`](../e181/README.md), "An E174-class defect found and fixed").

**What it changes for E176:** nothing measured or scored. E176 was refused at its start gate G0 and nothing is scored (dated note 3); the
copy its check read on the box matched the frozen sha256. **For any later kit ported from E176's:** take the box list from every file the
runner and its imports read (E181's form), and test it on a tree built from the sync list alone. E181's lanes did not check E178's or E180's kits
for this class; Q146(f)'s critic built a tree from each kit's v2 sync list alone and found every harness file in it at its sha256 (E178
80 of 80 non-binary files, E180 61 of 61), which tests the harness lists, not every file a runner's imports read.

SPDX-License-Identifier: Apache-2.0
