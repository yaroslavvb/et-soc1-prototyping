#!/usr/bin/env python3
"""Extract task A: human messages and main-agent activity/tokens from the main session transcript.

Streams the JSONL line by line. Writes:
  ../human.json       human inputs (summarised, never verbatim), active-time estimates, engagement sessions
  ../main_agent.json  main-agent busy intervals, token usage (deduped by message.id) per message/hour/day/model

Summaries are hand-written (<= 12 words, no names of other people, no credentials or access paths) in SUMMARIES
below, keyed by the UTC second of the human input.  Inputs not in SUMMARIES get summary=null and are flagged.
They describe a message in the third person and never repeat its wording.

The owner's messages sent from a published page's Talk tab (spacesheep Talk) reach the session as task notifications
of a monitor ({"spacesheep_talk": true, "from": "the account owner ...", "message": ...}); each counts as an input of
kind 'talk' (its text is never kept, only its length).

$TIMELINE_CUTOFF (an ISO time) ends the transcript there, so a rerun reproduces a snapshot of a session that has
gone on since; the page's snapshot is 2026-09-29T09:14:00Z (the earlier ones, 2026-09-29T04:00:00Z,
2026-09-28T20:57:00Z, 2026-09-28T13:23:04Z and 2026-09-27T18:21:05.646Z). Paths: tools/timeline/paths.py.
"""
import json, os, re, sys, collections, math
from datetime import datetime, timezone, timedelta
from zoneinfo import ZoneInfo

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import paths  # noqa: E402

MAIN = paths.MAIN
PRE = paths.PRE
OUT = os.path.join(paths.ensure_tl(), '')
TZ = ZoneInfo('America/Los_Angeles')
CUTOFF = paths.CUTOFF   # ISO time: lines after it are ignored (the page's snapshot)

GAP_S = 180            # busy-interval gap rule: consecutive events < 3 min apart belong together
ENGAGE_GAP_S = 1800    # engagement sessions: human inputs < 30 min apart
TYPE_CPM = 200         # typing speed, characters per minute
TYPE_MIN_S = 10        # minimum typing time per message
READ_WPM = 250         # reading speed, words per minute
READ_CAP_S = 600       # reading-time cap per message
PASTE_TYPING_CAP_S = 180  # paste-adjusted variant: likely-pasted messages capped at 3 min typing

# ---------------------------------------------------------------- hand-written summaries
# key: UTC timestamp to the second  ->  (summary <= 12 words, category, request id from docs/findings/02-requests.md or None)
SUMMARIES = {
 '2026-09-19T16:19:14': ("Asks to turn on remote control.", 'request', 'Q1'),
 '2026-09-19T16:19:22': ("Runs the remote-control slash command.", 'status', 'Q1'),
 '2026-09-19T16:19:47': ("Clone the prototyping repo and check the card works.", 'request', 'Q2'),
 '2026-09-19T16:21:50': ("Lists connected MCP servers.", 'status', None),
 '2026-09-19T16:21:59': ("Tries an MCP subcommand for spacesheep.", 'status', None),
 '2026-09-19T16:22:22': ("Asks to publish a page through spacesheep.", 'request', 'Q3'),
 '2026-09-19T16:22:52': ("Answers: just configure spacesheep for all future reports.", 'approval/answer', 'Q3'),
 '2026-09-19T16:26:55': ("Research fine-grained power and latency observability; break down memory energy.", 'request', 'Q4'),
 '2026-09-20T17:04:04': ("Asks the agent to commit its work and push it.", 'request', 'Q5'),
 '2026-09-20T17:11:05': ("Mini-report on the limits of observability, down to bit flips.", 'request', 'Q6'),
 '2026-09-20T18:03:50': ("Quota reset; asks the agent to continue.", 'status', None),
 '2026-09-20T19:50:40': ("Quota renewed; asks the agent to finish the started work.", 'status', None),
 '2026-09-20T20:02:42': ("Approves implementation including the reflash; work sequentially to save quota.", 'approval/answer', 'Q7'),
 '2026-09-20T20:05:20': ("Confirms permission for the reflash; nobody is using the card.", 'approval/answer', 'Q7'),
 '2026-09-20T20:08:41': ("Reports that pushing to GitHub now works.", 'status', None),
 '2026-09-20T20:46:56': ("Opens the permissions dialog and approves two pending actions.", 'approval/answer', None),
 '2026-09-20T20:47:27': ("Asks to change this session's permission settings.", 'request', None),
 '2026-09-20T20:50:54': ("Interrupts the running response.", 'correction', None),
 '2026-09-20T20:51:16': ("Asks for help fixing a Claude Code settings-file error.", 'request', None),
 '2026-09-20T20:51:49': ("Asks the agent to continue the task.", 'status', None),
 '2026-09-20T20:54:26': ("Narrows the work to steps that need no firmware reflash.", 'correction', 'Q7'),
 '2026-09-21T04:06:47': ("Asks what a debug-interface client unlocks; wants a power/temperature report.", 'request', 'Q8'),
 '2026-09-21T04:11:22': ("Find a blog post on random-matrix power; reproduce it on-chip.", 'request', 'Q9'),
 '2026-09-21T04:33:36': ("Rerun the random-matrix experiment, cooling to one start temperature.", 'request', 'Q10'),
 '2026-09-21T04:53:58': ("Stray two-letter input, likely accidental.", 'status', None),
 '2026-09-21T05:46:30': ("Rerun with strict temperature control, clearer charts, and a flips-to-power model.", 'request', 'Q11'),
 '2026-09-21T13:17:37': ("Better temperature visualisation, plus a shareable animated GIF.", 'request', 'Q11'),
 '2026-09-21T15:41:55': ("Run longer experiments; model temperature from transistor flips.", 'request', 'Q12'),
 '2026-09-21T15:44:43': ("Waives 10-second rule: runs up to 10 min, 6 h total.", 'approval/answer', 'Q13'),
 '2026-09-21T15:50:42': ("Next: explain why Esperanto chips are low power versus A100s.", 'request', 'Q14'),
 '2026-09-21T19:44:53': ("Also design custom matrix workloads and predict the heat they produce.", 'request', 'Q15'),
 '2026-09-21T22:24:57': ("How is overfitting controlled; is there independent validation?", 'question', 'Q16'),
 '2026-09-21T22:38:31': ("Asks for the report to be corrected and committed.", 'request', 'Q17'),
 '2026-09-22T15:54:37': ("Summarise all findings as self-contained Markdown files; commit.", 'request', 'Q18'),
 '2026-09-22T15:55:38': ("Add provenance: modular experiments and artifacts so findings are traceable.", 'request', 'Q19'),
 '2026-09-22T18:32:23': ("Research the DVFS loop and leakage suppression from shared notes; brief.", 'request', 'Q20'),
 '2026-09-22T19:01:30': ("Try the other two lab cards.", 'request', 'Q21'),
 '2026-09-22T19:04:28': ("Run on all three machines; fold into the public report.", 'request', 'Q22'),
 '2026-09-22T19:06:03': ("Typeset math formulas with MathJax instead of HTML.", 'correction', 'Q23'),
 '2026-09-22T19:24:15': ("Test a reported shire-0 starvation claim; publish as a new page.", 'request', 'Q24'),
 '2026-09-22T22:31:52': ("Explore cache-line starvation paths; find a winning systolic-array application.", 'request', 'Q25'),
 '2026-09-22T22:32:52': ("Drop systolic; find any shire-to-shire computation beating the standard approach.", 'correction', 'Q26'),
 '2026-09-23T14:40:40': ("Build an energy manual: a hierarchical catalogue of operation costs.", 'request', 'Q27'),
 '2026-09-23T15:26:44': ("Measure the energy of every instruction across cards, within five hours.", 'request', 'Q28'),
 '2026-09-23T15:27:07': ("Asks to redeploy in place and make the page public.", 'request', 'Q29'),
 '2026-09-23T15:29:28': ("Finer energy breakdown: wires, cache-line activation, leakage.", 'request', 'Q30'),
 '2026-09-23T19:50:27': ("Add confidence bars from reruns and from different cards.", 'request', 'Q31'),
 '2026-09-23T19:55:38': ("Reduce unmetered memory energy; extend and restructure the observability report.", 'request', 'Q32'),
 '2026-09-23T20:29:39': ("Then update the GitHub repo as the source of truth.", 'request', 'Q33'),
 '2026-09-23T22:33:02': ("Shell command typed into the chat by mistake.", 'status', None),
 '2026-09-23T22:34:16': ("Checks whether the session is alive.", 'status', None),
 '2026-09-23T22:36:33': ("Observability report: add measurement sessions; make section 5 fit.", 'correction', 'Q34'),
 '2026-09-23T22:37:12': ("Energy manual error bars are clipped in section 3.1.", 'correction', 'Q35'),
 '2026-09-23T22:39:01': ("Make section headings linkable anchors.", 'request', 'Q36'),
 '2026-09-23T22:41:27': ("Commit every linked tool; the repo is the knowledge base.", 'request', 'Q37'),
 '2026-09-23T22:46:24': ("Section 5 still scrolls horizontally a little.", 'correction', 'Q38'),
 '2026-09-23T22:53:39': ("Move companion links into a described Related Reports section.", 'correction', 'Q39'),
 '2026-09-24T00:53:56': ("Make all spacesheep links in the observability report public.", 'request', 'Q40'),
 '2026-09-24T20:13:02': ("Verify on-chip wire energy per bit-mm experimentally; publish a report.", 'request', 'Q41'),
 '2026-09-24T20:42:57': ("Then install the sessions-board hooks on this machine, per runbook.", 'request', 'Q42'),
 '2026-09-24T20:47:17': ("Supplies the complete hook-install instructions.", 'correction', 'Q42'),
 '2026-09-24T22:03:42': ("Asks where this session's files and process live.", 'question', None),
 '2026-09-24T22:16:13': ("Side task: debug report on sessions missing their links.", 'request', 'Q42'),
 '2026-09-24T22:17:13': ("Points to a related report written from another machine.", 'status', 'Q42'),
 '2026-09-24T22:17:34': ("Shares the link to that related debug page.", 'status', 'Q42'),
 '2026-09-24T22:21:26': ("Include every bug found in the debug report.", 'request', 'Q42'),
 '2026-09-24T22:35:36': ("Bug report on mismatched session titles, with screenshots.", 'request', 'Q42'),
 '2026-09-25T00:07:11': ("Robustness and readability check of the observability report set.", 'request', None),
 '2026-09-25T06:06:29': ("Full validation run of all linked pages; add interactive charts.", 'request', 'Q44'),
 '2026-09-25T06:13:06': ("Then file feedback: this session's board title is wrong.", 'request', None),
 '2026-09-25T06:22:12': ("Claims check version 3: test on both machines, keep proven effects.", 'request', 'Q45'),
 '2026-09-25T16:38:24': ("Make the repo the ground truth: agent entry point, mirrored pages.", 'request', 'Q53'),
 '2026-09-25T17:22:49': ("Look for chances to add compelling visualisations to the pages.", 'request', 'Q54'),
 '2026-09-25T19:56:33': ("Troubleshoot the broken lab machine; also mentions a problem of its own.", 'request', 'Q46'),
 '2026-09-25T20:25:12': ("Reports that problem is solved.", 'status', None),
 '2026-09-25T21:08:57': ("Then write a private report for the lab lead.", 'request', 'Q51'),
 '2026-09-25T21:53:14': ("Explore whether the chip could speed up influence-function research.", 'request', 'Q49'),
 '2026-09-25T21:58:05': ("Correction: meant sparsity, not sparse parity; stay in this repo.", 'correction', 'Q49'),
 '2026-09-25T22:00:08': ("Go ahead and fix the broken lab machine's problems.", 'request', 'Q47'),
 '2026-09-25T22:00:34': ("Report on the fix afterwards, whether it succeeds or fails.", 'request', 'Q47'),
 '2026-09-25T22:00:50': ("Correction on how to carry out the fix.", 'correction', 'Q47'),
 '2026-09-25T22:09:35': ("Make the fix report public; find who should clean the disk.", 'request', 'Q47'),
 '2026-09-25T22:10:35': ("Rerun the observability measurements using all three machines.", 'request', 'Q50'),
 '2026-09-25T22:15:21': ("Permission to upgrade and fix all three machines, then re-measure.", 'approval/answer', 'Q48'),
 '2026-09-26T01:31:51': ("Naming instruction for the report for the lab lead.", 'correction', 'Q51'),
 '2026-09-26T02:21:41': ("Then measure gather and scatter throughput on all cards.", 'request', 'Q52'),
 '2026-09-26T04:50:58': ("Reinstall the spacesheep CLI and its session hooks.", 'request', None),
 '2026-09-27T18:08:46': ("Asks the agent to try again.", 'status', None),
 '2026-09-27T18:09:05': ("Build an interactive one-week timeline of human, agent, cards, artifacts.", 'request', None),
 '2026-09-27T18:09:21': ("Run experiments on where computation is placed and chip heat.", 'request', 'Q60'),
 '2026-09-27T18:10:15': ("Finish the scatter-gather experiments with multi-card validation.", 'request', 'Q52'),
 '2026-09-27T18:11:22': ("Interactive chip diagram for tomorrow's talk, linked atop the index.", 'request', None),
 '2026-09-27T18:16:02': ("Make sure the verification campaign completes and pages are updated.", 'request', 'Q45'),
 '2026-09-27T18:20:51': ("Approves keeping the recently published pages public.", 'approval/answer', None),
 '2026-09-27T19:49:45': ("Heat placement: allows 150 s chains and the log level; try now.", 'approval/answer', None),
 '2026-09-27T21:08:37': ("Chip diagram feedback: measure PCIe, smoother flows, stage controls, zoom.", 'request', 'Q58'),
 '2026-09-28T03:09:00': ("Asks for a summary of the experiment queues.", 'status', None),
 '2026-09-28T03:09:54': ("Asks especially about the heat-placement experiments.", 'status', None),
 '2026-09-28T03:15:45': ("Polish the diagram walkthroughs; new charts and a correctness pass.", 'request', None),
 '2026-09-28T03:37:14': ("Interactive diagrams for each memory level; missing facts become team asks.", 'request', None),
 '2026-09-28T04:21:10': ("Refresh the report for the lab lead; group the asks.", 'request', None),
 '2026-09-28T04:47:49': ("Design more DVFS and heat experiments; update the pages.", 'request', 'Q59'),
 '2026-09-28T05:24:14': ("Chip diagram zoom still jumps: find the cause and fix it.", 'correction', 'Q58'),
 '2026-09-28T13:14:33': ("Asks for the status; finish every task with parallel agents.", 'status', None),
 '2026-09-28T13:33:20': ("Fix every lab problem that does not need the lab's team.", 'request', None),
 '2026-09-28T13:33:54': ("Approves stopping the leftover headless browser processes.", 'approval/answer', None),
 '2026-09-28T13:35:32': ("Approves resetting the hung card with the sysfs reset.", 'approval/answer', None),
 '2026-09-28T13:39:24': ("Requests for the lab lead keep only what needs the lab's team.", 'request', None),
 '2026-09-28T15:32:30': ("Approves trying the management reset after the first failed.", 'approval/answer', None),
 '2026-09-28T15:41:56': ("Research overheating: limits, average versus hottest, speed, recovery; a new page.", 'request', 'Q61'),
 '2026-09-28T16:07:57': ("The walkthrough is cut off on phones; fix it, report host issues.", 'correction', None),
 '2026-09-28T20:55:51': ("Refresh the session timeline with the latest experiments.", 'request', None),
 '2026-09-28T21:10:19': ("Asks the agent to listen for messages sent from the pages.", 'request', None),
 '2026-09-28T21:18:33': ("Memory levels: light tints instead of dotted, striped backgrounds.", 'correction', None),
 '2026-09-28T21:23:25': ("Timeline: lead with what each message asked; timing in small print.", 'correction', None),
 '2026-09-28T21:32:37': ("Feedback for spacesheep: Talk messages should name the page they came from.", 'request', None),
 '2026-09-28T21:35:48': ("Timeline highlights should link the published pages they produced.", 'correction', None),
 '2026-09-28T21:51:56': ("Chip diagram: add a section that visualizes broadcast.", 'request', 'Q62'),
 '2026-09-28T23:00:32': ("Pages still say energies superseded: fold the newer findings in.", 'request', None),
 '2026-09-28T23:09:21': ("Heat per mm: which process the cited figure is for; 2x expected?", 'request', 'Q63'),
 '2026-09-29T01:38:03': ("Heat per mm: a light cyan background.", 'correction', None),
 '2026-09-29T03:41:01': ("Asks for a major pass: lab fixes, NoC validation, to-do, timeline committed.", 'request', None),
 '2026-09-29T04:14:32': ("Next: prototype a sparse-parity solver, toy sizes first, then scalable on-chip.", 'request', None),
}


# inputs that are mostly pasted or templated text although under 2000 chars (typing capped in the adjusted variant)
LIKELY_PASTE = {'2026-09-20T20:51:16',   # a templated settings-fix prompt
                '2026-09-25T19:56:33'}   # carries pasted terminal output


def slash_chars(s):
    name = re.search(r'<command-name>(.*?)</command-name>', s, re.S)
    args = re.search(r'<command-args>(.*?)</command-args>', s, re.S)
    return len((name.group(1) if name else '').strip()) + (1 + len(args.group(1).strip()) if args and args.group(1).strip() else 0)


def T(s):
    return datetime.fromisoformat(s.replace('Z', '+00:00'))


def iso(dt):
    return dt.astimezone(timezone.utc).strftime('%Y-%m-%dT%H:%M:%S.') + f'{dt.microsecond // 1000:03d}Z'


def pdt(dt):
    return dt.astimezone(TZ).strftime('%Y-%m-%d %H:%M:%S %Z')


def text_of(c):
    """(text, n_images) of a message content (str or block list)."""
    if isinstance(c, str):
        return c, 0
    parts, imgs = [], 0
    for x in c or []:
        if x.get('type') == 'text':
            parts.append(x.get('text', ''))
        elif x.get('type') == 'image':
            imgs += 1
    return '\n'.join(parts), imgs


def words(s):
    return len(re.findall(r'\S+', s))


def origin_kind(o):
    return (o or {}).get('kind')


PROMPT_KIND = {'human': 'human', 'task-notification': 'task-notification', 'peer': 'agent-message'}

# a message the owner sent from a published page's Talk tab, relayed by a monitor as a task notification
TALK_RX = re.compile(r'<event>\s*(\{.*?\})\s*</event>', re.S)
talk_ids = set()


def talk_message(s):
    """(id, message length) of an owner's spacesheep Talk message in a task notification, else None."""
    if not isinstance(s, str) or 'spacesheep_talk' not in s:
        return None
    m = TALK_RX.search(s)
    try:
        ev = json.loads(m.group(1)) if m else None
    except ValueError:
        ev = None
    if ev is None:
        # the monitor cuts a long event short ("...(truncated)"), which leaves the JSON unterminated: read its fields
        body = re.search(r'<event>\s*(\{.*)', s, re.S)
        if body:
            b = body.group(1)
            talk, frm = re.search(r'"spacesheep_talk"\s*:\s*true', b), re.search(r'"from"\s*:\s*"([^"]*)"', b)
            mid, msg = re.search(r'"id"\s*:\s*(\d+)', b), re.search(r'"message"\s*:\s*"((?:[^"\\]|\\.)*)', b)
            if talk and frm and mid and msg:
                ev = {'spacesheep_talk': True, 'from': frm.group(1), 'id': int(mid.group(1)),
                      'message': re.sub(r'\.\.\.\(truncated\)\s*(?:</event>.*)?$', '', msg.group(1), flags=re.S)}
    if not isinstance(ev, dict) or ev.get('spacesheep_talk') is not True or not ev.get('message') \
            or not str(ev.get('from', '')).startswith('the account owner'):
        return None
    return ev.get('id'), len(ev['message'])

# What a foreground tool call waited on, by its command. 'watch': a loop that only watched the agent's own workflows or
# subagents (their journals, transcripts or output files); the subagents' own hours already count that time, so a
# gap spent only in such loops is idle for the main agent. 'lab': a card run or a lab machine (a loop on a run's end,
# pgrep, an ssh command, a claims-v3 queue). 'other': anything else (builds, analyses, a call held by a prompt).
WATCH_RX = re.compile(r'/subagents/workflows/|/subagents/[\w-]+\.jsonl|journal\.jsonl|scratchpad/(audit|validate2)\b')
LAB_RX = re.compile(r'aifoundry[123]|pgrep|ettelem|claims-v3|run_\w+\.(sh|py)|horace|ablation|enercat|reruns|/done\b|'
                    r'run\.log|_host\b|_launcher\b|it_test|smokes')


def tool_class(name, inp):
    if name != 'Bash':
        return 'other'
    c = (inp or {}).get('command') or ''
    if WATCH_RX.search(c) and not LAB_RX.search(c):
        return 'watch'
    return 'lab' if LAB_RX.search(c) else 'other'


# ---------------------------------------------------------------- stream the transcript
human = []            # human inputs
enqueue_ts = {}       # prompt text[:200] -> first enqueue timestamp (send time of queued messages)
absorbed_ts = {}      # prompt text[:200] -> queue 'remove absorbed_mid_turn' timestamp (when the agent took it in)
last_enqueue_ts = None
asst_text = {}        # message.id -> dict(first, last, text)
msgs = {}             # message.id -> dict(ts, model, usage, tool_ids, stop)
events = []           # activity events for busy intervals: (dt, kind, payload)
ask_ids = {}          # AskUserQuestion tool_use id -> question words
order_violations = 0
last_dt = None
n_lines = 0
bad_lines = 0
first_ts = last_ts = None
turn_duration_ms = 0
n_turn_duration = 0
compactions = []
refusals = []
api_errors = []
SKIP_SYS = {'away_summary', 'bridge_status', 'local_command'}
presence = []         # weak signals that the human looked at the session (no content kept)
rate_limits = []      # synthetic 429 messages: the agent stopped until the quota reset
tool_kind = {}        # tool_use id -> 'watch' | 'lab' | 'other' (tool_class)
cut = T(CUTOFF) if CUTOFF else None
past_cut = False

with open(MAIN) as f:
    for line in f:
        try:
            e = json.loads(line)
        except Exception:
            if not past_cut:
                n_lines += 1
                bad_lines += 1
            continue
        t = e.get('type')
        ts = e.get('timestamp')
        dt = T(ts) if ts else None
        if cut is not None and (past_cut or (dt is not None and dt > cut)):
            past_cut = past_cut or dt is not None
            continue
        n_lines += 1
        if dt is not None:
            if first_ts is None:
                first_ts = dt
            last_ts = max(last_ts, dt) if last_ts else dt
            if t in ('assistant', 'user', 'attachment', 'system'):
                if last_dt and dt < last_dt - timedelta(seconds=1):
                    order_violations += 1
                last_dt = dt

        if t == 'queue-operation' and e.get('operation') == 'enqueue':
            c = e.get('content')
            if isinstance(c, str):
                enqueue_ts.setdefault(c[:200], ts)
            last_enqueue_ts = ts
        elif t == 'queue-operation' and e.get('operation') == 'remove' and e.get('reason') == 'absorbed_mid_turn':
            c = e.get('content')
            absorbed_ts[c[:200] if isinstance(c, str) else None] = ts

        elif t == 'assistant':
            m = e['message']
            mid = m.get('id')
            rec = msgs.get(mid)
            if rec is None:
                rec = msgs[mid] = {'ts': dt, 'last': dt, 'model': m.get('model'), 'usage': m.get('usage') or {},
                                   'tool_ids': set(), 'stop': None}
            rec['last'] = dt
            if m.get('stop_reason'):
                rec['stop'] = m['stop_reason']
            tool_ids = []
            for c in m.get('content') or []:
                if c.get('type') == 'tool_use':
                    rec['tool_ids'].add(c['id'])
                    tool_ids.append(c['id'])
                    tool_kind[c['id']] = tool_class(c.get('name'), c.get('input'))
                    if c.get('name') == 'AskUserQuestion':
                        q = c.get('input', {})
                        ask_ids[c['id']] = words(json.dumps(q))
                elif c.get('type') == 'text':
                    a = asst_text.setdefault(mid, {'first': dt, 'last': dt, 'text': ''})
                    a['last'] = dt
                    a['text'] += '\n' + c.get('text', '')
            if m.get('stop_reason') == 'refusal':
                refusals.append(ts)
            if e.get('isApiErrorMessage'):
                api_errors.append(ts)
            if e.get('error') == 'rate_limit':
                txt = ' '.join(c.get('text', '') for c in m.get('content') or [] if c.get('type') == 'text')
                rate_limits.append({'ts': ts, 'pdt': pdt(dt), 'message': txt.strip()[:120]})
            events.append((dt, 'assistant', {'mid': mid, 'tools': tool_ids, 'stop': m.get('stop_reason')}))

        elif t == 'user':
            c = e['message'].get('content')
            ok = origin_kind(e.get('origin'))
            if isinstance(c, list) and any(x.get('type') == 'tool_result' for x in c):
                ids = [x.get('tool_use_id') for x in c if x.get('type') == 'tool_result']
                events.append((dt, 'tool_result', {'ids': ids}))
                for x in c:
                    if x.get('type') == 'tool_result' and x.get('tool_use_id') in ask_ids:
                        cc = x.get('content')
                        s = cc if isinstance(cc, str) else text_of(cc)[0]
                        mm = re.search(r'"=\s*"(.*)"', s, re.S)
                        ans = mm.group(1) if mm else s
                        human.append({'dt': dt, 'kind': 'question-answer', 'source': 'AskUserQuestion',
                                      'chars': len(ans), 'images': 0, 'read_words_override': ask_ids[x['tool_use_id']]})
                continue
            s, imgs = text_of(c)
            if ok == 'human':
                sent = enqueue_ts.get(s[:200]) if e.get('promptSource') == 'queued' else None
                human.append({'dt': T(sent) if sent else dt, 'kind': 'prompt', 'source': e.get('promptSource'),
                              'chars': len(s), 'images': imgs})
                events.append((dt, 'prompt', {'kind': 'human'}))
            elif ok in PROMPT_KIND:
                events.append((dt, 'prompt', {'kind': PROMPT_KIND[ok]}))
                tk = talk_message(s) if ok == 'task-notification' else None
                if tk and tk[0] not in talk_ids:
                    talk_ids.add(tk[0])
                    human.append({'dt': dt, 'kind': 'talk', 'source': 'spacesheep-talk', 'chars': tk[1], 'images': 0})
            elif e.get('isCompactSummary'):
                events.append((dt, 'prompt', {'kind': 'compact-continuation'}))
            elif isinstance(s, str) and s.startswith('<command-name>'):
                # a local slash command typed by the human (e.g. /permissions); the stdout entry is skipped
                human.append({'dt': dt, 'kind': 'slash-command', 'source': 'typed', 'chars': slash_chars(s), 'images': 0})
            elif isinstance(s, str) and s.strip() == '[Request interrupted by user]':
                human.append({'dt': dt, 'kind': 'interrupt', 'source': 'keypress', 'chars': 0, 'images': 0})
                events.append((dt, 'prompt', {'kind': 'interrupt'}))
            elif s.startswith('<local-command-stdout>'):
                pass
            else:
                events.append((dt, 'meta', {'kind': 'meta' if e.get('isMeta') else 'other'}))

        elif t == 'attachment':
            a = e.get('attachment') or {}
            if a.get('type') == 'queued_command':
                ok = origin_kind(a.get('origin'))
                s, imgs = text_of(a.get('prompt'))
                k = PROMPT_KIND.get(ok) or ('task-notification' if a.get('commandMode') == 'task-notification' else 'other')
                pr = a.get('prompt')
                ab = absorbed_ts.pop(pr[:200] if isinstance(pr, str) else None, None)
                ab_dt = T(ab) if ab else dt
                if ok == 'human':
                    human.append({'dt': T(a.get('timestamp') or ts), 'kind': 'midturn', 'source': 'queued',
                                  'chars': len(s), 'images': imgs, 'absorbed_at': ab_dt})
                tk = talk_message(s) if k == 'task-notification' else None
                if tk and tk[0] not in talk_ids:
                    talk_ids.add(tk[0])
                    human.append({'dt': T(a.get('timestamp') or ts), 'kind': 'talk', 'source': 'spacesheep-talk',
                                  'chars': tk[1], 'images': 0, 'absorbed_at': ab_dt})
                # the entry's own timestamp is the send time; the agent took the input in at ab_dt
                events.append((ab_dt, 'midturn', {'kind': k}))
            else:
                events.append((dt, 'attachment', {'type': a.get('type')}))

        elif t == 'system':
            st = e.get('subtype')
            if st == 'local_command':
                s = e.get('content') or ''
                if s.startswith('<command-name>'):
                    human.append({'dt': dt, 'kind': 'slash-command', 'source': 'typed', 'chars': slash_chars(s), 'images': 0})
                continue
            if st in ('away_summary', 'bridge_status'):
                presence.append({'ts': ts, 'pdt': pdt(dt), 'type': 'away-recap' if st == 'away_summary' else 'remote-control-connected'})
            if st in SKIP_SYS:
                continue
            if st == 'turn_duration':
                turn_duration_ms += e.get('durationMs') or 0
                n_turn_duration += 1
            if st == 'compact_boundary':
                md = e.get('compactMetadata') or {}
                compactions.append({'ts': ts, 'pdt': pdt(dt), 'pre_tokens': md.get('preTokens'),
                                    'post_tokens': md.get('postTokens'), 'duration_ms': md.get('durationMs')})
            events.append((dt, 'system', {'subtype': st}))

# ---------------------------------------------------------------- human inputs
human.sort(key=lambda h: h['dt'])
text_msgs = sorted(asst_text.items(), key=lambda kv: kv[1]['last'])
credited = set()
out_h = []
unknown = []
for i, h in enumerate(human, 1):
    dt = h['dt']
    key = dt.astimezone(timezone.utc).strftime('%Y-%m-%dT%H:%M:%S')
    summ = SUMMARIES.get(key)
    if summ is None:
        unknown.append(key)
        summ = (None, None, None)
    # reading: words of the latest assistant message with text that finished before this input, if not already credited
    read_words, read_src = 0, None
    if 'read_words_override' in h:
        read_words, read_src = h['read_words_override'], 'question'
    elif h['kind'] not in ('interrupt', 'talk'):   # a Talk message is written on a page, not after reading the session
        prev = None
        for mid, a in text_msgs:
            if a['last'] < dt:
                prev = (mid, a)
            else:
                break
        if prev and prev[0] not in credited:
            credited.add(prev[0])
            read_words, read_src = words(prev[1]['text']), prev[0]
    read_s = min(READ_CAP_S, read_words / READ_WPM * 60)
    type_s = 0 if h['kind'] == 'interrupt' else max(TYPE_MIN_S, h['chars'] / TYPE_CPM * 60)
    if h['kind'] == 'interrupt':
        type_s = 2
    likely_paste = h['chars'] > 2000 or key in LIKELY_PASTE
    type_s_adj = min(type_s, PASTE_TYPING_CAP_S) if likely_paste else type_s
    out_h.append({
        'n': i, 'ts': iso(dt), 'pdt': pdt(dt), 'kind': h['kind'], 'source': h['source'],
        'chars': h['chars'], 'images': h['images'],
        'summary': summ[0], 'category': summ[1], 'request_id': summ[2],
        'absorbed_mid_turn_at': iso(h['absorbed_at']) if h.get('absorbed_at') else None,
        'read_words': read_words, 'read_s': round(read_s, 1), 'type_s': round(type_s, 1),
        'active_s': round(read_s + type_s, 1), 'likely_paste': likely_paste,
        'active_s_paste_adjusted': round(read_s + type_s_adj, 1),
    })

# engagement sessions
sessions = []
for h in out_h:
    dt = T(h['ts'])
    if sessions and (dt - T(sessions[-1]['last_ts'])).total_seconds() < ENGAGE_GAP_S:
        s = sessions[-1]
        s['last_ts'] = h['ts']; s['n'] += 1; s['active_s'] += h['active_s']; s['msgs'].append(h['n'])
        s['active_s_paste_adjusted'] += h['active_s_paste_adjusted']
    else:
        sessions.append({'first_ts': h['ts'], 'last_ts': h['ts'], 'n': 1, 'active_s': h['active_s'],
                         'active_s_paste_adjusted': h['active_s_paste_adjusted'], 'msgs': [h['n']],
                         'lead_s': h['active_s']})
for k, s in enumerate(sessions, 1):
    start = T(s['first_ts']) - timedelta(seconds=s.pop('lead_s'))
    end = T(s['last_ts'])
    s.update({'id': k, 'start_est': iso(start), 'start_pdt': pdt(start), 'end': s['last_ts'], 'end_pdt': pdt(end),
              'span_s': round((end - start).total_seconds(), 1), 'active_s': round(s['active_s'], 1),
              'active_s_paste_adjusted': round(s['active_s_paste_adjusted'], 1)})

cat_counts = collections.Counter(h['category'] for h in out_h)
kind_counts = collections.Counter(h['kind'] for h in out_h)
human_by_day = collections.OrderedDict()
for h in out_h:
    d = T(h['ts']).astimezone(TZ).strftime('%Y-%m-%d')
    r = human_by_day.setdefault(d, {'n': 0, 'chars': 0, 'active_s': 0.0, 'active_s_paste_adjusted': 0.0})
    r['n'] += 1; r['chars'] += h['chars']; r['active_s'] += h['active_s']; r['active_s_paste_adjusted'] += h['active_s_paste_adjusted']
for r in human_by_day.values():
    r['active_s'] = round(r['active_s'], 1); r['active_s_paste_adjusted'] = round(r['active_s_paste_adjusted'], 1)

# pre-session transcript (2e4feded): count only
pre = []
try:
    with open(PRE) as f:
        for line in f:
            e = json.loads(line)
            if e.get('type') == 'user' and origin_kind(e.get('origin')) == 'human':
                pre.append({'ts': e['timestamp'], 'pdt': pdt(T(e['timestamp'])), 'chars': len(text_of(e['message']['content'])[0]),
                            'summary': 'Lists files (a two-letter shell command) before the session.'})
except FileNotFoundError:
    pass

human_json = {
    'source': os.path.basename(MAIN), 'generated_utc': iso(datetime.now(timezone.utc)), 'timezone': 'America/Los_Angeles',
    'transcript_first_ts': iso(first_ts), 'transcript_last_ts': iso(last_ts),
    'rules': {
        'what_counts': ("Human inputs = (a) user entries with origin.kind=='human' (typed at the prompt or delivered via the "
                        "queue from Remote Control); (b) queued_command attachments with origin.kind=='human' (messages sent "
                        "while the agent was working and absorbed mid-turn; timestamp = when sent, absorbed_mid_turn_at = when "
                        "the agent saw them); (c) local slash commands (/remote-control, /mcp, /permissions); (d) the "
                        "AskUserQuestion answers; (e) the one Esc interrupt; (f) the owner's messages from a published "
                        "page's Talk tab (spacesheep Talk), relayed as monitor task notifications whose event has "
                        "spacesheep_talk true and is from the account owner, counted once per message id. Excluded: tool "
                        "results, other task notifications, "
                        "agent-to-agent (peer) messages, system reminders, compaction summaries, isMeta injections. No "
                        "'user sent a new message while you were working' tool-result text exists in this transcript; mid-turn "
                        "messages appear only as queued_command attachments."),
        'timestamp': "For queued prompts, the matching queue-operation enqueue time (= send time); otherwise the entry time.",
        'typing_s': f"max({TYPE_MIN_S} s, chars / {TYPE_CPM} chars-per-minute); interrupt = 2 s; images not counted.",
        'talk': "a Talk message is credited no reading time (it is written on a page, not after reading the session)",
        'read_s': (f"words of the latest assistant message (by message.id) containing text that finished before the input, "
                   f"/ {READ_WPM} wpm, capped at {READ_CAP_S // 60} min; each assistant message is credited to at most one human "
                   f"input (no double counting); for the AskUserQuestion answer, the words of the question and options."),
        'active_s': 'read_s + typing_s',
        'active_s_paste_adjusted': (f"same, but likely-pasted inputs (over 2000 chars, plus two shorter ones that are a "
                                    f"template and pasted terminal output) have typing capped at {PASTE_TYPING_CAP_S // 60} min"),
        'engagement_sessions': (f"runs of inputs with gaps < {ENGAGE_GAP_S // 60} min; start_est = first input time minus "
                                f"that input's active_s; end = last input time"),
        'summaries': "hand-written, <= 12 words, no names of other people, credentials or access paths",
        'categories': "request, correction, approval/answer, question, status",
    },
    'counts': {'inputs': len(out_h), 'by_kind': dict(kind_counts), 'by_category': dict(cat_counts),
               'engagement_sessions': len(sessions), 'unsummarised': unknown},
    'totals': {'chars': sum(h['chars'] for h in out_h),
               'read_s': round(sum(h['read_s'] for h in out_h), 1), 'type_s': round(sum(h['type_s'] for h in out_h), 1),
               'active_s': round(sum(h['active_s'] for h in out_h), 1),
               'active_s_paste_adjusted': round(sum(h['active_s_paste_adjusted'] for h in out_h), 1),
               'engagement_span_s': round(sum(s['span_s'] for s in sessions), 1)},
    'by_day_pdt': human_by_day,
    'messages': out_h,
    'engagement_sessions': sessions,
    'presence_signals': {'note': ("weak signals only: 'away-recap' = Claude Code wrote a 'while you were away' recap "
                                  "(generated when the user returns to an idle session); 'remote-control-connected' = "
                                  "a Remote Control bridge came up"), 'events': presence},
    'pre_session_transcript': {'file': os.path.basename(PRE), 'human_inputs': pre,
                               'note': 'separate 3-second session just before this one; not part of the timeline'},
}

# ---------------------------------------------------------------- main agent busy intervals
events.sort(key=lambda x: x[0])
pending = set()
intervals = []
cur = None


def new_interval(ev, trigger=None):
    return {'start': ev[0], 'end': ev[0], 'n_events': 0, 'mids': set(), 'tool_ids': set(),
            'prompts': collections.Counter(), 'midturn': collections.Counter(), 'trigger': trigger,
            'active_s': 0.0, 'tool_wait_s': 0.0, 'tool_wait_lab_s': 0.0, 'model_wait_s': 0.0, 'compaction_s': 0.0}


watch_gaps = []       # gaps >= 3 min spent only in loops watching the agent's own workflows/subagents (idle)


gap_hist = collections.Counter()
prev = None
turn_open = False
for ev in events:
    dt, kind, pl = ev
    if cur is None:
        cur = new_interval(ev)
    else:
        gap = (dt - prev[0]).total_seconds()
        cls = None
        if gap < GAP_S:
            cls = 'active'
        elif pending and all(tool_kind.get(x) == 'watch' for x in pending):
            cls = 'watch'              # only loops watching its own workflows: idle, like waiting in the background
        elif pending:
            cls = 'tool_wait'          # a foreground tool call is in flight (e.g. a blocking wait loop)
        elif (kind == 'system' and pl.get('subtype') == 'compact_boundary') or \
                (kind == 'prompt' and pl.get('kind') == 'compact-continuation'):
            cls = 'compaction'          # auto-compaction runs a summarisation call (75-200 s here)
        elif kind == 'assistant' and turn_open:
            cls = 'model_wait'         # API call in flight inside a turn (long generation / retries)
        if cls == 'watch':
            gap_hist['watch'] += 1
            watch_gaps.append((prev[0], dt))
            intervals.append(cur)
            cur = new_interval(ev, 'watch-loop')
        elif cls is None:
            gap_hist['idle'] += 1
            intervals.append(cur)
            cur = new_interval(ev)
        else:
            gap_hist[cls] += 1
            cur[{'active': 'active_s', 'tool_wait': 'tool_wait_s', 'model_wait': 'model_wait_s',
                 'compaction': 'compaction_s'}[cls]] += gap
            if cls == 'tool_wait' and any(tool_kind.get(x) == 'lab' for x in pending):
                cur['tool_wait_lab_s'] += gap
    cur['end'] = dt
    cur['n_events'] += 1
    if kind == 'assistant':
        cur['mids'].add(pl['mid'])
        for tid in pl['tools']:
            cur['tool_ids'].add(tid); pending.add(tid)
        turn_open = pl['stop'] not in ('end_turn', 'stop_sequence', 'refusal') or bool(pending)
    elif kind == 'tool_result':
        for tid in pl['ids']:
            pending.discard(tid)
        turn_open = True
    elif kind == 'prompt':
        cur['prompts'][pl['kind']] += 1
        if cur['trigger'] is None:
            cur['trigger'] = pl['kind']
        turn_open = True
    elif kind == 'midturn':
        cur['midturn'][pl['kind']] += 1
    elif kind == 'system' and pl.get('subtype') in ('turn_duration', 'stop_hook_summary'):
        turn_open = bool(pending)
    elif kind == 'meta':
        turn_open = True
    prev = ev
if cur:
    intervals.append(cur)

out_i = []
dropped = 0
for iv in intervals:
    if not iv['mids']:
        dropped += 1
        continue
    u = collections.Counter()
    models = collections.Counter()
    for mid in iv['mids']:
        for k in ('input_tokens', 'cache_creation_input_tokens', 'cache_read_input_tokens', 'output_tokens'):
            u[k] += msgs[mid]['usage'].get(k, 0) or 0
        models[msgs[mid]['model']] += 1
    trig = iv['trigger']
    if trig is None:
        trig = 'continuation'
    dur = (iv['end'] - iv['start']).total_seconds()
    out_i.append({
        'start': iso(iv['start']), 'end': iso(iv['end']), 'start_pdt': pdt(iv['start']), 'end_pdt': pdt(iv['end']),
        'duration_s': round(dur, 1), 'active_s': round(iv['active_s'], 1), 'tool_wait_s': round(iv['tool_wait_s'], 1),
        'tool_wait_lab_s': round(iv['tool_wait_lab_s'], 1),
        'model_wait_s': round(iv['model_wait_s'], 1), 'compaction_s': round(iv['compaction_s'], 1),
        'trigger': trig, 'prompts': dict(iv['prompts']), 'midturn_inputs': dict(iv['midturn']),
        'n_assistant_messages': len(iv['mids']), 'n_tool_calls': len(iv['tool_ids']), 'n_events': iv['n_events'],
        'tokens': dict(u), 'tokens_total': sum(u.values()), 'models': dict(models),
        'api_error_only': set(models) == {'<synthetic>'},
    })

# ---------------------------------------------------------------- tokens
KEYS = ('input_tokens', 'cache_creation_input_tokens', 'cache_read_input_tokens', 'output_tokens')


def blank():
    return {'messages': 0, **{k: 0 for k in KEYS}, 'total': 0}


def add(r, rec):
    r['messages'] += 1
    for k in KEYS:
        v = rec['usage'].get(k, 0) or 0
        r[k] += v; r['total'] += v


per_hour = collections.OrderedDict(); per_day = collections.OrderedDict(); per_model = {}
per_day_model = collections.OrderedDict()
totals = blank()
thinking_tokens = 0
cache_1h = cache_5m = 0
messages_rows = []
for mid, rec in sorted(msgs.items(), key=lambda kv: kv[1]['ts']):
    loc = rec['ts'].astimezone(TZ)
    h = loc.strftime('%Y-%m-%dT%H'); d = loc.strftime('%Y-%m-%d')
    add(per_hour.setdefault(h, blank()), rec); add(per_day.setdefault(d, blank()), rec)
    add(per_model.setdefault(rec['model'], blank()), rec); add(totals, rec)
    add(per_day_model.setdefault(d, {}).setdefault(rec['model'], blank()), rec)
    u = rec['usage']
    thinking_tokens += (u.get('output_tokens_details') or {}).get('thinking_tokens', 0) or 0
    cc = u.get('cache_creation') or {}
    cache_1h += cc.get('ephemeral_1h_input_tokens', 0) or 0; cache_5m += cc.get('ephemeral_5m_input_tokens', 0) or 0
    messages_rows.append([mid, iso(rec['ts']), rec['model'], u.get('input_tokens', 0) or 0,
                          u.get('cache_creation_input_tokens', 0) or 0, u.get('cache_read_input_tokens', 0) or 0,
                          u.get('output_tokens', 0) or 0, len(rec['tool_ids']), rec['stop']])

# busy seconds per PDT hour/day (interval overlap)
busy_hour = collections.Counter(); busy_day = collections.Counter()
for iv in out_i:
    s, e = T(iv['start']), T(iv['end'])
    cur_t = s
    while cur_t < e:
        loc = cur_t.astimezone(TZ)
        nxt = (loc.replace(minute=0, second=0, microsecond=0) + timedelta(hours=1)).astimezone(timezone.utc)
        seg_end = min(e, nxt)
        sec = (seg_end - cur_t).total_seconds()
        busy_hour[loc.strftime('%Y-%m-%dT%H')] += sec; busy_day[loc.strftime('%Y-%m-%d')] += sec
        cur_t = seg_end
for h, r in per_hour.items():
    r['busy_s'] = round(busy_hour.get(h, 0), 1)
for h, s in busy_hour.items():
    if h not in per_hour:
        per_hour[h] = {**blank(), 'busy_s': round(s, 1)}
per_hour = collections.OrderedDict(sorted(per_hour.items()))
for d, r in per_day.items():
    r['busy_s'] = round(busy_day.get(d, 0), 1)
    r['by_model'] = per_day_model[d]

# model runs (consecutive messages with the same model)
runs = []
for row in messages_rows:
    if not runs or runs[-1]['model'] != row[2]:
        runs.append({'model': row[2], 'first': row[1], 'last': row[1], 'messages': 0})
    runs[-1]['last'] = row[1]; runs[-1]['messages'] += 1

trig_counts = collections.Counter(i['trigger'] for i in out_i)
main_json = {
    'source': os.path.basename(MAIN), 'generated_utc': iso(datetime.now(timezone.utc)), 'timezone': 'America/Los_Angeles',
    'transcript_first_ts': iso(first_ts), 'transcript_last_ts': iso(last_ts), 'lines': n_lines, 'bad_lines': bad_lines, 'cutoff': CUTOFF,
    'rules': {
        'events': ("activity events = assistant entries, user entries (tool results, prompts), attachments (incl. mid-turn "
                   "queued inputs) and system entries except away_summary, bridge_status and local_command; "
                   "queue-operation, file-history and bookkeeping entries are ignored"),
        'busy_interval': (f"consecutive events < {GAP_S // 60} min apart are merged ('active_s'); a longer gap is also merged "
                          "when the agent is provably blocked: a foreground tool call is in flight ('tool_wait_s', e.g. a "
                          "blocking until-loop waiting on a card run), the model call is in flight inside an open turn "
                          "('model_wait_s'), or the gap ends at a compaction ('compaction_s'); any other gap >= 3 min is "
                          "idle (e.g. waiting for background agents/workflows or for the human). A gap in which the only "
                          "calls in flight are loops watching the agent's own workflows or subagents ('watch_waits') is "
                          "idle too: the subagents' hours count that time. 'tool_wait_lab_s' is the part of tool_wait_s "
                          "with a card run or lab-machine command in flight. Intervals with no assistant message are "
                          "dropped. Strict 3-minute-rule busy time = sum of active_s."),
        'trigger': ("kind of the first prompt entry in the interval: human, task-notification, agent-message, "
                    "compact-continuation, interrupt; 'watch-loop' after a watch gap; 'continuation' if none"),
        'tool_class': ("watch: a Bash command matching " + WATCH_RX.pattern + " and not the lab pattern; lab: matching "
                       + LAB_RX.pattern + "; other: the rest"),
        'tokens': ("message.usage summed over assistant entries deduped by message.id (streaming writes several entries "
                   "per message, all with identical usage); hour/day keys are PDT of the message's first entry"),
        'messages_columns': ['message_id', 'ts', 'model', 'input_tokens', 'cache_creation_input_tokens',
                             'cache_read_input_tokens', 'output_tokens', 'n_tool_calls', 'stop_reason'],
    },
    'counts': {'assistant_messages': len(msgs), 'assistant_entries': sum(1 for e in events if e[1] == 'assistant'),
               'tool_calls': sum(len(r['tool_ids']) for r in msgs.values()), 'busy_intervals': len(out_i),
               'intervals_dropped_no_assistant': dropped, 'triggers': dict(trig_counts), 'gap_classes': dict(gap_hist),
               'turn_duration_entries': n_turn_duration, 'refusal_stops': len(refusals), 'api_error_messages': len(api_errors),
               'compactions': len(compactions), 'timestamp_order_violations': order_violations},
    'totals': {**totals, 'thinking_tokens_in_output': thinking_tokens, 'cache_creation_1h': cache_1h,
               'cache_creation_5m': cache_5m,
               'busy_s': round(sum(i['duration_s'] for i in out_i), 1),
               'active_s_strict_3min': round(sum(i['active_s'] for i in out_i), 1),
               'tool_wait_s': round(sum(i['tool_wait_s'] for i in out_i), 1),
               'tool_wait_lab_s': round(sum(i['tool_wait_lab_s'] for i in out_i), 1),
               'watch_wait_s': round(sum((b - a).total_seconds() for a, b in watch_gaps), 1),
               'model_wait_s': round(sum(i['model_wait_s'] for i in out_i), 1),
               'compaction_s': round(sum(i['compaction_s'] for i in out_i), 1),
               'turn_duration_sum_s': round(turn_duration_ms / 1000, 1)},
    'per_model': per_model, 'model_runs': runs,
    'per_day_pdt': per_day, 'per_hour_pdt': per_hour,
    'compactions': compactions, 'refusal_stops': refusals, 'api_error_messages': api_errors,
    'rate_limit_stops': rate_limits,
    'busy_intervals': out_i,
    'watch_waits': [[iso(a), iso(b)] for a, b in watch_gaps],
    'messages': messages_rows,
}

with open(OUT + 'human.json', 'w') as f:
    json.dump(human_json, f, indent=1, default=str)
with open(OUT + 'main_agent.json', 'w') as f:
    json.dump(main_json, f, indent=1, default=str)

print('human inputs', len(out_h), dict(kind_counts), dict(cat_counts), 'unsummarised', unknown)
print('human totals', human_json['totals'])
print('engagement sessions', len(sessions))
print('assistant messages', len(msgs), 'intervals', len(out_i), 'dropped', dropped, dict(trig_counts), dict(gap_hist))
print('token totals', main_json['totals'])
print('per_model', {k: v['total'] for k, v in per_model.items()})
print('range', iso(first_ts), iso(last_ts), 'order violations', order_violations)
