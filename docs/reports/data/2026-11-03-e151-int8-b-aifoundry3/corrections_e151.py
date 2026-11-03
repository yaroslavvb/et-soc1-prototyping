#!/usr/bin/env python3
"""E151, corrections after verification (post hoc, Tue 3 Nov 2026): the facts behind README C2 and C3.

Written after an independent verification of E151, at the desk: no card, no device command, no re-run. It reads committed
files only (the tiles and the four sessions' registrations and scored files) and prints; it changes nothing. Run it from
anywhere:

    python3 docs/reports/data/2026-11-03-e151-int8-b-aifoundry3/corrections_e151.py > .../corrections_e151.txt

[A] which tiles the four sessions ran (C2: the transfers test days and cards, not tiles);
[B] what those tiles hold: B's base words, the held A, and whether any B flip reaches zero (C2);
[C] what the A side rests on (C3: today's A is one block; E130's and E145's registered rules);
[D] the out-of-sample B and A tables as scored, with their scope (C2, C3).
"""
import hashlib
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
REPO_DIR = os.path.abspath(os.path.join(HERE, '..', '..', '..', '..'))
SESSIONS = ('e130', 'e138', 'e145', 'e151')
SCORED = {
    'E130': 'docs/reports/data/2026-11-02-e130-int8-netlists/scored.json',
    'E145': 'docs/reports/data/2026-11-02-e145-int8-b-card1/scored.json',
    'E151': 'docs/reports/data/2026-11-03-e151-int8-b-aifoundry3/scored.json',
}


def load(rel):
    with open(os.path.join(REPO_DIR, rel)) as f:
        return json.load(f)


def iv(s, nd=1):
    """mean [lo, hi] (n), or mean (n 1) when there is no interval."""
    if s.get('lo') is None:
        return '%+.*f (n %d, no interval)' % (nd, s['mean'], s['n'])
    return '%+.*f [%+.*f, %+.*f] (n %d)' % (nd, s['mean'], nd, s['lo'], nd, s['hi'], s['n'])


def hexes(vals):
    return ', '.join('0x%02X' % v for v in sorted(vals))


out = []
say = out.append

say('E151 corrections after verification: the facts behind C2 and C3 (post hoc; committed files only)')
say('')

# [A] the same tiles in all four sessions
items = {s: load('tools/claims-v3/%s/e130-items.json' % s) for s in SESSIONS}
lists = {s: [(t['tile'], t['sha256']) for t in items[s]['tiles']] for s in SESSIONS}
same = all(lists[s] == lists['e151'] for s in SESSIONS)
say('[A] Tiles. E130, E138, E145 and E151 each pin the tiles in their own tools/claims-v3/<e>/e130-items.json.')
say('    the four lists (tile name and sha256, in order) are identical: %s; %d tiles' % ('YES' if same else 'NO', len(lists['e151'])))
it = items['e151']
tiles = {}
for t in it['tiles']:
    with open(os.path.join(REPO_DIR, it['tiles_dir'], t['file']), 'rb') as f:
        raw = f.read()
    tiles[t['tile']] = dict(meta=t, A=raw[:1024], B=raw[1024:], ok=hashlib.sha256(raw).hexdigest() == t['sha256'])
say('    every tile file in %s matches its registered sha256: %s' % (it['tiles_dir'], all(v['ok'] for v in tiles.values())))
say('    so the day-to-day (E130 + E138 -> E151) and card-to-card (E145 -> E151) transfers repeat the same tiles: they test')
say('    sessions and cards, not other tiles, base words or kernels.')
say('')

# [B] what the tiles hold
say('[B] What the tiles hold (each file is A then B, 1,024 bytes each).')
for z in ('hb1', 'hb2', 'hb1d'):
    A, B = set(tiles[z]['A']), tiles[z]['B']
    counts = sorted({v: B.count(v) for v in set(B)}.items())
    say('    %-5s (%s): A = {%s}; B = %d distinct bytes {%s}, each on %s of 1,024' % (
        z, 'base word B%s' % tiles[z]['meta']['base_word'], hexes(A), len(counts), hexes(set(B)),
        '/'.join(sorted({str(c) for _, c in counts}))))
bits_ok = True
for k in range(8):
    t = tiles['b1_%d' % k]
    z = tiles['hb1']
    same_a = t['A'] == z['A']
    flipped = sum(1 for i in range(1024) if t['B'][i] == z['B'][i] ^ (1 << k))
    kept = sum(1 for i in range(1024) if t['B'][i] == z['B'][i])
    ok = same_a and flipped + kept == 1024
    bits_ok &= ok
    if k in (0, 6):
        pairs = sorted({(z['B'][i], t['B'][i]) for i in range(1024) if t['B'][i] != z['B'][i]})
        say('    b1_%d: A as hb1 (%s); B bit %d flipped on %d of 1,024 bytes, the rest as hb1; pairs %s' % (
            k, same_a, k, flipped, ', '.join('0x%02X->0x%02X' % p for p in pairs)))
say('    b1_0 ... b1_7 each differ from hb1 only in their own B bit, on half the bytes, with A unchanged: %s' % bits_ok)
btiles = [n for n, v in tiles.items() if v['meta']['side'] == 'b']
zero_b = {n: tiles[n]['B'].count(0) for n in btiles}
say('    B-side tiles (%d): zero bytes in B: %d in all (%s)' % (len(btiles), sum(zero_b.values()),
                                                            'none' if not any(zero_b.values()) else zero_b))
say('    so no B flip in these tiles goes to or from zero; the per-position B list (bits 0-6) is measured at one B base word,')
say('    B1, with A held at %s.' % hexes(set(tiles['b1_0']['A'])))
for z in ('ha1', 'ha2', 'ha1d'):
    say('    %-5s (base word A%s): A = {%s}; B = {%s}' % (z, tiles[z]['meta']['base_word'], hexes(set(tiles[z]['A'])),
                                                        hexes(set(tiles[z]['B']))))
say('')

# [C] the A side
e130, e145, e151 = (load(SCORED[k]) for k in ('E130', 'E145', 'E151'))
say('[C] The A side (C3).')
v = e130['primary']['verdicts']
say('    E130 (aifoundry3 card 0, registered primary = the board): R2 %s, A odd - even %s fJ; A blocks %d' % (
    v['E130-R2'], iv(e130['primary']['statistics']['A_odd_minus_even_fJ']), e130['primary']['n_blocks']['A']))
v = e145['primary']['verdicts']
say('    E145 (aifoundry1 card 1, registered primary = the rail): R2 %s, C1 %s, A odd - even %s board-equivalent fJ' % (
    v['E145-R2'], v['E145-C1'], iv(e145['primary']['statistics_board_equivalent']['A_odd_minus_even_fJ'])))
a = e145['cross_card']['A']
say('    E145 cross_card.A (card 0 predicting card 1, bits 0-6): flat %.1f rail fJ (%.0f%%), per position %.1f (%.0f%%)' % (
    a['rms_rail_fJ']['flat'], 100 * a['share_of_card1_mean']['flat'], a['rms_rail_fJ']['per_position'],
    100 * a['share_of_card1_mean']['per_position']))
v = e151['primary']['verdicts']
say('    E151 A blocks kept: %s; R2 %s, R3 %s, C1 %s, R4s %s, R5 %s; A odd - even %s board-equivalent fJ' % (
    e151['primary']['blocks']['A'], v['E151-R2'], v['E151-R3'], v['E151-C1'], v['E151-R4s'], v['E151-R5'],
    iv(e151['primary']['statistics_board_equivalent']['A_odd_minus_even_fJ'])))
say('')

# [D] the out-of-sample tables, as scored
say('[D] Out of sample, bits 0-6, rms in rail fJ (share of the predicted session\'s mean), as scored in E151\'s scored.json.')
for key, what in (('cross_session_card0', {'B': "card 0's earlier sessions (E130, E138) -> E151",
                                             'A': "card 0's E130 (E138 ran no A block) -> E151"}),
                  ('cross_card_from_card1_filtered', {'B': "card 1 (E145, E151's filter) -> E151",
                                                      'A': "card 1 (E145, E151's filter) -> E151"})):
    for side in ('B', 'A'):
        c = e151[key][side]
        r, s = c['rms_rail_fJ'], c['share_of_card1_mean']
        say('    %-46s %s: flat %.1f (%.0f%%), parity %.1f (%.0f%%), per position %.1f (%.0f%%)%s' % (
            what[side], side, r['flat'], 100 * s['flat'], r['parity'], 100 * s['parity'], r['per_position'],
            100 * s['per_position'], "  [E151's A: one block]" if side == 'A' else ''))
say('    Scope: the same tiles as [A] (B base word B1, A = 0x01 for bits 0-6); other base words and kernels untested.')

print('\n'.join(out))
