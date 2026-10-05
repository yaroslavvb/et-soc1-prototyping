# tools/timeline: the session-timeline page

These scripts build [A week with the ET-SoC-1: the session timeline](https://spacesheep.dev/@yaroslavvb/et-soc1-session-timeline)
(`docs/reports/2026-09-27-session-timeline.html`): the session, from 19 September, on one time axis, with the owner's
messages (a summary and, since the refresh of 5 October, the message's own words), the main agent and its subagents, the
other Claude sessions on the lab's machine in lanes of their own (on either of the owner's two Claude accounts), the four
cards and the hosts and cards down, and every deploy and commit.

The pipeline has two halves. The **extraction** reads the session's Claude Code transcripts and the lab machines' queue
logs. Those are not in the repository, so only the owner's machine can run it. The **build** needs only the eight
extracts committed in `docs/reports/data/2026-09-27-session-timeline/`, so any checkout can rebuild the page.

## The scripts, in order

| # | Script | Reads | Writes (to `$TIMELINE_DIR`) |
|---|---|---|---|
| 1 | `extract_main.py` | the main transcript | `human.json`: the owner's inputs (time, kind, category, a hand-written summary of at most 12 words from its `SUMMARIES` table, the message's words as `prompt_privacy.redact()` lets the public page show them, and estimated reading and typing time), plus engagement sessions. `main_agent.json`: the main agent's busy intervals, tokens per message, compactions and usage limits |
| 2 | `extract_agents.py` | every subagent and workflow transcript, the workflow run files, `main_agent.json` | `agents.json`: one row per agent, the workflow runs, busy agents per minute, the peaks |
| 3 | `tokens_by_time.py` | the same transcripts, `agents.json` | `tokens_by_time.json`: tokens per PDT day and hour, main agent against subagents |
| 4 | `extract_card_calls.py` | the main transcript | `card_calls.json`: the main agent's own commands that ran a program on a card (development and debug runs) |
| 5 | `build_cards.py` | `$TIMELINE_DIR/hostlogs/<host>/*.log` (copies of the claims-v3 queue and smoke logs), the committed `block.json` files, the earlier experiments' data files, `docs/findings/03-experiments.md` | `cards.json`: every interval in which a card was held by a measurement |
| 6 | `scan_spacesheep.py` | every transcript | `work/spacesheep_calls.jsonl`: every Bash call that mentions spacesheep or a deploy script, with its result |
| 7 | `extract_neighbors.py` | the transcripts of the sessions in `$TIMELINE_NEIGHBORS` (and their subagents'), in either account's project folder (`paths.PROJECTS`), the committed `neighbors.json` (for a transcript rewritten shorter), `docs/reports/MIRROR.md`, `git log` | `neighbors.json`: each neighbor's lane name (`NEIGHBOR_INFO`), busy intervals, its subagents' busy time, the owner's messages to it (summaries from its `NEIGHBOR_SUMMARIES` and their words, redacted as in step 1), its key events (its `EVENTS`, plus its deploys of public pages and its commits), and the hosts and cards down (`HOSTS`: the link-retrain hang and the power cycle of 30 Sep, aifoundry2's card off the bus and its reboots on 1–2 Oct, aifoundry1 off for card 0's new fan); `work/neighbor_deploys.json`: all its deploys, private spaces too (never copied to the data folder) |
| 8 | `build_artifacts.py` | `work/spacesheep_calls.jsonl`, `work/neighbor_deploys.json`, `docs/reports/MIRROR.md`, `spacesheep versions` of each MIRROR page (cached in `work/versions/`), `git log --all` | `artifacts.json`: every deploy, share and visibility change, and every commit; a version in a page's history that a neighbor deployed is not counted as this session's, and the versions of the two pages a cron job republishes (`AUTO_PAGES`: the lab dashboard and its history) are left out |
| 9 | `sanitize_extracts.py` | the extracts, after they are copied to the data folder | rewrites them in place with the page's redactions, then scans them; exits 1 on any hit |
| 10 | `build_timeline_data.py` | the eight extracts in the data folder (`neighbors.json` is optional) | `timeline.json`, which the page draws; the highlights and their captions are computed here |

`paths.py` holds every path the scripts use, and `prompt_privacy.py` the redaction of the owner's words (below, "The
sanitize rule"). The page itself is `docs/reports/sources/session-timeline.*`, assembled by `scripts/build-report.py`.

## A refresh, from start to end

On the owner's machine (aifoundry2), from the repository root:

```bash
export TIMELINE_DIR=~/claude/work/et-soc1-timeline     # not /tmp; copy the lab machines' queue logs to $TIMELINE_DIR/hostlogs/<host>/ first
export TIMELINE_DV2V_BUILD=$TIMELINE_DIR/dvfs2/claims-v3   # a copy of the claims-v3 build folder that holds the DV2 validation
export TIMELINE_CUTOFF=$(date -u +%Y-%m-%dT%H:%M:00Z)   # the snapshot
export TIMELINE_SKIP=<this refresh's own workflow or agent ids, comma-separated>   # their commands only search for spacesheep calls
# every other session on the machine in the span, each a lane; '+' joins short ones into one lane (5 Oct 2026's list)
export TIMELINE_NEIGHBORS=97db24ee-042f-547a-86c0-e1444e260a06,93af8ad7-eefa-5df8-8a2b-131bb784741b,c42b457d-be89-519e-afb1-7f3f5efb364d,1f1f61cb-8008-5774-b34d-1bfa335333c7,d1dcf7d2-cc6f-44a2-880f-6c0683670124+8ca68501-63e6-5110-97ae-b821665005d2+a4bad5b7-56bb-52be-ac0a-f4c76c7c14f6+344c2a05-f432-5d99-9c76-3be80145a731+a679cf50-7b99-4c38-a1ea-efd52ba06216+afaecf2a-e87a-5b3b-8894-a7df1ec1329b
python3 tools/timeline/extract_main.py
python3 tools/timeline/extract_agents.py
python3 tools/timeline/tokens_by_time.py
python3 tools/timeline/extract_card_calls.py
python3 tools/timeline/build_cards.py
python3 tools/timeline/scan_spacesheep.py
python3 tools/timeline/extract_neighbors.py             # before build_artifacts.py, which reads its work/neighbor_deploys.json
python3 tools/timeline/build_artifacts.py
D=docs/reports/data/2026-09-27-session-timeline
for f in human main_agent agents cards artifacts tokens_by_time card_calls neighbors; do cp "$TIMELINE_DIR/$f.json" $D/; done
python3 tools/timeline/sanitize_extracts.py            # must print "privacy scan: clean"
python3 tools/timeline/build_timeline_data.py
python3 scripts/build-report.py session-timeline $D/timeline.json docs/reports/2026-09-27-session-timeline.html
bash docs/reports/data/2026-09-24-report-review/tools/check_page.sh docs/reports/2026-09-27-session-timeline.html
DARK=1 bash docs/reports/data/2026-09-24-report-review/tools/check_page.sh docs/reports/2026-09-27-session-timeline.html
```

The logs to copy (read-only, with `scp`): every `*.log` in `~/nekko/build/claims-v3/` of aifoundry1 and aifoundry3 (the
queue logs, and the series and run logs of the experiments that ran without `queue.sh`, such as pcie2, nocr, memp2 and
tau); a waiter's own log (`*-waiter.log`) is not a queue log and stays behind. aifoundry2's are local: the claims-v3
queue and smoke logs, and the DV2 queue logs of the build folder the validation runs in (`queue-dv2-*.log`,
`queue-dv2val-*.log`), which is also the folder to copy for `TIMELINE_DV2V_BUILD`.

To list the sessions of a span on either account, with each owner message's time and length: the project folders in
`paths.PROJECTS` (a session started from the phone is named by a uuid whose third group starts with 5). A new neighbor
needs a line in `extract_neighbors.py`'s `NEIGHBOR_INFO` (its lane's label, its name, a line about it), and its key
events in `EVENTS`.

Before the first step, give every new owner message a summary in `extract_main.py`'s `SUMMARIES` (keyed by the UTC
second it was sent), and every owner message to a neighbor one in `extract_neighbors.py`'s `NEIGHBOR_SUMMARIES`. The
scripts print the ones they have no summary for as `unsummarised` (a neighbor's is then left off the page). A summary says what was
asked, in at most 12 words and the third person, and never quotes the message. When a new stretch of the week needs a
highlight, add it to `HL` in `build_timeline_data.py`, and add its page links to `HL_LINKS`, which may only name
public pages.

To rebuild the page from the committed extracts, only the `D=` line and the last five commands are needed.

## Settings (environment variables)

| Variable | Default | What it is |
|---|---|---|
| `TIMELINE_TRANSCRIPTS` | the Claude Code project folder of the checkout's parent directory | the Claude Code project folder with the session's transcripts |
| `TIMELINE_SESSION` | `ed6d06d5-de26-4323-94f1-0dc808eafbda` | the session id |
| `TIMELINE_DIR` | `~/claude/work/et-soc1-timeline` (until 30 September `$TMPDIR/et-soc1-timeline`, which a boot clears) | the working folder: the extracts, `hostlogs/`, `work/` |
| `TIMELINE_CUTOFF` | none (now) | ISO time of the snapshot; transcript lines, card calls, spacesheep calls and blocks after it are left out. `extract_agents.py` has no cutoff: it reads to the end, and the page's snapshot is the later of the two |
| `TIMELINE_SKIP` | none | comma-separated parts of transcript paths that `scan_spacesheep.py` skips (the refresh's own run: a workflow's `wf_…` id, or an Agent-tool agent's `agent-<id>`) |
| `TIMELINE_MORE_PROJECTS` | the second account's folder of the same name (`~/.claude-yv2/projects/<name>`) | more Claude Code project folders (separated by `:`) in which `extract_neighbors.py` finds neighbor sessions: the owner's second Claude account keeps its sessions in its own config home |
| `TIMELINE_PREV_WORK` | `~/claude/work/et-soc1-timeline/work` | the previous refresh's `work/` folder, whose `neighbor_deploys.json` keeps the deploys of a neighbor whose transcript has since been rewritten shorter |
| `TIMELINE_NEIGHBORS` | `97db24ee-042f-547a-86c0-e1444e260a06` | comma-separated ids of other Claude Code sessions that get a lane of their own; ids joined with `+` share one lane (`extract_neighbors.py`); `none` for none. The same privacy rules apply: summaries only, no workflow or agent names, no private page named |
| `TIMELINE_PRIVATE` | `~/.config/et-soc1-timeline/private.json` | the local privacy table (below); never committed. `none` lets `extract_agents.py` and `build_artifacts.py` run without one |
| `TIMELINE_HP_BUILD` | the heat-placement data's `raw/` | where aifoundry2's two heat-placement sessions' `hp/a2` blocks are |
| `TIMELINE_DV2V_BUILD` | `build/claims-v3` of this checkout | claims-v3 build folders (separated by `:`) with DV2 validation (`dv2v`) blocks that are not committed yet |
| `TIMELINE_EXTRA_MIRRORS` | none | other checkouts' `MIRROR.md` files (separated by `:`) that list pages main does not list yet |
| `TIMELINE_VERSIONS_FETCH` | `1` | `0` reuses the cached `spacesheep versions` output without the network |
| `TIMELINE_REPO` | this checkout | the repository |

## The sanitize rule

The page and its data are public, so they follow AGENT.md section 10. They never name who holds which privilege on
the lab machines, how the machines are reached, their addresses, keys or tokens; they never name other people beyond
the few already public; and they never link a private page. Until 5 October 2026 they never quoted the owner's
messages either; since then, at the owner's request ("make sure that when I hover, it gives a way to see the actual
prompts used, not just summaries"), each message carries its own words, redacted. The rule is applied in three places.

1. **At the source.** Each owner message has a summary written for the page (`extract_main.py`, `SUMMARIES`;
   `extract_neighbors.py`, `NEIGHBOR_SUMMARIES`), and its words pass through `prompt_privacy.redact()` before they are
   written to an extract: a link is judged whole (a spacesheep page stays only if MIRROR.md lists it public, and its
   anchor goes if it names access; the report for the lab lead becomes "the report for the lab lead"; a session page,
   a login link or a private repository is removed); then e-mail and IP addresses, absolute paths, `--space` ids of
   pages that are not public and the agents' permission mode; then the privacy table's `prompt_redactions` and name
   redactions, in any case (other people's names and places); then every sentence that names access (root, sudo, ssh,
   Tailscale, keys or passwords, ACLs, who logs in as whom) or matches a forbidden pattern is removed whole. Each removal
   is a visible "[removed: …]" marker, and the extract lists the kinds removed. The words of the maintenance session's
   messages of 30 September are gone (its transcript was rewritten on 2 October), so those keep only their summaries.
   The workflows and agents of the report for the lab lead are unnamed, from the local privacy table.
2. **The sanitize rules**, applied by `sanitize_extracts.py` to every string of every committed extract and of
   `timeline.json`, which covers every summary, label, name, caption and commit subject the page shows. Its rewrite
   rules are read from the privacy table, because they would name what they remove. A "source" or "file" field that
   holds an absolute path keeps only its basename.
3. **The scan.** `sanitize_extracts.py` fails, and `build_timeline_data.py` refuses to write `timeline.json`, on any
   match of `FORBIDDEN` (privilege words, SSH and ACL terms, private address ranges, spacesheep keys and listen links,
   e-mail addresses, local paths), on any pattern of the privacy table, and on any space uuid (in a uuid field, an
   address or a `--space` argument) that `MIRROR.md` does not list as public: a private page, such as this page's
   private duplicate, is never named or linked. When the scan fails, add a rule for the new wording to the privacy
   table's `sanitize` list. Never commit an extract that has not passed the scan.

The privacy table (`$TIMELINE_PRIVATE`) is JSON with `private_workflows` (a workflow name mapped to its display name),
`agent_name_redactions`, `artifact_name_redactions` and `sanitize` (pairs of a pattern and its replacement; `sanitize`
applies to every string), `forbidden` (more patterns the scan rejects, in any case), and `lab_report_slug_prefix`,
`lab_report_title_words` and `lab_report_file_word` (how the report for the lab lead is recognised). It holds what the
page must not show, so it stays out of the repository (keep it readable only by its owner). Without it
`extract_agents.py` and `build_artifacts.py` stop, unless `TIMELINE_PRIVATE=none`; `sanitize_extracts.py` and
`build_timeline_data.py` still run on the committed extracts, which have passed the scan, and check them against the
fixed list only.

## The owner's words: the tooltip and the reader

Since 5 October 2026 an owner message's details (hover, a tap, or Tab) show its summary and the start of its words (360
characters, with how many more there are), and a click, a second tap on the same mark (as on a highlight's flag) or
Enter opens the **prompt reader**, a `<dialog>` with the whole message, its time, kind and request, what was removed
for the public page, and ← Earlier / Later → (also the arrow keys) through all the owner's messages, every session's
in time order. §3 lists the start of each message's words under its summary, with a "read it whole" button that opens
the same reader. One trap, measured: on a phone the click that follows the tap that opened the reader lands on the
reader's backdrop, so the backdrop closes the reader only when the press also began there. `gestures/prompts.mjs`
checks all of it on a desktop and a phone.

## Gestures: what the page does, and what we measured

The two timeline frames take their gestures in `gestures()` (the page's script); the checks are in `gestures/`
(`suite.mjs`: synthesized touch and wheel input in the page checker's headless Chrome, phones at 390×844 and 360×740
with DPR 3 and a 4× CPU throttle, and a 1280×800 desktop; its README lists the rest).

- **Vertical page scroll stays native** (`touch-action: pan-y` on the frames). A touch decides its direction once,
  after 8 px: sideways pans the timeline (with momentum after the finger lifts); anything steeper is left to the page.
  Before, a diagonal swipe did both: the timeline lurched while the page scrolled.
- **A touch shows a tooltip only on a tap** (CK.tip pins at pointerdown, so the frames catch the touch first and send
  the tap on). Before, every vertical scroll that started on a mark left its tooltip pinned. A second tap on a
  highlight's flag zooms there; a mouse click still zooms at once.
- **A wheel gesture keeps the axis of its first event**, as Chrome latches a scroll: a page scroll that drifts
  sideways never starts a pan. Ctrl/⌘ + wheel (a trackpad pinch) zooms about the pointer; deltaX and Shift + wheel pan.
- **`overscroll-behavior-x: contain` on the SVG, never on the frames' scroller.** `.ck-plot` is a scroll container
  that never scrolls here; with `contain` on it, Chrome latched a diagonal swipe to it and the page did not scroll at
  all (measured: 0 px instead of about 175). On the SVG, as the reusable component has it, it is harmless; the
  back-swipe is stopped by the page consuming sideways input itself (`preventDefault` on a sideways wheel gesture).
- **From the reusable component's lessons** (spacesheep.dev/@yaroslavvb/scrollable-session-timeline, `LESSONS.md` §5,
  published 30 Sep 23:25 UTC): the two-finger distance is floored at 24 px (`hypot`), lifting one finger of a pinch
  carries on as a one-finger drag, the release listeners are on `window`, pointer capture is taken only once a drag
  starts, `pointerdown` is never filtered by target, and tooltips and keyboard stops wait for the gesture's end. Two
  deliberate differences: a touch's slop is 8 px with the direction decided once (the component's 6 px, measured
  sideways, turned a 6 px tap wobble into a pan here), and a wheel gesture keeps its first event's axis rather than
  arbitrating each event (per event, a trackpad scroll that drifted sideways scrolled the page, then panned).
- **Fast frames.** A redraw built every mark as a node with a tooltip, whose text used `toLocaleString` (an
  `Intl.NumberFormat` per call) and a DOMParser per node: 27 ms a frame at a two-day view and about 200 ms at the
  whole span on the throttled phone. While a gesture, its momentum or a zoom animation runs, each series is now one
  path with no tooltips, and the full drawing follows when the browser is idle: 7-10 ms a frame at two days, about 20
  at the whole span. Zoom animations interpolate the span in log space, so a deep zoom moves evenly.
