# E194: the firmware read on aifoundry2 card 0 after its 13 Nov boot, Sun 15 Nov 2026 - EQUAL to E69's read of record in all seven fields

*Sun 15 Nov 2026 (week 46), PST, round Q187's lane `fwread-e194`, on aifoundry2 itself. One `DM_CMD_GET_MODULE_FIRMWARE_REVISIONS`
query to aifoundry2 card 0 at **15:22:02 PST**, nothing else sent to the card, compared field by field with E69's read of record
(Tue 27 Oct 2026 13:56:26 PDT). **Every field is EQUAL:** release 1.4.0, BL1 0.22.0, BL2 0.22.0, PMIC 1.5.0, Master, Worker and Machine
Minion 0.25.1. About 0.03 s of card time. No post: the owner waived it (his words, Sun 15 Nov 2026 10:22:36 PST: "don't worry about
discord post, just use the machines, nobody is using them").*

**Labels.** The read and every host line here are **measured** (the files in this directory). E69's values are **the record**: the two
statements of them in the repo (below), since E69's raw output was never committed. The comparison is a **desk check of code**
(`compare_fwread.py`, run under `/usr/bin/python3` 3.12.3 on aifoundry2), with two negative controls run on altered copies of the output:
one field changed reads DIFFERENT (exit 1), one line removed reads PARSE-FAILED (exit 2). Nothing here is registered and nothing is post hoc.

## Why

- **aifoundry2 booted at 2026-11-13 16:53:28 PST** (`uptime -s`), after it went down abruptly that Friday afternoon; its kernel now
  reads 7.0.0-43 (E69's change record names 7.0.0-38). That boot is **after** E69's firmware read of 27 Oct 13:56:26 PDT.
- k6's session guard ([`rb_common.sh`](../../../../tools/claims-v3/q141k-runbook/k6/rb_common.sh) lines 271-282) carries a card's
  firmware identity by continuity: on aifoundry2 it keys the identity to `FWREAD='2026-10-27 13:56:26 PDT'`,
  `FWWHO="E69's firmware read"`, and refuses any session on a host booted at or after that read (`IDENTITY-STOP`). E194's kit
  (ported from E191's; it lands separately) inherits the gate, so E194 could not run on aifoundry2 until the identity was answered.
- Until his ruling below, the lab treated this query as a write (it was not to be sent), so the identity could only be carried by
  continuity, and the reboot broke the continuity. His ruling makes the query a read; this read answers the gate by evidence.

## His words (verbatim)

- **15:05:27 PST Sun 15 Nov 2026:** "yes, feel free to run it, feel free to read firmware as well". They answer the round's question of
  about 14:3x PST, which asked whether E194 may run on aifoundry2's own card after Friday's reboot (its kit refused to launch until he
  ruled that the card's firmware was still what was recorded on 27 Oct, the query then being treated as forbidden) and whether E188 should
  run.
- **15:07:01 PST Sun 15 Nov 2026:** "Firmware revisions query was a false positive. It should have never been forbidden. Reading
  operations and firmware are always allowed." They answer the round's note that the query writes the card's PMIC firmware-management
  command register (the table line below).

## What ran (measured)

The steps, in order, all on aifoundry2 (one card, `/dev/et0_mgmt` and `/dev/et0_ops`, card lock `/run/lock/etsoc-shire0.lock`):

1. The round's card booking for aifoundry2, taken at 15:22:02 PST (no other lane of ours on this card).
2. The round's quiet-desk flag for this box, written at 15:22:02 PST (no lane of ours starts a device-named process while it exists).
3. Host reads before the query ([`etiquette-before.txt`](etiquette-before.txt)): kernel 7.0.0-43-generic, booted 2026-11-13 16:53:28;
   load 0.72; the host driver `et_soc1` version string 0.20.0, srcversion `47D26A305A0428B29FB7FC4` (the same as E69's change record:
   a host-module version, not the firmware's); `ET_DEVICES` unset (the box's own environment); the stock tool
   `/opt/et/bin/dev_mngt_service` sha256 `a3d4c722d9505aa994de7ddbe93d687c4fa21c238a44cc18e6740733bf26aaee` (E69's change record:
   "begins `a3d4c722d9505aa9`", the same prefix). `who` printed no session (`uptime` said 3 users); no names are recorded.
4. At 15:22:02.874 PST: this account's device-named processes and session or queue scripts **0**; device-named processes of any account
   **0** (a count only); `et-who --check` **rc 0**, no process holding a card node or lock.
5. **The query, once** (E114's form, `tools/claims-v3/e114/run_e114.sh` line 53, with the one lock this one-card box has and the output
   kept whole):

   ```
   flock -w 60 -E 75 /run/lock/etsoc-shire0.lock timeout 10 /opt/et/bin/dev_mngt_service -m DM_CMD_GET_MODULE_FIRMWARE_REVISIONS -n 0 -u 5000 < /dev/null
   ```

   15:22:02.877 to 15:22:02.907 PST by the wall clock around the call; **rc 0**; one try (the busy-retry rule never fired). The tool
   printed everything on standard error ([`fwread.stderr`](fwread.stderr), byte for byte, with its terminal colour codes); standard output
   was empty ([`fwread.stdout`](fwread.stdout), 0 bytes). Its own lines: the command at 15:22:02.888596, "Host Latency: 6 ms", "Device
   Latency: 5101 us", "Service request succeeded" at 15:22:02.906544, the seven version lines by 15:22:02.906563.
6. At 15:22:02.911 PST `et-who --check` rc 0 again ([`etiquette-after.txt`](etiquette-after.txt)); the flag removed and the booking
   released at 15:22:02 PST.
7. A host read at 15:26:03 PST ([`kernel-log-after.txt`](kernel-log-after.txt)): the kernel log holds every line since the 13 Nov boot
   (1,357 lines; its last stamp about 2 s after the query) and **no `Error Event Detected` line**, before or after the query (E69
   counted that line in its `err_count_*.txt`).

## Device commands sent

| command | id | sent | `dmcmd_table.json`'s class (line 42) | the owner's ruling |
|---|---:|---:|---|---|
| `DM_CMD_GET_MODULE_FIRMWARE_REVISIONS` to card 0 | 14 | **1**, at 15:22:02.888596 PST | `"class": "WRITE"`, `"reaches": ["pmic"]`, `"pmic": "write"`: "Despite its name, it writes the PMIC's firmware-management command register twice (two subcommands, ACTIVE_SLOT then VERSION) and reads the answers. Nothing reaches the PMIC's configuration or its slots, but it is a PMIC command by E85 C1's standard." | **a read, allowed**: "Firmware revisions query was a false positive. It should have never been forbidden. Reading operations and firmware are always allowed." (15:07:01 PST Sun 15 Nov 2026). The table's class is the lab's earlier reading, which he calls a false positive |

Nothing else reached the card: no set, no reset, no statistics reset, no other management command, no `ettelem`, no sampler, no kernel
launch. The management node was opened once, by this one tool call, under the card's lock. This commit changes neither
[`dmcmd_table.json`](../../../../tools/claims-v3/dmcmd_table.json) nor AGENT.md's rule 2 of 2 November 2026 (which calls this query not a
read); his ruling of 15:07:01 governs the query from that time. `dmcmd_audit.py` was **not run** (it would refuse id 14 as a write).

## The raw output

The seven version lines, as [`fwread.stderr`](fwread.stderr) holds them (the log prefix shortened here to the tool's stamp):

```
2026/11/15 15:22:02 906547 ... Firmware release revision: Major: 1 Minor: 4 Revision: 0
2026/11/15 15:22:02 906548 ... BL1 Firmware versions: Major: 0 Minor: 22 Revision: 0
2026/11/15 15:22:02 906548 ... BL2 Firmware versions: Major: 0 Minor: 22 Revision: 0
2026/11/15 15:22:02 906549 ... PMIC Firmware versions: Major: 1 Minor: 5 Revision: 0
2026/11/15 15:22:02 906550 ... Master Minion Firmware versions: Major: 0 Minor: 25 Revision: 1
2026/11/15 15:22:02 906562 ... Worker Minion versions: Major: 0 Minor: 25 Revision: 1
2026/11/15 15:22:02 906563 ... Machine Minion versions: Major: 0 Minor: 25 Revision: 1
```

## The comparison: EQUAL, field by field

E69's read of record, as the repo states it twice (the two agree, and the script checks that they do):
[`tools/claims-v3/knob/CHANGE-RECORD.md`](../../../../tools/claims-v3/knob/CHANGE-RECORD.md) lines 67-69 ("Firmware identities, read
fresh 13:56:26 PDT": release 1.4.0; BL1 0.22.0; BL2 0.22.0; PMIC 1.5.0; Master / Worker / Machine Minion 0.25.1) and
[E69's data README](../2026-10-27-e69-governor-knob/README.md) lines 209-210. E69 read it through the stock `dev_mngt_service -n 0`
from an agent working over ssh; its exact argv and its raw output were not kept (E69's dated note of 1 Nov 2026).

| field | E69, Tue 27 Oct 2026 13:56:26 PDT | this read, Sun 15 Nov 2026 15:22:02 PST | verdict |
|---|---|---|---|
| Firmware release | 1.4.0 | 1.4.0 | **EQUAL** |
| BL1 | 0.22.0 | 0.22.0 | **EQUAL** |
| BL2 | 0.22.0 | 0.22.0 | **EQUAL** |
| PMIC | 1.5.0 | 1.5.0 | **EQUAL** |
| Master Minion | 0.25.1 | 0.25.1 | **EQUAL** |
| Worker Minion | 0.25.1 | 0.25.1 | **EQUAL** |
| Machine Minion | 0.25.1 | 0.25.1 | **EQUAL** |

[`comparison.txt`](comparison.txt) is the script's whole output: `VERDICT: EQUAL`, with one command line and one "Service request
succeeded" line found in the read.

## What it shows, and what it does not

- **It shows** that aifoundry2 card 0 reports, after its 13 Nov boot, the same seven firmware revisions it reported on 27 Oct: the
  identity E69 recorded holds across the boot by this evidence, not by continuity.
- **It does not show** a byte-identical image. The query reports version numbers only; no image hash or build id is read, so another build
  carrying the same numbers would read the same. The tool binary's sha256 and the host driver's srcversion are equal to E69's (host
  reads); with the seven revisions, that is the whole of the identity this read can give.
- **For E194:** this read is offered as aifoundry2 card 0's firmware read of record after its 13 Nov boot (Sun 15 Nov 2026 15:22:02 PST).
  E194's own guard is to read it through a dated amendment, verified and landed before any E194 session; that is not part of this commit.
  k6's guard is unchanged and still keys aifoundry2 to E69's read.

## Etiquette

- The card's lock was held for the one tool call (`flock -w 60`); the tool ran under `timeout 10`; `et-who` read no holder before and
  after; nothing of ours or anyone's held the card. The owner's standing waiver of the post (10:22:36 PST) stood: no claim, no release.
- The form differs from E114's in three ways, none in the command: one lock (this box has one card; E114's box has two), `flock -w 60`
  with exit 75 for a lock not taken (in place of `-n`), and the output kept whole (E114 kept a filtered copy).

## Files

| file | what |
|---|---|
| `fwread.stderr` | the tool's whole output, byte for byte (standard error; colour codes kept) |
| `fwread.stdout` | its standard output: empty |
| `fwread.meta.txt` | the call's argv, environment, wall-clock start and end (ms, and epoch seconds) and rc |
| `etiquette-before.txt` | the host reads before the query (step 3) and the step-4 line |
| `etiquette-after.txt` | `et-who --check` after the query |
| `kernel-log-after.txt` | the host kernel log after the query: its size and stamps, the count of `Error Event Detected` lines (0), the ET driver's four boot lines |
| `compare_fwread.py` | the comparison; reads only |
| `comparison.txt` | its output (exit 0) |
| `SHA256SUMS` | the sha256 of every file above |

## Reproduce

From the lab repo's top (`/usr/bin/python3` 3.12.3 here):

```
(cd docs/reports/data/2026-11-15-e194-fwread-aifoundry2 && sha256sum -c SHA256SUMS)
python3 -I docs/reports/data/2026-11-15-e194-fwread-aifoundry2/compare_fwread.py docs/reports/data/2026-11-15-e194-fwread-aifoundry2
```

The second line prints `comparison.txt` byte for byte (checked before the commit) and exits 0.
