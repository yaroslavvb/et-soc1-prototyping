# Dated note on `run_e79.sh` (Mon 2 Nov 2026, week 45, Q136(w))

Written by Q136(w), the write-command audit, beside the script and not inside it: E79's `code.sha256` files
(`docs/reports/data/2026-10-31-e79-fp16-int8-bit-prices/code.sha256` and each pass's) hold its hash, so its bytes stay as
they ran.

[`run_e79.sh`](run_e79.sh) line 49 sends `DM_CMD_GET_MODULE_FIRMWARE_REVISIONS` among its identity queries. It is not a
read. At et-platform `836a4ab` (BL2 0.22.0) its handler writes the PMIC's firmware-management command register twice,
ACTIVE_SLOT then VERSION, and reads the data register after each (`services/firmware_update.c:903` → `driver/pmic_controller.c:952-974`, with the two writes at `:2543` and `:2587` (paths under `device-bootloaders/src/ServiceProcessorBL2/`)): a PMIC command by E85 C1's standard. E79 sent
it once, on aifoundry3 at 09:27:22 PDT on 31 Oct 2026; the card answered normally. Under the owner's rules of
2 November 2026 ([AGENT.md](../../../AGENT.md) section 5) every device command a run can send is classified before its
first launch, and a write outside the allowed statistics reset is NO-GO, so do not reuse the script as it stands:
`python3 tools/claims-v3/dmcmd_audit.py tools/claims-v3/hlp/run_e79.sh` is NO-GO on line 49. Take a card's identity from
its module uptime (`DM_CMD_GET_MODULE_UPTIME`, service-processor RAM) against its last committed revisions read instead
(E77, E118, E120). The [hlp README](README.md) carries the same note, and the audit is
[`docs/reports/data/2026-11-02-q136w-write-audit/README.md`](../../../docs/reports/data/2026-11-02-q136w-write-audit/README.md).
