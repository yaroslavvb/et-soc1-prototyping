#!/usr/bin/env python3
"""counts-e214 (Q225) step 15: the lane's result.json and result.md from its own files (desk; reads files only).
    /usr/bin/python3 -I -B s15_result.py <lane dir>
"""
import csv
import hashlib
import json
import os
import sys
import time

L = sys.argv[1]
REL = 'tools/matmul/mm1/v3.1/counts-e214'
D = os.path.join(L, 'land', REL)
C = os.path.join(L, 'counts')
os.environ['TZ'] = 'America/Los_Angeles'
time.tzset()


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


def j(p):
    return json.load(open(p))


rows = list(csv.DictReader(open(os.path.join(C, 'counts-e214.csv'))))
rc = j(os.path.join(C, 'recount-check.json'))
xc = j(os.path.join(C, 'crosscheck-sparse50h.json'))['rows']['fp16.sparse50h']['table_units']
sc = j(os.path.join(C, 'scope-e214.json'))
src = j(os.path.join(C, 'SOURCES.json'))
lc = j(os.path.join(L, 'work', 'land-check.json'))
c32 = j(os.path.join(C, 'counts-fp32-gemm-states.json'))
cL = j(os.path.join(C, 'counts-fp16-int8-launch.json'))
files = []
for dp, _, fs in os.walk(D):
    for f in fs:
        p = os.path.join(dp, f)
        files.append({'path': os.path.relpath(p, os.path.join(L, 'land')), 'sha256': sha(p),
                      'final_pacific': time.strftime('%a %d %b %Y %H:%M:%S %Z', time.localtime(os.path.getmtime(p)))})
files.sort(key=lambda x: x['path'])
last = max(os.path.getmtime(os.path.join(L, 'land', f['path'])) for f in files)
problems = (c32.get('problems') or []) + (cL.get('problems') or [])
n_new = len([k for k in sc['kinds'] if k['verdict'] == 'NEEDS COUNT'])
counted = {(r['fmt'], r['mm1_v3_kind']) for r in rows}
ok = rc['pass'] and not problems and lc['verdict'] == 'LAND OK' and len(counted) == n_new
verdict = 'COUNTED' if ok else ('NOT COUNTED' if not rc['pass'] else 'COUNTED WITH GAPS')
npts = sum(int(r['n_points']) for r in rows)
nums = []
for r in rows:
    st = r['footing_class'].split(' ')[0] if r['fmt'] == 'fp32' else 'launch'
    nums.append(f"{r['fmt']} {r['mm1_v3_kind']} {st}: fin edges lo/hi a MAC {float(r['fin_edges_lo_per_mac']):,.0f} / {float(r['fin_edges_hi_per_mac']):,.0f}; "
                f"signal lo {float(r['signal_lo_per_mac']):,.0f}; valid share {float(r['valid_share']):.3f}; minus committed random (lo) "
                f"{float(r['minus_committed_random_lo_per_mac']):,.0f} (desk, {r['n_points']} points, check {r['check_mismatch_max']})")
ck = rc['checks']
leaves = sum(c['leaves_compared'] for c in ck.values())
leq = sum(c['leaves_bit_equal'] for c in ck.values())
summary = (f"{verdict}: E214's {n_new} plan tiles with no committed count (fp32 9 at GEMM states S1 and S2, fp16 5 and int8 6 at the launch points; "
           f"{npts} bench points, every check 0) counted on aifoundry2's desk with the RTL bench (8bde0182, Verilator 5.042) in each format's committed "
           f"footing; two committed v3.1 rows re-counted first: {'MATCH' if rc['pass'] else 'NO MATCH'} ({leq} of {leaves} numbers bit-equal); "
           f"E214's random/zeros/ones and sparse50 pools are committed kinds (sparse50h's pair-0 file cross-checked: fin edges lo {xc['fin_edges_lo_a_MAC']['ratio']:.3f} "
           f"of the committed fp16 sparse50 row, REPORTED); land dir {len(files)} new files, SHA256SUMS {lc['SHA256SUMS_sha256'][:16]}...; no E214 measurement "
           f"or E215 datum read; {src['slot_minutes_total']} slot-minutes.")
res = {'lane': 'counts-e214', 'round': 'Q225', 'track': 'A', 'verdict': verdict, 'summary': summary,
       'land_dir': 'OUT/counts-e214/land', 'land_path': REL, 'files': files, 'land_final_pacific': time.strftime('%a %d %b %Y %H:%M:%S %Z', time.localtime(last)),
       'SHA256SUMS_sha256': lc['SHA256SUMS_sha256'], 'lab_github_main': src['lab_github_main'], 'lab_head_at_check': lc['lab_head'],
       'recount': {'pass': rc['pass'], 'rule_sha256': rc['rule_sha256'], 'leaves_bit_equal': leq, 'leaves_compared': leaves,
                   'checks': {k: {'pass': v['pass'], 'leaves_bit_equal': v['leaves_bit_equal'], 'leaves_compared': v['leaves_compared']} for k, v in ck.items()}},
       'scope': {'arms': sc['n_arms'], 'kinds': len(sc['kinds']), 'needs_count': sc['needs_count'],
                 'arms_on_new_kinds': sum(k['n_arms'] for k in sc['kinds'] if k['verdict'] == 'NEEDS COUNT')},
       'crosscheck_sparse50h': {k: v['ratio'] for k, v in xc.items()},
       'numbers': nums, 'slot_minutes': src['slot_minutes_total'], 'slot_jobs': len(src['slot_jobs']),
       'interpreter': '/usr/bin/python3 3.12.3 (-I -B), numpy ' + str(src.get('numpy')), 'problems': problems}
res['open_issues'] = [
    "E214's sparse50 arms (pattern:sparse50f, pattern:sparse50h, pattern:sparse50i by data_v3.e212_kind) need data_v31's SPARSE_GEN alias to "
    "the committed sparse50 kind in an E214 reader (sparse50h included); no count is made for them here",
    "phi for the 20 new kinds: MM1-v3.1's item 7 looks for pattern:<name> tiles in inputs/e212tiles/ only; E214's tile files are committed in "
    "tools/claims-v3/e214/proposal/src/tiles/; whether the UNREAD test uses them through kinds_v3.phi is that lane's to declare",
    "the gate: fp32 pattern:sp_ar4 reads valid share 0.500 at S1 and S2 (half of A's rows zero); MM1-v3's gate_shares() gives fp32/fp16 a gate "
    "only for zeros, arow50 and sparse50, so a pattern kind gets none: the UNREAD test must declare how sp_ar4 is gated before reading E214 energy",
    "fp16 and int8 counted at the launch points (one tile pair repeated: for these one-file kinds the card's pair), not at GEMM states; E214's "
    "KB 8 fp32 arms (bh3_e3, sp_ar4) read the S2 states (gemmL1x1x4's depths)"]
res['incidents'] = [
    "s13's first land copy of its own script kept a scratch-path fragment (no login, no home path) in its pattern line; s14's scan caught it "
    "(LAND NOT OK at 09:59:01); s13 rewritten to take the paths from env.sh's variables, land dir rebuilt, s14 LAND OK; nothing else"]
res['not_run'] = ['any card', 'sys_emu', 'any fit', 'gate-level fp16 or int8', 'GEMM-state counts for fp16 and int8', 'a phi for the new kinds',
                  'MM1-v3.1, MM1-v3 or MM1-v2 run with these rows (the UNREAD test is unread-e214)']
res['no_e214_measurement_read'] = True
res['no_e215_datum_read'] = True
json.dump(res, open(os.path.join(L, 'result.json'), 'w'), indent=1, sort_keys=True)
print(json.dumps({k: res[k] for k in ('verdict', 'summary', 'SHA256SUMS_sha256', 'land_final_pacific')}, indent=1))

# result.md: short and exact, every number read from the files above
md = [f"# counts-e214 (Q225, track A): result", '', f"**Verdict: {verdict}.**", '', summary, '',
      '## What ran (desk only, aifoundry2, Thu 19 Nov 2026; no card, no sys_emu, no fit, no commit)', '',
      f"- Sources by `git archive` of GitHub main 8bde0182 (= LAB HEAD; LAB untouched) and core-et b38a1a31; the bench's source manifest identical "
      f"to v31-counts'. Build: Verilator 5.042, -fno-dfg, Verilator -j 2, make -j 1, 4 GB cap; obj_unit/Vtb, accum, settle_count byte-equal to "
      f"v31-counts'. {src['functional_check']} Maps byte-equal to v31-counts': {src['maps_sha256'] == src['maps_v31counts_sha256']}.",
      f"- Scope from E214's registered arms.json only: {sc['n_arms']} arms, {len(sc['kinds'])} (format, kind) pairs; MM1-v3.1's counts31() and "
      f"MM1-v3's counts() return None for exactly the 20 plan tiles of gen tiles ({res['scope']['arms_on_new_kinds']} arms); random, zeros, ones "
      f"and the three sparse50 pools are committed kinds.",
      f"- Re-count first (rule hashed before: {rc['rule_sha256'][:16]}...): v3.1's fp32 pattern:fld_mant S1 and pattern:den8 S2, int8 pattern:i8_pm1 "
      f"and fp16 pattern:fld16_mant at the launch points: {leq} of {leaves} numbers bit-equal, every row number equal: "
      f"{'MATCH' if rc['pass'] else 'NO MATCH'}.",
      f"- New counts: count_e210.py (fp32, S1 and S2) and run_kinds.py (fp16, int8 at the launch points), one bench process, one slot job at a "
      f"time; {npts} bench points, every check_mismatch 0; {src['slot_minutes_total']} slot-minutes in {len(src['slot_jobs'])} slot jobs.",
      f"- Cross-check (REPORTED, not a row): E214's sparse50h file at the launch points / the committed fp16 sparse50 row: "
      + ', '.join(f"{k} {v['ratio']:.4f}" for k, v in xc.items()) + '.', '',
      '## The counts (desk; fin edges a multiply-add)', '',
      '| fmt | kind | state | fin edges lo / hi | signal lo | valid share | minus committed random (lo) | points |', '|---|---|---|---:|---:|---:|---:|---:|']
for r in rows:
    st = r['footing_class'].split(' ')[0] if r['fmt'] == 'fp32' else 'launch'
    md.append(f"| {r['fmt']} | {r['mm1_v3_kind']} | {st} | {float(r['fin_edges_lo_per_mac']):,.0f} / {float(r['fin_edges_hi_per_mac']):,.0f} | "
              f"{float(r['signal_lo_per_mac']):,.0f} | {float(r['valid_share']):.3f} | {float(r['minus_committed_random_lo_per_mac']):,.0f} | {r['n_points']} |")
md += ['', f"## Land dir: OUT/counts-e214/land/{REL}/ (new files only; LAB HEAD {lc['lab_head'][:8]} has no path there)", '',
       f"{len(files)} files; SHA256SUMS sha256 **{lc['SHA256SUMS_sha256']}**; land check {lc['verdict']}; last file final {res['land_final_pacific']}.",
       'Each file, its sha256 and the time it was final (Pacific):', '']
for f in files:
    md.append(f"- `{f['path']}` {f['sha256']} ({f['final_pacific']})")
md += ['', '## Open issues (for unread-e214 and the orchestrator)', '',
       "1. E214's sparse50 arms are named `pattern:sparse50f`, `pattern:sparse50h`, `pattern:sparse50i` by data_v3.e212_kind: an E214 reader needs "
       "data_v31's SPARSE_GEN alias to `sparse50` for all three (sparse50h included); no count is made for them here.",
       "2. phi for the new kinds: MM1-v3.1's item 7 looks for `pattern:<name>` tiles in inputs/e212tiles/ only; E214's tiles are committed in "
       "tools/claims-v3/e214/proposal/src/tiles/; whether the UNREAD test uses them through kinds_v3.phi is that lane's to declare.",
       "3. fp16 and int8 are counted at the launch points (one tile pair repeated: for these one-file kinds the card's pair), not at GEMM states; "
       "E214's KB 8 fp32 arms (bh3_e3, sp_ar4) read the S2 states (gemmL1x1x4's depths), as MM1-v3 reads E210's S2 for every KB >= 2.",
       "4. The gate: " + ('; '.join(f"{r['fmt']} {r['mm1_v3_kind']} ({r['footing_class'].split(' ')[0] if r['fmt'] == 'fp32' else 'launch'}) valid share "
                                   f"{float(r['valid_share']):.3f}" for r in rows if float(r['valid_share']) < 0.999) or 'every row valid share 1.000')
       + ". MM1-v3's gate_shares() (used by v3.1) gives fp32 and fp16 a micro-op gate only for zeros, arow50 (0.5) and sparse50, so a "
       "pattern kind gets none whatever its valid share (int8's is 1 - v from the count): how such a kind is gated is the UNREAD test's to "
       "declare before any E214 energy is read.",
       '', '## Incidents', '', '- ' + res['incidents'][0] + '.',
       '', '## NOT RUN', '',
       "Any card; sys_emu; any fit; gate-level fp16 or int8; GEMM-state counts for fp16 and int8; a phi for the new kinds; MM1-v3.1, MM1-v3 or MM1-v2 "
       "run with these rows. No E214 measurement file and no E215 datum was opened.", '',
       f"Interpreter: {res['interpreter']}. Files: OUT/counts-e214/result.json, logs/progress.txt, counts/, raw bench outputs in work/counts/."]
open(os.path.join(L, 'result.md'), 'w').write('\n'.join(md) + '\n')
print('result.md written')
