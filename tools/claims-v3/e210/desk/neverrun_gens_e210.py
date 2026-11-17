#!/usr/bin/env python3
"""E210 (Q202, lane fix-e210, Tue 17 Nov 2026, before any E210 datum): the instrument of E210.md amendment A1 item 1 - which GEMM value strings
are host LAUNCH RECORDS (a GEMM that ran) and which are not, for both conditions of the registered never-run rule. No card. Standard library
only; it imports nothing of the lab, so it runs on any box from stdin, as the registered scanner does.

    python3 -I -B neverrun_gens_e210.py scan LABEL TOP [TOP ...] [--exclude=DIR ...] > gens.json     (on another box: the same, from stdin)

WHY (verify-e210's finding 1, kit-e210's finding 1): the registered rule (desk/neverrun_e210.py, unchanged) reads a law as run when a GEMM value
string ANYWHERE (i) names a generator rgm136 does not draw (then all nine laws at once) or (ii) names a tile file that passes the law outside
the desk folders, whatever file the string is in. On Tue 17 Nov 2026 such strings were not runs: (i) E211's host-refusal checks
("gemmLn2x2x2:noise:...", in shell scripts), which a GEMM host refuses before any kernel launch (rgm136 throws "unknown gen" while filling its
operand pools: it draws only randn, sparse50, sparse25 and e37 and reads tile files); (ii) E212's planned arms (its arms.json and session
schedules, copied into the round's folders), which name two of E212's own tiles that pass E210's signs and highmant8 laws and had not run.
A1 item 1 counts, for both conditions, only a string inside a HOST LAUNCH RECORD; the registered rule's verdict is kept and quoted beside.
WHAT IS READ: exactly the registered scanner's files (the same walk: every file under a top, directories holding a .git entry skipped below the
top, the --exclude folders left out, 2,048-byte files skipped as tiles, text files by the same extensions and size cap, gzip read through) and,
in each line holding "gemm", exactly the registered scanner's two patterns (a record's "values" field; a command's --values). Each string is
classed:
  LAUNCH RECORD  matched as a record's "values" field on a line that holds "SPARSITY" (the host's record of a launch: "SPARSITY {...}") or a
                 "launch" field (a record split from its prefix by a runtime line, read as a record all the same: the conservative side);
  ELSEWHERE      everything else: a command line, an argv list, a script, a document, a plan or a schedule (never a run: a GEMM that ran
                 leaves its launch records, and a host refuses a generator it does not draw before any launch).
OUTPUT (JSON): the scan's own counts; per generator not the host's own (randn, sparse50, sparse25, e37, tiles), the number of strings of each
class and up to 50 files of each class with up to 2 strings each ("non_host"); and per tile file name (the basename, as the registered report
matches names) the number of strings of each class that name it ("tile_names_launch_records", "tile_names_elsewhere"). desk/neverrun_card_e210.py
reads it (steps 6n and 12n) beside the registered report. SPDX-License-Identifier: Apache-2.0
"""
import gzip
import json
import os
import re
import socket
import sys
import time

RE_REC_VAL = re.compile(r'"values"\s*:\s*"(gemm[A-Za-z0-9]+:[^"]*)"')           # the registered scanner's two patterns, verbatim
RE_CMD_VAL = re.compile(r'--values"?\s*,?\s*"?(gemm[A-Za-z0-9]+:[^"\s]*)')
MAX_BYTES = 400 * 2 ** 20
TEXT_EXT = ('.json', '.jsonl', '.log', '.txt', '.csv', '.md', '.sh', '.py', '.out', '.err', '.gz', '.tsv', '')
HOST_GENS = ('randn', 'sparse50', 'sparse25', 'e37', 'tiles')
RE_LAUNCH = re.compile(r'SPARSITY|"launch"\s*:')
MAX_FILES = 50


def parse_values(v):
    parts = v.split(':', 2)
    return parts[0], (parts[1] if len(parts) > 1 else ''), [f for f in (parts[2].split(',') if len(parts) > 2 else []) if f]


def read_lines(path):
    try:
        if os.path.getsize(path) > MAX_BYTES:
            return None
        if path.endswith('.gz'):
            with gzip.open(path, 'rt', errors='replace') as f:
                return f.read().splitlines()
        with open(path, 'r', errors='replace') as f:
            return f.read().splitlines()
    except Exception:
        return None


def scan(label, tops, excludes=()):
    t0 = time.time()
    res = {'label': label, 'host': socket.gethostname(), 'tops': tops, 'python': sys.version.split()[0], 'started_epoch': t0,
           'files_seen': 0, 'text_files_read': 0, 'gemm_strings': 0, 'skipped_git_dirs': 0, 'unreadable': 0, 'excludes': list(excludes),
           'excluded_dirs': 0, 'non_host': {}, 'tile_names_launch_records': {}, 'tile_names_elsewhere': {}}
    for top in tops:
        if not os.path.isdir(top):
            res.setdefault('missing_tops', []).append(top)
            continue
        for dirpath, dirs, files in os.walk(top):
            if dirpath != top and ('.git' in dirs or '.git' in files):
                res['skipped_git_dirs'] += 1
                dirs[:] = []
                continue
            if any(dirpath == x or dirpath.startswith(x.rstrip('/') + '/') for x in excludes):
                res['excluded_dirs'] += 1
                dirs[:] = []
                continue
            dirs[:] = [d for d in dirs if d != '.git']
            for fn in files:
                p = os.path.join(dirpath, fn)
                res['files_seen'] += 1
                try:
                    size = os.path.getsize(p)
                except OSError:
                    res['unreadable'] += 1
                    continue
                if size == 2048:
                    continue
                if os.path.splitext(fn)[1].lower() not in TEXT_EXT:
                    continue
                lines = read_lines(p)
                if lines is None:
                    res['unreadable'] += 1
                    continue
                res['text_files_read'] += 1
                for line in lines:
                    if 'gemm' not in line:
                        continue
                    launch_line = RE_LAUNCH.search(line) is not None
                    for rx in (RE_REC_VAL, RE_CMD_VAL):
                        for m in rx.finditer(line):
                            v = m.group(1).rstrip("',]")
                            res['gemm_strings'] += 1
                            arm, gen, fl = parse_values(v)
                            cls = 'launch_records' if (rx is RE_REC_VAL and launch_line) else 'elsewhere'
                            tn = res['tile_names_' + cls]
                            for f in fl:
                                b = os.path.basename(f)
                                tn[b] = tn.get(b, 0) + 1
                            if gen in HOST_GENS:
                                continue
                            g = res['non_host'].setdefault(gen, {'launch_records': 0, 'elsewhere': 0, 'files_launch_records': {}, 'files_elsewhere': {}})
                            g[cls] += 1
                            fs = g['files_' + cls]
                            if p in fs or len(fs) < MAX_FILES:
                                lst = fs.setdefault(p, [])
                                if len(lst) < 2 and v not in lst:
                                    lst.append(v[:200])
    res['seconds'] = round(time.time() - t0, 1)
    return res


def main():
    if len(sys.argv) >= 4 and sys.argv[1] == 'scan':
        args = sys.argv[3:]
        tops = [x for x in args if not x.startswith('--exclude=')]
        excl = [x.split('=', 1)[1] for x in args if x.startswith('--exclude=')]
        json.dump(scan(sys.argv[2], tops, excl), sys.stdout, indent=1, sort_keys=True)
        return 0
    print(__doc__)
    return 2


if __name__ == '__main__':
    sys.exit(main())
