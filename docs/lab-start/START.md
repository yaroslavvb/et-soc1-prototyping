# The AI Foundry ET-SoC-1 lab: a brief for your coding agent

Version of 30 September 2026 (PDT). The current copy is `docs/lab-start/START.md` in
https://github.com/yaroslavvb/et-soc1-prototyping; if this one is more than a month old, read that one instead.

## Your setup

Your person fills these in. Ask about anything still in angle brackets.

- Your person's login on the lab machines: `<login>`
- The machine and card the lab lead (Roman) gave them: `<host>`, card `<N>`
- The card number is 0 on aifoundry2 and aifoundry3, and 1 on aifoundry1.
- Jobs to leave alone: every job that is not yours.

## Who you work for, and the limits

You work for one person, a new user of a shared lab: three x86_64 Ubuntu 24.04 machines (aifoundry1, aifoundry2,
aifoundry3) with four ET-SoC-1 PCIe cards, each with 1,088 small RISC-V cores ("minions"). Other people, CI jobs, a
demo service and queues that run for hours share the cards. A mistake on a card spoils other people's runs, and
only the lab admin can recover a hung card.

You may, without asking: run `et-who`, `loginctl list-sessions`, `uptime`, `ps`, `df`, `et-lab-health`,
`et-lab-manifest`, `dmesg` and `coredumpctl`; clone, edit, build and simulate in your person's home directory, with
`nice` and `-j4`, but not while `et-who` or the step 2 check shows someone's run on this host: wait or ask.

Ask your person first: before the first card run of each session, before any run of more than one process, and
before anything shared, such as a long detached job, a drain of a card's queue (see Traps), or any download, install
or pip package over 100 MB on aifoundry1, whose disk is nearly full and shared with the system.

Never do these; if one seems needed, stop and tell your person, who asks the lab admin:

- reset a card, or change its TDP, clocks, thresholds, power management, voltages, trace level, telemetry
  statistics (`ettelem --reset-ms`), firmware, driver or `/opt/et`;
- use sudo or root, or change any system setting;
- use any card but card `<N>` on `<host>`; never aifoundry1's card 0, which overheats;
- run `/opt/et/bin/dev_mngt_service` or `et-powertop` on aifoundry1: they open card 0 even with `-n 1`;
- `kill -9` a process that holds a card, or touch another user's processes or files;
- put a secret on an ssh command line: every user on the host can read a remote command in full with `ps`.

Leave to your person, and wait: the Tailscale login approval, GitHub pushes, logins to publishing services, posts on
the AI Foundry Discord, and anything for the lab admin.

## The four cards

| Card | Firmware | Clock | Idle | Watch for | Use it for |
|---|---|---|---|---|---|
| aifoundry2 | 1.3.1 | DVFS 600–800 MHz, above 600 only below about 68 °C, which it rarely is, so usually 600 | 31–36 W hot, 27 W cold | some traffic starves its meter; a CI runner shares it | the main card; ask before power work: comparable runs there start from a die at about 76 °C, which takes minutes of heating |
| aifoundry3 | 1.3.1 | pinned at 600 MHz (NoC 400) at every boot; no thermal step | 23.6 W at 50 °C | reaches 88 °C under load, nothing slows it; a demo service can use the card without the lock | switching power over idle, never absolute watts |
| aifoundry1 card 1 | 1.2.0 | 600 MHz always | 33–35 W | needs `ET_DEVICES=1` and `etsoc-shire1.lock`; disk 99% full; a CI runner shares the host | anything at a fixed 600 MHz |
| aifoundry1 card 0 | 1.4.1 | idles at 300 MHz | 18.6–18.8 W | overheats: 115–117 °C after 10 minutes of short tests | nothing |

Nothing on these cards limits the die temperature: aifoundry2 once ran at a 90–103 °C mean and nothing tripped.
Every host has driver 0.20.0 and RISC-V GCC 15.1 in `/opt/et`, but a different runtime build.

## The rules, with the why

1. **Use only your card, and only when it is free.** A free lock is not permission: queues release it between
   blocks. Why: two users on one card corrupt both runs, and your heat changes the next person's run.
2. **Look before every run** with `et-who --check`: exit 0 free, 1 held (your own lock included), 2 check failed.
   Never parse the sentence plain `et-who` prints. On exit 2, stop and tell your person; never run a card without
   the check. On aifoundry1 it counts both cards, so a holder on card 0 also gives exit 1: show your person the
   `et-who` output and wait. Why: each device node opens in one process at a time.
3. **Run every device-opening process under the card lock, capped at 10 s:**
   `ET_DEVICES=<N> flock -n /run/lock/etsoc-shire<N>.lock timeout 10 <cmd>`. `-n` fails at once instead of
   waiting. `ET_DEVICES` selects the card on aifoundry1 and is ignored elsewhere. Only programs built on aifoundry1
   against its `/opt/et` honour it; check with `grep -aq ET_DEVICES <binary>` before the first run there. Exit 1
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
6. **Work in your home directory.** `/tmp` is cleared at every boot, and each machine has its own `/home`.
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

**0. Agree the plan.** Confirm the setup lines with your person. They post "using `<host>`" in #community-lab on
the AI Foundry Discord.

**1. Reach the machine.** First check that `tailscale status` on your person's computer lists `<host>`. If
Tailscale is missing or the host is not listed, stop: your person accepts the lab's Tailscale invite and installs
Tailscale. If `<host>` does not resolve, use the full name `tailscale status` shows. The first ssh prints a
login.tailscale.com link and waits, so ask your person to run `ssh <login>@<host> true` in their own terminal and
approve the link. Tailscale asks again after its check period (12 hours by default): if a later ssh prints the link
again, give it to your person and wait. If the link answers 404, they sign out of login.tailscale.com, sign in and
retry. "Policy does not permit" can mean the account does not exist there yet.

Send each block below as one command, so that its `cd` and variables carry through to its last line:

```bash
ssh <login>@<host> 'bash -s' <<'EOF'
...one block from below, as written...
EOF
```

A remote command gets no `/opt/et/bin` on its PATH: keep the absolute paths below.

**1b. Give your person a Claude that lives on the machine** (recommended; skip it if they want you to work over ssh
only). It runs in tmux, survives dropped connections, and your person drives it from claude.ai/code or the Claude
app through Remote Control. Everything goes in their home directory; nothing needs sudo.

```bash
loginctl enable-linger "$(id -un)"     # else tmux dies when the last ssh login drops (it did on 23 Sep)
command -v claude >/dev/null || [ -x ~/.local/bin/claude ] || curl -fsSL https://claude.ai/install.sh | bash
grep -q 'HOME/.local/bin' ~/.bashrc || echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
tmux has-session -t claude 2>/dev/null || tmux new-session -d -s claude -c ~
```

Then hand your person these three steps, which need them at a keyboard:

1. `ssh -t <login>@<host> tmux attach -t claude`, then run `claude` once and approve the login link it prints in
   their browser; then `/exit`.
2. In the same tmux window: `cd ~ && claude remote-control --name <login>-<host>`, then detach with Ctrl-b d. Keep
   the default permission mode, which asks before risky steps: the machine and its cards are shared.
3. Open claude.ai/code (or the Claude app), pick the `<login>-<host>` session, and paste this brief into it. From
   then on that Claude runs the blocks below directly on the host, without the ssh wrapper.

To come back later: `ssh -t <login>@<host> tmux attach -t claude`. An idle Claude in tmux holds no card and may stay;
what must stop when you finish is any process that holds a card or a lock.

**2. Look.**

```bash
et-who; loginctl list-sessions; uptime
ps -eo user,etime,comm | grep -E '_host$|ettelem|queue.sh|sys_emu|it_test|dev_mngt|powertop|Runner.Worker'
et-lab-health; echo "exit $?"
cat /etc/motd
```

Any `ps` line that is not yours means someone's run or queue is active on this host: ask your person before a card
run, even when `et-who` shows the card free. `who` and `et-lab-health` miss ssh command sessions; `loginctl` shows
them. `et-lab-health` is read-only. Exit 1 means a WARN line, and aifoundry1 always has some: read them. Someone
logged in is not someone using a card; `et-who` is what counts. If it shows card `<N>` held, look again after a few
minutes, at most once a minute, or ask your person; never take another card instead. The banner (`/etc/motd`) is
older than this brief: where they differ, follow the brief.

**3. Get the code.** A clone without the reports' raw data takes about 35 MB; the full shallow clone is 380 MB.

```bash
free=$(df --output=avail -BG ~ | tail -1 | tr -dc 0-9)
[ "$free" -ge 5 ] || { echo "only ${free} GB free: stop and ask your person"; exit 1; }
git clone --depth 1 --filter=blob:none --sparse https://github.com/yaroslavvb/et-soc1-prototyping ~/et-soc1-prototyping
cd ~/et-soc1-prototyping && git sparse-checkout set --no-cone '/*' '!/docs/reports/'
```

The clone's `CLAUDE.md` and `AGENT.md` are the owner's standing instructions. Where they differ from this brief,
this brief wins. Do not commit or push to the clone, deploy pages, or run `scripts/deploy-lab*.sh`,
`scripts/check-mirror.py` or `tools/claims-v3` queues. If you run on the host, start the agent in `~`, not in the
clone, so the clone's `CLAUDE.md` does not load as your instructions.

Read `AGENT.md` §5–7, "Traps that cost time here" in `docs/findings/14-card-behaviour.md`, and
`docs/et-soc1-notes.md` before writing kernels. Start from `workloads/`, which use the runtime API and build on the
host. Skip `kernels/` and `launchers/`: they need a gp-sdk the lab machines do not have. Link programs you build
without CMake with `-Wl,-rpath,/opt/et/lib`. For Python packages, make a venv
(`python3 -m venv --system-site-packages ~/venv`); numpy is installed.

**4. Simulator smoke, no card.** It passes 3 tests in about 110 s: give it a 5-minute tool timeout, or start it
detached (rule 10). It writes its logs into the directory it runs in, so run it in a run directory.

```bash
mkdir -p ~/runs/first-hour && cd ~/runs/first-hour && nice /opt/et/bin/it_test_code_loading
```

**5. Card smoke, under 1 s.** Run it from the same directory. aifoundry1's copy honours `ET_DEVICES` (checked on
30 September); aifoundry2 and aifoundry3 ignore it.

```bash
cd ~/runs/first-hour
[ <N> = 0 ] || grep -aq ET_DEVICES /opt/et/bin/it_test_code_loading || { echo "ignores ET_DEVICES: stop"; exit 1; }
et-who --check && ET_DEVICES=<N> flock -n /run/lock/etsoc-shire<N>.lock timeout 10 /opt/et/bin/it_test_code_loading --mode=pcie
et-who
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
[ <N> = 0 ] || grep -aq ET_DEVICES build/sgemm-mine/host/sgemm_host || { echo "ignores ET_DEVICES: stop"; exit 1; }
et-lab-manifest > $R/manifest.txt; date > $R/when.txt
et-who --check && ET_DEVICES=<N> flock -n /run/lock/etsoc-shire<N>.lock timeout 10 \
  build/sgemm-mine/host/sgemm_host -n 512 --reps 3 | tee $R/out.txt
et-who
```

Expect `mismatches 0/262144`, `PASS` and about 2.4 ms per launch (aifoundry3, 18 September; host timings changed on
25 September). Host clocks are in PDT.

**8. Read telemetry safely.**

```bash
cd ~/et-soc1-prototyping
cmake -S tools/ettelem -B build/ettelem-mine -DCMAKE_PREFIX_PATH=/opt/et -Wno-dev
nice cmake --build build/ettelem-mine -j4
R=~/runs/first-hour
[ <N> = 0 ] || grep -aq ET_DEVICES build/ettelem-mine/ettelem || { echo "ignores ET_DEVICES: stop"; exit 1; }
et-who --check && ET_DEVICES=<N> flock -n /run/lock/etsoc-shire<N>.lock timeout 10 \
  build/ettelem-mine/ettelem sample --seconds 5 --every-ms 100 > $R/idle.jsonl
et-who
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
| `who` or `et-lab-health` says nobody is logged in | ssh command sessions leave no login record | `loginctl list-sessions` |
| every program dies with `std::bad_function_call` on opening the card | a killed tool left a stale reply | with your person's OK, on aifoundry2 or aifoundry3 only, drain once: `et-who --check && flock -n /run/lock/etsoc-shire0.lock timeout 10 /opt/et/bin/dev_mngt_service -m DM_CMD_GET_MODULE_POWER -n 0 -u 5000`; on aifoundry1, stop and tell your person |
| SIGSEGV (exit 139) 1.08 s in, about 1 run in 100, aifoundry3 | the runtime's logging race | rule 5; with an old binary, repeat the launch |
| every launch fails: `KernelLaunchCmIfaceMulticastFailed`, or "Perhaps the Master Minion is hanged?" | the card is wedged, often by a TensorSend or credit wait with no partner | stop; tell your person, for the lab admin. In kernels, poll `fccnb` with a bailout |
| clock or power differ between identical runs | the governor acts on temperature: above a 65 °C mean a card runs at 600 MHz; a cool, busy aifoundry2 climbs to 800 | check `mhz.minion` in every sample; start each run at the same temperature |
| watts differ between cards | idle and leakage differ | compare the run minus the idle just before it |
| readings lag the work | rails are running averages (τ about 1 s), board power updates every 133–224 ms, the die reads whole degrees | skip 2–3 s after any change |
| `took_ms` of 76 ms to 1.6 s on aifoundry2 | some on-chip traffic starves the meter | drop bursts whose median is over 60 ms |
| a host program fails while a sampler runs | both open the management node | later, not in the first hour: open the ops node only (`createPcieDeviceLayer(true, false)`) and hold one lock for both, `flock -n <lock> sh -c '...'`, each process with its own `timeout 10` |
| on aifoundry1, `dev_mngt_service` or `et-powertop` disturbs card 0 | they open both cards, even with `-n` | never run them on aifoundry1; tell your person |
| `pgrep -f` or `pkill -f` over ssh matches itself | the remote command line holds the pattern | bracket it (`'[m]y_run.sh'`); kill by PID |
| a running script breaks after an edit or scp | bash reads the file as it runs | copy to a temporary name, then `mv`; `chmod +x` after scp |
| wrong results only with many minions | the L1 is not coherent and writes back whole 64 B lines | give each hart whole lines, or use L/G ops or evicts |
| a memory pattern with no buffer "works" | it writes address 0, and nothing reports it | check every buffer on the host before launch |
| an empty kernel costs about 0.56 ms, a 4 KB copy about 0.4 ms | runtime overhead | batch the work |
| host timings differ between hosts | each host has its own runtime build | compare host timings within one host |

Kernel code that traps or hangs:

- `double` anywhere, and `fcvt.s.lu` (64-bit integer to float).
- In U-mode: `fdiv`, `fsqrt`, `frsq`, `fsin`, packed integer division, and reading the `cycle` CSR.
- Scratchpad offset 0 (start buffers 256 KB in), and a global atomic through scratchpad ID 0x7F.
- Many shires spinning on one global atomic hangs its home shire: use a credit-release barrier.
- Only hart 0 of a minion may issue tensor ops. TensorSend has one ready bit per minion: change partners only
  across a barrier. `sys_emu` catches neither.
- Erratum 1.29: nothing inserts its workaround and `sys_emu` does not model it. Simulate with `-vpurf_warn`, and
  suspect it when results are wrong only on silicon.

## Measuring so results hold

- **Pre-register.** Commit theories, numeric predictions and the decision rule before the first run. Write each
  change as a dated amendment before the data it touches. Report a failed prediction as failed.
- **Develop on one card, validate on another**, with the code frozen in between. Report development values, never
  judge them. Replicate across passes, sessions or cards, never across samples in one burst.
- **Freeze with hashes** of the code, schedules, predictions and each kernel's `.text`. Every pass runs
  `sha256sum -c` and refuses to start on any difference.
- **Run dry, then smoke (about 30 s of card time), then for real.**
- **Bring kernels up in stages:** a CPU oracle, `sys_emu` with its checkers, 1 minion, 1 shire, 32 shires. Give
  each step an expected result and a modelled time, and include negative controls that must fail.
- **Stop at the first failure**: write a STOP file that only a person removes.
- **Keep the host quiet while measuring**: no builds, `sys_emu` or other device processes.
- **Control the heat.** Start each run from the same die temperature, and compare switching power. Budget 3–8 times
  more wall-clock time than card time, for cooling.
- **Record everything in a repository**, because agent memory stays on one machine: the `et-lab-manifest` output,
  the firmware from the table above (only the lab admin changes it), the `.text` hash, the command and the PDT time.

## Leaving the lab clean

- `et-who` lists no node or lock of yours.
- `ps -u <login> -o pid,etime,cmd`: stop only the jobs you started, by the PIDs you recorded, with a plain
  `kill <pid>`; ask about any other.
- `du -sh ~/* | sort -h | tail`: delete only the builds and simulator logs you made, above all on aifoundry1; ask
  before deleting anything else.
- Copy anything worth keeping out of `/tmp`, where agents often keep scratch files.
- Log out of ssh sessions you no longer need, and close tmux sessions you started for one job: some queues wait while
  another user is logged in. The tmux session of step 1b may stay, idle.
- Your person posts "released" in #community-lab.

## When something breaks, and where to ask

- Look: `dmesg | grep ET` (refused opens, card errors, resets), `coredumpctl list`, `et-lab-health`.
- On a wedged card, an error you do not understand, or a die over 90 °C: stop. Do not retry in a loop, and never
  reset. Give your person the time (PDT), host, card, command, error text, `et-who` output and `dmesg` lines.
- Accounts, access, which card and lab policy: the lab lead. A hung card or anything needing root: the lab admin.
  #community-lab on the AI Foundry Discord is the shared place to ask; the lab lead can send an invite.
- Before reporting a problem, check the lab problems report, which lists the known ones with their status. The
  hub's improvement ladder links it: https://spacesheep.dev/@yaroslavvb/et-soc1-limits-of-observability#improve

## Read next

- The reports hub: https://spacesheep.dev/@yaroslavvb/et-soc1-limits-of-observability
- The chip, interactively: https://spacesheep.dev/@yaroslavvb/et-soc1-chip-diagram
- What each operation costs in joules: https://spacesheep.dev/@yaroslavvb/et-soc1-energy-manual
- The effect of overheating: https://spacesheep.dev/@yaroslavvb/et-soc1-effect-of-overheating
