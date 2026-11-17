#!/usr/bin/env python3
"""E210 (Q202) desk: did any of E210's operand patterns ever run in a GEMM on any card? A search of every data directory of ours. No card.
Standard library only; the scan mode imports nothing of the lab, so it runs on any box from stdin.

    python3 -I -B neverrun_e210.py scan LABEL TOP [TOP ...] [--exclude=DIR ...] > found.json   (on another box: the same, from stdin)
    python3 -I -B tools/claims-v3/e210/desk/neverrun_e210.py report OUT_JSON OUT_TXT found.json [...] [--scrub=PREFIX=>LABEL ...]
                     (the scrubs replace a box's folder prefixes by labels in the two outputs, so no login or home path is written)

WHAT IS SEARCHED, in every file under a top folder (gzip read through; directories holding a .git entry are skipped: the lab's committed
data are scanned at their source):
  (a) GEMM host records and host commands: a SPARSITY record ("arm": "gemm...", "values": "<arm>:<gen>:<files>") or a command line / argv
      list with --values <gemm arm>:<gen>:<files>. From each: the generator and the tile files it names.
  (b) every tile file: a file of exactly 2,048 bytes (rgm136's tile pair: A then B, 1,024 bytes each), classified by E210's laws below.
THE LAWS (fp32 words, little-endian; a tile is 16 lines of 16 words; A = the first 256 words, B = the last 256), each tested bit for bit:
  negzero    every word 0x80000000
  signs      every word 0x3F800000 or 0xBF800000, both present
  lowmant8   every word 0x3F800000 | (8 bits in mantissa bits 0-7), not all equal
  highmant8  every word 0x3F800000 | (8 bits in mantissa bits 15-22), not all equal
  bhalfeq    every word a normal fp32 value (exponent field 1-254); B[r][c] == B[r][c+8] for every r and c < 8; A and B each not constant
  badjeq     every word a normal fp32 value; B[r][2m] == B[r][2m+1] for every r and m; A and B each not constant
  hd4        every word a normal fp32 value; A: each column's successive rows differ in exactly 4 mantissa bits (and nothing else);
             B[r][c+8] = B[r][c] xor (exactly 4 mantissa bits)
  maxalte    every word a normal fp32 value; A: rows alternate down each column by xor 0x83FFFFFF; B[r][c+8] = B[r][c] xor 0x83FFFFFF
  arow50     A's odd rows all +0.0, every word of A's even rows and of B a normal fp32 value
The host (rgm136, unchanged) draws only randn, sparse50, sparse25 and e37 itself (every element independent: none of these laws) and otherwise
reads tile files, so a GEMM can have run one of these laws only from a tile file that passes it.
SPDX-License-Identifier: Apache-2.0
"""
import gzip
import hashlib
import json
import os
import re
import socket
import struct
import sys
import time

RE_REC_VAL = re.compile(r'"values"\s*:\s*"(gemm[A-Za-z0-9]+:[^"]*)"')
RE_CMD_VAL = re.compile(r'--values"?\s*,?\s*"?(gemm[A-Za-z0-9]+:[^"\s]*)')
MAX_BYTES = 400 * 2 ** 20
TEXT_EXT = ('.json', '.jsonl', '.log', '.txt', '.csv', '.md', '.sh', '.py', '.out', '.err', '.gz', '.tsv', '')
LAWS = ('negzero', 'signs', 'lowmant8', 'highmant8', 'bhalfeq', 'badjeq', 'hd4', 'maxalte', 'arow50')
HOST_GENS = ('randn', 'sparse50', 'sparse25', 'e37', 'tiles')


def popcount(x):
    return bin(x).count('1')


def classify(raw):
    """E210 laws a 2,048-byte tile pair passes (a list; empty for none)"""
    w = struct.unpack('<512I', raw)
    A, B = w[:256], w[256:]
    out = []
    if all(x == 0x80000000 for x in w):
        out.append('negzero')
    if all(x in (0x3F800000, 0xBF800000) for x in w) and len(set(w)) == 2:
        out.append('signs')
    if all((x & 0xFFFFFF00) == 0x3F800000 for x in w) and len(set(w)) > 1:
        out.append('lowmant8')
    if all((x & ~(0xFF << 15) & 0xFFFFFFFF) == 0x3F800000 for x in w) and len(set(w)) > 1:
        out.append('highmant8')
    a_var, b_var = len(set(A)) > 1, len(set(B)) > 1
    nrm = all(0 < ((x >> 23) & 0xFF) < 255 for x in w)
    if nrm and a_var and b_var and all(B[16 * r + c] == B[16 * r + c + 8] for r in range(16) for c in range(8)):
        out.append('bhalfeq')
    if nrm and a_var and b_var and all(B[16 * r + 2 * m] == B[16 * r + 2 * m + 1] for r in range(16) for m in range(8)):
        out.append('badjeq')
    mant = 0x007FFFFF
    if nrm and all(((A[16 * r + c] ^ A[16 * (r - 1) + c]) & ~mant & 0xFFFFFFFF) == 0 and popcount(A[16 * r + c] ^ A[16 * (r - 1) + c]) == 4
           for r in range(1, 16) for c in range(16)) and \
       all(((B[16 * r + c] ^ B[16 * r + c + 8]) & ~mant & 0xFFFFFFFF) == 0 and popcount(B[16 * r + c] ^ B[16 * r + c + 8]) == 4
           for r in range(16) for c in range(8)):
        out.append('hd4')
    F = 0x83FFFFFF
    if nrm and all(A[16 * r + c] == (A[16 * (r - 1) + c] ^ F) for r in range(1, 16) for c in range(16)) and \
       all(B[16 * r + c + 8] == (B[16 * r + c] ^ F) for r in range(16) for c in range(8)):
        out.append('maxalte')
    if all(A[16 * r + c] == 0 for r in range(1, 16, 2) for c in range(16)) and \
       all(0 < ((A[16 * r + c] >> 23) & 0xFF) < 255 for r in range(0, 16, 2) for c in range(16)) and \
       all(0 < ((x >> 23) & 0xFF) < 255 for x in B):
        out.append('arow50')
    return out


def parse_values(v):
    parts = v.split(':', 2)
    arm = parts[0]
    gen = parts[1] if len(parts) > 1 else ''
    files = [f for f in (parts[2].split(',') if len(parts) > 2 else []) if f]
    return arm, gen, files


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
    res = {'label': label, 'host': socket.gethostname(), 'tops': tops, 'python': sys.version.split()[0],
           'started_epoch': t0, 'files_seen': 0, 'text_files_read': 0, 'tile_files': 0, 'gemm_lines': 0,
           'gens': {}, 'tile_names': {}, 'values_unique': 0, 'law_hits': [], 'skipped_git_dirs': 0, 'unreadable': 0,
           'excludes': list(excludes), 'excluded_dirs': 0}
    vals = set()
    for top in tops:
        if not os.path.isdir(top):
            res.setdefault('missing_tops', []).append(top)
            continue
        for dirpath, dirs, files in os.walk(top):
            if dirpath != top and ('.git' in dirs or '.git' in files):
                res['skipped_git_dirs'] += 1          # a scratch clone inside a top: the lab's data are scanned at their source
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
                    try:
                        raw = open(p, 'rb').read()
                    except OSError:
                        res['unreadable'] += 1
                        continue
                    res['tile_files'] += 1
                    hits = classify(raw)
                    if hits:
                        res['law_hits'].append({'path': p, 'laws': hits, 'sha256': hashlib.sha256(raw).hexdigest()})
                    continue
                ext = os.path.splitext(fn)[1].lower()
                if ext not in TEXT_EXT:
                    continue
                lines = read_lines(p)
                if lines is None:
                    res['unreadable'] += 1
                    continue
                res['text_files_read'] += 1
                for line in lines:
                    if 'gemm' not in line:
                        continue
                    for rx in (RE_REC_VAL, RE_CMD_VAL):
                        for m in rx.finditer(line):
                            v = m.group(1).rstrip("',]")
                            res['gemm_lines'] += 1
                            if v in vals:
                                continue
                            vals.add(v)
                            arm, gen, fl = parse_values(v)
                            res['gens'][gen] = res['gens'].get(gen, 0) + 1
                            for f in fl:
                                b = os.path.basename(f)
                                res['tile_names'][b] = res['tile_names'].get(b, 0) + 1
    res['values_unique'] = len(vals)
    res['seconds'] = round(time.time() - t0, 1)
    return res


def scrub_text(t, scrubs):
    for pre, lab in scrubs:
        t = t.replace(pre, lab)
    return t


def report(out_json, out_txt, founds, scrubs=()):
    data = [json.load(open(f)) for f in founds]
    gens, names, hits = {}, {}, []
    for d in data:
        for g, n in d['gens'].items():
            gens[g] = gens.get(g, 0) + n
        for b, n in d['tile_names'].items():
            names[b] = names.get(b, 0) + n
        for h in d['law_hits']:
            hits.append(dict(h, scan=d['label']))
    desk_marks = ('/out/sw-design-a/', '/out/reg-e210/', '/tools/claims-v3/e210/')
    hits_desk = [h for h in hits if any(m in h['path'] for m in desk_marks)]
    hits_other = [h for h in hits if not any(m in h['path'] for m in desk_marks)]
    other_gens = sorted(g for g in gens if g not in HOST_GENS)
    named_hit = sorted({os.path.basename(h['path']) for h in hits_other} & set(names))
    verdict = {}
    for law in LAWS:
        bad = [h for h in hits_other if law in h['laws']]
        verdict[law] = 'NEVER IN A GEMM' if not other_gens and not [h for h in bad if os.path.basename(h['path']) in names] else 'SEE HITS'
    out = {'what': 'E210 never-run search: GEMM records and commands of the lab host, and every 2,048-byte tile file, in every data directory of ours',
           'scans': [{k: d[k] for k in ('label', 'host', 'tops', 'files_seen', 'text_files_read', 'tile_files', 'gemm_lines', 'values_unique',
                                       'skipped_git_dirs', 'unreadable', 'seconds', 'python', 'excludes', 'excluded_dirs')} for d in data],
           'generators_seen_in_gemm_values': gens, 'generators_not_the_hosts': other_gens,
           'tile_files_named_by_gemm_values': names,
           'law_hits_outside_desk_folders': hits_other, 'law_hits_in_desk_folders_count': len(hits_desk),
           'law_hit_files_named_by_a_gemm': named_hit, 'verdict': verdict}
    open(out_json, 'w').write(scrub_text(json.dumps(out, indent=1, sort_keys=True), scrubs) + '\n')
    L = ['E210 never-run search (desk; reads only)', '']
    for s in out['scans']:
        L.append(f"scan {s['label']} on {s['host']}: {s['files_seen']:,} files seen, {s['text_files_read']:,} text files read, {s['tile_files']:,} "
                 f"tile files classified, {s['gemm_lines']:,} GEMM value strings ({s['values_unique']:,} distinct), {s['skipped_git_dirs']} git dirs "
                 f"skipped, {s['unreadable']} unreadable, {s['seconds']} s, Python {s['python']}"
                 + (f"; excluded (not read): {', '.join(s['excludes'])}" if s['excludes'] else ''))
    L.append('')
    L.append('generators in GEMM value strings: ' + ', '.join(f'{g} {n}' for g, n in sorted(gens.items())))
    L.append('generators not the host\'s own (randn, sparse50, sparse25, e37, tiles): ' + (', '.join(other_gens) or 'none'))
    L.append(f'tile files named by GEMM value strings ({len(names)} distinct names): ' + ', '.join(sorted(names)))
    L.append(f'tile files passing an E210 law outside the desk folders: {len(hits_other)}; of them named by a GEMM: {len(named_hit)}; '
             f'in the desk folders (sw-design-a, reg-e210, the registration): {len(hits_desk)}')
    for h in hits_other[:40]:
        L.append(f"  {h['scan']}: {h['path']} {','.join(h['laws'])} {h['sha256'][:16]}")
    L.append('')
    for law in LAWS:
        L.append(f'{law:10s} {verdict[law]}')
    txt = scrub_text('\n'.join(L) + '\n', scrubs)
    open(out_txt, 'w').write(txt)
    print(txt, end='')


def main():
    if len(sys.argv) >= 4 and sys.argv[1] == 'scan':
        args = sys.argv[3:]
        tops = [x for x in args if not x.startswith('--exclude=')]
        excl = [x.split('=', 1)[1] for x in args if x.startswith('--exclude=')]
        json.dump(scan(sys.argv[2], tops, excl), sys.stdout, indent=1, sort_keys=True)
        return 0
    if len(sys.argv) >= 5 and sys.argv[1] == 'report':
        args = sys.argv[4:]
        founds = [x for x in args if not x.startswith('--scrub=')]
        scrubs = [tuple(x.split('=', 1)[1].split('=>', 1)) for x in args if x.startswith('--scrub=')]
        report(sys.argv[2], sys.argv[3], founds, scrubs)
        return 0
    if len(sys.argv) == 3 and sys.argv[1] == 'classify':
        print(json.dumps(classify(open(sys.argv[2], 'rb').read())))
        return 0
    print(__doc__)
    return 2


if __name__ == '__main__':
    sys.exit(main())
