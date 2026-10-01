# Set me up in the AI Foundry ET-SoC-1 lab

I am a new user of the AI Foundry ET-SoC-1 lab, and my username on the lab machines is `<login>`. Please set me up
and run a first test, following the brief below. Choose the machine and card yourself, as it says. Ask me only for
what only I can do: approving login links in my browser, a few steps at my keyboard to start a Claude on the machine,
the lab's Discord posts, and a yes before the first run on a card.

Everything below is the lab's brief for you, my coding agent.

Version of 30 September 2026 (PDT), fourth edition, revised in the evening. The current copy is `docs/lab-start/START.md` in
https://github.com/yaroslavvb/et-soc1-prototyping; if this one is more than a month old, read that one instead.

## Your person, the machine and the card

- Your person's username on the lab machines: `<login>` (ask them if this is a placeholder in angle brackets).
- `<host>` and `<N>` are the machine and card you choose in step 2. Your person does not choose them.
- Jobs to leave alone: every job that is not yours.

## Who you work for, and the limits

You work for one person, a new user of a shared lab: three x86_64 Ubuntu 24.04 machines (aifoundry1, aifoundry2,
aifoundry3) with four ET-SoC-1 PCIe cards, each with 1,088 small RISC-V cores ("minions"). Other people, CI jobs, a
demo service and queues that run for hours share the cards. A mistake on a card spoils other people's runs, and
only the lab admin can recover a hung card or host. The lab is starting to log card use: where `et-usage` is
installed, it shows who used which card when, naming users and programs, never arguments or files.

You may, without asking: run `et-who`, `et-usage`, `et-lab-start`, `uptime`, `ps`, `df`, `et-lab-health`,
`et-lab-manifest`, `dmesg` and `coredumpctl`; clone, edit, build and simulate in your person's home directory, with
`nice` and `-j4`. Builds and the simulator wait while step 2's check shows someone else's run on the machine.

Ask your person first: before the first card run of each session, before any run of more than one process, and
before anything shared, such as a long detached job, a drain of a card's queue (see Traps), or any download, install
or pip package over 1 GB on aifoundry1 (a model, a dataset, a container image), whose disk is one pool shared with
the system and filled up once (it has had room since 30 September).

Never do these; if one seems needed, stop and tell your person, who asks the lab admin:

- reset a card, retrain, re-speed or reset its PCIe link, or write its PCI or sysfs settings. Why: on 30 September
  a link retrain hung all of aifoundry1 until someone power-cycled the lab on site;
- change a card's TDP, clocks, thresholds, power management, voltages, trace level, telemetry statistics
  (`ettelem --reset-ms`), firmware, driver or `/opt/et`;
- use sudo or root, or change any system setting;
- use any card but card `<N>` on `<host>`; never aifoundry1's card 0, which overheats;
- run `/opt/et/bin/dev_mngt_service` or `et-powertop` on aifoundry1: they open card 0 even with `-n 1`;
- `kill -9` a process that holds a card, or touch another user's processes or files;
- put a secret on an ssh command line: every user on the host can read a remote command in full with `ps`.

Leave to your person, and wait: the Tailscale and Claude login approvals, GitHub pushes, logins to publishing
services, posts on the AI Foundry Discord, and anything for the lab admin.

## The four cards

| Card | Firmware | Clock | Idle | Watch for | Use it for |
|---|---|---|---|---|---|
| aifoundry2 | 1.3.1 | DVFS 600–800 MHz, above 600 only below about 68 °C, so usually 600 | 31–36 W hot, 27 W cold | some traffic starves its meter; a CI runner shares it | a first or second choice (step 2); ask before power work: comparable runs there start from a die at about 76 °C |
| aifoundry3 | 1.3.1 | pinned at 600 MHz (NoC 400) at every boot; no thermal step | 23.6 W at 50 °C; about 25 W at 55–57 °C since 25 Sep | reaches 88 °C under load, nothing slows it; a demo service can use the card without the lock | a first or second choice; switching power over idle, never absolute watts |
| aifoundry1 card 1 | 1.2.0 | 600 MHz in every sample of 25–30 Sep; not rechecked since the power cycle of 30 Sep: read `mhz.minion` | 33–35 W | needs `ET_DEVICES=1` and `etsoc-shire1.lock`; a CI runner shares the host | the third choice (step 2) |
| aifoundry1 card 0 | 1.4.1 | idles at 300 MHz | 18.6–18.8 W | overheats: 115–117 °C after 10 minutes of short tests | nothing |

Nothing on these cards limits the die temperature: aifoundry2 once ran at a 90–103 °C mean and nothing tripped.
Every host has driver 0.20.0 and RISC-V GCC 15.1 in `/opt/et`, but a different runtime build.

## The rules, with the why

1. **Use only the card you chose, and only when it is free.** A free lock is not permission: queues release it
   between blocks. Why: two users on one card corrupt both runs, and your heat changes the next person's run.
2. **Look before every run** with `et-who --check`: exit 0 free, 1 held (your own lock included), 2 check failed.
   Never parse the sentence plain `et-who` prints. On exit 2, stop and tell your person; never run a card without
   the check. On aifoundry1 it counts both cards, so a holder on card 0 also gives exit 1: show your person the
   `et-who` output and wait. Why: each device node opens in one process at a time.
3. **Run every device-opening process under the card lock, capped at 10 s:**
   `ET_DEVICES=<N> flock -n /run/lock/etsoc-shire<N>.lock timeout 10 <cmd>`. `-n` fails at once instead of
   waiting. `ET_DEVICES` selects the card on aifoundry1 and is ignored elsewhere. Only programs built on aifoundry1
   against its `/opt/et` honour it; check with `grep -aqw ET_DEVICES <binary>` before the first run there. Exit 1
   with no output means the lock was taken; exit 124 means `timeout` stopped the program at 10 s. Either way, stop
   and run `et-who`. Release the lock between sub-tests. Why: long holds block everyone. The lock is advisory, and
   aifoundry3's demo does not take it, so run `et-who` again after each run.
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
10. **Start long jobs detached**, because the hosts use Wi-Fi and a dropped ssh hangs up its command:
    `setsid nohup <cmd> > <log> 2>&1 < /dev/null & echo $!`. Stop the job by that PID. A detached job still runs
    each device-opening process under the lock and `timeout 10`.

## The first hour

Stop at the first surprise.

**1. Reach the machines.** You must run on your person's own computer, where their Tailscale is: an agent in the
cloud cannot reach the lab. Check that `tailscale status` lists aifoundry1, aifoundry2 and aifoundry3 (on a Mac the
command may be `/Applications/Tailscale.app/Contents/MacOS/Tailscale`). If Tailscale is missing or the machines are
not listed, stop: your person accepts the lab's Tailscale invite and installs Tailscale, or switches to the lab's
network (`tailscale switch`). If a name does not resolve, use the full name `tailscale status` shows.

Then log in to each machine once, with a command you run in the background so you can read its log while it waits
(here aifoundry2; the same for aifoundry1 and aifoundry3):

```bash
timeout 600 ssh -o StrictHostKeyChecking=accept-new <login>@aifoundry2 true > aifoundry2-login.log 2>&1 < /dev/null; echo "exit $?" >> aifoundry2-login.log
```

If the log shows a login.tailscale.com link, give it to your person to approve in their browser, and wait for the
exit line; exit 0 means the machine is reachable. Tailscale asks again after its check period (12 hours by
default): treat a later link the same way. If the link answers 404, your person signs out of
login.tailscale.com and signs in, and you retry. "Policy does not permit" can mean the account does not exist there
yet: leave that machine out.

Send each block below as one command, so that its `cd` and variables carry through to its last line:

```bash
ssh <login>@<host> 'bash -s' <<'EOF'
...one block from below, as written...
EOF
```

A remote command gets no `/opt/et/bin` on its PATH: keep the absolute paths below.

**2. Choose the machine and card.** You choose. On each machine that step 1 reached, run this with `timeout 60`
before the ssh; leave out a machine that does not answer, since it may be down:

```bash
hostname; et-who --check; echo "card check exit $?"
ps -eo user:32=,etime=,args= | awk -v me="$(id -un)" '$1 != me && /queue[.]sh|claims-v3|campaign[.]py|_host( |$)|ettelem|sys_emu|it_test|dev_mngt|powertop|mmbench|Runner[.]Worker/ { n++; print substr($0, 1, 200) } END { if (!n) print "no card programs of other users" }'
ps -eo uid=,user:32= | awk '$1 >= 1000 && $1 != 65534 { print $2 }' | sort | uniq -c   # people with processes here
uptime; df -h ~ | tail -1
if command -v et-usage >/dev/null; then et-usage; else echo "et-usage: not installed here"; fi
```

Where `et-lab-start` is installed, `et-lab-start --check` shows the same and changes nothing. A card is free when the
check exits 0 and the second line finds no card program of another user, even when `et-who` shows the card free.
Then:

1. Of the free cards of aifoundry2 and aifoundry3 (card 0 on each), take the one whose machine has the fewest other
   people with processes (the third line: `who` and `loginctl` miss a Claude kept in tmux); where `et-usage` is
   installed, prefer the card used less over the last 24 hours; on a tie, aifoundry3.
2. Else aifoundry1's card 1 (`ET_DEVICES=1`), if free: never its card 0.
3. Else no card is free: take the first reachable machine in the order aifoundry3, aifoundry2, aifoundry1, do only
   step 3 there (builds and the simulator wait), and look again at most once a minute. After 30 minutes, tell your
   person.
4. If step 1 reached no machine, stop: your person asks the lab lead.

Where the banner (`/etc/motd`) differs from this brief, follow the brief. Tell your person which machine and card
you chose, and why; they post "using `<host>`" in #community-lab on the AI Foundry Discord. If card `<N>` is held
later, look again after a few minutes, at most once a minute, or ask your person; do not move to another card
without their OK.

**3. Set up on `<host>`.** A Claude that lives on the machine runs in tmux, survives dropped connections, and your
person drives it from claude.ai/code or the Claude app through Remote Control, which needs a claude.ai plan. Set it
up unless your person has no plan or wants you to work over ssh only. If `et-lab-start` is installed on `<host>`,
run it: it does what is missing of this step, is safe to run again, and prints the next steps (`--no-claude` leaves
Claude out). If not, run the two blocks below, without the Claude lines if Claude is not wanted.
Everything goes in the home directory; nothing needs sudo.

```bash
loginctl enable-linger "$(id -un)"     # else tmux stops when the last ssh login drops
command -v claude >/dev/null || [ -x ~/.local/bin/claude ] || curl -fsSL https://claude.ai/install.sh | bash
grep -qs '^[^#]*PATH=.*/\.local/bin' ~/.bashrc || printf '\nexport PATH="$HOME/.local/bin:$PATH"\n' >> ~/.bashrc
export PATH="$PATH:/snap/bin"          # tmux is a snap on some hosts
tmux has-session -t =claude 2>/dev/null || tmux new-session -d -s claude -c ~
```

The code: a clone without the reports' raw data takes about 35 MB; the full shallow clone is 380 MB.

```bash
free=$(df --output=avail -BG ~ | tail -1 | tr -dc 0-9)
[ "$free" -ge 5 ] || { echo "only ${free} GB free: stop and ask your person"; exit 1; }
git clone --depth 1 --filter=blob:none --sparse https://github.com/yaroslavvb/et-soc1-prototyping ~/et-soc1-prototyping
cd ~/et-soc1-prototyping && git sparse-checkout set --no-cone '/*' '!/docs/reports/'
```

Then hand your person these steps, at their keyboard:

1. `ssh -t <login>@<host> tmux attach -t claude`, then run `claude`, approve the login link it prints in their
   browser, trust the folder, and `/exit`.
2. In the same tmux window: `cd ~ && claude remote-control --name <login>-<host>`, then detach with Ctrl-b d.
3. In claude.ai/code (or the Claude app), open the session `<login>-<host>` and paste this message, which you fill
   in: "Read ~/et-soc1-prototyping/docs/lab-start/START.md and follow it from step 4, running its blocks directly.
   My username is <login>. You are on <host>, card <N>, chosen because <reason>. Steps 1–3 are done." Keep the
   default permission mode, which asks before each command not yet allowed: your person may allow read-only and
   build commands with "don't ask again", and reads every command that names a card lock.

After the hand-off you stop; go on over ssh only if your person skips the Claude on the machine. To come back later:
`ssh -t <login>@<host> tmux attach -t claude`. If there is no session (the machines rebooted), run `et-lab-start`,
or the first block above, again, then hand-off steps 2 and 3. An idle Claude in tmux holds no card and may stay; what must
stop when you finish is any process that holds a card or a lock.

The clone's `CLAUDE.md` and `AGENT.md` are the owner's standing instructions. Where they differ from this brief,
this brief wins. Do not commit or push to the clone, deploy pages, or run `scripts/deploy-lab*.sh`,
`scripts/check-mirror.py` or `tools/claims-v3` queues. If you run on the host, start the agent in `~`, not in the
clone, so the clone's `CLAUDE.md` does not load as your instructions.

**4. Simulator smoke, no card.** It passes 3 tests in about 110 s: give it a 5-minute tool timeout, or start it
detached (rule 10). It writes its logs into the directory it runs in, so run it in a run directory.

```bash
mkdir -p ~/runs/first-hour && cd ~/runs/first-hour && nice /opt/et/bin/it_test_code_loading --mode=sysemu
```

**5. Card smoke, under 1 s.** Ask your person for a yes first. Run it from the same directory. aifoundry1's copy
honours `ET_DEVICES` (checked on 30 September); aifoundry2 and aifoundry3 ignore it.

```bash
cd ~/runs/first-hour
[ <N> = 0 ] || grep -aqw ET_DEVICES /opt/et/bin/it_test_code_loading || { echo "ignores ET_DEVICES: stop"; exit 1; }
et-who --check && ET_DEVICES=<N> flock -n /run/lock/etsoc-shire<N>.lock timeout 10 /opt/et/bin/it_test_code_loading --mode=pcie
echo "exit $?"; et-who
```

**6. Build a workload and run it in the simulator.**

```bash
cd ~/et-soc1-prototyping
cmake -S workloads/sgemm -B build/sgemm-mine -DCMAKE_PREFIX_PATH=/opt/et -Wno-dev
nice cmake --build build/sgemm-mine -j4
mkdir -p build/sgemm-mine/run
cd build/sgemm-mine/run && nice ../host/sgemm_host --sysemu -n 64 --shires 0x1 --reps 1
```

Expect `mismatches 0/4096` and `PASS` after about a minute. A warning that `CMAKE_INSTALL_LIBDIR` is unused is
harmless. The simulator checks correctness, never speed.

**7. Run it on the card, and record the run.**

```bash
cd ~/et-soc1-prototyping
R=~/runs/first-hour; mkdir -p $R
[ <N> = 0 ] || grep -aqw ET_DEVICES build/sgemm-mine/host/sgemm_host || { echo "ignores ET_DEVICES: stop"; exit 1; }
et-lab-manifest > $R/manifest.txt; date > $R/when.txt
et-who --check && ET_DEVICES=<N> flock -n /run/lock/etsoc-shire<N>.lock timeout 10 \
  build/sgemm-mine/host/sgemm_host -n 512 --reps 3 > $R/out.txt 2>&1
echo "exit $?"; cat $R/out.txt; et-who
```

Expect `mismatches 0/262144`, `PASS` and about 2.4 ms per launch (aifoundry3, 18 September; host timings changed on
25 September, and on aifoundry1 and aifoundry2 again at their reboot into a new kernel on 30 September). Host clocks
are in PDT.

**8. Read telemetry safely.**

```bash
cd ~/et-soc1-prototyping
cmake -S tools/ettelem -B build/ettelem-mine -DCMAKE_PREFIX_PATH=/opt/et -Wno-dev
nice cmake --build build/ettelem-mine -j4
R=~/runs/first-hour
[ <N> = 0 ] || grep -aqw ET_DEVICES build/ettelem-mine/ettelem || { echo "ignores ET_DEVICES: stop"; exit 1; }
et-who --check && ET_DEVICES=<N> flock -n /run/lock/etsoc-shire<N>.lock timeout 10 \
  build/ettelem-mine/ettelem sample --seconds 5 --every-ms 100 > $R/idle.jsonl
echo "exit $?"; et-who
```

Each line has `board_w`, `mhz.minion`, the die mean `temp_c.minshire[0]` and `took_ms`. An empty file is a failed
start (about 1 in 3): wait a few seconds and retry once. If the retry is empty too, stop and tell your person; never
loop or drain yourself. Use only `sample` and `config`, never `--reset-ms` or `loglevel`. The sampler and
`sgemm_host` both hold the management node, so never run them together.

**9. Finish.** Check that `et-who` lists nothing of yours, and tell your person what ran and what you saw; the
files are in `~/runs/first-hour`. They post "released" in #community-lab.

**Next.** Read two worked examples: `workloads/sparseparity/README.md` (a kernel brought up in stages, with
negative controls) and `tools/claims-v3/pcie2/README.md` (pre-registered, developed on one card, validated on
another). Copy their patterns; do not run their runners, which are written for the owner's trees.

## Traps: symptom, cause, fix

| Symptom | Cause | Fix |
|---|---|---|
| a locked command exits 1 with no output, or exits 124 | `flock -n` found the card taken; `timeout` stopped the run at 10 s | `et-who`, then wait or ask; never retry in a loop |
| "Device or resource busy" | another process holds the node | `et-who`, then wait |
| `who`, `loginctl` or `et-lab-health` shows nobody logged in, yet the machine is busy | ssh commands leave no `who` record, and a Claude kept in tmux has no login session | count people by their processes (step 2) |
| every program dies with `std::bad_function_call` on opening the card | a killed tool left a stale reply | with your person's OK, on aifoundry2 or aifoundry3 only, drain once: `et-who --check && flock -n /run/lock/etsoc-shire0.lock timeout 10 /opt/et/bin/dev_mngt_service -m DM_CMD_GET_MODULE_POWER -n 0 -u 5000`; on aifoundry1, stop and tell your person |
| SIGSEGV (exit 139) 1.08 s in, about 1 run in 100, aifoundry3 | the runtime's logging race | rule 5; with an old binary, repeat the launch |
| every launch fails: `KernelLaunchCmIfaceMulticastFailed`, or "Perhaps the Master Minion is hanged?" | the card is wedged, often by a TensorSend or credit wait with no partner | stop; tell your person, for the lab admin. In kernels, poll `fccnb` with a bailout |
| `pgrep -f` or `pkill -f` over ssh matches itself | the remote command line holds the pattern | bracket it (`'[m]y_run.sh'`); kill by PID |
| a running script breaks after an edit or scp | bash reads the file as it runs | copy to a temporary name, then `mv`; `chmod +x` after scp |
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
- Log out of ssh sessions you no longer need, and close tmux sessions you started for one job: some queues wait while
  another user is logged in. The tmux session of step 3 may stay, idle.
- Your person posts "released" in #community-lab.

## When something breaks, and where to ask

- Look: `dmesg | grep ET` (refused opens, card errors, resets), `coredumpctl list`, `et-lab-health` (read-only;
  exit 1 means a WARN line, and aifoundry1 always has some).
- On a wedged card, an error you do not understand, or a die over 90 °C: stop. Do not retry in a loop, and never
  reset a card or retrain its link. Give your person the time (PDT), host, card, command, error text, `et-who`
  output and `dmesg` lines.
- Accounts, access and lab policy: the lab lead. A hung card or anything needing root: the lab admin.
  #community-lab on the AI Foundry Discord is the shared place to ask; the lab lead can send an invite.
- Before reporting a problem, check the lab problems report, which lists the known ones with their status. The
  hub's improvement ladder links it: https://spacesheep.dev/@yaroslavvb/et-soc1-limits-of-observability#improve

## Read next

- The reports hub: https://spacesheep.dev/@yaroslavvb/et-soc1-limits-of-observability
- The chip, interactively: https://spacesheep.dev/@yaroslavvb/et-soc1-chip-diagram
- What each operation costs in joules: https://spacesheep.dev/@yaroslavvb/et-soc1-energy-manual
- The effect of overheating: https://spacesheep.dev/@yaroslavvb/et-soc1-effect-of-overheating
