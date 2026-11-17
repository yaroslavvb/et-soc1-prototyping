#!/usr/bin/env python3
"""E210 (Q202) desk: the RTL bench (rtl-sim/fma_toggle_v2) at a GEMM's accumulator states, for E210's patterns and the calibration kinds.
sw-design-a's count_gemm.py (round Q202), unchanged in what it measures, with every path an argument and the tile lists from a spec file.

The harness's own run_kinds.py (the command behind counts-v2.json and MM1-v1's switch table) starts each measured op at a point of a 0.5 s
LAUNCH of ONE tile pair repeated (91,575 / 274,725 / 457,875 ops in), so its accumulators are about 1e5 times one op's sum. A GEMM restarts C
every K/16 ops (32 at gemmL1x1x1 fp32, K 512; 128 at gemmL1x1x4, K 2,048) and feeds a new tile pair every op. This driver keeps run_kinds.py's
measurement exactly (its point(): one warm op, a coverage run of --ops ops with the C check, one VCD op counted by settle_count with the maps
trained on the same binary, the multiply-add unit and the whole VPU) and changes only the C loaded before the warm op: C0 = the accumulator
after j ops of OTHER tiles of the same kind (the kind's files cycled; the first of them a MUL pass), computed with hd_model_e210's arithmetic.
The check compares the bench's C after warm + ops ops of tile T with the same arithmetic (check_mismatch must be 0 for every point).
The warm and measured ops read one tile pair (A and B of the same file); the card pairs A of one file with B of another (the pool rule):
the laws draw A and B independently, so the count's statistics are the same (a desk assumption, stated in E210.md).

    /usr/bin/python3 -I -B count_e210.py --bench <built rtl-sim/fma_toggle_v2 dir> --maps <dir> --spec <kinds json> --kinds a,b,..
                                         --js 3,11,19,27 --tsel 0,1 --out <json> [--jobs 4] [--tmp <dir>]
    the spec (spec_e210.py): {"<kind>": {"files": ["<tile file>", ...], ...}, ...} (absolute paths). Run inside W/slot.sh and W/nodev.sh.
SPDX-License-Identifier: Apache-2.0
"""
import argparse
import json
import os
import subprocess
import sys
import tempfile
from concurrent.futures import ThreadPoolExecutor

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import hd_model_e210 as H  # noqa: E402

RK = None
MACS = 4096


def point(a, files, ti, j, warm, ops):
    tiles = [H.load(p) for p in files]
    T = tiles[ti % len(tiles)]
    others = [tiles[(ti + 1 + m) % len(tiles)] for m in range(j)] if len(tiles) > 1 else [T] * j
    c0 = H.c_after(others) if j > 0 else np.zeros((16, 16), np.uint32)
    c1 = H.c_after([T] * (warm + ops), c0=c0, first_first=(j == 0))
    with tempfile.TemporaryDirectory(dir=a.tmp) as d:
        A, B = T
        words = list(A.ravel()) + list(B.ravel()) + list(c0.ravel())
        hexf = os.path.join(d, 't.hex')
        with open(hexf, 'w') as f:
            f.write('\n'.join(f'{int(w):08x}' for w in words) + '\n')
        base = [a.bin, f'+tiles={hexf}', '+fmt=fp32', f'+warm={warm}', f'+first={1 if j == 0 else 0}', f'+loadc={0 if j == 0 else 1}']
        cov = os.path.join(d, 'cov.dat')
        out = subprocess.run(base + [f'+ops={ops}', '+printc=1', f'+verilator+coverage+file+{cov}'], capture_output=True, text=True,
                             check=True).stdout
        acct, unit, final = None, None, {}
        last = warm + ops
        for line in out.splitlines():
            if line.startswith('ACCT '):
                acct = json.loads(line[5:])
            elif line.startswith('ACCTU '):
                unit = [int(x) for x in line.split()[1:]]
            elif line.startswith('C '):
                _, op, i, jj, v = line.split()
                if int(op) == last:
                    final[(int(i), int(jj))] = int(v, 16)
        miss = sum(1 for i in range(16) for jj in range(16) if final.get((i, jj)) != int(c1[i, jj]))
        by_block, clock = RK.parse_cov(cov)
        n = acct['ops']
        res = {'tile': os.path.basename(files[ti % len(files)]), 'j': j, 'check_words': 256, 'check_mismatch': miss,
               'cycles': acct['cycles'] / n, 'busy': acct['busy'] / n, 'uops': acct['uops'] / n,
               'valid_slots': acct['txfma_valid'] / n, 'scp_reads': acct['scp_reads'] / n,
               'ff': {'all': {'clocked': acct['ff_clocked_bits'] / n, 'toggles': acct['ff_toggles'] / n, 'present': acct['ff_present_bits'] / n},
                      'txfma': {'clocked': unit[0] / n, 'toggles': unit[1] / n, 'present': unit[2] / n},
                      'rest': {'clocked': unit[6] / n, 'toggles': unit[7] / n, 'present': unit[8] / n}},
               'nets_cov': sum(by_block.values()) / n, 'clock_nets_cov': clock / n,
               'median_abs_c0': float(np.median(np.abs(c0.view(np.float32))))}
        vcd = os.path.join(d, 't.vcd')
        subprocess.run(base + ['+ops=1', f'+dump={vcd}', '+dump_ops=1', f'+verilator+coverage+file+{cov}'], capture_output=True, text=True,
                       check=True)
        res['unit'] = RK.settle(a, vcd, '.txfma.', d, 'unit', os.path.join(a.maps, 'unit_float.map'))
        res['vpu'] = RK.settle(a, vcd, '.dut.', d, 'vpu', os.path.join(a.maps, 'vpu.map'))
        os.remove(vcd)
    return res


def main():
    global RK
    ap = argparse.ArgumentParser()
    ap.add_argument('--bench', required=True)
    ap.add_argument('--maps', required=True)
    ap.add_argument('--spec', required=True)
    ap.add_argument('--kinds', required=True)
    ap.add_argument('--js', default='3,11,19,27')
    ap.add_argument('--tsel', default='0,1')
    ap.add_argument('--ops', type=int, default=2)
    ap.add_argument('--jobs', type=int, default=4)
    ap.add_argument('--tmp', default=None)
    ap.add_argument('--label', default='')
    ap.add_argument('--stop-if-file', default='', help='no new bench point starts while this file exists (a box rule: the card in use)')
    ap.add_argument('--out', required=True)
    a = ap.parse_args()
    sys.path.insert(0, a.bench)
    import run_kinds  # noqa: E402  (parse_cov, settle, mean_rows: the harness's own, unchanged)
    RK = run_kinds
    a.bin = os.path.join(a.bench, 'obj_vpu/Vtb')
    a.settle = os.path.join(a.bench, 'settle_count')
    spec = {k: (v if isinstance(v, list) else v['files']) for k, v in json.load(open(a.spec)).items()}
    js = [int(x) for x in a.js.split(',')]
    tsel = [int(x) for x in a.tsel.split(',')]
    work = []
    for nm in a.kinds.split(','):
        files = spec[nm]
        ts = tsel if len(files) > 1 else [0]
        for ti in ts:
            for j in js:
                work.append((nm, files, ti, j))

    def job(w):
        nm, files, ti, j = w
        if a.stop_if_file and os.path.exists(a.stop_if_file):
            print(f'SKIPPED {nm} t{ti} j{j}: {a.stop_if_file} exists', flush=True)
            return nm, None
        try:
            return nm, point(a, files, ti, j, 1, a.ops)
        except Exception as e:  # report and keep going; an incomplete kind is flagged below
            print(f'FAILED {nm} t{ti} j{j}: {e}', flush=True)
            return nm, None

    with ThreadPoolExecutor(a.jobs) as ex:
        done = list(ex.map(job, work))
    res = {'bench': 'rtl-sim/fma_toggle_v2 (vpu_top, -fno-dfg), built from the committed sources; maps trained on the same binary',
           'units': 'per TensorFMA op on one minion (4,096 multiply-adds in fp32)', 'label': a.label,
           'driver': 'count_e210.py: run_kinds.point() with C0 = a GEMM accumulation of j other tiles of the kind', 'js': js, 'tsel': tsel,
           'python': sys.version.split()[0], 'numpy': np.__version__, 'rows': {}, 'incomplete': []}
    for nm in a.kinds.split(','):
        rows = [r for k, r in done if k == nm and r is not None]
        want = len([w for w in work if w[0] == nm])
        if len(rows) < want:
            res['incomplete'].append(f'{nm}: {len(rows)} of {want}')
            print(f'{nm}: incomplete ({len(rows)} of {want})', flush=True)
            if not rows:
                continue
        res['rows'][nm] = {'kind': nm, 'macs_per_op': MACS, 'n_files': len(spec[nm]), 'points': rows,
                           'mean': RK.mean_rows([{k: v for k, v in r.items() if k != 'tile'} for r in rows])}
        m = res['rows'][nm]['mean']
        print(f"{nm:12s} n {len(rows):2d} miss {m['check_mismatch']:5.1f} valid {m['valid_slots']:6.0f} unit_hier/MAC {m['unit']['nets_hier'] / MACS:8.1f} "
              f"vpu_map/MAC {m['vpu']['nets_map'] / MACS:8.1f} clk/MAC {m['clock_nets_cov'] / MACS:7.2f} ffclk/MAC {m['ff']['all']['clocked'] / MACS:7.1f}",
              flush=True)
    json.dump(res, open(a.out, 'w'), indent=1, sort_keys=True)


if __name__ == '__main__':
    main()
