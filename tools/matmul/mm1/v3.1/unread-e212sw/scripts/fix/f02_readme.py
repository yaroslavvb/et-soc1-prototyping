#!/usr/bin/env python3
"""fix-unread-e212sw (Q218) step 04: the corrected README (answers verify-unread-e212sw's findings 1-8), written to OUT/fix-unread-e212sw/README.md.

Starts from the unread lane's README (sha256 7f0ca663..., asserted) and applies exact, counted replacements; every figure that was rounded twice is
re-printed from the unchanged scorer's unrounded values (work/rerun-full.json); section 9 (dated, post hoc) is added, with the addendum's numbers
read from work/addendum/scores-e209-posthoc.json. No number of the declared score changes except where the README printed it rounded twice.
Desk. Run: /usr/bin/python3 -I -B f02_readme.py
"""
import hashlib
import json
import os

W = '<W>'
ME = os.path.join(W, 'out', 'fix-unread-e212sw')
LANDU = os.path.join(W, 'out', 'unread-e212sw', 'land', 'tools', 'matmul', 'mm1', 'v3.1', 'unread-e212sw')


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


SRC = os.path.join(LANDU, 'README.md')
assert sha(SRC) == '7f0ca663d9b27d7df1dd38c9988331df7fadd27940e9b0a30bdfc272d14c0a38'
t = open(SRC).read()
RF = json.load(open(os.path.join(ME, 'work', 'rerun-full.json')))
AS_P = os.path.join(ME, 'work', 'addendum', 'scores-e209-posthoc.json')
assert sha(AS_P) == '8ab39919582658f6ab7c3f78b45c213eda837c27da80ece406c2ef3a62fa8c5c'
AS = json.load(open(AS_P))
G = RF['groups_full']


def f2(x):
    return f'{x:.2f}'


def s2(x):
    return f'{x:+.2f}'


# the unrounded values behind every figure that was rounded twice (asserted against the slips list of step 02)
nQ1 = RF['pass_rule_full']['Q1']['N']['rms_full']                        # 24.965160
v1V3 = RF['reported_full']['against_V1_where_it_applies']['Q1']['V3']['rms_full']   # 7.824510
pr = G['A']['all']['V3']['Q1_runs']['mean_full']                         # 2.965008
a11N2 = G['A']['card=aifoundry1 card 1']['N2']['Q2_cases']['rms_full']   # 20.125127
a3V3 = G['A']['card=aifoundry3 card 0']['V3']['Q1_cases']['rms_full']    # 7.824510
f16N2 = G['A']['fmt=fp16']['N2']['Q1_cases']['rms_full']                 # 21.205179
e6aN2 = G['A']['source=E206A']['N2']['Q1_cases']['mean_full']            # -19.935247
b3N = G['B']['card=aifoundry3 card 0']['N']['Q2_cases']['rms_full']      # 52.785373
bAN = G['B']['source=E206A']['N']['Q2_cases']['rms_full']                # 52.785373
c11N = G['C']['card=aifoundry1 card 1']['N']['Q1_cases']['mean_full']    # -10.844982
c20V3 = G['C']['card=aifoundry2 card 0']['V3']['Q1_cases']['mean_full']  # 3.195480
cntV3 = G['C']['not tabulated by any MM1-v3 design/spec lane']['V3']['Q1_cases']['mean_full']
assert (f2(nQ1), f2(v1V3), s2(pr), f2(a11N2), f2(a3V3), f2(f16N2), s2(e6aN2), f2(b3N), f2(bAN), s2(c11N), s2(c20V3), s2(cntV3)) == \
    ('24.97', '7.82', '+2.97', '20.13', '7.82', '21.21', '-19.94', '52.79', '52.79', '-10.84', '+3.20', '+3.20')

REPL = [
    # ---- the label paragraph: the counts' committed folder, and a pointer to the changes
    ("the switch counts it lacked (fix-v31counts, `SHA256SUMS` c74c2d49..., frozen by the orchestrator's post #2.7.2.1.1 at 06:28:37 PST) were both frozen",
     "the switch counts it lacked (fix-v31counts, `SHA256SUMS` c74c2d49..., frozen by the orchestrator's post #2.7.2.1.1 at 06:28:37 PST; committed unchanged as "
     "`tools/matmul/mm1/v3.1/counts/` in 3e8991d0 at 07:23:56 PST) were both frozen", 1),
    ("**Not blind:** the data existed, the data lanes had read them, and two of MM1-v3's design lanes had tabulated some of them (`DECLARED-unread.md` section g).",
     "**Not blind:** the data existed, the data lanes had read them, and MM1-v3's design and spec lanes had tabulated some of them; for the E206 and E207 "
     "points, so had its build lane and mm-residuals (`DECLARED-unread.md` section g and its dated note 1).", 1),
    ("Desk only: no card, no simulator, nothing refitted, no constant changed.",
     "Desk only: no card, no simulator, nothing refitted, no constant changed. **Corrected after the verify** (section 9, dated, post hoc): the declaration, "
     "the forecasts and the scores are unchanged; this README's wording, fifteen figures it had rounded twice, and an addendum (E209's three real points, "
     "missed by the declared list) are what changed.", 1),
    # ---- section 0
    (f"against N's 24.96% (-16.04). MM1-v3 is closer on 35 cases", f"against N's {f2(nQ1)}% (-16.04). MM1-v3 is closer on 35 cases", 1),
    ("- **The cleanest part:** no MM1-v3 design or spec lane tabulated these runs before the freeze (15 cases: E212 a2c0-S2's 8 on aifoundry2 under its "
     "governor, E206 arm A's p112 and E207's 6 points). There MM1-v3 reads Q1 5.08% (+1.22), n 15 and Q2 3.04% of D (-2.95), n 6. aifoundry2's 8 alone read "
     "Q1 1.34% (+0.96), n 8.",
     "- **Not tabulated by an MM1-v3 design or spec lane** (15 cases: E212 a2c0-S2's 8 on aifoundry2 under its governor, E206 arm A's p112 and E207's 6 "
     "points): Q1 5.08% (+1.22), n 15 and Q2 3.04% of D (-2.95), n 6. Seven of them (p112 and E207's six) are not clean: MM1-v3's own build lane wrote "
     "their measured W into its committed `out/points_energy_v3.csv` before the freeze, and mm-residuals' committed table holds them too. **The cleanest "
     "part is E212 a2c0-S2's 8 runs**, tabulated in energy by no MM1-v3 lane (design, spec or build) and by no residual lane: Q1 1.34% (+0.96), n 8 and "
     "Q2 3.04% of D (-2.95), n 6 (section 9.2).", 1),
    ("MM1-v1 reads 5.98% and MM1-v3 7.83%, NOT DECIDED (5 of 9).", f"MM1-v1 reads 5.98% and MM1-v3 {f2(v1V3)}%, NOT DECIDED (5 of 9).", 1),
    ("so the declared phi rule helps.",
     "so the declared phi rule helps. **Post hoc (addendum 1, section 9.1):** E209's real points e35 (int8) and e36 (fp16), which the declared list "
     "missed, read Q1 -0.01% and +4.75% (N -23.13% and -31.74%); with them group A reads 6.71% against N's 25.10%, 37 of 42, p = 4.4e-07, so the verdict "
     "is unchanged.", 1),
    # ---- section 2: one line for the two numbers seen before the declaration, one dated line for the counts' commit
    ("Their as-run sha256 are in the logs and in the table at the end.",
     "Their as-run sha256 are in the logs and in the table at the end.\n\n"
     "- **Seen before the declaration** (verify-unread-e212sw, from the harness transcript): two measured numbers, neither a group A value nor an input "
     "to any forecast: E210.md's quote of E206's S1 random-minus-zeros D (29.78 W, the reference D of group B's p110), and a1c1-S2's session rest values "
     "in its `queue.json` (29.91 W, 51 C).\n"
     "- **The counts, committed** (dated line, Wed 18 Nov 2026, fix-unread-e212sw): the counts folder used here (fix-v31counts' land dir, `SHA256SUMS` "
     "c74c2d49...) is on GitHub main unchanged as `tools/matmul/mm1/v3.1/counts/`, added by commit 3e8991d0 (07:23:56 PST): `diff -r` against the land dir "
     "used finds no difference, and `sha256sum -c` reads 71 of 71 OK (07:42:01 PST). The hashed declaration keeps the scratch name.", 1),
    # ---- section 4: the figures rounded twice, re-printed from the unrounded values
    ("| A: all | 42 | 6.83% (+2.61), n 42 | 24.96% (-16.04), n 42 |", f"| A: all | 42 | 6.83% (+2.61), n 42 | {f2(nQ1)}% (-16.04), n 42 |", 1),
    ("| 6.33% (+3.44), n 22 | 23.21% (-13.41), n 22 | 20.12% (+8.29), n 22 |", f"| 6.33% (+3.44), n 22 | 23.21% (-13.41), n 22 | {f2(a11N2)}% (+8.29), n 22 |", 1),
    ("| A: card=aifoundry3 card 0 | 10 | 7.83% (+1.95), n 10 |", f"| A: card=aifoundry3 card 0 | 10 | {f2(a3V3)}% (+1.95), n 10 |", 1),
    ("| 34.99% (-32.06), n 9 | 21.20% (-7.88), n 9 |", f"| 34.99% (-32.06), n 9 | {f2(f16N2)}% (-7.88), n 9 |", 1),
    ("| 39.16% (-37.89), n 4 | 21.92% (-19.93), n 4 |", f"| 39.16% (-37.89), n 4 | 21.92% ({s2(e6aN2)}), n 4 |", 1),
    ("| B: card=aifoundry3 card 0 | 2 | 4.85% (-2.03), n 2 | 46.67% (-46.41), n 2 | 28.38% (-27.99), n 2 | 0.75% (-0.41), n 2 | 52.78% (-52.77), n 2 |",
     f"| B: card=aifoundry3 card 0 | 2 | 4.85% (-2.03), n 2 | 46.67% (-46.41), n 2 | 28.38% (-27.99), n 2 | 0.75% (-0.41), n 2 | {f2(b3N)}% (-52.77), n 2 |", 1),
    ("| B: source=E206A | 2 | 4.85% (-2.03), n 2 | 46.67% (-46.41), n 2 | 28.38% (-27.99), n 2 | 0.75% (-0.41), n 2 | 52.78% (-52.77), n 2 |",
     f"| B: source=E206A | 2 | 4.85% (-2.03), n 2 | 46.67% (-46.41), n 2 | 28.38% (-27.99), n 2 | 0.75% (-0.41), n 2 | {f2(bAN)}% (-52.77), n 2 |", 1),
    ("| C: card=aifoundry1 card 1 | 4 | 2.27% (+1.34), n 4 | 20.36% (-10.85), n 4 |", f"| C: card=aifoundry1 card 1 | 4 | 2.27% (+1.34), n 4 | 20.36% ({s2(c11N)}), n 4 |", 1),
    ("| C: card=aifoundry2 card 0 | 2 | 3.24% (+3.19), n 2 |", f"| C: card=aifoundry2 card 0 | 2 | 3.24% ({s2(c20V3)}), n 2 |", 1),
    ("| C: not tabulated by any MM1-v3 design/spec lane | 2 | 3.24% (+3.19), n 2 |", f"| C: not tabulated by any MM1-v3 design/spec lane | 2 | 3.24% ({s2(cntV3)}), n 2 |", 1),
    ("Per run (group A, 59): Q1 MM1-v3 7.20% (+2.96), n 59;", f"Per run (group A, 59): Q1 MM1-v3 7.20% ({s2(pr)}), n 59;", 1),
    ("(46 runs with a D).",
     "(46 runs with a D).\n\n"
     "Row \"A: card=aifoundry2 card 0\" is E212 a2c0-S2's 8 runs, the cleanest part (section 9.2). The \"not tabulated\" rows mean not tabulated by an "
     "MM1-v3 design or spec lane; seven of group A's 15 such cases were tabulated by MM1-v3's build lane and by mm-residuals, and so was group B's one "
     "(E206 arm A p110). Fifteen figures in this "
     "section and in sections 0 and 6 were printed from values already rounded to 3 decimals; they are re-printed from the unrounded values (section 9.4).", 1),
    # ---- section 6
    ("| **declared: group A against N** | 6.83 / 24.96%, 35 of 40, p 1.4e-06 |", f"| **declared: group A against N** | 6.83 / {f2(nQ1)}%, 35 of 40, p 1.4e-06 |", 1),
    ("| REPORTED: against V1 where it applies (aifoundry3) | 7.83 / 5.98%,", f"| REPORTED: against V1 where it applies (aifoundry3) | {f2(v1V3)} / 5.98%,", 1),
    ("| REPORTED: E206/E207 alone against N | 7.91 / 33.36%, 13 of 13, p 0.00024 | 2.96 / 37.71%, 2 of 2, p 0.5 | NOT DECIDED |",
     "| REPORTED: E206/E207 alone against N | 7.91 / 33.36%, 13 of 13, p 0.00024 | 2.96 / 37.71%, 2 of 2, p 0.5 | NOT DECIDED |\n"
     "| REPORTED, post hoc (addendum 1, section 9.1): group A with E209's e35 and e36, against N | 6.71 / 25.10%, 37 of 42, p 4.4e-07 | "
     "unchanged (no E209 point has a share of D) | P1 and P2 hold |", 1),
    # ---- section 7
    ("The 15 cases no design lane tabulated are given apart (section 4).",
     "The 15 cases no MM1-v3 design or spec lane tabulated are given apart (section 4); seven of them were tabulated by MM1-v3's build lane and by "
     "mm-residuals, so the cleanest part is E212 a2c0-S2's 8 runs (section 9.2).", 1),
    # ---- section 8
    ("`inputs/earlier-lanes.json` holds the search for earlier reads.",
     "`inputs/earlier-lanes.json` holds the search for earlier reads (one entry, a scratch script's file name, is left out of this public copy: section 9.5). "
     "`DECLARED-unread.md.dated-note-1.md` holds the post hoc corrections to the declaration (section 9).", 1),
    ("`logs/` holds the lane's log and the scorer's output.",
     "`logs/` holds the lane's log and the scorer's output. The fix lane's scripts are in `scripts/fix/` and its logs in `logs/fix/`; addendum 1's "
     "declaration, forecasts and scores are in `addendum-1-e209/`.", 1),
    ("with `/usr/bin/python3` 3.12.3 `-I -B` and numpy 1.26.4.",
     "with `/usr/bin/python3` 3.12.3 `-I -B` and numpy 1.26.4.\n"
     "- The fix lane's steps, in order (each script asserts the hashes of the files before it): `scripts/fix/f00_setup.sh` (work copies by `git archive` "
     "of GitHub main 3e8991d0 and the counts' checks), `f01_rerun.py` (the unread lane's `s03_score.py` re-run unchanged, and the unrounded figures), "
     "`a01_declare_e209.py`, `a02_forecast_e209.py` and `a03_score_e209.py` (addendum 1: declared, forecast, then read and scored), `f02_readme.py` "
     "(this README) and `f03_land.py` (this folder); each Python step ran inside the round's CPU slot (`slotpy.sh`), single-threaded.", 1),
]
for old, new, n in REPL:
    c = t.count(old)
    assert c == n, (c, old[:90])
    t = t.replace(old, new)
import re  # noqa: E402
assert '24.96' not in t and not re.search(r'(?<![0-9])7\.83(%| /)', t) and '(+2.96)' not in t   # ('17.83%' in group C rows is another figure)

# ---------------------------------------------------------------- section 9 (new, dated, post hoc)
cs = {c['case'].split('|')[1]: c for c in AS['cases']}
P = AS['pooled_REPORTED_post_hoc']
pa, pa2, pb, pe = P['group_A_with_e35_e36_Q1_vs_N'], P['group_A_with_e35_e36_Q1_vs_N2'], P['group_B_with_e34_Q1'], P['E209_alone_Q1']
d42 = P['group_A_declared_42_Q1_vs_N']
assert (d42['V3_closer'], d42['non_tied'], d42['ties']) == (35, 40, 2)
runs = {}
import csv  # noqa: E402
for r in csv.DictReader(open(os.path.join(ME, 'work', 'addendum', 'scores-e209-posthoc-runs.csv'))):
    runs.setdefault(r['point'], []).append(r)


def pc(x):
    return f'{100 * x:+.2f}'


o = []
w = o.append
w('## 9. After the verify: what changed, and why (fix-unread-e212sw, Wed 18 Nov 2026, from 07:35 PST; post hoc)')
w('')
w('verify-unread-e212sw (07:04-07:35 PST) found that the score re-derives exactly, the order holds and the declared rule gives PASS (HOLDS WITH FIXES), '
  'with eight findings. **Unchanged:** `DECLARED-unread.md` (f1daf832...), `declared-unread.json` (5eb2c93d...), the forecasts (2c26f013..., 8938bbeb...), '
  'the scores (a535d78c..., 892628bb..., 78cfa3fb...) and every script as run. The frozen scorer, re-run unchanged at 07:44:06 PST from a fresh copy of '
  'its inputs (`scripts/fix/f01_rerun.py`), gives byte-equal CSVs and an equal JSON apart from its two clock stamps. The post hoc corrections to the '
  'declaration are in `DECLARED-unread.md.dated-note-1.md`.')
w('')
w('### 9.1 Addendum 1, post hoc: E209\'s three real points (finding 1)')
w('')
w('- **What section a missed.** By its own rule, the declared list missed three E209 points on aifoundry2 card 0 under its governor. They ran with '
  'E206\'s real2 tiles, byte-equal to the files rule e and the counts read. e35 (int8) and e36 (fp16) have no count in MM1-v3 as landed and have one in the '
  'frozen counts, so they belong in group A. e34 (fp32) has its count but no phi, so it belongs in group B. They were missed because the brief named only '
  'E212, E206 and E207, and the counts lane\'s list scanned only energy points and E212 runs.')
w('- **How they were scored.** The same rules and the same order, each step hashed before the next:')
w('  1. the addendum\'s declaration at 07:47:44 PST (`addendum-1-e209/addendum-declared-e209.json`, '
  f"{AS['addendum_declaration_sha256']});")
w(f"  2. its forecasts at 07:53:34 PST (`forecasts-e209-posthoc.json`, {AS['addendum_forecasts_sha256']}), by the unread lane's step-2 machinery "
  'unchanged, which re-made four frozen entries bit for bit;')
w('  3. the first read of E209\'s data file by this lane, and the score, at 07:55:15 PST (`scores-e209-posthoc.json`).')
w('- **Only Q1 can be scored.** E209 has no zeros point at these configurations (random only: e01, e18, e19), so the share of D is NOT SCORED.')
w('- **The figures equal the verifier\'s** own post hoc numbers to 2.2e-16.')
w('')
w('| point | group | format, shape | runs | clock (MHz) | W over idle measured (W) | Q1 MM1-v3 | Q1 N | Q1 N2 | J at rest given t | J over idle, t forecast |')
w('|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|')
for pt in ('e35', 'e36', 'e34'):
    c = cs[pt]
    fm = sum(float(r['f_mhz']) for r in runs[pt]) / len(runs[pt])
    w(f"| {pt} | {c['group']} | {c['fmt']} `{c['arm']}` | {c['n_runs']} | {fm:.1f} | {c['W_meas']:.2f} | {pc(c['e1_V3'])}% | {pc(c['e1_N'])}% | "
      f"{pc(c['e1_N2'])}% | {pc(c['e3_V3'])}% | {pc(c['e4_V3'])}% |")
w('')
w(f"- **Group A, Q1, with e35 and e36 added** (44 cases): MM1-v3 {pa['V3']['rms_pct']:.2f}% rms ({s2(pa['V3']['mean_pct'])}) against N's "
  f"{pa['other']['rms_pct']:.2f}% ({s2(pa['other']['mean_pct'])}). MM1-v3 is closer on {pa['V3_closer']} of {pa['non_tied']} non-tied cases "
  f"({pa['ties']} ties), p = {pa['p_two_sided']:.1e}. Against N2 the null reads {pa2['other']['rms_pct']:.2f}%.")
w('  - P1 and P2 hold. Q2\'s 29 cases are unchanged, so P3 and P4 are as declared.')
w('  - The pass rule would still read PASS. **The verdict of record is the declared one.**')
w(f"- **Group B with e34 added** (4 points): MM1-v3 {pb['V3']['rms_pct']:.2f}% ({s2(pb['V3']['mean_pct'])}) against N's {pb['N']['rms_pct']:.2f}%. "
  f"**E209's three alone:** MM1-v3 {pe['V3']['rms_pct']:.2f}%, N {pe['N']['rms_pct']:.2f}%, N2 {pe['N2']['rms_pct']:.2f}%.")
w('- **Label: post hoc and UNREAD, not blind.** MM1-v3 and the counts were frozen before any lane read these runs for this test. These lanes had read them earlier:')
w('  - E209\'s own lanes: card-e209 (the session and its checks), collect-e209 (the collection and the step-13 scorer, joules per point against '
  'the frozen MM1 forecasts), verify-e209d, fix-e209d and scores-e209;')
w('  - MM1-v3\'s design lane v3-design-a, which tabulated MM1-v2\'s J-over-idle error at all 45 E209 points (these three included);')
w('  - this round\'s verifier, which scored them first.')
w('')
w('### 9.2 Earlier reads, corrected (findings 2, 3, 5, 6)')
w('')
w('- **mm-residuals**, under E206 arms A and B as well as E207. Its committed table `tools/matmul/mm1/residuals/residuals-2026-11-17.csv` (a514caf0) '
  'holds the measured W over idle of E206 arm A\'s p110-p115 and arm B\'s p111 and p113-p115. v3-design-a\'s `diag_terms.py` and `diag2_groups.py` read it '
  'before MM1-v3\'s freeze.')
w('- **mm-data is withdrawn** from section g\'s E206 arm A line. Its 43 files date from 09:54-10:31 PST Mon 16 Nov, about eight hours before E206 arm A\'s '
  'data commit d7e4f35e (18:26:14 PST). Its search hit was the token `e37`, the older experiment E37\'s kind name.')
w('- **The cleanest part.** Of the 15 cases no MM1-v3 design or spec lane tabulated, E206 p112 and E207\'s six have their measured W in MM1-v3\'s committed '
  '`out/points_energy_v3.csv` (written by its build lane before the freeze) and in mm-residuals\' table. Only E212 a2c0-S2\'s 8 runs were tabulated in '
  'energy by no MM1-v3 lane: MM1-v3\'s `out/unread_v2_e212_runs.csv` holds them for time only, every energy column empty, and mm-residuals predates them. '
  'There MM1-v3 reads Q1 1.34% (+0.96), n 8, and Q2 3.04% of D (-2.95), n 6 (null N: 6.07% and 7.37%). The declaration\'s own words already named this '
  'split; section 0 now does too.')
w('- **Seen before the declaration:** E210.md\'s quote of E206\'s S1 D (29.78 W) and a1c1-S2\'s session rest values (29.91 W, 51 C) (section 2).')
w('')
w('### 9.3 The counts, by their commit (finding 4)')
w('')
w('The counts used here are committed unchanged as `tools/matmul/mm1/v3.1/counts/` in 3e8991d0 (07:23:56 PST Wed 18 Nov 2026); `SHA256SUMS` '
  'c74c2d49c336159f6ca63aad2652601a10e22d6a8b5db00d46c66bfb1cf8aa7f; `diff -r` against the land dir the test used: no difference. This folder\'s files are '
  'all new on GitHub main: no file under its path at 3e8991d0 (07:42:02 PST), nor at d8404ef2 (08:03:03 PST), the commit after it.')
w('')
w('### 9.4 Figures re-printed from unrounded values (finding 7)')
w('')
w('The unread lane printed every rms and mean from values already rounded to 3 decimals. Where the third decimal was a 5, the second could come out one '
  'step off. The unchanged scorer\'s unrounded values (`logs/fix/rerun-full.json`) give these 15 corrections; no other printed figure differs.')
w('')
w('| where | printed | unrounded | now |')
w('|---|---|---|---|')
for where, old, val in (
        ('section 0 (Q1 line), section 4 (A: all), section 6 (declared row): N\'s Q1 rms', '24.96%', nQ1),
        ('section 0 (REPORTED), section 4 (A: card=aifoundry3 card 0), section 6 (V1 row): MM1-v3\'s Q1 rms on aifoundry3', '7.83%', a3V3),
        ('section 4, per run, group A: MM1-v3\'s Q1 mean (the verifier\'s finding 7)', '+2.96', pr),
        ('section 4, A: card=aifoundry1 card 1, Q2 N2 rms', '20.12%', a11N2),
        ('section 4, A: fmt=fp16, Q1 N2 rms', '21.20%', f16N2),
        ('section 4, A: source=E206A, Q1 N2 mean', '-19.93', e6aN2),
        ('section 4, B: card=aifoundry3 card 0 and B: source=E206A, Q2 N rms', '52.78%', b3N),
        ('section 4, C: card=aifoundry1 card 1, Q1 N mean', '-10.85', c11N),
        ('section 4, C: card=aifoundry2 card 0 and C: not tabulated, Q1 MM1-v3 mean', '+3.19', c20V3)):
    unit = '%' if old.endswith('%') else ''
    now = (f2(val) + '%') if unit else s2(val)
    w(f'| {where} | {old} | {val:.6f} | {now} |')
w('')
w('### 9.5 The public copy of `inputs/earlier-lanes.json` (finding 8)')
w('')
w('One entry is left out of the public copy: lane data-e212\'s scratch script, matched on the token `sparse50f`. Only its file name was listed, never its '
  'content. The file as run in step 1 is sha256 f20b2fb67bcb5c111b9a899cdb423c60dc3047ef3f324af001ddb3d3d92e1e60 (in `logs/step1-sha256.txt`), and '
  '`SHA256SUMS` gives the public copy\'s. The declaration\'s section g, its counts and its search totals are unchanged by it.')
w('')
w('### 9.6 This README')
w('')
w('It replaces the unread lane\'s README (sha256 7f0ca663d9b27d7df1dd38c9988331df7fadd27940e9b0a30bdfc272d14c0a38). `scripts/fix/f02_readme.py` makes it from '
  'that README by exact, counted replacements. They change:')
w('')
w('- the label paragraph: the counts\' commit, the lanes that had read the runs, and a pointer to this section;')
w('- section 0: N\'s Q1 figure, MM1-v3\'s figure against MM1-v1, the cleanest-part bullet and the addendum\'s line;')
w('- section 2: two lines, the numbers seen before the declaration and the counts\' commit;')
w('- section 4: the re-printed figures and the note under the table;')
w('- section 6: two figures and the addendum\'s row;')
w('- section 7: the wording on the cleanest part;')
w('- section 8: the new files and the fix lane\'s steps;')
w('- this section, which is new.')
w('')
t = t.rstrip('\n') + '\n\n' + '\n'.join(o)
# the scripts' table: the fix lane's scripts as run (sha256 before the path replacement), appended after the unread lane's
FIX = ['slotpy.sh', 'f00_setup.sh', 'f01_rerun.py', 'a01_declare_e209.py', 'a02_forecast_e209.py', 'a03_score_e209.py', 'f02_readme.py', 'f03_land.py']
o = ['', '**The fix lane\'s scripts as run** (`scripts/fix/`, before the path replacement; `f02_readme.py` and `f03_land.py` as in their final run):', '',
     '| script | sha256 as run |', '|---|---|']
for f in FIX:
    o.append(f'| `{f}` | `{sha(os.path.join(ME, "scripts", f))}` |')
t = t + '\n'.join(o) + '\n'
out = os.path.join(ME, 'README.md')
open(out, 'w').write(t)
print('README written', out, sha(out), len(t.splitlines()), 'lines')
