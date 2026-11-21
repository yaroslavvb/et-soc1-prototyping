#!/usr/bin/env python3
"""mask-posimb (Q238) z01: FREEZE. Writes OUT/mask-posimb/FROZEN.txt (the sha256 of the declaration, the code, the params, the fits and the
held-out record, and every other land file, with the time they were final), a byte copy in the land folder (FROZEN-posimb-mask.txt), the land
folder's SHA256SUMS, and msg/to-orchestrator-frozen.txt (one line: the time and FROZEN.txt's sha256). Refuses if the declaration's or the fit
record's sha256 is not the one the fit and the params name. Desk; stdlib."""
import datetime
import hashlib
import json
import os
import shutil

LANE = os.environ['MASKPOS_LANE']
LAND = os.path.join(LANE, 'land/tools/matmul/mm1/v3.4-cands/posimb-mask')
DECL_SHA = 'b59f1c4dc5ff1b67483face805216585cfca94b2fe709700c458ff2ca4714f40'


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


def main():
    assert sha(os.path.join(LAND, 'DECLARED-posimb-mask.md')) == DECL_SHA
    par = json.load(open(os.path.join(LAND, 'params-posimb-mask.json')))
    assert par['declaration_sha256'] == DECL_SHA and par['fit_results_sha256'] == sha(os.path.join(LAND, 'out/fit_results.json'))
    F = json.load(open(os.path.join(LAND, 'out/fit_results.json')))
    kept = bool(F['keep_rule']['KEPT'])
    files = []
    for root, _, fs in os.walk(LAND):
        for f in fs:
            rel = os.path.relpath(os.path.join(root, f), LAND)
            if rel in ('SHA256SUMS', 'FROZEN-posimb-mask.txt'):
                continue
            files.append(rel)
    files.sort()
    latest = max(os.path.getmtime(os.path.join(LAND, f)) for f in files)
    final = datetime.datetime.fromtimestamp(latest).astimezone().strftime('%Y-%m-%d %H:%M:%S %Z')
    now = datetime.datetime.now().astimezone().strftime('%Y-%m-%d %H:%M:%S %Z')
    a = par['constants']
    groups = [('the declaration (hashed 2026-11-21 01:31:42 PST, before any fit)', ['DECLARED-posimb-mask.md', 'DECLARED-posimb-mask.md.sha256']),
              ('the code (the predictor; the fit and its inputs)', ['posimb_mask.py', 'scripts/g01_fit.py', 'scripts/d01_points.py', 'scripts/e01_base.py',
                                                                  'scripts/f02_run.sh', 'scripts/a02_reduce_e224b.sh', 'scripts/h01_params.py']),
              ('the params', ['params-posimb-mask.json']),
              ('the fits (every fold\'s constants, the keep rule, the placebo, the REPORTED tables)', ['out/fit_results.json']),
              ('the held-out record (every point\'s held-out op time in every fold family)', ['out/heldout_points.csv']),
              ('the data and features the fit read', ['out/points_all.json', 'out/private_shared.json', 'out/base_meta.json'])]
    named = {f for _, fs in groups for f in fs}
    groups.append(('every other land file', [f for f in files if f not in named]))
    L = ['# mask-posimb (Q238, track P): FROZEN. Label: %s (%s by its declared rule).' % (par['label'], 'KEPT' if kept else 'NOT KEPT: a rejected candidate, REPORTED'),
         '# the files final at %s (the latest file time); FROZEN.txt written %s; land dir OUT/mask-posimb/land/tools/matmul/mm1/v3.4-cands/posimb-mask/' % (final, now),
         '# constants (all data through E224, two-stage on MM1-v3.2 4e386f75 unchanged): a_hop %r, a_lag %r, a_al %r' % (a['a_hop'], a['a_lag'], a['a_al']),
         '# held out: M1 LOSO on E221 363 MASK cases %.4f%% (MM1-v3.2 %.4f%%; K1 <= %.4f); M1L LOMO %.4f%% (K1L <= %.4f); M2 non-MASK LOEO no twin %.4f%% (MM1-v3.2 %.4f%%); '
         'M4 MASK outside E221 LOEO no twin %.4f%% (MM1-v3.2 %.4f%%); placebo beaten %d/100' % (
             F['M1_LOSO_head_rms_pct']['cand'], F['M1_LOSO_head_rms_pct']['v32'], F['keep_rule']['K1_threshold'], F['M1L_LOMO_head_rms_pct']['cand'],
             F['keep_rule']['K1L_threshold'], F['M2_LOEO_nonMASK_no_twin_rms_pct']['cand'], F['M2_LOEO_nonMASK_no_twin_rms_pct']['v32'],
             F['M4_LOEO_MASK_not_E221_no_twin_rms_pct']['cand'], F['M4_LOEO_MASK_not_E221_no_twin_rms_pct']['v32'], F['M3_placebo']['cand']['beaten']),
         '# no E226 file was read; desk only; /usr/bin/python3 3.12.3, numpy 1.26.4, single-threaded in the round\'s slots']
    for title, fs in groups:
        L.append('## ' + title)
        for f in fs:
            L.append('%s  %s' % (sha(os.path.join(LAND, f)), f))
    txt = '\n'.join(L) + '\n'
    fz = os.path.join(LANE, 'FROZEN.txt')
    open(fz, 'w').write(txt)
    os.chmod(fz, 0o444)
    shutil.copyfile(fz, os.path.join(LAND, 'FROZEN-posimb-mask.txt'))
    allf = sorted(files + ['FROZEN-posimb-mask.txt'])
    open(os.path.join(LAND, 'SHA256SUMS'), 'w').write(''.join('%s  %s\n' % (sha(os.path.join(LAND, f)), f) for f in allf))
    h = sha(fz)
    os.makedirs(os.path.join(LANE, 'msg'), exist_ok=True)
    open(os.path.join(LANE, 'msg/to-orchestrator-frozen.txt'), 'w').write(
        '%s FROZEN.txt sha256 %s (mask-posimb, %s, %s by its declared rule)\n' % (now, h, par['label'], 'KEPT' if kept else 'a rejected candidate'))
    print(txt)
    print('FROZEN.txt', h)
    print('SHA256SUMS', sha(os.path.join(LAND, 'SHA256SUMS')), len(allf), 'files')


if __name__ == '__main__':
    main()
