"""Post hoc, desk only: after each statistics reset in the TEL block's windows (committed raw, 25-26 Sep 2026), each rail's
PMIC average relative to the same window's last sample, by time since the reset, idle windows only (board_w < 40 W and
within 0.5 W of the previous sample throughout). Shows how each rail's average restarts."""
import gzip, json, sys, statistics as st, glob, os
RAWDIR = sys.argv[1]
out = {}
for card in ('aifoundry1-c1', 'aifoundry2', 'aifoundry3'):
    curves = {r: {} for r in ('minion_w', 'sram_w', 'noc_w')}
    for f in sorted(glob.glob(os.path.join(RAWDIR, card, 'tel', 'p*', 'reset.jsonl.gz'))):
        win = []
        rows = []
        for line in gzip.open(f, 'rt'):
            try:
                rows.append(json.loads(line))
            except Exception:
                pass
        # split into windows at since_reset_ms drops
        cur = []
        last = None
        for d in rows:
            sr = d.get('since_reset_ms', -1)
            if sr is None or sr < 0 or 'sp' not in d:
                continue
            if last is not None and sr < last:
                win.append(cur); cur = []
            cur.append(d); last = sr
        if cur:
            win.append(cur)
        for w in win:
            bs = [d.get('board_w') or 0 for d in w]
            if not bs or max(bs) >= 40 or max(abs(a - b) for a, b in zip(bs, bs[1:] or bs)) > 0.5 or len(w) < 8:
                continue
            for r in curves:
                ref = w[-1]['sp'][r][0]
                if ref <= 0.3:
                    continue
                for d in w:
                    b = int(d['since_reset_ms'] // 100) * 100
                    curves[r].setdefault(b, []).append(d['sp'][r][0] / ref)
    out[card] = {r: {str(k): round(st.median(v), 3) for k, v in sorted(c.items()) if len(v) >= 5} for r, c in curves.items()}
print(json.dumps(out, indent=1))
