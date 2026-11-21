#!/usr/bin/env python3
"""decl-e221 (Q235) step 1d (decl-e219's, decl-e217's and unread-e214's s01d_bands.py, unchanged in its arithmetic; aifoundry2 card 0 added in the card-0 form): the pass rule's bands and the head-to-head ties, by E215's registered rule form (E215.md section 7,
tools/claims-v3/e215/rules_e215.py, imported unchanged from the work copy of GitHub main 0f046200, work/lab-commit.txt), for E221's three cards
(aifoundry1 card 1 and card 0 as E219's; aifoundry2 card 0 in card 0's form: its floors from E212 a2c0-S1 and a2c0-S2, the card's most recent
committed sessions in this run form that MM1-v3 vendors). Desk; no E221 data file (none exists).
  BANDS: band = 2 x max(B1, B2), rounded up to a whole percent; B1 = MM1-v3.1's LOEO error without configuration twins over every point,
  B2 = the same over this card's points (rules_e215.heldout() and .bases(), after rules_e215.validate() reproduces MM1-v3.1's own
  holdout_v31.json figures); T3 (seconds) takes T1's bases. WATTS BAND (E1, E2 at points under 3 W): 2 x max(B1 watts, B2 watts, SD_rep),
  rounded up to 0.01 W. SD_rep and the replicate floors: aifoundry1 card 1 E215 arm B's (rules-e215.json: E213 arm B, the card's most recent
  day in a run form, as E215 registered); aifoundry1 card 0 (no E213 or E215 arm there) the pooled within-case sd between the runs of each
  case of the card's most recent committed sessions before E214 in this run form, E212 a1c0-S1 and a1c0-S2 (MM1-v3's vendored copies,
  read by data_v3.mms_runs, the primary view): W over idle (watts; under 3 W apart), ln of the wall cycles, the counter's mean, the op time,
  J over idle at 3 W and above. TIES: rules_e215.ties_of on those floors (never below E209's 0.005 / 0.01 / 0.05 W).
Run: /usr/bin/python3 -I -B s01d_bands.py <lane dir>
"""
import collections
import json
import math
import os
import sys

L = os.path.abspath(sys.argv[1])
LW = os.path.join(L, 'work', 'lab')
OUTD = os.path.join(L, 'work', 'step1')
sys.path.insert(0, os.path.join(LW, 'tools', 'claims-v3', 'e215'))
import rules_e215 as RU  # noqa: E402

C0, C1, C2 = 'aifoundry1 card 0', 'aifoundry1 card 1', 'aifoundry2 card 0'
Trec, Erec, meta = RU.heldout()
val = RU.validate(Trec, Erec)
nval = sum(1 for v in val.values() if v['equal'])
out = {'what': 'decl-e221 step 1d: bands (E215 form) and ties for aifoundry1 card 0 and card 1 and aifoundry2 card 0 (unread-e214 s01d_bands.py in form)', 'python': sys.version.split()[0],
       'validation': {'reproduced': nval, 'of': len(val)}, 'cards': {}}
RJ = json.load(open(os.path.join(LW, 'tools', 'claims-v3', 'e215', 'rules-e215.json')))
armB = RJ['arms']['B']


def floors_card0(tag='a1c0'):
    sys.path.insert(0, os.path.join(LW, 'tools', 'matmul', 'mm1', 'v3'))
    import data_v3 as D  # noqa: E402
    runs = []
    for fn in (f'{tag}-S1__data-e212-{tag}-S1.json', f'{tag}-S2__data-e212-{tag}-S2.json'):
        runs += D.mms_runs(('e212', fn), 'E212', D.e212_kind)
    by = collections.defaultdict(list)
    for r in runs:
        by[r['case']].append(r)
    acc = {k: [0.0, 0] for k in ('W', 'W_under_3W', 'wall_ln', 'mean_ln', 'seconds_ln', 'J_ln', 'J_ln_3W_and_above')}
    npts = 0
    for case, rs in by.items():
        if len(rs) < 2:
            continue
        npts += 1
        vals = {'wall_ln': [math.log(r['cyc_wall']) for r in rs], 'mean_ln': [math.log(r['cyc_mean']) for r in rs],
                'seconds_ln': [math.log(r['T']) for r in rs]}
        re_ = [r for r in rs if 'w' in r]
        if len(re_) >= 2:
            wv = [r['w'] for r in re_]
            vals['W'] = wv
            vals['J_ln'] = [math.log(max(1e-12, r['w'] * r['T'])) for r in re_]
            if sum(wv) / len(wv) < 3.0:
                vals['W_under_3W'] = wv
            else:
                vals['J_ln_3W_and_above'] = vals['J_ln']
        for k, v in vals.items():
            m = sum(v) / len(v)
            acc[k][0] += sum((x - m) ** 2 for x in v)
            acc[k][1] += len(v) - 1
    fl = {k: round(math.sqrt(s / df), 5) if df else None for k, (s, df) in acc.items()}
    fl.update({'cases_with_two_or_more_runs': npts, 'source': f"E212 {tag}-S1 and {tag}-S2 (tools/matmul/mm1/v3/inputs/e212/, data_v3.mms_runs)",
               'how': 'pooled within-case sd between each case\'s runs (the primary view): W over idle in watts; the rest sd of ln'})
    return fl


fl0 = floors_card0('a1c0')
fl2 = floors_card0('a2c0')
for card, tag in ((C1, 'c1'), (C0, 'c0'), (C2, 'a2c0')):
    b = RU.bases(Trec, Erec, card)
    bands = {}
    for q in ('T1', 'T2', 'E1', 'E2', 'E3', 'E4'):
        B1 = b[q]['B1_LOEO_no_twin_all']['rms_pct']
        B2 = b[q]['B2_LOEO_no_twin_card']['rms_pct'] if b[q]['B2_LOEO_no_twin_card'] else None
        basis = max(B1, B2 if B2 is not None else 0.0) / 100.0
        bands[q] = {'B1': B1, 'B2': B2, 'n_B2': (b[q]['B2_LOEO_no_twin_card'] or {}).get('n'), 'basis': round(basis, 6),
                    'band': RU.ceil_pct(2 * basis), 'arithmetic': f"2 x max({B1:.3f}, {B2:.3f}) = {200 * basis:.2f} -> {round(100 * RU.ceil_pct(2 * basis))}%"}
    bands['T3'] = dict(bands['T1'], note='seconds: T1\'s bases (E215\'s form)')
    wall = b['W']['all_under_3W_no_twin']['rms_W']
    wcard = (b['W']['card_under_3W_no_twin'] or {}).get('rms_W')
    if card == C1:
        sdrep = armB['band_w']['SD_rep_W']
        ties = RJ['ties_by_arm']['B']
        floor_src = "E215 arm B's (rules-e215.json: E213 arm B)"
    else:
        flx = fl0 if card == C0 else fl2
        sdrep = flx['W']
        ties = RU.ties_of(flx)
        floor_src = flx['source']
    bw = math.ceil(round(100 * 2 * max(wall, wcard or 0.0, sdrep or 0.0), 6)) / 100.0
    out['cards'][card] = {'bands': bands, 'band_w': {'band_W': bw, 'B1_W': wall, 'B2_W': wcard, 'SD_rep_W': sdrep,
                                                      'arithmetic': f"2 x max({wall:.4f}, {wcard if wcard is None else round(wcard, 4)}, SD_rep {sdrep}) -> {bw:.2f} W"},
                          'ties': ties, 'floors_source': floor_src, 'bases': b}
out['card0_floors'] = fl0
out['a2c0_floors'] = fl2
# E215 arm B's registered bands, for the check that this code gives card 1 the same
out['check_card1_equals_E215_armB'] = {q: (out['cards'][C1]['bands'][q]['band'], armB['bands'][q]['band']) for q in ('T1', 'T2', 'T3', 'E1', 'E2', 'E3', 'E4')}
out['check_card1_equals_E215_armB']['band_W'] = (out['cards'][C1]['band_w']['band_W'], armB['band_w']['band_W'])
out['check_card1_all_equal'] = all(abs(a - b_) < 1e-12 for a, b_ in out['check_card1_equals_E215_armB'].values())
json.dump(out, open(os.path.join(OUTD, 'bands.json'), 'w'), indent=1, sort_keys=True)
print('validation', out['validation'], 'card1 = E215 arm B:', out['check_card1_all_equal'])
for card in (C1, C0, C2):
    c = out['cards'][card]
    print(card, {q: v['arithmetic'] for q, v in c['bands'].items()}, c['band_w']['arithmetic'], 'ties', c['ties'])
print('card0 floors', json.dumps(fl0))
print('aifoundry2 card 0 floors', json.dumps(fl2))
