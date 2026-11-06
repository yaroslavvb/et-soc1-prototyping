"""Post hoc, desk only: within the TEL block's statistics-reset windows (committed raw, 25-26 Sep 2026), how far each rail's
PMIC min and max sit from its average, per card. A rail whose stat gets two updates per PMIC scan (P0 alone, then P0+P1)
would show min/avg near 2/3 and max/avg near 4/3 at a steady load; a single-update rail near 1 and 1."""
import gzip, json, sys, statistics as st, glob, os
RAWDIR = sys.argv[1]
out = {}
for card in ('aifoundry1-c1', 'aifoundry2', 'aifoundry3'):
    res = {r: {'mn': [], 'mx': [], 'zero': 0, 'n': 0} for r in ('minion_w', 'sram_w', 'noc_w')}
    files = sorted(glob.glob(os.path.join(RAWDIR, card, 'tel', 'p*', 'reset.jsonl.gz')))
    for f in files:
        for line in gzip.open(f, 'rt'):
            try:
                d = json.loads(line)
            except Exception:
                continue
            s = d.get('sp'); sr = d.get('since_reset_ms', -1)
            if not s or sr is None or sr < 0:
                continue
            for r in res:
                a, mn, mx = s[r]
                if sr < 600:          # skip the first pass or two after each reset
                    if a == 0 and mn == 0 and mx == 0:
                        res[r]['zero'] += 1
                    continue
                res[r]['n'] += 1
                if a > 0.3 and mx < 65.0 and mn < 65.0:
                    res[r]['mn'].append(mn / a); res[r]['mx'].append(mx / a)
    out[card] = {}
    for r, v in res.items():
        q = lambda xs, p: (sorted(xs)[int(p * (len(xs) - 1))] if xs else None)
        out[card][r] = {'files': len(files), 'n_600ms+': v['n'], 'n_ratio': len(v['mn']),
                        'min_over_avg_median': (round(st.median(v['mn']), 4) if v['mn'] else None),
                        'min_over_avg_p10_p90': [round(q(v['mn'], .1), 4), round(q(v['mn'], .9), 4)] if v['mn'] else None,
                        'max_over_avg_median': (round(st.median(v['mx']), 4) if v['mx'] else None),
                        'max_over_avg_p10_p90': [round(q(v['mx'], .1), 4), round(q(v['mx'], .9), 4)] if v['mx'] else None,
                        'all_zero_samples_under_600ms': v['zero']}
print(json.dumps(out, indent=1))
