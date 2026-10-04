# tools/lab: the shared tools we installed on the lab machines

These are the sources of the small tools and login-banner texts we put on aifoundry1, aifoundry2 and aifoundry3 at
the repo owner's request. The first set was installed on 25 September 2026 (the lab fixes, A12 "onboarding"); before
this directory existed its only copies were on the hosts. The second set (et-who's `--check`, the health check, the
corrected banners), written on 27 September, was **installed on all three hosts on 28 September** (aifoundry2 07:09,
aifoundry3 07:26, aifoundry1 07:54 PDT). A read-only check at 21:03 on 28 September (`md5sum` of each installed file
over ssh, as our user) found every installed file equal to this directory, `et-lab-health` equal to its rev 2.
`et-lab-health` rev 3 and `et-reset`, written on 28 September, were installed on all three hosts on 30 September (aifoundry1 14:38, aifoundry3 14:39, aifoundry2 15:36 PDT; `et-lab-health` equal to this directory's rev 3 by `md5sum`). The third set, written on 30 September for the new users of 2 October, was installed on all three hosts the same day: `et-lab-start` (16:10), the card-usage logger `et-usage` (20:54) and banner lines that announce both (20:58). The daily timer below is still not installed. Of these tools only `et-reset` changes a card; the others never open a `/dev/et*` node, query a card or change one.

| File here | Installed as | Mode | Version | What it does |
|---|---|---|---|---|
| `et-holders` | `/usr/local/sbin/et-holders` | 0755 root | 27 Sep: idle sentence reworded (installed 28 Sep, all three) | lists every process that holds a `/dev/et*` node or a card lock file (`fuser` and `ps` only) |
| `et-who` | `/usr/local/bin/et-who` | 0755 root | 27 Sep: `--check` added (installed 28 Sep, all three) | what users run: `sudo -n et-holders`. `et-who --check` is for scripts (below) |
| `et-lab-health` | `/usr/local/bin/et-lab-health` | 0755 root | 28 Sep rev 3 (installed 30 Sep, all three) | a read-only health check of the host and its cards (below) |
| `et-reset` | `/usr/local/bin/et-reset` | **0750 root:sudo** | 28 Sep (installed 30 Sep, all three) | a checked management reset of one card, for root and the sudo group (below) |
| `et-lab-start` | `/usr/local/bin/et-lab-start` | 0755 root | installed: the 30 Sep third version (Claude Code installs by default on aifoundry1 too; installed 22:38, all three; the first at 16:10), which still calls aifoundry1's card 0 `never` (it overheats) and aifoundry2's card usable. This directory's copy is the 2 Oct fourth version (`--card N`, down cards left out, per-card verdicts; aifoundry1's card 0 usable again, aifoundry2's card never), **not installed yet** | onboarding, run by a new user as themselves: looks (cards, `et-who`, `et-usage`, people by process, disk), sets up what is missing (linger, Claude Code, a `claude` tmux session, a sparse clone), prints the Remote Control steps and the rules; `--check`, `--dry-run`; no sudo, never opens a card ([docs/lab-start/README.md](../../docs/lab-start/README.md)) |
| `et-usage/` | `/usr/local/sbin/et-usaged` (the service `et-usaged`, user `et-usage`, two capabilities), `/usr/local/bin/et-usage`, `/etc/default/et-usaged`, logs in `/var/log/et-usage/` (readable by every user) | 0755 root | 30 Sep (installed 20:54, all three; aifoundry1 with `--skip-counters 0 --skip-pci 0000:01:00.0` until 4 Oct 2026, when card 0's exclusions were removed: /etc/default/et-usaged now passes nothing) | the card-usage logger: which process of which user holds each card's nodes or lock, from when to when, by inotify and `/proc`, never opening a card; `et-usage` prints the last 24 hours, `--json` feeds the lab dashboard ([et-usage/README.md](et-usage/README.md)) |
| `et-lab-manifest` | `/usr/local/bin/et-lab-manifest` | 0755 root | 25 Sep, unchanged | prints the machine facts a measurement should record ([lab-access.md](../../docs/lab-access.md)) |
| `60-labfix-et-who` | `/etc/update-motd.d/60-labfix-et-who` | 0755 root | 25 Sep, unchanged | the login banner's live part: what `et-holders` prints |
| `motd-aifoundry1`, `-2`, `-3` | `/etc/motd` on that host | 0644 root | 30 Sep: two lines on card-use logging and `et-lab-start` (installed 20:58, all three), and aifoundry1's disk line after the cleanup (installed 22:38; the 27 Sep text otherwise). The installed banners predate 2 Oct: aifoundry1's card 0 back in service and aifoundry2's card out of service are in this directory's `motd-aifoundry1` and `motd-aifoundry2` but **not installed yet** | the login banner's fixed part: the machine's cards, clocks and rules |

Three more files from 25 September are one-liners, described here rather than kept as files (all present on the
three hosts on 28 September):

- `/etc/sudoers.d/60-labfix-et-holders` lets every account run `/usr/local/sbin/et-holders` as root with no
  password and **no arguments** (`fuser` needs root to see other users' open files). `et-who` relies on it.
- `/etc/tmpfiles.d/labfix-etsoc-lock.conf` creates one advisory lock file per card at every boot, mode 0666, owned by
  root: `/run/lock/etsoc-shire0.lock` (and `etsoc-shire1.lock` on aifoundry1). aifoundry3's clock guard creates the
  same path.
- `/etc/profile.d/et-soc1.sh` appends `/opt/et/bin` to PATH in login shells.

## et-who

```
et-who            # the holders, one line per open node or lock; "No process holds ..." when none; exit 0
et-who --check    # for scripts: prints only holder lines; exit 0 if nothing is held, 1 if something is, 2 if the check failed
```

Plain `et-who` behaves as on 25 September (exit 0 always), so nothing that calls it changes. Scripts should use
`et-who --check` and its exit status, and never parse the idle sentence: on 27 September a starter of ours read the
old sentence ("No process has an ET-SoC-1 device node open.") as a holder and refused to start. A lock your own
script holds counts as held. Callers that parse the output keep only lines that start with `/dev/et` or `lock:`
(`tools/claims-v3/lib.sh` does), and the holder-line format is unchanged.

## et-lab-health

One line per check, `OK`, `WARN` or `INFO`; exit 0 with no WARN, 1 with any. It reads sysfs, `/proc`, the kernel
log, `dpkg`, `zpool`, unit and session state, never opens a card node (strace of rev 3 on 28 September: no open of
any `/dev/et*` path; it only stats them), and takes 0.2–0.35 s. It reports:

- the `et_soc1` driver version (an empty version makes every ET tool refuse the cards) and whether each installed
  kernel (one with a `/boot/vmlinuz-<version>`) has the module built;
- per card: the PCIe link, the driver's world-readable error counters (`err_stats`: power and thermal events give a
  WARN), the root port's corrected PCIe errors per hour, and the kernel log's counts of card error events, refused
  second opens and re-enables (a reset re-enables a card);
- device-node modes, each card's lock file (missing, or not owned by root, is a WARN: in the sticky `/run/lock` a lock
  file one user created cannot be opened by anyone else's `flock`), current holders, and aifoundry3's clock-guard
  marker against the boot id;
- available memory, disk and ZFS pool use (WARN at 85%; an unhealthy pool's status sentence and last scrub), `dpkg
  --audit`, a pending reboot, systemd state with the failed units' names, chrony, the CPU power profile, the wired
  link, the CI runners, the login sessions and, with read access to the system journal, its size and boots kept.

Rev 3 (28 September; installed on all three hosts on 30 September) fixes two wrong lines of rev 2 and makes it safe to run from a timer:

- **Logins.** Rev 2 listed `who`'s users, and `who` reads utmp, which has no entry for a session without a terminal
  (a Tailscale SSH command, for one): on aifoundry3 it printed "nobody logged in" while `uptime` counted 3 users.
  Rev 3 lists logind's sessions (`loginctl list-sessions`, where `uptime`'s count comes from), one entry per user
  and state with a count, and marks "closing" sessions (logged out, processes still running, such as tmux); `who` is
  the fallback.
  Rev 2 on aifoundry3: `INFO logins nobody logged in`; rev 3: `INFO logins 3 session(s): gdm, <user> (closing), <user>`.
- **Boots kept.** Rev 2 counted every line of `journalctl --list-boots`, the `IDX BOOT ID ...` header too, so it
  reported 47 boots where 46 were listed (systemd 255 has no `--no-legend` for that listing). Rev 3 counts the lines
  whose first field is a boot index, and names the oldest boot's date.
- **The kernel log.** Read once (rev 2 ran `dmesg` three times per card). dmesg's buffer wraps on a noisy host, so
  rev 3 says how much it covers: on 28 September aifoundry1's started 235 h into a 245 h boot (its card 0's
  corrected-error messages) and aifoundry2's 49–52 h in (about 2,000 lines, mostly Wi-Fi roaming and a snap's
  AppArmor denials), so "this boot" counts were really the last 10 h and about 195 h. Where
  `dmesg` is refused (`kernel.dmesg_restrict=1`; it is 0 on all three hosts), a user who may read the journal gets
  `journalctl -k -b` instead.
- **Timer-safe.** Every command that could wait (`sudo`, `systemctl`, `loginctl`, `chronyc`, `powerprofilesctl`,
  `zpool`, `dpkg`, `df`, `modinfo`, `journalctl`, `dmesg`) runs under `timeout` with its stdin closed, so it never
  waits for a terminal or hangs; the whole check runs with no tty and an empty environment
  (`env -i PATH=/usr/bin:/bin setsid -w sh et-lab-health </dev/null`, tested on aifoundry2). A check it cannot make
  as the current user prints an `INFO ... not checked` line instead of a wrong answer (the holders if `sudo -n
  et-holders` is refused, the journal without root or the `adm` or `systemd-journal` group, an unreadable guard
  marker).

As a user who is not root, as `nobody` from the timer would be, rev 3 differs from a root run only in the journal
line (`not checked` unless the unit adds `SupplementaryGroups=systemd-journal`, as below). The kernel-log counts
work for any user on these hosts (dmesg is world-readable), and the holders line works for every account through the
sudoers rule above. A run as `nobody` itself needs root to try, and waits for the install.

### The daily timer (not installed yet; lab report U18)

A oneshot service as `nobody` and a daily timer. `SuccessExitStatus=1` because the check exits 1 whenever it
prints a WARN (aifoundry1 does every day: card 0's events, and until 30 September its 95% pool); without it the
unit would fail and leave the system "degraded". `SupplementaryGroups=systemd-journal` lets it read the system
journal for the journal line; leave it out and that line reads "not checked". Its output goes to the journal:
`journalctl -u et-lab-health`.

```
# /etc/systemd/system/et-lab-health.service
[Unit]
Description=Read-only health check of this ET-SoC-1 lab host (et-lab-health)

[Service]
Type=oneshot
User=nobody
Group=nogroup
SupplementaryGroups=systemd-journal
ExecStart=/usr/local/bin/et-lab-health
SuccessExitStatus=1
TimeoutStartSec=5min
Nice=10
IOSchedulingClass=idle

# /etc/systemd/system/et-lab-health.timer
[Unit]
Description=Run et-lab-health once a day

[Timer]
OnCalendar=daily
RandomizedDelaySec=1h
Persistent=true

[Install]
WantedBy=timers.target
```

Install, as root, after `et-lab-health` rev 3: write the two files (mode 0644), then
`systemctl daemon-reload && systemctl enable --now et-lab-health.timer`, run it once with
`systemctl start et-lab-health.service`, and check `journalctl -u et-lab-health -n 40` and that
`systemctl is-system-running` still says `running`. Roll back: `systemctl disable --now et-lab-health.timer` and
remove the two files. On aifoundry3, which has its own admin, tell that admin first.

## et-reset

```
et-reset --dry-run N   # the read-only checks, and what it would do; takes no lock, sends nothing, logs nothing
et-reset N             # reset card N (as in /dev/etN_mgmt); root or the sudo group only
```

A checked version of the management reset that recovered aifoundry2's hung Master Minion on 28 September (C27; the
sysfs reset, `soc_reset/reinitiate`, had not). In order, it:

1. validates `N` strictly (0–63, digits only, no leading zero, one argument) and finds `/dev/etN_mgmt`, `/dev/etN_ops`
   and the card's PCI address (the driver's `devnum` attribute);
2. refuses unless it runs as root or a member of the sudo group, and unless the kernel log is readable (it is how
   the reset is confirmed);
3. refuses unless `et-who --check` shows nothing held, on any card;
4. takes the lock files with `flock -n`, opened read-only and never created: on a host with several cards, **every**
   card's lock, because the stock `dev_mngt_service` opens every card's management node whatever `-n` says (on
   aifoundry1, `-n 1` also opens card 0's, C13; `-n 0` card 1's); then checks again that no process has a node open;
5. logs `card N (<pci>) reset by <user>: sending DM_CMD_RESET_ETSOC` with `logger -t et-reset` (the sudo user when run
   through sudo), and runs `timeout 10 /opt/et/bin/dev_mngt_service -m DM_CMD_RESET_ETSOC -n N -u 9000` in a new
   directory under `/tmp` (the tool saves the service processor's traces to its working directory when their buffer
   is full). The reset itself gets no reply, so stopping the tool while it waits for the card leaves nothing stale in
   the management queue (C10); its only other request, that trace read, took under a second on 28 September;
6. waits up to 60 s for the kernel log, after the moment it sent the reset, to show the driver's
   `ET <pci>: added peer-to-peer DMA memory` (the end of its re-initialisation) with both nodes back, or one of its
   failure lines (`Unable to detect the device on bus`, `PCIe re-initialization failed`, `reset cannot be done`);
7. prints the kernel lines and the link, logs the result (`done`, `FAILED` or `NOT CONFIRMED`) with `logger`, and
   exits 0 only when the re-add was seen. It suggests a short test kernel under the card's lock, since the re-add
   does not prove the Master Minion takes work.

On aifoundry3 it never touches `et-board-clock-guard.service` (its admin's), which set the card's clocks and TDP at
boot and does not re-check the card after a reset (C6): it prints a reminder to tell that admin, and to check the
clock before measuring. Agents never run it: CLAUDE.md's rule is never to reset a card yourself, but to ask the lab
admin. Because the management reset needs no root (any user can send it, C12), the 0750 root:sudo mode gives no one
a power they lack and no sudoers file is needed; opening it to every user is the lab's call.

Tested on 28 September without a reset: the argument checks, and `--dry-run` on all three hosts (aifoundry1 card 1
would take both cards' locks; card 2 there is refused as "no card 2 (cards: 0 1)"; aifoundry3 prints the guard
reminder); a copy whose `dev_mngt_service` was `/bin/true`, run by a user outside the sudo group, was refused before
any lock; the lock mechanics and the kernel-log match were checked on scratch files and on the 28 September reset's
kernel lines. The reset path itself has not run. Install (each host, as root, after the lab agrees):
`install -o root -g sudo -m 0750 tools/lab/et-reset /usr/local/bin/et-reset`; roll back by removing it.

## The banners

Each `motd-<host>` states that machine's cards, firmware and clock behaviour as of 27 September (aifoundry1's and
aifoundry2's card notes as of 2 October, not installed yet), the one-opener rule with `et-who`, the card lock, the
commands that change a card for every user, the never-`kill -9` rule with the one-line drain, the host-program crash
fix, `/tmp` being cleared at boot, `coredumpctl`, and the two lab tools. They are the lab's text once the lab adopts
them; after any change to a card, a runner or a service, update the file here first, then the host.

## Installing a change

The hosts are the lab's machines: installing is an admin step, done with the repo owner's agreement. Copy the file
to the host as your user, check its sha256 there against this directory, save the installed file, then install it
under a temporary name and rename it into place (`install -m <mode> <file> <dest>.new && mv -f <dest>.new <dest>`),
so a script that runs the tool at that moment sees either the old or the new file. Run `et-who`, `et-who --check`
and `et-lab-health` as an unprivileged user afterwards, and compare `md5sum` of each installed file with this
directory.

## Root logins and who uses the cards (2 October 2026)

- `root-notice.sh`: install as `/etc/profile.d/zz-lab-root-notice.sh` (0644 root). At an interactive root login it says
  that root is the shared login, only for creating your own account (the new-user page's step 1). Installed on
  aifoundry1 on 4 Oct 2026 (13:41 PDT); not yet on aifoundry2, nor on aifoundry3 (its admin first).
- The dashboard tells a card held by root apart: under the CI runner (`Runner.Worker` among its ancestors) it is "CI
  runner", otherwise "root (shared login)", which raises a warning; a terminal logged in as root raises one too.
- `et-usage/et-opens`: names every open of a card node, so that nothing is "unseen" (et-usage/README.md).
