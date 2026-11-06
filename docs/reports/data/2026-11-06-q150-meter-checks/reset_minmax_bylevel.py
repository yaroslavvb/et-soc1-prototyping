"""Post hoc, desk only: card 1's SRAM-rail min/avg and max/avg in the TEL reset windows, split idle (board < 40 W) and busy
(board >= 40 W), steady samples only (as reset_minmax_steady.py)."""
import gzip, json, sys, statistics as st, glob, os
RAWDIR = sys.argv[1]
out = {}
for card in ('aifoundry1-c1', 'aifoundry2', 'aifoundry3'):
    bins = {'idle': [], 'busy': []}
    for f in sorted(glob.glob(os.path.join(RAWDIR, card, 'tel', 'p*', 'reset.jsonl.gz'))):
        prev = None
        for line in gzip.open(f, 'rt'):
            try:
                d = json.loads(line)
            except Exception:
                continue
            s = d.get('sp'); sr = d.get('since_reset_ms', -1); b = d.get('board_w')
            ok = (s and sr is not None and sr >= 700 and b is not None and prev is not None
                  and abs(b - s['board_avg_w']) < 0.5 and abs(b - prev) < 0.5)
            prev = b
            if not ok:
                continue
            a, mn, mx = s['sram_w']
            if a > 0.3 and mx < 65:
                bins['idle' if b < 40 else 'busy'].append((mn / a, mx / a, a, b))
    out[card] = {k: ({'n': len(v), 'min_over_avg': round(st.median(x[0] for x in v), 4),
                      'max_over_avg': round(st.median(x[1] for x in v), 4),
                      'sram_avg_W': round(st.median(x[2] for x in v), 3), 'board_W': round(st.median(x[3] for x in v), 2)}
                     if v else None) for k, v in bins.items()}
print(json.dumps(out, indent=1))
