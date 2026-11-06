"""Post hoc, desk only: the highest minion-rail average and board reading in E80's committed aifoundry2 telemetry (tel/*.jsonl.gz),
against the 16-bit milliwatt field of the PMIC's rail statistics (65.535 W)."""
import gzip, json, sys, glob
best = []; nb = 0
for f in sorted(glob.glob(sys.argv[1] + '/*/tel/*.jsonl.gz')):
    for line in gzip.open(f, 'rt'):
        try:
            d = json.loads(line)
        except Exception:
            continue
        s = d.get('sp')
        if not s:
            continue
        nb += 1
        best.append((s['minion_w'][0], s['minion_w'][2], d.get('board_w') or 0.0, s.get('board_avg_w') or 0.0, f.split('/')[-1]))
print('samples', nb)
best.sort(reverse=True)
for b in best[:3]:
    print('minion avg %.3f  minion max %.3f  board %.2f  board_avg %.2f  %s' % b)
print('max board_w %.2f' % max(b[2] for b in best))
