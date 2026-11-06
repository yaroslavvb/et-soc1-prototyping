"""Post hoc, desk only: the PMIC's regulator set points (reg_mv, GET_MODULE_VOLTAGE) against the die's voltage monitors
(die_mv, GET_ASIC_VOLTAGE; sp.*_mv, the SP stats' PVT averages), per card, idle samples of committed telemetry."""
import gzip, json, sys, statistics as st, glob, os
out = {}
for card, pat in (('aifoundry1-c1', sys.argv[1] + '/aifoundry1-c1/tel/p*/reset.jsonl.gz'),
                  ('aifoundry2', sys.argv[1] + '/aifoundry2/tel/p*/reset.jsonl.gz'),
                  ('aifoundry3', sys.argv[1] + '/aifoundry3/tel/p*/reset.jsonl.gz')):
    acc = {}
    for f in sorted(glob.glob(pat)):
        for line in gzip.open(f, 'rt'):
            try:
                d = json.loads(line)
            except Exception:
                continue
            if 'reg_mv' not in d or 'die_mv' not in d or d.get('board_w', 99) > 45:
                continue
            for k in ('minion', 'sram', 'noc', 'ddr', 'maxion'):
                acc.setdefault(k, []).append((d['reg_mv'].get(k), d['die_mv'].get(k)))
    out[card] = {k: {'reg_mv_median': st.median(a for a, b in v), 'die_mv_median': st.median(b for a, b in v),
                     'die_minus_reg_mv': st.median(b - a for a, b in v), 'n': len(v)} for k, v in acc.items()}
print(json.dumps(out, indent=1))
