#!/usr/bin/env python3
"""blind-v3-e212s3 step 2 (after the data commit is on GitHub main): the order check. Reads from the archived data folder (work/data-s3,
extracted from main's commit) only the session's own time records, never a measured value: the session log's lines up to its first run,
its last line, the meta file's claim / window / release / copy records, and the data commit's times from git. Decides the label by the
declaration's rule (DECLARED-blind-s3.md section 6):
    BLIND    when b1493082's push (2026-11-17 20:52:51 PST) and the declaration's logged time both precede the re-run's first card command
             (the first session-log line at or after the session start that touches the card; the session start, T0, the conservative bound);
    REPORTED otherwise.
Also: no line of the re-run's session log is older than b1493082's push.

    /usr/bin/python3 -I -B s02_order.py --folder <work/data-s3/.../2026-11-18-e212-mmsweep2-a2c0-S3> --lab <LAB> --main <sha>
                                        --declared '2026-11-18 14:10:50' --out <order.json>
"""
import argparse
import datetime as dt
import glob
import json
import os
import re
import subprocess

PUSH = dt.datetime(2026, 11, 17, 20, 52, 51)
TS = re.compile(r'^(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}) P[SD]T (.*)$')
CARD_WORDS = ('config start', 'sampler started', 'identity read', 'stop-path test', 'smoke ', 'run ', 'the opening rest')


def git(lab, *a):
    return subprocess.run(['git', '-C', lab] + list(a), capture_output=True, text=True, check=True).stdout


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--folder', required=True)
    ap.add_argument('--lab', required=True)
    ap.add_argument('--main', required=True)
    ap.add_argument('--declared', required=True)
    ap.add_argument('--out', required=True)
    a = ap.parse_args()
    F = os.path.abspath(a.folder)
    decl = dt.datetime.strptime(a.declared, '%Y-%m-%d %H:%M:%S')
    rel = os.path.relpath(F, F.split('/docs/reports/data/')[0]) if '/docs/reports/data/' in F else None
    res = {'folder': rel, 'main': a.main, 'b1493082_pushed': PUSH.strftime('%F %T') + ' PST', 'declared_logged': a.declared + ' PST'}
    # the data commit: the commit on main that added the folder, and every commit on main touching it
    log = git(a.lab, 'log', '--format=%H|%ci|%ai|%s', a.main, '--', rel).strip().splitlines()
    res['commits_touching_folder'] = [dict(zip(('sha', 'committer', 'author', 'subject'), ln.split('|', 3))) for ln in log]
    add = git(a.lab, 'log', '--diff-filter=A', '--format=%H|%ci', a.main, '--', rel).strip().splitlines()
    res['added_by'] = add[-1] if add else None
    # the session log (time records only: lines before the first run line, the first run line, the last line)
    logs = sorted(glob.glob(os.path.join(F, '**', 'session.log'), recursive=True))
    res['session_logs'] = [os.path.relpath(p, F) for p in logs]
    lines = []
    for p in logs:
        for ln in open(p, errors='replace'):
            m = TS.match(ln.rstrip('\n'))
            if m:
                lines.append((dt.datetime.strptime(m.group(1), '%Y-%m-%d %H:%M:%S'), m.group(2)))
    if lines:
        lines.sort(key=lambda x: x[0])
        t0 = next((t for t, s in lines if s.startswith('session start')), lines[0][0])
        card = [(t, s) for t, s in lines if t >= t0 and any(s.startswith(w) or w in s[:40] for w in CARD_WORDS)]
        first_card = card[0] if card else None
        first_run = next(((t, s) for t, s in lines if s.startswith('run ')), None)
        res.update({'n_timed_lines': len(lines), 'earliest_line': [lines[0][0].strftime('%F %T'), lines[0][1][:160]],
                    'session_start_T0': t0.strftime('%F %T'),
                    'first_card_command': ([first_card[0].strftime('%F %T'), first_card[1][:200]] if first_card else None),
                    'first_run_line': ([first_run[0].strftime('%F %T'), first_run[1][:120]] if first_run else None),
                    'last_line': [lines[-1][0].strftime('%F %T'), lines[-1][1][:200]],
                    'opening_lines_to_first_run': [[t.strftime('%F %T'), s[:200]] for t, s in lines if (first_run is None or t <= first_run[0])][:40],
                    'lines_older_than_b1493082_push': sum(1 for t, _ in lines if t < PUSH)})
        fc = first_card[0] if first_card else t0
        res['checks'] = {'push_before_first_card_command': PUSH < fc, 'declared_before_first_card_command': decl < fc,
                         'push_before_T0': PUSH < t0, 'declared_before_T0': decl < t0,
                         'no_session_line_older_than_push': res['lines_older_than_b1493082_push'] == 0}
        ok = all(res['checks'].values())
        res['label'] = 'BLIND' if ok else 'REPORTED'
    else:
        res['label'] = 'UNDECIDED: no timed session-log line found'
    # meta records (claim, window, release, copy), as the data lane wrote them
    for p in sorted(glob.glob(os.path.join(F, 'meta-*.json'))):
        m = json.load(open(p))
        res.setdefault('meta', {})[os.path.basename(p)] = {k: m.get(k) for k in ('label', 'sid', 'box', 'card', 'schedule', 'window', 'claim', 'release',
                                                                                  'copied', 'registration', 'host_words')}
    json.dump(res, open(a.out, 'w'), indent=1, sort_keys=True)
    print(json.dumps({k: res.get(k) for k in ('added_by', 'session_start_T0', 'first_card_command', 'first_run_line', 'last_line',
                                               'lines_older_than_b1493082_push', 'checks', 'label')}, indent=1))


if __name__ == '__main__':
    main()
