#!/usr/bin/env python3
"""Build facts-numbers.json: measured numbers per ET-SoC-1 component, for the chip diagram's overlays.

Every value is read from a committed data file where one holds it (and checked against the page's rounding),
or quoted from the page / claim index text with its line. Run from anywhere; paths are absolute.
"""
import json, os, re

REPO = '/home/yaroslavvb/claude/et-soc1-pages'
OUT = '/tmp/claude-1019/-home-yaroslavvb-claude/ed6d06d5-de26-4323-94f1-0dc808eafbda/scratchpad/chip/facts-numbers.json'

def J(p):
    return json.load(open(os.path.join(REPO, p)))

MAN = J('docs/reports/data/2026-09-23-energy-manual/manual.json')
GS = J('docs/reports/data/2026-09-25-claims-v3/results/gs.json')
MMB = J('docs/reports/data/2026-09-25-claims-v3/results/mmb.json')
ONCHIP = J('docs/reports/data/2026-09-22-onchip-aifoundry2/onchip.json')
WREP = J('docs/reports/data/2026-09-24-wire-energy/report.json')
LAT = J('docs/reports/data/2026-09-25-claims-v3/results/lat.json')
_h = open(os.path.join(REPO, 'docs/reports/2026-09-18-et-soc1-ridge-points.html')).read()
RIDGE = json.loads(re.search(r'<script[^>]*id="ridge-data"[^>]*>(.*?)</script>', _h, re.S).group(1))

# claims index line numbers, looked up by a unique substring so the citation stays right
CLAIMS_PATH = 'docs/findings/05-claims.md'
CLAIMS = open(os.path.join(REPO, CLAIMS_PATH)).read().split('\n')
def cl(sub):
    hits = [i + 1 for i, l in enumerate(CLAIMS) if sub in l]
    assert len(hits) >= 1, sub
    return f'{CLAIMS_PATH}:{hits[0]}'

def mdline(path, sub):
    lines = open(os.path.join(REPO, path)).read().split('\n')
    hits = [i + 1 for i, l in enumerate(lines) if sub in l]
    assert hits, (path, sub)
    return f'{path}:{hits[0]}'

PAGES = {
    'energy': ('The energy manual', 'docs/reports/2026-09-23-energy-manual.html', 'https://spacesheep.dev/@yaroslavvb/et-soc1-energy-manual'),
    'memhier': ('Memory hierarchy', 'docs/reports/2026-09-18-et-soc1-memory-hierarchy.html', 'https://spacesheep.dev/@yaroslavvb/et-soc1-memory-hierarchy'),
    'anatomy': ('Anatomy of a memory access', 'docs/reports/2026-09-19-et-soc1-memory-anatomy.html', 'https://spacesheep.dev/@yaroslavvb/et-soc1-memory-anatomy'),
    'noc': ('On-chip communication', 'docs/reports/2026-09-18-et-soc1-on-chip-communication.html', 'https://spacesheep.dev/@yaroslavvb/et-soc1-on-chip-communication'),
    'hotline': ('One hot line stops a shire', 'docs/reports/2026-09-22-hot-line.html', 'https://spacesheep.dev/@yaroslavvb/et-soc1-hot-line'),
    'relay': ('Hand it to the next shire: on-chip relay vs DRAM', 'docs/reports/2026-09-22-on-chip-relay.html', 'https://spacesheep.dev/@yaroslavvb/et-soc1-on-chip-relay'),
    'ridge': ('Ridge points', 'docs/reports/2026-09-18-et-soc1-ridge-points.html', 'https://spacesheep.dev/@yaroslavvb/et-soc1-ridge-points'),
    'matmul': ('Matmul efficiency', 'docs/reports/2026-09-18-et-soc1-matmul-efficiency.html', 'https://spacesheep.dev/@yaroslavvb/et-soc1-matmul-efficiency'),
    'dvfs': ('The DVFS loop and its leakage', 'docs/reports/2026-09-22-dvfs-leakage.html', 'https://spacesheep.dev/@yaroslavvb/et-soc1-dvfs-leakage'),
    'power': ('Power and temperature telemetry', 'docs/reports/2026-09-20-et-soc1-power-temperature.html', 'https://spacesheep.dev/@yaroslavvb/et-soc1-power-temperature'),
    'horace': ('The Horace experiment', 'docs/reports/2026-09-20-horace-experiment.html', 'https://spacesheep.dev/@yaroslavvb/et-soc1-horace-experiment'),
    'why': ('Why is it low power?', 'docs/reports/2026-09-21-why-low-power.html', 'https://spacesheep.dev/@yaroslavvb/et-soc1-why-low-power'),
    'wire': ('Heat per millimetre', 'docs/reports/2026-09-24-heat-per-mm.html', 'https://spacesheep.dev/@yaroslavvb/et-soc1-heat-per-mm'),
    'spatial': ('Spatial temperature: a brief', 'docs/reports/2026-09-22-et-soc1-spatial-temperature-brief.html', 'https://spacesheep.dev/@yaroslavvb/et-soc1-spatial-temperature-brief'),
    'hub': ('Limits of observability (the reports hub)', 'docs/reports/2026-09-20-et-soc1-limits-of-observability.html', 'https://spacesheep.dev/@yaroslavvb/et-soc1-limits-of-observability'),
}

CARDS3 = 'aifoundry2, aifoundry3, aifoundry1-c1'
FACTS = []

def F(id, component, topic, statement, value, unit, source, kind, card=None, note=None, page=None):
    assert kind in ('spec', 'measured', 'derived', 'inferred'), kind
    if kind == 'measured':
        assert card, id
    p = PAGES[page] if page else (None, None, None)
    FACTS.append({
        'id': id, 'component': component, 'topic': topic, 'statement': statement,
        'value': value, 'unit': unit, 'source': source, 'kind': kind,
        'card': card, 'note': note,
        'page': p[0], 'page_file': p[1], 'url': p[2],
    })

def near(a, b, tol):
    assert abs(a - b) <= tol, (a, b)
    return a

def r(x, n):
    return round(x, n)

# --------------------------------------------------------------------------------------------------
# Clock, voltage and the operating point
# --------------------------------------------------------------------------------------------------
ops = {o['mhz']: o['volts'] for o in MAN['rest']['operating_points']}
F('op-600', 'clock and voltage', 'operating point',
  'Base operating point: minion clock 600 MHz at 0.517 V on die (median while a kernel runs, aifoundry2). A warm card is held here by the governor; every table in the reports is at this point.',
  600, 'MHz', 'docs/reports/data/2026-09-23-energy-manual/manual.json: rest.operating_points[0] (mhz 600, volts 0.517); ' + mdline('docs/energy-manual/01-at-rest.md', '| 600 | 0.517'),
  'measured', 'aifoundry2', 'Minion rail voltage at 600 MHz by card: 518 mV (aifoundry2), 522-523 mV (aifoundry3), 499 mV (aifoundry1-c1) (manual.json catalogue.rail_mv; 01-at-rest.md "The three cards").', 'energy')
F('op-700', 'clock and voltage', 'operating point',
  'Second operating point: 700 MHz at 0.568 V, reached only from a cool start on aifoundry2 (V^2 f: 1.41x the 600 MHz switching power).',
  700, 'MHz', 'manual.json: rest.operating_points[1] (volts 0.568); ' + mdline('docs/energy-manual/01-at-rest.md', '| 700 | 0.568'),
  'measured', 'aifoundry2', 'aifoundry3 never leaves 600 MHz (TDP 0 W set by a boot service); aifoundry1-c1 sat at 600 MHz in every sample of the version-3 check.', 'dvfs')
F('op-800', 'clock and voltage', 'operating point',
  'Top operating point: 800 MHz at 0.618 V, reached only below about 68 C die on aifoundry2 (V^2 f: 1.91x the 600 MHz switching power).',
  800, 'MHz', 'manual.json: rest.operating_points[2] (volts 0.618); ' + mdline('docs/energy-manual/01-at-rest.md', '| 800 | 0.618'),
  'measured', 'aifoundry2', 'The 0.52 / 0.57 / 0.62 V shorthand in the text rounds 0.517 / 0.568 / 0.618.', 'dvfs')
assert ops == {600: 0.517, 700: 0.568, 800: 0.618}
F('op-800-peak', 'board power', 'power',
  'Peak board power at 800 MHz on random data: 87.8 W, for an instant before the governor stepped down (cold start).',
  87.8, 'W', cl('Peak board power at 800 MHz on random data'), 'measured', 'aifoundry2', 'E10, DATA/vf.json randn800_peak.', 'dvfs')
F('op-800-tflops', 'tensor unit', 'rate',
  'On a cool die (62-63 C) a zeros matmul reached 11.38 and 11.81 TFLOPS, spending 5-6 s of a 7 s run at 800 MHz; random data only 9.29-9.33 TFLOPS (under 0.3 s at 800 MHz).',
  11.81, 'TFLOP/s', cl('Zeros from a 62–63 °C die'), 'measured', 'aifoundry2', 'The data sets the power, and the power the clock: about a 25% speed gap zeros vs random (E10).', 'horace')
F('clk-noc', 'mesh (NoC)', 'clock',
  'The mesh network-on-chip runs at 400 MHz; minion clock 600 MHz; LPDDR4X at a 933 MHz DDR clock (3,733 MT/s).',
  400, 'MHz', 'docs/reports/2026-09-19-et-soc1-memory-anatomy.html header ("minion clock 600 MHz, NoC 400 MHz, LPDDR4X at 3,733 MT/s"); ridge-data noc_mhz 400',
  'spec', None, 'The 933 MHz DDR clock is read from card telemetry / SP firmware mem_controller.c (ridge-data levels[dram].spec.src); 3,733 MT/s assumes the 1066:4266 ratio.', 'anatomy')
rv = MAN['catalogue']['rail_mv']
F('rail-mesh-v', 'mesh (NoC)', 'voltage',
  'Mesh (NoC) rail at 484-486 mV on die, the same on all three cards (0.485 V is the voltage Heat per millimetre scales from).',
  rv['aifoundry2']['noc'], 'mV', 'manual.json: catalogue.rail_mv.<card>.noc (a2 484, a3 484, a1c1 486); docs/reports/data/2026-09-24-wire-energy/report.json inputs (noc 0.485 V)',
  'measured', CARDS3, None, 'wire')
F('rail-sram-v', 'L2 cache', 'voltage',
  'SRAM rail (L2, L3, scratchpad arrays) at 704 mV on aifoundry2, 698 mV on aifoundry3, 751 mV on aifoundry1-c1.',
  rv['aifoundry2']['sram'], 'mV', 'manual.json: catalogue.rail_mv.<card>.sram; ' + mdline('docs/energy-manual/08-cards.md', 'Minion and SRAM rail voltage'),
  'measured', CARDS3, 'By V^2 alone aifoundry1-c1 SRAM accesses would cost 14% more (08-cards.md).', 'energy')

# --------------------------------------------------------------------------------------------------
# Latency (load-to-use, cycles at 600 MHz)
# --------------------------------------------------------------------------------------------------
m1 = {c: v['passes'][0] for c, v in [(x['item'], x) for x in LAT['items']][0][1]['per_card'].items()} if False else None
lat_items = {x['item']: x for x in LAT['items']}
l1s = [p['L1'] for c in lat_items['LAT-M1']['per_card'].values() for p in c['passes']]
F('lat-l1', 'L1 data cache', 'latency',
  'L1 data cache hit: 5.25 cycles load-to-use (8.8 ns at 600 MHz); the same on three cards (per-pass ranges 5.247-5.259).',
  5.25, 'cycles', 'docs/reports/data/2026-09-25-claims-v3/results/lat.json: items[LAT-M1].per_card.<card>.passes[].L1; ' + cl('Load-to-use latency, L1 / read buffer / L2 and local scratchpad; hart 1'),
  'measured', CARDS3, 'Only 512 B of L1 per hart: the firmware puts the L1 in scratchpad mode before every launch.', 'memhier')
F('lat-rb', 'L2 read buffer', 'latency',
  'L2 read buffer (8 clean lines per bank x 4 banks = 2 KB per shire): 36 cycles (60 ns), 11 fewer than the L2 array.',
  36.0, 'cycles', 'lat.json: items[LAT-M1].per_card.<card>.passes[].RB (35.998-36.006); ' + cl('Load-to-use latency, L1 / read buffer / L2 and local scratchpad; hart 1'),
  'measured', CARDS3, 'Spec: 10 vs 21 shire cycles (CORE-ET Shire Cache Specification), per the memory-hierarchy page.', 'memhier')
F('lat-l2', 'L2 cache', 'latency',
  'L2 cache hit (and the shire\'s own scratchpad): 47 cycles (78 ns); hart 1 pays 3 more (39 read buffer, 50 L2).',
  47.0, 'cycles', 'lat.json: items[LAT-M1].per_card.<card>.passes[].L2 (46.998-47.024), .hart1; ' + cl('Load-to-use latency, L1 / read buffer / L2 and local scratchpad; hart 1'),
  'measured', CARDS3, 'The single-load ladder of Anatomy reads L2 at 49 cycles in every pass (a different probe and offset).', 'memhier')
F('lat-scp-own', 'scratchpad (own shire)', 'latency',
  'The shire\'s own L2 scratchpad: 47 cycles (78 ns), the same SRAM, latency and bandwidth as the L2 cache.',
  47.0, 'cycles', cl('Load-to-use latency, L1 / L2 read buffer / L2 and local scratchpad'), 'measured', CARDS3,
  'Re-measured on three cards 26 Sep (E36).', 'memhier')
F('lat-scp-remote', 'scratchpad (other shire)', 'latency',
  'Another shire\'s scratchpad: 99.84 + 12.00 cycles per mesh hop at 600 MHz (112-220 cycles, 186-366 ns over 1-10 hops); all 124 points within 1 cycle, a->b equals b->a within 0.032 cycles.',
  99.84, 'cycles + 12.00 cycles/hop', 'lat.json: items[LAT-M3].per_card.<card>.passes[] (row0_slope 11.998-12.002, frac_within_1 1.0); ' + cl('Another shire\'s scratchpad | 99.84'),
  'measured', CARDS3, 'Clock model (aifoundry2, 18 Sep): 66 minion cycles + 56 ns + 20 ns per hop.', 'memhier')
F('lat-l3-hop', 'L3', 'latency',
  'L3 hit against distance to the line\'s home shire: 110.5 + 11.99 cycles per mesh hop (from shire 0), within 4 cycles for 99.4-100% of lines on each card.',
  110.5, 'cycles + 11.99 cycles/hop', 'docs/reports/data/2026-09-25-claims-v3/results/mem.json: [item=MEM-P1].per_card.<card>.tests.P1_l3_slope / P1_l3_intercept; ' + cl('L3 hit latency against mesh hops'),
  'measured', CARDS3, 'A local L3 hit is ~110 cycles: ~48 for the L1 and L2 lookup and miss, ~62 for the home slice (Anatomy, inferred). 31 of 32 L3 lines live in another shire.', 'anatomy')
l3 = {c: v['passes'][0]['L3'] for c, v in lat_items['LAT-M2']['per_card'].items()}
F('lat-l3-avg', 'L3', 'latency',
  'L3 hit from a pointer chase, averaged over all 32 slices: 159-169 cycles at 600 MHz (265-282 ns), by requesting shire: 168.8-168.9 (shire 0), 160.6-160.7 (7), 159.1-159.2 (24), 168.8-168.9 (31).',
  near(l3['aifoundry2']['24'], 159.1, 0.1), 'cycles', 'lat.json: items[LAT-M2].per_card.<card>.passes[].L3; ' + cl('L3 and DRAM latency by requesting shire'),
  'measured', CARDS3, 'The value field is the fastest requester (shire 24). Clock model: 72 cycles + 61 ns + 20 ns per hop.', 'memhier')
F('lat-dram', 'DRAM (LPDDR4X, memory shires)', 'latency',
  'DRAM load from a pointer chase: 287-297 cycles at 600 MHz (479-495 ns): 296.6-297.1 from shires 0 and 31, 287.2-288.8 from 7 and 24; about 490 ns, a fifth more than an A100\'s HBM (405 ns).',
  297.0, 'cycles', 'lat.json: items[LAT-M2].per_card.<card>.passes[].DRAM; ' + cl('L3 and DRAM latency by requesting shire'),
  'measured', CARDS3, 'The value field is the slowest requesters (shires 0 and 31). At 800 MHz (aifoundry2 only) 352-368 cycles, 440-460 ns: the mesh and DDR parts do not scale with the minion clock.', 'memhier')
F('lat-dram-typical', 'DRAM (LPDDR4X, memory shires)', 'latency',
  'A typical DRAM load, timed one at a time: 299 cycles (500 ns), the median of 4,500 loads from shire 0 to random lines; 299 in each of 15 passes on three cards.',
  299, 'cycles', 'docs/reports/2026-09-19-et-soc1-memory-anatomy.html, headline tile "A DRAM load, typical"',
  'measured', CARDS3, None, 'anatomy')
F('lat-dram-model', 'DRAM (LPDDR4X, memory shires)', 'latency',
  'DRAM latency model: 110 + 12 x hops(requester -> L3 home) + 91 + 12 x hops(L3 home -> memory shire) cycles; within 3 cycles for 97% (a2), 93% (a3), 94% (a1c1) of lines, left as fitted on 19 Sep.',
  91, 'cycles (memory-shire leg constant)', 'mem.json: [item=MEM-P2].per_card.<card>.tests.P2_dram_within3_frac; ' + cl('DRAM latency against the 19 September model'),
  'derived', CARDS3, 'Fitted on aifoundry2 (one constant plus eight memory-shire positions); PA bits 10:6 pick the L3 home, bits 8:6 the memory shire.', 'anatomy')
F('lat-dram-chip', 'DRAM (LPDDR4X, memory shires)', 'latency',
  'Of a DRAM load\'s ~300 cycles only about 25-28 are the DRAM chip\'s own timing (activate tRCD 18 ns, 19.3 ns read latency, one or two 4.3 ns bursts); the rest is paths on the chip.',
  28, 'cycles', 'docs/reports/2026-09-19-et-soc1-memory-anatomy.html section 4 ("Of the 91 cycles (152 ns), the DRAM chip itself accounts for about 25-28")',
  'inferred', None, 'From the controller\'s timing registers set against the fit; the memory shire (queue, PHY, clock crossings) is at most ~63-66 cycles.', 'anatomy')
F('lat-dram-refresh', 'DRAM (LPDDR4X, memory shires)', 'latency',
  'LPDDR4X refresh every 2,325 cycles (3.88 us) on every card; a load that meets it waits up to 208 extra cycles (347 ns).',
  208, 'cycles', 'mem.json: [item=MEM-P5].per_card.<card>.tests.P5_refresh_period, .P5_max_extra; ' + cl('DRAM refresh and open rows'),
  'measured', CARDS3, None, 'anatomy')
F('lat-dram-rowconflict', 'DRAM (LPDDR4X, memory shires)', 'latency',
  'Two loads to the same bank but different rows, issued together: the second pays about +37 cycles (a2 36.9, a3 37.4, a1c1 36.5); bank = PA[12:10].',
  36.9, 'cycles', 'mem.json: [item=MEM-P4].per_card.<card>.tests.P4_row_conflict_extra; ' + cl('DRAM bank timing (bits)'),
  'measured', CARDS3, None, 'anatomy')
F('lat-wake', 'L2 cache', 'latency',
  'No cache level wakes up slower after idle: no shift of 5 cycles or more at any level after 16M idle cycles, on every card (no array power gating seen).',
  0, 'cycles', cl('No cache level wakes up after idle (the E18 probe)'), 'measured', CARDS3, None, 'dvfs')

# --------------------------------------------------------------------------------------------------
# Bandwidth (per minion-cycle and chip-wide, 600 MHz, 1,024 minions)
# --------------------------------------------------------------------------------------------------
lv = {L['key']: L for L in RIDGE['levels']}
F('bw-l1', 'L1 data cache', 'bandwidth',
  'L1 hits, 32 B vector loads by both harts: 14.5 TB/s chip-wide (23.6 B per minion-cycle) in the energy manual\'s unrolled loop; the memory-hierarchy probe\'s loop reaches 6.2 TB/s (10 B per minion-cycle). Spec: 32 B per cycle.',
  r(lv['l1d']['demonstrated']['gbps'] / 1000, 2), 'TB/s', 'docs/reports/2026-09-18-et-soc1-ridge-points.html ridge-data: levels[l1d].demonstrated (bpc 23.57, gbps 14,480; by card 14,474-14,488), .measured (bpc 10.04, gbps_600 6,211), .spec.bpc 32',
  'measured', CARDS3, 'The 6.2 TB/s figure is aifoundry2 and aifoundry3 (rerun passes); the 14.5 TB/s catalogue figure is on all three cards.', 'ridge')
near(lv['l1d']['demonstrated']['bpc'], 23.57, 0.01)
F('bw-l2', 'L2 cache', 'bandwidth',
  'L2 cache, 1 KB tensor loads by every minion: 2.45 TB/s chip-wide, 4.0 B per minion-cycle (128 B per shire-cycle), half the four banks\' 256 B per shire-cycle spec.',
  r(lv['l2']['measured']['gbps'] / 1000, 2), 'TB/s', 'ridge-data: levels[l2].measured (bpc 3.999, gbps 2,452), .spec.bpc 8.0; ' + cl('Bandwidth at 600 MHz, 1,024 minions'),
  'measured', 'aifoundry2, aifoundry3', 'A lone minion reads 6.4 B per cycle from L2 or scratchpad on all three cards (ridge points, three-card check).', 'ridge')
F('bw-scp-own', 'scratchpad (own shire)', 'bandwidth',
  'Own-shire scratchpad: 2.46 TB/s chip-wide, 4.0 B per minion-cycle, same as the L2. Tensor stores into it reach 1.23 TB/s (half the read rate).',
  r(lv['scp']['measured']['gbps'] / 1000, 2), 'TB/s', 'ridge-data: levels[scp].measured (bpc 4.000, gbps 2,456); limits.write_gbps.tstore_scp (1,230 on each card)',
  'measured', CARDS3, 'Read rate on aifoundry2 and aifoundry3 (rerun passes); the store rate on all three cards.', 'ridge')
F('bw-l3', 'L3', 'bandwidth',
  'L3, every minion streaming: 0.98 TB/s chip-wide, 1.6 B per minion-cycle; spec (assumed one 64 B beat per NoC cycle per shire port) 3.3 TB/s, 5.33 B per minion-cycle.',
  r(lv['l3']['measured']['gbps'] / 1000, 2), 'TB/s', 'ridge-data: levels[l3].measured (bpc 1.599, gbps 982.7), .spec (bpc 5.33, gbps 3,276.8, assumed)',
  'measured', 'aifoundry2, aifoundry3', None, 'ridge')
F('bw-scp-remote', 'scratchpad (other shire)', 'bandwidth',
  'Another shire\'s scratchpad (each shire reading the one 16 IDs away, 2.1 hops on average): 0.96 TB/s chip-wide, 1.56 B per minion-cycle.',
  r(lv['scp_remote']['measured']['gbps'] / 1000, 2), 'TB/s', 'ridge-data: levels[scp_remote].measured (bpc 1.562, gbps 959.5)',
  'measured', 'aifoundry2, aifoundry3', 'If many shires read one shire\'s scratchpad its four mesh ports would allow only about 0.1 TB/s (ridge points, inferred).', 'ridge')
F('bw-dram', 'DRAM (LPDDR4X, memory shires)', 'bandwidth',
  'DRAM streaming: 76 GB/s for the whole chip (0.124 B per minion-cycle), about 64% of the 119 GB/s that 16 x 16-bit channels carry at 3,733 MT/s; about a twentieth of an A100.',
  r(lv['dram']['measured']['gbps'], 1), 'GB/s', 'ridge-data: levels[dram].measured (bpc 0.1235, gbps 75.9), .spec (gbps 119.5; datasheet max 136.5); ' + cl('Bandwidth at 600 MHz, 1,024 minions'),
  'measured', 'aifoundry2, aifoundry3', 'Tensor stores to DRAM also 76 GB/s on all three cards; stores through the L1 only 27 GB/s (ridge-data limits.write_gbps). The runtime\'s 128,000 MB/s is a firmware placeholder constant.', 'ridge')
F('bw-dram-lone', 'DRAM (LPDDR4X, memory shires)', 'bandwidth',
  'A lone minion streams 1.4 B per cycle from DRAM, so at least about 93 minions streaming 1 KB loads at once are needed to reach the chip\'s 76 GB/s.',
  93, 'minions', 'docs/reports/2026-09-18-et-soc1-ridge-points.html text, "A lone minion" paragraph',
  'derived', None, 'The lone-minion DRAM rate depends on the kernel (0.91 B/cycle in the catalogue loop: at least ~140 minions).', 'ridge')
F('bw-pcie', 'chip', 'bandwidth',
  'Host link: PCIe Gen4 x8, 15.75 GB/s per direction before protocol overhead; host transfers have not been timed on these cards.',
  15.75, 'GB/s', 'ridge-data: levels[pcie].spec (ET Preliminary Datasheet sec. 1)',
  'spec', None, 'Never measured (05-claims ridge row kind A).', 'ridge')
F('bw-tsend-fln', 'tensor network (TensorSend)', 'bandwidth',
  'TensorSend on the neighbourhood fast local network (pairs on tree edges), every minion sending 1 KB messages: 2,992 GB/s chip-wide, 4.9 B per minion-cycle.',
  r(lv['fln']['measured']['gbps'], 0), 'GB/s', 'ridge-data: levels[fln].measured (bpc 4.87, gbps 2,991.7); docs/energy-manual/05-bytes-between-cores.md ring table (pair)',
  'measured', 'aifoundry2', 'Rates are one session on aifoundry2 (18 Sep); the energies below are three cards.', 'noc')
F('bw-tsend-shire', 'tensor network (TensorSend)', 'bandwidth',
  'TensorSend around rings of 8 or 32 minions inside a shire: 1,120 GB/s chip-wide (1.8 B per minion-cycle).',
  r(lv['xbar']['measured']['gbps'], 0), 'GB/s', 'ridge-data: levels[xbar].measured (bpc 1.82, gbps 1,120.2)',
  'measured', 'aifoundry2', None, 'noc')
F('bw-tsend-mesh', 'tensor network (TensorSend)', 'bandwidth',
  'TensorSend between shires: 87-156 GB/s chip-wide over six shire-to-shire ring patterns (0.25 B per minion-cycle at best): 7-34x less message bandwidth than inside a shire.',
  r(lv['xmesh']['measured']['gbps'], 0), 'GB/s', 'ridge-data: levels[xmesh].measured (gbps 156.0); docs/energy-manual/05-bytes-between-cores.md ring table (87-156 GB/s)',
  'measured', 'aifoundry2', 'Limited by how many packets a sender keeps in flight (3-5 GB/s per shire).', 'noc')
F('bw-tsend-link', 'tensor network (TensorSend)', 'bandwidth',
  'One TensorSend link, 1 KB messages: 5.3 GB/s on the fast local network, 2.9 through the shire crossbar, 2.7 over one mesh hop, 1.8 over 10 hops (the three cards agree to the digits).',
  5.3, 'GB/s', 'docs/reports/2026-09-18-et-soc1-on-chip-communication.html, "Message size and bandwidth" table',
  'measured', CARDS3, None, 'noc')

# --------------------------------------------------------------------------------------------------
# Energy per byte by level (energy manual section 4, the version-3 reruns on three cards)
# --------------------------------------------------------------------------------------------------
lev = MAN['reruns']['levels_pj_per_byte']
bycont = MAN['reruns']['levels_by_contents_pj_per_byte']
def pcs(d, nd=2):
    pc = d['per_card']
    return 'a2 %.*f, a3 %.*f, a1c1 %.*f' % (nd, pc['aifoundry2']['mean'], nd, pc['aifoundry3']['mean'], nd, pc['aifoundry1-c1']['mean'])
def lvfact(id, comp, key, label, nd=2, d=None, src=None, note=None):
    d = d or lev[key]
    F(id, comp, 'energy per byte',
      f'{label}: {d["mean"]:.{nd}f} pJ/B [{d["lo"]:.{nd}f}-{d["hi"]:.{nd}f}] above idle, 1 KB tensor loads (L1: 32 B vector loads) by every minion at 600 MHz; per card {pcs(d, nd)}.',
      r(d['mean'], nd), 'pJ/B', src or f'docs/reports/data/2026-09-23-energy-manual/manual.json: reruns.levels_pj_per_byte["{key}"] (mean, lo, hi, per_card); docs/energy-manual/04-bytes-memory.md table 4.2',
      'measured', CARDS3, note, 'energy')
lvfact('e-l1', 'L1 data cache', 'l1', 'L1 hit (memhier loop)', 2,
       note='The manual recommends the catalogue\'s L1 row instead: flw.ps 0.54 pJ/B [0.52-0.56] random, 0.39 zeros (4.1). Brackets are the range over 18 passes (6 per card).')
lvfact('e-l2', 'L2 cache', 'l2', 'L2 cache', 2, note='Contents not set; moves a lot pass to pass (1.42-4.99).')
lvfact('e-l3', 'L3', 'l3', 'L3 (over the mesh)', 1, note='Contents not set; 7.1-20.5 pJ/B pass to pass.')
lvfact('e-dram', 'DRAM (LPDDR4X, memory shires)', 'dram', 'DRAM', 1,
       note='About 70% of a DRAM byte\'s energy lands on no metered rail (DDR PHY, I/O, the DRAM chips); the E30 fit puts ~73 pJ/B of it off-rail.')
lvfact('e-scp-own-zeros', 'scratchpad (own shire)', None, 'Own scratchpad filled with zeros', 2, d=bycont['zeros']['scp-local'],
       src='manual.json: reruns.levels_by_contents_pj_per_byte.zeros["scp-local"]; docs/energy-manual/04-bytes-memory.md table 4.2')
lvfact('e-scp-own-rand', 'scratchpad (own shire)', None, 'Own scratchpad filled with random data', 2, d=bycont['random']['scp-local'],
       src='manual.json: reruns.levels_by_contents_pj_per_byte.random["scp-local"]; docs/energy-manual/04-bytes-memory.md table 4.2',
       note='The only level where cards differ beyond noise: aifoundry1-c1 reads above the registered band (5.03 vs 3.7-4.7).')
lvfact('e-scp-remote-zeros', 'scratchpad (other shire)', None, 'Scratchpad 16 shire IDs away (2.1 hops mean) filled with zeros', 2, d=bycont['zeros']['scp-remote'],
       src='manual.json: reruns.levels_by_contents_pj_per_byte.zeros["scp-remote"]; docs/energy-manual/04-bytes-memory.md table 4.2')
lvfact('e-scp-remote-rand', 'scratchpad (other shire)', None, 'Scratchpad 16 shire IDs away (2.1 hops mean) filled with random data', 1, d=bycont['random']['scp-remote'],
       src='manual.json: reruns.levels_by_contents_pj_per_byte.random["scp-remote"]; docs/energy-manual/04-bytes-memory.md table 4.2')
near(lev['dram']['mean'], 114.6, 0.05); near(lev['l3']['mean'], 14.73, 0.01); near(bycont['random']['scp-remote']['mean'], 11.83, 0.01)
F('e-dram-tload', 'DRAM (LPDDR4X, memory shires)', 'energy per byte',
  'Tensor load from DRAM (catalogue, both data sets): 94.6 pJ/B [86.2-105.7] on zeros, 132.6 [117.9-145.4] on random data; tensor store to DRAM 94.4 / 141.9. Even DRAM is data-dependent.',
  132.6, 'pJ/B', mdline('docs/energy-manual/04-bytes-memory.md', '| Tensor load from DRAM |') + '; manual.json catalogue.combined (tload/dram)',
  'measured', CARDS3, 'Per card, random: a2 134.8, a3 127.3, a1c1 135.8 pJ/B.', 'energy')
F('e-dram-writeback', 'DRAM (LPDDR4X, memory shires)', 'energy per byte',
  'Stores to DRAM through the L1 write-back path (fsw.ps): 341.5 pJ/B [317.4-373.3] on random data, 2.4x a tensor store, at 27 GB/s: each store allocates its line, so the byte pays a read and a write.',
  341.5, 'pJ/B', mdline('docs/energy-manual/04-bytes-memory.md', 'stores to DRAM through the L1'),
  'measured', CARDS3, None, 'energy')
F('e-scp-tload', 'scratchpad (own shire)', 'energy per byte',
  'Tensor load from the own scratchpad (catalogue): 2.12 pJ/B on zeros, 4.43 on random data; tensor store into it 4.65 / 8.58: a scratchpad write is twice a read.',
  4.43, 'pJ/B', mdline('docs/energy-manual/04-bytes-memory.md', '| Tensor load from the shire'),
  'measured', CARDS3, None, 'energy')
F('e-l1-cat', 'L1 data cache', 'energy per byte',
  'L1 hit, flw.ps 32 B by both harts: 0.54 pJ/B [0.52-0.56] on random data, 0.39 on zeros, including the instruction: an L1 hit is nearly free.',
  0.54, 'pJ/B', mdline('docs/energy-manual/04-bytes-memory.md', '| L1 hit, `flw.ps`'),
  'measured', CARDS3, None, 'energy')
F('e-dram-vs-scp', 'DRAM (LPDDR4X, memory shires)', 'energy per byte',
  'DRAM is 30x the energy of the shire\'s own scratchpad per byte read, and 17x per byte written.',
  30, 'x', mdline('docs/energy-manual/04-bytes-memory.md', 'DRAM is 30× the energy'),
  'derived', CARDS3, 'Ratio of the catalogue rows above (random data).', 'energy')
F('e-l1-fill', 'L1 data cache', 'energy',
  'Filling one 64 B line from the scratchpad into the L1: 101 pJ on zeros, 238 pJ on random data (1.6 and 3.7 pJ per byte of line).',
  238, 'pJ per line', mdline('docs/energy-manual/04a-fine-grain.md', 'Twice the difference between the stride-64'),
  'derived', CARDS3, 'Difference of catalogue strides (stride64 - stride32) x 2; per card random a2 221, a3 223, a1c1 271 pJ.', 'energy')

# --------------------------------------------------------------------------------------------------
# Instructions: energy per op (energy manual section 3, catalogue on three cards)
# --------------------------------------------------------------------------------------------------
I3 = 'docs/energy-manual/03-instructions.md'
F('e-add', 'minion', 'energy per instruction',
  'Integer add: 6.2 pJ [5.6-6.9] on zeros, 9.7 [9.3-10.3] on random operands, both harts of 1,024 minions flat out (little more than a nop, 5.1 pJ).',
  9.7, 'pJ/instruction', mdline(I3, '| `add` |'), 'measured', CARDS3, None, 'energy')
F('e-fadd', 'minion', 'energy per instruction',
  'Scalar float add fadd.s: 23.7 pJ [22.0-24.5] on zeros, 26.3 [24.1-27.0] on random data: 3.8x an integer add even on zeros (the FPU does not gate on zero).',
  26.3, 'pJ/instruction', mdline(I3, '| `fadd.s` |'), 'measured', CARDS3, None, 'energy')
F('e-fmadd-ps', 'vector unit', 'energy per instruction',
  '8-lane vector multiply-add fmadd.ps: 27.1 pJ [26.4-28.9] on zeros, 55.8 [53.8-57.0] on random data, 7.0 pJ per lane-MAC (6.3-6.4 with the instruction issue taken out); 16 flops.',
  55.8, 'pJ/instruction', mdline(I3, '| `fmadd.ps (8 lanes)` |'), 'measured', CARDS3,
  'Per card random: a2 55.6, a3 56.2, a1c1 55.4. The vector lane is ~10% above the tensor unit\'s 5.8 pJ per multiply-add.', 'energy')
F('e-fadd-ps', 'vector unit', 'energy per instruction',
  '8-lane vector add fadd.ps: 22.4 pJ on zeros (same as the scalar op: lanes on zeros add nothing), 41.1 on random data (5.1 per lane).',
  41.1, 'pJ/instruction', mdline(I3, '| `fadd.ps (8 lanes)` |'), 'measured', CARDS3, None, 'energy')
F('e-fexp-ps', 'vector unit', 'energy per instruction',
  'Transcendental fexp.ps (8 lanes): 155.4 pJ [147.3-162.4] on random data at a quarter the issue rate; flog.ps 218 pJ. No hardware divide or square root: they trap.',
  155.4, 'pJ/instruction', mdline(I3, '| `fexp.ps (8 lanes)` |'), 'measured', CARDS3, None, 'energy')
F('e-nop', 'minion', 'energy per instruction',
  'The awake core\'s issue floor: a nop costs 5.1 pJ [4.8-5.7] and a fence 4.4 [4.0-4.8] per instruction with both harts.',
  5.1, 'pJ/instruction', mdline('docs/energy-manual/02-awake.md', 'The addi loop is not the floor'), 'measured', CARDS3, None, 'energy')
F('e-awake', 'minion', 'power',
  'An awake minion (addi loop) costs about 2 mW (1.87 mW one hart, 3.02 mW both harts, aifoundry2); 5.1 / 6.6 pJ per instruction pooled over three cards.',
  1.87, 'mW per minion', mdline('docs/energy-manual/02-awake.md', '| One hart per minion, `addi` loop |'), 'measured', CARDS3,
  'Keeping 1,024 minions awake for a second is 2-3.1 J, against 36 J for the card at 80 C.', 'energy')
F('e-stalled', 'minion', 'power',
  'A minion stalled on a contended atomic draws about 1.2 mW (1,024 stalled: 1.19 W [1.01-1.41] over idle), less than a spinning one (1.9 mW): waiting is cheap.',
  1.19, 'W over idle (1,024 minions)', 'manual.json: reruns.hotline_over_idle_w.contended; ' + mdline('docs/energy-manual/02-awake.md', '1,024 minions stalled on one contended atomic'),
  'measured', 'aifoundry2, aifoundry3', None, 'energy')
F('e-amo-dearest', 'minion', 'energy per instruction',
  'Cheapest and dearest instruction in the 161 that execute in U-mode: fence 4.6 pJ, amoaddg.d 1,486 pJ (aifoundry2, 23 Sep catalogue); atomics span 351-1,450 pJ in the three-card catalogue.',
  1486, 'pJ/instruction', cl('Cheapest and dearest instruction') + '; ' + mdline(I3, 'atomics (351–1,450 pJ)'),
  'measured', 'aifoundry2', 'The 1,486 figure is the 23 Sep edition on aifoundry2; the three-card manual text gives the 351-1,450 range.', 'energy')

# Tensor unit (energy manual 3.2, version-3 ablation on three cards)
tb = MAN['tensor']['bars']
def tfact(id, key, label, nd=3, note=None):
    d = tb[key]
    F(id, 'tensor unit', 'energy per MAC',
      f'TensorFMA {label}: {d["mean"]:.{nd}f} pJ per multiply-add [{d["lo"]:.{nd}f}-{d["hi"]:.{nd}f}] above idle, all 1,024 minions; per card {pcs(d, nd)}.',
      r(d['mean'], nd), 'pJ/MAC', f'manual.json: tensor.bars.{key} (mean, lo, hi, per_card); ' + mdline(I3, '| TensorFMA ' + label.replace(' random', ', randn').replace(' zeros', ', zeros').replace(' ones', ', ones') + ' |'),
      'measured', CARDS3, note, 'energy')
tfact('e-tfma-fp32', 'fp32_randn', 'fp32 random', note='Loaded (idle included, aifoundry2 at 80 C): 13.84 pJ per MAC. 546 cycles per 16x16x16 op. Launched at 80 C (a3 at 57 C); amendment C2 offset applies.')
tfact('e-tfma-fp32-zeros', 'fp32_zeros', 'fp32 zeros', note='Zeros clock nothing: the lane clock is withheld when an operand word is zero.')
tfact('e-tfma-fp16', 'fp16_randn', 'fp16 random')
tfact('e-tfma-int8', 'int8_randn', 'int8 random', note='int8 is about 19x cheaper per MAC than fp32 (E38: 18.9-20.5 by card). 318 cycles per 16x16x64 op.')
near(tb['fp32_randn']['mean'], 5.782, 0.001); near(tb['int8_randn']['mean'], 0.295, 0.001)
F('e-tfma-flop', 'tensor unit', 'energy per FLOP',
  'Dense fp32 matmul per FLOP: 6.9 pJ loaded (63.6 W over 9.18 TFLOP/s, aifoundry2 at 80 C) and 2.89 pJ marginal [2.67-3.07 over runs and cards].',
  2.89, 'pJ/FLOP', mdline('docs/energy-manual/07-composition.md', 'Per flop, the measurement is') + '; ridge-data energy.e_flop.fp32 (2.891)',
  'measured', CARDS3, None, 'energy')
F('e-flip-model', 'tensor unit', 'energy',
  'Tensor unit energy by RTL event (fitted on aifoundry2): 3.18 fJ per register bit clocked, 0.025 per multiplier-tree net toggle, 0.80 per other net toggle, 15.5 per operand-word bit; 1.8 mW per minion of state machines. A random tile prices at 27.2 W on 1,024 minions.',
  3.18, 'fJ per register bit clocked', 'manual.json: tensor.flips.e_fJ (ffclk 3.179, mult 0.025, rest 0.801, bus 15.54), .p_sm_full_chip_w 1.85',
  'derived', 'aifoundry2', 'A fit (E17); 14 structured matrices predicted to 0.9 W rms before they ran.', 'horace')

# --------------------------------------------------------------------------------------------------
# Matmul throughput and board power per card (E37 mmbench, and the Horace ablation)
# --------------------------------------------------------------------------------------------------
mmc = [x for x in MMB['items'] if x.get('item') == 'MMB-c'][0]['per_card']
F('mm-rate', 'tensor unit', 'rate',
  'Tensor matmul, tiles in L2, all 1,024 minions at 600 MHz: 9.51 TFLOP/s fp32, 19.02 fp16, 71.77 TOP/s int8, the same on each card (91-97% of the 9.83 / 19.66 / 78.6 peak); 529 cycles per fp32/fp16 op, 280.35 per int8 op.',
  9.51, 'TFLOP/s', 'docs/reports/data/2026-09-25-claims-v3/results/mmb.json: items[MMB-b].per_card.<card>.<mode>.tflops_pass_values; ' + cl('mmbench cycles per op and rate, three cards'),
  'measured', CARDS3, 'Every result bit-exact against a host reference.', 'matmul')
F('mm-peak', 'tensor unit', 'rate',
  'Tensor peak per minion-cycle: 16 fp32 / 32 fp16 / 128 int8 ops; 9.83 TFLOP/s, 19.7 TFLOP/s and 78.6 TOP/s on 1,024 minions at 600 MHz.',
  16, 'FLOP per minion-cycle (fp32)', 'ridge-data: peaks.<fp32|fp16|int8>.per_cycle, chip_600; ' + cl('Tensor peak per minion-cycle'),
  'spec', None, 'Minion VPU Specification sec. 2.', 'ridge')
for c, lab in [('aifoundry2', 'a2'), ('aifoundry3', 'a3'), ('aifoundry1-c1', 'a1c1')]:
    d = mmc[c]
    f32, i8, dr = d['fp32-tensor-L2'], d['int8-tensor-L2'], d['fp32-tensor-DRAM']
    F(f'mm-board-{lab}', 'board power', 'power',
      f'{c}: board power under the fp32 tensor matmul (tiles in L2) {f32["board_w"]:.1f} W against {f32["idle_before_w"]:.1f} W idle just before (die {f32["die_c_mean"]:.0f} C); {f32["mean"]:.1f} W above idle. int8: {i8["board_w"]:.1f} W; fp32 from DRAM: {dr["board_w"]:.1f} W.',
      r(f32['board_w'], 1), 'W', f'mmb.json: items[MMB-c].per_card.{c}.fp32-tensor-L2 (board_w, idle_before_w, mean, die_c_mean); ' + cl('mmbench board watts over idle'),
      'measured', c, 'Four passes; the matmul page\'s three-card table.', 'matmul')
F('mm-perw', 'tensor unit', 'efficiency',
  'Board GFLOP/s per W, L2 matmul fp32 / fp16 / int8: aifoundry2 161 / 316 / 1,172; aifoundry3 189 / 370 / 1,377; aifoundry1-c1 138 / 270 / 958 (each card at its own die temperature).',
  161, 'GFLOP/s per W (fp32, aifoundry2)', cl('Board GFLOP/s per W, L2 matmul'), 'measured', CARDS3,
  'Against the A100 spec sheet (peak / TDP) at full fp32 precision the card is 3.3x (a2), 3.9x (a3), 2.8x (a1c1) more energy-efficient on the benchmark\'s +-1/+-2 operands; the A100\'s int8 tensor cores lead by 1.13-1.63x.', 'matmul')
tr = MAN['tensor']['per_card_rows']
def bw(c, k):
    return tr[c][k]['idle_w'] + tr[c][k]['over_idle_w']
F('hor-board', 'board power', 'power',
  'The same fp32 TensorFMA draws 38 W on zeros, 47 on ones and 64 on random-normal values on aifoundry2 at 80 C; 51 / 60 / 78 W on aifoundry1-c1 at 80 C (idle 50 W); 27 / 35 / 50 W on aifoundry3 at 57-58 C: the data decides the dynamic power.',
  r(bw('aifoundry2', 'fp32_randn'), 1), 'W', 'manual.json: tensor.per_card_rows.<card>.<fp32_zeros|fp32_ones|fp32_randn> (idle_w + over_idle_w); docs/reports/2026-09-18-et-soc1-matmul-efficiency.html "Later measurements"',
  'derived', CARDS3, 'Board = the idle bracket plus the measured over-idle power, four runs per card (version-3 ablation); amendment C2 launch-temperature offset.', 'horace')
near(bw('aifoundry2', 'fp32_zeros'), 38.2, 0.1); near(bw('aifoundry1-c1', 'fp32_randn'), 77.9, 0.1); near(bw('aifoundry3', 'fp32_randn'), 50.4, 0.1)
F('hor-heat', 'die temperature', 'temperature',
  'At full load only zeros hold a steady temperature: random-normal data takes the die from 80 to 90 C in 19-26 s (four runs), ones in 107-167 s; zeros cool it to 76-78 C over 10 minutes.',
  19, 's (80 -> 90 C, random)', cl('Random normal, 1,024 minions | **19, 20, 20, 26 s**'), 'measured', 'aifoundry2', None, 'horace')

# --------------------------------------------------------------------------------------------------
# Idle, leakage and the rails
# --------------------------------------------------------------------------------------------------
rest = MAN['rest']
F('idle-law', 'idle and leakage', 'power',
  'Idle law (aifoundry2): P_idle(T) = 12.6 W + 23.3 W x e^((T - 80 C)/36 C): 35.9 W at 80 C, rising 0.65 W per degree there; predicted the idle 20.6 h later to +0.01 W.',
  r(rest['P_fix_w'] + rest['A_leak_80_w'], 1), 'W at 80 C', 'manual.json: rest.P_fix_w 12.63, A_leak_80_w 23.26, T_L_c 36, lambda_80_w_per_c 0.646; ' + mdline('docs/energy-manual/01-at-rest.md', 'What the idle measurements pin down is the slope'),
  'derived', 'aifoundry2', 'A fit (E17); only the total and the slope are pinned down.', 'dvfs')
F('idle-leak-range', 'idle and leakage', 'power',
  'Leakage at 80 C is 20-29 W of the 35.9 W idle (fixed part 7-16 W): the idle bins fit equally well with the leakage e-folding anywhere from 30 to 45 C.',
  r(rest['A_leak_80_w'], 1), 'W (best fit; range 19.6-28.6)', 'manual.json: rest.profile.A_leak_80_w [19.57, 28.65], .P_fix_w [7.30, 16.28], .T_L_window_c [30, 45]',
  'derived', 'aifoundry2', None, 'energy')
lf = rest['leak_fraction']
F('idle-leak-share', 'idle and leakage', 'power',
  'Leakage share at 80 C (best-fit law): 65% of an idle card (64% of the 36.3 W measured) and 36% of a card running a random-data fp32 matmul; above the 5-30% called typical for a mature chip.',
  r(lf['idle_80c_law'] * 100, 0), '%', 'manual.json: rest.leak_fraction (idle_80c_law 0.648, idle_80c 0.640, busy_randn_80c 0.364); ' + cl('Leakage share of an idle card at 80 °C'),
  'derived', 'aifoundry2', 'Busy leakage share not identified in the version-3 check (0.17-0.80 fit equally well; E44).', 'dvfs')
F('idle-cards', 'board power', 'power',
  'Idle board power per card at 80 C by each card\'s own law: 35.9 W (aifoundry2), 37.3 W (aifoundry3), 48.9 W (aifoundry1-c1); aifoundry3 idles +1.01 W and aifoundry1-c1 +10.07 W above aifoundry2\'s law.',
  35.9, 'W at 80 C (aifoundry2)', mdline('docs/energy-manual/07-composition.md', '37.3 W and 48.9 W at 80 °C') + '; manual.json rest.per_card (a3 12.29 + 25.03, a1c1 14.06 + 34.80); ' + cl('aifoundry3\'s idle against aifoundry2\'s idle law'),
  'derived', CARDS3, 'Laws refitted per card with the e-folding held at 36 C, rms 0.10 and 0.09 W.', 'energy')
F('idle-catalogue', 'board power', 'power',
  'Idle during the 26 Sep catalogue: 32.8 W on aifoundry2 (die 67-92 C), 25.8 W on aifoundry3 (55-60 C), 34.3 W on aifoundry1-c1 (57-71 C).',
  32.8, 'W', 'manual.json: catalogue.idle_split.<card>.board (32.75, 25.77, 34.35); ' + mdline('docs/energy-manual/01-at-rest.md', 'Idle during the catalogue'),
  'measured', CARDS3, None, 'energy')
r73 = rest['rails_73c']
F('idle-rails', 'board power', 'power',
  'Where idle goes at 73 C (aifoundry2): minions 11.05 W (35%), SRAM 2.00 W (6%), mesh 3.64 W (11%), no rail sensor (PCIe, DDR PHY, I/O shire, regulators) 15.10 W (48%); board 31.79 W. aifoundry1-c1 at 73 C: 15.96 / 3.05 / 5.83 / 17.87, board 42.71 W.',
  r(r73['board'], 2), 'W', 'manual.json: rest.rails_73c (minion 11.05, sram 2.00, noc 3.64, unsensed 15.10, board 31.79); ' + mdline('docs/energy-manual/01-at-rest.md', '| Minions | 11.05'),
  'measured', 'aifoundry2, aifoundry1-c1', 'The unsensed ~15 W is the largest single component of idle on every card and cannot be split with any instrument here.', 'energy')
F('idle-unsensed-slope', 'idle and leakage', 'power',
  'The unsensed blocks move little with temperature (0.10 W/C on aifoundry2 over 74-88 C); the three metered rails carry the leakage, 0.53 W/C between them at 75-80 C.',
  0.53, 'W/C', cl('Unsensed idle slope (board − three rails)'), 'measured', 'aifoundry2, aifoundry1-c1', 'aifoundry1-c1: 0.16 and 0.77 W/C.', 'energy')
F('sram-idle', 'L2 cache', 'power',
  'SRAM rail at idle (leakage of the L2/L3/scratchpad arrays): 1.60 W at 67 C, 2.63 W at 82 C on aifoundry2; slope 0.066 W/C on aifoundry3.',
  2.63, 'W at 82 C', cl('SRAM rail at idle | 1.60 W') + '; ' + cl('SRAM rail at idle | slope'), 'measured', 'aifoundry2, aifoundry3', None, 'energy')
F('mm-composition', 'board power', 'power',
  'Dense fp32 matmul on random data at 80 C, priced from the tables: fixed 12.6 W + leakage 23.3 W + multiply-adds 26.5 W = 62.4 W, against 63.6 W measured: 57% of it is keeping the card on and leaking.',
  62.4, 'W', mdline('docs/energy-manual/07-composition.md', '**Board power from the tables**'),
  'derived', 'aifoundry2', 'A decomposition checked against a measurement, not a prediction.', 'energy')
F('tdp-a3', 'clock and voltage', 'operating point',
  'The firmware\'s static TDP: 65 W on aifoundry2 and aifoundry1-c1, 0 W on aifoundry3 (set by a boot service), which pins aifoundry3 at 600 MHz; the driver reports 65 W on all.',
  0, 'W (aifoundry3 TDP)', cl('Governor configuration and trace, per card') + '; ' + mdline('docs/energy-manual/01-at-rest.md', 'Static TDP the firmware uses'),
  'measured', CARDS3, None, 'dvfs')
F('gov-thresholds', 'clock and voltage', 'operating point',
  'Governor thresholds in the firmware source: 65 C software and 65 W TDP (75 C / 75 W catastrophic), checked once per management pass (~133 ms on aifoundry2); no hysteresis; the power input is a PMIC measurement.',
  65, 'C', cl('Firmware governor thresholds') + '; ' + cl('Governor thresholds | 65 °C software'),
  'spec', None, 'Read from et-platform source at 353f20e (thermal_pwr_mgmt.h); the cards run an older build.', 'dvfs')

# --------------------------------------------------------------------------------------------------
# Die temperature
# --------------------------------------------------------------------------------------------------
F('temp-sensors', 'die temperature', 'temperature',
  '35 temperature sensors on the die (34 minion shires + the I/O shire, one per tile of the 6x6 grid except PCIe), 12-bit (0.061 C) in hardware; the host sees one 34-shire mean in whole degrees plus peak-hold extremes.',
  35, 'sensors', 'docs/reports/2026-09-22-et-soc1-spatial-temperature-brief.html headline tiles; ' + cl('Moortec PVT: 35 temperature sensors'),
  'spec', None, 'Firmware source (bl2_pvt_controller.h) and PRM sec. 1.6.', 'spatial')
F('temp-hottest', 'die temperature', 'temperature',
  'At each rise, the hottest shire read 2-3 C above the chip mean (3-4 C in 61-83% of rises by card), but the host never learns which shire it was.',
  3, 'C above the mean', cl('Peak-hold high against the SP\'s maximum of the mean'), 'measured', CARDS3, None, 'spatial')
F('temp-idle', 'die temperature', 'temperature',
  'Idle die temperatures: aifoundry2 62-80 C (62 C after a night idle, 26.7 W; 80 C, 36.3 W), aifoundry3 near 50-56 C; under the catalogue the median busy die was 74 C (a2), 58 C (a3), 61 C (a1c1).',
  74, 'C (aifoundry2 busy median)', 'manual.json: catalogue.die_c_busy_median; ' + cl('Idle board power at 62 °C') + '; docs/reports/2026-09-20-et-soc1-power-temperature.html lede',
  'measured', CARDS3, None, 'power')
F('temp-slope-busy', 'die temperature', 'power',
  'Under load the same work costs about 1 W more per C the die warms: 0.9-1.2 W/C at 73-97 C on aifoundry2 and aifoundry1-c1 (1.02 and 1.13 W/C in the load step), 0.6 W/C on the cooler aifoundry3.',
  1.02, 'W/C (aifoundry2)', cl('Load step: busy slope and DRAM phase') + '; docs/reports/2026-09-20-et-soc1-power-temperature.html lede',
  'measured', CARDS3, None, 'power')
F('temp-rth', 'die temperature', 'temperature',
  'Thermal resistance, card in its desktop box: 1.47 C/W total (six stages, 1.5 s to 2,500 s); leakage loop gain 0.95 at 80 C, passing 1 at 82 C: about 3 W of sustained switching power before runaway.',
  1.47, 'C/W', cl('Thermal resistance, total') + '; ' + cl('Leakage loop gain at 80 °C'), 'derived', 'aifoundry2',
  'A fit (E17); do not apply to aifoundry3 (its heatsink is visibly faster).', 'horace')
F('temp-a3-90', 'die temperature', 'temperature',
  'aifoundry3 under a back-to-back random-data heater: the die peaks at 90 C in 3 of 3 cycles (after 126-150 two-second bursts), against a predicted 60-66 C plateau.',
  90, 'C', cl('aifoundry3 under a back-to-back random-data heater'), 'measured', 'aifoundry3', None, 'dvfs')
F('temp-a1c0', 'die temperature', 'temperature',
  'aifoundry1\'s card 0 overheats: ten minutes of short smoke blocks took its die to 98-102 C, and right after it read 115-117 C with nothing running, drawing 66-71 W at 600 MHz. It is excluded from all measurements.',
  117, 'C', mdline('docs/findings/14-card-behaviour.md', "aifoundry1's card 0 overheats"),
  'measured', 'aifoundry1 card 0', None, None)

# --------------------------------------------------------------------------------------------------
# Mesh (NoC): cost per hop
# --------------------------------------------------------------------------------------------------
F('mesh-hop-lat', 'mesh (NoC)', 'latency',
  'Each mesh hop adds 12 cycles round trip at 600 MHz (20 ns): L3 11.99, remote scratchpad 12.00, TensorSend 12.01-12.02 cycles per hop on every card.',
  12.0, 'cycles per hop (round trip)', cl('L3 hit latency against mesh hops') + '; ' + cl('Another shire\'s scratchpad | 99.84') + '; ' + cl('TensorSend round trip between shires; credits'),
  'measured', CARDS3, '20 ns at either clock (16 cycles at 800 MHz): a NoC-clock cost.', 'noc')
F('mesh-hop-mm', 'mesh (NoC)', 'geometry',
  'One mesh hop is 3.72 mm of silicon (3.64-3.74; x 3.73, y 3.70), from Esperanto\'s die plot scaled to the 570 mm^2 die (25.6 x 22.2 mm).',
  WREP['inputs']['hop_mm']['value'], 'mm', 'docs/reports/data/2026-09-24-wire-energy/report.json: inputs.hop_mm, pitch_x_mm, pitch_y_mm, die_w_mm, die_h_mm',
  'inferred', None, 'An estimate from the die plot, not a measurement (05-claims kind A).', 'wire')
hl = WREP['headline']
F('mesh-bit-mm-free', 'mesh (NoC)', 'energy',
  f'A random bit per mm on free links, mesh rail at 0.485 V: {hl["uncontended/noc_rail"]["random_bit_total"]["mean"]:.0f} fJ ({hl["uncontended/noc_rail"]["random_bit_data"]["mean"]:.0f} of it data-dependent); on board power {hl["uncontended/board"]["random_bit_total"]["mean"]:.0f} fJ. Dally\'s rule of thumb is ~100 fJ/b-mm.',
  r(hl['uncontended/noc_rail']['random_bit_total']['mean'], 1), 'fJ per bit-mm', 'report.json: headline["uncontended/noc_rail"].random_bit_total / .random_bit_data, headline["uncontended/board"].random_bit_total; per card (V3) ' + cl('A random bit per mm, free links (V3)'),
  'measured', CARDS3, 'Per card, mesh rail: a2 36.1, a3 35.8, a1c1 38.1 fJ; board 46.7, 44.4, 51.1 fJ (99% intervals in 05-claims). Scaled to 0.9 V the data cost is 85-105 fJ.', 'wire')
F('mesh-bit-mm-loaded', 'mesh (NoC)', 'energy',
  f'On a busy mesh where flows share links the same random bit costs {hl["loaded/noc_rail"]["random_bit_total"]["mean"]:.0f} fJ per mm on the mesh rail and {hl["loaded/board"]["random_bit_total"]["mean"]:.0f} fJ on board power.',
  r(hl['loaded/noc_rail']['random_bit_total']['mean'], 1), 'fJ per bit-mm', 'report.json: headline["loaded/noc_rail"].random_bit_total, headline["loaded/board"].random_bit_total',
  'measured', CARDS3, None, 'wire')
F('mesh-hop-pjb-derived', 'mesh (NoC)', 'energy per byte',
  'Per byte per hop, from the free-link figure: about 1.1 pJ/B on the mesh rail (37 fJ/bit-mm x 8 bits x 3.72 mm); the energy manual quotes Heat per millimetre as 1.5 pJ/B per hop on the mesh rail and 2.2 on board power for a loaded mesh.',
  r(hl['uncontended/noc_rail']['random_bit_total']['mean'] * 8 * 3.72 / 1000, 2), 'pJ/B per hop', 'derived from report.json headline x inputs.hop_mm; ' + mdline('docs/energy-manual/05-bytes-between-cores.md', 'measures 1.5 pJ/B per hop on the mesh rail'),
  'derived', CARDS3, 'The manual\'s 1.5 / 2.2 derive from the earlier two-card loaded-mesh fit (50.4 / 72.9 fJ per bit-mm); the page now shows the three-card 53 / 79.', 'wire')
F('mesh-hop-fit', 'mesh (NoC)', 'energy per byte',
  'Tensor loads from a scratchpad d hops away, fitted over 1-8 hops (board power): one hop costs 0.67 pJ/B on zeros [0.62-0.73] and 1.80 pJ/B on random data [1.72-1.91]; 142 fJ per random bit per hop is data-dependent.',
  1.80, 'pJ/B per hop', mdline('docs/energy-manual/04a-fine-grain.md', 'Fitted over 1–8 hops, one hop costs'),
  'derived', CARDS3, 'Over 1-6 hops 2.23 / 2.19 / 2.40 pJ/B per hop on random data (a2 / a3 / a1c1).', 'energy')
F('mesh-hop-ring', 'tensor network (TensorSend)', 'energy per byte',
  'TensorSend across the mesh: 9.2 pJ/B to leave the shire plus 1.75 pJ/B per mean hop (three cards pooled; a2 9.1 + 1.8, a3 8.0 + 1.7, a1c1 10.4 + 1.7); no card\'s per-hop cost differs from another\'s.',
  1.75, 'pJ/B per hop', 'docs/reports/data/2026-09-25-claims-v3/results/rl.json: items[RL-a].pooled_mean; ' + cl('Ring energy per mesh hop, five 1 KB cross-shire rings (V3)') + '; ' + mdline('docs/energy-manual/05-bytes-between-cores.md', '9.1 pJ to leave the shire'),
  'derived', CARDS3, 'Straight line through five 1 KB rings (1.6-4.7 mean hops), six passes per card.', 'noc')
F('mesh-ones', 'mesh (NoC)', 'energy',
  'The ones carried cost energy, not only bits that flip: a stream of all ones costs 8-12% more per hop than random data on the mesh rail, though at one hop it costs 35-37% less.',
  9.6, '% more per hop (aifoundry2)', cl('All ones against random data'), 'measured', CARDS3, 'Per one carried per hop: 129 fJ mesh rail (E32 fit, two cards).', 'wire')

# --------------------------------------------------------------------------------------------------
# Tensor network (TensorSend), barriers and reductions
# --------------------------------------------------------------------------------------------------
F('ts-rt-fln', 'tensor network (TensorSend)', 'latency',
  'TensorSend round trip, 32 B register to register inside a shire: 68 cycles (113 ns) on the 7 fast-network tree edges of each neighbourhood, 114-115 cycles (190 ns) for every other pair.',
  68, 'cycles', cl('TensorSend round trip inside a shire, 32 B') + '; docs/reports/2026-09-18-et-soc1-on-chip-communication.html "Inside a shire, only the tree edges are fast"',
  'measured', CARDS3, 'Same pairs and same cycles in every pass on all three cards.', 'noc')
F('ts-rt-mesh', 'tensor network (TensorSend)', 'latency',
  'TensorSend round trip between shires, 32 B: 150 + 12.02 cycles per mesh hop (250 ns + 20 ns/hop), worst residual 1.1-1.4 cycles over all 496 shire pairs; 1 KB messages add 12 cycles per hop to 5 hops and 36 beyond.',
  150, 'cycles + 12.02 cycles/hop', 'lat.json: items[LAT-N2].per_card.<card>.passes[].pingpong_fit, .c32_slope_to5, .c32_slope_beyond5; ' + cl('TensorSend round trip between shires; credits'),
  'measured', CARDS3, 'The shire map (marty1885\'s) is recovered from latency alone in 12 of 12 search restarts.', 'noc')
F('ts-credit', 'synchronisation (barriers, atomics)', 'latency',
  'Credit-counter (FCC) round trip: 140.2 + 14.43 cycles per hop (234 ns + 24 ns/hop); blocking credit inside a shire 119.5-119.9 cycles (200 ns).',
  140.2, 'cycles + 14.43 cycles/hop', cl('TensorSend round trip between shires; credits'), 'measured', CARDS3, 'The registered prediction (148 + 12.2) failed: credits rise 24 ns per hop, not 20.', 'noc')
F('ts-flag', 'synchronisation (barriers, atomics)', 'latency',
  'A flag handed off through global atomics in memory (the GPU pattern): 610-1,150 ns round trip (median 873 ns across shires), with no measurable dependence on distance.',
  873, 'ns', 'docs/reports/2026-09-18-et-soc1-on-chip-communication.html "Latency grows with distance, except through memory"', 'measured', CARDS3, None, 'noc')
F('sync-shire-barrier', 'synchronisation (barriers, atomics)', 'latency',
  'Shire barrier (fast local barrier + credits, 32 minions, all 32 shires at once): 233 cycles (388 ns); 232.5-232.7 on the three cards.',
  233, 'cycles', 'lat.json: items[LAT-N1].per_card.<card>.passes[].shire_barrier; ' + cl('Barriers and allreduces'), 'measured', CARDS3,
  'Corrected from 237 (one session, 18 Sep).', 'noc')
F('sync-allreduce32', 'synchronisation (barriers, atomics)', 'latency',
  'Hardware allreduce (TensorReduce + TensorBroadcast) of 32 B over a shire\'s 32 minions: 444 cycles (0.74 us), 444.06-444.31 on all three cards.',
  444, 'cycles', 'lat.json: items[LAT-N1].per_card.<card>.passes[].allreduce32; ' + cl('Barriers and allreduces'), 'measured', CARDS3, 'Corrected from 432.', 'noc')
F('sync-allreduce1024', 'synchronisation (barriers, atomics)', 'latency',
  'Hardware allreduce of 32 B over all 1,024 minions: 1,393 cycles (2.3 us), 1,392.6-1,393.4 on the three cards; an A100 grid.sync() alone is 1.1-1.2 us.',
  1393, 'cycles', 'lat.json: items[LAT-N4].per_card.<card>.passes[].allreduce_1024; ' + cl('Barriers and allreduces'), 'measured', CARDS3, None, 'noc')
F('sync-chip-barrier', 'synchronisation (barriers, atomics)', 'latency',
  'Chip-wide barrier built from FLB, global atomics and credits: 4,976-4,991 cycles with one minion per shire, 4,998-5,013 with all 1,024 (about 8.3 us); the allreduce tree does it in 2.3 us.',
  5013, 'cycles', 'lat.json: items[LAT-N4].per_card.<card>.passes[].chip_barrier; ' + cl('Barriers and allreduces'), 'measured', CARDS3,
  'Energy: about 10 uJ of waiting (1,024 stalled minions at 1.2 mW for the barrier\'s length; derived, energy manual section 6).', 'noc')
tsring = MAN['reruns']['rings_pj_per_byte']
F('ts-e-pair', 'tensor network (TensorSend)', 'energy per byte',
  f'Messaging energy, 1 KB TensorSend: {tsring["pair"]["mean"]:.2f} pJ/B between the two minions of a pair, {tsring["neigh"]["mean"]:.2f} around a neighbourhood, {tsring["shire"]["mean"]:.2f} around a shire, 12.5-18.3 across the mesh (busy cores included).',
  r(tsring['pair']['mean'], 2), 'pJ/B', 'manual.json: reruns.rings_pj_per_byte.<pair|neigh|shire|xshire*>; ' + mdline('docs/energy-manual/05-bytes-between-cores.md', '| pair |'),
  'measured', CARDS3, '128 B messages cost more: 3.66 pJ/B around a shire, 20.2 to the next shire ID.', 'noc')

# --------------------------------------------------------------------------------------------------
# Hot line (one contended global atomic)
# --------------------------------------------------------------------------------------------------
F('hot-cost', 'hot line', 'rate',
  'One contended global atomic (amoaddg.w on one line, 1,024 minions): the bank retires one every 10.00 cycles, about 60 M/s for the whole chip; spread over 32 lines, one per shire, 0.31 cycles and 1,919 M/s: 32x.',
  10.0, 'cycles per atomic', cl('Cost of one contended atomic') + '; ' + cl('Same work on 32 lines, one per shire'), 'measured', 'aifoundry2',
  'The atomic itself is fair: every shire gets 0.998-1.004 of an even split, the host included.', 'hotline')
F('hot-stop', 'hot line', 'rate',
  'The host shire\'s own memory path stops, not slows: 384-392 of its loads get through per window (192-240 for a DRAM-backed line) whether the window is 5 ms or 100 ms, on every card.',
  384, 'loads per window', cl('One hot line, repeated (E22–E23)') + '; docs/reports/2026-09-22-hot-line.html sections 2 and 4', 'measured', CARDS3,
  'About 17 loads per minion get through, then nothing; the kernel finishes when the hammering stops.', 'hotline')
F('hot-edge', 'hot line', 'rate',
  'The switch is sharp: 21 remote requesters leave the host at 95.5-95.7% of its rate, 22 stop it (0.02%). Rule: the bank is not saturated while N x 10 cycles < P + t_round_trip (216 cycles).',
  22, 'requesters', cl('One hot line, repeated (E22–E23)') + '; docs/reports/2026-09-22-hot-line.html section 3', 'measured', CARDS3, None, 'hotline')
F('hot-rt', 'hot line', 'latency',
  'Uncontended remote global-atomic round trip: 216 cycles (216.2 = 6,000,000 / 27,755).',
  216.2, 'cycles', cl('Uncontended remote global-atomic round trip') + '; manual.json sync.remote_atomic_latency_cycles', 'measured', 'aifoundry2', None, 'hotline')
hn = MAN['reruns']['hotline_nj_per_op']
F('hot-energy', 'hot line', 'energy',
  f'Energy per atomic: {hn["contended"]["mean"]:.1f} nJ [{hn["contended"]["lo"]:.1f}-{hn["contended"]["hi"]:.1f}] contended against {hn["spread"]["mean"]:.2f} nJ [{hn["spread"]["lo"]:.2f}-{hn["spread"]["hi"]:.2f}] spread over 32 lines: 17x.',
  r(hn['contended']['mean'], 1), 'nJ per atomic', 'manual.json: reruns.hotline_nj_per_op.contended / .spread; ' + cl('Contended hot line | 19.8 nJ'), 'measured', 'aifoundry2, aifoundry3',
  'The three-card check did not repeat the power runs; n = 7 (4 a2 + 3 a3).', 'hotline')
F('hot-pace', 'hot line', 'rate',
  'The workaround (erratum 4.1: slow the others down): pacing the remote minions at 10,000 cycles gives the host back 54.5-56.8% while the hammering shires keep about 96%.',
  54.5, '% of host rate (aifoundry2)', cl('One hot line, repeated (E22–E23)') + '; ' + cl('Pacing that restores the host'), 'measured', CARDS3,
  'Errata 4.1 (RTLMIN-6207) and 4.2 (RTLMIN-6214), both Postponed, describe it.', 'hotline')

# --------------------------------------------------------------------------------------------------
# The relay
# --------------------------------------------------------------------------------------------------
rel = MAN['reruns']['relay_pj_per_byte']
F('relay-energy', 'relay', 'energy per byte',
  f'Relay energy per byte (write + read): through DRAM {rel["dram"]["mean"]:.1f} pJ/B [{rel["dram"]["lo"]:.1f}-{rel["dram"]["hi"]:.1f}], to the next shire\'s scratchpad {rel["hop"]["mean"]:.1f} [{rel["hop"]["lo"]:.1f}-{rel["hop"]["hi"]:.1f}], in the own scratchpad {rel["scp"]["mean"]:.1f} [{rel["scp"]["lo"]:.1f}-{rel["scp"]["hi"]:.1f}].',
  r(rel['hop']['mean'], 1), 'pJ/B (next shire)', 'manual.json: reruns.relay_pj_per_byte.<dram|hop|scp>; ' + mdline('docs/energy-manual/05-bytes-between-cores.md', '| Write where the next shire reads it |'),
  'measured', CARDS3, 'Per card DRAM / next shire / own: a2 111.3 / 8.61 / 4.05; a3 107.5 / 8.27 / 4.11; a1c1 129.9 / 9.89 / 4.86.', 'relay')
F('relay-13x', 'relay', 'energy per byte',
  'Handing a slab to the next shire through its scratchpad costs 12.9x, 13.0x and 13.1x less energy per byte than the DRAM round trip (aifoundry2, aifoundry3, aifoundry1-c1): about a thirteenth, the same on every card at 99%.',
  12.97, 'x (pooled)', 'docs/reports/data/2026-09-25-claims-v3/results/rl.json: items[RL-d, part=relay DRAM / next shire].per_card.<card>.ratio_geo_mean; ' + cl('The relay (V3): through DRAM'),
  'measured', CARDS3, None, 'relay')
hg = {c: {m: ONCHIP['headline'][c][m]['gb_s'] for m in ('dram', 'hop', 'scp')} for c in ONCHIP['headline']}
F('relay-bw', 'relay', 'bandwidth',
  f'Relay bandwidth (8 stages, 1,024 minions): {hg["aifoundry2"]["dram"]:.1f} GB/s through DRAM, {hg["aifoundry2"]["hop"]:.1f} GB/s to the next shire ({hg["aifoundry2"]["hop"]/hg["aifoundry2"]["dram"]:.1f}x), {hg["aifoundry2"]["scp"]:.0f} GB/s in the own scratchpad (aifoundry2 pass means; the other cards within 1.5%).',
  r(hg['aifoundry2']['hop'], 1), 'GB/s (next shire)', 'docs/reports/data/2026-09-22-onchip-aifoundry2/onchip.json: headline.<card>.<dram|hop|scp>.gb_s; ' + cl('On-chip relay, repeated (E25)'),
  'measured', CARDS3, 'Speed-ups 12.25-12.42x (next shire) and 30.8-31.2x (own scratchpad) over DRAM; the advantage needs the live data to outgrow the 32 MB L3 (below it 1.4-1.5x).', 'relay')
F('relay-watts', 'relay', 'power',
  'The three relay media draw within a watt of each other over idle (4.34 / 4.42 / 5.30 W for DRAM / next shire / own): the relay\'s energy saving is time, not power.',
  4.42, 'W over idle (next shire)', cl('Power over idle, all three media'), 'measured', 'aifoundry2', 'The 22 Sep session\'s power block (onchip.json power).', 'relay')

# --------------------------------------------------------------------------------------------------
# Gathers and scatters (E48, gs.json; reduced 27 Sep, not yet on a published page)
# --------------------------------------------------------------------------------------------------
GSP = 'docs/reports/data/2026-09-25-claims-v3/results/gs.json'
gp = GS['items']['GS-RATE']['pooled']
gpc = GS['items']['GS-RATE']['per_card']
LEVELS = [('dram-512B', 'L1 data cache', 'L1 (512 B table per hart)'),
          ('dram-4K', 'L2 cache', 'L2 (4 KB table per hart)'),
          ('scp-16K', 'scratchpad (own shire)', 'own scratchpad (16 KB per hart)'),
          ('rscp-16K', 'scratchpad (other shire)', 'scratchpad 2 hops away (16 KB per hart)'),
          ('dram-256K', 'DRAM (LPDDR4X, memory shires)', 'DRAM (256 KB table per hart)')]
GS_NOTE = ('E48 (V3-GS), reduced 27 Sep; not yet on a published page or in 03-experiments.md. Each visit issues 8 indexed '
           'instructions of 8 lanes; "rand" puts the visit\'s 64 elements on the 64 distinct lines of one 4 KB tile, tiles walked '
           'in scrambled order, not uniform random addresses (tools/claims-v3/gs/README.md). A 512 B private table stays in the L1 '
           'and a 4 KB one thrashes the 8-line L1 and hits the L2. Both harts of 1,024 minions, random data, energy above idle; brackets are the range over the 9 passes (three per card).')
for op, opname, prep in [('fgw.ps', 'Gather (fgw.ps, 32-bit elements)', 'from'), ('fscw.ps', 'Scatter (fscw.ps, 32-bit elements)', 'into')]:
    for lvkey, comp, lvname in LEVELS:
        k = f'gs/E/{op}/{lvkey}/rand/random/h2/mff/n1024'
        d = gp[k]
        e = d['elements_per_s']['mean']; pj = d['pj_per_element']
        def fm(x):
            return f'{x:,.0f}' if x >= 1000 else (f'{x:.1f}' if x >= 100 else f'{x:.2f}')
        per = ', '.join(f'{lab} {fm(gpc[c][k]["pj_per_element"]["mean"])}' for c, lab in (('aifoundry2', 'a2'), ('aifoundry3', 'a3'), ('aifoundry1-c1', 'a1c1')))
        cpi = gpc['aifoundry2'][k]['cpi_med']['mean']
        eu = f'{e/1e9:.3g} G elements/s'
        F(f'gs-{"g" if op == "fgw.ps" else "s"}-{lvkey}', comp, 'gather/scatter',
          f'{opname} {prep} {lvname}, random lines: {eu} chip-wide, {fm(pj["mean"])} pJ per element [{fm(pj["min"])}-{fm(pj["max"])}] (per card: {per}); {fm(cpi)} cycles per instruction per hart.',
          float('%.4g' % pj['mean']), 'pJ per element',
          f'{GSP}: items["GS-RATE"].pooled["{k}"] (elements_per_s, pj_per_element over 9 passes); .per_card.<card>["{k}"].cpi_med',
          'measured', CARDS3, GS_NOTE, None)
ul = GS['items']['GS-UC']
F('gs-uc', 'gather/scatter', 'gather/scatter',
  'GS-UC failed on all three cards: an L1-bypassing gather (fgwl.ps, random lines from L2, one minion) runs only 1.03x faster with both harts than with one (registered prediction 1.6-2.4x): the second hart adds about 3%.',
  1.03, 'x (h2/h1)', f'{GSP}: items["GS-UC"].per_card.<card>.h2_over_h1 (1.0299-1.0303), outcome FAIL', 'measured', CARDS3, GS_NOTE, None)
F('gs-l1', 'gather/scatter', 'gather/scatter',
  'A 32-bit gather of 8 lanes from L1 (fgw.ps, random, 512 B per hart) takes 10.89 cycles per instruction per minion on every card (registered 7-12: PASS).',
  GS['items']['GS-L1']['per_card']['aifoundry2']['cpi_minion']['mean'], 'cycles per instruction per minion',
  f'{GSP}: items["GS-L1"].per_card.<card>.cpi_minion', 'measured', CARDS3, GS_NOTE, None)
mh = GS['items']['GS-MH']['per_card']['aifoundry2']
F('gs-mh', 'gather/scatter', 'gather/scatter',
  f'Gathers from L2 and the own scratchpad saturate at {mh["l2"]["mean"]/1e9:.2f} G elements/s chip-wide on every card, 1.15x the two-miss-handler bound of 23.86 G/s (registered 0.5-2x: PASS); a second hart adds nothing (h2/h1 1.0005).',
  r(mh['l2']['mean'] / 1e9, 2), 'G elements/s', f'{GSP}: items["GS-MH"].per_card.<card>.l2 / .scp, .bound_elements_per_s, .h2_over_h1_l2', 'measured', CARDS3, GS_NOTE, None)
gd = GS['items']['GS-DRAM']['per_card']
F('gs-dram', 'gather/scatter', 'gather/scatter',
  f'Random gathers from DRAM (256 KB per hart) move whole lines at {gd["aifoundry2"]["line_bytes_per_s"]["mean"]/1e9:.1f} GB/s of line traffic, the chip\'s 76 GB/s DRAM stream, on every card (PASS): 1.19 G useful 4-byte elements/s.',
  r(gd['aifoundry2']['line_bytes_per_s']['mean'] / 1e9, 1), 'GB/s (line bytes)', f'{GSP}: items["GS-DRAM"].per_card.<card>.line_bytes_per_s', 'measured', CARDS3, GS_NOTE, None)
ga = {x['method']: x for x in GS['items']['GS-ADD']['rows']}
F('gs-add', 'gather/scatter', 'gather/scatter',
  f'Scatter-add alternatives, updates/s and nJ per update: gather + add + scatter in L1 {ga["upd L1"]["updates_per_s"]["mean"]/1e9:.0f} G/s at {ga["upd L1"]["nj_per_update"]["mean"]*1000:.0f} pJ; in DRAM {ga["upd DRAM"]["updates_per_s"]["mean"]/1e9:.2f} G/s at {ga["upd DRAM"]["nj_per_update"]["mean"]:.1f} nJ; packed atomic famoaddl.pi on a shire table {ga["famoaddl.pi shire table"]["updates_per_s"]["mean"]/1e9:.1f} G/s at {ga["famoaddl.pi shire table"]["nj_per_update"]["mean"]:.2f} nJ; amoaddg.w on a chip table {ga["amoaddg.w chip table"]["updates_per_s"]["mean"]/1e9:.2f} G/s at {ga["amoaddg.w chip table"]["nj_per_update"]["mean"]:.2f} nJ.',
  r(ga['famoaddl.pi shire table']['nj_per_update']['mean'], 3), 'nJ per update (famoaddl.pi, shire table)', f'{GSP}: items["GS-ADD"].rows[] (updates_per_s, nj_per_update, pooled over 9 passes)',
  'measured', CARDS3, GS_NOTE + ' Reference: spread global atomics 1.92 G/s at 1.16 nJ (energy manual section 6).', None)
gc = GS['items']['GS-CARD']['ratios']
F('gs-card', 'gather/scatter', 'gather/scatter',
  f'Card to card, gathers and scatters: elements/s identical (median ratio 1.000); pJ per element aifoundry3/aifoundry2 {gc["aifoundry3/aifoundry2"]["pj_per_element"]["median"]:.3f}, aifoundry1-c1/aifoundry2 {gc["aifoundry1-c1/aifoundry2"]["pj_per_element"]["median"]:.3f} (median over 100 configurations).',
  r(gc['aifoundry3/aifoundry2']['pj_per_element']['median'], 3), 'ratio', f'{GSP}: items["GS-CARD"].ratios', 'measured', CARDS3, GS_NOTE, None)
F('gs-conflict', 'gather/scatter', 'gather/scatter',
  'When every lane of a scatter hits one word, lane 7 (the highest active lane) wins, in every launch on every card, as the simulator orders it.',
  7, 'lane', f'{GSP}: items["GS-CONFLICT"].per_card.<card>.winners_by_op', 'measured', CARDS3, GS_NOTE, None)

# --------------------------------------------------------------------------------------------------
# Chip-level measured facts
# --------------------------------------------------------------------------------------------------
F('chip-minions', 'chip', 'configuration',
  'Kernels run on 1,024 minions (32 compute shires x 32) of the 1,088 on the chip; every measurement here uses them at 600 MHz.',
  1024, 'minions', cl('Minions used by these workloads'), 'measured', 'aifoundry2', 'The other 64 are the master and spare shires (34 minion shires in all).', 'hub')
F('chip-cross-card', 'chip', 'card-to-card',
  'Card to card, 392 catalogue entries at each card\'s own die temperature: aifoundry3 / aifoundry2 median 0.972, aifoundry1-c1 / aifoundry2 median 0.962 (1.147 per byte).',
  0.972, 'ratio', mdline('docs/energy-manual/08-cards.md', 'Instruction and byte energies, 392 catalogue entries'), 'measured', CARDS3,
  'Energy per operation rises with die temperature: +0.48%/C (a2), +0.30%/C (a3).', 'energy')
F('pmic-refresh', 'board power', 'measurement',
  'The board power meter (PMIC, 10 mW resolution) takes a new value about every 156 ms on aifoundry2 and aifoundry1-c1 and 263 ms on aifoundry3 under 10 Hz sampling; the service-processor pass is 133.2 / 134.8 / 224.1-224.5 ms quiet.',
  133.2, 'ms (aifoundry2 SP pass)', cl('Service-processor pass, quiet (no poller)') + '; docs/reports/2026-09-20-et-soc1-power-temperature.html lede', 'measured', CARDS3,
  'Every energy number is an average over billions of identical events.', 'power')

# ---------------------------------------------------------------------------------------------------
ids = [f['id'] for f in FACTS]
assert len(ids) == len(set(ids)), [i for i in ids if ids.count(i) > 1]
json.dump(FACTS, open(OUT, 'w'), indent=1, ensure_ascii=False)
print(len(FACTS), 'facts ->', OUT)
from collections import Counter
print(Counter(f['component'] for f in FACTS))
print(Counter(f['kind'] for f in FACTS))
