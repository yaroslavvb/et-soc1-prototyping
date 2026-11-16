# The write-command audit, dated note 1: the firmware-revisions query and GET_FRU are reads (Q188)

*Written Sun 15 Nov 2026 (week 46), PST, on aifoundry2, desk only (Q188, the fix-guards lane). It sits beside
[`README.md`](README.md), which stays as committed; its results 3 and 6 read with this note.*

The owner's words, Sun 15 Nov 2026: "Firmware revisions query was a false positive. It should have never been forbidden.
Reading operations and firmware are always allowed." (15:07:01 PST) and "Yeah, fix the corresponding guards. I don't want to
modify firmware, but commands which read firmware should be fine." (15:09:49 PST).

- **Result 3's first row** ("NO-GO (a PMIC command, though named GET)") and **result 6** ("a card's identity now comes from
  module-uptime continuity") are superseded for a run written after this date: `GET_MODULE_FIRMWARE_REVISIONS` (14) is a
  READ. Its handler's two writes to the PMIC's firmware-management command register (0x16) each select a query, ACTIVE_SLOT
  then VERSION, whose answer is read from the data register (0x17); it never issues an update or boot-slot subcommand and
  never writes the data register (et-platform `836a4ab`, `driver/pmic_controller.c:952-974` and `:2531-2600`;
  `include/pmic_hal.h:66-77`). The register facts in result 3 stand, and so do the sends result 6 lists: they were reads.
- **Result 3's paragraph on `GET_FRU`** (71) likewise: it writes the FRU command register (SET_OFFSET, then
  READ_FRU_DATA_BYTE) and the offset once, then reads the record; it never issues WRITE_FRU_DATA_BYTE or WRITE_COMMIT
  (`:2412-2445`; only `SET_FRU`, 70, does, `:2485-2502`). A READ. The vendor tool writes its answer, which holds board
  identifiers, to a file in its working directory: never commit it.
- **What carries it:** [`tools/claims-v3/dmcmd_table_v2.json`](../../../../tools/claims-v3/dmcmd_table_v2.json), made from
  this audit's table by [`make_dmcmd_table_v2.py`](../../../../tools/claims-v3/make_dmcmd_table_v2.py) with exactly those two
  entries changed (class READ, pmic "read", so `--deny-pmic-read` still refuses them; each with the ruling and the handler
  lines) and every other line kept byte for byte; [`dmcmd_audit_v2.py`](../../../../tools/claims-v3/dmcmd_audit_v2.py), this
  audit's checker reading it; [`test_dmcmd_audit_v2.py`](../../../../tools/claims-v3/test_dmcmd_audit_v2.py); and
  [`tools/claims-v3/fwgate/`](../../../../tools/claims-v3/fwgate/README.md), which reads a card's firmware after a reboot and
  compares it with the box's record.
- **One side effect, on v1 alone:** `dmcmd_audit_v2.py` skips v1's two files and its own two; v1's checker skips only its
  own two, so v1 run over the top level of `tools/claims-v3/` now also lists the command sites in v2's audit and its tests
  (41 records when this note was written, 42 when those two files are audited alone) and reads NO-GO there. No committed
  kit audits that folder with v1 (none of the kits' 50 audit calls, verify-guards' count at Q188); a kit audits its own
  files.
- **What does not change:** every other WRITE of this audit (38 entries), every form and pseudo entry, and the checker's
  rules. `dmcmd_table.json` and `dmcmd_audit.py` stay as committed (sha256 `50168632...` and `f29e91ca...`) for the kits that
  pin them; a kit written before 15 November keeps them.

SPDX-License-Identifier: Apache-2.0
