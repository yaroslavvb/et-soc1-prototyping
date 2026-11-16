# The k6 runbook, dated note 3: its reboot gate, and the firmware read the owner allows (Q188)

*Written Sun 15 Nov 2026 (week 46), PST, on aifoundry2, desk only (Q188, the fix-guards lane). It sits beside
[`README.md`](README.md) and its dated notes [1](README.md.dated-note-1.md) and [2](README.md.dated-note-2.md), which stay as
committed; k6's code is unchanged, and so is every kit that pins it.*

k6's launch lines (`rb_common.sh`, `rb_guard_text`, lines 265-283) carry one firmware read per box (aifoundry1: E82's of
2026-10-31 13:45:24 PDT; aifoundry2: E69's of 2026-10-27 13:56:26 PDT) and stop a launch on any later boot with
`IDENTITY-STOP` (exit 16 through `rb_identity_stop`, lines 175-179), whose message says to show the identity "on a READ path
(never the firmware-revisions query)". aifoundry2 booted again on 2026-11-13 at 16:53:28 PST, so k6 refuses there.

The owner's words, Sun 15 Nov 2026: "Firmware revisions query was a false positive. It should have never been forbidden.
Reading operations and firmware are always allowed." (15:07:01 PST) and "Yeah, fix the corresponding guards. I don't want to
modify firmware, but commands which read firmware should be fine." (15:09:49 PST).

- **The parenthesis "never the firmware-revisions query" is superseded** for a kit written after this date: that query is a
  READ path. It is a READ in [`../../dmcmd_table_v2.json`](../../dmcmd_table_v2.json) (id 14).
- **A later kit opts in to [`../../fwgate/`](../../fwgate/README.md)** in place of k6's fixed dates: `fwgate.py look` (no
  device: continuity, or a read needed), `fwgate.py read` (one firmware read, under the card's lock with `et-who` free,
  compared with the box's newest record field by field; EQUAL writes a dated record, anything else stops, and then no
  later read or launch of that card follows on that boot, from any folder, until a person has read it), and
  `fwgate.py guard` at launch (k6's words: `identity: ... ok` or `IDENTITY-STOP: ...`, exit 0 or 16). Its records are the
  committed reads of E69 and E72 (aifoundry2), E82, E84 and E114 (aifoundry1) and E79 (aifoundry3), by path and sha256.
- **k6 itself stays as committed** (24 hash lists pin `rb_common.sh`): a kit that ports k6 unchanged keeps its gate, and on
  aifoundry2 after 13 November such a kit needs its own dated amendment to use fwgate instead.
- **Device commands:** a kit that calls fwgate lists it in its audit: `dmcmd_audit_v2.py` reads it GO with no allow-list;
  v1's `dmcmd_audit.py` reads it NO-GO.

SPDX-License-Identifier: Apache-2.0
