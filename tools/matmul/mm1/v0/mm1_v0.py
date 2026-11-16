# tools/matmul/mm1/v0/mm1_v0.py: MM1-v0, the lab's matmul model AS FROZEN on Mon 16 Nov 2026 (before any E206 datum), vendored.
# This is the frozen predictor (sha256 ab2e43b53d066873334b5663f9c7a926eb75dc879b69eb4e8a91f525970d83c2) with its path lines changed
# and nothing else: every input is read from inputs/ beside this file, and the outputs go to the folder named by --out. The model,
# every constant and every output byte are unchanged (README.md, 'Reproduce'; mm1_v0.sha256's last line names this file).
#   /usr/bin/python3 -I -B tools/matmul/mm1/v0/mm1_v0.py --out <folder>
# SPDX-License-Identifier: Apache-2.0
# mm-synth (Q198): MM1-v0, the spec's desk prototype, frozen as one parameter file, and its forecasts for (a) every E206 point
# (arm A, aifoundry3 card 0, 600 MHz) and (b) the blind matmul day's candidate points (planning only). Desk, post hoc as a fit: every
# constant below was fitted on points that existed before (769 GEMM points for time, 682 zeros/random GEMM points for energy).
#   time    MAXAB per-op maximum (design C's form) over the walk's op classes (r = 0 / r = 1 halves; the lab's own c-arm operand split),
#           design B's closed-form stack distances with a logistic L3 retention, design A's block-stride collapse rule (map 'M3' of
#           harness_time.py); Tc = E119's c1 law, never below the RTL floor (529 fp32/fp16, 270 int8 cycles with B through TenB).
#   energy  form E3 of harness_energy.py refitted here on the same M3 lines: W over idle = P_aw(card) n/1024 + g (B(f) - B(600))
#           + rate s_V [e_res(card, fmt, kind) + sum_l n_l/32 (b_l + d_l phi)]; e_res = ledger v2's frozen resident anchors (not refitted).
#   switches  counted part (design C's table: fin edges a MAC by format and kind, open flow) + an energy-scaled estimate for the classes
#           with no public netlist (kappa fin edges a joule, band), voltage removed.
# L2 hits: the lab's desk L2 model per shape where run (inputs/l2_lab.json, KB <= 2), else design B's KB rule (they agree on every measured shape).
# Writes, in the --out folder: mm1_v0_params.json, mm1_v0_e206.csv, mm1_v0_e206.json, blind_day_plan.csv, SHA256 lines in mm1_v0.sha256.
# /usr/bin/python3 3.12.3, numpy 1.26.4.
import json, math, sys, csv, re, hashlib, importlib.util, collections, os
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))   # vendored: the inputs sit in inputs/ beside this file
IN = os.path.join(HERE, 'inputs')
if len(sys.argv) != 3 or sys.argv[1] != '--out':
    sys.exit('usage: /usr/bin/python3 -I -B mm1_v0.py --out <folder>   (writes the four outputs and mm1_v0.sha256 there)')
OUTD = os.path.abspath(sys.argv[2])
if os.path.realpath(OUTD) == os.path.realpath(HERE):
    sys.exit('refused: --out must not be this folder (the frozen outputs beside the code stay as committed)')
os.makedirs(OUTD, exist_ok=True)
spec = importlib.util.spec_from_file_location('linemap_b', IN + '/linemap.py')
LM = importlib.util.module_from_spec(spec); spec.loader.exec_module(LM)
HT = json.load(open(IN + '/harness_time-MAXAB_M3-RSW_M3.json'))['results']['MAXAB|M3']
c3, m3, cF, mF, kA = HT['params']; X50, S = HT['retention']
FLOOR = {'fp32': 529.0, 'fp16': 529.0, 'int8': 270.0}
MACS = {'fp32': 4096, 'fp16': 8192, 'int8': 16384}
WKB = {'fp32': 1, 'fp16': 2, 'int8': 4}

def Tc(fmt, f):
    t = (283.03 / f + 0.0146) if fmt == 'int8' else (527.48 / f + 0.0176)
    return max(t, FLOOR[fmt] / f)

L2LAB = json.load(open(IN + '/l2_lab.json'))['shapes']   # the lab's desk L2 model, A and B apart (KB <= 2 shapes)
def l2_override(MB, NB, KB):
    """per group L2 hits from the lab's L2 model: A's hits to A_near (then A_far), B's to B_r1 first (up to 64), then B_r0"""
    k = 'gemmL%dx%dx%d' % (MB, NB, KB)
    if k not in L2LAB:
        return None
    a, b = L2LAB[k]['A_L2'], L2LAB[k]['B_L2']
    return {'A': a, 'B_r1': min(b, 64.0), 'B_r0': max(b - 64.0, 0.0)}

def classes_gemmL(MB, NB, KB):
    F = 2 * MB * KB + NB * KB + 2 * MB * NB
    A = np.zeros(3); Br0 = np.zeros(3); Br1 = np.zeros(3)
    ov = l2_override(MB, NB, KB)
    a_left = ov['A'] if ov else None
    for name, cnt, l2, ds in LM.groups(MB, NB, KB, 1.0):
        if ov is not None:
            if name.startswith('A'):
                l2 = min(cnt, a_left); a_left -= l2
            else:
                l2 = min(cnt, ov[name])
        ds = np.array(ds)
        rr = float(np.mean(1.0 / (1.0 + np.exp(np.clip((ds - X50) / S, -50, 50)))))
        if name == 'B_r0' and MB == 1 and NB in (4, 8) and KB >= 4 and F > 32:
            rr *= 0.15
        v = np.array([l2, (cnt - l2) * rr, (cnt - l2) * (1 - rr)])
        if name.startswith('A'): A += v
        elif name == 'B_r1': Br1 += v
        else: Br0 += v
    Q = np.zeros((3, 3))
    for a in range(3):
        for b in range(3):
            Q[a, b] += 0.5 * (A[a] / 64) * (Br0[b] / 64) + 0.5 * (A[a] / 64) * (Br1[b] / 64)
    return Q / Q.sum(), F

def classes_carm(arm):
    cl = {'gemmc1': [(1.0, 0, 0)], 'gemmc8s': [(0.5, 1, 1), (0.5, 1, 0)], 'gemmc4s': [(0.5, 1, 1), (0.5, 1, 0)],
          'gemmc16': [(0.5, 2, 2), (0.5, 2, 0)], 'gemmc16s': [(0.5, 2, 2), (0.5, 2, 0)], 'gemmc8': [(0.5, 2, 2), (0.5, 2, 0)]}[arm]
    Q = np.zeros((3, 3))
    for w, a, b in cl: Q[a, b] += w
    return Q

def t_op(Q, fmt, f):
    tau = [0.0, c3 / f + m3, cF / f + mF]
    tc = Tc(fmt, f)
    return float(sum(Q[a, b] * max(tc, kA * tau[a], tau[b]) for a in range(3) for b in range(3)))

def lines(Q):
    A = 64 * Q.sum(axis=1); B = 128 * Q.sum(axis=0)
    return A + B          # n_L2, n_L3, n_F a shire-op

# ------------------------------------------------ energy refit (E3 on M3 lines), on design C's working table
D = json.load(open(IN + '/gemm_table.json'))
rows = [r for r in D['rows'] if r['w'] is not None and r['w'] > 0 and r['phi'] is not None and r['e_res_nJ'] is not None]
CARDS = ['aifoundry1 card 1', 'aifoundry2 card 0', 'aifoundry3 card 0']
PJ = 1e-12
def Qof(arm):
    if arm.startswith('gemmL'):
        MB, NB, KB = [int(x) for x in arm[5:].split('x')]
        return classes_gemmL(MB, NB, KB)[0]
    m = re.fullmatch(r'gemmc16r(\d+)', arm)
    if m:
        R = int(m.group(1)); Q = np.zeros((3, 3)); Q[2, 2] += 0.5 / R; Q[2, 0] += 0.5 / R; Q[0, 0] += 1 - 1.0 / R
        return Q
    return classes_carm(arm)
def ecols(r, rate, n2, n3, nF, G):
    rs = rate * r['s']
    x = [rs * n2 / 32 * PJ, rs * n2 / 32 * r['phi'] * PJ, rs * n3 / 32 * PJ, rs * n3 / 32 * r['phi'] * PJ,
         rs * nF / 32 * PJ, rs * nF / 32 * r['phi'] * PJ, G] + [(r['minions'] / 1024.0) * (1.0 if r['card'] == c else 0.0) for c in CARDS]
    return x, rs * r['e_res_nJ'] * 1e-9
X = []; y = []
for r in rows:
    n2, n3, nF = lines(Qof(r['arm']))
    x, off = ecols(r, r['rate'], n2, n3, nF, r['G'])
    X.append([v / r['w'] for v in x]); y.append((r['w'] - off) / r['w'])
th, *_ = np.linalg.lstsq(np.array(X), np.array(y), rcond=None)
names = ['b2', 'd2', 'b3', 'd3', 'bF', 'dF', 'g'] + ['Paw|' + c for c in CARDS]
TH = dict(zip(names, [float(v) for v in th]))
e_in = []
for r in rows:
    n2, n3, nF = lines(Qof(r['arm']))
    x, off = ecols(r, r['rate'], n2, n3, nF, r['G'])
    e_in.append((off + sum(TH[k] * v for k, v in zip(names, x))) / r['w'] - 1)
e_in = np.array(e_in)

# ------------------------------------------------ resident anchors (ledger v2, frozen) and switch constants
T = json.load(open(IN + '/tables.json'))
ERES = {(r['card'], r['kind']): r['nJ_per_op_600'] for r in T['ledger_v2_tensor_term']['rows']}
SW = json.load(open(IN + '/switch_table.json'))['rows']
KAPPA = dict(central=108000 / 5.783e-12, low=71000 / 5.783e-12, high=14.5 / 0.2985e-15)   # fin edges a joule at 0.517 V (see spec)

def kindkey(fmt, kind):
    if kind == 'zeros': return fmt + '.zeros'
    if kind == 'random': return fmt + ('.full' if fmt == 'int8' else '.randn')
    return None

def predict(card_key, card_name, arm, fmt, kind, f, V, minions, G=0.0):
    if arm.startswith('gemmL'):
        MB, NB, KB = [int(x) for x in arm[5:].split('x')]
        Q, Fmb = classes_gemmL(MB, NB, KB)
        ops = 64 * MB * NB * KB
    else:
        Q = classes_carm(arm); Fmb = None
        ops = None
    t = t_op(Q, fmt, f)                       # us an op, wall basis (the slowest minion), per-launch clock f
    n2, n3, nF = lines(Q)
    # rho = wall / counter mean (the slowest minion over the average one): the scorecard's measured medians by regime (OUT/mm-scorecard)
    if arm.startswith('gemmL'):
        rho = 1.006 if n2 >= 191.5 else (1.126 if Fmb <= 32 else 1.011)
    else:
        rho = {'gemmc1': 1.006, 'gemmc8s': 1.143, 'gemmc4s': 1.143}.get(arm, 1.001)
    out = dict(T_op_us=t, cycles_per_op_wall=t * f, cycles_per_op_mean=t * f / rho, rho=rho, floor_cycles=FLOOR[fmt], lines_L2_L3_F=[round(n2, 2), round(n3, 2), round(nF, 2)],
               footprint_MB=Fmb, ops_per_minion_per_gemm=ops)
    if ops:
        out['seconds_per_gemm'] = ops * t * 1e-6
        out['sim_steps_per_minion_per_gemm'] = 46.625 * ops + 24.25 * (2 * MB * NB) + 92
    kk = kindkey(fmt, kind)
    if kk is None or (card_key, kk) not in ERES:
        out['energy'] = 'NOT FORECAST (no frozen resident anchor for this kind in ledger v2; the kind term is MM1-v2 work)'
        return out
    s = (V / 0.517) ** 2
    phi = 0.0 if kind == 'zeros' else 1.0
    rate = minions / (t * 1e-6)
    rs = rate * s
    w = (TH['Paw|' + card_name] * minions / 1024.0 + TH['g'] * G + rs * ERES[(card_key, kk)] * 1e-9
         + rs * PJ * (n2 / 32 * (TH['b2'] + TH['d2'] * phi) + n3 / 32 * (TH['b3'] + TH['d3'] * phi) + nF / 32 * (TH['bF'] + TH['dF'] * phi)))
    out['W_over_idle'] = w
    if ops:
        J = w * out['seconds_per_gemm']
        out['J_over_idle_per_gemm'] = J
        Nop = ops * minions
        sw = SW.get(kk)
        Jt = Nop * s * ERES[(card_key, kk)] * 1e-9          # the resident op's joules (the counted class's energy)
        if sw:
            lo = Nop * MACS[fmt] * sw['fin_edges_per_mac']['lo']; hi = Nop * MACS[fmt] * sw['fin_edges_per_mac']['hi']
        else:
            lo = hi = None
        est = max(J - Jt, 0.0) / s
        out['switches'] = dict(counted_tensor_unit=[lo, hi], estimated_rest=[est * KAPPA['low'], est * KAPPA['central'], est * KAPPA['high']],
                               note='counted: open-flow fin edges a MAC (fp32 unit at gate level; rest of the vector unit by the RTL ratio; int8 arithmetic MISSING); estimated: (J over idle - resident op J) / s_V x kappa')
    return out

# ------------------------------------------------ E206 forecasts (arm A: aifoundry3 card 0, 600 MHz pinned, 0.522 V)
e206 = list(csv.DictReader(open(IN + '/points.csv')))
F206 = []
for p in e206:
    pr = predict('a3', 'aifoundry3 card 0', p['arm'], p['format'], p['kind'], 600.0, 0.522, int(p['minions']))
    rec = dict(id=p['id'], group=p['group'], arm=p['arm'], fmt=p['format'], kind=p['kind'], shire_mask=p['shire_mask'], minions=int(p['minions']),
               cycles_per_op_wall=round(pr['cycles_per_op_wall'], 2), cycles_per_op_mean=round(pr['cycles_per_op_mean'], 2), rho=pr['rho'],
               floor_cycles=pr['floor_cycles'],
               seconds_per_gemm=(round(pr['seconds_per_gemm'], 7) if 'seconds_per_gemm' in pr else ''),
               W_over_idle=(round(pr['W_over_idle'], 3) if 'W_over_idle' in pr else ''),
               J_over_idle_per_gemm=(round(pr['J_over_idle_per_gemm'], 6) if 'J_over_idle_per_gemm' in pr else ''),
               lines=pr['lines_L2_L3_F'], footprint_MB=pr['footprint_MB'],
               sim_steps_per_minion_per_gemm=pr.get('sim_steps_per_minion_per_gemm', ''),
               note=('v0 has no contention term: a subset point carries its full-chip per-op time' if p['group'] == 'subset' else '')
                    + (pr['energy'] if isinstance(pr.get('energy'), str) else ''))
    F206.append(rec)
with open(OUTD + '/mm1_v0_e206.csv', 'w', newline='') as fh:
    wr = csv.DictWriter(fh, fieldnames=list(F206[0].keys())); wr.writeheader(); [wr.writerow(r) for r in F206]
json.dump(dict(what='MM1-v0 forecasts for every E206 point on arm A (aifoundry3 card 0, 600 MHz); desk; offered as a freeze line',
               python=sys.version.split()[0], rows=F206), open(OUTD + '/mm1_v0_e206.json', 'w'), indent=1)

# ------------------------------------------------ blind matmul day: candidate points (planning: board peak = 26.0 W rest + 1.10 W + 1 W)
BD = [  # (id, family, arm, fmt, kind, mask)
    ('b01', 'inside', 'gemmL1x3x2', 'fp32', 'random', '0xffffffff'), ('b02', 'inside', 'gemmL1x3x2', 'int8', 'random', '0xffffffff'),
    ('b03', 'inside', 'gemmL1x3x2', 'fp16', 'random', '0xffffffff'), ('b04', 'inside', 'gemmL2x3x2', 'fp32', 'random', '0xffffffff'),
    ('b05', 'inside', 'gemmL2x3x2', 'int8', 'random', '0xffffffff'), ('b06', 'inside', 'gemmL3x2x2', 'fp32', 'random', '0xffffffff'),
    ('b07', 'inside', 'gemmL3x2x2', 'int8', 'random', '0xffffffff'), ('b08', 'inside', 'gemmL1x4x3', 'fp32', 'random', '0xffffffff'),
    ('b09', 'inside', 'gemmL1x4x3', 'int8', 'random', '0xffffffff'),
    ('b10', 'knee', 'gemmL1x9x3', 'fp32', 'random', '0xffffffff'), ('b11', 'knee', 'gemmL1x9x3', 'int8', 'random', '0xffffffff'),
    ('b12', 'knee', 'gemmL2x3x5', 'fp32', 'random', '0xffffffff'), ('b13', 'knee', 'gemmL2x3x5', 'int8', 'random', '0xffffffff'),
    ('b14', 'knee', 'gemmL2x3x5', 'fp16', 'random', '0xffffffff'), ('b15', 'knee', 'gemmL3x3x4', 'fp32', 'random', '0xffffffff'),
    ('b16', 'knee', 'gemmL3x3x4', 'int8', 'random', '0xffffffff'), ('b17', 'knee', 'gemmL5x2x3', 'fp32', 'random', '0xffffffff'),
    ('b18', 'knee', 'gemmL5x2x3', 'int8', 'random', '0xffffffff'),
    ('b19', 'past', 'gemmL3x5x5', 'fp32', 'random', '0xffffffff'), ('b20', 'past', 'gemmL3x5x5', 'int8', 'random', '0xffffffff'),
    ('b21', 'past', 'gemmL5x3x6', 'fp32', 'random', '0xffffffff'), ('b22', 'past', 'gemmL2x6x10', 'fp32', 'random', '0xffffffff'),
    ('b23', 'past', 'gemmL1x3x24', 'fp32', 'random', '0xffffffff'), ('b24', 'past', 'gemmL1x3x24', 'int8', 'random', '0xffffffff'),
    ('b25', 'past', 'gemmL6x6x6', 'fp32', 'random', '0xffffffff'), ('b26', 'past', 'gemmL6x6x6', 'fp16', 'random', '0xffffffff'),
    ('b27', 'stride', 'gemmL1x7x6', 'fp32', 'random', '0xffffffff'), ('b28', 'stride', 'gemmL1x8x6', 'fp32', 'random', '0xffffffff'),
    ('b29', 'stride', 'gemmL1x9x6', 'fp32', 'random', '0xffffffff'), ('b30', 'stride', 'gemmL1x4x12', 'fp32', 'random', '0xffffffff'),
    ('b31', 'stride', 'gemmL1x5x10', 'fp32', 'random', '0xffffffff'), ('b32', 'stride', 'gemmL1x8x6', 'int8', 'random', '0xffffffff'),
    ('b33', 'stride', 'gemmL1x7x6', 'int8', 'random', '0xffffffff'),
    ('b34', 'subset', 'gemmL3x6x4', 'fp32', 'random', '0x3'), ('b35', 'subset', 'gemmL3x6x4', 'fp32', 'random', '0xfff'),
    ('b36', 'subset', 'gemmL3x6x4', 'fp32', 'random', '0xffffff'), ('b37', 'subset', 'gemmL3x6x4', 'fp32', 'random', '0x0f0f0f0f'),
    ('b38', 'subset', 'gemmL3x6x4', 'int8', 'random', '0x3'), ('b39', 'subset', 'gemmL3x6x4', 'int8', 'random', '0xffffff'),
    ('b40', 'subset', 'gemmL1x2x2', 'fp32', 'random', '0x3'), ('b41', 'subset', 'gemmL1x2x2', 'fp32', 'random', '0xfff'),
    ('b42', 'kinds', 'gemmL1x3x2', 'fp32', 'e37', '0xffffffff'), ('b43', 'kinds', 'gemmL3x5x5', 'fp32', 'e37', '0xffffffff'),
    ('b44', 'kinds', 'gemmL1x3x2', 'int8', 'e37', '0xffffffff'), ('b45', 'kinds', 'gemmL3x5x5', 'int8', 'e37', '0xffffffff'),
    ('b46', 'kinds', 'gemmL1x3x2', 'fp32', 'sparse25', '0xffffffff'), ('b47', 'kinds', 'gemmL3x5x5', 'fp32', 'sparse25', '0xffffffff'),
    ('b48', 'kinds', 'gemmL1x3x2', 'fp32', 'ones', '0xffffffff'),
    ('b49', 'kinds', 'gemmL1x3x2', 'fp32', 'real:blind4 fp32.real_pythia_embed_qkv + fp32.real_qwen_q_down', '0xffffffff'),
    ('b50', 'kinds', 'gemmL1x3x2', 'fp16', 'real:blind4 fp16.real_pythia_embed_qkv + fp16.real_qwen_ln_down', '0xffffffff'),
    ('b51', 'kinds', 'gemmL1x3x2', 'int8', 'real:blind4 int8.real_pythia_embed_mlpout + int8.real_qwen_q_down', '0xffffffff'),
    ('b52', 'kinds', 'gemmL3x5x5', 'fp32', 'designed:blind3 a_colconst_b_randn', '0xffffffff'),
    ('b53', 'kinds', 'gemmL1x3x2', 'fp32', 'designed:row-permuted pair, original (new tile file)', '0xffffffff'),
    ('b54', 'kinds', 'gemmL1x3x2', 'fp32', 'designed:row-permuted pair, permuted (new tile file)', '0xffffffff'),
]
def nmask(m):
    return bin(int(m, 16)).count('1') * 32
measured = set(json.load(open(IN + '/inventory.json'))['gemmL_shapes_measured'])
in206 = {(p['arm'], p['format'], p['kind'], p['shire_mask']) for p in e206}
in206_arms = {p['arm'] for p in e206}
plan = []
for bid, fam, arm, fmt, kind, mask in BD:
    n = nmask(mask)
    kind_e = kind if kind in ('zeros', 'random') else 'random'     # planning peak: the busiest kind as an upper bound
    pr = predict('a3', 'aifoundry3 card 0', arm, fmt, kind_e, 600.0, 0.522, n)
    w = pr.get('W_over_idle')
    plan.append(dict(id=bid, family=fam, arm=arm, fmt=fmt, kind=kind, shire_mask=mask, minions=n,
                     M=1024 * int(arm[5:].split('x')[0]) if mask == '0xffffffff' else '', N=512 * int(arm[5:].split('x')[1]) if mask == '0xffffffff' else '',
                     K=512 * int(arm[5:].split('x')[2]) * WKB[fmt],
                     footprint_MB=pr['footprint_MB'], never_run_shape=(arm not in measured and arm not in in206_arms),
                     never_run_point=((arm, fmt, kind, mask) not in in206), plan_cycles_per_op=round(pr['cycles_per_op_wall'], 1),
                     plan_seconds_per_gemm=round(pr.get('seconds_per_gemm', 0), 6),
                     plan_W_over_idle=(round(w, 2) if w is not None else ''), plan_peak_W=(round(26.0 + 1.10 * w + 1.0, 1) if w is not None else '')))
with open(OUTD + '/blind_day_plan.csv', 'w', newline='') as fh:
    wr = csv.DictWriter(fh, fieldnames=list(plan[0].keys())); wr.writeheader(); [wr.writerow(r) for r in plan]

params = dict(what='MM1-v0: the spec prototype frozen (desk, post hoc fits; not MM1-v1, which the build lane freezes after refitting)',
              python=sys.version.split()[0], numpy=np.__version__,
              time=dict(form='MAXAB over op classes', Tc='E119 c1 law, floored at the RTL law (529 / 270 cycles)', c3=c3, m3=m3, cF=cF, mF=mF, kA=kA,
                        retention=dict(x50_MB=X50, s_MB=S, form='1/(1+exp((d-x50)/s)) on design B closed-form stack distances'),
                        collapse='far-B (B_r0) retention x 0.15 when MB = 1, NB in {4, 8}, KB >= 4, footprint > 32 MB (design A rule)',
                        loeo=HT['loeo_all'], loeo_gemmL=HT['loeo_gemmL'], loeo_carm=HT['loeo_carm'], loco=HT['loco']),
              energy=dict(form='E3: P_aw(card) n/1024 + g (B(f)-B(600)) + rate s_V [e_res + sum_l n_l/32 (b_l + d_l phi)]', theta=TH,
                          units='b, d: pJ a line a shire-op; P_aw: W at 1,024 minions; g: share of B(f) - B(600)',
                          in_sample=dict(n=int(len(e_in)), rms_pct=round(float(np.sqrt(np.mean(e_in ** 2))) * 100, 2), bias_pct=round(float(np.mean(e_in)) * 100, 2)),
                          e_res_source='ledger v2 frozen anchors (OUT/mm-models/work/tables.json from frozen-v2.json); aifoundry2 fp16/int8 placeholders'),
              switches=dict(kappa_fin_edges_per_J_at_0p517V=KAPPA, counted='design C switch_table.json fin_edges_per_mac (lo zero delay, hi timed)'))
json.dump(params, open(OUTD + '/mm1_v0_params.json', 'w'), indent=1)
lines_out = []
for fn in ('mm1_v0_params.json', 'mm1_v0_e206.csv', 'mm1_v0_e206.json', 'blind_day_plan.csv'):
    h = hashlib.sha256(open(OUTD + '/' + fn, 'rb').read()).hexdigest()
    lines_out.append(f'{h}  {fn}')
h = hashlib.sha256(open(os.path.abspath(__file__), 'rb').read()).hexdigest(); lines_out.append(f'{h}  mm1_v0.py')
open(OUTD + '/mm1_v0.sha256', 'w').write('\n'.join(lines_out) + '\n')
print('\n'.join(lines_out))
print('time params', [round(v, 4) for v in (c3, m3, cF, mF, kA)], 'retention', X50, S)
print('energy theta', {k: round(v, 3) for k, v in TH.items()}, 'in sample', params['energy']['in_sample'])
print('E206 rows', len(F206), 'with energy', sum(1 for r in F206 if r['W_over_idle'] != ''))
for r in plan:
    print(r['id'], r['family'], r['arm'], r['fmt'], r['kind'][:20], r['shire_mask'], 'F', r['footprint_MB'], 'never shape', r['never_run_shape'], 'never pt', r['never_run_point'],
          'cyc', r['plan_cycles_per_op'], 's', r['plan_seconds_per_gemm'], 'W', r['plan_W_over_idle'], 'peak', r['plan_peak_W'])
