#!/usr/bin/env python3
"""Partition the chip diagram's facts, scales and flows into checker slices (every fact in exactly one slice).
Writes slices/<name>.json with the full fact records, the crawled panels of the slice's scales and its flows."""
import json, re, os, sys, collections

REPO = '/home/yaroslavvb/claude/et-soc1-prototyping'
W = '/home/yaroslavvb/claude/work/chip-check-1014'
F = json.load(open(f'{REPO}/docs/reports/data/2026-09-27-chip-diagram/facts.json'))
LZ = json.load(open(f'{REPO}/docs/reports/ladder-img/ladder-data.json'))['facts']
CR = f'{W}/crawl/out'
SC = json.load(open(f'{CR}/scales.json')) if os.path.exists(f'{CR}/scales.json') else []
FL = json.load(open(f'{CR}/flows.json')) if os.path.exists(f'{CR}/flows.json') else []

facts = {}
for k, v in F['facts'].items():
    facts[k] = dict(v, id=k, where='chip')
for k, v in LZ.items():
    facts[k] = dict(v, id=k, where='deepzoom')

# (slice, fact-id regex) in order: first match wins
RULES = [
    ('s07-memlevels', r'^ml:'),
    ('s09-device-physics', r'^(el|n7|si|dope|gate|wire|cu|p)\.|^size\.p\.|^in\.lib\.(fin|finfet|si|gate|wire)\.|^size\.lib\.(wire\.view)$'),
    ('s10-outside', r'^(out|s45|card|host|b|e|ring|cmp)\.|^pcie\.gen4\.|^size\.(bayarea|california|card|earth|host|laniakea|localgroup|milkyway|moon|package|rack|sf|solar|stars|universe|us)$|^buck\.|^size\.lib\.(buck|powerfet|strap)$'),
    ('s08-circuits', r'^(tb|st)\.|^in\.lib\.|^size\.lib\.|^size\.fma\.'),
    ('s01-die-mesh', r'^(chip|die|fw|ms|ms2|et)[.\-]|^chip-minions$|^mesh\.(clock|empty-cells|grid|logical-map|memshire-positions|no-counters|orientation|port-width|shortest-paths|single-attach|voltage|xy-assumption)$|^mesh-hop-|^L(08|09|11|12|23|24|25|26|28|29|31|32|33|34|37|40|42|44|72|101|102|103|104|105|120|121)$|^(size|in)\.(die|mesh|io|master|pcie)\b'),
    ('s02-shire', r'^(shire|neigh|l2|l3|scp|sc|sram)[.\-]|^L(111|114|115|116)$|^(size|in)\.(shire|etlink|fln)\b|^sram-idle$'),
    ('s03-minion', r'^(minion|tfma|tl|ridge)\.|^(size|in)\.(minion|core|vpu|tensor|l1d|l1scp)\b'),
    ('s04-memory', r'^(dram|addr|mem)\.|^lat-|^bw-(dram|l1|l2|l3|scp)|^gs-|^L(41|43|45|46|47|48|50|79|80)$|^(size|in)\.(dram|memshire)\b'),
    ('s05-messaging', r'^(ts|hot|relay|sync)[.\-]|^(ar|bc)\.|^bw-tsend|^mesh\.1kb-knee$|^mesh-bit-mm|^L(70|71|86|87|88|91|92|93|94)$'),
    ('s06-host-power', r'^(pcie|board|clock|volt|power|heat|op|temp|idle|mm|e)[.\-]|^bw-pcie$|^L123$'),
]
SCALES = {
    's01-die-mesh': ['die', 'mesh', 'pcie', 'io', 'die.metal', 'mesh.link.wire', 'package'],
    's02-shire': ['shire', 'shire.meshstop', 'shire.meshstop.router', 'shire.meshstop.xing', 'shire.bank', 'shire.subbank', 'shire.panel', 'shire.uc', 'shire.xbar', 'shire.neigh'],
    's03-minion': ['minion', 'core', 'tensor', 'vpu', 'vpu.lane', 'vpu.lane.fma', 'vpu.lane.fma.tree', 'fma.tree.col', 'l1d', 'l1d.cmp', 'l1d.block', 'l1d.row'],
    's04-memory': ['memshire', 'memshire.phy', 'memshire.phy.dq', 'dram', 'dram.bank', 'dram.cell'],
    's05-messaging': [],
    's06-host-power': ['pcie.phy', 'pcie.lane', 'lib.buck', 'lib.powerfet', 'lib.strap', 'lib.pll'],
    's07-memlevels': ['lib.sram6t', 'lib.dramcell', 'lib.senseamp', 'lib.decoder', 'lib.latch'],
    's08-circuits': ['lib.xor', 'lib.inverter', 'lib.fa', 'lib.nand2', 'lib.cmp42', 'lib.booth', 'lib.mux2', 'lib.shifter', 'lib.adder', 'lib.lzd', 'lib.round', 'lib.icg', 'lib.aoi21', 'lib.nor2', 'lib.regfile', 'lib.rom', 'lib.flipflop', 'lib.logic', 'lib.counter', 'lib.cmpeq', 'lib.fifo', 'lib.xbar', 'lib.ecc', 'lib.diffamp'],
    's09-device-physics': ['lib.finfet', 'lib.fin', 'lib.channel', 'lib.si', 'lib.wire', 'p.cu', 'p.atom', 'p.nucleus', 'p.nucleon', 'p.quark', 'p.electron', 'p.dopant', 'p.planck', 'p.wrap'],
    's10-outside': ['beyond', 'universe', 'laniakea', 'localgroup', 'milkyway', 'stars', 'solar', 'moon', 'earth', 'us', 'california', 'bayarea', 'sf', 'bernal', 'st29', 'studio45', 'rack', 'host', 'card'],
    's11-prose': [],
}
FLOWS = {'s04-memory': ['A', 'B', 'E'], 's05-messaging': ['C', 'D', 'I', 'J', 'K'], 's06-host-power': ['F', 'G', 'H']}

assign = {}
for fid in facts:
    for name, rx in RULES:
        if re.search(rx, fid):
            assign[fid] = name; break
un = [f for f in facts if f not in assign]
cnt = collections.Counter(assign.values())
print('facts', len(facts), 'assigned', len(assign), 'unassigned', len(un), un[:80])
print(sorted(cnt.items()))
scale_ids = [s.get('id') for s in SC]
claimed = {s for v in SCALES.values() for s in v}
print('scales crawled', len(SC), 'unclaimed', [s for s in scale_ids if s not in claimed])
if '--write' in sys.argv:
    os.makedirs(f'{W}/slices', exist_ok=True)
    keep = ('id', 'where', 'statement', 'kind', 'source', 'note', 'url', 'page', 'cards_txt', 'card', 'caveat', 'topic', 'value', 'unit')
    for name in [r[0] for r in RULES] + ['s11-prose']:
        fl = [{k: facts[f][k] for k in keep if facts[f].get(k) not in (None, '')} for f in sorted(assign) if assign[f] == name]
        sc = [s for s in SC if s.get('id') in SCALES.get(name, [])]
        fw = [x for x in FL if x['flow'] in FLOWS.get(name, [])]
        json.dump({'slice': name, 'n_facts': len(fl), 'facts': fl, 'scales': sc, 'flows': fw}, open(f'{W}/slices/{name}.json', 'w'), indent=1, ensure_ascii=False)
        print(name, len(fl), 'facts', len(sc), 'scales', len(fw), 'flows', os.path.getsize(f'{W}/slices/{name}.json'), 'bytes')
