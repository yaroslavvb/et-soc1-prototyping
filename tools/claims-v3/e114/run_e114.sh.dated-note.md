# Dated note on `run_e114.sh` (Mon 2 Nov 2026, week 45, Q136(w))

Written by Q136(w), the write-command audit, beside the script and not inside it: its sha256 is in E114's
`docs/reports/data/2026-11-01-e114-card0-replicates/logs/e114-start.json`, so its bytes stay as they ran (as
[`E114.md`](E114.md)'s dated note of 1 November already decided).

[`run_e114.sh`](run_e114.sh) lines 50–54 send `DM_CMD_GET_MODULE_FIRMWARE_REVISIONS`, which the echo at its line 50 calls
read only. It is not a read. At et-platform `836a4ab` (BL2 0.22.0) its handler writes the PMIC's firmware-management command
register twice, ACTIVE_SLOT then VERSION, and reads the data register after each (`services/firmware_update.c:903` → `driver/pmic_controller.c:952-974`, with the two writes at `:2543` and `:2587` (paths under `device-bootloaders/src/ServiceProcessorBL2/`)): a PMIC command by E85 C1's
standard. E114 sent it once, at 14:18:10 PST on 1 Nov 2026 on aifoundry1 card 0, and its records disclose it (E114's C1).
Its runner's residency reads asked raw states 4–6 too, each of which logs two SP Runtime Errors at BL2 0.22.0
([Q134(a)](../../../docs/reports/data/2026-11-01-q134a-alarm-residency/README.md)). Under the owner's rules of
2 November 2026 ([AGENT.md](../../../AGENT.md) section 5) every device command a run can send is classified before its
first launch, and a write outside the allowed statistics reset is NO-GO, so do not reuse the script as it stands:
`python3 tools/claims-v3/dmcmd_audit.py tools/claims-v3/e114/run_e114.sh` is NO-GO on line 52. Take a card's identity
from its module uptime (`DM_CMD_GET_MODULE_UPTIME`, service-processor RAM) against its last committed revisions read
instead (E77, E118, E120). The audit: [`docs/reports/data/2026-11-02-q136w-write-audit/README.md`](../../../docs/reports/data/2026-11-02-q136w-write-audit/README.md).
