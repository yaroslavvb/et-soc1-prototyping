"""The deep zoom's data (30 Sep 2026): the scale nodes from the universe to the silicon lattice, their facts, the map
outlines, the image manifest and the memory-levels facts the copied drawings cite. build_facts.py calls build().

Inputs, beside this file:
  inside.json       what is inside every part the diagram lets a reader select, as a tree down to the silicon crystal
                    (build_inside.py; 130 nodes, 395 facts; its research-inside.md says how each was found)
  outside.json      the 18 levels outside the chip, from the package to "beyond what we can see" (build_outside.py;
                    research-outside.md)
  outside-geo.json  the map outlines in km (make_geo.py, from the US Census and Natural Earth files, public domain)
  ../../2026-09-28-memory-levels/facts.json   the memory-levels page's facts and numbers: imported, prefixed ml:,
                    exactly those the tree cites and the copied drawings (sources/circuitkit.js) print
  ../../../chip-diagram-img/*.webp   the six images (sha256 into the manifest; the page checks nothing at run time,
                    the build refuses a manifest that does not match)

Kinds: one vocabulary of nine (DESIGN §4.2): measured, spec, derived, inferred, outside, generic, owner, hypothesis,
unknown. outside.json's "estimate" and "assumed" become inferred (the word kept in the note); "outside source"
becomes outside; a compound kind ("spec, measured, inferred") takes its weakest member, with a note saying so; a
"note" is not a fact and becomes the level's note text. Any other kind stops the build.
"""
import hashlib
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..', '..', '..'))
IMG = os.path.join(ROOT, 'docs', 'reports', 'chip-diagram-img')
KINDS = ['measured', 'spec', 'derived', 'inferred', 'outside', 'generic', 'owner', 'hypothesis', 'unknown']
# weakest first: a compound kind takes the first of these it contains
WEAK = ['hypothesis', 'unknown', 'inferred', 'derived', 'generic', 'outside', 'owner', 'spec', 'measured']
KMAP = {'outside source': 'outside', 'estimate': 'inferred', 'assumed': 'inferred', 'none': 'unknown'}
# the nodes of inside.json the page does not draw as scales: the tree's root of shared circuits, the die's legend
# and its host (the host is a level of the outside ladder)
SKIP = {'lib', 'inferred'}
# short names for the breadcrumb (else the name up to its first parenthesis or comma)
SHORT = {
    'beyond': 'Beyond', 'universe': 'Universe', 'laniakea': 'Laniakea', 'localgroup': 'Local Group', 'milkyway': 'Milky Way',
    'stars': 'Nearest stars', 'solar': 'Solar System', 'moon': 'Earth–Moon', 'earth': 'Earth', 'us': 'US', 'california': 'California',
    'bayarea': 'Bay Area', 'sf': 'San Francisco', 'studio45': 'Studio 45', 'rack': 'Rack', 'host': 'Host', 'card': 'Card',
    'package': 'Package', 'die': 'Chip', 'shire': 'Shire', 'minion': 'Minion',
    'lib.cmp42': '4:2 compressor', 'lib.xor': 'XOR gate', 'lib.fa': 'Full adder', 'lib.finfet': 'FinFET', 'lib.fin': 'Fin',
    'lib.channel': 'Channel', 'lib.si': 'Silicon crystal', 'vpu.lane.fma': 'Multiply-add', 'vpu.lane.fma.tree': 'Compressor tree',
    'fma.tree.col': 'Column', 'core': 'Core', 'vpu': 'Vector unit', 'tensor': 'Tensor unit', 'l1d': 'L1 cache', 'die.metal': 'Wiring stack',
    'lib.inverter': 'Inverter', 'lib.nand2': 'NAND gate', 'lib.flipflop': 'Flip-flop', 'lib.latch': 'Latch', 'lib.sram6t': '6T cell',
}


# the numbers the outside levels print in their drawings: key -> (fact, text); the text must occur in the fact's
# statement, so no number in a drawing lacks its source
ONUM = {
    'u_age': ('out.universe.1', '13.79 billion years'), 'u_rad': ('out.universe.2', '46.2 billion light-years'),
    'u_cmb': ('out.universe.3', '380,000 years'), 'lan_size': ('out.laniakea.1', '520 million light-years'),
    'lan_n': ('out.laniakea.2', '100,000 galaxies'), 'lg_m31': ('out.localgroup.2', '2.5 million light-years'),
    'lg_m33': ('out.localgroup.3', '3 million light-years'), 'lg_lmc': ('out.localgroup.3', '160,000'),
    'lg_size': ('out.localgroup.1', '10 million light-years'), 'mw_sun': ('out.milkyway.2', '26,000 light-years'),
    'mw_size': ('out.milkyway.1', '100,000 light-years'), 'st_prox': ('out.stars.1', '4.2 light-years'),
    'so_earth': ('out.solar.1', '8.32 min'), 'so_nep': ('out.solar.2', '30.07 au'), 'so_nep_h': ('out.solar.2', '4.17 h'),
    'so_voy': ('out.solar.3', '173 au'), 'mo_dist': ('out.moon.1', '0.3844 million km'), 'mo_light': ('out.moon.2', '1.28 s'),
    'ea_r': ('out.earth.1', '6,371'), 'ea_eq': ('out.earth.2', '134 ms'), 'us_sfny': ('out.us.2', '20.2 ms'),
    'us_sfny_km': ('out.us.2', '4,129 km'), 'ca_ns': ('out.california.2', '1060 km'), 'ca_ms': ('out.california.2', '5.19 ms'),
    'ba_ms': ('out.bayarea.2', '1.07 ms'), 'sf_us': ('out.sf.3', '54 µs'), 'rack_ns': ('out.rack.5', '5 ns'),
    'card_w': ('out.card.1', '167.6 x 111.8 mm'), 'pkg_body': ('out.package.1', '45.0 x 45.0 mm'),
    'pkg_balls': ('out.package.1', '2,494'), 'pkg_lid': ('out.package.1', '44.8 mm'), 'pkg_h': ('out.package.1', '3.95 mm'),
    'pkg_die': ('out.package.4', '25.6 x 22.2 mm'), 'pkg_bumps': ('out.package.3', '30,000'),
    'pkg_pitch': ('out.package.2', '0.80 mm'), 'card_88': ('out.card.6', '88 W'), 'card_v': ('out.card.7', '0.52 V'),
}


# the numbers the circuit drawings inside the chip print: key -> (fact, text), checked like ONUM
INUM = {
    'fma_st': ('in.vpu.lane.fma.1', '7 stages'), 'pp17': ('in.vpu.lane.fma.booth.2', '17 partial products'),
    'pp33': ('in.vpu.lane.fma.booth.2', '33 bits'), 'tree_tr': ('in.vpu.lane.fma.tree.2', '14,000 transistors'),
    'fa_tr': ('in.lib.fa.1', '28 transistors'), 'xor_tr': ('in.lib.xor.1', '8-12 transistors'), 'nand_tr': ('in.lib.nand2.1', '4 transistors'),
    'gate_p': ('in.lib.finfet.1', '57 nm'), 'fin_p': ('in.lib.finfet.1', '30 nm'), 'fin_w': ('in.lib.fin.3', '6-7 nm'),
    'fin_h': ('in.lib.fin.3', '45-50 nm'), 'lg': ('in.lib.gate.1', '20 nm'), 'si_a': ('in.lib.si.1', '0.5431 nm'),
    'si_nn': ('in.lib.si.2', '0.235 nm'), 'si_pl': ('in.lib.si.3', '31 planes'), 'ch_at': ('in.lib.channel.1', '270,000'),
    'm_pitch': ('in.die.metal.2', '40 nm'), 'masks': ('chip.process', '89 mask layers'),
}
# nodes the tree does not have that the page draws: a column of the compressor tree, between the tree and one 4:2
# compressor (DESIGN §1.5: the tree to a 4:2 is 27 times; the column splits it)
EXTRA = {'fma.tree.col': {'name': 'One column of the compressor tree', 'parent': 'vpu.lane.fma.tree', 'size_m': 1e-05,
                          'size': {'label': 'inferred', 'note': 'order of magnitude: one bit-column of a tree some 40 um wide'},
                          'kind': 'circuit', 'facts': [], 'children': [], 'see': ['lib.cmp42', 'lib.fa'],
                          'blurb': 'One bit position of the multiplier: its 17 partial-product bits pass down through layers of 4:2 compressors. Each passes a carry to the next column and takes one from the column before, so the whole tree works in parallel.'}}


def kind_of(k, where):
    k0 = str(k).strip()
    k1 = KMAP.get(k0, k0)
    if k1 in KINDS:
        return k1, None
    parts = [KMAP.get(x.strip(), x.strip()) for x in k0.split(',')]
    if len(parts) > 1 and all(p in KINDS for p in parts):
        w = next(x for x in WEAK if x in parts)
        return w, f'The statement combines {", ".join(parts)}; it is labelled by the weakest, {w}.'
    raise SystemExit(f'{where}: kind "{k}" is not one of the nine')


def short_of(nid, name):
    if nid in SHORT:
        return SHORT[nid]
    s = re.split(r'\s*[(,:]\s*', name)[0]
    s = re.sub(r'^(The|A|An|One) ', '', s)
    return s[:1].upper() + s[1:] if len(s) <= 26 else s[:24].rstrip() + '…'


def sha(path):
    return hashlib.sha256(open(path, 'rb').read()).hexdigest()


def build(ALL, ml_keys_extra=(), ml_num_keys=()):
    """ALL: the chip page's fact pool (research files and additions), by id. Returns a dict with facts (the new and
    the imported ones, by page id), scales (the nodes, by id), geo, img (the manifest) and ml_num (the memory-levels
    numbers the copied drawings print, by ml key)."""
    INS = json.load(open(os.path.join(HERE, 'inside.json')))
    OUT = json.load(open(os.path.join(HERE, 'outside.json')))
    GEO = json.load(open(os.path.join(HERE, 'outside-geo.json')))
    MLD = json.load(open(os.path.join(ROOT, 'docs', 'reports', 'data', '2026-09-28-memory-levels', 'facts.json')))
    facts, scales, used_chip, ml_need = {}, {}, set(), set(ml_keys_extra)

    def ml_fact(key):
        f = MLD['facts'].get(key)
        if not f:
            raise SystemExit(f'no memory-levels fact {key}')
        k, kn = kind_of(f['kind'], 'ml:' + key)
        return {'id': 'ml:' + key, 'statement': f['statement'], 'kind': k, 'source': f['source'],
                'note': f.get('note') or kn, 'url': f.get('url'), 'page': f.get('page'), 'cards': f.get('cards') or [],
                'caveat': f.get('caveat'), 'value': f.get('value'), 'unit': f.get('unit'), 'set': 'memory-levels'}

    def add_fact(fid, text, kind, source, note=None, caveat=None):
        k, kn = kind_of(kind, fid)
        facts[fid] = {'id': fid, 'statement': text, 'kind': k, 'source': source, 'note': ' '.join(x for x in (note, kn) if x) or None,
                      'url': None, 'page': None, 'cards': [], 'caveat': caveat, 'set': 'deep zoom'}
        return fid

    # ---- inside the chip
    INS['nodes'] = INS['nodes'] + [dict(v, id=k) for k, v in EXTRA.items()]
    for n in INS['nodes']:
        nid = n['id']
        if nid in SKIP:
            continue
        ids = []
        for i, f in enumerate(n.get('facts', [])):
            fid = f.get('fid') or ''
            if fid.startswith('chip:') or fid.startswith('chip-research:'):
                cid = fid.split(':', 1)[1]
                if cid in ALL:
                    used_chip.add(cid); ids.append(cid); continue
            if fid.startswith('ml:'):
                key = fid[3:]
                if key in MLD['facts']:
                    ml_need.add(key); ids.append('ml:' + key); continue
            cav = f.get('caveat')
            note = ('Erbium RTL: core-et\'s RTL is the Erbium branch, the same Minion core lineage as the ET-SoC-1 in a later '
                    'configuration; that the ET-SoC-1 silicon matches it block for block is not confirmed.') if cav == 'erbium-rtl' else None
            ids.append(add_fact(f'in.{nid}.{i + 1}', f['text'], f['label'], f['source'], note, cav))
        sz = n.get('size') or {}
        sk = kind_of(sz.get('label') or 'unknown', nid + ' size')[0]
        s = {'name': n['name'], 'short': short_of(nid, n['name']), 'blurb': n.get('blurb') or '', 'parent': n.get('parent'),
             'm': n.get('size_m'), 'kind': sk, 'note': sz.get('note'), 'facts': ids, 'kids': [c for c in n.get('children', []) if c not in SKIP],
             'see': n.get('see') or [], 'zoom_to': n.get('zoom_to'), 'nk': n.get('kind'),
             'erbium': any(f.get('caveat') == 'erbium-rtl' for f in n.get('facts', []))}
        if n.get('size_m'):
            s['f'] = add_fact(f'size.{nid}', f'{n["name"]}: about {fmt_m(n["size_m"])} across, the width of the view that frames it. '
                              + (sz.get('note') or ''), sk if sk != 'unknown' else 'inferred', 'the deep zoom\'s scale ladder (research/inside.json, size)')
        scales[nid] = s

    # ---- outside the chip
    for lv in OUT['levels']:
        lid = lv['id']
        ids, notes = [], []
        for i, f in enumerate(lv['facts']):
            if f['kind'] == 'note':
                notes.append(f['text']); continue
            ids.append(add_fact(f'out.{lid}.{i + 1}', f['text'], f['kind'], f['source']))
        sk, skn = kind_of(lv.get('size_kind') or 'unknown', lid + ' size')
        img = lv.get('image')
        s = {'name': lv['name'], 'short': short_of(lid, lv['name']), 'blurb': lv.get('blurb') or '', 'parent': lv.get('parent'),
             'm': lv.get('size_m'), 'kind': sk, 'note': lv.get('size_note'), 'facts': ids, 'notes': notes, 'frame_m': lv.get('frame_m'),
             'zoom_from_inner': lv.get('zoom_from_inner'), 'child': lv.get('child'), 'light': lv.get('light'), 'out': True}
        if img:
            s['img'] = {k: img[k] for k in ('file', 'px', 'crop_px', 'credit', 'licence', 'licence_url', 'px_per_mm', 'hotspots_px', 'geometry', 'source_url', 'note') if k in img}
        if lv.get('size_m'):
            word = {'estimate': ' (an estimate)', 'assumed': ' (a frame chosen for the picture, assumed)'}.get(lv.get('size_kind'), '')
            s['f'] = add_fact(f'size.{lid}', f'{lv["name"]}: about {fmt_m(lv["size_m"])} across{word}. ' + (lv.get('size_note') or ''),
                              sk, 'the deep zoom\'s scale ladder (research/outside.json, size_m and size_note)', skn)
        scales[lid] = s
    # the chip's size: the inside tree's die, kept; the outside's child box (the die under the lid) stays on the package
    # ---- the memory-levels facts: those cited, and the numbers the copied drawings print
    ml_num = {}
    for k in ml_num_keys:
        x = MLD['num'].get(k)
        if not x:
            raise SystemExit(f'no memory-levels number {k}')
        ml_num[k] = dict(x, f=' '.join('ml:' + i for i in str(x['f']).split()))
        ml_need.update(str(x['f']).split())
    # (a fact id the copied code names that the memory levels' data does not have stops the build)
    gone = sorted(k for k in ml_need if k not in MLD['facts'])
    if gone:
        raise SystemExit('the copied drawings cite memory-levels facts that do not exist: ' + ', '.join(gone[:20]))
    for key in sorted(ml_need):
        facts['ml:' + key] = ml_fact(key)
    # ---- the image manifest
    img = {}
    for fn in sorted(os.listdir(IMG)):
        if fn.endswith('.webp'):
            img[fn] = {'bytes': os.path.getsize(os.path.join(IMG, fn)), 'sha256': sha(os.path.join(IMG, fn))}
    for s in scales.values():
        if s.get('img') and s['img']['file'] not in img:
            raise SystemExit('no image ' + s['img']['file'])
    # facts read from a search summary of a page that refused the connection (the N7 cell height and density): shown as
    # inferred until someone re-reads the page (DESIGN §7 R8)
    for f in facts.values():
        if 'search summary' in (f.get('source') or '') and f['kind'] == 'outside':
            f['kind'] = 'inferred'
            f['note'] = ((f.get('note') or '') + ' Read from a search engine\'s summary of the page, which refused the connection; not yet re-read, so shown as inferred.').strip()
    onum = {}
    for k, (fid, t) in list(ONUM.items()) + list(INUM.items()):
        st = (facts.get(fid) or ALL.get(fid) or {}).get('statement', '')
        if t not in st:
            raise SystemExit(f'{k}: "{t}" not in {fid}')
        if fid in ALL:
            used_chip.add(fid)
        onum[k] = {'t': t.replace(' x ', ' × '), 'f': fid}
    geo = {k: v for k, v in GEO.items() if k != 'meta'}
    geo['meta'] = {k: GEO['meta'][k] for k in ('units', 'sources', 'privacy', 'sf_nyc_great_circle_km') if k in GEO['meta']}
    return {'facts': facts, 'scales': scales, 'geo': geo, 'img': img, 'ml_num': ml_num, 'used_chip': used_chip, 'onum': onum, 'ml_addr': MLD.get('addr'),
            'outside_meta': {k: OUT['meta'].get(k) for k in ('clock_hz', 'clock_source', 'fibre_group_index', 'fibre_source', 'privacy')}}


def fmt_m(m):
    """A length in words for a statement: the unit that keeps it between 1 and 1,000."""
    LY = 9.4607304725808e15
    def r(v, u):
        t = float(f'{v:.3g}')
        return (f'{t:,.0f}' if t >= 1000 else f'{t:g}') + ' ' + u
    if m >= 0.1 * LY:
        y = m / LY
        return r(y / 1e9, 'billion light-years') if y >= 1e9 else r(y / 1e6, 'million light-years') if y >= 1e6 else r(y, 'light-years')
    if m >= 1e9:
        return r(m / 1e9, 'million km')
    if m >= 1000:
        return r(m / 1000, 'km')
    if m >= 1:
        return r(m, 'm')
    if m >= 0.1:
        return r(m * 100, 'cm')
    if m >= 1e-3:
        return r(m * 1e3, 'mm')
    if m >= 1e-6:
        return r(m * 1e6, 'µm')
    return r(m * 1e9, 'nm')
