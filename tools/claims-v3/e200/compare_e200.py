#!/usr/bin/env python3
"""E200's REPORTED comparison with E197 (E200.md section 14), registered before any E200 or E197 datum: it decides nothing.

    python3 -I -B tools/claims-v3/e200/compare_e200.py REGFILE-E200.json REGFILE-E197.json [--out compare-e200.json]

Inputs: E200's reduction output (reduce_e200.py; its pooled form when sitting 2 ran) and E197's (reduce_regfile.py; its pooled form
when E197's sitting 2 ran), each as committed with its experiment's data. For every derived price of E197.md 2 that both read with
the same sign (both POSITIVE or both NEGATIVE), it prints the two board prices in pJ (with their 95 % intervals) and their ratio,
E200 over E197, with the ratio's range from the two intervals' ends; a price that is NOT RESOLVED, BOUNDED or NOT SCORED in either is
printed without a ratio. Beside every ratio, as fixed references (constants below, from committed files): the frozen ledger's
v2(800) = (V800 / V600)^2 for aifoundry2 (the per-instruction scaling of the ledger's form from 600 to 800 MHz), and E190's
card-to-card reading, arm A (aifoundry2 card 0, 800 MHz) over arm B (aifoundry1 card 1, 600 MHz), J over idle a GEMM, bursts and
sustained, per format. Also: the two device rates (R), the two train gains, the anchors' res.k64 - nop.z levels. No verdict word is
printed and no forecast is read (both forecasts are sealed; the model session scores them privately). Standard library only.
"""
import argparse
import json
import math

V600, V800 = 0.5174, 0.6174109375          # docs/reports/data/2026-11-12-q166-ledger-v2/frozen-v2.json volts.aifoundry2
V2_800 = (V800 / V600) ** 2
E190_A_OVER_B = {                          # docs/reports/data/2026-11-13-e190-large-gemm/README.md, J over idle a GEMM, A / B
    'bursts': {'fp32': 8.943 / 5.332, 'fp16': 4.243 / 2.512, 'int8': 1.304 / 0.726},
    'sustained': {'fp32': 9.984 / 6.505, 'fp16': 4.723 / 3.023, 'int8': 1.388 / 0.824},
}
SIGNED = ('POSITIVE', 'NEGATIVE')


def ratio_range(a, b):
    """the ratio a/b's mean and its range over the two intervals' ends, when both intervals keep one sign"""
    am, bm = a.get('mean'), b.get('mean')
    if am is None or bm is None or bm == 0:
        return None, None, None
    ends = []
    if None not in (a.get('lo'), a.get('hi'), b.get('lo'), b.get('hi')) and b['lo'] * b['hi'] > 0:
        ends = [x / y for x in (a['lo'], a['hi']) for y in (b['lo'], b['hi'])]
    return am / bm, (min(ends) if ends else None), (max(ends) if ends else None)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('e200')
    ap.add_argument('e197')
    ap.add_argument('--out', default=None)
    a = ap.parse_args()
    r2, r1 = json.load(open(a.e200)), json.load(open(a.e197))
    print('E200 / E197, REPORTED (no verdict): v2(800) = %.6f; E190 arm A / arm B, J over idle a GEMM: bursts %s; sustained %s' % (
        V2_800, ', '.join('%s %.3f' % kv for kv in E190_A_OVER_B['bursts'].items()),
        ', '.join('%s %.3f' % kv for kv in E190_A_OVER_B['sustained'].items())))
    rate = {}
    for tag, r in (('E200', r2), ('E197', r1)):
        rs = [t.get('rate_median') for t in r['trains'].values() if t.get('rate_median')]
        rate[tag] = sorted(rs)[len(rs) // 2] if rs else None
        print('%s: device rate (median over the trains) %s instr/s; train gain %s; session clocks %s MHz' % (
            tag, '%.4e' % rate[tag] if rate[tag] else '-', '%.4f' % r['train_gain'] if r.get('train_gain') else '-', r.get('clock_mhz')))
    if rate['E200'] and rate['E197']:
        print('rate ratio E200 / E197: %.5f' % (rate['E200'] / rate['E197']))
    out = {'v2_800': V2_800, 'e190_a_over_b': E190_A_OVER_B, 'rate': rate, 'prices': {}}
    for name in r1.get('derived', {}):
        d1, d2 = r1['derived'][name], r2.get('derived', {}).get(name)
        if d2 is None:
            continue
        b1, b2 = d1.get('board_pJ') or {}, d2.get('board_pJ') or {}
        row = {'per': d1.get('per'), 'e197': {'board_pJ': b1, 'verdict': d1.get('verdict')},
               'e200': {'board_pJ': b2, 'verdict': d2.get('verdict')}, 'ratio': None}
        txt = '%-14s E197 %s %-12s E200 %s %-12s' % (
            name, ('%+.5f pJ [%+.5f, %+.5f]' % (b1['mean'], b1['lo'], b1['hi'])) if b1.get('lo') is not None else '%-31s' % '-',
            d1.get('verdict'), ('%+.5f pJ [%+.5f, %+.5f]' % (b2['mean'], b2['lo'], b2['hi'])) if b2.get('lo') is not None else '%-31s' % '-',
            d2.get('verdict'))
        if d1.get('verdict') in SIGNED and d1.get('verdict') == d2.get('verdict'):
            m, lo, hi = ratio_range(b2, b1)
            row['ratio'] = {'mean': m, 'lo': lo, 'hi': hi}
            txt += '  ratio %.4f%s' % (m, (' [%.4f, %.4f]' % (lo, hi)) if lo is not None else '')
        else:
            txt += '  no ratio (not the same sign in both)'
        out['prices'][name] = row
        print(txt)
    if a.out:
        json.dump(out, open(a.out, 'w'), indent=1)


if __name__ == '__main__':
    main()
