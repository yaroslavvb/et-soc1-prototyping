#!/usr/bin/env python3
"""E210 (Q202) desk: the kinds spec the switch count (count_e210.py) and the stream reader (flips_e210.py) read: each kind's tile files, in the
order the host's pool cycles them, and its MM1-v1 phi source.

    /usr/bin/python3 -I -B spec_e210.py <lab top> <desk-only tile dir (make_tiles_e210.sh's)> <out json>
E210's patterns: tools/claims-v3/e210/tiles/fp32/<p>/ (61 files; negzero 1). random and sparse50: the host draws them itself (gen randn and
sparse50), so the desk reads 61 tiles of the same law (rgm136's drawTile, make_tiles_e210.sh); zeros and ones: the lab's committed kind tiles
E206 and E208 ran; real: E206's four real2 tiles in E206's order. phi: a tile-file kind over its files, a generator kind by its law, zeros 0
(MM1-v1's own conventions, kinds_v1 and mm1_v1.Model.predict).
SPDX-License-Identifier: Apache-2.0
"""
import glob
import json
import os
import sys

PATTERNS = ['negzero', 'signs', 'lowmant8', 'highmant8', 'bhalfeq', 'badjeq', 'hd4', 'maxalte', 'arow50']
REAL = ['gpt2_l9_attn_qk', 'gpt2_l3_mlp_down', 'bert_l6_up', 'vit_l5_down']


def main():
    top, dsk, out = os.path.abspath(sys.argv[1]), os.path.abspath(sys.argv[2]), sys.argv[3]
    spec = {}
    for p in PATTERNS:
        fl = sorted(glob.glob(os.path.join(top, 'tools/claims-v3/e210/tiles/fp32', p, p + '_*.bin')))
        assert fl and (len(fl) == 61 or p == 'negzero'), p
        spec[p] = {'files': fl, 'phi': {'tiles': fl}}
    for k in ('randn', 'sparse50'):
        fl = sorted(glob.glob(os.path.join(dsk, 'fp32', k, k + '_*.bin')))
        assert len(fl) == 61, k
        spec[k] = {'files': fl, 'phi': {'gen': k}}
    spec['zeros'] = {'files': [os.path.join(top, 'tools/claims-v3/kinds/tiles/fp32/zeros.bin')], 'phi': {'gen': 'zeros'}}
    ones = os.path.join(top, 'tools/claims-v3/kinds/tiles/fp32/ones.bin')
    spec['ones'] = {'files': [ones], 'phi': {'tiles': [ones]}}
    real = [os.path.join(top, 'tools/claims-v3/kinds/real2/tiles/fp32', t + '.bin') for t in REAL]
    spec['real'] = {'files': real, 'phi': {'tiles': real}}
    for k, v in spec.items():
        for f in v['files']:
            assert os.path.getsize(f) == 2048, f
    json.dump(spec, open(out, 'w'), indent=1)
    print(f'{len(spec)} kinds: ' + ', '.join(f'{k} {len(v["files"])}' for k, v in spec.items()))


if __name__ == '__main__':
    main()
