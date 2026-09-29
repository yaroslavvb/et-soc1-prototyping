#!/usr/bin/env python3
"""Extract the card runs that left no timestamped data file: the agents' own commands that ran a program on a card.

    TIMELINE_CUTOFF=2026-09-28T13:23:04Z tools/timeline/extract_card_calls.py

Streams the main agent's transcript line by line and keeps each foreground Bash call whose
command runs a program on a card, as the first word of one of its commands: a host program (..._host,
..._launcher), the runtime's it_test, the management service's -m/-n/-t queries, ettelem sampling, a
run_*.py / run_*.sh measurement script or a make with DEVICE=silicon. A call's span
is its tool_use to its tool_result, so it includes any build or copy in the same command: an upper bound on the time
the card was in use. The card is the machine the command ran on: aifoundry2 when local (the session's machine), else
the lab machine the command was sent to; on aifoundry1 the card is ET_DEVICES (card 0 when unset). Excluded: simulator runs, --help,
dry runs (V3_DRY=1), the text of heredocs that only write a script, and background calls (their card time is in
the data files or queue logs). Subagents are left out: their card work went through the logged claims-v3 queues
(agents that only write code may not reach a card), and their commands that match are analysis scripts named run_*
re-run from raw data. Writes card_calls.json to $TIMELINE_DIR:

  calls[]   [start_iso, end_iso, card, program] per call, program being the matched executable's name only (no
            arguments, paths or hosts)

build_timeline_data.py keeps the parts of these spans that no data file or queue log already covers.
"""
import json, os, re, sys
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import paths  # noqa: E402

MAIN = paths.MAIN
OUT = os.path.join(paths.ensure_tl(), 'card_calls.json')
CUTOFF = paths.CUTOFF

# a program that runs on a card, as the first word of a command (see command_words)
PROG = re.compile(r'^(?:\S*/)?(\w+_(?:host|launcher)|it_test\w*|run_\w+\.(?:py|sh))$')
SKIP = re.compile(r'sysemu|--help|-h 2>|V3_DRY=1|--dry-run')
HEREDOC = re.compile(r"<<-?\s*['\"]?(\w+)['\"]?[^\n]*\n.*?\n\s*\1\s*(?:\n|$)", re.S)
SPLIT = re.compile(r"&&|\|\||[;|&\n()'\"`]|\$\(|\bdo\b|\bthen\b|\belse\b")
PREFIX = {'timeout', 'nohup', 'nice', 'sudo', 'exec', 'time', 'env', 'bash', 'sh', 'python3', 'python', 'stdbuf', 'flock'}
SSH = re.compile(r'\bssh\b[^|;&\n]*?\b(?:\w+@)?(aifoundry[123])\b')


def T(s):
    return datetime.fromisoformat(s.replace('Z', '+00:00'))


def iso(dt):
    return dt.astimezone(timezone.utc).strftime('%Y-%m-%dT%H:%M:%S.') + f'{dt.microsecond // 1000:03d}Z'


def card_of(cmd):
    m = SSH.search(cmd)
    host = m.group(1) if m else 'aifoundry2'
    if host != 'aifoundry1':
        return host
    d = re.search(r'ET_DEVICES=(\d)', cmd)
    return 'aifoundry1-c' + (d.group(1) if d else '0')


def command_words(cmd):
    """The first word of every simple command in cmd, after wrappers (timeout 10, nohup, nice -n 5, flock -n LOCK,
    env assignments, bash/python3) are skipped; with the words that follow it."""
    for seg in SPLIT.split(cmd):
        w = seg.split()
        i = 0
        while i < len(w):
            t = w[i]
            if re.match(r'^\w+=', t) or t in PREFIX:
                i += 1
                # a wrapper's own options and arguments: timeout 10, nice -n 5, flock -n /run/lock/x.lock
                while i < len(w) and (w[i].startswith('-') or re.match(r'^[\d.]+[smh]?$', w[i]) or
                                      (t == 'flock' and w[i].startswith('/'))):
                    i += 1
                continue
            break
        if i < len(w):
            yield w[i], w[i + 1:]


def program(cmd):
    body = HEREDOC.sub('\n', cmd)       # a heredoc's text is a file being written, not a command being run
    if SKIP.search(body):
        return None
    for first, rest in command_words(body):
        m = PROG.match(first)
        if m:
            return m.group(1)
        base = first.rsplit('/', 1)[-1]
        if base == 'ettelem' and rest[:1] == ['sample']:
            return 'ettelem sample'
        if base == 'dev_mngt_service' and any(re.match(r'^-[mnt]$', x) for x in rest):
            return 'dev_mngt_service'
        if base == 'make' and any(x in ('DEVICE=silicon', '--device_type=silicon') for x in rest):
            return 'make (silicon)'
    return None


def scan(path, cut):
    pend, out = {}, []
    with open(path, encoding='utf-8', errors='replace') as fh:
        for line in fh:
            if 'tool_use' not in line and 'tool_result' not in line:
                continue
            try:
                o = json.loads(line)
            except ValueError:
                continue
            ts = o.get('timestamp')
            if not ts or (cut and T(ts) > cut):
                continue
            ct = (o.get('message') or {}).get('content')
            if not isinstance(ct, list):
                continue
            for b in ct:
                if b.get('type') == 'tool_use' and b.get('name') == 'Bash':
                    inp = b.get('input') or {}
                    if inp.get('run_in_background'):
                        continue
                    cmd = inp.get('command') or ''
                    prog = program(cmd)
                    if prog:
                        pend[b['id']] = (T(ts), card_of(cmd), prog)
                elif b.get('type') == 'tool_result' and b.get('tool_use_id') in pend:
                    s, card, prog = pend.pop(b['tool_use_id'])
                    e = max(T(ts), s)
                    out.append([iso(s), iso(e), card, prog])
    return out


if __name__ == '__main__':
    cut = T(CUTOFF) if CUTOFF else None
    calls = sorted(scan(MAIN, cut))
    out = {'generated': iso(datetime.now(timezone.utc)), 'cutoff': CUTOFF,
           'rule': ' '.join(__doc__.split('\n\n')[2].split()),
           'cols': ['start', 'end', 'card', 'program'], 'calls': calls}
    json.dump(out, open(OUT, 'w'), separators=(',', ':'), ensure_ascii=False)
    by = {}
    for c in calls:
        k = (c[0][:10], c[2])
        by[k] = by.get(k, 0) + (T(c[1]) - T(c[0])).total_seconds()
    print('wrote', OUT, len(calls), 'calls')
    for k in sorted(by):
        print(k, round(by[k] / 60, 1), 'min')
