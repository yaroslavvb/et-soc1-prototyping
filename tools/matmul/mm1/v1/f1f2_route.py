#!/usr/bin/env python3
"""The route F1 and F2 read from the lab at run time, recorded with sha256 and checked. Desk.

    /usr/bin/python3 -I -B f1f2_route.py --repo <the lab at GitHub main> --out <dir>     runs f1f2_blind_day.py's main into <dir> under an audit
        hook, checks its two outputs equal this folder's frozen out/f1f2_blind_day.json and .csv byte for byte, and writes f1f2_route.json into
        <dir>: every file the run read under --repo outside this folder (modules and data), each with its sha256
    /usr/bin/python3 -I -B f1f2_route.py --repo <lab> --check [<route json>]      compares every file in the record (default out/f1f2_route.json)
        with --repo's copy; prints each difference and exits 3 if any

Why (verify-mm1v1 finding 4, Mon 16 Nov 2026): F1 and F2 are E206's registered routes, imported from the lab at run time and not vendored;
forecast_e206.py was unpinned and its imports (E190's route, ledger v3) and their data were recorded nowhere. f1f2_blind_day.py now pins its three
named files by full sha256; this file records the rest of the route. The frozen F1/F2 forecasts themselves are fixed by their sha256 (README 1).
Run with -I -B (no bytecode written, so every module is read from its source and its read is seen by the hook).
SPDX-License-Identifier: Apache-2.0
"""
import argparse
import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
FROZEN = ('f1f2_blind_day.json', 'f1f2_blind_day.csv')


def sha(path):
    return hashlib.sha256(open(path, 'rb').read()).hexdigest()


def under(p, top):
    top = os.path.join(os.path.abspath(top), '')
    return os.path.abspath(p).startswith(top)


def record(repo, out):
    opened = set()

    def hook(event, args):
        if event != 'open' or not args:
            return
        path, mode = args[0], (args[1] if len(args) > 1 else None)
        if not isinstance(path, (str, bytes, os.PathLike)):
            return
        if isinstance(mode, str) and any(c in mode for c in 'wax+'):
            return
        try:
            p = os.path.abspath(os.fsdecode(path))
        except Exception:  # noqa: BLE001
            return
        if under(p, repo) and not under(p, HERE) and not under(p, out) and os.path.isfile(p):
            opened.add(p)
    sys.addaudithook(hook)
    sys.path.insert(0, HERE)
    import f1f2_blind_day as FB
    argv = sys.argv
    sys.argv = ['f1f2_blind_day.py', '--repo', repo, '--out', out]
    try:
        FB.main()
    finally:
        sys.argv = argv
    mods = {}
    for name, m in list(sys.modules.items()):
        f = getattr(m, '__file__', None)
        if f and under(f, repo) and not under(f, HERE):
            mods[os.path.abspath(f)] = name
    files = sorted(opened | set(mods))
    route = [{'path': os.path.relpath(p, repo), 'sha256': sha(p), 'bytes': os.path.getsize(p), 'how': ('module ' + mods[p]) if p in mods else 'data'}
             for p in files]
    eq = {n: sha(os.path.join(out, n)) == sha(os.path.join(HERE, 'out', n)) for n in FROZEN}
    pins = {k: v for k, v in FB.PIN.items()}
    res = {'what': "every file F1 and F2 (E206's registered routes, f1f2_blind_day.py) read from the lab at run time, outside MM1-v1's folder, with "
                   "its sha256 (the route is not vendored; f1f2_blind_day.py pins the three files it names)",
           'answers': 'verify-mm1v1 finding 4 (Mon 16 Nov 2026)', 'pinned_in_code': pins, 'n_files': len(route), 'route': route,
           'outputs_equal_frozen': eq, 'python': sys.version.split()[0]}
    json.dump(res, open(os.path.join(out, 'f1f2_route.json'), 'w'), indent=1, sort_keys=True)
    print(f'route: {len(route)} files under --repo outside this folder; modules {sum(1 for r in route if r["how"] != "data")}, '
          f'data {sum(1 for r in route if r["how"] == "data")}')
    for r in route:
        print(f"  {r['sha256'][:16]} {r['bytes']:>9} {r['how']:<28} {r['path']}")
    print('outputs equal the frozen out/ files:', eq)
    if not all(eq.values()):
        sys.exit(4)


def check(repo, rj):
    rec = json.load(open(rj))
    bad = []
    for r in rec['route']:
        p = os.path.join(repo, r['path'])
        got = sha(p) if os.path.isfile(p) else None
        if got != r['sha256']:
            bad.append((r['path'], r['sha256'], got))
    print(f"route check: {len(rec['route']) - len(bad)} of {len(rec['route'])} files equal the record at {repo}")
    for b in bad:
        print('  DIFFERS', b)
    if bad:
        sys.exit(3)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--repo', required=True)
    ap.add_argument('--out')
    ap.add_argument('--check', nargs='?', const=os.path.join(HERE, 'out', 'f1f2_route.json'))
    a = ap.parse_args()
    repo = os.path.abspath(a.repo)
    if a.check:
        check(repo, a.check)
        return
    if not a.out:
        sys.exit('f1f2_route.py: --out or --check')
    out = os.path.abspath(a.out)
    if out == HERE or under(out, HERE):
        sys.exit('f1f2_route.py: --out must not be this folder')
    os.makedirs(out, exist_ok=True)
    record(repo, out)


if __name__ == '__main__':
    main()
