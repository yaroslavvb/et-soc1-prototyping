# Lab machine accounts

The AI Foundry lab machines are x86_64 Ubuntu 24.04 boxes on the lab's Tailscale tailnet (updated 2026-09-29):

| Machine | ET-SoC-1 cards | Device nodes |
|---|---|---|
| `aifoundry1` | 2: card 0 (firmware 1.4.1; **overheats under load, do not run sustained work on it**) and card 1 (firmware 1.2.0; its clock stays at 600 MHz) | `/dev/et0_{mgmt,ops}`, `/dev/et1_{mgmt,ops}` |
| `aifoundry2` | 1 (firmware 1.3.1) | `/dev/et0_{mgmt,ops}` |
| `aifoundry3` | 1 (firmware 1.3.1; pinned at 600 MHz at every boot) | `/dev/et0_{mgmt,ops}` |

How the four cards and the three hosts differ, and what that does to measurements, is in
[findings/14-card-behaviour.md](findings/14-card-behaviour.md). The device nodes are mode 0666, so any local account
can use them and no group membership is needed. The ET tools are in `/opt/et/bin`. Each machine has its own local
`/home`, so files are not shared between machines.

There is an older standalone version of this page, with the account script built in, at
https://spacesheep.dev/@yaroslavvb/aifoundry-lab-accounts (written on 18 September; this page is the current text).

## How access works

Logins go through **Tailscale SSH**, not sshd passwords or keys. A new person needs two things: membership in the
tailnet, and an account on each machine. Ask the repo owner or the lab lead for both.

**Tailscale SSH runs in "check" mode** (2026-09-25). `ssh aifoundryN` prints a `https://login.tailscale.com/a/…`
URL and waits. Open it in a browser that is signed in to the lab tailnet as your member account, and approve it
while that `ssh` is still waiting. One approval lasts the tailnet's check period (12 hours by default), and then
Tailscale asks again. If the URL answers "Error 404 … could not be located", sign out of login.tailscale.com and sign
back in (the owner's fix, 25 September), then run `ssh` again for a fresh URL. **An AI agent cannot approve this
itself**: when a login prints the URL, it has to hand the URL to a person and wait.

## Adding someone

1. Get a username from them (lowercase, e.g. their usual handle). You can also ask for their SSH public key
   (`~/.ssh/id_ed25519.pub`). The key is optional: logins go through Tailscale SSH.
2. Make sure they are invited to the tailnet (Tailscale admin console, Users, Invite).
3. A lab admin, who has administrative access to each machine, creates the account from the repo root:

   ```bash
   scripts/add-lab-user.sh alice ~/Downloads/alice.pub "Alice Example"
   ```

   It creates the account on every `aifoundryN` listed by `tailscale status` (set `HOSTS="aifoundry2"` to limit it),
   installs the key, and checks that the account can read and write `/dev/et*`. Re-running it is safe.
4. Send them the "First login" section below.

Accounts made this way have no password, so they cannot use `sudo`. Whether anyone gets `sudo` is the lab admin's
decision.

## First login

1. Accept the Tailscale invite and install Tailscale on your laptop.
2. Run `ssh alice@aifoundry1` (or `aifoundry2`, `aifoundry3`), and approve the check URL it prints (above).
3. Read the login banner. It lists the machine's cards with their firmware and clock policy, who is using a card
   right now, and the rules below.

`/opt/et/bin` is on PATH in login shells on every machine since 25 September (`/etc/profile.d`); an older
`export PATH=/opt/et/bin:$PATH` in your `~/.bashrc` is harmless. To link against the ET libraries, use
`-Wl,-rpath,/opt/et/lib`.

If Tailscale says the policy does not permit you to log in, a tailnet admin needs to add you to the SSH rules
in the tailnet policy file. Tailscale SSH rejects a user that does not exist on the machine with the same "tailnet policy does not
permit" message it gives for a made-up name, so the account has to be created on the lab machine
first (above).

**Logging in from one lab machine to another.** On aifoundry2 the router's DNS is searched before the tailnet's, so
`ssh aifoundry1` or `ssh aifoundry3` from there goes over the LAN, not through Tailscale SSH, and fails or does not
reach the machine the way a Tailscale login does. Give each machine's full tailnet name (the MagicDNS name
that `tailscale status` shows) as its `HostName` in `~/.ssh/config` on aifoundry2 (2026-09-25).

## On every machine (since 25 September 2026)

- **`et-who`** lists who holds each card: every user's processes with a `/dev/et*` node or a card lock open. It
  never opens a device node, so it is safe to run at any time. The login banner runs it too. In a script, keep only
  the lines that start with `/dev/et` or `lock:`, and never parse the sentence plain `et-who` prints when nothing is
  held. Since 28 September (installed on all three hosts; source in [`tools/lab/`](../tools/lab/README.md)) it has
  **`et-who --check`**: it prints only the holders and exits 0 if nothing is held, 1 if a node or lock is held (your
  own lock included), 2 if the check failed. Scripts should use its exit status.
- **Card locks.** `flock /run/lock/etsoc-shire<N>.lock <command>` reserves card N for the length of the command
  (aifoundry1 has `etsoc-shire0.lock` and `etsoc-shire1.lock`, the others `etsoc-shire0.lock`). The lock is advisory:
  it protects you only from tools that take it too. The `tools/claims-v3` blocks hold it, and aifoundry3's clock
  guard and CI configuration use the same path.
- **`et-lab-manifest`** prints the machine facts a measurement should record: host, kernel, CPU, power profile,
  clock sync, `et_soc1` driver version, each card's PCIe link, the hashes of the ET runtime libraries, and
  aifoundry3's clock-guard marker. It reads files only. Save its output with every run, and the card's firmware from
  your own tool.
- **`et-lab-health`** is a read-only health check of the machine: the driver version and the module for each
  installed kernel, each card's PCIe link and the error counters the driver keeps, device-node modes, holders,
  aifoundry3's clock-guard marker, disk and ZFS use, packages, systemd, time, power profile and CI runners. One line
  per check (`OK`, `WARN`, `INFO`); exit 1 if anything warns. It never opens a card. The hosts run rev 2 (installed
  28 September). Rev 3, written on 28 September and **not installed yet**, lists logins from logind's sessions (rev 2
  missed sessions without a terminal), counts the journal's boots without the header line, and is safe to run from a
  timer; its daily timer (a oneshot service as `nobody`, once a day, output in `journalctl -u et-lab-health`) is
  written in `tools/lab/README.md` and not installed either. Installing them is an admin step that waits for the
  owner's go-ahead.
- **`et-reset`** (28 September; written and dry-tested, **not installed**) is a checked management reset of one card,
  for the lab admin: it refuses while anyone holds any card, takes every card's lock on the host, logs the reset,
  and succeeds only when the driver has re-added the card. Agents never run it: a reset is the lab admin's
  ([AGENT.md](../AGENT.md) §5).
- **`/tmp` is cleared at every boot.** Keep work, logs and agents' scratch files in your home directory.
- **Core dumps** of your programs are kept: `coredumpctl list`, then `coredumpctl gdb <pid>`.
- **Time** is kept by chrony (several NTP sources), so timestamps agree across the machines.
- **Kernel messages:** users can read `dmesg`. The journal is persistent.
- **Python:** the system `python3-numpy` (1.26.4) and `venv` are installed on all three.

The sources of `et-who`, `et-lab-health`, `et-lab-manifest`, `et-reset` and the login banners are in
[`tools/lab/`](../tools/lab/README.md), with what is installed where.

## aifoundry1's lab fixes of 28 September

At 20:51 PDT on 28 September aifoundry1 got four of the items in the lab report's section 2.8 (owner-approved lab
fixes, each logged on the host):

- **U27:** it boots to the text console (a headless default target) from its next boot; the running system is
  unchanged until then.
- **U20:** bluetooth, cups-browsed and the firmware-updater snap are disabled, and apport's core-dump hook is masked.
- **U22:** one login-service setting (the lab report has it).
- **U24:** aifoundry2 and aifoundry3 are pinned to their tailnet names in `/etc/hosts`, so from aifoundry1 they are
  reached over the tailnet (the problem aifoundry2 has, above).

The same four on aifoundry2 and aifoundry3, and the report's other items (the `et-reset` install, a pool scrub, the
daily health timer, the reboots, card 0's link test, aifoundry3's login-service item), wait for the owner
([`reports/TODO.md`](reports/TODO.md), part 0). In our own account only, the firmware notifier and wireplumber are
masked in the user service manager on all three hosts on 28 September, and the notifier's timer on aifoundry2 and
aifoundry3 (aifoundry1 has none since U20 disabled the snap); other accounts are unchanged.

## Sharing the cards

The cards are shared. The rules, each with its reason, are in [AGENT.md](../AGENT.md) §5, and
[`CLAUDE.md`](../CLAUDE.md) repeats them for agents. In short: ask before using a machine, look with `et-who` first,
never hold a device for more than 10 s, stop tools with Ctrl-C or a plain `kill` (never `kill -9`, which poisons the
card's management queue), and never reset a card yourself. Other users include CI runners on aifoundry1 and
aifoundry2 and a demo service on aifoundry3, all of which can use a card at any time.
