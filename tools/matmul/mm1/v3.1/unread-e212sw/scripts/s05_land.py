#!/usr/bin/env python3
"""unread-e212sw (Q218) step 5: the land dir (new files only): land/tools/matmul/mm1/v3.1/unread-e212sw/ with the README (the order of the
hashes and their times, the results), the declaration, the forecasts, the scores, the step-1 inputs, the scripts (the box's paths replaced
by <W> and <LAB>) and SHA256SUMS. Desk. Run: /usr/bin/python3 -I -B s05_land.py <lane dir>
"""
import csv
import hashlib
import json
import os
import re
import shutil
import sys

L = os.path.abspath(sys.argv[1])
W = '<W>'
LAB = '<LAB>'
DST = os.path.join(L, 'land', 'tools', 'matmul', 'mm1', 'v3.1', 'unread-e212sw')
assert not os.path.exists(DST), 'land dir exists: no overwrite'
os.makedirs(os.path.join(DST, 'scripts'))
os.makedirs(os.path.join(DST, 'inputs'))
os.makedirs(os.path.join(DST, 'logs'))


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


def clean(t):
    t = t.replace(W + '/out/unread-e212sw', '<W>/out/unread-e212sw').replace(W, '<W>').replace(LAB, '<LAB>')
    t = re.sub(r'/tmp/cl' r'aude-\d+/[^\s\'"]*', '<scratch>', t)
    return t


for f in ('DECLARED-unread.md', 'declared-unread.json', 'forecasts-unread.csv', 'forecasts-unread.json'):
    shutil.copy2(os.path.join(L, f), os.path.join(DST, f))
for f in ('scores-unread.json', 'scores-unread-runs.csv', 'scores-unread-cases.csv'):
    shutil.copy2(os.path.join(L, 'work', 'step3', f), os.path.join(DST, f))
for f in ('runs-listed.json', 'phi-declared.json', 'earlier-lanes.json'):
    shutil.copy2(os.path.join(L, 'work', 'step1', f), os.path.join(DST, 'inputs', f))
scripts_as_run = {}
for f in sorted(os.listdir(os.path.join(L, 'scripts'))):
    if not f.endswith(('.py', '.sh')):
        continue
    src = os.path.join(L, 'scripts', f)
    scripts_as_run[f] = sha(src)
    open(os.path.join(DST, 'scripts', f), 'w').write(clean(open(src).read()))
for f in ('progress.txt', 'step1-sha256.txt', 'step2-sha256.txt', 'step3-sha256.txt', 's03_score.out', 's04_recheck.out',
          'v3-sha256sum-c.txt', 'counts-sha256sum-c.txt'):
    open(os.path.join(DST, 'logs', f), 'w').write(clean(open(os.path.join(L, 'logs', f)).read()))

S = json.load(open(os.path.join(DST, 'scores-unread.json')))
CS = list(csv.DictReader(open(os.path.join(DST, 'scores-unread-cases.csv'))))
V = S['pass_rule_against_N']
R = S['reported']
G = S['groups']


def fs(s, unit='%'):
    return '-' if not s else f"{s['rms_pct']:.2f}{unit} ({s['mean_pct']:+.2f}), n {s['n']}"


def p(x):
    return '-' if x in ('', None) else f'{100 * float(x):+.1f}'


o = []
w = o.append
w('# MM1-v3\'s switch route on runs it never read in energy: an UNREAD test with the new switch counts (unread-e212sw, Q218, Wed 18 Nov 2026)')
w('')
w('**Label: UNREAD.** MM1-v3 (landed b1493082) and the switch counts it lacked (fix-v31counts, `SHA256SUMS` c74c2d49..., frozen by the '
  'orchestrator\'s post #2.7.2.1.1 at 06:28:37 PST) were both frozen before this lane read any power, energy or seconds of the runs scored here. '
  '**Not blind:** the data existed, the data lanes had read them, and two of MM1-v3\'s design lanes had tabulated some of them (`DECLARED-unread.md` section g). '
  'Desk only: no card, no simulator, nothing refitted, no constant changed.')
w('')
w('The owner\'s words that set the matmul focus (Mon 16 Nov 2026, a voice transcription, where "matte mold" is the matmul): "I want to have a model which '
  'predicts matte mold energy and number of transistor switches and clock cycles." No card counts switches. The count can be checked only through '
  'energy, when only the data changes (E210). Here the check is made on data patterns MM1-v3 could not price before, because their kinds had no count '
  '(MM1-v3 README section 7).')
w('')
w('## 0. On one screen')
w('')
w(f"- **Verdict (the declared pass rule, decided by `scripts/s03_score.py`): {S['VERDICT']}.** P1-P4 all hold against the declared null N, which is each format's "
  'mean of the counted kinds (zeros, ones, random) priced by MM1-v3 itself at the run\'s own conditions.')
w(f"- **Q1, W over idle given the run's measured seconds**, group A, {V['Q1']['n_cases']} cases: MM1-v3 with the new counts reads **{V['Q1']['V3']['rms_pct']:.2f}% rms "
  f"({V['Q1']['V3']['mean_pct']:+.2f})**, against N's {V['Q1']['N']['rms_pct']:.2f}% ({V['Q1']['N']['mean_pct']:+.2f}). MM1-v3 is closer on "
  f"{V['Q1']['V3_closer']} cases and N on {V['Q1']['N_closer']}, with {V['Q1']['ties']} ties (exact sign test p = {V['Q1']['p_two_sided']:.1e}).")
w(f"- **Q2, the data-dependent power as a share of D** (E210's registered metric), {V['Q2']['n_cases']} cases with in-session random and zeros: "
  f"**{V['Q2']['V3']['rms_pct']:.2f}% of D rms ({V['Q2']['V3']['mean_pct']:+.2f})**, against N's {V['Q2']['N']['rms_pct']:.2f}% "
  f"({V['Q2']['N']['mean_pct']:+.2f}). MM1-v3 is closer on {V['Q2']['V3_closer']} of {V['Q2']['non_tied']} (p = {V['Q2']['p_two_sided']:.4f}).")
ga = G['A']
w(f"- **By format (group A, Q1 / Q2):** fp32 {fs(ga['fmt=fp32']['V3']['Q1_cases'])} / {fs(ga['fmt=fp32']['V3']['Q2_cases'], '% of D')}; "
  f"fp16 {fs(ga['fmt=fp16']['V3']['Q1_cases'])} / {fs(ga['fmt=fp16']['V3']['Q2_cases'], '% of D')}; "
  f"int8 {fs(ga['fmt=int8']['V3']['Q1_cases'])} / {fs(ga['fmt=int8']['V3']['Q2_cases'], '% of D')}. fp32's count is gate-level, and the "
  'route holds best there. fp16\'s count is estimated (RTL x the fp32 ratio) and runs high: MM1-v3 over-forecasts its patterns\' data share by about 7% of D. '
  'int8\'s count leaves out the arithmetic, and its worst case is `i8_pm1`, at +18.8% of D.')
nt = ga['not tabulated by any MM1-v3 design/spec lane']
w(f"- **The cleanest part:** no MM1-v3 design or spec lane tabulated these runs before the freeze ({nt['n_cases']} cases: E212 a2c0-S2's 8 on aifoundry2 under its "
  f"governor, E206 arm A's p112 and E207's 6 points). There MM1-v3 reads Q1 {fs(nt['V3']['Q1_cases'])} and Q2 {fs(nt['V3']['Q2_cases'], '% of D')}. "
  f"aifoundry2's 8 alone read Q1 {fs(ga['card=aifoundry2 card 0']['V3']['Q1_cases'])}.")
r1 = R['against_V1_where_it_applies']['Q1']
w(f"- **REPORTED:** against the stricter null N2 (ones and random only), MM1-v3 also wins every condition: Q1 {R['against_N2']['Q1']['N2']['rms_pct']:.2f}%, "
  f"Q2 {R['against_N2']['Q2']['N2']['rms_pct']:.2f}% of D. Against **MM1-v1's kind term**, which applies on aifoundry3's 10 E206/E207 points, MM1-v1 reads "
  f"{r1['V1']['rms_pct']:.2f}% and MM1-v3 {r1['V3']['rms_pct']:.2f}%, NOT DECIDED ({r1['V3_closer']} of {r1['non_tied']}). MM1-v1 prices each real tile "
  'from ledger v2\'s per-tile row or a frozen per-tile prediction (and E206 arm A\'s points were in its own in-sample scoring), while MM1-v3\'s route '
  'prices them from the count at one constant per format. With phi = 1 for every new kind, '
  f"group A reads Q1 {fs(ga['all']['V3phi1']['Q1_cases'])}, so the declared phi rule helps.")
w(f"- REPORTED, the checkpoint's other scorings (per run, group A): J at rest given t {fs(ga['all']['V3']['Q3_J_at_rest_given_t_runs'])}; J over idle with "
  f"the seconds forecast {fs(ga['all']['V3']['Q4_J_over_idle_t_forecast_runs'])}. **Group B** (E206 fp32 real, phi only, 3 points): Q1 "
  f"{fs(G['B']['all']['V3']['Q1_cases'])}, Q2 {fs(G['B']['all']['V3']['Q2_cases'], '% of D')}. **Group C** (E212's 7 gen-sparse50 runs, the committed "
  f"sparse50 kind): Q1 {fs(G['C']['all']['V3']['Q1_cases'])}, Q2 {fs(G['C']['all']['V3']['Q2_cases'], '% of D')}.")
w('- Every case\'s configuration (card, kernel, arm, format, mask, clock) is in MM1-v3\'s energy fit with other kinds (a configuration twin). Every kind is new '
  'to the fit, so the test is of the data term on known configurations, not of new shapes.')
w('')
w('## 1. What was scored (`DECLARED-unread.md` section a)')
w('')
w('- **Group A** (the pass rule\'s pool): 46 E212 runs (aifoundry1 card 1 sessions S2 and S3, 38 runs; aifoundry2 card 0 session S2, 8 runs), 19 plan-tile '
  'kinds (fp32 10, fp16 5, int8 4), at `gemmL1x1x1` on 32 and 16 shires and at `gemmL4x8x8`. Also 13 E206/E207 points (26 runs): E206\'s fp16 and int8 real tiles '
  'on aifoundry3 and aifoundry1 card 1, and E207\'s e37, real:blind4 (three formats) and blind3. Each had no switch count in MM1-v3 and has one in the '
  'frozen counts. All 59 entered energy by the loaders\' own rules, and none was set aside.')
w('- **Group B** (REPORTED): E206\'s fp32 real points (p110 and p111 on aifoundry3, p111 on card 1). Their count was committed, and only phi was missing.')
w('- **Group C** (REPORTED): E212\'s 7 gen-sparse50 runs (`sparse50f`, `sparse50i`), the committed sparse50 kind. MM1-v3 had read them for time only.')
w('- **Not scored for Q2:** 13 group A entries have no in-session random-and-zeros pair: a2c0-S2\'s two 1x1x1 full-chip runs, E206 p112 (arm A) and p113 and p115 (both arms), and '
  'E207\'s six. Group C\'s a1c0-S2 run lost its random reference to the loader\'s rule (that reference run is capped).')
w('')
w('## 2. The order, the hashes and their times (Pacific, from the box\'s clock; `logs/progress.txt`)')
w('')
w('| when (PST, Wed 18 Nov 2026) | step | what was hashed |')
w('|---|---|---|')
w('| 06:30:22 | before step 1 | the counts\' land dir: `sha256sum -c SHA256SUMS` 71 of 71 OK, `SHA256SUMS` c74c2d49c336159f6ca63aad2652601a10e22d6a8b5db00d46c66bfb1cf8aa7f |')
w('| 06:41:58-06:41:59 | step 0 | work copies by `git archive` of GitHub main 8e91dda6: MM1-v3 (its `SHA256SUMS` c24efc14..., 170/170 OK), MM1-v1 (77/77), E212\'s registration (87/87); the counts copied (71/71) |')
w('| **06:53:28** | **step 1, the declaration** | `DECLARED-unread.md` f1daf832cc0078ef8fe90d108ce646cd3d656ca96634928deb2cfe6787aae44f, `declared-unread.json` 5eb2c93d2d60640347bdd6f827f2800cccb6bfd96ea6744f8e5036839a4c03cc; every step-1 file in `logs/step1-sha256.txt` (8182bf85...) |')
w('| 06:55:50 | step 2 starts | `sha256sum -c SHA256SUMS` in the counts\' land dir and in the work copy: 71 of 71 OK each, `SHA256SUMS` c74c2d49... |')
w('| **06:56:16** | **step 2, the forecasts** | `forecasts-unread.csv` 2c26f0138f03f98b52686adee629cf1235364aad86f89aec59e92f11f658c9ee, `forecasts-unread.json` 8938bbebd1a6db028d55602773e7c2bce7286f6e378f2bcede948f82deb79f01, `s02_forecast.py` c8166622... |')
w('| 06:59:05 | the scorer, before the read | `s03_score.py` 74df0a0688179a22c2f65c5567a7989eed0f6940abff6ba308aab176bdb743ab (it refuses to run unless the declaration and the forecasts hash as above) |')
w(f"| **{S['start_pst'][16:24]}-{S['end_pst'][16:24]}** | **step 3, the first read of the test runs and the score** | `scores-unread.json` a535d78c..., `scores-unread-runs.csv` 892628bb..., `scores-unread-cases.csv` 78cfa3fb... (logged 07:00:09) |")
w('| 07:00:50 | step 4, a re-check | the verdict\'s four numbers re-derived from the cases CSV alone, and one run by hand from the committed data file (`logs/s04_recheck.out`) |')
w('')
w('Every file here, with the scripts as run, is in `SHA256SUMS`. The scripts in `scripts/` are the scripts as run, with the box\'s paths replaced by `<W>` and `<LAB>`. '
  'Their as-run sha256 are in the logs and in the table at the end.')
w('')
w('## 3. How each figure was made (summary; the declaration is the rule)')
w('')
w('- **MM1-v3 (V3):** the landed predictor, unchanged. The frozen counts were added as rows of the tables `counts()` reads (fp32 at GEMM states; fp16 and int8 in '
  'the switch-table form), with no existing row touched. phi follows the declared desk rule, MM1-v3\'s own formula `kinds_v3.phi` over each kind\'s tile files. '
  'Each run\'s W over idle is frozen in step 2 in a form exact in its measured conditions, W = [K0 + g G(f) + (1e6/t)(sV K1 + (1 + xi (sV - 1)) K2)] x '
  '(1 + 0.0048 (T0 - 50)). In step 3 that form equals the predictor called at the measured conditions to 4.4e-16 (193 calls).')
w('- **N:** the mean of MM1-v3\'s own W for zeros, ones and random at the run\'s conditions. N2 is the same over ones and random. **V1:** MM1-v1 frozen, '
  'with its own kind term where it has a source.')
w('- **Q1** = W_fc / W_meas - 1 at W_meas >= 3 W (every scored entry is above 3 W). **Q2** = [(W_fc(P) - W_fc(R)) - (W_P - W_R)] / D, with D = W_R - W_Z '
  'measured in the same session (E212) or experiment arm (E206).')
w('- **Readings:** E212 from each committed session file at GitHub main 8e91dda6, byte-equal to MM1-v3\'s vendored copies. The reduction is `data_v3.mms_runs`\'s own, and '
  'equals it on 1,942 fields of the reference runs. E206/E207 come from MM1-v3\'s own loader records, whose vendored inputs are byte-equal to the committed data files.')
w('')
w('## 4. Results by group, card and format (rms % (signed mean), n; Q2 in % of D)')
w('')
w('| set | cases | Q1 MM1-v3 | Q1 N | Q1 N2 | Q2 MM1-v3 | Q2 N | Q2 N2 |')
w('|---|---:|---|---|---|---|---|---|')
for g in ('A', 'B', 'C'):
    for k in ['all'] + sorted(x for x in G[g] if x.startswith(('card=', 'fmt=', 'source='))) + \
            ['tabulated by an MM1-v3 design/spec lane', 'not tabulated by any MM1-v3 design/spec lane']:
        v = G[g].get(k)
        if not v or v['n_cases'] == 0:
            continue
        w(f"| {g}: {k} | {v['n_cases']} | {fs(v['V3']['Q1_cases'])} | {fs(v['N']['Q1_cases'])} | {fs(v['N2']['Q1_cases'])} | "
          f"{fs(v['V3']['Q2_cases'])} | {fs(v['N']['Q2_cases'])} | {fs(v['N2']['Q2_cases'])} |")
w('')
w('Per run (group A, 59): Q1 MM1-v3 ' + fs(ga['all']['V3']['Q1_runs']) + '; Q2 ' + fs(ga['all']['V3']['Q2_runs']) + ' (46 runs with a D).')
w('')
w('## 5. Every case (group A, then B, then C; errors in %, Q2 in % of D; the share s = (W - W_zeros) / D)')
w('')
w('| group | case | runs | W over idle measured (W) | D (W) | s measured | s MM1-v3 | Q1 MM1-v3 | Q1 N | Q1 V1 | Q2 MM1-v3 | Q2 N |')
w('|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|')
for c in CS:
    w(f"| {c['group']} | `{c['case']}` | {c['n_runs']} | {float(c['W_meas']):.2f} | {('%.2f' % float(c['D_W'])) if c['D_W'] else '-'} | "
      f"{('%.3f' % float(c['s_meas'])) if c['s_meas'] else '-'} | {('%.3f' % float(c['s_V3'])) if c['s_V3'] else '-'} | {p(c['e1_V3'])} | {p(c['e1_N'])} | "
      f"{p(c['e1_V1'])} | {p(c['e2_V3'])} | {p(c['e2_N'])} |")
w('')
w('The per-run table, with every condition and every model, is `scores-unread-runs.csv`.')
w('')
w('## 6. The pass rule, and the reported variants')
w('')
w('| test | Q1: MM1-v3 / other rms, closer, p | Q2: MM1-v3 / other rms, closer, p | verdict |')
w('|---|---|---|---|')


def hrow(name, h, other):
    def one(q):
        x = h[q]
        if not x.get('V3') or not x.get(other):
            return '-'
        return f"{x['V3']['rms_pct']:.2f} / {x[other]['rms_pct']:.2f}%, {x['V3_closer']} of {x['non_tied']}, p {x['p_two_sided']:.2g}"
    return f"| {name} | {one('Q1')} | {one('Q2')} | {h['verdict']} |"


w(hrow('**declared: group A against N**', V, 'N'))
w(hrow('REPORTED: group A against N2', R['against_N2'], 'N2'))
w(hrow('REPORTED: against V1 where it applies (aifoundry3)', R['against_V1_where_it_applies'], 'V1'))
w(hrow('REPORTED: E212 alone against N', R['E212_alone_against_N'], 'N'))
w(hrow('REPORTED: E206/E207 alone against N', R['E206_E207_alone_against_N'], 'N'))
w('')
w('## 7. What this cannot say')
w('')
w('- **It is not blind.** The model\'s constants and the counts never saw these runs\' energy. But one of MM1-v3\'s design lanes had printed 14 of the 46 E212 runs\' '
  'shares of D, and its spec lane had tabulated 38 of them before MM1-v3\'s form was chosen. The 15 cases no design lane tabulated are given apart (section 4).')
w('- **Known configurations:** every case\'s configuration is in MM1-v3\'s energy fit with other kinds, and only the kind is new. Their time is in MM1-v3\'s time fit '
  '(time is kind-blind), and Q1 and Q2 use the measured time.')
w('- **Energy through the count, not the count:** no card counts switches. fp16\'s count is an RTL estimate, int8\'s leaves out the arithmetic, and both are at launch '
  'points, not GEMM states. The fp16 bias (+7.4% of D) and `i8_pm1` (+18.8% of D) are where the count and the card part.')
w('- **Narrow shapes:** E212\'s patterns ran at `gemmL1x1x1` (32 and 16 shires) and `gemmL4x8x8` on two cards; fp16 and int8 on card 1 only. Q2 for E206/E207 '
  'rests on 2 points.')
w('- **phi is a desk rule,** never checked on a card\'s line order; with phi = 1 the group A Q1 error rises from 6.83% to 8.29%.')
w('')
w('## 8. Files and how to reproduce')
w('')
w('- `DECLARED-unread.md`, `declared-unread.json`: the declaration (step 1). `inputs/runs-listed.json` holds the runs from schedules, queues and point files; '
  '`inputs/phi-declared.json` holds phi from tile bytes; `inputs/earlier-lanes.json` holds the search for earlier reads.')
w('- `forecasts-unread.csv`, `forecasts-unread.json`: the forecasts (step 2), 133 rows (69 test entries and 64 references), every model\'s frozen coefficients.')
w('- `scores-unread.json`, `scores-unread-runs.csv`, `scores-unread-cases.csv`: the score (step 3).')
w('- `scripts/`: `s00_setup.sh` (work copies), `s01_list.py`, `s01g_search.py`, `s01h_context.py`, `s01p_phi.py`, `s01d_declare.py`, `s01m_md.py` '
  '(step 1), `s02_forecast.py` (step 2), `s03_score.py` (step 3), `s04_recheck.py` (step 4) and `s05_land.py` (this folder). `logs/` holds the lane\'s log and the '
  'scorer\'s output.')
w('- To reproduce, from a checkout of GitHub main 8e91dda6 (or any commit where `tools/matmul/mm1/v3` is b1493082\'s) and the counts folder: put MM1-v3, '
  'MM1-v1 and E212\'s registration under `work/lab/` and the counts under `work/counts/`, then run steps 1-4 in order. Each runs single-threaded '
  '(`OMP_NUM_THREADS=1` and the like), with `/usr/bin/python3` 3.12.3 `-I -B` and numpy 1.26.4.')
w('')
w('**The scripts\' sha256 as run** (before the path replacement):')
w('')
w('| script | sha256 as run |')
w('|---|---|')
for f, h in sorted(scripts_as_run.items()):
    w(f'| `{f}` | `{h}` |')
w('')
open(os.path.join(DST, 'README.md'), 'w').write('\n'.join(o) + '\n')
# SHA256SUMS
lines = []
for dp, dn, fn in os.walk(DST):
    for f in sorted(fn):
        pth = os.path.join(dp, f)
        rel = os.path.relpath(pth, DST)
        if rel == 'SHA256SUMS':
            continue
        lines.append(f'{sha(pth)}  {rel}')
open(os.path.join(DST, 'SHA256SUMS'), 'w').write('\n'.join(sorted(lines, key=lambda x: x.split('  ', 1)[1])) + '\n')
bad = []
for dp, dn, fn in os.walk(DST):
    for f in fn:
        t = open(os.path.join(dp, f), errors='replace').read()
        if ('/' + 'home' + '/') in t or ('yaro' + 'slavvb') in t or ('/tmp/' + 'claude') in t:
            bad.append(os.path.relpath(os.path.join(dp, f), DST))
print('land files', sum(len(fn) for _, _, fn in os.walk(DST)), '; files with a home path, login or scratch path:', bad)
print('SHA256SUMS', sha(os.path.join(DST, 'SHA256SUMS')))
