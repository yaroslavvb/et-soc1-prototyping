# aifoundry1: what is broken (25 September 2026)

The evidence behind [`../../2026-09-25-aifoundry1-troubleshooting.html`](../../2026-09-25-aifoundry1-troubleshooting.html)
(published at <https://spacesheep.dev/@yaroslavvb/aifoundry1-troubleshooting>, with the fix log at <https://spacesheep.dev/@yaroslavvb/aifoundry1-fix>), written for Roman
Shaposhnik's question "Can someone try to see exactly what is broken on 1?".

- `facts.md`: the read-only facts gathered on aifoundry1, 2 and 3 (sysfs, modinfo, lspci, dpkg, file hashes,
  /proc/interrupts, the logs of our 22 September attempts), with the side-by-side table and the source locations.
- `collect.sh`: the read-only collection script (no device is opened; no root).
- `answer-for-roman.txt`: the short answer.

How it was found: a workflow of AI agents (one fact-gatherer, three analysts with different lenses, a skeptic for each,
a writer and a checker); every statement in the report was re-checked against fresh read-only output. No card was
opened: another user was logged in on aifoundry1, and our own experiment queues held the cards on aifoundry2 and 3.
Raw per-host outputs were not committed (they list other users' processes).

*Dated note, Mon 2 Nov 2026 (week 45), added by Q136(w), the write-command audit, without editing the text above:* the
fix log of that afternoon ([`fix-transcript.txt`](fix-transcript.txt), 15:02:17 PDT, line 157) sent
`DM_CMD_GET_MODULE_FIRMWARE_REVISIONS` to card 0 and to card 1, and both published pages give it as a check
([`2026-09-25-aifoundry1-fix.html`](../../2026-09-25-aifoundry1-fix.html) line 168,
[`2026-09-25-aifoundry1-troubleshooting.html`](../../2026-09-25-aifoundry1-troubleshooting.html) lines 280–281). It is
not a read. In the public et-platform source its handler writes the PMIC's firmware-management command register twice,
ACTIVE_SLOT then VERSION, and reads the data register after each (`services/firmware_update.c:903` → `driver/pmic_controller.c:952-974`, with the two writes at `:2543` and `:2587` (paths under `device-bootloaders/src/ServiceProcessorBL2/`), at `836a4ab`), and the same two writes are
there at every BL2 version from 0.18.0 (card 1's then) to 0.22.0: a PMIC command by E85 C1's standard. The cards
answered normally. The two pages are not edited here (each is mirrored on spacesheep and must equal its file). Under the
owner's rules of 2 November 2026 ([AGENT.md](../../../../AGENT.md) section 5) every device command is classified before
the first launch and a write outside the allowed statistics reset is NO-GO: tell a card's firmware by its module uptime
(`DM_CMD_GET_MODULE_UPTIME`) against a committed read, not by sending the query again. The audit:
[`2026-11-02-q136w-write-audit`](../2026-11-02-q136w-write-audit/README.md).
