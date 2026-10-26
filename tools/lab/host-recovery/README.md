# tools/lab/host-recovery: the lab hosts recover from a bad boot by themselves (26 October 2026)

Installed on aifoundry1, aifoundry2 and aifoundry3 on Monday 26 October 2026, 15:11 PDT, as root, at the repo owner's
request after the lab's power cut of 25–26 October: *"Make sure that you do extra work to make sure next time restart
isn't needed."* Backups, notes and an undo script are in `/root/host-recovery-20261026/` on each host
(`sudo bash /root/host-recovery-20261026/UNDO.sh` removes everything below).

| File here | Installed as | Mode | Enabled | What it does |
|---|---|---|---|---|
| `et-boot-check` | `/usr/local/sbin/et-boot-check` | 0755 root | by its timer | after each boot, checks every card's PCIe link; cold-reboots once when one trained badly (below) |
| `et-boot-check.service`, `.timer` | `/etc/systemd/system/` | 0644 root | timer enabled, all three | runs it 3 minutes after each boot |
| (written per host) | `/etc/default/et-boot-check` | 0644 root | | the cards it expects: aifoundry1 `0000:01:00.0 0000:02:00.0`, aifoundry2 and aifoundry3 `0000:02:00.0` |
| `lab-panic.conf` | `/etc/sysctl.d/60-lab-panic-reboot.conf` | 0644 root | yes, all three | `kernel.panic = 10`: a kernel panic reboots after 10 s instead of freezing (it was 0) |
| `p3-eth-nat`, `p3-eth-nat.service` | `/usr/local/sbin/p3-eth-nat`, `/etc/systemd/system/p3-eth-nat.service` | 0755 / 0644 root | **no** (below) | the camera phone's NAT out through the lab cable, saved so it survives a reboot |

## et-boot-check

A card's link is trained once per boot, and on a marginal slot the training is a lottery. aifoundry1's card 0 (root
port `00:01.0`, the top x16 slot) shows it:

| Boot | How | Card 0's link | Corrected errors at its root port |
|---|---|---|---|
| Sat 3 Oct 08:17 | | 16 GT/s x8 | 697 in 4.5 days |
| Wed 7 Oct 18:17 and 21:28 | the lab's power | 16 GT/s x8 | 26 in 3 h; 67 in 18 days |
| Mon 26 Oct 11:54 | power back after the cut | 16 GT/s x8 | **34,552 in 3 h 6 min (about 3 a second)** |
| Mon 26 Oct 15:02 | cold reboot (mode cold, type pci) | **8 GT/s x8, "downgraded"** | 0 |

Card 1 beside it trained at 16 GT/s with no errors every time, and so did aifoundry2's and aifoundry3's cards. A card
that falls off the bus is the same story: only a cold reboot brings it back
([14-card-behaviour.md](../../../docs/findings/14-card-behaviour.md)). Until now someone had to notice and ask for that
reboot. `et-boot-check` asks for it itself, at boot, where nobody's work can be lost:

1. For each card in `ET_BOOT_CHECK_CARDS`: present on the bus, bound to the `ET` driver, the driver's start finished
   this boot (`ET <pci>: added peer-to-peer DMA memory`), the link at the speed its root port targets (Link Control 2,
   so a slot capped in the BIOS is not "bad") and at full width, and at most `ET_BOOT_CHECK_ERR_MAX` (30) corrected
   errors at the root port in `ET_BOOT_CHECK_WINDOW_S` (60) seconds. A clean link logs 0–1 a minute; the 26 Oct
   flood logged about 180.
2. All good: one `ok` line.
3. A card is bad: a cold reboot (`echo cold > /sys/kernel/reboot/mode; echo pci > /sys/kernel/reboot/type;
   systemctl reboot`), but only if all of these hold, and otherwise a warning and exit status 1, so the unit shows
   as failed (`systemctl --failed`, et-lab-health's systemd line and the lab dashboard all show it):
   - the machine is in its first `ET_BOOT_CHECK_MAX_UPTIME_S` (1,200) seconds;
   - `et-who --check` says nothing is held;
   - no CI job runs (`Runner.Worker`);
   - nobody is logged in at a terminal (a logind session of class user with a TTY);
   - fewer than `ET_BOOT_CHECK_MAX_REBOOTS` (2) automatic reboots in the last 24 hours, so a slot that never trains
     clean costs at most two reboots a day and then waits for a person.

It never opens a `/dev/et*` node, never writes a PCIe register (retraining a live link hung aifoundry1 on
30 September), and never reboots a machine after its first 20 minutes. `ET_BOOT_CHECK_REBOOT=0` in
`/etc/default/et-boot-check` keeps the check and switches the reboot off.

```
et-boot-check --status     # the last runs and the automatic reboots of the last 24 h (any user)
et-boot-check --dry-run    # check now and say what it would do; changes nothing
journalctl -t et-boot-check -b
```

Tested on 26 Oct before it was installed: `--dry-run` on all three hosts said `ok` for aifoundry2's and aifoundry3's
cards and, for aifoundry1's card 0 at 8 GT/s, `bad: … link at 8.0 GT/s, below the 16.0 GT/s its root port
0000:00:01.0 targets` and `would reboot cold now`. After the cold reboots the timer's first runs read
`ok: 0000:02:00.0 (16.0 GT/s x8, 0 errors in 60 s)` on aifoundry2 (15:17, at 248 s) and on aifoundry3 (15:22, at
240 s). aifoundry1's first run is at its next boot.

Installed, sha256 (first 16 hex digits) equal to this directory on all three: `et-boot-check` 60ffccbab205b0f6,
`et-boot-check.service` a1b60ba7343d7aab, `et-boot-check.timer` 1502b00d0e5437d9, `lab-panic.conf` cf87a0d3ac4810cf,
`p3-eth-nat` 9cf34ce9544f6979, `p3-eth-nat.service` db97ad4bdb9ffd6d.

## The chipset watchdog cannot reset these boards

Tried and taken out the same afternoon, so that nobody tries it again. Ubuntu blacklists the chipset's TCO watchdog
driver (`iTCO_wdt`); loaded by hand it finds the device (`Intel PCH TCO device (Version=6, TCOBASE=0x0400)`), and
systemd armed it with a 2-minute timeout. On aifoundry3 at 15:13 systemd let go of it, a test process armed it for
10 s and exited without stopping it (`watchdog0: watchdog did not stop!`), and the machine kept running for more than
three minutes. The registers say why: the BIOS (Gigabyte Z590 AORUS MASTER, F5 on aifoundry1 and aifoundry2, F6 on
aifoundry3) routes the TCO timeout to its own SMI handler and locks that (`TCO1_CNT` = 0x1000: `TCO_LOCK` set,
`NO_REBOOT` clear; `SMI_EN` = 0x8000203b: `TCO_EN` set), so the second timeout that would reset the machine never
comes. A hung host still needs a power cycle from outside: per-machine switched outlets are the fix, on the lab's
hardware list.

## The camera phone's NAT: installed, not enabled

The phone (10.45.0.55) takes its DHCP lease on the cable from aifoundry1 or aifoundry2 (`p3-eth-dhcp.service`).
thermal-android's `tools/setup_aifoundry_lan_ssh.sh` added the NAT that lets it out through a box's Wi-Fi live on
16 October and never saved it, so the power cut dropped it. On 26 October the phone's own Wi-Fi passed its internet
check (it failed on 18 October, which is why the cable carried the stream), so the stream goes out over the phone's
Wi-Fi and does not depend on any box. Through the cable it would depend on aifoundry2, its current gateway, the box
meant for firmware work. So the unit is installed and left off. To route the phone through a box again:
`sudo systemctl enable --now p3-eth-nat` on aifoundry1 and aifoundry2 (`p3-eth-nat status` shows the rules).
