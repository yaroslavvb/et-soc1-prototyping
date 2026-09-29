# tools/timeline: the session-timeline page

These scripts build [A week with the ET-SoC-1: the session timeline](https://spacesheep.dev/@yaroslavvb/et-soc1-session-timeline)
(`docs/reports/2026-09-27-session-timeline.html`): the session's week on one time axis, with the owner's messages,
the main agent and its subagents, the four cards, and every deploy and commit.

The pipeline has two halves. The **extraction** reads the session's Claude Code transcripts and the lab machines' queue
logs. Those are not in the repository, so only the owner's machine can run it. The **build** needs only the seven
extracts committed in `docs/reports/data/2026-09-27-session-timeline/`, so any checkout can rebuild the page.

## The scripts, in order

| # | Script | Reads | Writes (to `$TIMELINE_DIR`) |
|---|---|---|---|
| 1 | `extract_main.py` | the main transcript | `human.json`: the owner's inputs (time, kind, category, a hand-written summary of at most 12 words from its `SUMMARIES` table, never the text, and estimated reading and typing time), plus engagement sessions. `main_agent.json`: the main agent's busy intervals, tokens per message, compactions and usage limits |
| 2 | `extract_agents.py` | every subagent and workflow transcript, the workflow run files, `main_agent.json` | `agents.json`: one row per agent, the workflow runs, busy agents per minute, the peaks |
| 3 | `tokens_by_time.py` | the same transcripts, `agents.json` | `tokens_by_time.json`: tokens per PDT day and hour, main agent against subagents |
| 4 | `extract_card_calls.py` | the main transcript | `card_calls.json`: the main agent's own commands that ran a program on a card (development and debug runs) |
| 5 | `build_cards.py` | `$TIMELINE_DIR/hostlogs/<host>/*.log` (copies of the claims-v3 queue and smoke logs), the committed `block.json` files, the earlier experiments' data files, `docs/findings/03-experiments.md` | `cards.json`: every interval in which a card was held by a measurement |
| 6 | `scan_spacesheep.py` | every transcript | `work/spacesheep_calls.jsonl`: every Bash call that mentions spacesheep or a deploy script, with its result |
| 7 | `build_artifacts.py` | `work/spacesheep_calls.jsonl`, `docs/reports/MIRROR.md`, `spacesheep versions` of each MIRROR page (cached in `work/versions/`), `git log --all` | `artifacts.json`: every deploy, share and visibility change, and every commit |
| 8 | `sanitize_extracts.py` | the extracts, after they are copied to the data folder | rewrites them in place with the page's redactions, then scans them; exits 1 on any hit |
| 9 | `build_timeline_data.py` | the seven extracts in the data folder | `timeline.json`, which the page draws; the highlights and their captions are computed here |

`paths.py` holds every path the scripts use. The page itself is `docs/reports/sources/session-timeline.*`, assembled by
`scripts/build-report.py`.

## A refresh, from start to end

On the owner's machine (aifoundry2), from the repository root:

```bash
export TIMELINE_DIR=/path/to/a/scratch/folder          # copy the lab machines' queue logs to $TIMELINE_DIR/hostlogs/<host>/ first
export TIMELINE_DV2V_BUILD=$TIMELINE_DIR/dvfs2/claims-v3   # a copy of the claims-v3 build folder that holds the DV2 validation
export TIMELINE_CUTOFF=$(date -u +%Y-%m-%dT%H:%M:00Z)   # the snapshot
export TIMELINE_SKIP=<this refresh's own workflow or agent id>   # its commands only search for spacesheep calls
python3 tools/timeline/extract_main.py
python3 tools/timeline/extract_agents.py
python3 tools/timeline/tokens_by_time.py
python3 tools/timeline/extract_card_calls.py
python3 tools/timeline/build_cards.py
python3 tools/timeline/scan_spacesheep.py
python3 tools/timeline/build_artifacts.py
D=docs/reports/data/2026-09-27-session-timeline
for f in human main_agent agents cards artifacts tokens_by_time card_calls; do cp "$TIMELINE_DIR/$f.json" $D/; done
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

Before the first step, give every new owner message a summary in `extract_main.py`'s `SUMMARIES` (keyed by the UTC
second it was sent). The script prints the ones it has no summary for as `unsummarised`. A summary says what was
asked, in at most 12 words and the third person, and never quotes the message. When a new stretch of the week needs a
highlight, add it to `HL` in `build_timeline_data.py`, and add its page links to `HL_LINKS`, which may only name
public pages.

To rebuild the page from the committed extracts, only the `D=` line and the last five commands are needed.

## Settings (environment variables)

| Variable | Default | What it is |
|---|---|---|
| `TIMELINE_TRANSCRIPTS` | the Claude Code project folder of the checkout's parent directory | the Claude Code project folder with the session's transcripts |
| `TIMELINE_SESSION` | `ed6d06d5-de26-4323-94f1-0dc808eafbda` | the session id |
| `TIMELINE_DIR` | `$TMPDIR/et-soc1-timeline` | the working folder: the extracts, `hostlogs/`, `work/` |
| `TIMELINE_CUTOFF` | none (now) | ISO time of the snapshot; transcript lines, card calls, spacesheep calls and blocks after it are left out. `extract_agents.py` has no cutoff: it reads to the end, and the page's snapshot is the later of the two |
| `TIMELINE_SKIP` | none | comma-separated parts of transcript paths that `scan_spacesheep.py` skips (the refresh's own run) |
| `TIMELINE_PRIVATE` | `~/.config/et-soc1-timeline/private.json` | the local privacy table (below); never committed. `none` lets `extract_agents.py` and `build_artifacts.py` run without one |
| `TIMELINE_HP_BUILD` | the heat-placement data's `raw/` | where aifoundry2's two heat-placement sessions' `hp/a2` blocks are |
| `TIMELINE_DV2V_BUILD` | `build/claims-v3` of this checkout | claims-v3 build folders (separated by `:`) with DV2 validation (`dv2v`) blocks that are not committed yet |
| `TIMELINE_EXTRA_MIRRORS` | none | other checkouts' `MIRROR.md` files (separated by `:`) that list pages main does not list yet |
| `TIMELINE_VERSIONS_FETCH` | `1` | `0` reuses the cached `spacesheep versions` output without the network |
| `TIMELINE_REPO` | this checkout | the repository |

## The sanitize rule

The page and its data are public, so they follow AGENT.md section 10. They never quote the owner's messages; they
never name who holds which privilege on the lab machines, how the machines are reached, their addresses, keys or
tokens; they never name other people beyond the few already public; and they never link a private page. The rule is
applied in three places.

1. **At the source.** The owner's messages are summaries written for the page (`extract_main.py`, `SUMMARIES`), and the
   workflows and agents of the report for the lab lead are unnamed, from the local privacy table.
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
