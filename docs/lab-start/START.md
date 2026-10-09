# The AI Foundry ET-SoC-1 lab: a brief for the Claude on a lab machine

Your person asked you to read this and follow it: set them up in the lab and run a first test. You are running on one
of the lab's machines, as your person's own account, in a tmux session they attach to from their own computer. They
got here with the steps of https://spacesheep.dev/@yaroslavvb/aifoundry-lab-start: the lab lead let them onto the
lab's Tailscale network; they logged in as the lab's shared `root` once, only to create their account; they logged in
as that account and started you; then they pasted one line. Ask them only for what only they can do: a yes before the
first run on a card, the lab's Discord posts, and anything for the lab lead.

Version of 9 October 2026, thirteenth edition: the person creates their own account and starts Claude on the lab
machine themselves; this brief is for that Claude, which never uses ssh or root. Access (a Tailscale invite) comes from
the lab lead by direct message, never from #community-lab. aifoundry3's card and aifoundry1's card 1 run firmware 1.4.0
since the lab lead's update of 7 October. All four cards are in service: aifoundry2's again since 9 October, with a new
two-fan bracket at the card, and aifoundry1's card 0 since 2 October. The current copy is `docs/lab-start/START.md` in
https://github.com/yaroslavvb/et-soc1-prototyping; if this one is more than a month old, read that one instead.

## Where you are

Check first:

```bash
hostname; id -un; echo "$HOME"
```

You must be on aifoundry1, aifoundry2 or aifoundry3, as a normal account, not `root`. If `id -un` says `root`, stop:
tell your person to quit you, log in as their own account (step 2 of the page) and start Claude there. If `hostname`
is not one of the three, you are on your person's own computer: stop, and tell them to follow the page's steps 1 and 2,
which start Claude on a lab machine.

- `<login>` below is your person's username (`id -un`); `<host>` is this machine (`hostname`).
- `<N>` is the card you choose in step 1. Your person does not choose it.
- Jobs to leave alone: every job that is not yours.

## Who you work for, and the limits

You work for one person, a new user of a shared lab: three x86_64 Ubuntu 24.04 machines (aifoundry1, aifoundry2,
aifoundry3) with four ET-SoC-1 PCIe cards, each with 1,088 small RISC-V cores ("minions"). Other people, CI jobs, a
demo service and queues that run for hours share the cards. A mistake on a card spoils other people's runs, and
only the lab admin can recover a hung card or host. Card use is logged where `et-usage` is installed: who used which
card when, naming users and programs, never arguments or files.

You may, without asking: run `et-who`, `et-usage`, `uptime`, `ps`, `df`, `et-lab-health`, `et-lab-manifest`, `dmesg`
and `coredumpctl`; clone, edit, build and simulate in your person's home directory, with `nice` and `-j4`. Builds and
the simulator wait while another person's card program or queue runs on the machine (one that `et-who` lists, on any
card); other people's builds, simulator runs and idle shells do not hold them up.

Ask your person first: before the first card run of each session, before any run of more than one process, and
before anything shared, such as a long detached job, a drain of a card's queue (see Traps), or any download, install
or pip package over 1 GB on aifoundry1 (a model, a dataset, a container image), whose disk is one pool shared with
the system.

Never do these; if one seems needed, stop and tell your person, who asks the lab admin:

- reset a card, retrain, re-speed or reset its PCIe link, or write its PCI or sysfs settings. Why: on 30 September
  a link retrain hung all of aifoundry1 until someone power-cycled the lab on site;
- change a card's TDP, clocks, thresholds, power management, voltages, trace level, telemetry statistics
  (`ettelem --reset-ms`), firmware, driver or `/opt/et`;
- use `sudo`, `su`, `root` or `ssh root@…`, or change any system setting. Your person used root once, to create this
  account; you never do;
- use any card but card `<N>` on this machine;
- run `/opt/et/bin/dev_mngt_service` or `et-powertop` on aifoundry1: they open both cards even with `-n`, and would
  break the run of whoever uses the other card;
- `kill -9` a process that holds a card, or touch another user's processes or files;
- put a secret on a command line: every user on the machine can read it in full with `ps`.

Leave to your person, and wait: logins (Claude, GitHub, publishing services), GitHub pushes, posts on the AI Foundry
Discord, and anything for the lab admin.

## The four cards

| Card | Firmware | Clock | Idle | Watch for | Use it for |
|---|---|---|---|---|---|
| aifoundry2 | 1.3.1 | DVFS 600–800 MHz, usually 600 | about 51 °C and 23 W since 9 Oct, when a two-fan bracket was fitted at the card | full load on every minion settles near 75 °C over 10 minutes, but nothing on the card stops a runaway: before the bracket it heated to 138 °C at idle and dropped off the PCIe bus | the card on aifoundry2 (back in service since 9 October) |
| aifoundry3 | 1.4.0 since 7 Oct (1.3.1 before) | pinned at 600 MHz (NoC 400) at every boot, seen again on 8 Oct under 1.4.0; no thermal step under 1.3.1 | 23.6 W at 50 °C; about 25 W at 55–57 °C since 25 Sep | reaches 88 °C under load, nothing slows it; a demo service can use the card without the lock | the card on aifoundry3; switching power over idle, never absolute watts |
| aifoundry1 card 1 | 1.4.0 since 7 Oct (1.2.0 before) | 600 MHz in every sample of 25–30 Sep, under 1.2.0; not rechecked since: read `mhz.minion` | 31–35 W | needs `ET_DEVICES=1` and `etsoc-shire1.lock`; a CI runner shares the host | the first choice on aifoundry1 |
| aifoundry1 card 0 | 1.4.1 | idles at 300 MHz; sgemm runs as fast as on card 1 | 19–20 W | needs `ET_DEVICES=0` and `etsoc-shire0.lock`; its fan was replaced on 2 Oct: 49 °C idle, 52–53 °C (peak 56 °C) under 8 minutes of sgemm | the second choice on aifoundry1 |

Nothing on these cards limits the die temperature: aifoundry2's card reached 138 °C at idle on 2, 7 and 8 October,
before its fan was replaced on 9 October, and nothing tripped.
The lab dashboard shows every machine, its cards, who is using them and each card's temperature, live:
https://spacesheep.dev/@yaroslavvb/aifoundry-lab-dashboard (click a machine's temperature panel for its last hour,
day and week). Every host has driver 0.20.0 and RISC-V GCC 15.1 in `/opt/et`, but a different runtime build.

## The rules, with the why

1. **Use only the card you chose, and only when it is free.** A free lock is not permission: queues release it
   between blocks. Why: two users on one card corrupt both runs, and your heat changes the next person's run.
2. **Look before every run** with `et-who --check`: exit 0 free, 1 held (your own lock included), 2 check failed.
   Never parse the sentence plain `et-who` prints. On exit 2, stop and tell your person; never run a card without
   the check. **Check only your card:** on aifoundry1, which has two cards, `et-who --check` exits 1 when anyone holds
   either card, so the blocks below look for your card's lines (`/dev/et<N>_…` or `lock:etsoc-shire<N>.lock`) in its
   output, and stop on exit 2. A holder named `ettelem` owned by `yaroslavvb` is the lab's live monitor, which reads
   each free card's temperature for about 4 ms a second and stays off a card while anyone holds its lock: check again
   a second later. Why: each device node opens in one process at a time.
3. **Run every device-opening process under the card lock, capped at 10 s:**
   `ET_DEVICES=<N> flock -n /run/lock/etsoc-shire<N>.lock timeout 10 <cmd>`. `-n` fails at once instead of
   waiting. `ET_DEVICES` selects the card on aifoundry1 and is ignored elsewhere. Only programs built on aifoundry1
   against its `/opt/et` honour it; check with `grep -aqw ET_DEVICES <binary>` before the first run there, for either
   card: a program that ignores it opens both cards and breaks the other card's user. Exit 1 with no output means the
   lock was taken; exit 124 means `timeout` stopped the program at 10 s. Either way, stop and run `et-who`. Release
   the lock between sub-tests. Why: long holds block everyone. The lock is advisory, and aifoundry3's demo does not
   take it, so run `et-who` again after each run.
4. **Stop tools with Ctrl-C, a plain `kill` or `timeout`'s default signal**, never `kill -9` or `timeout -s KILL`.
   Why: ettelem finishes the request in flight on Ctrl-C or SIGTERM, and `kill -9` never lets it; a request cut off
   mid-way leaves a stale reply, and the next program that opens the card dies. Other programs die at once either
   way, so keep each run well inside its `timeout` (sgemm stops itself at 8 s).
5. **Call `registerRuntimeLogLevels()` first in every host `main`**; copy it from any `workloads/*/host/main.cpp`.
   Why: a race in the runtime's logging crashes about 1 launch in 100 on aifoundry3. With the fix, 641 launches
   had 0 crashes where 6.4 were expected.
6. **Work in your home directory.** `/tmp` is cleared at every boot (the power cycle of 30 September cleared it on
   all three machines), and each machine has its own `/home`.
7. **Build into directories of your own**, and never rebuild, edit or copy over files a running job uses. Why: bash
   reads a script while it runs, and the job would run a binary its recorded hash does not match.
8. **Code-only work never reaches a card.** Give every script a dry mode that fails closed, run it from absolute
   paths, and check `et-who` afterwards. Why: on 25 September a code-only agent ran a real block, because a `cd` in
   a backgrounded chain did not apply.
9. **Stop any run at a 90 °C die mean.**
10. **Start long jobs detached**, so that they outlive a closed session:
    `setsid nohup <cmd> > <log> 2>&1 < /dev/null & echo $!`. Stop the job by that PID. A detached job still runs
    each device-opening process under the lock and `timeout 10`.

## The first hour

Stop at the first surprise. Run each block below as one command, so that its `cd` and variables carry through to its
last line, and keep the absolute paths.

**1. Look at this machine and choose the card.**

```bash
hostname; et-who --check; echo "card check exit $?"
for d in /sys/bus/pci/drivers/ET/0000:*; do [ -e "$d/devnum" ] && echo "card $(cat "$d/devnum"): link $(cat "$d/current_link_speed")"; done
ps -eo user:32=,etime=,args= | awk -v me="$(id -un)" '$1 != me && /queue[.]sh|claims-v3|campaign[.]py|_host( |$)|ettelem|sys_emu|it_test|dev_mngt|powertop|mmbench|Runner[.]Worker/ { n++; print substr($0, 1, 200) } END { if (!n) print "no card programs of other users" }'
ps -eo uid=,user:32= | awk '$1 >= 1000 && $1 != 65534 { print $2 }' | sort | uniq -c   # people with processes here
uptime; df -h ~ | tail -1
if command -v et-usage >/dev/null; then et-usage --since 30m; else echo "et-usage: not installed here"; fi
```

Card `<N>` of this machine is free when all of these hold:

- its link is up: the second line shows a speed for it, not `Unknown` (a card that fell off the bus keeps its
  `/dev` node, and `et-who` cannot see that it is down);
- `et-who --check` exits 0, or exits 1 with no line for card `<N>` (`/dev/et<N>_…` or `lock:etsoc-shire<N>.lock`):
  on aifoundry1 that means someone holds its other card;
- the third line shows no queue (`queue.sh`, `claims-v3`, `campaign.py`, `Runner.Worker`: a queue can take either
  card between its runs) and no other card program of another user, except those `et-who` lists on the other card,
  the shells that started them, and simulator runs (`--sysemu`, `--mode=sysemu`, `sys_emu`);
- nobody has claimed it: `et-usage --since 30m --card <N>` shows no other user on it (rows for `yaroslavvb`'s
  `ettelem` and for `?` are the lab's live monitor), and your person sees no "using `<host>` card `<N>`" post in
  #community-lab without a "released" after it.

Then, by machine:

- **aifoundry3**: card 0, if free.
- **aifoundry1**: card 1 (`ET_DEVICES=1`) if free, else card 0 (`ET_DEVICES=0`). Two people can work here at once,
  one per card.
- **aifoundry2**: card 0, if free (one card, as on aifoundry3).

Several new people may start at the same time. A card that someone holds or has claimed is theirs, even though their
runs are short. If no card here is free, do steps 2, 3 and 5 (no card) and look again at most once a minute; after 30
minutes, tell your person, who can set up on the other machine (the page's steps 1 and 2 again). Where the banner
(`/etc/motd`) differs from this brief, follow the brief. Tell your person which card you chose, and why; they post
"using `<host>` card `<N>`" in #community-lab on the AI Foundry Discord. If card `<N>` is held later, look again after
a few minutes, at most once a minute, or ask your person; do not move to another card without their OK.

**2. Get the code.** A clone without the reports' raw data takes about 35 MB; the full shallow clone is 380 MB.

```bash
free=$(df --output=avail -BG ~ | tail -1 | tr -dc 0-9)
[ "$free" -ge 5 ] || { echo "only ${free} GB free: stop and ask your person"; exit 1; }
[ -d ~/et-soc1-prototyping ] || git clone --depth 1 --filter=blob:none --sparse https://github.com/yaroslavvb/et-soc1-prototyping ~/et-soc1-prototyping
cd ~/et-soc1-prototyping && git sparse-checkout set --no-cone '/*' '!/docs/reports/'
```

The clone's `CLAUDE.md` and `AGENT.md` are the owner's standing instructions, and Claude Code loads the clone's
`CLAUDE.md` once you read a file there. Where they differ from this brief, this brief wins. Do not commit or push to
the clone, deploy pages, or run `scripts/deploy-lab*.sh`, `scripts/check-mirror.py` or `tools/claims-v3` queues.

**3. Simulator smoke, no card.** It passes 3 tests in about 110 s: give it a 5-minute tool timeout, or start it
detached (rule 10). It writes its logs into the directory it runs in, so run it in a run directory.

```bash
mkdir -p ~/runs/first-hour && cd ~/runs/first-hour && nice /opt/et/bin/it_test_code_loading --mode=sysemu
```

**4. Card smoke, under 1 s.** Ask your person for a yes first. Run it from the same directory. aifoundry1's copy
honours `ET_DEVICES` (checked on 30 September); aifoundry3's ignores it, which is fine there (one card).

```bash
cd ~/runs/first-hour
[ "$(hostname)" != aifoundry1 ] || grep -aqw ET_DEVICES /opt/et/bin/it_test_code_loading || { echo "ignores ET_DEVICES: stop"; exit 1; }
o=$(et-who --check); [ $? -le 1 ] && ! printf '%s\n' "$o" | grep -qE '^(/dev/et<N>_|lock:etsoc-shire<N>[.]lock)' || { echo "card <N> is held, or the check failed: stop"; printf '%s\n' "$o"; exit 1; }
ET_DEVICES=<N> flock -n /run/lock/etsoc-shire<N>.lock timeout 10 /opt/et/bin/it_test_code_loading --mode=pcie
echo "exit $?"; et-who
```

**5. Build a workload and run it in the simulator.**

```bash
cd ~/et-soc1-prototyping
cmake -S workloads/sgemm -B build/sgemm-mine -DCMAKE_PREFIX_PATH=/opt/et -Wno-dev
nice cmake --build build/sgemm-mine -j4
mkdir -p build/sgemm-mine/run
cd build/sgemm-mine/run && nice ../host/sgemm_host --sysemu -n 64 --shires 0x1 --reps 1
```

Expect `mismatches 0/4096` and `PASS` after about a minute. A warning that `CMAKE_INSTALL_LIBDIR` is unused is
harmless. The simulator checks correctness, never speed.

**6. Run it on the card, and record the run.**

```bash
cd ~/et-soc1-prototyping
R=~/runs/first-hour; mkdir -p $R
[ "$(hostname)" != aifoundry1 ] || grep -aqw ET_DEVICES build/sgemm-mine/host/sgemm_host || { echo "ignores ET_DEVICES: stop"; exit 1; }
et-lab-manifest > $R/manifest.txt; date > $R/when.txt
o=$(et-who --check); [ $? -le 1 ] && ! printf '%s\n' "$o" | grep -qE '^(/dev/et<N>_|lock:etsoc-shire<N>[.]lock)' || { echo "card <N> is held, or the check failed: stop"; printf '%s\n' "$o"; exit 1; }
ET_DEVICES=<N> flock -n /run/lock/etsoc-shire<N>.lock timeout 10 \
  build/sgemm-mine/host/sgemm_host -n 512 --reps 3 > $R/out.txt 2>&1
echo "exit $?"; cat $R/out.txt; et-who
```

Expect `mismatches 0/262144`, `PASS` and about 2.4 ms per launch (aifoundry3, 18 September; host timings changed on
25 September, and on aifoundry1 again at its reboot into a new kernel on 30 September). Host clocks are in PDT.

**7. Read telemetry safely.**

```bash
cd ~/et-soc1-prototyping
cmake -S tools/ettelem -B build/ettelem-mine -DCMAKE_PREFIX_PATH=/opt/et -Wno-dev
nice cmake --build build/ettelem-mine -j4
R=~/runs/first-hour
[ "$(hostname)" != aifoundry1 ] || grep -aqw ET_DEVICES build/ettelem-mine/ettelem || { echo "ignores ET_DEVICES: stop"; exit 1; }
o=$(et-who --check); [ $? -le 1 ] && ! printf '%s\n' "$o" | grep -qE '^(/dev/et<N>_|lock:etsoc-shire<N>[.]lock)' || { echo "card <N> is held, or the check failed: stop"; printf '%s\n' "$o"; exit 1; }
ET_DEVICES=<N> flock -n /run/lock/etsoc-shire<N>.lock timeout 10 \
  build/ettelem-mine/ettelem sample --seconds 5 --every-ms 100 > $R/idle.jsonl
echo "exit $?"; et-who
```

Each line has `board_w`, `mhz.minion`, the die mean `temp_c.minshire[0]` and `took_ms`. An empty file is a failed
start (about 1 in 3): wait a few seconds and retry once. If the retry is empty too, stop and tell your person; never
loop or drain yourself. Use only `sample` and `config`, never `--reset-ms` or `loglevel`. The sampler and
`sgemm_host` both hold the management node, so never run them together.

**8. Finish.** Check that `et-who` lists nothing of yours, and tell your person what ran and what you saw; the
files are in `~/runs/first-hour`. They post "released" in #community-lab. You may stay open in tmux, idle: your
person comes back with `ssh -t <login>@<host> tmux attach -t claude` from their computer.

**Next.** Read two worked examples: `workloads/sparseparity/README.md` (a kernel brought up in stages, with
negative controls) and `tools/claims-v3/pcie2/README.md` (pre-registered, developed on one card, validated on
another). Copy their patterns; do not run their runners, which are written for the owner's trees.

## Traps: symptom, cause, fix

| Symptom | Cause | Fix |
|---|---|---|
| a locked command exits 1 with no output, or exits 124 | `flock -n` found the card taken; `timeout` stopped the run at 10 s | `et-who`, then wait or ask; never retry in a loop |
| "Device or resource busy" | another process holds the node; about 1 start in 100, the lab's live monitor reading the temperature at that moment | `et-who`; if it lists nothing, retry once after a second; else wait |
| `who`, `loginctl` or `et-lab-health` shows nobody logged in, yet the machine is busy | a Claude kept in tmux has no login session | count people by their processes (step 1) |
| every program dies with `std::bad_function_call` on opening the card | a killed tool left a stale reply | with your person's OK, on aifoundry3 only, drain once: `et-who --check && flock -n /run/lock/etsoc-shire0.lock timeout 10 /opt/et/bin/dev_mngt_service -m DM_CMD_GET_MODULE_POWER -n 0 -u 5000`; on aifoundry1, stop and tell your person |
| SIGSEGV (exit 139) 1.08 s in, about 1 run in 100, aifoundry3 | the runtime's logging race | rule 5; with an old binary, repeat the launch |
| every launch fails: `KernelLaunchCmIfaceMulticastFailed`, or "Perhaps the Master Minion is hanged?" | the card is wedged, often by a TensorSend or credit wait with no partner | stop; tell your person, for the lab admin. In kernels, poll `fccnb` with a bailout |
| `pgrep -f` or `pkill -f` matches itself | the shell that runs it has the pattern on its command line | bracket it (`'[m]y_run.sh'`); kill by PID |
| a running script breaks after an edit | bash reads the file as it runs | write to a temporary name, then `mv` |
| `took_ms` of 76 ms to 1.6 s on aifoundry2 | some on-chip traffic starves the meter | drop bursts whose median is over 60 ms |

## Before kernels and measurements

Start from `workloads/`, which use the runtime API and build on the host. Skip `kernels/` and `launchers/`: they
need a gp-sdk the lab machines do not have. Link programs you build without CMake with `-Wl,-rpath,/opt/et/lib`. For
Python packages, make a venv (`python3 -m venv --system-site-packages ~/venv`); numpy is installed.

Before writing a kernel or measuring anything, read `docs/et-soc1-notes.md`, `AGENT.md` §6–7 and "Traps that cost
time here" in `docs/findings/14-card-behaviour.md`. They hold what this brief leaves out: kernel code that traps or
hangs (`double`, `fdiv` or `cycle` in U-mode, scratchpad offset 0, many shires spinning on one atomic, tensor ops
off hart 0, erratum 1.29), the non-coherent L1, a clock governor that follows temperature, telemetry that lags, and
how to measure so results hold: pre-register predictions, develop on one card and validate on another, freeze code
with hashes, bring kernels up in stages with negative controls, start each run at the same die temperature, compare
switching power over idle, keep the host quiet, and record `et-lab-manifest` with every run in a repository.

## Leaving the lab clean

- `et-who` lists no node or lock of yours.
- `ps -u <login> -o pid,etime,cmd`: stop only the jobs you started, by the PIDs you recorded, with a plain
  `kill <pid>`; ask about any other.
- `du -sh ~/* | sort -h | tail`: delete only the builds and simulator logs you made, above all on aifoundry1; ask
  before deleting anything else.
- Copy anything worth keeping out of `/tmp`, where agents often keep scratch files.
- Close tmux windows you started for one job: some queues wait while another user is logged in. The `claude`
  session may stay, idle.
- Your person posts "released" in #community-lab.

## When something breaks, and where to ask

- Look: `dmesg | grep ET` (refused opens, card errors, resets), `coredumpctl list`, `et-lab-health` (read-only;
  exit 1 means a WARN line, and aifoundry1 always has some).
- On a wedged card, an error you do not understand, or a die over 90 °C: stop. Do not retry in a loop, and never
  reset a card or retrain its link. Give your person the time (PDT), host, card, command, error text, `et-who`
  output and `dmesg` lines.
- Access and lab policy: the lab lead, by direct message on the AI Foundry Discord. Tailscale invites are never asked
  for or sent in #community-lab, the public channel. A hung card or anything needing root: the lab admin.
  #community-lab is the shared place for card claims ("using `<host>` card `<N>`", "released") and questions.
- Before reporting a problem, check the lab problems report, which lists the known ones with their status:
  https://spacesheep.dev/@yaroslavvb/aifoundry-lab-problems-for-roman

## Read next

- The lab dashboard: https://spacesheep.dev/@yaroslavvb/aifoundry-lab-dashboard
- The reports hub: https://spacesheep.dev/@yaroslavvb/et-soc1-limits-of-observability
- The chip, interactively: https://spacesheep.dev/@yaroslavvb/et-soc1-chip-diagram
- What each operation costs in joules: https://spacesheep.dev/@yaroslavvb/et-soc1-energy-manual
- The effect of overheating: https://spacesheep.dev/@yaroslavvb/et-soc1-effect-of-overheating
