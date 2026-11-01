#!/usr/bin/python3
"""The bench's own back-test on the lists E102 builds on: the desk lane's counts of E65's, E67's and E79's tiles (Q132(b), run on the mini at 01:21 and 01:28 PDT, not yet
committed by it), distilled to what the frozen formula reads, with each list's measured step beside it. Writes bench/backtest-hl-hlp.json and copies bench/counts-e102.json."""
import hashlib, json, math, os, shutil
import sys
HL, HLP, COUNTS = sys.argv[1:4]     # the bench lane's counts-hl.json and counts-hlp.json, and E102's counts-e102.json
R = ''       # run from the repo's root
D = R + 'docs/reports/data/2026-11-01-e102-balanced-bit-prices/bench/'
os.makedirs(D, exist_ok=True)
shutil.copy(COUNTS, D + 'counts-e102.json')
hl = json.load(open(HL))['rows']
hlp = json.load(open(HLP))['rows']
pred = json.load(open(R + 'docs/reports/data/2026-11-01-q132-rtl-bench/e92-bench-prediction.json'))['variants']
e65 = json.load(open(R + 'docs/reports/data/2026-10-26-e65-bit-prices-hart-ladder/hl.json'))['cards']['aifoundry3']
e67 = json.load(open(R + 'docs/reports/data/2026-10-27-e67-a-side-bit-prices/hl.json'))['cards']['aifoundry3']
e79 = json.load(open(R + 'docs/reports/data/2026-10-31-e79-fp16-int8-bit-prices/hlp.json'))['cards']['aifoundry3']
e78 = json.load(open(R + 'docs/reports/data/2026-10-31-e78-kinds-energy-matrix/e78.json'))['items']
RATE = {t: e78[f'{t}.randn' if t != 'int8' else 'int8.full']['rate']['mean'] for t in ('fp32', 'fp16', 'int8')}
def row(r):
    m = r['mean']
    return {'nets_map': m['vpu']['nets_map'], 'nets_hier2': m['vpu']['nets_hier2'], 'clocked': m['ff']['all']['clocked'], 'check_mismatch': m['check_mismatch']}
def D_(r, var, t):
    v = pred[var]
    return (r[var] * v['k_fJ_per_net_toggle'] + r['clocked'] * v['a_fJ_per_clocked_bit']) * 1e-15 * RATE[t]
out = {'_note': 'Bench counts of E65, E67 and E79 tiles (aifoundry3), by the bench of Q132(b); the coefficients are e92-bench-prediction.json, fitted on E78 alone; so every number here is out of sample. Written before any E102 data exist.',
       'sources_sha256': {'counts-hl.json': hashlib.sha256(open(HL, 'rb').read()).hexdigest(), 'counts-hlp.json': hashlib.sha256(open(HLP, 'rb').read()).hexdigest()},
       'lists': {}}
def lst(name, rows, t):
    ent = {}
    for var in ('nets_map', 'nets_hier2'):
        ds = [(x['measured_w'] - (D_(x['row'], var, t) - D_(x['zero'], var, t))) for x in rows]
        ent[var] = {'rms_w': round(math.sqrt(sum(d * d for d in ds) / len(ds)), 3), 'mean_measured_minus_bench_w': round(sum(ds) / len(ds), 3)}
    out['lists'][name] = {'summary': ent, 'n': len(rows), 'rows': {x['j']: {'measured_w': round(x['measured_w'], 3), 'bench_map_w': round(D_(x['row'], 'nets_map', t) - D_(x['zero'], 'nets_map', t), 3), 'bench_hier2_w': round(D_(x['row'], 'nets_hier2', t) - D_(x['zero'], 'nets_hier2', t), 3)} for x in rows}}
rows = []
for j in range(32):
    if j == 30:
        continue    # its twin's own zero is not in the bench's hl set under this name
    rows.append({'j': j, 'measured_w': e65['bits'][str(j)]['dW'], 'row': row(hl[f'fp32.bit_{j}']), 'zero': row(hl['fp32.lq_h0'])})
lst('E65 fp32 B (31 positions, bit 30 left out)', rows, 'fp32')
rows = []
for j in range(32):
    if j == 30:
        continue
    rows.append({'j': j, 'measured_w': e67['a_bits'][str(j)]['dW'], 'row': row(hl[f'fp32.abit_{j}']), 'zero': row(hl['fp32.aq_h0'])})
lst('E67 fp32 A (31 positions)', rows, 'fp32')
rows = []
for j in range(16):
    if j == 14:
        continue
    rows.append({'j': j, 'measured_w': e79['prices']['fp16_b'][str(j)]['dW'], 'row': row(hlp[f'fp16.b16_{j}']), 'zero': row(hlp['fp16.h16q'])})
lst('E79 fp16 B (15 positions)', rows, 'fp16')
rows = []
for j in range(16):
    if j == 14:
        continue
    rows.append({'j': j, 'measured_w': e79['prices']['fp16_a'][str(j)]['dW'], 'row': row(hlp[f'fp16.a16_{j}']), 'zero': row(hlp['fp16.a16q'])})
lst('E79 fp16 A (15 positions)', rows, 'fp16')
rows = [{'j': 'b32_22', 'measured_w': e79['prices']['fp32_b']['22']['dW'], 'row': row(hlp['fp32.b32_22']), 'zero': row(hlp['fp32.h32q'])},
        {'j': 'b32p_22', 'measured_w': e79['prices']['fp32_b_jgp']['22']['dW'], 'row': row(hlp['fp32.b32p_22']), 'zero': row(hlp['fp32.h32q'])},
        {'j': 'b16p_9', 'measured_w': e79['prices']['fp16_b_jgp']['9']['dW'], 'row': row(hlp['fp16.b16p_9']), 'zero': row(hlp['fp16.h16q'])}]
lst('E79 balanced and tie', rows, 'fp32')
rows = []
for j in range(8):
    rows.append({'j': j, 'measured_w': e79['prices']['int8_b_kg'][str(j)]['dW'], 'row': row(hlp[f'int8.b8k_{j}']), 'zero': row(hlp['int8.h8q'])})
lst('E79 int8 B kg (fitted slope), against the FLOAT coefficients', rows, 'int8')
json.dump(out, open(D + 'backtest-hl-hlp.json', 'w'), indent=1)
for k, v in out['lists'].items():
    print(k, v['summary'])
