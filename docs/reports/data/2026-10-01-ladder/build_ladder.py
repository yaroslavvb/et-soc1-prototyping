#!/usr/bin/env python3
"""The shared ladder's data (1 Oct 2026): the scales the chip diagram and the memory levels draw beyond the chip's own
three, their facts and the numbers their drawings print. Design: /home/yaroslavvb/claude/work/ladder/DESIGN.md §2.4
(written in the session's work directory; its decisions are summarised in README.md beside this file).

    build_ladder.py           writes ladder.json beside this file
    build_ladder.py --check   exits 1 if ladder.json is stale, or if any rule below fails

Inputs (research/, each with the script that wrote it):
  process.json    (build_process.py)    TSMC N7, the ET-SoC-1's process facts and the electronics, 99 facts
  particles.json  (build_particles.py)  the atom to the Planck length, the wrap, the early universe, 93 facts
  studio45.json   (build_studio45.py)   Studio 45, Bernal Heights and 29th Street, from the owner's words and public data
  bernal-geo.json (simplify_bernal_geo.py) the Bernal Heights map and 29th Street's profile, simplified

Output, ladder.json:
  nodes    the new scales and the corrected ones: name, short name, a beginner's lead (blurb), size in metres with its
           kind and fact (or a bound, or "conceptual" for the ring), the facts its panel lists, and egg: true for the
           levels above the rack, which the pages never list in advance (the owner, 1 Oct 07:25: an easter egg)
  facts    every fact, by id, with its kind (one of the nine), source, URL where it has one, and note
  more     facts to add to the chip's existing scales (the die, a minion, a 6T cell, ...), by scale
  num      the numbers the new drawings print: key -> {t: the text drawn, f: the fact}; the build checks that each
           text occurs in its fact's statement
  ring     the ring of sizes: its ticks (a scale and its size fact) and the strip of epochs
  geo      the Bernal Heights map and the street's profile

Rules it checks: every fact has one of the nine kinds; every outside, spec and generic fact has a source; every
derived and inferred fact says how (a source naming its inputs, or a note); every number a drawing prints occurs in
its fact; the superseded fin, gate and channel numbers (6-7 nm, 45-50 nm, a 20 nm gate, 270,000 atoms) appear in no
statement, lead or printed number; no geo point but the hill's summit, and nothing called a studio in the geo."""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
R = os.path.join(HERE, 'research')
OUT = os.path.join(HERE, 'ladder.json')
KINDS = ['measured', 'spec', 'derived', 'inferred', 'outside', 'generic', 'owner', 'hypothesis', 'unknown']

PROC = json.load(open(os.path.join(R, 'process.json')))
PART = json.load(open(os.path.join(R, 'particles.json')))
S45 = json.load(open(os.path.join(R, 'studio45.json')))
GEO = json.load(open(os.path.join(R, 'bernal-geo.json')))

facts = {}


def add(fid, statement, kind, source, url=None, note=None, quote=None):
    if fid in facts:
        raise SystemExit(f'fact {fid} twice')
    if kind not in KINDS:
        raise SystemExit(f'{fid}: kind {kind!r} is not one of the nine')
    facts[fid] = {k: v for k, v in (('statement', statement), ('kind', kind), ('source', source), ('url', url), ('note', note), ('quote', quote)) if v}
    return fid


# ---- the research facts
for f in PROC['facts']:
    add(f['id'], f['statement'], f['kind'], f['source'], f.get('url'), f.get('note'), f.get('quote'))
PLEV = {lv['id']: lv for lv in PART['levels']}
for lv in PART['levels']:
    for i, f in enumerate(lv['facts']):
        add(f'{lv["id"]}.{i + 1}', f['text'], f['kind'], f['source'], None, f.get('note'))
for e in PART['epochs'] + [PART['stardust']]:
    for i, f in enumerate(e['facts']):
        add(f'{e["id"]}.{i + 1}', f['text'], f['kind'], f['source'], None, f.get('note'))
for f in S45['facts']:
    add(f['id'], f['statement'], f['kind'], f['source'], f.get('url'), f.get('note'))
# the arithmetic of the particles' derived and inferred facts whose research gave none (DESIGN §2.4)
HOW = {
    'p.atom.4': 'sqrt(3)/4 x 0.5431 nm = 0.2352 nm; 8 atoms per cubic cell / (0.5431 nm)^3 = 49.9 per nm^3',
    'p.atom.11': 'a sphere of radius 117.6 pm (half the 0.2352 nm neighbour distance) against the nucleus\'s 3.64 fm radius (1.2 fm x 28^(1/3)): 117.6 / 0.00364 = 32,300',
    'p.dopant.5': '10^21 per cm^3 = 1 per nm^3; silicon has 49.9 atoms per nm^3 (p.atom.4)',
    'p.nucleus.6': 'the 32,000 ratio of p.atom.11 applied to a 1 cm marble: 1 cm x 32,300 = 323 m',
    'p.electron.4': 'the dipole limit divided by the charge: 4.1 x 10^-30 e cm / e = 4.1 x 10^-30 cm = 4.1 x 10^-32 m',
    'p.electron.7': '1 C / 1.602176634 x 10^-19 C = 6.2415 x 10^18',
    'p.planck.5': 'log10(8.74 x 10^26 m / 1.616 x 10^-35 m) = 61.7',
    'e.cmb.2': '2.7255 K x (1 + 1089.92) = 2,973 K',
    'e.bbn.4': '1 / eta = 1 / 6.04 x 10^-10 = 1.66 x 10^9',
    'e.bbn.5': 'the standard reading of the baryon asymmetry (eta) in PDG review 22, sec. 22.3.6; why it arose is the next fact',
    'e.qcd.3': 'entropy conservation (a T g*s^(1/3) constant) from today\'s 8.74 x 10^26 m, 2.7255 K and g*s = 3.91 back to 156.5 MeV, with g*s between 69/4 (hadrons) and 205/4 (quarks and gluons): 5.6-8.0 x 10^14 m, 3,700-5,300 au',
    'e.qcd.5': 'protons and neutrons formed at the QCD crossover (e.qcd.1-2); silicon is made in stars (e.stars.1)',
    'e.stars.4': 'e.stars.1 (silicon from massive stars and supernovae), e.stars.2 (the Solar System from enriched gas, 4,567 million years ago) and e.qcd.5',
}
for k, v in HOW.items():
    facts[k]['note'] = (facts[k].get('note', '') + ' ' if facts[k].get('note') else '') + v

# ---- facts of the ladder's own (DESIGN §4.1-4.2): each derived from the research's, the arithmetic in its note
HU6 = 'C. Hu, Modern Semiconductor Devices for Integrated Circuits (Pearson 2010), ch. 6 (author\'s free chapter)'
add('el.rails', 'In CMOS logic a 0 is the ground rail, 0 V, and a 1 is the supply rail: here 0.517 V on a minion at 600 MHz. A gate at 0 V turns an n-type transistor off; a gate at the rail turns it on.',
    'generic', HU6 + '; the minion rail measured on this chip (et.v-minion)', 'https://www.chu.berkeley.edu/wp-content/uploads/2020/01/Chenming-Hu_ch6-1.pdf')
add('el.off-channel', 'An "off" transistor still lets about 10 billion electrons a second through, but each crosses its 16.5 nm channel in about 0.2 ps, so at any instant its channel holds on average 0.002 electrons.',
    'derived', 'arithmetic on et.leak-per-tr (10 billion electrons a second) and si.mobility (0.2 ps to cross the channel)',
    note='10^10 per second x 0.2 x 10^-12 s = 0.002. An average over every transistor on the chip; a given off transistor leaks more or less.')
add('el.half-energy', 'At the minion rail\'s 0.517 V each switch costs (0.517 / 0.75)² = 0.48 of what it would at N7\'s nominal 0.75 V: half the energy, since the energy goes as the voltage squared.',
    'derived', 'arithmetic on et.v-minion, et.nominal-075 and el.dynamic (E = C V²)')
add('el.sram-electrons', 'A 6T SRAM bit holds roughly a thousand electrons (440-1,300) on its storage node at the 0.705 V SRAM rail; a latch bit of the minion\'s L1 at 0.517 V holds about 320-970.',
    'inferred', 'arithmetic on gate.cap-fin, n7.sram-dims, et.v-sram and et.v-minion (el.sram-node)',
    note='No N7 storage-node capacitance is published: 0.1-0.3 fF is assumed (el.sram-node). The inverters restore the charge all the time, so it needs no refresh.')
add('size.p.nucleus', 'The silicon-28 nucleus is about 8.1 fm across: a uniform sphere with its measured rms charge radius of 3.1224 fm has a radius of 4.03 fm. (The rule R = 1.2 fm x 28^(1/3) gives 7.3 fm across; a nucleus has a soft edge, so any size is a convention.)',
    'derived', 'arithmetic on p.nucleus.3 (the measured rms charge radius) and p.nucleus.2 (the 1.2 A^(1/3) rule)', note='sqrt(5/3) x 3.1224 fm = 4.031 fm; x 2 = 8.06 fm')
add('size.p.atom', 'One silicon atom takes about 0.235 nm in the crystal: the distance between neighbours, sqrt(3)/4 x 0.5431 nm.',
    'derived', 'arithmetic on si.lattice (CODATA 2022 lattice parameter)', note=PLEV['p.atom']['size_note'])
add('size.lib.dramcell', 'A DRAM cell of the 2019-2022 generations is roughly 0.1 µm across (an order of magnitude: about 6 F² at a feature size of 15-20 nm); the card\'s DRAM generation is not known.',
    'inferred', 'the memory levels\' DRAM cell (dram.cell, inside.json); TechInsights, DRAM scaling trend (el.dram-cell)', 'https://www.techinsights.com/blog/dram-scaling-trend-and-beyond',
    note='Order of magnitude only: the cell is about 6 F², F the half-pitch of its generation; its capacitor is far taller than it is wide.')
add('ring.mid', 'On a logarithmic scale the middle of all sizes, between the Planck length (1.6 x 10^-35 m) and the observable universe (8.7 x 10^26 m), is 0.12 mm: about a minion\'s L1 data cache.',
    'derived', 'arithmetic on p.planck.1 and the observable universe\'s diameter (out.universe.2): the square root of their product (p.wrap.7)')

# ---- the scales (DESIGN §1.2, §1.4, §1.6, §4.5, §4.6)
EGG = ['beyond', 'universe', 'laniakea', 'localgroup', 'milkyway', 'stars', 'solar', 'moon', 'earth', 'us', 'california', 'bayarea', 'sf',
       'bernal', 'st29', 'studio45', 'p.wrap']
pl = lambda i: PLEV[i]['blurb']
pf = lambda i, *ns: [f'{i}.{n}' for n in ns] if ns else [f'{i}.{k + 1}' for k in range(len(PLEV[i]['facts']))]
nodes = {
    # ---- inner: the device, corrected to N7's published numbers
    'lib.finfet': {'name': 'FinFET transistor', 'short': 'FinFET', 'm': 5.7e-8, 'kind': 'outside', 'f': 'n7.cpp',
                   'blurb': 'The switch everything is made of. A voltage on the gate decides whether current flows: at 0 V the path along the fin is shut; at the supply rail (0.517 V on a minion) the gate\'s field pulls a thin sheet of electrons into the fin, and current flows from source to drain. The gate drapes over the fins on three sides.',
                   'facts': ['el.switch', 'el.rails', 'n7.cpp', 'n7.fin-pitch', 'n7.two-fin', 'n7.cells', 'n7.generation', 'n7.litho', 'n7.features', 'n7.vt-options', 'n7.vt-abs',
                             'n7.ss', 'n7.dibl', 'el.off-not-off', 'el.ss-80c', 'el.finfet-why', 'et.nominal-075', 'et.sweet-spot', 'et.v-minion', 'el.half-energy',
                             'et.leak-per-tr', 'et.leakage', 'et.leak-double', 'n7.contacts-co', 'dope.n-sd', 'dope.p-sd', 'n7.density-hd', 'n7.hpc']},
    'lib.fin': {'name': 'The fin, in section', 'short': 'Fin', 'm': 5.2e-8, 'kind': 'outside', 'f': 'n7.fin-height',
                'blurb': 'A wall of crystalline silicon 6 nm thick and 52 nm tall, tapered with a rounded top; fins stand 30 nm apart. The gate wraps over three sides, so it holds the channel shut tightly: that is why fins replaced flat transistors.',
                'note': 'N7\'s fin: 6 nm wide and 52 nm tall (WikiChip Fuse on TSMC\'s IEDM 2016 paper); the earlier drawing\'s 6-7 by 45-50 nm, inferred from 10 nm-class sections, is superseded',
                'facts': ['n7.fin-width', 'n7.fin-height', 'n7.fin-pitch', 'n7.weff', 'el.finfet-why', 'gate.hfo2', 'gate.eot', 'gate.metals', 'gate.undoped-vt', 'gate.cap-fin',
                          'n7.contacts-co', 'cmp.tsmc10', 'cmp.intel10', 'cmp.gf7']},
    'lib.gate': {'name': 'Gate stack', 'short': 'Gate stack', 'm': 1.65e-8, 'kind': 'outside', 'f': 'n7.leff',
                 'blurb': 'The gate: a metal electrode on an insulating layer only a few atoms thick (hafnium oxide on a thin silicon oxide), wrapped over the top and both sides of the fin. Its metal\'s work function sets the voltage at which the transistor turns on.',
                 'note': 'effective gate length about 16.5 nm (N7, Dick James on IEDM 2016); the earlier 20 nm (IRDS, 7 nm-class) is superseded',
                 'facts': ['n7.leff', 'gate.hfo2', 'gate.eot', 'gate.metals', 'gate.undoped-vt', 'gate.cap-fin', 'n7.generation', 'n7.vt-options']},
    'lib.channel': {'name': 'Channel (the silicon under the gate)', 'short': 'Channel', 'm': 1.65e-8, 'kind': 'outside', 'f': 'n7.leff',
                    'blurb': 'The strip of fin under the gate, 16.5 nm long, where the current flows: about 257,000 silicon atoms and almost no dopant atoms. Off, it is nearly empty of free electrons; on, the gate pulls in about a hundred.',
                    'note': 'the channel\'s length, the effective gate length of N7: 16.5 nm; the channel is 6 nm wide and 52 nm tall',
                    'facts': ['n7.leff', 'dope.count-channel', 'si.planes-width', 'el.channel-electrons', 'el.off-channel', 'el.off-not-off', 'et.leak-per-tr', 'n7.ss', 'n7.dibl',
                              'si.ni', 'si.mobility', 'dope.channel', 'dope.levels', 'gate.undoped-vt', 'p.atom.9', 'p.dopant.7', 'p.atom.10']},
    'lib.si': {'name': 'Silicon crystal', 'short': 'Silicon crystal', 'm': 5.431e-10, 'kind': 'outside', 'f': 'si.lattice',
               'blurb': 'Silicon atoms in a diamond lattice, each bonded to four neighbours. Every outer electron is held in a bond; freeing one takes 1.12 eV, 43 times the thermal energy at room temperature, so pure silicon barely conducts. A transistor\'s electrons come from its doped source instead.',
               'facts': ['si.lattice', 'si.density', 'si.planes-width', 'si.bandgap', 'el.kt', 'si.ni', 'dope.donor-acceptor', 'si.mobility', 'p.atom.7', 'p.atom.8', 'p.atom.6']},
    'lib.dramcell': {'name': 'A DRAM cell, in section', 'short': 'DRAM cell', 'm': 1e-7, 'kind': 'inferred', 'f': 'size.lib.dramcell',
                     'blurb': 'A DRAM bit is charge on one tiny capacitor, reached through one transistor. With no circuit to restore it, the charge leaks away, so every row is read and rewritten every 32 ms. Drawn generically: the card\'s DRAM is made on a DRAM process, not TSMC N7, and its generation is not known.',
                     'facts': ['el.dram-cell', 'el.dram-leak', 'size.lib.dramcell', 'el.sram-electrons', 'et.v-other']},
    # ---- inner: the atom and below (particles.json)
    'p.atom': {'name': 'A silicon atom', 'short': 'Atom', 'm': 2.352e-10, 'kind': 'derived', 'f': 'size.p.atom', 'blurb': pl('p.atom'),
               'facts': ['size.p.atom'] + pf('p.atom') + pf('p.core') + ['si.atom']},
    'p.dopant': {'name': 'A dopant atom: phosphorus in the crystal', 'short': 'Dopant atom', 'm': 2.352e-10, 'kind': 'derived', 'f': 'size.p.atom', 'blurb': pl('p.dopant'),
                 'facts': pf('p.dopant') + ['dope.n-sd', 'dope.p-sd', 'dope.donor-acceptor', 'dope.count-sd', 'el.kt']},
    'p.nucleus': {'name': 'The silicon-28 nucleus', 'short': 'Nucleus', 'm': 8.06e-15, 'kind': 'derived', 'f': 'size.p.nucleus', 'blurb': pl('p.nucleus'),
                  'facts': ['size.p.nucleus'] + pf('p.nucleus') + ['si.nucleus', 'p.atom.11']},
    'p.nucleon': {'name': 'A proton', 'short': 'Proton', 'm': 1.6815e-15, 'kind': 'outside', 'f': 'p.nucleon.1', 'blurb': pl('p.nucleon'), 'facts': pf('p.nucleon')},
    'p.quark': {'name': 'A quark', 'short': 'Quark', 'm': 8.6e-19, 'kind': 'outside', 'f': 'p.quark.1',
                'bound': {'txt': '< 4.3 × 10⁻¹⁹ m', 'words': 'no size measured: a radius under 4.3 × 10⁻¹⁹ m'}, 'blurb': pl('p.quark'), 'facts': pf('p.quark')},
    'p.electron': {'name': 'An electron', 'short': 'Electron', 'm': 4e-20, 'kind': 'outside', 'f': 'p.electron.2',
                   'bound': {'txt': '< 2 × 10⁻²⁰ m', 'words': 'no size measured: a radius under 2 × 10⁻²⁰ m'}, 'blurb': pl('p.electron'), 'facts': pf('p.electron') + ['el.electron']},
    'p.planck': {'name': 'The Planck length', 'short': 'Planck length', 'm': 1.616255e-35, 'kind': 'outside', 'f': 'p.planck.1', 'blurb': pl('p.planck'), 'facts': pf('p.planck')},
    'p.wrap': {'name': 'The ring of sizes', 'short': 'Ring of sizes', 'm': None, 'kind': 'unknown', 'f': None, 'conceptual': True,
               'blurb': 'This is not further out in space. The ring is a picture of every size at once, the smallest joined to the largest; the links across it are physics, not distance. Looking far out is looking back in time, to an early universe that was a sea of quarks.',
               'facts': pf('p.wrap') + ['ring.mid'] + [f'e.cmb.{i}' for i in range(1, 7)] + [f'e.qcd.{i}' for i in range(1, 7)] + [f'e.stars.{i}' for i in range(1, 5)]
               + [f'e.bbn.{i}' for i in range(1, 7)] + [f'e.ew.{i}' for i in range(1, 4)] + ['e.planck.1', 'e.planck.2']},
    # ---- outer (DESIGN §4.6), an easter egg with everything above the rack
    'bernal': {'name': 'Bernal Heights', 'short': 'Bernal Heights', 'm': 2200.0, 'kind': 'derived', 'f': 'b.2',
               'blurb': 'Bernal Heights, a hill neighbourhood of about 26,000 people in south-east San Francisco. The hill is red chert: quartz, silicon dioxide, from the shells of plankton that lived 100 to 200 million years ago. Refined, the same silicon is the die. Light crosses the neighbourhood in 7.3 µs, about 4,400 of the chip\'s clock ticks.',
               'facts': ['b.1', 'b.2', 'b.3', 'b.4', 'b.5', 'b.6', 'b.7', 'b.8', 'b.9']},
    'st29': {'name': '29th Street', 'short': '29th Street', 'm': 1293.0, 'kind': 'derived', 'f': 'st.1',
             'blurb': '29th Street, 1.3 km long, drops about 95 m from the hills of Noe Valley to the flats where the Mission meets Bernal Heights. Light runs its length in 4.3 µs, about 2,600 ticks of the chip\'s clock.',
             'facts': ['st.1', 'st.2', 'st.3', 's45.1']},
    'studio45': {'name': 'Studio 45', 'short': 'Studio 45', 'm': 37.0, 'kind': 'derived', 'f': 's45.6',
                 'blurb': 'Studio 45, a co-working space and workshop for people who build hardware: the lab\'s rack is here. Light crosses the building in 123 ns, 74 ticks of the chip\'s clock.',
                 'note': 'the building at its address, about 37 m deep and 9 m wide (DataSF building footprints); where the rack stands in it is not recorded',
                 'facts': ['s45.1', 's45.2', 's45.3', 's45.4', 's45.5', 's45.6', 's45.7', 's45.8']},
}
for k in EGG:
    if k in nodes:
        nodes[k]['egg'] = True
# what the chip's existing scales gain (DESIGN §4.1, §4.4): the process and Esperanto's facts, scale by scale
more = {
    'die': ['et.process', 'et.process-n7', 'et.transistors', 'et.die-area', 'et.masks', 'et.density', 'et.sram-bytes', 'et.cores', 'et.power', 'et.leakage', 'et.leak-double',
            'n7.start', 'n7.litho', 'n7.vs-n16', 'n7.density-hd', 'el.dynamic'],
    'package': ['et.package'],
    'minion': ['et.sweet-spot', 'et.lib-04', 'et.one-plane', 'et.v-minion', 'el.half-energy', 'et.cdyn-target', 'et.cdyn-measured', 'et.electrons-per-cycle', 'et.tr-per-minion',
               'et.ops-per-ghz', 'et.tensor-512', 'et.vt-area', 'et.custom-sram', 'et.range'],
    'shire': ['et.shire-supplies', 'et.sram-nominal', 'et.per-shire-v', 'et.custom-sram'],
    'shire.neigh': ['et.wires-slow', 'et.icache'],
    'mesh': ['et.v-noc'],
    'memshire': ['et.v-other'],
    'vpu.lane': ['et.trans-rom'],
    'die.metal': ['n7.mmp', 'n7.metal-layers', 'n7.cu-co-liner', 'n7.contacts-co', 'wire.cu', 'n7.litho'],
    'lib.sram6t': ['el.sram-electrons', 'el.sram-node', 'n7.sram-hd', 'n7.sram-dims', 'n7.sram-vmin', 'et.sram-nominal', 'et.v-sram', 'et.custom-sram'],
    'lib.latch': ['el.sram-electrons', 'et.one-plane', 'et.custom-sram', 'et.v-minion'],
    'lib.flipflop': ['et.flip-reg', 'el.bus-bit', 'el.dynamic'],
    'lib.inverter': ['el.switch', 'el.rails', 'el.dynamic', 'n7.cells'],
    'lib.nand2': ['el.switch', 'el.rails'],
    'lib.xor': ['el.switch'],
    'dram.cell': ['el.dram-cell', 'el.dram-leak'],
}

# ---- the numbers the new drawings print: key -> (fact, the text as it occurs in the fact[, the text drawn])
NUM = {
    # the device
    'n7_cpp': ('n7.cpp', '57 nm'), 'n7_fp': ('n7.fin-pitch', '30 nm'), 'n7_cell': ('n7.cells', '240 nm'), 'n7_fw': ('n7.fin-width', '6 nm'),
    'n7_fh': ('n7.fin-height', '52 nm'), 'n7_lg': ('n7.leff', '16.5 nm'), 'n7_weff': ('n7.weff', '110 nm'), 'n7_ss': ('n7.ss', '65 mV per decade'),
    'v_min': ('et.v-minion', '0.517 V'), 'v_sram': ('et.v-sram', '0.703-0.707 V'), 'v_noc': ('et.v-noc', '0.485 V'), 'v_0': ('el.rails', '0 V'),
    'ch_at': ('dope.count-channel', '257,000'), 'ch_dop': ('dope.count-channel', '0.05 to 5 dopant atoms'),
    'ch_e': ('el.channel-electrons', '85-120 electrons'), 'leak_e': ('et.leak-per-tr', '10 billion electrons a second'),
    'off_e': ('el.off-channel', '0.002 electrons'), 'cross_t': ('si.mobility', '0.2 ps'),
    'hfo2': ('gate.hfo2', 'HfO2', 'HfO₂'), 'k24': ('gate.hfo2', '~24', 'k ≈ 24'), 'tial': ('gate.metals', 'TiAl'), 'tin': ('gate.metals', 'TiN'),
    'wf': ('gate.metals', 'about 4.1 and 4.85 eV'), 'v_nom': ('et.nominal-075', '0.75 V'), 'dop_sd': ('dope.n-sd', '1.75e21', '1.75 × 10²¹'),
    'gap': ('si.bandgap', '1.12 eV'), 'kt': ('el.kt', '25.9 meV'), 'kt43': ('el.kt', 'about 43 kT'), 'dop_e': ('dope.donor-acceptor', 'about 50 meV'),
    'si_la': ('si.lattice', '0.5431 nm'), 'si_bd': ('si.lattice', '0.235 nm'), 'si_pw': ('si.planes-width', 'about 31 planes'),
    'ni': ('si.ni', '1e10 free electrons per cm³', '10¹⁰ free electrons per cm³'),
    'sram_e': ('el.sram-electrons', 'roughly a thousand electrons'), 'latch_e': ('el.sram-electrons', 'about 320-970'),
    'dram_e': ('el.dram-cell', '45,000-70,000 electrons'), 'dram_ms': ('el.dram-leak', '32 ms'), 'dram_fa': ('el.dram-leak', '30 femtoamps'),
    'reg_e': ('et.flip-reg', '38,000 electrons'), 'bus_e': ('el.bus-bit', '190,000 electrons'), 'cyc_e': ('et.electrons-per-cycle', '540 million electrons'),
    'half': ('el.half-energy', '0.48'),
    # the atom and below
    'at_shells': ('p.atom.1', '2 in the first shell, 8 in the second and 4 in the third'), 'at_14': ('p.atom.1', '14 electrons'),
    'at_ion': ('p.atom.2', '8.15'), 'at_ion5': ('p.atom.2', '166.8 eV'), 'at_nn': ('size.p.atom', '0.235 nm'), 'at_32k': ('p.atom.11', 'about 32,000 times'),
    'nu_pn': ('p.nucleus.1', '14 protons and 14 neutrons'), 'nu_rms': ('p.nucleus.3', '3.1224'), 'nu_mass': ('p.nucleus.4', '99.97%'),
    'nu_size': ('size.p.nucleus', 'about 8.1 fm'), 'nu_bind': ('p.nucleus.7', '8.448 MeV per nucleon'),
    'pr_r': ('p.nucleon.1', '0.84075'), 'pr_m': ('p.nucleon.3', '938.272 MeV'), 'pr_uud': ('p.nucleon.4', 'uud'), 'pr_1pc': ('p.quark.3', '1% of the proton'),
    'qk_b': ('p.quark.1', '4.3 x 10^-19 m', '4.3 × 10⁻¹⁹ m'), 'qk_u': ('p.quark.3', '2.16'), 'qk_d': ('p.quark.3', '4.70'), 'qk_1955': ('p.quark.2', '1,955 times'),
    'el_b': ('p.electron.2', '2 x 10^-20 m', '2 × 10⁻²⁰ m'), 'el_q': ('p.electron.1', '1.602176634 x 10^-19 C', '1.602176634 × 10⁻¹⁹ C'),
    'pl_l': ('p.planck.1', '1.616255 x 10^-35 m', '1.616255 × 10⁻³⁵ m'), 'pl_16': ('p.planck.3', '16 powers of ten'), 'pl_617': ('p.planck.5', '61.7 powers of ten'),
    'dp_p': ('p.dopant.1', '0.045 eV'), 'dp_50': ('p.dopant.5', 'about 1 atom in 50'),
    'ring_mid': ('ring.mid', '0.12 mm'),
    'ep_cmb': ('e.cmb.1', '372.6 +/- 1.0 thousand years', '372,600 years'), 'ep_cmbT': ('e.cmb.2', '2,973 K'), 'ep_bbn': ('e.bbn.1', 'about 180 s', 'about 3 minutes'),
    'ep_qcd': ('e.qcd.2', '14-24 microseconds'), 'ep_qcdT': ('e.qcd.1', '156.5 MeV'), 'ep_ew': ('e.ew.2', '9 picoseconds'), 'ep_pl': ('e.planck.1', '5.391247 x 10^-44 s', '5.4 × 10⁻⁴⁴ s'),
    'ep_sun': ('e.stars.2', '4,567.30 +/- 0.16 million years', '4,567 million years'),
    # the outer levels
    'b_area': ('b.2', '2.79 km²'), 'b_sum': ('b.4', '142 m'), 'b_park': ('b.5', '10.7 ha'), 'b_pop': ('b.3', '26,140'), 'b_light': ('b.8', '7.3 µs'),
    'st_len': ('st.1', '1.29 km'), 'st_top': ('st.2', '126 m'), 'st_bot': ('st.2', 'about 30 m'), 'st_drop': ('st.2', 'about 95 m'), 'st_light': ('st.3', '4.31 µs'),
    's45_l': ('s45.6', '37 m'), 's45_w': ('s45.6', '9 m wide', '9 m'), 's45_h': ('s45.6', '6 to 8 m'), 's45_cnc': ('s45.3', '4 x 8 ft', '4 × 8 ft'), 's45_light': ('s45.7', '123 ns'),
}
# the ring's ticks: a scale and the fact of its size (the drawing places each at its size's log)
RING = [('p.planck', 1.616255e-35, 'p.planck.1'), ('p.quark', 8.6e-19, 'p.quark.1'), ('p.nucleon', 1.6815e-15, 'p.nucleon.1'), ('p.atom', 2.352e-10, 'size.p.atom'),
        ('lib.fin', 6e-9, 'n7.fin-width'), ('l1d', 1.2e-4, 'ring.mid'), ('die', 0.0257, None), ('studio45', 37.0, 's45.6'), ('earth', 1.2742e7, None),
        ('solar', 9.0e12, None), ('milkyway', 9.46e20, None), ('universe', 8.738988638177877e26, None)]
EPOCHS = [('e.cmb', 'ep_cmb', 'the oldest light'), ('e.bbn', 'ep_bbn', 'the first nuclei'), ('e.qcd', 'ep_qcd', 'quarks become protons'),
          ('e.ew', 'ep_ew', 'particles get their masses'), ('e.planck', 'ep_pl', 'the Planck time')]


def norm(s):
    return s.replace('×', 'x').replace('–', '-')


def build():
    num = {}
    for k, v in NUM.items():
        fid, t = v[0], v[1]
        st = facts.get(fid, {}).get('statement', '')
        if t not in st:
            raise SystemExit(f'num {k}: "{t}" is not in {fid}: {st[:160]}')
        num[k] = {'t': v[2] if len(v) > 2 else t, 'f': fid}
    for nid, n in nodes.items():
        for f in n.get('facts', []) + ([n['f']] if n.get('f') else []):
            if f not in facts:
                raise SystemExit(f'{nid}: no fact {f}')
    for nid, fl in more.items():
        for f in fl:
            if f not in facts:
                raise SystemExit(f'more {nid}: no fact {f}')
    # the checks of DESIGN §2.4
    bad = []
    for fid, f in facts.items():
        if f['kind'] in ('spec', 'outside', 'generic') and not f.get('source'):
            raise SystemExit(f'{fid}: a {f["kind"]} fact without a source')
        if f['kind'] in ('derived', 'inferred') and not (f.get('note') or f.get('quote') or re.search(r'arithmetic|derived|from|model|estimate', f.get('source', ''))):
            bad.append(f'{fid}: a {f["kind"]} fact that does not say how')
    if bad:
        raise SystemExit('\n'.join(bad))
    STALE = re.compile(r'6-7 nm|45-50 nm|270,000|6 x 20 x 45|about 20 nm long')
    for where, text in [(f'fact {k}', v['statement']) for k, v in facts.items()] + [(f'lead {k}', v.get('blurb', '')) for k, v in nodes.items()] + [(f'num {k}', v['t']) for k, v in num.items()]:
        if STALE.search(text) and not text.startswith('TSMC 10 nm') and 'Intel 10 nm' not in text:
            raise SystemExit(f'{where}: a superseded fin, gate or channel number: {text[:140]}')
    g = json.dumps(GEO)
    if re.search(r'studio', g, re.I) and not re.search(r'of the studio', g):
        raise SystemExit('the geo names a studio')
    pts = [k for k, v in GEO.items() if isinstance(v, dict) and 'xy_km' in v]
    if pts != ['summit']:
        raise SystemExit(f'the geo has points other than the summit: {pts}')
    ring = []
    for nid, m, f in RING:
        ring.append({'id': nid, 'm': m, 'f': f})
    eps = []
    for eid, key, lab in EPOCHS:
        e = next(x for x in PART['epochs'] if x['id'] == eid)
        eps.append({'id': eid, 'lab': lab, 'num': key, 'T_K': e.get('temperature_K'), 't_s': e.get('time_s')})
    out = {'meta': {'written': '2026-10-01', 'by': 'build_ladder.py', 'inputs': ['research/process.json', 'research/particles.json', 'research/studio45.json', 'research/bernal-geo.json'],
                    'egg': 'the levels above the rack are an easter egg (the owner, 1 Oct 2026 07:25 PDT): no written hierarchy names them; a reader finds them by pressing Up',
                    'kinds': KINDS},
           'nodes': nodes, 'more': more, 'facts': facts, 'num': num, 'ring': {'ticks': ring, 'epochs': eps},
           'geo': {'bernal': GEO}}
    return json.dumps(out, indent=1, ensure_ascii=False) + '\n'


if __name__ == '__main__':
    s = build()
    if '--check' in sys.argv:
        old = open(OUT).read() if os.path.exists(OUT) else ''
        if old != s:
            print('ladder.json is stale: run build_ladder.py'); sys.exit(1)
        print('ladder.json is current:', len(facts), 'facts,', len(nodes), 'scales,', len(NUM), 'numbers'); sys.exit(0)
    open(OUT, 'w').write(s)
    print('wrote', OUT, len(s), 'bytes:', len(facts), 'facts,', len(nodes), 'scales,', len(NUM), 'numbers')
