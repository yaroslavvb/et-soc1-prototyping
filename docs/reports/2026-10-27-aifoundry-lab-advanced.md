# Advanced: keeping your Claude up through restarts

<p data-ss-id="nav-lab-dashboard" data-ss-react="off"><a href="https://spacesheep.dev/@yaroslavvb/aifoundry-lab-dashboard">← AI Foundry lab dashboard</a> › <a href="https://spacesheep.dev/@yaroslavvb/aifoundry-lab-dashboard#worklog">Worklog</a> · <a href="https://spacesheep.dev/@yaroslavvb/aifoundry-lab-start">New user? Start here</a></p>

The lab machines restart now and then: kernel updates, power cuts, and a self-check right after boot. Step 2 of
**New user? Start here** set you up so that your Claude comes back by itself. These tips explain what comes back and
what doesn't, and what to do when something doesn't. In the commands, `<you>` is your username and `<machine>` is the
lab machine.

## 1. Your Claude is brought back every minute

**You'd see:** after a restart, your tmux session is back and Claude has picked up your last conversation.
**What does it:** a crontab line runs `~/.local/bin/lab-sessions` every minute. It starts the tmux session `claude`
when it's missing. Once you've signed in, it also keeps a Remote Control server running in `claude-rc`. It only
starts things, and only your own.
**Check:** `crontab -l | grep lab-sessions`. **Bring it back now:** `~/.local/bin/lab-sessions`.
**Why:** without it, a restart left people with no session until they redid step 2 by hand. Set up before 13 October?
Run step 2 again: it's safe to repeat.

## 2. Attach by exact name

**You'd see:** `tmux attach -t claude` drops you into a window with a server log in it, not Claude.
**Why:** tmux matches session names by prefix. If `claude` isn't back yet, `claude` matches `claude-rc`.
**Do:** `ssh -t <you>@<machine> tmux attach -t =claude`. Don't press Ctrl-C in `claude-rc`: that stops your server.

## 3. Linger keeps tmux alive when your connection drops

**You'd see:** without linger, a short network blip that ends your last login also kills tmux and every Claude in
it.
**What does it:** step 1 turned on linger for your account.
**Check:** `loginctl show-user "$USER" -p Linger` should say `Linger=yes`. If not: `loginctl enable-linger`.

## 4. What comes back is a conversation, not running work

**You'd see:** Claude is back, but a command it was running is gone.
**Why:** a restart ends every process. `lab-sessions` runs `claude --continue`, which reopens the most recent
conversation in your home folder, nothing else. `/tmp` is cleared at every boot.
**Do:** keep notes, logs and results in files under `~`. Reopen an older conversation with `claude --resume`.

## 5. Long jobs don't come back

**You'd see:** a job started with `setsid nohup` survived your logout but not the restart.
**Do:** check when the machine last booted with `uptime -s`. Write long jobs so they can resume from their own log.
Restart them yourself, under the card rules.

## 6. "Connected", yet new sessions fail

**You'd see:** the Claude app lists the machine, but a new session "didn't finish connecting".
**Two causes:** Claude Code's update cleanup deleted the build the server was started from, so it can't start new
sessions; or the server is full (32 sessions by default), which looks the same. `lab-sessions` only restarts a server
that has stopped, so it won't catch either.
**Check:** `ls -l /proc/$(pgrep -u "$(id -u)" -f '^([^ ]*/)?claude remote-control' | head -1)/exe`. "(deleted)" is the
first cause.
**Fix:** `tmux kill-session -t =claude-rc`. `lab-sessions` starts a fresh server within a minute, or within 10 minutes
if it restarted one recently.

## 7. Your sign-in runs out after about 30 days

**You'd see:** Claude asks you to sign in, and the app stops offering the machine.
**Do:** attach (tip 2) and type `/login`, in a browser signed in to your own Claude account. **Check:**
`claude auth status`. A token from `claude setup-token` can't run Remote Control, so a browser sign-in is the only way.

## 8. A restarted Claude starts in your default mode

**You'd see:** you had switched modes with Shift+Tab, and after the restart it asks for permission again.
**Why:** `lab-sessions` passes no mode, so both Claude and the server's sessions start in your settings' default.
**Do:** set `permissions.defaultMode` in `~/.claude/settings.json` to the mode you want after every restart. Keep to the
brief's rules whatever the mode.

## 9. The machine may restart itself once right after boot

**What does it:** if a card's link came up bad, the machine does one cold reboot in its first 20 minutes. It does this
only when no card is held and nobody is at a terminal, and at most twice a day. A kernel panic reboots after 10
seconds, and after a power cut the machines start by themselves.
**Check:** `et-boot-check --status` and `uptime -s`. A machine that hangs still needs a person: tell the lab admin.

## On your own machines

- Run a Remote Control server inside a loop that restarts it, plus a per-minute cron check under `flock`. Close the
  lock's descriptor (`9>&-`) on any command that can start a tmux server, or that server holds the lock for good.
- Cron's PATH is bare. Set it yourself, including `/snap/bin` where tmux is a snap.
- A tmux window inherits the tmux server's environment, not yours. With two Claude accounts, name the account on every
  command line.
- Inside a git repository, folder trust stops at the repo's own folder. A server started there waits at a trust
  prompt until you answer it once. Start it with `--spawn=same-dir`.
