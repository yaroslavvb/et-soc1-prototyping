# tools/lab: the shared tools we installed on the lab machines

These are the sources of the small tools and login-banner texts we put on aifoundry1, aifoundry2 and aifoundry3 at
the repo owner's request. The first set was installed on 25 September 2026 (the lab fixes, A12 "onboarding"); before
this directory existed its only copies were on the hosts. The second set (et-who's exit status, the health check,
the corrected banners) was written on 27 September and staged on each host the same evening; installing it needs
root and waits for the owner's go-ahead, so until then the hosts run the 25 September versions. None of these tools
opens a `/dev/et*` node, queries a card or changes one.

| File here | Installed as | Mode | Version | What it does |
|---|---|---|---|---|
| `et-holders` | `/usr/local/sbin/et-holders` | 0755 root | 27 Sep: idle sentence reworded (installed: 25 Sep) | lists every process that holds a `/dev/et*` node or a card lock file (`fuser` and `ps` only) |
| `et-who` | `/usr/local/bin/et-who` | 0755 root | 27 Sep: `--check` added (installed: 25 Sep) | what users run: `sudo -n et-holders`. `et-who --check` is for scripts (below) |
| `et-lab-health` | `/usr/local/bin/et-lab-health` | 0755 root | 27 Sep (rev 2; not installed yet) | a read-only health check of the host and its cards (below) |
| `et-lab-manifest` | `/usr/local/bin/et-lab-manifest` | 0755 root | 25 Sep, unchanged | prints the machine facts a measurement should record ([lab-access.md](../../docs/lab-access.md)) |
| `60-labfix-et-who` | `/etc/update-motd.d/60-labfix-et-who` | 0755 root | 25 Sep, unchanged | the login banner's live part: what `et-holders` prints |
| `motd-aifoundry1`, `-2`, `-3` | `/etc/motd` on that host | 0644 root | 27 Sep: corrected (installed: 25 Sep) | the login banner's fixed part: the machine's cards, clocks and rules |

Three more files from 25 September are one-liners, described here rather than kept as files:

- `/etc/sudoers.d/60-labfix-et-holders` lets every account run `/usr/local/sbin/et-holders` as root with no
  password and **no arguments** (`fuser` needs root to see other users' open files). `et-who` relies on it.
- `/etc/tmpfiles.d/labfix-etsoc-lock.conf` creates one advisory lock file per card at every boot, mode 0666:
  `/run/lock/etsoc-shire0.lock` (and `etsoc-shire1.lock` on aifoundry1). aifoundry3's clock guard creates the same
  path.
- `/etc/profile.d/et-soc1.sh` appends `/opt/et/bin` to PATH in login shells.

## et-who

```
et-who            # the holders, one line per open node or lock; "No process holds ..." when none; exit 0
et-who --check    # for scripts: prints only holder lines; exit 0 if nothing is held, 1 if something is, 2 if the check failed
```

Plain `et-who` behaves as on 25 September (exit 0 always), so nothing that calls it changes. Scripts should use
`et-who --check` and its exit status where the 27 September version is installed, and never parse the idle
sentence: on 27 September a starter of ours read the old sentence ("No process has an ET-SoC-1 device node open.")
as a holder and refused to start. A lock your own script holds counts as held. Callers that parse the output keep only lines that start with `/dev/et` or `lock:`
(`tools/claims-v3/lib.sh` does), and the holder-line format is unchanged.

## et-lab-health

One line per check, `OK`, `WARN` or `INFO`; exit 0 with no WARN, 1 with any. It reads sysfs, `/proc`, `dmesg`,
`dpkg`, `zpool` and unit state, never opens a card node, and takes about a quarter of a second. It reports:

- the `et_soc1` driver version (an empty version makes every ET tool refuse the cards) and whether each installed
  kernel has the module built;
- per card: the PCIe link, the driver's world-readable error counters (`err_stats`: power and thermal events give a
  WARN), the root port's corrected PCIe errors per hour, and this boot's kernel-log counts (card error events,
  refused second opens, re-enables);
- device-node modes, current holders, and aifoundry3's clock-guard marker against the boot id;
- disk and ZFS pool use (WARN at 85%), `dpkg --audit`, a pending reboot, systemd state, chrony, the CPU power
  profile, the wired link, the CI runners and who is logged in; as root, the journal's size and boots kept.

Rev 2 (27 September): a ZFS WARN now sets the exit status (rev 1 printed it from a pipeline subshell and still
exited 0).

## The banners

Each `motd-<host>` states that machine's cards, firmware and clock behaviour as of 27 September, the one-opener
rule with `et-who`, the card lock, the commands that change a card for every user, the never-`kill -9` rule with the
one-line drain, the host-program crash fix, `/tmp` being cleared at boot, `coredumpctl`, and the two lab tools. They
are the lab's text once the lab adopts them; after any change to a card, a runner or a service, update the file
here first, then the host.

## Installing a change

The hosts are the lab's machines: installing is an admin step, done with the repo owner's agreement. Copy the file
to the host as your user, check its sha256 there against this directory, save the installed file, then install it
under a temporary name and rename it into place (`install -m <mode> <file> <dest>.new && mv -f <dest>.new <dest>`),
so a script that runs the tool at that moment sees either the old or the new file. Run `et-who`, `et-who --check`
and `et-lab-health` as an unprivileged user afterwards.
