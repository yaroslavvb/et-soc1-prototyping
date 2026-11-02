# Dated note on `block.sh` and `README.md` (Mon 2 Nov 2026, week 45, Q136(w))

Written by Q136(w), the write-command audit, beside the two files and not inside them: each TEL pass's `code.sha256`
(`docs/reports/data/2026-09-25-claims-v3/raw/*/tel/p*/code.sha256`) holds their hashes, so their bytes stay as they ran.

- **[`block.sh`](block.sh) line 332 and [`README.md`](README.md) line 47 send `DM_CMD_GET_MODULE_FIRMWARE_REVISIONS`.**
  It is not a read. At et-platform `836a4ab` (BL2 0.22.0) its handler writes the PMIC's firmware-management command
  register twice, ACTIVE_SLOT then VERSION, and reads the data register after each (`services/firmware_update.c:903` → `driver/pmic_controller.c:952-974`, with the two writes at `:2543` and `:2587` (paths under `device-bootloaders/src/ServiceProcessorBL2/`)); the same two writes are in
  the public source at every BL2 version from 0.18.0 to 0.22.0. That is a PMIC command by E85 C1's standard. The block
  sent it once a pass, nine times on 25–26 September 2026, as its check that `dev_mngt_service -n <n>` reached the right
  card ([the claims-v3 data README](../../../docs/reports/data/2026-09-25-claims-v3/README.md), its dated note). On
  aifoundry1 that check no longer tells the cards apart anyway: both report release 1.4.0 / BL2 0.22.0 since 31 Oct.
- **The block's other writes**, each a WRITE in [`dmcmd_table.json`](../dmcmd_table.json): `ettelem loglevel info` and
  `debug` (`DM_CMD_SET_DM_TRACE_CONFIG`, lines 186, 316, 379 and 408: the SP log level, left at INFO, never restored to
  the boot default WARNING, which the stock `ettelem` cannot set); `dev_mngt_service -t SPST:enable`
  (`DM_CMD_SET_STATS_RUN_CONTROL` with control 1, lines 185 and 194); and the reset segment's `ettelem sample --reset-ms`
  (the statistics reset, which also turns the SP stats trace off, as README "Deviations" 1 says).
- **Under the owner's rules of 2 November 2026** ([AGENT.md](../../../AGENT.md) section 5) every device command a run can
  send is classified before its first launch, and a write outside the allowed statistics reset is NO-GO. Do not reuse
  this block as it stands: `python3 tools/claims-v3/dmcmd_audit.py --allow SET_STATS_RUN_CONTROL tools/claims-v3/tel/block.sh`
  is NO-GO on line 332 and the four `loglevel` lines. Take a card's identity from its module uptime
  (`DM_CMD_GET_MODULE_UPTIME`, service-processor RAM) against its last committed revisions read instead (E77, E118, E120).

The audit: [`docs/reports/data/2026-11-02-q136w-write-audit/README.md`](../../../docs/reports/data/2026-11-02-q136w-write-audit/README.md).

**Corrected after verification, Mon 2 Nov 2026 (week 45), by Q136(w)'s fix pass; nothing above is edited.** The checker
line above under-reports two writes. `--allow SET_STATS_RUN_CONTROL` used to pass every form of that command, and lines
185 and 194 (`dev_mngt_service -t SPST:enable`, type 1, control 1: the SP stats trace switched on, nothing reset) are
not the statistics reset the owner ruled on (type 1, control 2); and `$ETTELEM` and `$DEVMNGT` come from `lib.sh`, which
the line does not pass. With the corrected checker, `python3 tools/claims-v3/dmcmd_audit.py --allow STATS_RESET
tools/claims-v3/tel/block.sh tools/claims-v3/lib.sh` is NO-GO on line 332 (the revisions query), the four `loglevel`
lines (186, 316, 379, 408) and the two `SPST:enable` lines (185, 194): `SPST_TRACE_CONTROL`, a write outside the ruled
reset. The audit's "Corrections after verification" lists the change.
