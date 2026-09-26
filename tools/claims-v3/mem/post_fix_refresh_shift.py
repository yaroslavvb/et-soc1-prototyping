"""Post-data correction (26 Sep 2026, AMENDMENTS.md "C1"): re-run the reducer's pre-registered extra_values.py (P5b, P6r) on every kept V3-MEM pass with the refresh series
re-referenced to the pass's own L1 hit (extra_values.py loads refresh_jit with shift 0; everything else it shifts)."""
import sys, os, json, gzip, shutil, tempfile, io, contextlib, statistics as st
OUT = sys.argv[1] if len(sys.argv) > 1 else 'docs/reports/data/2026-09-25-claims-v3/results/mem-refresh-shift.json'
sys.path.insert(0, 'tools/claims-v3/mem/prereg')
import extra_values as ev
RAW = 'docs/reports/data/2026-09-25-claims-v3/raw'
meta = json.load(open('docs/reports/data/2026-09-25-claims-v3/results/mem.passes.json'))
orig = ev.load
res = {}
for card in meta['cards']:
    rows = []
    for pk in meta['kept'][card]['x1']:
        tmp = tempfile.mkdtemp()
        for n in ('ladder', 'decomp', 'refresh_jit'):
            with gzip.open(f'{RAW}/{card}/mem/{pk}/{n}.json.gz', 'rt') as f, open(f'{tmp}/{n}.json', 'w') as o: shutil.copyfileobj(f, o)
            shutil.copy(f'{RAW}/{card}/mem/{pk}/{n}.u32', f'{tmp}/{n}.u32')
        out = {}
        for mode in ('as registered', 'shifted'):
            def load(d, name, shift, _m=mode):
                if name == 'refresh_jit' and _m == 'shifted':
                    shift = SHIFT[0]
                return orig(d, name, shift)
            ev.load = load
            _, labs, r = orig(tmp, 'ladder', 0)
            SHIFT = [int(round(st.median(v + 5 for l, v in zip(labs, r) if l[0] == 'ladder' and l[2] in (-1, 0)) - 10))]
            sys.argv = ['x', '--data', tmp]
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                ev.main()
            j = json.loads(buf.getvalue())
            out[mode] = {k: j[k] for k in ('l1_shift', 'P5b_closed_minus_open_means', 'P6r_hit_no_refresh', 'P6r_hit_refresh', 'P6r_counts')}
        shutil.rmtree(tmp)
        rows.append((pk, out))
        print(card, pk, 'registered P5b %.2f P6r %.3f/%.4f | shifted P5b %.2f P6r %.4f (%s) / %.4f' % (
            out['as registered']['P5b_closed_minus_open_means'], out['as registered']['P6r_hit_no_refresh'], out['as registered']['P6r_hit_refresh'],
            out['shifted']['P5b_closed_minus_open_means'], out['shifted']['P6r_hit_no_refresh'], out['shifted']['P6r_counts'], out['shifted']['P6r_hit_refresh']))
    res[card] = rows
json.dump(res, open(OUT, 'w'), indent=1)
