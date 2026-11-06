"""Post hoc, desk only. The TEL block's 1 s statistics-reset windows (committed raw, 25-26 Sep 2026), steady samples only:
board_w within 0.3 W of the PMIC's board average and of the previous sample, at least 700 ms after the reset.
Per card and rail: the PMIC's min/avg and max/avg, and the SRAM rail's level against the other rails."""
import gzip, json, sys, statistics as st, glob, os
RAWDIR = sys.argv[1]
out = {}
for card in ('aifoundry1-c1', 'aifoundry2', 'aifoundry3'):
    rows = {r: [] for r in ('minion_w', 'sram_w', 'noc_w')}
    lv = []
    for f in sorted(glob.glob(os.path.join(RAWDIR, card, 'tel', 'p*', 'reset.jsonl.gz'))):
        prev = None
        for line in gzip.open(f, 'rt'):
            try:
                d = json.loads(line)
            except Exception:
                continue
            s = d.get('sp'); sr = d.get('since_reset_ms', -1); b = d.get('board_w')
            ok = (s and sr is not None and sr >= 700 and b is not None and prev is not None
                  and abs(b - s['board_avg_w']) < 0.3 and abs(b - prev) < 0.3)
            prev = b
            if not ok:
                continue
            for r in rows:
                a, mn, mx = s[r]
                if a > 0.3 and mx < 65 and mn < 65:
                    rows[r].append((mn / a, mx / a, a, mn, mx))
            lv.append((b, s['sram_w'][0], s['sram_w'][1], s['sram_w'][2], s['minion_w'][0]))
    out[card] = {}
    for r, v in rows.items():
        if not v:
            out[card][r] = None; continue
        out[card][r] = {'n': len(v),
                        'min_over_avg': round(st.median(x[0] for x in v), 4),
                        'max_over_avg': round(st.median(x[1] for x in v), 4),
                        'mid_over_avg': round(st.median((x[0] + x[1]) / 2 for x in v), 4),
                        'avg_W_median': round(st.median(x[2] for x in v), 3),
                        'min_W_median': round(st.median(x[3] for x in v), 3),
                        'max_W_median': round(st.median(x[4] for x in v), 3)}
    if lv:
        out[card]['board_W_median_steady'] = round(st.median(x[0] for x in lv), 2)
print(json.dumps(out, indent=1))
