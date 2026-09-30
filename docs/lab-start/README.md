# docs/lab-start: the new-user brief

The owner asked on 30 September 2026 for a "New user? Start now" link on the lab dashboard, leading to
self-contained instructions that people can give their coding agents to do the setup, built from what a week of
running the lab taught us. This directory holds that brief; the page shows it.

| File | What it is |
|---|---|
| `START.md` | The brief itself: one self-contained markdown document that a new user pastes into a coding agent (Claude Code or similar). Who the agent works for and its limits, the four cards, the rules with their reasons, a first-hour checklist with exact commands, the traps (symptom, cause, fix), how to measure so results hold, how to leave the lab clean, where to ask. About 3,600 words, including the steps for a Claude on the machine. |
| `make_page_data.py` | Writes `docs/reports/data/2026-09-30-lab-start/brief.json` (START.md word for word, its sha256 and word count, and the page's card tiles). `--check` exits 1 if the JSON is stale. |
| `README.md` | This file. |

The page is `docs/reports/2026-09-30-aifoundry-lab-start.html`, built from
`docs/reports/sources/lab-start.{body.html,script.js,meta.json}`. It shows START.md in a copy box (with the
viewer's login and card filled into `<login>`, `<host>` and `<N>`), renders the same text below it, and offers the
repository copy as a one-line alternative
(`https://raw.githubusercontent.com/yaroslavvb/et-soc1-prototyping/main/docs/lab-start/START.md`, which works once
this directory is pushed). The page is meant to be public: new users cannot open the owner's private pages.

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

Edit START.md, never the JSON or the HTML. The page's markdown renderer (in `lab-start.script.js`) knows only what
START.md uses: `##`/`###` headings, paragraphs, flat `-` and `1.` lists, pipe tables, fenced code, inline code,
bold and links. Keep the placeholders spelled exactly `<login>`, `<host>` and `<N>`, since the page fills those.

## Where the content comes from

Everything in the brief is in the public repository already, or was read on the machines without root:

- the rules and their reasons: `AGENT.md` §5, `CLAUDE.md`, `docs/lab-access.md`, the login banners in `tools/lab/`;
- the cards: `AGENT.md` §4 and `docs/findings/14-card-behaviour.md`;
- the traps: `docs/findings/14-card-behaviour.md` ("Traps that cost time here"), `docs/getting-started.md` §7, and
  the onboarding and per-card drafts (appendices A and B) of the public lab problems report;
- the measuring practice: `AGENT.md` §7, `tools/claims-v3/` (its `lib.sh`, `pcie2/README.md`) and
  `workloads/sparseparity/card_run.sh`;
- the host facts: a read-only check of aifoundry1, aifoundry2 and aifoundry3 on 30 September 2026, 13:24–13:40 PDT
  (no card opened, no card binary run, no sudo). It found what a new user meets that the other documents do not
  say: `ssh host 'cmd'` gets no `/opt/et/bin` on PATH (the `et-*` tools are in `/usr/local/bin` and work); `gh` is
  missing on aifoundry2 and aifoundry3, so the brief clones over HTTPS; a `--depth 1` clone is about 380 MB (78 MB of
  git, 257 MB of it `docs/reports/data/`); pip needs a venv (PEP 668); tmux is on all three hosts; nothing such as
  node or an agent is installed system-wide.
- a review and a cold-start test of the brief on 30 September 2026 (13:46–13:52 PDT on aifoundry3, no card opened),
  whose findings the brief applies, and a read-only recheck at 13:55–14:00 PDT. What they found that the other
  documents do not yet say: `who` and the installed `et-lab-health` (rev 2) miss ssh command sessions, which
  `loginctl list-sessions` shows; on aifoundry1, `/opt/et/bin/it_test_code_loading`, `libetrt.so` and host programs
  built there honour `ET_DEVICES`, while `dev_mngt_service` does not; a partial clone without `docs/reports/`
  (`--filter=blob:none --sparse`, then `git sparse-checkout set --no-cone '/*' '!/docs/reports/'`) is about 35 MB
  and holds every file the brief names; aifoundry1's `/home` had 7.4 GB free, in a pool shared with `/`; the
  simulator test writes its UART logs into the directory it runs in; `flock -n` exits 1 with no output on a taken
  lock. These belong in `docs/lab-access.md` and `docs/getting-started.md` too (`AGENT.md` §10).

## What the brief leaves out, on purpose

The page is public, so it follows `AGENT.md` §10: no access routes or credentials, no addresses or tailnet names, no
sudo, ACL or policy details, nothing on which accounts hold which privileges, no PCI addresses, no reset commands, no
service names, and no people's names (it says "the lab lead" and "the lab admin"). How to get access is said the way
`docs/lab-access.md` says it: ask the lab lead for an account and a Tailscale invite, and approve the login in a
browser. No name remains, in links either: the brief reaches the lab problems report through the hub's improvement
ladder (`et-soc1-limits-of-observability#improve`) rather than by the report's own address.

## Keeping it current

Update START.md when a card's firmware, clock policy or health changes, when a lab tool changes (for instance
`et-lab-health` rev 3 or `et-reset` being installed), when the lab adopts the onboarding page (the lab problems
report's request DI1), or when a new trap costs someone time. Bump the version date on its second line, rebuild,
and redeploy the page. The facts it states are dated in `AGENT.md` §4, `docs/lab-access.md` and
`docs/findings/14-card-behaviour.md`; where those change, this changes.
