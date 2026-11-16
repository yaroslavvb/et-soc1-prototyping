# fwgate: the firmware-identity gate, read after a reboot (Q188)

*Sun 15 Nov 2026 (week 46), PST, on aifoundry2, desk only (Q188: written by the fix-guards lane, revised by the fix-guards2
lane after its verifier's findings): no device opened, no card lock taken, no device command sent, no ssh to a lab box. New
files only; k6 (`../q141k-runbook/k6/`) and every earlier gate stay as committed. A kit opts in by calling it; nothing calls
it by itself.*

## Why it exists

A card's firmware identity has been carried by continuity: a box that has not booted since a committed firmware read of
its card still runs that firmware. k6's launch gate (`../q141k-runbook/k6/rb_common.sh`, `rb_guard_text`) wrote one read
per box into its code (aifoundry1: E82's of 2026-10-31 13:45:24 PDT; aifoundry2: E69's of 2026-10-27 13:56:26 PDT) and
refused a launch on any later boot, because the one command that reads the firmware back,
`DM_CMD_GET_MODULE_FIRMWARE_REVISIONS`, was classed a PMIC write. aifoundry2 booted again on 2026-11-13 at 16:53:28 PST,
so every k6-derived kit there refused (exit 16).

The owner's words, Sun 15 Nov 2026: *"Firmware revisions query was a false positive. It should have never been forbidden.
Reading operations and firmware are always allowed."* (15:07:01 PST) and *"Yeah, fix the corresponding guards. I don't want
to modify firmware, but commands which read firmware should be fine."* (15:09:49 PST). The audit table v2
([`../dmcmd_table_v2.json`](../dmcmd_table_v2.json)) classes the query READ (id 14) with the handler lines; fwgate is the
gate that uses it: after a reboot it reads the firmware again and compares it, field by field, with the record.

## What it does

`fwgate.py` (stdlib Python 3; run with `/usr/bin/python3` on the boxes, 3.12.3 on aifoundry2):

| subcommand | what | exit |
|---|---|---|
| `look --box B --card N [--extra DIR]` | no device: the box's boot time (`/proc/stat` btime) against the newest record of that card | 0 CONTINUITY, 17 NEEDS-READ, 16 NO-RECORD, 16 STOPPED (a read of this boot did not end EQUAL) |
| `read --box B --card N --out DIR [--extra DIR] [--both-nodes-ok]` | only on NEEDS-READ: `et-who --check` must read free (exit 0), then the card's lock `/run/lock/etsoc-shire<N>.lock` is taken non-blocking, then **one call, exactly** `timeout 10 /opt/et/bin/dev_mngt_service -m DM_CMD_GET_MODULE_FIRMWARE_REVISIONS -n <N> -u 5000 < /dev/null`, in a scratch working directory under DIR; the answer is parsed and compared with the newest committed record | 0 EQUAL (a dated record written in DIR), 16 DIFFERENT or UNREADABLE, 16 a read of this boot already ended otherwise (nothing sent), 17 held, or a busy or missing lock (nothing sent), 0 CONTINUITY (nothing sent) |
| `guard --box B --card N [--extra DIR]` | at launch, in k6's words: `identity: ... ok` or `IDENTITY-STOP: ... nothing launched`, from the committed records and any EQUAL record a read wrote today, on this boot, in an `--extra` DIR; always IDENTITY-STOP while the ledger or an `--extra` DIR holds a read of this boot that did not end EQUAL | 0 or 16 |
| `parse FILE [--section N]` | desk: the seven fields of a saved answer | 0 or 16 |
| `check-records` | desk: every record against its committed source | 0 or 16 |

10 is a refusal before anything: a usage error, a `--box` that is not this host, aifoundry1 without `--both-nodes-ok`, a
desk-test setting outside a desk test or a desk test without every stand-in, or a ledger that cannot be written.

- **It never sends any other command, and never retries on a boot.** The only programs it runs are `et-who --check` and
  that one call. Before the call it writes the attempt to the **ledger**, `<home>/.local/state/fwgate/<box>-c<card>.jsonl`
  (the home directory from the user database, never `$HOME`): one JSON line SENT before the call and one END with the
  verdict after it, each with the boot id (`/proc/sys/kernel/random/boot_id`) and the boot time; then the attempt's record
  with the verdict SENT in DIR. Once a read of a card has not ended EQUAL on a boot, even one cut off midway, every later
  `read` of that card on that boot refuses (16), whatever its DIR, and `look` and `guard` refuse (16) too; they also refuse
  while an `--extra` DIR holds such a read of this boot, or a record that cannot be read. Only this boot's ledger lines
  count, so a reboot starts afresh; a ledger line that cannot be read stops every read (fail closed). The ledger lives
  outside the repository and outside DIR, per user and per box, so a stop carries across a kit's folders and re-runs (it
  is not shared with another user's account on the box). A person who has read a stopped attempt moves its files out of
  DIR and the ledger file aside (renamed with the date); fwgate never clears a stop, and an agent does not either. A read
  that ended EQUAL stops nothing: a read into a folder that holds this boot's EQUAL read (or with it as `--extra`) finds
  the identity carried and sends nothing, and a kit with a new folder on the same boot reads once more.
- **The card's lock.** fwgate opens the lab's own lock file and never makes one: when it is missing, `read` refuses and
  sends nothing (17), as the lab's kits refuse to start without it. Earlier attempts are judged again holding the lock, so
  a second read while one is in flight finds the lock held and is told to call again (17); a SENT found while holding the
  lock is a read cut off midway, and stops (16).
- **A busy node is a stop, not a retry.** A card's management node opens for one process at a time, and a box's live collector
  can hold it for a few milliseconds a second. A read that meets it gets no `Service request succeeded` and ends UNREADABLE
  (16). A person who has read that attempt's files may move them out of DIR and the ledger file aside, which allows one
  more read on that boot.
- **The parse** (desk-tested on the committed answers of E69's two statements, E72, E79, E82, E84 and E114): colour codes
  stripped; each of the seven labels (`Firmware release revision`, `BL1 Firmware versions`, `BL2 Firmware versions`,
  `PMIC Firmware versions`, `Master Minion Firmware versions`, `Worker Minion versions`, `Machine Minion versions`) on
  exactly one line, at its start or after the logger's `]: `, its three numbers ending the line; `Service request succeeded`
  exactly once; a `command:` line, when printed, naming the query and code 14 alone; rc 0. A runtime line between the
  answer's lines changes nothing (E191's lesson, a runtime print inside a host's output); one spliced into a field's line, a
  label twice, a missing success line or another command make the answer UNREADABLE (16). So do a line of digits alone and
  a line `Opening device <d>` followed by digits alone: a print that begins with a newline, spliced into a field's last
  number, leaves the number's tail there, and the field would otherwise read short (`0.25.12` as `0.25.1`). Desk-checked
  over every splice position of E72's and E82's answers and of two answers with an extended last number, in five print
  forms (36,600 parses): where the revised parse reads values they are the first version's and never wrong; it turns 586
  positions UNREADABLE that the first version read: 6 are the short values the first version returned, and 580 are stops
  where it read right (567 from prints that begin with a newline, 13 from E191's own form splitting a number that is no
  field's, such as the command's code 14): a stop, never a wrong value.
- **All seven fields are compared.** When the PMIC read fails inside the firmware, the handler still answers success with
  the PMIC field holding the Machine Minion's version (et-platform `836a4ab`, `services/firmware_update.c:896-908`); that
  compares DIFFERENT, so the gate fails closed.
- **The record it writes** (`fwgate-<box>-c<N>-<YYYYmmdd-HHMMSS>.json`, schema `fwgate-read/1`, beside the raw `.stdout` and
  `.stderr`): the argv, the lock(s), et-who's exit, the boot and read times, the CLI's sha256, the seven fields, the verdict
  per field, the committed record it was compared with (file and sha256), and anything the tool left in its working
  directory (it may extract the SP trace there on a trace-full event). A kit commits DIR with its data after its own
  public-text scan; a later round may add an EQUAL record to `records/` by path and sha256.
- **aifoundry1:** the vendor CLI opens both cards' management nodes even with `-n` (E82, E84 and E114 held both locks), so
  a read of one card opens the other card's node too. `read` refuses there unless `--both-nodes-ok` is passed, which needs
  the owner's word for that read; with it, both cards' locks are held. aifoundry1 had been up since 2026-10-26 15:02:04 PDT
  when the round last looked that day (10:06 PST), before every record of its cards, so no read was needed there.
- **aifoundry3** runs a non-public build that reports the same versions as aifoundry2's and has changed behaviour under
  unchanged versions: fwgate prints that caveat; an EQUAL there shows the reported versions only. k6 never gated aifoundry3;
  whether a kit does is its own registration's choice.
- **Desk tests** set `FWGATE_DESK_TEST=1` and every stand-in: `FWGATE_CLI`, `FWGATE_ETWHO`, `FWGATE_LOCKDIR` and
  `FWGATE_LEDGER_DIR` are required, none may be a real path (the vendor CLI, `et-who`, `/run/lock`, the real ledger folder,
  by real path or inode), and neither program may carry a lab tool's name (the process names THE QUIET DESK FLAG keeps off
  a box during a card session, `et-who`, `et-holders`); `FWGATE_HOSTNAME`, `FWGATE_BOOT_EPOCH`, `FWGATE_BOOT_ID` and
  `FWGATE_NOW_EPOCH` may stand in. fwgate refuses those settings without `FWGATE_DESK_TEST=1`, refuses a desk test without
  every stand-in (it never falls back to the real tools), and refuses one wherever a card node (`/dev/et*_mgmt`,
  `/dev/et*_ops`) exists.

## The records of record (`records/`)

Each is a committed read of one card, named by repo path and sha256, version numbers only (`check-records` re-reads every
one from its source):

| record | box, card | read | source | release / BL1 / BL2 / PMIC / minions |
|---|---|---|---|---|
| `aifoundry2-c0-2026-10-27-e69.json` | aifoundry2, 0 | E69, 2026-10-27 13:56:26 PDT (k6's) | two committed statements that agree: `tools/claims-v3/knob/CHANGE-RECORD.md:67-69`, `docs/reports/data/2026-10-27-e69-governor-knob/README.md:209-210` (no raw answer was committed) | 1.4.0 / 0.22.0 / 0.22.0 / 1.5.0 / 0.25.1 |
| `aifoundry2-c0-2026-10-27-e72.json` | aifoundry2, 0 | E72, 2026-10-27 14:59:39 PDT | `docs/reports/data/2026-10-27-e72-600mhz/gov.jsonl`, line 2 | the same |
| `aifoundry1-c1-2026-10-31-e82.json` | aifoundry1, 1 | E82, 2026-10-31 13:45:24 PDT (k6's, for the box) | `docs/reports/data/2026-10-31-e82-kinds-aifoundry1/ident/firmware_pre.txt` | 1.4.0 / 0.22.0 / 0.22.0 / 1.3.0 / 0.25.1 |
| `aifoundry1-c0-2026-10-31-e84.json` | aifoundry1, 0 | E84, 2026-10-31 15:42:00 PDT | `docs/reports/data/2026-10-31-e84-speed-aifoundry1-card0/ident/ident-154200.out` | 1.4.0 / 0.22.0 / 0.22.0 / 1.6.1 / 0.25.1 |
| `aifoundry1-c0-2026-11-01-e114.json` | aifoundry1, 0 | E114, 2026-11-01 14:18:10 PST | `docs/reports/data/2026-11-01-e114-card0-replicates/ident/ident-141810.out` | the same |
| `aifoundry3-c0-2026-10-31-e79.json` | aifoundry3, 0 | E79, 2026-10-31 09:27:22 PDT | `docs/reports/data/2026-10-31-e79-fp16-int8-bit-prices/ident/firmware.txt`, the first of its five answers | 1.4.0 / 0.22.0 / 0.22.0 / 1.5.0 / 0.25.1 |

The newest record of a card by read time (not by file name) is the reference. A transcribed record's seven values are each
tied to their field in its statements: the first version number after the field's word (`release`, `BL1`, `BL2`, `PMIC`,
`Master` / `Worker` / `Machine` or `minion`) is the record's value. E194's read of aifoundry2 card 0 on 15 Nov (Q187, EQUAL to
E69's record) landed on GitHub's main in `15cb0fcb` while these files were revised; it is not among these records: a later
round adds it by path and sha256 after its own check. Until then aifoundry2 reads NEEDS-READ against E72's record, and a kit
there reads once more.

## How a kit opts in

From the kit's tree on the box, never instead of a gate its registration names:

```
python3 tools/claims-v3/fwgate/fwgate.py look  --box "$(hostname -s)" --card 0                       # 0, or 17: read
python3 tools/claims-v3/fwgate/fwgate.py read  --box "$(hostname -s)" --card 0 --out "$DATA/fwgate"   # only after 17
python3 tools/claims-v3/fwgate/fwgate.py guard --box "$(hostname -s)" --card 0 --extra "$DATA/fwgate" # at launch: 0 or 16
```

and lists fwgate in its device-command audit: `python3 tools/claims-v3/dmcmd_audit_v2.py <its files>
tools/claims-v3/fwgate/fwgate.py` reads GO with no allow-list (the query READ, pmic read); `--deny-pmic-read` refuses it, as it
refuses the voltage reads; v1's `dmcmd_audit.py` still reads it NO-GO, as it should for the kits that pin v1. On a card the
tool reports a host latency of about 6 ms and a device latency of about 5 ms (E82's committed answer); the read's record goes
in "Device commands sent" with the owner's words and the table's id 14 line.

## Device commands sent

None in this round. fwgate sends one command, `DM_CMD_GET_MODULE_FIRMWARE_REVISIONS` (READ in v2), one query a read, only
on a boot later than the card's newest record, and never again on that boot once a read of the card has not ended EQUAL;
nothing else.

## Tests

`tests/test_fwgate.py` (stdlib; `python3 tools/claims-v3/fwgate/tests/test_fwgate.py -v`): the parse on the committed answers
and its failure shapes, a number split by a print at every position, the records' order and their ties to their sources;
look and guard on every box's records; the read end to end with the stand-ins `tests/fwcli-standin` (for the vendor CLI: it
logs its argv, working directory, standard input and which locks it could take, and can wait so that two reads overlap) and
`tests/etwho-standin`; the ledger's stop across folders and boots, a desk test without every stand-in, a missing lock file
and two reads at once. The read tests are skipped where a card node exists; on aifoundry2 they ran under bubblewrap with a
private `/dev` and an empty `/run/lock`: 48 of 48 OK ([`logs/test-fwgate.txt`](logs/test-fwgate.txt)). The audit tests
(`../test_dmcmd_audit_v2.py`: 36 of 36 OK, and v1's 55 of 55 unchanged,
[`logs/test-dmcmd-audit-v2.txt`](logs/test-dmcmd-audit-v2.txt)) check that fwgate reads GO under v2 and NO-GO under v1
([`logs/dmcmd-audit-fwgate.txt`](logs/dmcmd-audit-fwgate.txt)). [`logs/check-records.txt`](logs/check-records.txt): the six
records re-read from their sources, all OK. [`logs/table-v2.txt`](logs/table-v2.txt): the generator reproduces the committed
v2 (MATCH), and ids 14 and 71 read READ. [`logs/whole-tree-v1-v2.txt`](logs/whole-tree-v1-v2.txt): v1 and v2 over the 3,509
code files under `tools/`, `scripts/` and `workloads/` at GitHub main `b7af9be5` with these files, each file alone: 3,497
give the same records; 10 differ only in the class, pmic and verdict of their firmware-revisions query sites, and five of
those turn GO (`e114/run_e114.sh`, `hlp/run_e79.sh`, `kspeed/e84/run_e84.sh`, and fwgate's own `fwgate.py` and its tests);
the other 2 are v2's own audit and tests, which v2 skips and v1 reads; nothing else changes.

SPDX-License-Identifier: Apache-2.0
