#!/usr/bin/env python3
"""Build inside.json and research-inside.md: what is inside every part the chip diagram lets a reader select, as a
tree down to circuit components, transistors and the silicon crystal.

Run: python3 build_inside.py  (reads the worktree's facts files; writes next to this script)

Facts that already exist in the pages' data are pulled from those files (their statement, kind and source), with a
`fid` that names them: `chip:<id>` for docs/reports/data/2026-09-27-chip-diagram/facts.json, `chip-research:<id>` for
a row of that page's research/ files that did not reach facts.json, `ml:<level>:<id>` for
docs/reports/data/2026-09-28-memory-levels/facts.json. Everything else carries its own source string.
"""
import json, os, re, sys, textwrap

WT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..', '..', '..'))   # the repository's root
OUT = os.path.dirname(os.path.abspath(__file__))
CF = json.load(open(f'{WT}/docs/reports/data/2026-09-27-chip-diagram/facts.json'))['facts']
MF = json.load(open(f'{WT}/docs/reports/data/2026-09-28-memory-levels/facts.json'))['facts']
CR = {}
for fn in ['facts-arch.json', 'facts-layout.json', 'facts-numbers.json', 'facts-v2.json']:
    d = json.load(open(f'{WT}/docs/reports/data/2026-09-27-chip-diagram/research/{fn}'))
    items = d if isinstance(d, list) else d.get('facts', d)
    if isinstance(items, dict): items = list(items.values())
    for x in items:
        if isinstance(x, dict) and x.get('id'): CR.setdefault(x['id'], x)

LABELS = ['spec', 'measured', 'derived', 'inferred', 'outside', 'generic', 'unknown']
KMAP = {'spec': 'spec', 'measured': 'measured', 'derived': 'derived', 'inferred': 'inferred', 'generic': 'generic',
        'unknown': 'unknown'}

def _fact(label, text, source, fid=None):
    assert label in LABELS, label
    f = {'text': text, 'label': label, 'source': source}
    if fid: f['fid'] = fid
    return f

def cf(fid, text=None, label=None):
    x = CF[fid]
    return _fact(label or KMAP[x['kind']], text or x['statement'], x['source'], 'chip:' + fid)

def cr(fid, text=None, label=None):
    x = CR[fid]
    return _fact(label or KMAP[x['kind']], text or x['statement'], x['source'], 'chip-research:' + fid)

def mf(key, text=None, label=None):
    x = MF[key]
    return _fact(label or KMAP[x['kind']], text or x['statement'], x['source'], 'ml:' + key)

S = lambda t, s: _fact('spec', t, s)
M = lambda t, s: _fact('measured', t, s)
D = lambda t, s: _fact('derived', t, s)
I = lambda t, s: _fact('inferred', t, s)
O = lambda t, s: _fact('outside', t, s)
G = lambda t, s: _fact('generic', t, s)
U = lambda t, s: _fact('unknown', t, s)

# ---- the outside and document sources used below (full references in the Markdown's source list) ----
IEDM16 = ('S.-Y. Wu et al. (TSMC), "A 7nm CMOS platform technology featuring 4th generation FinFET transistors with a '
          '0.027um2 high density 6-T SRAM cell for mobile SoC applications", IEDM 2016, paper 2.6')
WIKI7 = ('Wikipedia, "7 nm process", comparison table, row TSMC N7 (gate pitch 57 nm, fin pitch 30 nm, minimum metal '
         'pitch 40 nm, 91.2-96.5 MTr/mm2, SRAM cell 0.027 um2; fins SAQP, gates and M0-M4 SADP), '
         'https://en.wikipedia.org/wiki/7_nm_process (read 30 Sep 2026)')
WIKI7IRDS = 'Wikipedia, "7 nm process" (quoting IRDS 2021, Lithography: 7 nm-class gate length 20 nm), https://en.wikipedia.org/wiki/7_nm_process'
FUSE = ('WikiChip Fuse, "TSMC 7nm HD and HP Cells, 2nd Gen 7nm, And The Snapdragon 855 DTCO", https://fuse.wikichip.org/?p=2408 '
        '(HD cell 240 nm tall = 6 tracks of 40 nm, HP 300 nm; about 91.2 MTr/mm2 HD, 65 HP); values as the search summary '
        'reported them, the page itself refused the connection on 30 Sep 2026')
SILICONICS = ('D. James (Siliconics), "A Quick Look at 14-nm and 10-nm", AVS Joint Users Group, July 2018 (JTG718-4), '
              'slides 11 and 17-18: TSMC 10 nm (Apple A11) fin pitch ~33 nm, fin width ~6 nm, functional gate height ~44 nm, '
              'gate width ~95 nm; Intel 10 nm fin height 46-53 nm, width ~7 nm at half height, Lg 18 nm; '
              'https://nccavs-usergroups.avs.org/wp-content/uploads/JTG2018/JTG718-4-James-Siliconics.pdf')
CODATA = 'NIST CODATA 2018: lattice parameter of silicon a = 543.1020511 pm (at 22.5 C in vacuum), https://physics.nist.gov/cgi-bin/cuu/Value?asil'
WH = 'N. Weste and D. Harris, CMOS VLSI Design, 4th ed. (Addison-Wesley 2011)'
RABAEY = 'J. Rabaey, A. Chandrakasan, B. Nikolic, Digital Integrated Circuits, 2nd ed. (Prentice Hall 2003)'
MICRO22 = ('D. Ditzel et al., "Accelerating ML Recommendation With Over 1,000 RISC-V/Tensor Processors on Esperanto\'s '
           'ET-SoC-1 Chip", IEEE Micro 42(3), May/June 2022 (https://www.esperanto.ai/wp-content/uploads/2022/05/Dave-IEEE-Micro.pdf)')
EXT = 'external/'   # the gitignored clones; in the main checkout
VPUSPEC = EXT + 'core-et/docs/Minion VPU Specification.pdf'
FEINT = EXT + 'core-et/docs/FE-Intpipe-Description.pdf'
SHIREDESC = EXT + 'core-et/docs/CORE-ET Minion Shire Description.pdf'
NBHMAS = EXT + 'core-et/docs/CORE-ET-Neigborhood-MAS.pdf'
ICDESC = EXT + 'core-et/docs/Neighborhood-ICache-Description.pdf'
DLLDOC = EXT + 'core-et/docs/Minion Shire DLL Delay Control.pdf'
PRM = EXT + "et-man/ET Programmer's Reference Manual.pdf"
DS = EXT + 'et-man/ET Preliminary Datasheet Rev 1.0.pdf'
ERBIUM = '<<ERBIUM>>'
ERBIUM_NOTE = ('core-et\'s RTL is the Erbium branch: the same Minion core lineage as the ET-SoC-1 in a later MCU-class '
               'configuration (docs/findings/01-resources.md R2); that the ET-SoC-1 silicon matches it block for block is '
               'not confirmed')
RTL = EXT + 'core-et/rtl/'

NODES, ORDER = {}, []

def N(id, parent, name, size_m, size_label, size_note, blurb, facts=(), kind='block', comp=None, layer=None, tip=None,
      see=(), reuse=None, zoom_to=None, off_die=False, instances=None):
    assert id not in NODES, id
    assert size_label in LABELS + ['none'], size_label
    n = {'id': id, 'parent': parent, 'name': name, 'size_m': size_m,
         'size': {'label': size_label, 'note': size_note}, 'kind': kind, 'blurb': ' '.join(blurb.split()),
         'facts': list(facts), 'children': []}
    if comp: n['selectable'] = {'comp': comp, 'layer': layer, 'tooltip': tip}
    if instances: n['instances'] = instances
    if see: n['see'] = list(see)
    if zoom_to: n['zoom_to'] = zoom_to
    if reuse: n['reuse'] = reuse
    if off_die: n['off_die'] = True
    NODES[id] = n; ORDER.append(id)
    return n

def R(scene, scale, builders, how):
    return {'page': 'memory-levels', 'scene': scene, 'scale': scale, 'builders': builders, 'how': how}

# =====================================================================================================================
# The die (layer 0)
# =====================================================================================================================
N('die', None, 'The ET-SoC-1 die', 0.0257, 'inferred',
  'about 25.6-25.8 mm east-west by 22.1-22.2 mm north-south, scaled from Esperanto\'s die plot to 570 mm2 (chip.die-dims)',
  '''One slab of silicon about 26 by 22 mm, carrying over 24 billion transistors. It is a grid of 36 tiles called shires
  (32 compute shires, a master, a spare, a PCIe shire and an I/O shire), eight memory shires down the two sides, and an
  on-chip network joining them.''',
  [cf('chip.die-area'), cf('chip.die-dims'), cf('chip.process'),
   D('Average density: 24 billion transistors over 570 mm2 is about 42 million per mm2, less than half the ~91 MTr/mm2 '
     'of TSMC N7\'s dense logic cells; SRAM periphery, analog blocks (PLLs, PHYs), I/O and wiring take the rest.',
     'arithmetic on chip.process and chip.die-area; the N7 figure: ' + WIKI7),
   cr('L12'), cf('chip.cores-total')],
  comp='chip', layer=0, tip='The ET-SoC-1 die: details')

# ---------------------------------------------------------------------------------------------------------------------
# A compute shire
# ---------------------------------------------------------------------------------------------------------------------
N('shire', 'die', 'Compute shire', 3.72e-3, 'inferred',
  'one tile pitch: 3.73 mm east-west, 3.70 north-south, measured in pixels on the die plot (chip.hop-pitch)',
  '''A tile of 32 small cores (minions) in four neighbourhoods, with 4 MB of shared on-chip memory, a crossbar joining
  them, and one stop on the on-chip network. All 34 minion shires are the same design; 32 of them run the programs.''',
  [cf('shire.composition'), cf('L11'), cf('L114'), cr('shire.voltage-domains'), cr('shire.clock'),
   cf('L123')],
  comp='cshire', layer=0, tip='Shire N, compute shire. Space for details; Enter zooms in.', instances=32,
  reuse=R('l2', 'shire', ['buildL2Shire'], 'the L2 scene\'s shire scale draws the same four neighbourhoods of eight minions over four banks, the crossbars, the UC block and the mesh stop, with the LV and HV bands: reuse it as the logical view, or copy its band drawing into the chip diagram\'s buildShire'))

N('shire.meshstop', 'shire', 'Mesh stop', 5e-4, 'inferred',
  'order of magnitude only: nine 512-bit routers and their crossings; no floorplan of the shire is published (L114, l2.floorplan)',
  '''Where the shire joins the on-chip network. Every request that leaves the shire, and every one that comes in, passes
  through its routers, which pass packets on to the four neighbouring stops.''',
  [cf('mesh.single-attach'), cf('L105'), cf('L103'), cf('L102'), cf('L101'), cf('mesh.clock')],
  comp='meshstop', layer=1, tip='Mesh stop: details',
  reuse=R('l3', 'hop', ['buildL3Hop', 'buildHop'], 'the L3 scene\'s mesh-hop scale draws the requester bank\'s to_l3 master, the VCFIFO with its level shifters and synchroniser, a router and the 3.72 mm link: the inside of a mesh stop, from one lane\'s point of view'))

N('shire.meshstop.router', 'shire.meshstop', 'Router (one of nine main-NoC layers)', 2e-4, 'inferred',
  'order of magnitude: an 8-port router with 512-bit datapaths; the NetSpeed configuration is not in the repository',
  '''A small switch. Packets arrive on its input ports, wait in short queues, and an arbiter decides which one crosses
  the router's internal switch to which output each cycle. Each mesh stop has nine of them stacked as separate networks,
  plus one for debug.''',
  [cf('L105'), mf('l3:g.router'), mf('l3:u.noc-hop'), mf('l3:l3.hop-noc-cycles'),
   cr('L92', 'At least 117 B cross one link direction per 400 MHz NoC cycle (at least 936 data bits), more than one '
      '512-bit layer carries: the link was not saturated in that test.')],
  see=['lib.flipflop', 'lib.mux2', 'lib.arbiter'])

N('shire.meshstop.router.buf', 'shire.meshstop.router', 'Input buffers (virtual channels)', 1e-4, 'inferred',
  'order of magnitude: 8 ports x 4 VC slots of a flit (512 bits or more) each, if flip-flops',
  '''Short queues at each input where packets wait their turn. Each port has four slots (virtual channels), so one
  blocked packet does not stop the others.''',
  [cf('L105', 'Routers have 8 ports (H, E, S, W, N, I, J, K) with 4 VC slots each.'),
   I('If every slot holds one 512-bit flit, one router buffers 8 x 4 x 512 = 16,384 bits, about 147,000 bits over the nine '
     'layers of one stop.', 'arithmetic on L105 with an estimated flit width (SYNTHESIS.md row "Flit width", unknown): '
     'inferred, the weakest of its inputs'),
   mf('l3:g.router', 'Router input buffers are flip-flop or register-file arrays (textbook).')],
  see=['lib.flipflop'])

N('shire.meshstop.router.alloc', 'shire.meshstop.router', 'Route computation and allocators', 5e-5, 'inferred',
  'order of magnitude: arbitration logic for 8 ports',
  '''Logic that reads each packet's destination, picks the output (x first, then y, for a request), and arbitrates when
  two packets want the same output in the same cycle.''',
  [cf('L104'), mf('l3:g.router', 'Route computation, a virtual-channel allocator and a switch allocator (arbiters) pick '
                  'which packet crosses the switch each cycle (textbook).')],
  see=['lib.arbiter', 'lib.nand2'])

N('shire.meshstop.router.xbar', 'shire.meshstop.router', 'Router switch (crossbar)', 1e-4, 'inferred',
  'order of magnitude: an 8 x 8 switch of 512-bit or wider datapaths',
  '''A grid of multiplexers that connects any input port to any output port for one cycle. It is wide: a whole 64-byte
  cache line moves in one beat.''',
  [cf('L102'), mf('l3:g.router', 'A crossbar of multiplexers joins the inputs to the output drivers (textbook).')],
  see=['lib.mux2'])

N('shire.meshstop.xing', 'shire.meshstop', 'Voltage and clock crossing (VCFIFO)', 5e-5, 'inferred',
  'order of magnitude: a FIFO of a few 512-bit entries with level shifters on every bit',
  '''The shire's cache runs at 0.705 V on its own clock, the network at 0.485 V and 400 MHz. Every bit that crosses is
  shifted in voltage and re-timed through two flip-flops into the other clock, so it cannot be caught half-changed.''',
  [mf('l2:l2.vc-fifo'), mf('l3:l3.hv-region'), mf('l3:g.crossing'),
   S('The ET cell library has level shifters in both directions (vclevel_shft_h2l, vclevel_shft_l2h) and VCFIFO '
     'memories and synchronisers (vcfifo_mem, vcfifo_wr_hiv_*, vcfifo_wr_lov_*, et_cdc_sync) for these crossings. ' + ERBIUM,
     RTL + 'libs/mems_and_fifos/ (file names)'),
   mf('scp:scp.lat-remote', None)],
  see=['lib.levelshift', 'lib.sync'],
  reuse=R('l2', 'xing', ['buildL2Xing', 'buildXing'], 'the crossing scale draws a VC FIFO cell with a level shifter (cross-coupled PMOS over an NMOS pair); the same drawing serves the mesh stop\'s 0.705 V to 0.485 V crossing with the rails relabelled'))

# ---- the shire cache ----
N('shire.cache', 'shire', 'Shire cache (four banks)', 1.5e-3, 'inferred',
  'order of magnitude: 4 MB of SRAM macros (about 1.1 mm2 of bitcells if HD 6T, more with periphery) and their logic',
  '''The shire's shared 4 MB of fast on-chip memory, in four banks. One memory, three uses: part of it is the shire's
  cache (L2), part a slice of the chip-wide cache (L3), and part a scratchpad programs manage themselves.''',
  [cf('shire.cache-geometry'), cf('shire.partition-m0'), mf('l3:l3.same-arrays'), mf('l2:l2.macro.count'),
   mf('l2:l2.bits'), mf('l2:l2.transistors'),
   I('At TSMC N7\'s 0.027 um2 high-density 6T cell, the shire cache\'s 40.3 Mbit of cells would take about 1.1 mm2, '
     'about 8% of the 13.9 mm2 shire tile, before the macros\' periphery; which bitcell the macros use is not documented.',
     'arithmetic on l2.bits and ' + IEDM16 + '; the bitcell is asked (u.bitcell)'),
   S('"These SRAM banks operate near the process-nominal supply voltage to allow higher density than the smaller '
     'caches within each core."', MICRO22 + ', p. 35')],
  reuse=R('l2', 'shire', ['buildL2Shire'], 'the L2 scene\'s shire scale draws the four banks under the crossbars; its bank scale is this node\'s child'))

N('shire.bank', 'shire.cache', 'Bank (one of four)', 7e-4, 'inferred',
  'order of magnitude: a quarter of the shire cache',
  '''Each bank is a complete cache of its own, with a queue of waiting requests, a pipeline and four sub-banks of
  memory. Consecutive 64-byte lines go to banks 0, 1, 2, 3 in turn, so the four work in parallel.''',
  [mf('l2:l2.banks'), mf('l2:l2.bank-select'), cf('shire.bank-queues'), mf('l2:l2.subbank-busy'),
   mf('l2:l2.lat.measured'), mf('l2:l2.bw.measured')],
  comp='banks', layer=1, tip='Shire cache bank N: details', instances=4,
  reuse=R('l2', 'bank', ['buildL2Bank'], 'direct: set inst.bank from the chip diagram\'s ctx.bank; request queue, read buffer, coalescing buffer, atomic unit, the 15-stage pipeline strip and the four sub-banks'))

N('shire.bank.reqq', 'shire.bank', 'Request queue', 1e-4, 'inferred', 'order of magnitude: 64 entries of address and state',
  '''A list of the requests the bank is working on, like a to-do list: 64 entries, each kept from its arrival until
  its data is back, so many misses can be outstanding at once.''',
  [mf('l2:l2.reqq'), mf('l2:l2.reqq.arb')], see=['lib.flipflop', 'lib.arbiter'])

N('shire.bank.rbuf', 'shire.bank', 'Read buffer', 6.5e-5, 'inferred',
  '8 x 512 bits = 4,096 flip-flops at about 1 um2 each (an N7 flip-flop, inference) is about 0.004 mm2, 65 um on a side',
  '''Eight recently read lines kept in registers next to the pipeline. A repeat read is served from here without
  waking the big memory panels: 36 cycles instead of 47.''',
  [mf('l2:l2.rbuf'), mf('l2:l2.rbuf.enabled'), mf('l2:l2.rbuf.storage')], see=['lib.flipflop', 'lib.mux2'])

N('shire.bank.dataq', 'shire.bank', 'Data queue', 1e-4, 'inferred', 'order of magnitude: 64 lines of 576 bits in a two-port register file',
  '''A holding area for the data of requests in flight: one 64-byte line per request-queue entry.''',
  [mf('l2:l2.dataq'), mf('l2:l2.cbuf')], see=['lib.sram8t'])

N('shire.bank.atomic', 'shire.bank', 'Atomic unit', 5e-5, 'inferred', 'order of magnitude: a 256-bit ALU',
  '''A small arithmetic unit beside the memory that performs read-modify-write operations (add, swap, min, max ...) on
  a word in one place, so that many cores can update a shared counter without racing.''',
  [mf('l2:l2.atomic'), mf('scp:scp.atomic')], see=['lib.adder', 'lib.flipflop'])

N('shire.bank.pipe', 'shire.bank', 'Bank pipeline', 1e-4, 'inferred', 'order of magnitude: the stage registers and control of one bank',
  '''The assembly line a request moves through, one stage per clock: allocate, arbitrate, read the tags, check them,
  compare, read the data, check it, send it. Registers between the stages hold each request's state.''',
  [mf('l2:l2.stages'), mf('l2:l2.stages.budget'), mf('l2:l2.clock-gating'), mf('l2:l2.perfmon')],
  see=['lib.flipflop', 'lib.icg'],
  reuse=R('l2', 'bank', ['buildL2Bank'], 'the bank scale\'s pipeline strip (STG: ag ad rqa tap ta ta0 ta1 te tc dap da da0 da1 de dc) is this node'))

N('shire.subbank', 'shire.bank', 'Sub-bank', 3.5e-4, 'inferred',
  'order of magnitude: four data panels of about 150 um plus a tag and a state macro',
  '''A quarter of a bank: its own tag memory (which lines are here), state memory (valid, dirty, LRU), and four data
  panels that together hold one 64-byte line per row.''',
  [mf('l2:l2.subbanks'), mf('l2:l2.sets'), mf('l2:l2.serial-lookup'), mf('l2:l2.panel-select')],
  reuse=R('l2', 'sub', ['buildL2Sub'], 'direct: a tag RAM, a tag-state RAM, four data panels, the ECC and the comparators, with the partition band of the level in view'))

N('shire.subbank.tag', 'shire.subbank', 'Tag RAM (1,024 x 116 macro)', 7e-5, 'inferred',
  '118,784 bits at 0.027 um2 is 0.0032 mm2 (57 um square) of cells, more with periphery; if HD 6T (inference)',
  '''A small memory that stores, for every set, which four lines (tags) are in it, so a lookup can tell hit from miss.''',
  [mf('l2:l2.tag-ram'), mf('l2:l2.macro.tag')], see=['lib.sram6t'])

N('shire.subbank.state', 'shire.subbank', 'Tag-state RAM (1,024 x 40, two-port)', 5e-5, 'inferred',
  '40,960 bits; a two-port cell is larger than a 6T cell (order of magnitude)',
  '''A memory read and written on every request: which lines are valid, dirty, locked or all zeros, and the order in
  which they were used. It has two ports so the read and the update happen in one pass.''',
  [mf('l2:l2.tag-state-ram'), mf('l2:l2.macro.state'), mf('l3:l3.zero-state')], see=['lib.sram8t'])

N('shire.panel', 'shire.subbank', 'Data panel (4,096 x 144 SRAM macro)', 1.5e-4, 'inferred',
  '589,824 bits x 0.027 um2 = 0.016 mm2 of cells; if the array is 1,024 rows x 576 columns of 114 x 237 nm cells it is '
  'about 117 x 137 um, some 150 um with its periphery (inference on the unconfirmed m4 reading and the HD cell)',
  '''The basic memory block: a compiled SRAM macro holding 4,096 words of 144 bits (128 data bits and 16 error-check
  bits). A shire has 64 of them; a line is one row across four panels. Inside: a grid of storage cells, with decoders
  down one side and sense amplifiers along the bottom.''',
  [mf('l2:l2.macro.data'), mf('l2:l2.data-ram'), mf('l2:l2.macro.vendor'), mf('l3:l3.vendor'), mf('scp:scp.panel-count'),
   mf('scp:scp.e-sram-line'), mf('l2:l2.macro.name-decode'), mf('l2:l2.storage-question')],
  reuse=R('l2', 'panel', ['buildL2Panel', 'buildPanel'], 'direct: buildPanel(L, ap, o) draws the documented shell (4096 x 144, 1PUHD, ICG, trims), the generic periphery and the dashed unknown geometry; o selects the band lit (L2 sets 0x280-0x2FF, L3 768-1023, scratchpad 0-639)'))

N('shire.panel.array', 'shire.panel', 'Bitcell array', 1.37e-4, 'inferred',
  '1,024 rows x 114 nm = 117 um tall, 576 columns x 237 nm = 137 um wide, if HD 6T and 4:1 column mux (inference)',
  '''The grid of storage cells, each holding one bit: rows are selected by wordlines, and each column's cells share a
  pair of bitlines that carry the value to the edge.''',
  [mf('l3:u.macro-geometry'), mf('l3:g.panel-read-count'), mf('scp:scp.g-half-select'),
   D('A 64-byte line read raises one wordline in each of 4 panels; 576 bits are sensed of the 2.36 million stored in the '
     'four panels.', 'arithmetic on l2.data-ram')],
  kind='circuit', see=['lib.sram6t'])

N('shire.panel.decoder', 'shire.panel', 'Row decoder and wordline drivers', 1.2e-4, 'inferred',
  'a strip the height of the array (inference)',
  '''Turns the row number into one active wordline: small logic gates decode the address, and a strong driver per row
  raises that row's wordline across all 576 columns.''',
  [mf('l3:g.read', 'Read: the row decoder\'s NAND/NOR gates select one wordline driver, which raises that wordline across '
      'the row (textbook, not an ET source).'), mf('scp:scp.g-assist')],
  kind='circuit', see=['lib.nand2', 'lib.inverter'])

N('shire.panel.colio', 'shire.panel', 'Precharge, column mux, sense amplifiers, write drivers', 1.4e-4, 'inferred',
  'a strip the width of the array (inference)',
  '''The circuits along the bottom edge. Before a read they charge every bitline pair high; a tiny difference then
  appears on the selected pair, and a sense amplifier turns it into a full 0 or 1. For a write, drivers force the
  bitlines.''',
  [mf('scp:scp.g-read-data'), mf('l3:g.write'), mf('l3:g.assist'), mf('scp:scp.trim-knobs'), mf('scp:scp.vmin-table'),
   mf('scp:scp.rail-margin')],
  kind='circuit', see=['lib.senseamp', 'lib.mux2', 'lib.latch'],
  reuse=R('scp', 'vmin', ['buildVmin'], 'the Vmin inset (RM table against the three rails) belongs here'))

N('shire.panel.ctrl', 'shire.panel', 'Clock gate and timing control', 3e-5, 'inferred', 'order of magnitude',
  '''A clock gate that lets the panel's clock run only for the cycles it is accessed, and the self-timing that decides
  when the sense amplifiers fire (the trims set its margins).''',
  [mf('l3:l3.clock-gating'), mf('l3:g.icg'), mf('l2:l2.trim')], kind='circuit', see=['lib.icg'])

N('shire.subbank.ecc', 'shire.subbank', 'ECC (SECDED) logic', 3e-5, 'inferred', 'order of magnitude: eight 72-bit XOR trees',
  '''Error-correcting code: 8 extra bits stored with every 64 data bits let the logic find and fix any single flipped
  bit, and detect two. It is trees of exclusive-OR gates.''',
  [mf('l2:l2.ecc'), mf('l3:g.ecc')], see=['lib.xor'])

N('shire.subbank.cmp', 'shire.subbank', 'Tag comparators', 2e-5, 'inferred', 'order of magnitude: four 23-bit comparators',
  '''Four comparators check the stored tags against the address at once; the one that matches is the hit way.''',
  [mf('l3:g.tag-compare')], see=['lib.xor', 'lib.nand2'],
  reuse=R('l1', 'cmp', ['buildL1Cmp', 'buildComparator'], 'buildComparator draws an XNOR per bit and an AND tree; pass 23 bits for the shire cache (33 in the L1)'))

# ---- the three partitions (selectable) ----
N('shire.l2', 'shire', 'L2 (a partition of the shire cache)', 1.5e-3, 'inferred',
  'spread over all 64 data panels: not a place of its own',
  '''The shire's own cache: 512 KB, where a core looks next when its small private cache misses. It is not a separate
  memory: it is 128 of the 1,024 sets in every sub-bank of the shire cache.''',
  [mf('l2:l2.partition.rows'), mf('l2:l2.lat.measured'), mf('l2:l2.e.level'), mf('l2:l2.leak')],
  comp='l2', layer=1, tip='L2, 512 KB: details', zoom_to='shire.bank',
  reuse=R('l2', 'shire', ['SCENES.l2 (all scales)'], 'the whole L2 scene is the inside of this part: shire, bank, sub-bank, panel with the L2 band, 6T cell, and the crossing'))

N('shire.l3', 'shire', 'L3 slice (a partition of the shire cache)', 1.5e-3, 'inferred',
  'spread over all 64 data panels: not a place of its own',
  '''This shire's 1 MB share of a cache the whole chip shares. It is the top quarter of the rows of the same panels; a
  line's home slice is chosen by address, so a core usually finds its line in another shire's slice.''',
  [mf('l3:l3.same-arrays'), mf('l3:l3.partition-m0'), cf('l3.latency'), mf('l3:l3.leakage')],
  comp='l3', layer=1, tip='L3 slice, 1 MB: details', zoom_to='shire.bank',
  reuse=R('l3', 'home', ['SCENES.l3 (home, hbank, sub, panel, cell)'], 'from the home-shire scale down; its chip scale (buildL3Chip, chipMap) duplicates the chip diagram\'s die and is not needed'))

N('shire.scp', 'shire', 'Scratchpad (a partition of the shire cache)', 1.5e-3, 'inferred',
  'spread over all 64 data panels: not a place of its own',
  '''2.5 MB of the same panels that programs read and write directly, with no cache in between: never a miss, and any
  shire can reach it by address.''',
  [mf('scp:scp.m0-rows'), cf('scp.size'), mf('scp:scp.always-hit'), cf('lat-scp-own'), cf('lat-scp-remote')],
  comp='scp', layer=1, tip='Scratchpad, 2.5 MB: details', zoom_to='shire.bank',
  reuse=R('scp', 'shire', ['SCENES.scp (shire, bank, panel, vmin, cell, hop, rep)'], 'from the shire scale down, with the scratchpad band lit; its hop and rep scales serve a remote access'))

# ---- UC block ----
N('shire.uc', 'shire', 'UC block', 2e-4, 'inferred', 'order of magnitude: counters, interrupt logic and an atomic ALU',
  '''Hardware for coordination: barrier counters (everyone waits until all have arrived), credit counters, interrupts
  between cores, and atomic operations that do not go through the cache.''',
  [cf('shire.composition', 'The uncacheable (UC) block holds fast local barriers, fast credit counters, inter-processor '
      'interrupts and global atomics.'), cf('sync-shire-barrier'), cf('hot-cost')],
  comp='uc', layer=1, tip='UC block: barriers, credits and atomics: details')

N('shire.uc.flb', 'shire.uc', 'Fast local barrier counters', 5e-5, 'inferred', '32 counters of 8 bits: a few hundred flip-flops',
  '''Thirty-two 8-bit counters. Each thread that reaches a barrier adds one; when the count reaches the number
  expected, everyone may go on.''',
  [S('The FLB extension provides 32 barrier counters, 8 bits wide, directly accessible by the threads in the shire, '
     'usable from user mode.', PRM + ', pdf p.327 (ch. 10)'),
   D('32 x 8 = 256 counter bits per shire.', 'arithmetic on the PRM\'s 32 x 8-bit counters')],
  see=['lib.adder', 'lib.flipflop'])

N('shire.uc.fcc', 'shire.uc', 'Fast credit counters', 5e-5, 'inferred', 'order of magnitude: 4 counters per minion',
  '''Per-thread counters that other threads can add credits to; a thread that reads its counter takes a credit, or
  waits until one arrives. A cheap way to say "your data is ready".''',
  [S('Each hart has two credit-counter CSRs (four per minion); remote harts increment them through the CREDINC0-3 '
     'ESRs of the target shire; a read with no credit blocks until one arrives.', PRM + ', pdf p.328 (ch. 11)')],
  see=['lib.adder', 'lib.flipflop'])

# ---- crossbar ----
N('shire.xbar', 'shire', 'Crossbar', 1.5e-3, 'inferred',
  'the specification routes the request crossbar "on top of all four banks": it spans the shire cache (l2.xbar.req)',
  '''The switch inside the shire that connects each group of eight cores to each of the four memory banks and the UC
  block. It is wide: 512 bits, a whole cache line, per transfer.''',
  [cf('shire.crossbar'), mf('l2:l2.xbar.req'), mf('l2:l2.xbar.rsp'), cf('ts-rt-fln')],
  comp='xbar', layer=1, tip='Crossbar: details')

N('shire.xbar.req', 'shire.xbar', 'Request crossbar', 1.5e-3, 'inferred', 'as the crossbar',
  '''Carries requests from the 5 clients (4 neighbourhoods and the RBOX) to the 4 banks and the UC block; each bank has
  a small waiting queue per neighbourhood and a round-robin arbiter.''',
  [mf('l2:l2.xbar.req')], see=['lib.mux2', 'lib.arbiter', 'lib.wire', 'lib.repeater'])

N('shire.xbar.rsp', 'shire.xbar', 'Response crossbar', 1.5e-3, 'inferred', 'as the crossbar',
  '''The same switch in reverse: lines coming back from the banks to the neighbourhood that asked.''',
  [mf('l2:l2.xbar.rsp')], see=['lib.mux2', 'lib.wire', 'lib.repeater'])

# ---- neighbourhood ----
N('shire.neigh', 'shire', 'Neighbourhood', 1.5e-3, 'inferred',
  'if 8 minions of about 0.25 mm2 plus the neighbourhood\'s logic make about 2.4 mm2, about 1.5 mm on a side (no floorplan published)',
  '''Eight minions that share one instruction cache and sit close enough for fast direct links. Esperanto grouped them
  so because 7 nm wires are slow over longer distances.''',
  [cf('neigh.composition'), cf('L115'), mf('l1:l1.lv-region'),
   S('"Physical design plays an important role in chip architecture as 7-nm wires are relatively slow. We found it '
     'convenient to group eight ET-Minion cores together before wire length became a problem."', MICRO22 + ', p. 34'),
   cf('neigh.coop-tload')],
  comp='neigh', layer=1, tip='Neighbourhood N: details', instances=4)

N('shire.neigh.icache', 'shire.neigh', 'Instruction cache (32 KB)', 1.2e-4, 'inferred',
  'four 512 x 144 macros of 73,728 bits each; order of magnitude',
  '''Holds the program's instructions for all eight minions. Its tags sit with the minions, but its data memory had to
  be placed in the shire's higher-voltage region, because those memory cells need the higher voltage.''',
  [cf('neigh.composition'), mf('l1:l1.icache-sram'),
   S('The memory cells of the I-cache data RAMs need an HV region while the neighbourhood is LV, so the data RAMs were '
     'moved into the Shire Channel; an L1 I-cache hit takes around ten cycles.', ICDESC + ', pdf p.16 (§4.2-4.3)'),
   I('If each 512 x 144 macro holds 512 x 128 data bits (8 KB) plus ECC, the 32 KB cache is four macros, 16 per shire.',
     'arithmetic on l1.icache-sram and neigh.composition; the 128 + 16 split is an assumption, so the result is inferred')],
  see=['lib.sram6t'])

N('shire.neigh.l0', 'shire.neigh', 'L0 micro instruction caches (two)', 8e-5, 'inferred',
  '2 x 16 x 512 bits = 16,384 bits of registers: about 0.01 mm2 (order of magnitude)',
  '''Two tiny caches, each serving four minions, that hold the last few instruction lines fetched, so most fetches never
  reach the 32 KB cache.''',
  [cf('neigh.composition'), S('The L0 microcache pipeline has five stages; each of the two (north and south) serves four '
     'minions over one shared bus.', ICDESC + ', pdf p.12 (§4.1)')],
  see=['lib.flipflop', 'lib.xor'])

N('shire.neigh.req', 'shire.neigh', 'Request path to the banks', 2e-4, 'inferred', 'order of magnitude',
  '''Where the eight minions' requests queue up: arbiters pick one request at a time, and per-bank queues carry them
  out of the low-voltage region into the shire's high-voltage channel.''',
  [mf('l2:l2.path.nbr-request'), mf('l2:l2.path.widths'), mf('l2:l2.vc-fifo'), cf('shire.neigh-link')],
  see=['lib.arbiter', 'lib.flipflop', 'lib.levelshift', 'lib.sync'],
  reuse=R('l2', 'xing', ['buildXing'], 'the per-bank VC FIFO and its level shifter; buildL2Shire already draws the 2:1 and 13:1 arbiters'))

N('shire.neigh.rsp', 'shire.neigh', 'Response path from the banks', 2e-4, 'inferred', 'order of magnitude',
  '''Lines coming back cross down to the minions' voltage, wait in a small fill queue, and reach the minion in two
  256-bit halves.''',
  [mf('l2:l2.nbr.response')], see=['lib.flipflop', 'lib.levelshift'])

N('shire.neigh.pmu', 'shire.neigh', 'Performance counters (PMU)', 3e-5, 'inferred', 'order of magnitude: 12 counters',
  '''Twelve event counters shared by the eight minions' threads.''', [cf('neigh.pmu')], see=['lib.adder', 'lib.flipflop'])

# ---- shire clocking and sensors (not selectable today) ----
N('shire.clock', 'shire', 'Shire clock generation (PLL, DLL, delay lines)', 2e-4, 'inferred',
  'order of magnitude: a digital PLL and a DLL are each on the order of 0.01-0.05 mm2 (inference)',
  '''Each shire makes its own clock: a phase-locked loop multiplies a reference up to the shire's frequency, and a
  delay-locked loop feeds the neighbourhoods a copy shifted by half a cycle, corrected for the delay of the wires that
  carry it.''',
  [cr('shire.clock'), S('Five clocks in a minion shire: ref_clock (24/100 MHz pin), step_clk (400-1,000 MHz from PLL4 in '
     'the I/O shire), the shire\'s local DPLL output (1,000 MHz design), the DLL output for the four neighbourhoods '
     '(shire_clock shifted 180 degrees), and clk__noc (500 MHz design, from PLL2).', SHIREDESC + ', pdf p.11-12 (§4.1, Table 2)'),
   S('Programmable clock delay lines: 25 ps steps (first specified at 100 ps), up to 1 ns, set by ESR, one per DLL '
     'feedback path.', DLLDOC + ', pdf p.4 (§2)'),
   cr('clock.dvfs-limits'), cf('minion.sleep-unused')],
  see=['lib.clocktree', 'lib.icg'])

N('shire.sensors', 'shire', 'On-die sensors (temperature, process, voltage)', 5e-5, 'inferred',
  'order of magnitude: one small analog sensor block',
  '''Each shire carries a temperature sensor, a process detector and voltage sense points, read by the service
  processor. The host sees only the average temperature.''',
  [cr('L120'), cr('temp-sensors'), cf('L121')], kind='circuit')

# =====================================================================================================================
# The minion (layer 1 part, layer 2 view)
# =====================================================================================================================
N('minion', 'shire.neigh', 'Minion', 5e-4, 'inferred',
  'if the 32 minions take one half to two thirds of the 13.9 mm2 tile, each is 0.22-0.29 mm2, about 0.5 mm on a side; no floorplan is published (l1.u-floorplan)',
  '''One of the chip's 1,088 small cores. It runs two threads, has an eight-lane vector unit that also runs the matrix
  instructions, and a 4 KB data cache, all on one low-voltage supply.''',
  [cf('minion.isa'), cf('chip.harts'),
   S('"The vector/tensor unit takes far more area than the integer pipeline"; "the entire ET-Minion, including its 4-KB '
     'L1 caches, operates on a single low-voltage power plane"; libraries were "recharacterized at 0.4 V".', MICRO22 + ', p. 33'),
   mf('l1:l1.voltage'), cf('e-awake'), cr('minion.power-awake', 'On a random-data fp32 matmul a minion draws about 26.5 mW above idle (aifoundry2).')],
  comp='minion', layer=1, tip='Minion M of neighbourhood N: details; Enter zooms in', instances=32,
  reuse=R('l1', 'minion', ['buildL1Minion'], 'the L1 scene\'s minion scale is a logical drawing of the same core (pipeline strip ID-EX-TAG-MEM-WB, DCache, TLB, miss handlers, replay queue, VPU port, TensorLoad unit, the rail band): adapt it or keep the chip diagram\'s buildMinion and link down into the L1 scene'))

N('minion.hart', 'minion', 'Hart (hardware thread)', 5e-4, 'none',
  'a thread is not a place: its registers are spread through the core and the vector unit',
  '''One of the minion's two threads. Each has its own program counter and registers, and the two take turns issuing
  instructions into the same pipeline; only thread 0 may issue most of the matrix instructions.''',
  [cf('minion.tensor-hart0'), cf('minion.vpu-regs'),
   S('When two harts are enabled and ready, the thread scheduler alternates between them round robin; a hart that cannot '
     'issue (a hazard) is skipped.', FEINT + ', pdf p.7 (§2.2.4)')],
  comp='hart', layer=2, tip='Hart T: details', instances=2, see=['core.irf', 'vpu.lane.vrf'])

N('core', 'minion', 'Integer pipeline (the core)', 2e-4, 'inferred',
  'smaller than the vector unit (Esperanto: the vector/tensor unit takes far more area); order of magnitude',
  '''The part that runs ordinary RISC-V instructions one at a time: fetch, decode, read registers, compute, access
  memory, write back. It also hands vector and matrix work to the vector unit.''',
  [cf('minion.isa'), S('Five integer stages: ID (dependencies, register read), EX (ALU; an extra GSC stage for gathers '
     'and scatters), TAG (DCache tags), MEM (DCache data), WB.', FEINT + ', pdf p.9 (§3.1-3.2)'),
   mf('l1:l1.pipeline'), cf('lat-l1')],
  comp='minion', layer=2, tip='The minion core: details')

N('core.fe', 'core', 'Front end (fetch, thread scheduler, decoder)', 8e-5, 'inferred', 'order of magnitude',
  '''Fetches instructions from the shared instruction cache, keeps a small buffer per thread, expands compressed
  instructions, picks which thread goes next, and decodes.''',
  [S('The front end (the document says 7 stages and describes stages 0-7): stage 0 sends the fetch, stages 1-5 wait a '
     'fixed time for the I-cache, stage 6 holds the double buffer and expands compressed instructions, stage 7 decodes '
     'and holds the thread scheduler. A taken '
     'branch requests its new PC in the TAG stage and kills the younger instructions; no branch predictor is described.',
     FEINT + ', pdf p.6-7 (§2.2) and p.14 (§3.2.4)'),
   S('RTL modules: frontend_thread_buffer, frontend_thread_sched, frontend_rvc_expander, frontend_top. ' + ERBIUM,
     RTL + 'shire/minion/frontend/')],
  see=['lib.flipflop', 'lib.mux2'])

N('core.irf', 'core', 'Integer register file', 4e-5, 'inferred',
  '4,096 latch bits at roughly 0.15-0.2 um2 each (an HD latch, inference) is 0.0006-0.0008 mm2: about 25-30 um before the read trees, some 40 um with them',
  '''The 32 integer registers of each thread: 64 entries of 64 bits, built from latches, with two read ports and one
  write port.''',
  [S('intpipe_rf instantiates rf_latch_2r_1w with WIDTH = 64 (XREG_SIZE) and ENTRIES = 2 threads x 32: a latch register '
     'file, 2 read ports and 1 write port. ' + ERBIUM, RTL + 'shire/minion/intpipe/intpipe_rf.v:43-50'),
   I('64 x 64 = 4,096 storage latches per minion; at about 10 transistors each, some 41,000 transistors before the read '
     'multiplexers.', 'arithmetic on intpipe_rf.v and the latch count of l1:g.latch-cell; the 10 transistors per latch '
     'are assumed, so the total is inferred')],
  see=['lib.latch', 'lib.mux2', 'lib.icg'],
  reuse=R('l1', 'lram/row/latch', ['buildL1Block', 'buildL1Row', 'drawReadTree', 'buildLatchCell'], 'the same latch register-file pattern as the L1 data array (per-row clock gates, latch rows, a read mux tree); a new instance with 64 rows and two read trees'))

N('core.alu', 'core', 'ALU', 4e-5, 'inferred', 'order of magnitude: a 64-bit adder, shifter and logic unit',
  '''The arithmetic-logic unit: adds, subtracts, compares, shifts and does bitwise logic on 64-bit numbers in one
  cycle.''',
  [S('RTL module intpipe_alu. ' + ERBIUM, RTL + 'shire/minion/intpipe/intpipe_alu.v'),
   G('A fast 64-bit adder is a parallel-prefix adder (generate and propagate signals combined in about log2(64) = 6 levels); '
     'a 64-bit barrel shifter is 6 levels of 2:1 multiplexers.', WH + ', ch. 11 (datapath subsystems: adders, shifters)')],
  see=['lib.adder', 'lib.mux2'])

N('core.muldiv', 'core', 'Multiplier and divider', 5e-5, 'inferred', 'order of magnitude',
  '''An iterative unit: it multiplies 8 bits of the multiplier per cycle (a 64-bit product in 8 cycles) and divides one
  bit per cycle (65 cycles), so it is small.''',
  [S('Loop counts: a 64-bit multiply takes 8 iterations (4 for 32-bit), a divide 65 (33 for 32-bit); each multiply '
     'iteration Booth-encodes 4 partial products (4 x 2 bits = 8 multiplier bits). ' + ERBIUM,
     RTL + 'shire/minion/intpipe/intpipe_mul_div_ctl.v:160-161; intpipe_mul_div_dp.v:41, 57-60')],
  see=['lib.booth', 'lib.fa', 'lib.flipflop'])

N('core.csr', 'core', 'Control and status registers', 3e-5, 'inferred', 'order of magnitude',
  '''Special registers that configure the core and start the matrix operations: a tensor instruction is a write to one
  of these, and runs by itself afterwards.''',
  [cf('minion.tensor-csrs')], see=['lib.flipflop'])

# ---- the vector unit ----
N('vpu', 'minion', 'Vector unit', 3.5e-4, 'inferred',
  'if it takes about half of a 0.25 mm2 minion, about 0.35 mm on a side (order of magnitude)',
  '''Eight identical lanes that do the same operation on eight numbers at once. Each lane can multiply and add every
  cycle; the matrix instructions run on these same lanes.''',
  [cf('minion.vpu'), cf('minion.vpu-pipeline'), cf('minion.vec-peak'), cf('e-fmadd-ps'), cf('minion.vector-rate')],
  comp='vpu', layer=2, tip='Vector unit: details')

N('vpu.lane', 'vpu', 'Lane (one of eight)', 1.2e-4, 'inferred', 'an eighth of the vector unit (order of magnitude)',
  '''One lane holds a 32-bit slice of every vector register, a fused multiply-add unit, two 8-bit integer
  multiply-add units, an integer unit and a unit for exponentials and logarithms.''',
  [cf('minion.vpu'), S('RTL: vpu_lane, vpu_lane_tima, txfma_7s, tima, trans_unit, vpu_rf. ' + ERBIUM, RTL + 'shire/minion/vpu/')])

N('vpu.lane.vrf', 'vpu.lane', 'Lane register file (64 x 32 bits, 3 read, 2 write ports)', 3e-5, 'inferred',
  '2,048 bits with five ports: order of magnitude',
  '''This lane's 32-bit slice of the 32 vector registers of each thread. Three read ports feed a multiply-add its three
  operands in one cycle; two write ports take a result and a load together.''',
  [S('The VRF: 64 entries x 32 bits (32 per thread), 3 read ports, 2 write ports (functional results and loads), thread '
     'ID as the address MSB, flopped inputs; "parameterized selection between ET-custom RF and synthesized SOL '
     '(sea-of-latches)".', VPUSPEC + ', pdf p.18 (§2.2.2)'),
   S('Its macro model is vpu_64x32_3r2w_vpurf. ' + ERBIUM, RTL + 'libs/macros/vpu_64x32_3r2w_vpurf.v'),
   D('8 lanes x 64 x 32 = 16,384 register bits per minion.', 'arithmetic on the VRF geometry'),
   U('Which of the two register files (ET-custom or sea of latches) the ET-SoC-1 taped out is not stated.', VPUSPEC + ', pdf p.18 (§2.2.2)')],
  see=['lib.latch', 'lib.mux2'])

N('vpu.lane.fma', 'vpu.lane', 'Fused multiply-add unit (TXFMA)', 6e-5, 'inferred',
  'order of magnitude; the multiplier array alone is some 20,000 transistors (see below)',
  '''Computes a x b + c on 32-bit floating-point numbers (or two 16-bit ones) in one pass, rounding only once. Inside
  are a multiplier array, an adder, and circuits that line up and normalise the exponents.''',
  [S('The TXFMA pipeline has 7 stages, the first used to clock-gate the operands when the unit is idle; it does 32-bit '
     'integer and FP32/FP16 arithmetic.', VPUSPEC + ', pdf p.18 (§2.2.3)'),
   cf('e-fmadd-ps'), cf('e-tfma-fp32'), cf('e-tfma-fp32-zeros'),
   cr('e-flip-model'),
   M('A random-data 16x16x16 tile clocks 2.5 million register bits and toggles 74 million multiplier-tree nets; zeros '
     'clock nothing, because the lane clock is withheld when an operand word is zero.',
     'docs/energy-manual/03-instructions.md:53-65 (flip model fitted on aifoundry2)')],
  see=['lib.booth', 'lib.cmp42', 'lib.adder', 'lib.flipflop'])

N('vpu.lane.fma.booth', 'vpu.lane.fma', 'Booth encoders and partial products', 3e-5, 'inferred', 'order of magnitude',
  '''Multiplication is many shifted additions. Radix-4 Booth encoding looks at the multiplier two bits at a time, halving
  the number of rows to add: 17 rows for a 32-bit multiplier.''',
  [S('Partial-product generators txfma_booth_ppg_32r4 (radix 4, 32 bits) with a 17th partial product '
     '(booth_fpp17). ' + ERBIUM, RTL + 'shire/minion/vpu/txfma_7s/txfma_booth_ppg_32r4*.v, txfmafrac_top.v:299-301'),
   D('17 partial products of about 33 bits: some 560 partial-product bits, each a small multiplexer choosing 0, +/-1 or '
     '+/-2 times the multiplicand.', 'arithmetic on the RTL\'s 17 radix-4 partial products'),
   G('Radix-4 (modified) Booth recoding halves the partial products.', WH + ', ch. 11 (datapath subsystems: multiplication)')],
  see=['lib.booth'])

N('vpu.lane.fma.tree', 'vpu.lane.fma', 'Compressor tree (Wallace tree of 4:2 compressors)', 4e-5, 'inferred',
  'order of magnitude',
  '''The 17 rows are added in a tree of small adders that turn every four bits of a column into two, level after level,
  until two rows remain for one final adder. This is most of the multiplier's area and most of its switching.''',
  [S('Modules txfma_wallace1, txfma_wallace2, txfma_4_2_compressor_array, txfma_4_2_compressor, txfma_csa. ' + ERBIUM,
     RTL + 'shire/minion/vpu/txfma_7s/'),
   I('Reducing 17 rows of about 33 bits to 2 takes on the order of 500 full-adder equivalents; at about 28 transistors per '
     'full adder, some 14,000 transistors, about 20,000 with the Booth selectors.',
     'estimate from the RTL\'s structure and the textbook full adder (' + RABAEY + ', ch. 11)'),
   cr('e-flip-model', 'Fitted energy per event on aifoundry2: 0.025 fJ per multiplier-tree net toggle, 0.80 fJ per other '
      'net toggle, 3.18 fJ per register bit clocked.')],
  see=['lib.cmp42', 'lib.fa'])

N('vpu.lane.fma.norm', 'vpu.lane.fma', 'Align, add, normalise, round', 3e-5, 'inferred', 'order of magnitude',
  '''Floating-point numbers must be lined up by their exponents before adding, and the result shifted back and rounded:
  a shifter, a wide adder, a leading-zero counter and a rounding adder.''',
  [S('Modules txfma_align_shf (alignment shifter), txfma_adder, txfma_lxd (leading-digit detection), txfma_norm_shf '
     '(normalisation shifter), txfma_rnd_adder (rounding adder), txfma_exp_special_detect. ' + ERBIUM,
     RTL + 'shire/minion/vpu/txfma_7s/')],
  see=['lib.adder', 'lib.mux2'])

N('vpu.lane.tima', 'vpu.lane', 'Integer multiply-add units (two TIMA)', 3e-5, 'inferred', 'order of magnitude',
  '''Two units that multiply 8-bit integers and add the products into 32-bit sums, four at a time each: the int8
  matrix work that makes the chip's peak eight times its fp32 rate.''',
  [cf('minion.vpu', 'Each lane has two integer multiply-add units, four int8 multiply-accumulates each.'),
   cf('e-tfma-int8'), S('Modules tima_top, tima_adder. ' + ERBIUM, RTL + 'shire/minion/vpu/tima/')],
  see=['lib.fa', 'lib.booth'])

N('vpu.lane.trans', 'vpu.lane', 'Transcendental unit (exp2, log2, reciprocal)', 3e-5, 'inferred', 'order of magnitude',
  '''Computes functions like 2^x and log2(x): it looks up three coefficients in small read-only tables and evaluates a
  quadratic, c0 + c1·m + c2·m², on the lane's own multiply-add unit.''',
  [S('Every transcendental is a quadratic approximation of the mantissa, m1 = c0 + c1 x m0 + c2 x m0^2: the coefficients '
     'sit in ROMs ("LUT latch-based") addressed by the input mantissa\'s bits, and a sequencer runs the arithmetic as '
     'micro-instructions on the lane\'s TXFMA; the ROM unit has 7 stages like the TXFMA.',
     VPUSPEC + ', pdf p.35 (§2.2.6) and p.61 (§2.3.7)'),
   S('ROM modules trans_{exp,log,rcp,rsqrt,sin}_rom_case_c0 and _c1c2. ' + ERBIUM, RTL + 'shire/minion/vpu/trans_unit/'),
   cf('minion.no-divide')],
  see=['lib.latch', 'lib.mux2'])

N('vpu.shsw', 'vpu', 'Shuffle, swizzle and bypass network', 8e-5, 'inferred', 'order of magnitude',
  '''Wires and multiplexers that move values between lanes (shuffles), and bypass paths that hand a fresh result to the
  next instruction before it is written back.''',
  [S('Stage F2 holds the TXFMA, the short-swizzle (SH-SW) unit, the mask and the transcendental sequencer; a bypass '
     'network forwards results from stages F3-F8 to the EX-stage inputs.', VPUSPEC + ', pdf p.15-17 (§2.1.3-2.1.7, §2.2.1)')],
  see=['lib.mux2', 'lib.wire'])

# ---- the tensor sequencer ----
N('tensor', 'minion', 'Tensor sequencer', 1e-4, 'inferred', 'order of magnitude: state machines and two 1 KiB buffers',
  '''Runs the matrix-multiply instructions: state machines that feed the eight lanes step after step for up to 512
  cycles from one instruction, with the operands in the L1 scratchpad and a stream buffer.''',
  [cf('minion.vec-peak'), cf('minion.tensor-shape'), cf('minion.tensorfma-546'),
   S('"A single tensor instruction can perform up to 32,000 operations"; tensor instructions "run for up to 512 cycles"; '
     'the integer pipeline sleeps meanwhile.', MICRO22 + ', pp. 33-34'),
   cf('e-tfma-fp32')],
  comp='tensor', layer=2, tip='Tensor sequencer: details')

N('tensor.fsm', 'tensor', 'Tensor state machines', 3e-5, 'inferred', 'order of magnitude',
  '''Counters and state machines that step through the rows and columns of a matrix tile, injecting one micro-operation
  into the lanes each cycle.''',
  [S('Modules vpu_tensorfma, vpu_tensorquant, vpu_tensorreduce, vpu_ml, vpu_uinst_decoder. ' + ERBIUM, RTL + 'shire/minion/vpu/'),
   cr('e-flip-model', 'The tensor state machines cost 1.81 mW per active minion whatever the data (fitted on aifoundry2).')],
  see=['lib.flipflop', 'lib.adder'])

N('tensor.tenb', 'tensor', 'TenB (stream buffer for B)', 3e-5, 'inferred', 'logically 1 KiB, "physically much smaller"',
  '''Where the B matrix streams in from the cache on its way to the lanes; the programmer sees 16 registers of 64 bytes,
  the hardware keeps only what is in flight.''',
  [cf('minion.tenb-tenc'), S('Modules vpu_tensorb_rf, vpu_tensora_rf, vpu_tensortmp_rf. ' + ERBIUM, RTL + 'shire/minion/vpu/')],
  see=['lib.latch', 'lib.flipflop'])

N('tensor.tenc', 'tensor', 'TenC (int32 accumulators)', 4e-5, 'inferred', '8,192 bits of register file: order of magnitude',
  '''Sixteen 64-byte registers that hold the running 32-bit sums of an integer matrix multiply.''',
  [cf('minion.tenb-tenc'), S('Macro model vpu_tensorc_rf_buffer_array. ' + ERBIUM, RTL + 'libs/macros/vpu_tensorc_rf_buffer_array.v')],
  see=['lib.latch'])

# ---- the L1 data cache ----
N('l1d', 'minion', 'L1 data cache (4 KB)', 1.2e-4, 'inferred',
  '32,768 latch bits at roughly 0.15-0.25 um2 each with their read trees is 0.005-0.008 mm2 (70-90 um), plus tags and TLB: order of magnitude',
  '''The minion's own small data cache, built from latches rather than SRAM, because it lives on the minion's low
  voltage. Three quarters of it is set aside as a scratchpad for the matrix instructions.''',
  [cf('minion.l1d'), mf('l1:l1.lram'), mf('l1:l1.why-latch'), mf('l1:l1.rail'), cf('lat-l1'), mf('l1:l1.e-vload'),
   mf('l1:l1.bits')],
  comp='l1d', layer=2, tip='L1 data cache: details',
  reuse=R('l1', 'dcache', ['buildL1Cache'], 'direct: tags as four latch RFs, comparators, the data array as 4 LRAM blocks x 2 macros, the set-map strip by mode'))

N('l1d.meta', 'l1d', 'Tags, valid and LRU bits', 3e-5, 'inferred', 'order of magnitude: 2,240 latch bits and 320 flip-flops',
  '''For each of the 64 lines: which address it holds (a 33-bit tag), its state, whether it is valid, and the order of
  use that picks the next line to replace.''',
  [mf('l1:l1.metadata'), mf('l1:l1.lru'), mf('l1:g.flipflop')], see=['lib.latch', 'lib.flipflop'])

N('l1d.cmp', 'l1d', 'Tag comparators (four)', 1e-5, 'inferred', '33 XNORs and an AND tree each: about 10 um (order of magnitude)',
  '''Four comparators check the four stored tags of a set against the address at once.''',
  [mf('l1:l1.phased'), mf('l1:g.compare')], see=['lib.xor', 'lib.nand2'],
  reuse=R('l1', 'cmp', ['buildL1Cmp', 'buildComparator'], 'direct'))

N('l1d.tlb', 'l1d', 'TLB (8 entries)', 2e-5, 'inferred', 'order of magnitude',
  '''A tiny table that translates virtual to physical addresses; the documents note virtual memory is unused on this
  silicon revision.''',
  [mf('l1:l1.tlb')], see=['lib.latch'])

N('l1d.mh', 'l1d', 'Miss handlers and replay queue', 3e-5, 'inferred', 'order of magnitude',
  '''When the cache misses, a miss handler (there are two) fetches the line while the instruction waits in an 8-entry
  replay queue; the core carries on with other work.''',
  [mf('l1:l1.mh'), mf('l1:l1.rq'), cf('minion.miss-handlers')], see=['lib.flipflop'])

N('l1d.data', 'l1d', 'Data array (4 LRAM blocks)', 9e-5, 'inferred', 'as the L1 minus its tags (order of magnitude)',
  '''The 4 KB of data: four latch-RAM blocks side by side, each 128 rows of 64 bits; a row across the four blocks is
  half a cache line.''',
  [mf('l1:l1.lram'), mf('l1:l1.lram-macros'), mf('l1:l1.lram-addr'), mf('l1:l1.bank-enables')],
  reuse=R('l1', 'dcache', ['buildL1Cache'], 'the data-array half of the data-cache scale'))

N('l1d.block', 'l1d.data', 'LRAM block (128 x 64)', 4.5e-5, 'inferred', '8,192 latch bits (order of magnitude)',
  '''One block: a write decoder and a clock gate per row on one side, 128 rows of 64 latches, and a read selector that
  picks one row onto the 64 output wires.''',
  [mf('l1:l1.latch-rf'), mf('l1:l1.icg-cells'), mf('l1:l1.lram-model')],
  reuse=R('l1', 'lram', ['buildL1Block'], 'direct'))

N('l1d.row', 'l1d.block', 'Row and read tree', 3.2e-5, 'inferred', '64 latches of about 0.5 um: about 32 um long (inference)',
  '''One row of 64 latches that all load together when the row's clock gate fires; for reading, each output bit is
  chosen from 128 rows by a tree of seven levels of two-way switches.''',
  [mf('l1:g.latch-read'), mf('l1:g.latch-write')], kind='circuit', see=['lib.latch', 'lib.icg', 'lib.mux2'],
  reuse=R('l1', 'row', ['buildL1Row', 'drawReadTree'], 'direct'))

N('l1scp', 'minion', 'L1 tensor scratchpad (3 KB)', 7e-5, 'inferred', '12 of the L1\'s 16 sets (order of magnitude)',
  '''Three quarters of the L1 cache, set aside before each program to hold a tile of matrix A for the matrix
  instructions. It is the same latch RAM, used without tags.''',
  [cf('minion.l1-modes'), cf('minion.l1-firmware'), mf('l1:l1.scp-impl'), mf('l1:l1.tensorload'), cf('minion.tensorload')],
  comp='l1scp', layer=2, tip='L1 tensor scratchpad: details', zoom_to='l1d.block',
  reuse=R('l1', 'lram', ['buildL1Cache', 'buildL1Block'], 'the same scales with sets 0-11 lit (the set-map strip already colours them)'))

N('etlink', 'minion', 'ET-Link port', 5e-5, 'inferred', 'order of magnitude: interface registers of 256-bit buses',
  '''The minion's doorway to the shire's memory: requests for lines its cache lacks, and evictions, leave here; lines
  come back in two 256-bit halves.''',
  [cf('minion.etlink-width'), cf('shire.neigh-link'), mf('l2:l2.path.miss'),
   S('ET-Link has a request and a reply channel, each handshaken by valid/ready pairs; a transfer happens only when both '
     'are high.', EXT + 'core-et/docs/ET-Link-Specification.pdf, pdf p.6 (§2)')],
  comp='etlink', layer=2, tip='ET-Link port: details', see=['lib.flipflop', 'lib.wire'])

N('fln', 'minion', 'Fast local network', 5e-4, 'inferred',
  'its edges join minions a minion-width or two apart: about 0.5 mm (inference)',
  '''Direct links between some pairs of minions in a neighbourhood, along a tree, for passing register values without
  going through the caches: 68 cycles round trip, against 114 through the crossbar.''',
  [cf('neigh.fln-edges'), cf('neigh.fln-latency-spec'), cf('L116'), cf('minion.one-ready-bit'), cf('minion.combine-free')],
  comp='fln', layer=2, tip='Fast local network: details', see=['lib.wire', 'lib.flipflop'])

# =====================================================================================================================
# The other tiles and parts of the die view
# =====================================================================================================================
N('master', 'die', 'Master shire and spare shire', 3.72e-3, 'inferred', 'one tile pitch (chip.hop-pitch)',
  '''Two more minion shires of the same design. The master runs the chip's own firmware, which starts each program on
  the compute shires; the spare waits, powered down, to replace a shire lost to a manufacturing defect.''',
  [cf('fw.grey-cells'), cf('chip.master-shire-id'), cf('chip.spare-shire-id'), cf('chip.compute-array')],
  comp='master', layer=0, tip='Master shire, shire 32 / Spare shire, shire 33, from the firmware\'s map: details',
  instances=2, zoom_to='shire')

N('memshire', 'die', 'Memory shire', 3.7e-3, 'inferred',
  'a cell of the 1.76 mm side strip (L09), and, if the four memory shires of a side sit in the four middle rows as their mesh stops do, one tile pitch tall: about 1.8 x 3.7 mm',
  '''One of the eight blocks that connect the chip to its memory chips. Each drives two 16-bit channels through a
  memory controller per channel and one physical interface (PHY) that sends and receives the signals on the pins.''',
  [cf('chip.memshires'), cf('L09'), mf('dram:dram.topo.controllers'), mf('dram:dram.topo.phy'), cf('L48'),
   cf('L46'), cf('dram.leg')],
  comp='memshire', layer=0, tip='Memory shire N: details', instances=8,
  reuse=R('dram', 'ms', ['buildMS'], 'direct: NoC port, the clock crossing, two uMCTL2 controllers, one PHY, pins; the up-to-63 cycles hatched'))

N('memshire.noc', 'memshire', 'NoC port and clock crossing', 1e-4, 'inferred', 'order of magnitude',
  '''Where requests arrive from the mesh (a whole line per beat) and cross from the network's 400 MHz clock to the
  memory controller's 933 MHz clock.''',
  [mf('dram:dram.topo.noc-port'), mf('dram:dram.ctl.clock')], see=['lib.sync', 'lib.levelshift'])

N('memshire.ctrl', 'memshire', 'Memory controllers (two uMCTL2)', 5e-4, 'inferred', 'order of magnitude',
  '''The controllers turn line requests into DRAM commands (open a row, read, write, refresh), reorder them to use open
  rows, and keep the timing rules of the memory chips.''',
  [mf('dram:dram.topo.controllers'), cf('dram.controller-policy'), cf('dram.row-bits'), cf('dram.counters')],
  see=['lib.flipflop', 'lib.xor'])

N('memshire.phy', 'memshire', 'DDR PHY (one for both channels)', 1e-3, 'inferred',
  'along the die edge in the 1.76 mm strip; order of magnitude',
  '''The analog front end: drivers that push each bit onto a pin and wire to the memory package, receivers that read
  the bits coming back, and delay lines that line up the timing.''',
  [mf('dram:dram.topo.phy'), mf('dram:dram.ctl.dbi'), mf('dram:dram.pwr.rails'), mf('dram:dram.topo.pll')],
  reuse=R('dram', 'phy', ['buildPHY'], 'direct'))

N('memshire.phy.dq', 'memshire.phy', 'One DQ pin driver', 2e-5, 'inferred',
  'a pin driver\'s transistors are wide (tens of fins): tens of um (inference)',
  '''The transistors that drive one data pin: one pulls the line up to the I/O voltage, one pulls it down to ground,
  sized to drive a trace on the circuit board.''',
  [mf('dram:gen.io')], kind='circuit', see=['lib.finfet'],
  reuse=R('dram', 'dq', ['buildDQ'], 'direct: an LVSTL driver and its receiver'))

N('dram', 'die', 'LPDDR4X package (memory chips)', 1.2e-2, 'inferred',
  'the card\'s part is not identified (dram.org.part); LPDDR4X packages are commonly about 10-15 mm on a side (inference)',
  '''The card's main memory, off the chip: four packages of 8 GB, each holding four 16-bit channels. Large and cheap,
  but a load takes about 300 cycles, and a byte costs some 30 times a byte from on-chip memory.''',
  [cf('dram.channels'), cf('dram.capacity'), cf('dram.rate-card'), cf('L47'), cf('dram.pkg-pairing'), mf('dram:dram.org.part')],
  comp='dram', layer=0, tip='LPDDR4X package, drawn beside memory shires X and Y (pairing inferred): details', instances=4,
  off_die=True,
  reuse=R('dram', 'chip', ['buildDramChip'], 'the card-and-chip scale draws the four packages beside the memory shires with the pairing dashed; the chip diagram already draws this level'))

N('dram.chan', 'dram', 'Channel (one DRAM die or die pair)', 7e-3, 'inferred',
  'a DRAM die is several mm on a side; order of magnitude',
  '''One 16-bit channel: 8 banks, each a large grid of rows; opening a row copies its 16,384 bits into a row of sense
  amplifiers, from which the 64-byte line is read.''',
  [mf('dram:dram.org.geometry'), mf('dram:dram.org.capacity')],
  reuse=R('dram', 'chan', ['buildChan'], 'direct, with the command and data timeline'))

N('dram.bank', 'dram.chan', 'Bank and subarrays', 2e-3, 'inferred', 'order of magnitude',
  '''A bank is split into many small tiles (mats) of cells between stripes of sense amplifiers and wordline drivers,
  because long wires would be too slow.''',
  [mf('dram:dram.org.die-internals'), mf('dram:gen.wordline'), mf('dram:gen.column')],
  reuse=R('dram', 'dbank', ['buildDBank'], 'direct'))

N('dram.cell', 'dram.bank', 'DRAM cell and sense amplifier', 1e-7, 'inferred',
  'DRAM cells are tens of nm apart, their capacitors far taller; order of magnitude only',
  '''A DRAM bit is one transistor and one tiny capacitor: charged is 1, empty is 0. The charge leaks away, so every row
  is read and rewritten every few tens of milliseconds (refresh).''',
  [mf('dram:gen.cell'), mf('dram:gen.sense'), mf('dram:gen.equalize'), mf('dram:gen.refresh')], kind='circuit',
  see=['lib.dram1t1c', 'lib.senseamp'],
  reuse=R('dram', 'dcell', ['buildDCell'], 'direct'))

N('pcie', 'die', 'PCIe shire', 3.72e-3, 'inferred', 'one tile pitch (chip.hop-pitch)',
  '''The chip's connection to the host computer: two PCIe controllers and an eight-lane physical interface, each lane
  sending 16 billion bits per second in each direction on a pair of wires.''',
  [cf('chip.pcie-shire'), cf('L28'), cf('pcie.negotiated'), cf('pcie.h2d')],
  comp='pcie', layer=0, tip='PCIe shire: details')

N('pcie.ctrl', 'pcie', 'PCIe controllers (two)', 1e-3, 'inferred', 'order of magnitude',
  '''Digital logic that packs reads and writes into PCIe packets, checks them, and retries lost ones.''',
  [cf('chip.pcie-shire')], see=['lib.flipflop'])

N('pcie.phy', 'pcie', 'PCIe PHY (8 lanes)', 2e-3, 'inferred', 'along the die edge; order of magnitude',
  '''Eight serialiser-deserialiser lanes: each turns parallel data into a 16 GT/s bit stream and back, with a clock
  recovered from the incoming bits.''',
  [cf('L28'), cf('pcie.negotiated'),
   G('A PCIe Gen4 lane carries 16 GT/s with 128b/130b encoding: 8 lanes give 8 x 16 x 128/130 / 8 = 15.75 GB/s per direction.',
     'PCI Express Base Specification 4.0 (16 GT/s, 128b/130b encoding); arithmetic as pcie.negotiated')])

N('pcie.lane', 'pcie.phy', 'One SerDes lane', 2.5e-4, 'inferred', 'order of magnitude',
  '''A transmitter that drives a differential pair of wires, and a receiver that equalises the smeared signal, recovers
  its clock and decides each bit.''',
  [G('A multi-gigabit lane: a serialiser and driver (with pre-emphasis) on the transmit side; on the receive side a '
     'continuous-time linear equaliser, decision-feedback equaliser, clock-and-data recovery and a deserialiser, clocked '
     'by a shared PLL.', WH + ', ch. 13 (I/O and high-speed links); no ET source describes the PHY\'s circuits')],
  kind='circuit', see=['lib.finfet', 'lib.senseamp'])

N('io', 'die', 'I/O shire', 3.72e-3, 'inferred', 'one tile pitch (chip.hop-pitch)',
  '''The chip's housekeeping block: four larger general-purpose cores, the service processor that starts the chip and
  manages its power and clock speed, the clock generators, the sensor controllers and the peripherals.''',
  [cf('L29'), cf('chip.io-shire'), cf('chip.maxions'), cf('chip.service-processor')],
  comp='io', layer=0, tip='I/O shire: details')

N('io.maxion', 'io', 'ET-Maxion cores (four)', 6e-4, 'inferred', 'order of magnitude; out-of-order cores are larger than minions',
  '''Four out-of-order RISC-V cores for general-purpose control. Unlike a minion, each looks ahead in the program and
  runs independent instructions early.''',
  [cf('chip.maxions'), G('An out-of-order core renames registers, holds decoded instructions in issue queues, executes '
     'them when their operands are ready and retires them in order from a reorder buffer.', WH + ' and standard texts; '
     'no ET source describes the ET-Maxion\'s microarchitecture')])

N('io.sp', 'io', 'Service processor', 5e-4, 'inferred', 'a minion core without vector unit, plus ROM and 1 MB SRAM (order of magnitude)',
  '''A single minion core without the vector unit that boots the chip, runs the power and clock governor and answers
  the host's management commands.''',
  [cf('chip.service-processor')], zoom_to='core')

N('io.pll', 'io', 'Clock generators (PLL0-PLL4)', 1e-4, 'inferred', 'a PLL is on the order of 0.01-0.05 mm2 (inference)',
  '''Phase-locked loops that multiply the 24 and 100 MHz reference oscillators up to the chip's clocks: the I/O shire's
  own, the peripherals', the network's 500 MHz (400 on these cards) and the minions' step clock.''',
  [S('PLL0: I/O shire core clocks; PLL1: fixed high-frequency device clocks; PLL2: the NoC clock; PLL4: a stepping clock '
     'for the minions.', PRM + ', pdf p.429'), cr('clock.design')],
  see=['lib.clocktree'])

N('io.pvt', 'io', 'PVT controllers (five)', 1e-4, 'inferred', 'order of magnitude',
  '''Controllers that read the temperature sensors, process detectors and voltage monitors spread over the die.''',
  [S('36 process detectors and 36 temperature sensors (one each per minion shire and the I/O shire) and 8 voltage-monitor '
     'blocks of up to 16 sense points (128 in all), read through five PVT controllers. (The manual\'s own count does '
     'not add up: 34 minion shires and the I/O shire make 35, and it does not say where the 36th sensor sits.)',
     PRM + ', pdf p.17-18 (§1.6, Table 1-6: "36 sensors. 1 PD in each minion/IO-Shire")'),
   cr('temp-sensors')])

N('io.periph', 'io', 'Peripherals, root of trust, 4 MB cache', 1e-3, 'inferred', 'order of magnitude',
  '''USB, I2C, SPI, UART and eMMC interfaces, a hardware root of trust, and another 4 MB of shared cache for the
  Maxions.''', [cf('L29'), cf('chip.io-shire')])

N('mesh', 'die', 'The mesh (network on chip)', 2.22e-2, 'derived',
  'the 6-column shire grid spans about 22.2 mm (L08); with the memory shires the mesh spans the die',
  '''The on-chip network: a grid of 44 stops, one per shire, joined by links to their neighbours. A message crosses one
  link per step (a hop); each hop adds 12 cycles to a round trip.''',
  [cf('mesh.grid'), cf('mesh-hop-lat'), cf('L104'), cf('mesh.voltage'), cf('mesh.clock'), cf('mesh-bit-mm-free'),
   S('"Shires are connected to each other via an on-chip mesh interconnect operated on its own low-voltage domain."', MICRO22 + ', p. 35')],
  comp='mesh', layer=0, tip='The mesh: details', zoom_to='shire.meshstop')

N('mesh.link', 'mesh', 'One hop\'s link', 3.72e-3, 'inferred', 'one tile pitch long (chip.hop-pitch)',
  '''The bundle of wires between two neighbouring stops, about 3.7 mm long: hundreds of parallel wires per direction,
  each broken into segments by repeaters.''',
  [cf('chip.hop-pitch'), mf('l3:l3.wire-energy'), cr('L88'),
   D('Measured on the mesh rail, routers included: 0.50-0.84 pF of switched capacitance per mm of travel, against 0.2-0.4 '
     'pF/mm estimated for a plain 7 nm repeated wire; most of the mesh\'s efficiency comes from its 0.485 V.',
     'docs/reports/data/2026-09-24-wire-energy/research/SYNTHESIS.md lines 38, 170, 255')],
  see=['lib.wire', 'lib.repeater'],
  reuse=R('l3', 'hop', ['buildL3Hop', 'buildHop'], 'the link segment of the hop scale'))

N('mesh.link.wire', 'mesh.link', 'A wire segment between repeaters', 2e-4, 'inferred',
  'repeaters every few hundred um (textbook); no ET source gives the spacing',
  '''One wire of the link, from one repeater to the next: a thin copper line whose resistance and capacitance slow the
  signal, which is why it is re-driven every few hundred micrometres.''',
  [mf('l3:g.wire-energy'), mf('l3:g.router', 'Each link is a bundle of wires broken by repeaters (inverter pairs) every '
      'few hundred microns (textbook).')],
  see=['lib.wire', 'lib.repeater'],
  reuse=R('l3', 'rep', ['buildL3Wire', 'buildWire'], 'direct: a repeater toggling with the data, and a level shifter, transistor by transistor'))

# ---- chip-wide infrastructure (not selectable today) ----
N('die.power', 'die', 'Power delivery (rails, grid, bumps)', 2.57e-2, 'inferred', 'spans the die',
  '''Power comes in through tens of thousands of solder bumps and spreads over a grid of thick metal. The chip has
  separate supplies: about 0.52 V for the minions, 0.705 V for the shire caches' memory, 0.485 V for the mesh.''',
  [cr('L12'), mf('l1:l1.voltage'), mf('l2:l2.rail.sram'), cf('mesh.voltage'), cf('L123'), cr('board.regulators'),
   cr('idle-rails')])

N('die.clock', 'die', 'Clock distribution', 2.57e-2, 'inferred', 'spans the die',
  '''A clock is a signal that ticks every cycle at every flip-flop. Each shire makes its own from a shared reference and
  spreads it through a tree of buffers; clock gates stop it where there is no work.''',
  [cr('clock.design'), cr('shire.clock'), cf('minion.sleep-unused'), mf('l1:l1.icg-cells')],
  see=['lib.clocktree', 'lib.icg'], zoom_to='shire.clock')

N('die.metal', 'die', 'The wiring stack (metal layers)', 5e-6, 'inferred',
  'a cross-section of the stack: a few um thick (inference; TSMC does not publish N7\'s stack heights)',
  '''Above the transistors lie a dozen or more layers of copper wires separated by insulator, the lowest ones finest
  (40 nm pitch), the top ones thick for power and long distances. Vias connect the layers.''',
  [cf('chip.process', 'TSMC 7 nm, over 24 billion transistors, 89 mask layers.'),
   O('TSMC N7: minimum metal pitch 40 nm (M0-M4, self-aligned double patterning).', WIKI7)],
  see=['lib.wire'])

N('host', 'die', 'Host and the PCIe link', 0.4, 'inferred', 'a desktop computer, some tens of cm (off the card)',
  '''The computer the card is plugged into: it sends programs and data over the PCIe link and starts them.''',
  [cf('pcie.negotiated'), cf('pcie.h2d')], comp='host', layer=0, tip='The host and the PCIe link: details',
  off_die=True, zoom_to='pcie.lane')

N('inferred', 'die', 'What the drawing infers (a key, not a part)', None, 'none', 'not a physical part',
  '''A key under the die, not a part of the chip: it lists what the drawing infers and what would settle it.''',
  [], comp='inferred', layer=0, tip='What the drawing infers, and what would settle it: details')

# =====================================================================================================================
# The circuit library: the components every part above is made of, down to the silicon
# =====================================================================================================================
N('lib', None, 'Circuit components (shared library)', None, 'none', 'not a place: the shared components',
  '''The small circuits every block above is built from, and what those are made of: transistors, a fin of silicon, and
  the crystal. Each part's "see" list points here.''', [])

N('lib.inverter', 'lib', 'Inverter (NOT gate)', 2.4e-7, 'inferred',
  'about 2 gate pitches (114 nm) wide in a 240 nm-tall N7 high-density cell (inference from ' + FUSE.split(',')[0] + ')',
  '''The simplest logic gate: one p-type transistor pulls the output up when the input is 0, one n-type pulls it down
  when the input is 1. Output is always the opposite of the input.''',
  [G('A static CMOS inverter is one PMOS and one NMOS transistor; energy per 0-to-1 output transition is about C x V^2.',
     WH + ', ch. 1, 2 and 5'),
   O('TSMC N7 high-density cells are 240 nm tall (6 tracks of 40 nm); high-performance cells 300 nm.', FUSE)],
  kind='circuit', see=['lib.finfet'])

N('lib.nand2', 'lib', 'NAND gate', 2.4e-7, 'inferred', 'about 3 gate pitches wide in a 240 nm cell (inference)',
  '''Output 0 only when both inputs are 1: two p-type transistors in parallel, two n-type in series. Any logic can be
  built from NAND gates.''', [G('A static CMOS 2-input NAND is 4 transistors.', WH + ', ch. 1')], kind='circuit',
  see=['lib.finfet'])

N('lib.xor', 'lib', 'XOR / XNOR gate', 3e-7, 'inferred', 'about 5 gate pitches wide (inference)',
  '''Outputs 1 when its inputs differ (XOR) or agree (XNOR): the gate of comparators, adders and error-checking codes.''',
  [G('A static CMOS XOR takes about 8-12 transistors depending on style.', WH + ', ch. 9 (combinational circuits)'), mf('l1:g.compare')],
  kind='circuit', see=['lib.finfet'],
  reuse=R('l1', 'cmp', ['buildComparator'], 'the XNOR-per-bit comparator'))

N('lib.mux2', 'lib', 'Two-way multiplexer', 3e-7, 'inferred', 'about 4-5 gate pitches wide (inference)',
  '''A switch that passes one of two inputs to the output, chosen by a select signal: trees of them read register files,
  and grids of them make crossbars.''',
  [G('A 2:1 multiplexer is two transmission gates (4 transistors) plus an inverter, or about 12 transistors in static CMOS.',
     WH + ', ch. 9 (combinational circuits)'), mf('l1:g.latch-read')], kind='circuit', see=['lib.finfet'],
  reuse=R('l1', 'row', ['drawReadTree', 'mux2'], 'the mux2 symbol and the 128:1 read tree'))

N('lib.arbiter', 'lib', 'Arbiter', 2e-6, 'inferred', 'order of magnitude: a few dozen gates',
  '''Decides who goes next when several requesters want one resource: round-robin arbiters rotate the priority so no one
  starves.''',
  [S('The ET library has priority, LRU and round-robin arbiters (arb_prio, arb_lru, arb_rr, rr_sel). ' + ERBIUM, RTL + 'libs/arbiters/'),
   mf('l2:l2.reqq.arb')], kind='circuit', see=['lib.nand2', 'lib.flipflop'])

N('lib.fa', 'lib', 'Full adder', 8e-7, 'inferred', 'about 12-16 gate pitches wide (inference)',
  '''Adds three bits and gives a sum bit and a carry bit: the brick of every adder and multiplier.''',
  [G('A static CMOS full adder takes about 28 transistors (the "mirror adder": 24 plus two output inverters).',
     RABAEY + ', ch. 11 (arithmetic building blocks); ' + WH + ', ch. 11')], kind='circuit', see=['lib.xor', 'lib.finfet'])

N('lib.cmp42', 'lib', '4:2 compressor', 1.5e-6, 'inferred', 'about two full adders (inference)',
  '''Takes four bits of a column (and a carry in) and gives two bits out: the step of a multiplier's adder tree that
  halves the rows at each level.''',
  [S('r42cmp: cout = (a^b)&c | ~(a^b)&a; sum = a^b^c^d^cin; carry = (a^b^c^d)&cin | ~(a^b^c^d)&d. ' + ERBIUM,
     RTL + 'libs/compressors/r42cmp.v'),
   G('A 4:2 compressor is equivalent to two full adders in series.', WH + ', ch. 11 (multiplication)')],
  kind='circuit', see=['lib.fa', 'lib.xor'])

N('lib.booth', 'lib', 'Booth encoder and partial-product selector', 5e-7, 'inferred', 'order of magnitude',
  '''Looks at three overlapping bits of the multiplier and chooses 0, +/-1 or +/-2 times the multiplicand for that
  row: two multiplier bits per row instead of one.''',
  [S('txfma_booth_ppg_32r4_norm decodes each 3-bit group into one of five selections (0, +1, +2, -2, -1). ' + ERBIUM,
     RTL + 'shire/minion/vpu/txfma_7s/txfma_booth_ppg_32r4_norm.v:13-25'),
   G('Radix-4 Booth recoding.', WH + ', ch. 11 (multiplication)')], kind='circuit', see=['lib.mux2', 'lib.xor'])

N('lib.adder', 'lib', 'Fast (parallel-prefix) adder', 3e-5, 'inferred', 'a 64-bit adder: tens of um (order of magnitude)',
  '''Adding 64-bit numbers quickly means not waiting for a carry to ripple through 64 positions: prefix adders compute
  all the carries in about six levels of logic.''',
  [G('Parallel-prefix adders (Kogge-Stone, Sklansky, Brent-Kung) compute carries in log2(N) levels of generate/propagate '
     'cells.', WH + ', ch. 11 (addition)')], kind='circuit', see=['lib.fa', 'lib.nand2'])

N('lib.latch', 'lib', 'Latch (drawn as the L1\'s storage cell)', 5e-7, 'inferred',
  'about 8-10 gate pitches wide in a 240 nm cell: about 0.1-0.15 um2 (inference)',
  '''A bit of memory made of logic: two inverters in a loop hold the value, and a clocked switch lets a new value in
  while the clock is high. The minion's caches and register files are made of these.''',
  [mf('l1:g.latch-cell'), mf('l1:l1.transistors'), mf('l1:l1.u-cell')], kind='circuit', see=['lib.inverter', 'lib.mux2'],
  reuse=R('l1', 'latch', ['buildL1Latch', 'buildLatchCell'], 'direct: a transmission-gate D latch, 10 transistors, D, CK, Q, QB'))

N('lib.flipflop', 'lib', 'Flip-flop (register bit)', 1e-6, 'inferred', 'about 16-20 gate pitches wide (inference)',
  '''Two latches back to back: the value changes only at the clock's rising edge. Pipelines are chains of logic between
  rows of flip-flops.''', [mf('l1:g.flipflop'), cr('e-flip-model', 'Fitted on aifoundry2: 3.18 fJ per register bit '
      'clocked in the tensor unit.')], kind='circuit', see=['lib.latch'],
  reuse=R('l1', 'dcache', ['flopSym'], 'the flip-flop symbol'))

N('lib.icg', 'lib', 'Clock gate (ICG)', 6e-7, 'inferred', 'about 10 gate pitches wide (inference)',
  '''A latch and an AND gate that stop the clock to a block that has nothing to do, so its flip-flops and clock wires
  draw no switching power.''', [mf('l3:g.icg'), mf('l1:l1.icg-cells'), mf('l1:g.latch-write')], kind='circuit',
  see=['lib.latch', 'lib.nand2'], reuse=R('l1', 'lram', ['icgSym'], 'the ICG symbol'))

N('lib.levelshift', 'lib', 'Level shifter', 1e-6, 'inferred', 'order of magnitude: it needs both supplies nearby',
  '''Translates a signal from one supply voltage to another (0.52 V minions to 0.705 V cache, 0.705 V to 0.485 V
  mesh), so the receiving transistors switch fully.''', [mf('scp:scp.g-level-shifter'), mf('l3:g.crossing')],
  kind='circuit', see=['lib.finfet'],
  reuse=R('l2', 'xing', ['buildXing'], 'direct: cross-coupled PMOS over an NMOS differential pair'))

N('lib.sync', 'lib', 'Synchroniser (two flip-flops)', 2e-6, 'inferred', 'two flip-flops (inference)',
  '''Two flip-flops in a row on the receiving clock: a bit that changed just as the clock ticked gets a full cycle to
  settle before anyone uses it.''', [mf('l3:g.crossing')], kind='circuit', see=['lib.flipflop'])

N('lib.senseamp', 'lib', 'Sense amplifier', 2e-6, 'inferred', 'about 4 SRAM columns wide (inference)',
  '''A tiny cross-coupled latch that, once fired, amplifies a difference of tens of millivolts between two bitlines into
  a full 0 or 1.''', [mf('scp:scp.g-read-data'), mf('dram:gen.sense')], kind='circuit', see=['lib.finfet'])

N('lib.sram6t', 'lib', '6T SRAM cell', 2.4e-7, 'inferred',
  '0.027 um2: 2 gate pitches (114 nm) x about 8 fin pitches (237 nm), if the macros use N7\'s high-density cell (inference)',
  '''The bit of the shire cache: two inverters in a loop hold the bit, and two access transistors connect it to a
  pair of bitlines when its row's wordline is raised. Six transistors per bit.''',
  [mf('l3:g.6t-cell'), O('TSMC N7 high-density 6T SRAM cell: 0.027 um2.', IEDM16), mf('l3:u.bitcell'),
   mf('l3:g.leakage'), mf('scp:scp.leak')], kind='circuit', see=['lib.inverter', 'lib.finfet'],
  reuse=R('l2', 'cell', ['buildL2Cell', 'buildCell', 'draw6T'], 'direct: read, write, half-select and leakage'))

N('lib.sram8t', 'lib', 'Two-port register-file cell (8T)', 3e-7, 'inferred', 'larger than the 6T cell (order of magnitude)',
  '''A 6T cell with a separate two-transistor read port, so a row can be read and another written in the same cycle.''',
  [mf('l2:l2.transistors', 'The two-port tag-state file is taken as an 8-transistor cell, the usual choice for such macros (generic).', 'generic'),
   mf('l2:l2.macro.state')], kind='circuit', see=['lib.sram6t'])

N('lib.dram1t1c', 'lib', 'DRAM cell (1T1C)', 1e-7, 'inferred', 'order of magnitude (a DRAM process, not TSMC N7)',
  '''One access transistor and one capacitor. The memory chips on the card are made this way, in a DRAM process, not in
  the logic process of the ET-SoC-1.''', [mf('dram:gen.cell')], kind='circuit',
  reuse=R('dram', 'dcell', ['buildDCell'], 'direct'))

N('lib.wire', 'lib', 'On-chip wire', 4e-8, 'outside',
  'the minimum metal pitch of TSMC N7, 40 nm: the finest wires are about 20 nm wide',
  '''A copper line embedded in insulator. Its capacitance, about 0.2 fF per micrometre, must be charged every time the
  signal changes; on long wires that costs more energy than the logic.''',
  [O('TSMC N7 minimum metal pitch 40 nm.', WIKI7),
   G('Most wires have about 0.2 fF/um of capacitance, nearly independent of the process generation.',
     'D. Harris, "Interconnect RC" lecture (https://pages.hmc.edu/harris/class/hal/lect4.pdf), as quoted in SYNTHESIS.md line 160'),
   S('"7-nm wires are relatively slow."', MICRO22 + ', p. 34'), cf('mesh-bit-mm-free')],
  kind='circuit', see=['lib.repeater'])

N('lib.repeater', 'lib', 'Repeater', 1e-6, 'inferred', 'a pair of wide inverters (order of magnitude)',
  '''A pair of strong inverters placed along a long wire to re-drive the signal, so that the delay grows with the length
  instead of its square.''', [mf('l3:g.wire-energy'),
   G('Delay of an unrepeated wire grows with the square of its length; optimally spaced repeaters make it linear.', WH + ', ch. 6 (interconnect)')],
  kind='circuit', see=['lib.inverter'], reuse=R('l3', 'rep', ['buildWire'], 'direct'))

N('lib.clocktree', 'lib', 'Clock tree', 3.72e-3, 'inferred', 'a shire\'s clock tree spans its tile',
  '''A tree of buffers that brings the clock from the PLL to every flip-flop at nearly the same instant; a delay-locked
  loop corrects the delay of the branch that feeds the neighbourhoods.''',
  [cr('shire.clock'), S('The DLL compensates the variable delays in the distribution network of shire_clock and '
     'neigh_clock (voltage, temperature, process).', DLLDOC + ', pdf p.3 (§1)'),
   G('Clock distribution by H-trees, grids or spines of buffers.', WH + ', ch. 13 (clocks, PLLs and DLLs)')],
  kind='circuit', see=['lib.inverter', 'lib.icg'])

N('lib.finfet', 'lib', 'FinFET transistor', 5.7e-8, 'outside',
  'one contacted gate pitch of TSMC N7: 57 nm',
  '''The switch everything is made of. A thin wall of silicon (the fin) runs from source to drain, and the gate wraps
  over it on three sides: a voltage on the gate lets current flow along the fin, or stops it.''',
  [O('TSMC N7: FinFET, contacted gate pitch 57 nm, fin pitch 30 nm.', WIKI7), O('TSMC N7 is TSMC\'s 4th-generation FinFET.', IEDM16),
   O('N7 high-density cells are 240 nm tall; high-performance cells 300 nm.', FUSE), cf('chip.process')],
  kind='device')

N('lib.gate', 'lib.finfet', 'Gate stack', 2e-8, 'outside',
  'gate length about 20 nm for a 7 nm-class process (IRDS); TSMC does not publish N7\'s',
  '''The gate: a metal electrode on an insulating layer only a few atoms thick (a high-k oxide), wrapped over the top
  and both sides of the fin.''',
  [O('7 nm-class gate length about 20 nm (IRDS 2021).', WIKI7IRDS),
   O('Comparable generations: TSMC 10 nm minimum Lg about 25 nm; Intel 10 nm 18 nm.', SILICONICS),
   G('A high-k metal gate: a hafnium-based oxide on a thin silicon-oxide interlayer under work-function metals; TSMC does '
     'not publish its N7 stack.', WH + ', ch. 3 (processing)')], kind='device')

N('lib.fin', 'lib.finfet', 'The fin (cross-section)', 5e-8, 'inferred',
  'about 6-7 nm wide and 45-50 nm tall, by analogy with TSMC 10 nm (6 nm, 44 nm) and Intel 10 nm (7 nm, 46-53 nm); TSMC does not publish N7\'s',
  '''A wall of crystalline silicon about 6 nm thick and some 50 nm tall, standing up from the wafer; fins sit 30 nm
  apart. Current flows along it under the gate.''',
  [O('TSMC N7 fin pitch 30 nm (self-aligned quadruple patterning).', WIKI7), O('TSMC 10 nm (Apple A11): fin width ~6 nm, '
     'functional gate height ~44 nm; Intel 10 nm: fin height 46-53 nm, width ~7 nm at half height.', SILICONICS),
   I('For N7, a fin about 6-7 nm wide and 45-50 nm tall, carrying about 2 x 45 + 6 = ~100 nm of effective channel width.',
     'inference from the two outside rows above')],
  kind='device')

N('lib.channel', 'lib.fin', 'Channel (the silicon under the gate)', 6e-9, 'inferred', 'the fin\'s width, about 6 nm (inference)',
  '''The strip of fin under the gate, about 6 by 20 by 45 nm, where the current flows: a few hundred thousand silicon
  atoms.''',
  [I('6 nm x 20 nm x 45 nm = 5,400 nm3 at 50 atoms per nm3 is about 270,000 silicon atoms.',
     'arithmetic on the fin and gate estimates above (inferred: the fin\'s 6 nm width and 45 nm height, the 20 nm '
     'gate length) and the atomic density below; a number built on inferred inputs is inferred')], kind='material')

N('lib.si', 'lib.channel', 'Silicon crystal', 5.43e-10, 'outside', 'one cubic unit cell: 0.543 nm (NIST CODATA)',
  '''Silicon atoms in a diamond lattice: each bonded to four neighbours at the corners of a tetrahedron. A 6 nm fin is
  only about 30 planes of atoms across.''',
  [O('Silicon lattice parameter a = 0.5431 nm.', CODATA),
   D('Diamond cubic: 8 atoms per cubic cell gives 8 / 0.5431^3 nm3 = 50 atoms per nm3 (5.0 x 10^22 per cm3); nearest '
     'neighbours are sqrt(3)/4 x a = 0.235 nm apart.', 'arithmetic on the lattice parameter'),
   I('Across a 6 nm fin whose sidewalls are (110) planes (the usual orientation on a (100) wafer, an assumption), the '
     '(220) planes are a / sqrt(8) = 0.192 nm apart: about 31 planes of atoms.', 'arithmetic on the lattice parameter, '
     'the inferred 6 nm fin and the assumed (110) sidewalls: inferred')],
  kind='material')

# =====================================================================================================================
# checks, children, outputs
# =====================================================================================================================
for i in ORDER:
    n = NODES[i]
    if n['parent']:
        assert n['parent'] in NODES, (i, n['parent'])
        NODES[n['parent']]['children'].append(i)
    for s in n.get('see', []): assert s in NODES, (i, s)
    if n.get('zoom_to'): assert n['zoom_to'] in NODES, (i, n['zoom_to'])
    for f in n['facts']:
        if ERBIUM in f['text']:
            f['text'] = f['text'].replace(' ' + ERBIUM, '').replace(ERBIUM, '').strip()
            f['caveat'] = 'erbium-rtl'
        assert f['label'] in LABELS and f['text'] and f['source'], (i, f)
        assert '<<' not in f['text'], (i, f)

roots = [i for i in ORDER if NODES[i]['parent'] is None]
sel = [NODES[i] for i in ORDER if 'selectable' in NODES[i]]
counts = {}
for i in ORDER:
    for f in NODES[i]['facts']: counts[f['label']] = counts.get(f['label'], 0) + 1

def depth(i):
    d = 0
    while NODES[i]['parent']: i = NODES[i]['parent']; d += 1
    return d

doc = {
    'meta': {
        'built': '2026-09-30', 'by': 'build_inside.py', 'worktree': 'the repository this file is in',
        'what': 'What is inside every part the chip diagram lets a reader select, as a tree down to circuit components, the FinFET, its fin and the silicon crystal.',
        'roots': roots, 'n_nodes': len(ORDER), 'n_facts': sum(counts.values()), 'fact_labels': counts,
        'labels': {
            'spec': 'an Esperanto/ET document, manual, firmware or RTL says so (RTL from core-et\'s Erbium branch is flagged in the text)',
            'measured': 'measured on the lab\'s cards (the repository\'s findings and facts)',
            'derived': 'arithmetic on spec or measured values',
            'inferred': 'our reading or estimate; no source states it',
            'outside': 'a published outside source about the process or this class of circuit',
            'generic': 'a textbook circuit or rule, not specific to this chip',
            'unknown': 'an open question: no source settles it'},
        'fields': {
            'size_m': 'characteristic linear size in metres: the width of the view that frames the part (null for a key or a group)',
            'size': 'label and note for size_m; most sub-shire sizes are order-of-magnitude inferences (no floorplan is published)',
            'selectable': 'the chip diagram\'s comp key, layer (0 die, 1 shire, 2 minion) and aria-label today',
            'see': 'the shared circuit nodes (under lib) this part is made of: where a zoom continues past the tree\'s leaves',
            'zoom_to': 'the node a double-click should continue into when the part is a view of another node (a partition, a key, a twin)',
            'reuse': 'the memory-levels page\'s scene, scale and builders that already draw this node',
            'fid': 'on a fact: chip:<id> (chip-diagram facts.json), chip-research:<id> (its research/ files), ml:<level>:<id> (memory-levels facts.json)',
            'caveat': 'on a fact: erbium-rtl = ' + ERBIUM_NOTE},
    },
    'nodes': [NODES[i] for i in ORDER],
}
json.dump(doc, open(os.path.join(OUT, 'inside.json'), 'w'), indent=1, ensure_ascii=False)

# ---- Markdown ----
def fmt_size(m):
    if m is None: return 'n/a'
    for unit, k in [('m', 1), ('cm', 1e-2), ('mm', 1e-3), ('um', 1e-6), ('nm', 1e-9)]:
        if m >= k * 0.999 or unit == 'nm':
            v = m / k
            return (f'{v:.3g} {unit}').replace('um', 'µm')
    return str(m)

def md_node(i, out):
    n = NODES[i]; d = depth(i)
    h = '#' * min(6, 3 + min(d, 3))
    title = f'{h} {n["name"]} `{i}`'
    out.append(title)
    bits = [f'**Size:** {fmt_size(n["size_m"])} ({n["size"]["label"]}: {n["size"]["note"]})']
    if 'selectable' in n:
        s = n['selectable']
        bits.append(f'**Selectable today:** comp `{s["comp"]}`, layer {s["layer"]}' + (f', {n["instances"]} instances' if n.get('instances') else '') + f'; aria-label "{s["tooltip"]}"')
    if n.get('off_die'): bits.append('**Off the die** (drawn in the chip view; on the card)')
    out.append('  \n'.join(bits))
    out.append('')
    out.append(n['blurb'])
    out.append('')
    for f in n['facts']:
        fid = f' [{f["fid"]}]' if f.get('fid') else ''
        src = f['source']
        if f.get('fid') and len(src) > 170: src = src[:170].rsplit(' ', 1)[0] + ' ... (full source in inside.json and the pages\' data)'
        cav = ', Erbium RTL' if f.get('caveat') == 'erbium-rtl' else ''
        out.append(f'- {f["text"]} *({f["label"]}{cav}{fid}; {src})*')
    tail = []
    if n['children']: tail.append('**Inside:** ' + ', '.join(f'`{c}`' for c in n['children']))
    if n.get('see'): tail.append('**Made of (see):** ' + ', '.join(f'`{c}`' for c in n['see']))
    if n.get('zoom_to'): tail.append(f'**Double-click continues into:** `{n["zoom_to"]}`')
    if n.get('reuse'):
        r = n['reuse']; tail.append(f'**Reuse:** memory-levels scene `{r["scene"]}`, scale `{r["scale"]}`, ' + ', '.join(f'`{b}`' for b in r['builders']) + f': {r["how"]}')
    if tail:
        out.append(''); out.append('  \n'.join(tail))
    out.append('')
    for c in n['children']: md_node(c, out)

MD_HEAD = open(os.path.join(OUT, 'research-inside.head.md')).read()
MD_TAIL = open(os.path.join(OUT, 'research-inside.tail.md')).read()

# ---- zoom ladders: the chains a reader would double-click through, with each step's magnification ----
LADDERS = [
    ('Compute, to the atom', ['die', 'shire', 'shire.neigh', 'minion', 'vpu', 'vpu.lane', 'vpu.lane.fma', 'vpu.lane.fma.tree',
                              'lib.cmp42', 'lib.fa', 'lib.xor', 'lib.finfet', 'lib.fin', 'lib.channel', 'lib.si']),
    ('Shire memory, to the atom', ['die', 'shire', 'shire.cache', 'shire.bank', 'shire.subbank', 'shire.panel',
                                   'shire.panel.array', 'lib.sram6t', 'lib.finfet', 'lib.fin', 'lib.channel', 'lib.si']),
    ('The L1, to the latch', ['minion', 'l1d', 'l1d.data', 'l1d.block', 'l1d.row', 'lib.latch', 'lib.inverter', 'lib.finfet']),
    ('A mesh hop, to the repeater', ['die', 'mesh', 'mesh.link', 'mesh.link.wire', 'lib.repeater', 'lib.inverter', 'lib.finfet']),
]
lad = []
for title, path in LADDERS:
    for a in path: assert a in NODES, a
    lad.append(f'**{title}.** ' + ' → '.join(f'{NODES[a]["name"].split(" (")[0]} ({fmt_size(NODES[a]["size_m"])})' for a in path))
    steps = [NODES[path[k - 1]]['size_m'] / NODES[path[k]]['size_m'] for k in range(1, len(path))]
    total = NODES[path[0]]['size_m'] / NODES[path[-1]]['size_m']
    lad.append(f'Steps: ' + ', '.join(f'{x:.3g}×' for x in steps) + f'; overall {total:.3g}× ({len(path) - 1} steps).\n')
MD_TAIL = MD_TAIL.replace('<!-- LADDERS -->', '\n'.join(lad))

out = []
# the selectable parts table
out.append('## 1. Every part the page lets a reader select today\n')
out.append('Read from `docs/reports/sources/chip-diagram.script.js` at 1980ebb: `buildChip` (layer 0), `buildShire` (layer 1) and '
           '`buildMinion` (layer 2) make each selectable part with `comp(parent, key, ctx, label)`, a `<g class="comp">` with '
           'role button and an aria-label; a click selects it and opens its panel (`COMPS[key]`, `LEADS[key]`, the facts '
           'of `D.comp[key]`), and every number or word in its drawing that carries `data-f` shows a source tooltip on hover. '
           'Double-click zooms today only from a compute shire (layer 0) and a minion (layer 1): `zoomInto`, lines 1434-1439.\n')
out.append('| Layer | comp key | Instances | aria-label (tooltip for screen readers) | Panel title | Node here |')
out.append('|---|---|---|---|---|---|')
PT = {'chip': 'ET-SoC-1', 'cshire': 'Shire N', 'master': 'Master shire (32) / Spare shire (33)', 'pcie': 'PCIe shire', 'io': 'I/O shire',
      'memshire': 'Memory shire N', 'dram': 'LPDDR4X', 'mesh': 'The mesh', 'host': 'Host and PCIe', 'inferred': 'Dashed, inferred, and what would settle it',
      'meshstop': 'Mesh stop', 'banks': 'Shire cache (bank N)', 'l2': 'L2', 'l3': 'L3 slice', 'scp': 'Scratchpad', 'uc': 'UC block', 'xbar': 'Crossbar',
      'neigh': 'Neighbourhood N', 'minion': 'Minion M · neighbourhood N', 'hart': 'Hart T', 'vpu': 'Vector unit', 'tensor': 'Tensor sequencer',
      'l1d': 'L1 data cache', 'l1scp': 'L1 tensor scratchpad', 'etlink': 'ET-Link port', 'fln': 'Fast local network'}
for n in sorted(sel, key=lambda n: (n['selectable']['layer'], ORDER.index(n['id']))):
    s = n['selectable']
    title = 'Minion M · neighbourhood N' if (s['comp'] == 'minion' and s['layer'] == 1) else ('Minion M · neighbourhood N (the core box)' if s['comp'] == 'minion' else PT.get(s['comp'], ''))
    out.append(f'| {s["layer"]} | `{s["comp"]}` | {n.get("instances", 1)} | {s["tooltip"]} | {title} | `{n["id"]}` |')
out.append('')
out.append(MD_TAIL.split('<!-- SPLIT:TREE -->')[0])
out.append('## 2. The tree\n')
out.append(f'{len(ORDER)} nodes under two roots: `die` (the parts, as the page\'s three layers nest them, plus the chip-wide '
           'power, clock and wiring that no layer draws yet) and `lib` (the shared circuit components each part is made of, '
           f'down to the silicon crystal). Facts: {sum(counts.values())}, labelled ' + ', '.join(f'{k} {v}' for k, v in sorted(counts.items(), key=lambda kv: -kv[1])) + '. '
           'Each node gives its size, a beginner\'s line or three, its facts with their labels and sources (a `[chip:...]` or '
           '`[ml:...]` tag names the fact in the pages\' data, which carries the full source), what it is made of, and what '
           'the memory-levels page already draws for it. The machine-readable copy is `inside.json` beside this file.\n')
for r in roots: md_node(r, out)
out.append(MD_TAIL.split('<!-- SPLIT:TREE -->')[1])
open(os.path.join(OUT, 'research-inside.md'), 'w').write(MD_HEAD + '\n'.join(out))
print('nodes', len(ORDER), 'facts', sum(counts.values()), counts, 'selectable', len(sel), 'max depth', max(depth(i) for i in ORDER))
