"""Post hoc desk check (critic-q140), unverified: the paired-anchor card scale's 95% half-width with t quantiles, using EACH
anchor's own committed passes (pool 6's anchors included: their per-pass D are in E153's and E157's primary runs.csv, one run
a pass), instead of copying E78's error onto pool 6's anchors as Q140(c) check 3 and lab a7fbb2ac do.
Standard library; the t quantile is imported from the committed anchor_scale_t95.py (itself ablcore.py's, verbatim)."""
import csv, sys, os, json, math, statistics as st, collections, importlib.util
R = sys.argv[1]
spec = importlib.util.spec_from_file_location('t95', os.path.join(R, 'docs/reports/data/2026-11-04-q140-anchor-scale-t95/anchor_scale_t95.py'))
T = importlib.util.module_from_spec(spec); spec.loader.exec_module(T)
def per_pass(path):
    by = collections.defaultdict(lambda: collections.defaultdict(list))
    for r in csv.DictReader(open(path)):
        if r.get('fail') not in ('0', '', None):
            continue
        if r['D'] in ('', None):
            continue
        by[r['item']][r['pass']].append(float(r['D']))
    return {k: [st.mean(v) for p, v in sorted(pp.items())] for k, pp in by.items()}
A3 = per_pass(os.path.join(R, 'docs/reports/data/2026-11-03-e153-blind6-aifoundry3/runs.csv'))
C1 = per_pass(os.path.join(R, 'docs/reports/data/2026-11-03-e157-blind6-card1/runs.csv'))
fams = {'int8': ['int8.full', 'int8.anchor6_full'],
        'floats': ['fp32.randn', 'fp32.anchor6_randn', 'fp16.randn', 'fp16.anchor6_randn']}
out = {}
for fam, names in fams.items():
    parts = []  # (variance component of the mean scale, df)
    rows = {}
    ratios = []
    for n in names:
        a, c = A3[n], C1[n]
        ma, mc = st.mean(a), st.mean(c)
        r = mc / ma
        va = (st.stdev(a) / ma) ** 2 / len(a)   # relative variance of the aifoundry3 mean
        vc = (st.stdev(c) / mc) ** 2 / len(c)
        rows[n] = {'ratio': round(r, 5), 'n_a3': len(a), 'n_c1': len(c), 'rel_sd_a3': round(st.stdev(a) / ma, 5),
                   'rel_sd_c1': round(st.stdev(c) / mc, 5), 'rel_se_ratio': round(math.sqrt(va + vc), 5)}
        ratios.append(r)
        k = len(names)
        parts += [((r / k) ** 2 * va, len(a) - 1), ((r / k) ** 2 * vc, len(c) - 1)]
    mean = st.mean(ratios)
    var = sum(p for p, _ in parts)
    df = var ** 2 / sum(p ** 2 / d for p, d in parts)
    se_rel = math.sqrt(var) / mean
    t = T.t_ppf(0.975, df)
    out[fam] = {'anchors': rows, 'scale_mean': round(mean, 5), 'rel_se': round(se_rel, 5), 'welch_df': round(df, 2),
                't975': round(t, 3), 'half_width_95_rel': round(t * se_rel, 5)}
json.dump(out, open(sys.argv[2], 'w'), indent=1)
for fam, o in out.items():
    print('%s: scale (mean of anchors) %.4f, rel s.e. %.2f%%, Welch df %.2f, t %.2f, 95%% half-width %.2f%%' % (
        fam, o['scale_mean'], 100 * o['rel_se'], o['welch_df'], o['t975'], 100 * o['half_width_95_rel']))
    for n, r in o['anchors'].items():
        print('    %-20s ratio %.4f  sd/pass a3 %.2f%% (n %d)  c1 %.2f%% (n %d)  rel s.e. %.2f%%' % (
            n, r['ratio'], 100 * r['rel_sd_a3'], r['n_a3'], 100 * r['rel_sd_c1'], r['n_c1'], 100 * r['rel_se_ratio']))
