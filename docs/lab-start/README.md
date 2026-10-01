# docs/lab-start: the new-user prompt, its page and et-lab-start

The owner asked on 30 September 2026 for a "New user? Start now" link on the lab dashboard, leading to
self-contained instructions that people can give their coding agents to do the setup, built from what a week of
running the lab taught us. The same evening they asked for less: "I should only have a single option: a single
prompt they should do, and also they shouldn't select which machine, just maybe type in their name", and for a
script that makes onboarding easy. New users arrive on Friday 2 October 2026. This directory holds the prompt; the
page shows it; `tools/lab/et-lab-start` is the script.

| File | What it is |
|---|---|
| `START.md` | The prompt: one self-contained markdown document that a new user pastes into a coding agent (Claude Code or similar). Its first lines are the person's own request (they are a new user, their username is `<login>`: set them up and run a first test, and ask them only for login approvals, a few keyboard steps to start a Claude on the machine, the Discord posts and a yes before the first card run); the rest is the lab's brief: who the agent works for and its limits (never reset a card or retrain its PCIe link, since the retrain of 30 September hung aifoundry1), card use being logged where `et-usage` is installed, the four cards, the rules with their reasons, the first hour (reach the machines, with the agent passing on Tailscale login links from a background ssh; **the agent chooses the machine and card** by a fixed decision list; set up, with `et-lab-start` where installed, including a Claude on the machine with Remote Control and one message that hands over to it; simulator and card smoke tests), the first-hour traps (symptom, cause, fix), a pointer to `AGENT.md` §6–7 and the findings' traps before kernels and measurements, how to leave the lab clean, where to ask. Fourth edition, about 3,800 words. |
| `make_page_data.py` | Writes `docs/reports/data/2026-09-30-lab-start/brief.json` (START.md word for word, its sha256, version and word count, the placeholders the page fills, and the page's card tiles). `--check` exits 1 if the JSON is stale. It refuses a START.md whose opening lines lack `<login>`. |
| `README.md` | This file. |

The page is `docs/reports/2026-09-30-aifoundry-lab-start.html`, built from
`docs/reports/sources/lab-start.{body.html,script.js,meta.json}`. It is short on purpose: the three things a person
does (ask Roman, the lab lead, for an account and a Tailscale invite; join Tailscale; type their username and copy
the prompt), the diagram of the three machines and four cards with one sentence saying that the lab is starting to
log card use (`et-usage` shows it where installed; it is installed on no machine yet on 30 September), and
one prompt section: one field ("Your username on the lab machines"), one "Copy the prompt" button, and START.md in a
scrollable box. The field fills only `<login>` (lowercase letters, digits, `_`, `-`, `.`, up to 32, starting with a
letter or `_`, as Ubuntu's `adduser` requires by default; `root` and other system accounts are refused, since the
prompt would send the agent in as them; anything else leaves the placeholder, with a hint, and Copy then says it
copied the prompt without the username); left blank, the agent asks. `<host>` and `<N>` stay in the text: the agent
chooses them (START.md, step 2). Copying tries the clipboard API, then a selected textarea with
`execCommand('copy')`, and failing both selects the prompt's text for Ctrl-C (the page may run in a frame that
forbids the clipboard). The page is meant to be public: new users cannot open the owner's private pages.

### How the agent chooses the machine

START.md's steps 1 and 2, in short. The agent logs in to each machine once with an ssh it runs in the background,
its output in a file, so that it can pass a Tailscale login link to the person while the ssh waits; a machine that
refuses the account, or whose ssh does not answer within `timeout 60` (it may be down, as aifoundry1 was from 14:41 to
15:07 on 30 September), is left out. On each machine reached it runs one read-only block: `et-who --check`; other
users' card programs and queues, matched on the whole command line (`ps -o comm` is cut at 15 characters, so
`sparseparity_host` shows as `sparseparity_ho`, and a queue run as `bash queue.sh` or a Python runner has comm `bash`
or `python3`); the people with processes there; `uptime`, `df`, and `et-usage` where installed. A card is free when
the check exits 0 and no other user's card program runs. Then: (1) of the free cards of aifoundry2 and aifoundry3, the
one whose machine has the fewest other people with processes, preferring the card used less over 24 hours where
`et-usage` is installed, and aifoundry3 on a tie; (2) else aifoundry1's card 1 (`ET_DEVICES=1`), if free; (3) else the
first reachable machine in the order aifoundry3, aifoundry2, aifoundry1, doing only the setup (step 3) while builds and
the simulator wait, looking at most once a minute, and telling the person after 30 minutes; (4) no machine reached:
stop, the person asks the lab lead. People are counted by their processes, not by `loginctl list-sessions` or `who`:
at 15:26 on 30 September aifoundry2 had no login session at all while two users kept Claude sessions running in tmux
under linger (29 and 10 processes). The agent tells the person which machine and why; the person posts "using
<host>" in #community-lab.

After the setup the laptop agent gives the person one message to paste into the Claude on the machine ("Read
~/et-soc1-prototyping/docs/lab-start/START.md and follow it from step 4 … You are on <host>, card <N>, chosen
because …"), and stops. That message reads START.md from the clone, so it gets this edition only once START.md is
pushed to GitHub.

## Rebuild

From the repository root:

```
python3 docs/lab-start/make_page_data.py
NODE_PATH=$PWD/node_modules python3 scripts/build-report.py lab-start \
  docs/reports/data/2026-09-30-lab-start/brief.json docs/reports/2026-09-30-aifoundry-lab-start.html
T=docs/reports/data/2026-09-24-report-review/tools
bash $T/check_page.sh docs/reports/2026-09-30-aifoundry-lab-start.html
DARK=1 bash $T/check_page.sh docs/reports/2026-09-30-aifoundry-lab-start.html
```

Edit START.md, never the JSON or the HTML. The page shows START.md as plain text (no markdown rendering), so any
markdown works. Keep the placeholder spelled exactly `<login>`, since the page fills it everywhere it appears: never
write `<login>` where the literal placeholder is meant (say "a placeholder in angle brackets" instead). `<host>` and
`<N>` are never filled by the page.

## et-lab-start

`tools/lab/et-lab-start` (bash, one file), to be installed as `/usr/local/bin/et-lab-start` (0755 root). A new user,
or their agent, runs it on a lab machine as themselves; START.md step 3 runs it where it is installed and does the
same steps by hand where it is not.

```
et-lab-start             # look, set up what is missing, print the next steps and the rules; safe to run again
et-lab-start --check     # only look; changes nothing
et-lab-start --dry-run   # look, and print what the setup would do, without doing it
--no-claude              # leave out Claude Code, its PATH line and the `claude` tmux session
--with-claude            # install Claude Code: the default everywhere since 30 Sep (kept for older instructions)
--no-clone               # leave out the clone
-h, --help
```

- **Look**: the host, the user, this machine's cards (the names of `/dev/et*_ops`, from a glob and a stat, never an
  open; built-in facts per host: aifoundry1 card 0 never, card 1 with `ET_DEVICES=1`; each card's lock path, and a
  WARN if the lock file is missing, since a lock a user creates cannot be opened by the others' `flock`),
  `et-who --check` (free, held with the holders, or failed), other users' card programs and queues in `ps` (the
  brief's pattern, on the whole command line), a verdict for the usable card (on aifoundry1, "not held itself, but
  another card here is" when only card 0 is held), `et-usage` (its default last-24-hour summary, at most 40 lines) if
  installed, how many other people have processes here (uids from 1000 up, no names) and how many of them are logged
  in (`loginctl list-sessions`; a failure is a WARN, not a zero), the load, and the free space in `~` (WARN under
  5 GB, or "unknown" when `df` fails, which leaves out the install and the clone; a note on aifoundry1's disk).
- **Set up**, each step only if missing: `loginctl enable-linger` for oneself (checked by
  `/var/lib/systemd/linger/<login>`); Claude Code by the native installer (`curl -fsSL https://claude.ai/install.sh
  | bash`, downloaded first, then run) into `~/.local/bin`, with 1 GB free, on every machine (the second version
  installed it on aifoundry1 only with `--with-claude`, while that `/home` was 99% full; the option is still
  accepted and means the default); the PATH line in `~/.bashrc` (only an uncommented assignment
  counts as present; a newline is added first if the file does not end in one); a detached tmux session `claude` in
  `~` (exact name, `=claude`; `/snap/bin` is added to PATH, where tmux is a snap); a sparse clone of the repository
  into `~/et-soc1-prototyping` with the same commands as START.md step 3, only with 5 GB free, made in
  `~/.et-soc1-prototyping.partial` under a lock (`~/.cache/et-lab-start.lock`, so two runs cannot delete each other's
  partial clone) and moved into place when complete, and skipped if the directory exists. The installer and the
  clone run under `timeout --foreground 900`, so Ctrl-C reaches them too. The checks that make the setup fail (curl,
  git, tmux, free space, an `~/.bashrc` that is not the user's) come before the mode, so `--check` and `--dry-run`
  report the same failure ("would FAIL: …") instead of a step the setup would not do.
- **Then** it prints the three Remote Control steps with the user's login and this host filled in, including the one
  message to paste into the Claude on the machine, what to do when the tmux session is gone after a reboot, the five
  rules that matter most (`et-who --check` before a run; `ET_DEVICES=<N> flock -n <lock> timeout 10 <cmd>` with this
  host's card; never aifoundry1's card 0; stop at a 90 °C die mean; never `kill -9` a card process, never reset a
  card or retrain its PCIe link), and, only where `et-usage` is installed, that card use is logged.
- **Never**: sudo itself (`et-who` uses its own fixed `sudo -n` rule), root (it refuses to run as root, with a
  relative `$HOME`, or, for the setup, with a `$HOME` other than the account's home directory), another user's
  files, an open of a `/dev/et*` node, a card program. It writes only in the home directory, apart from logind's
  linger record and tmux's socket. The whole body is one function called on the last line with stdin from
  `/dev/null`: bash has read the whole script before anything runs, so it works fed through `bash -s` or a pipe (the
  first version exited 0 there having done nothing, because its `exec </dev/null` cut off the script bash was
  reading), and inside `ssh host 'bash -s' <<EOF` nothing it runs can eat the rest of the caller's script. Run by
  `sh`, it says it needs bash and exits 2. Exit 0 on success, 1 if a setup step failed (said on stderr), 2 on a bad
  option or a refusal.

Tested on 30 September 2026 as the owner's user, with `--check` and `--dry-run` only (the real setup was not run,
so as not to touch that account's tmux sessions and Claude). The first version: both exit 0 in about 0.15 s on
aifoundry2; with an empty scratch `HOME` and a minimal PATH, `--dry-run` lists the Claude install, the PATH line and
the clone it would do; with stub `et-who`, `et-usage` and `hostname` it shows a held card with its holders,
truncates a 50-line `et-usage` at 40, and gives aifoundry1's card notes; a stub `id` reporting uid 0 is refused
(exit 2). The second version (15:45–15:55 PDT): `--check` and `--dry-run` exit 0 with the full report on all three
hosts, run as a file on aifoundry2 and fed through `ssh <host> 'bash -s -- --check' < tools/lab/et-lab-start` on
aifoundry1 and aifoundry3 (and `bash -s` and `cat | bash -s` locally); `sh`, `sh -s`, unknown options, `--check
--dry-run` and `--no-claude --with-claude` exit 2; `HOME=.` is refused, and a `HOME` other than the passwd one is a
WARN in `--check`/`--dry-run` and a refusal (exit 2) in the setup; with a stub `hostname` of aifoundry1 and an empty
scratch `HOME`, the Claude step says `ask` and the next steps say to run `--with-claude` first; stub `loginctl` and
`df` that fail give a WARN and "unknown", not zeros; fake card nodes 0 and 1 with a stub `et-who` holding card 0 give
"card 1: not held itself, but another card here is". The PATH-line step, copied into a harness, adds the line after
a last line without a newline, and does not count a commented line; the clone step, copied into a harness with a
stub `git`, lets a second run started 0.5 s later exit 3 ("another et-lab-start is cloning") while the first
completes. `strace -f` of `--check` and `--dry-run` shows no open of a `/dev/et*` node or a card lock. `bash -n` and
ShellCheck 0.11.0 pass. The setup path itself (linger, the installer, tmux, the clone) runs the same commands as
START.md step 3 but has not been run by the script yet: the first new user's run, or a run as a test account, is its
first. The third version (30 September, evening), after aifoundry1's `/home` went from 99% to 72% used (116 GB
free) when a departed user's public model checkpoints were deleted at the owner's word, installs Claude Code there by
default too and words aifoundry1's disk note as history; `bash -n`, ShellCheck, and `--check` and `--dry-run` on
aifoundry2 (as a file) and aifoundry1 (through `bash -s`) were rerun. Install, as root, on each host:
`install -o root -g root -m 0755 tools/lab/et-lab-start /usr/local/bin/et-lab-start.new && mv -f
/usr/local/bin/et-lab-start.new /usr/local/bin/et-lab-start`; roll back by removing it.

## Where the content comes from

Everything in the brief is in the public repository already, or was read on the machines without root:

- the rules and their reasons: `AGENT.md` §5, `CLAUDE.md`, `docs/lab-access.md`, the login banners in `tools/lab/`;
- the cards: `AGENT.md` §4 and `docs/findings/14-card-behaviour.md`;
- the traps: `docs/findings/14-card-behaviour.md` ("Traps that cost time here"), `docs/getting-started.md` §7, and
  the onboarding and per-card drafts (appendices A and B) of the public lab problems report;
- the measuring practice: `AGENT.md` §7, `tools/claims-v3/` (its `lib.sh`, `pcie2/README.md`) and
  `workloads/sparseparity/card_run.sh`;
- the machine choice (START.md step 2) and `et-lab-start`: the owner's request of 30 September 2026 (one prompt,
  only a username, the agent choosing the machine; an onboarding script; card use logged, shown by `et-usage`);
- the host facts: a read-only check of aifoundry1, aifoundry2 and aifoundry3 on 30 September 2026, 13:24–13:40 PDT
  (no card opened, no card binary run, no sudo). It found what a new user meets that the other documents do not
  say: `ssh host 'cmd'` gets no `/opt/et/bin` on PATH (the `et-*` tools are in `/usr/local/bin` and work); `gh` is
  missing on aifoundry2 and aifoundry3, so the brief clones over HTTPS; a `--depth 1` clone is about 380 MB (78 MB of
  git, 257 MB of it `docs/reports/data/`); pip needs a venv (PEP 668); tmux is on all three hosts; nothing such as
  node or an agent is installed system-wide.
- a review and a cold-start test of the brief on 30 September 2026 (13:46–13:52 PDT on aifoundry3, no card opened),
  whose findings the brief applies, and a read-only recheck at 13:55–14:00 PDT. What they found that the other
  documents do not yet say: `who` and `et-lab-health` rev 2 miss ssh command sessions, which
  `loginctl list-sessions` shows (and `loginctl` in turn misses a Claude kept in tmux under linger, which has no
  session at all: the brief counts people by their processes); on aifoundry1, `/opt/et/bin/it_test_code_loading` and
  host programs built there (through the static `libdeviceLayer.a`) honour `ET_DEVICES`, while `dev_mngt_service`
  does not (`libetrt.so` holds only `GET_DEVICES`, which a plain `grep ET_DEVICES` also matches: the brief uses
  `grep -w`); `it_test_code_loading` defaults to the simulator (the upstream `RuntimeFixture.h`), and the brief passes
  `--mode=sysemu`, which aifoundry1's fork build also accepts; a partial clone without `docs/reports/`
  (`--filter=blob:none --sparse`, then `git sparse-checkout set --no-cone '/*' '!/docs/reports/'`) is about 35 MB
  and holds every file the brief names; aifoundry1's `/home` had 7.4 GB free, in a pool shared with `/`; the
  simulator test writes its UART logs into the directory it runs in; `flock -n` exits 1 with no output on a taken
  lock. These belong in `docs/lab-access.md` and `docs/getting-started.md` too (`AGENT.md` §10).

## What the brief leaves out, on purpose

The page is public, so it follows `AGENT.md` §10: no access routes or credentials, no addresses or tailnet names, no
sudo, ACL or policy details, nothing on which accounts hold which privileges, no PCI addresses, no reset commands, no
service names, and no people's names in the prompt (it says "the lab lead" and "the lab admin"; only the page names
Roman, as the person to ask). `et-lab-start` follows the same rule in what it prints. How to get access is said the way
`docs/lab-access.md` says it: ask the lab lead for an account and a Tailscale invite, and approve the login in a
browser. No name remains, in links either: the brief reaches the lab problems report through the hub's improvement
ladder (`et-soc1-limits-of-observability#improve`) rather than by the report's own address.

## Keeping it current

Update START.md when a card's firmware, clock policy or health changes, when a lab tool changes (for instance
`et-usage` and `et-lab-start` being installed everywhere, when "the lab is starting to log card use" becomes "the lab
logs card use"; `et-lab-health` rev 3 and `et-reset` are on all three machines since 30 September, aifoundry1 and
aifoundry3 at 14:38–14:39 PDT and aifoundry2 at 15:36, the same `et-lab-health` as `tools/lab/et-lab-health`), when
aifoundry1 card 1's clock after the power cycle of 30 September has been read (the brief says "not rechecked"),
when the lab adopts the onboarding page (the lab problems report's request DI1), or when a new trap costs someone
time. Bump its "Version of" line (the page shows it), rebuild, and redeploy the page. Keep `et-lab-start`'s per-host
card facts and its printed Remote Control steps and rules in step with START.md. The facts it states are dated in `AGENT.md` §4, `docs/lab-access.md` and
`docs/findings/14-card-behaviour.md`; where those change, this changes.
