#!/usr/bin/env python3
"""Build ../outside.json: the chip diagram's levels OUTSIDE the chip, from the package to the observable universe.

Every level: id, name, size_m, blurb (a beginner's line, LEADS-style), facts [{text, source, kind}], image {file,
credit, licence, ...} | null, plus: parent (the next level out), optional, frame_m (a suggested view width),
size_kind / size_note, light (derived crossing times), draw (the imagery plan), child (where the next level in sits).

Kinds, as the page set labels them: measured (this project's own record), spec (a vendor document), derived
(arithmetic on the others, shown), inferred (read off a photo or reasoned, not documented), estimate, assumed,
outside source (a public reference), owner (the owner's own statement), hypothesis (not an observation).
All derived numbers are computed here, so the text and the numbers cannot drift apart.
"""
import json
import math
import os

HERE = os.path.dirname(os.path.abspath(__file__))
GEO = json.load(open(os.path.join(HERE, 'outside-geo.json')))
IMG = os.path.join(HERE, '..', '..', '..', 'ladder-img')   # the page's images, beside the built page

C = 299_792_458.0                 # m/s, exact (SI)
N_FIBRE = 1.4682                  # group index, Corning SMF-28e+ at 1550 nm
V_FIBRE = C / N_FIBRE
ER_FR4 = 4.0                      # ASSUMED: FR-4's relative permittivity, typical 3.8-4.5
V_PCB = C / math.sqrt(ER_FR4)
F_CLK = 600e6                     # Hz: the lab cards' usual minion clock (14-card-behaviour.md:338)
T_CLK = 1 / F_CLK
LY = 9_460_730_472_580_800.0      # m (IAU: Julian year x c)
PC = 3.0856775814913673e16        # m (IAU 2015 B2)
AU = 149_597_870_700.0            # m (IAU 2012 B2)
YEAR = 365.25 * 86400


def si_time(s, sig=3):
    def g(v):
        v = float(f'{v:.{sig}g}')
        return f'{v:,.0f}' if v >= 1e4 else f'{v:g}'
    for u, k in (('ns', 1e-9), ('µs', 1e-6), ('ms', 1e-3)):
        if s < 1000 * k:
            return f'{g(s / k)} {u}'
    if s < 120:
        return f'{g(s)} s'
    if s < 7200:
        return f'{g(s / 60)} min'
    if s < 3 * 86400:
        return f'{g(s / 3600)} h'
    if s < 3 * YEAR:
        return f'{g(s / 86400)} days'
    return f'{g(s / YEAR)} years'


def cycles(s):
    n = s / T_CLK
    if n < 1000:
        return f'{n:.2g}'
    for k, name in ((12, 'trillion'), (9, 'billion'), (6, 'million'), (3, 'thousand')):
        if n >= 10 ** k:
            v = float(f'{n / 10 ** k:.2g}')
            if k == 3:
                return f'{v * 1000:,.0f}'
            return (f'{v:,.0f}' if v >= 10 else f'{v:g}') + ' ' + name
    return f'{n:.2g}'


def sci(x, sig=2):
    e = int(math.floor(math.log10(abs(x))))
    m = float(f'{x / 10 ** e:.{sig}g}')
    return f'{m:g} × 10^{e}'


def light(d, fibre=False, pcb=False):
    out = {'distance_m': d, 'vacuum_s': d / C, 'vacuum': si_time(d / C), 'cycles_600MHz_vacuum': d / C / T_CLK}
    if fibre:
        out.update({'fibre_s': d / V_FIBRE, 'fibre': si_time(d / V_FIBRE), 'cycles_600MHz_fibre': d / V_FIBRE / T_CLK})
    if pcb:
        out.update({'pcb_s': d / V_PCB, 'pcb': si_time(d / V_PCB), 'cycles_600MHz_pcb': d / V_PCB / T_CLK})
    return out


# ------------------------------------------------------------------ sources (short keys -> full citations)
S = {
    'ds': 'Esperanto, ET-SoC-1 Preliminary Datasheet Rev 1.0 (github.com/aifoundry-org/et-man)',
    'card': 'Esperanto, "PCIe Dev Card (V3)", ET-PCIe-Dev-Card-V3.pdf (github.com/aifoundry-org/et-man)',
    'hc33': 'D. Ditzel, "Esperanto ET-SoC-1", Hot Chips 33 (2021), slides, as cited on the heatsink page '
            '(docs/reports/sources/esperanto-without-heatsink.body.html, section 1, ref [3])',
    'facts': 'docs/reports/data/2026-09-27-chip-diagram/facts.json',
    'cb14': 'docs/findings/14-card-behaviour.md',
    'claims': 'docs/findings/05-claims.md',
    'hs': 'the heatsink feasibility page, docs/reports/sources/esperanto-without-heatsink.body.html',
    'hosts': 'docs/reports/data/2026-09-27-pcie/hosts.txt',
    'nasa_earth': 'NASA NSSDCA, Earth Fact Sheet, https://nssdc.gsfc.nasa.gov/planetary/factsheet/earthfact.html',
    'nasa_moon': 'NASA NSSDCA, Moon Fact Sheet, https://nssdc.gsfc.nasa.gov/planetary/factsheet/moonfact.html',
    'nasa_nep': 'NASA NSSDCA, Neptune Fact Sheet, https://nssdc.gsfc.nasa.gov/planetary/factsheet/neptunefact.html',
    'si': 'BIPM, The International System of Units (SI Brochure, 9th ed., 2019): c = 299 792 458 m/s exactly',
    'iau_au': 'IAU 2012 Resolution B2: 1 au = 149 597 870 700 m exactly',
    'iau_ly': 'IAU: 1 light-year = c x one Julian year (365.25 d) = 9.4607 x 10^15 m',
    'iau_pc': 'IAU 2015 Resolution B2: 1 pc = 3.0857 x 10^16 m',
    'corning': 'Corning SMF-28e+ optical fibre, product information sheet: effective group index 1.4676 at 1310 nm, '
               '1.4682 at 1550 nm (copy at https://img-en.fs.com/file/datasheet/corning-smf-28eplus-33175.pdf)',
}


def F(text, source, kind):
    return {'text': text, 'source': source, 'kind': kind}


L = []

# ------------------------------------------------------------------ 1. the package
die_w = 25.6e-3
L.append({
    'id': 'package', 'name': 'The package', 'parent': 'card', 'optional': False,
    'size_m': 0.045, 'frame_m': 0.06, 'size_kind': 'spec',
    'size_note': '45.0 x 45.0 mm body (datasheet Fig. 9-1, p. 33).',
    'blurb': 'The chip itself is a thin slab of silicon about 2.6 cm across, mounted face down under this metal lid. '
             'The package fans its tens of thousands of microscopic connections out to 2,494 solder balls, big '
             'enough to solder onto the card.',
    'facts': [
        F('A 45.0 x 45.0 mm flip-chip ball-grid array with a 44.8 mm lid, at most 3.95 mm tall, with 2,494 solder '
          'balls of 0.50 mm diameter.', S['ds'] + ', Fig. 9-1, p. 33 (also ' + S['hs'] + ', section 1)', 'spec'),
        F('Most balls sit on a 0.80 mm grid; the drawing also dimensions a central region at 0.90-0.96 mm spacing. '
          'Columns are numbered 1-53 and rows lettered A-BR (skipping I, O, Q, S, X, Z), with many positions left '
          'empty: 2,494 balls in all.',
          S['ds'] + ', Fig. 9-1 (dimensions read off the bottom view)', 'spec'),
        F('More than 30,000 bumps join the die to the package substrate: the substrate fans them out to the 2,494 '
          'balls, about 12 bumps per ball.', S['hc33'], 'spec'),
        F('Under the lid: a die of 570 mm^2, about 25.6 x 22.2 mm. Where it sits under the lid is not documented; '
          'the drawing centres it.', S['facts'] + ' (chip.die-area, chip.die-dims)', 'inferred'),
        F('TSMC 7 nm, more than 24 billion transistors.', S['facts'] + ' (chip.process; Hot Chips 33, IEEE Micro 2022)',
          'spec'),
        F('The vendor photo\'s lid reads "ET-SoC-1 ... A0 ... 2217 ES TT TAIWAN": in the datasheet\'s scheme a date '
          'code (2217), an engineering sample (ES), assembled in Taiwan. "TT" is not explained there. The lab cards\' '
          'own markings are not recorded.', S['card'] + ', p. 2 (photo); ' + S['ds'] + ', Table 10-1, p. 34', 'inferred'),
        F('The datasheet gives no thermal ratings for the package (section 9.1 is a placeholder).', S['ds'] + ', §9.1',
          'spec'),
        F(f'Light crosses the die (25.6 mm) in {si_time(die_w / C, 2)}, about a twentieth of one 600 MHz clock tick; in '
          f'one tick light goes {C * T_CLK * 100:.0f} cm.', S['si'] + '; the clock: ' + S['cb14'] + ':338', 'derived'),
    ],
    'light': light(die_w),
    # (no image: the level is drawn from Fig. 9-1; the card level's photo shows the lid)
    'image': None,
    'draw': 'Drawn SVG from Fig. 9-1: top view (45.0 mm body, 44.8 mm lid), a cut-away side view (lid, TIM, die, '
            'bumps, substrate 1.6 mm, balls 0.50 mm, 3.95 mm total) and the bottom view\'s ball grid at its 0.80 mm '
            'pitch (depopulated as in the figure; the exact map is there). The die (25.6 x 22.2 mm) as a dashed '
            'rectangle under the lid, labelled "position assumed". Scale bar: 10 mm. The lid photo crop can fade in '
            'as the camera arrives.',
    'child': {'id': 'chip', 'box_mm': [9.7, 11.4, 35.3, 33.6],
              'note': 'the die, centred under the 45 mm body (assumed)'},
})

# ------------------------------------------------------------------ 2. the card
card_w = 0.1676
L.append({
    'id': 'card', 'name': 'The PCIe card', 'parent': 'host', 'optional': False,
    'size_m': card_w, 'frame_m': 0.19, 'size_kind': 'spec',
    'size_note': '6.6 x 4.4 in (167.6 x 111.8 mm), the dev card\'s assembly drawing (p. 3).',
    'blurb': 'A circuit board about 17 by 11 cm that plugs into the computer. Around the chip sit four memory chips '
             'holding its 32 GB, and the regulators that turn the computer\'s 12 volts into the half a volt its cores '
             'run on.',
    'facts': [
        F('6.6 x 4.4 in (167.6 x 111.8 mm); a PCIe x16 card edge carrying an x8 PCIe Gen 4 link; the chip soldered '
          'down, no socket.', S['card'] + ', pp. 1 and 3', 'spec'),
        F('On all four lab cards the link runs at 16 GT/s on 8 lanes: 15.75 GB/s each way after coding. Measured '
          'host-to-card DMA: 12.5-12.6 GB/s; card to host 10.4-10.5 GB/s.',
          S['hosts'] + ' (the link speed and width of all four cards); ' + S['claims'] + ':550-552 (E50: the DMA rates, '
          'on three cards)', 'measured'),
        F('Four LPDDR4X memory packages, 256 bits wide in all (16 channels of 16 bits), 32 GB: each package serves '
          'two of the chip\'s eight memory shires.', S['facts'] + ' (L47, dram.channels); ' + S['card'] + ', p. 1',
          'spec'),
        F(f'Peak memory rate on these cards: 256 bits x 3,733 MT/s = {256 * 3733e6 / 8 / 1e9:.1f} GB/s, the firmware\'s '
          f'933 MHz mode, which every lab card runs; the datasheet\'s 4,266 MT/s would give {256 * 4266e6 / 8 / 1e9:.1f} '
          'GB/s. Tensor loads from memory have been measured at 75 GB/s.',
          S['facts'] + ' (dram.rate-card: the firmware hard-codes 3,733 MT/s on every card; dram.peak-card; L47: the '
          'datasheet\'s 4,266 Mb/s per pin); ' + S['claims'] + ':155 (E15)', 'derived'),
        F('Each memory package is about 15 mm square on the vendor photo, which shows SK hynix parts (a second photo '
          'in the same document shows Micron parts). Which maker\'s DRAM the lab cards carry is not recorded.',
          S['card'] + ', pp. 2, 8 and 10 (photos)', 'inferred'),
        F('Power arrives as 12 V at the card edge: at most 7.3 A, 88 W. The highest draw on record is 87.8 W; the cards '
          'idle at about 19-36 W, depending on the card and its temperature.',
          S['card'] + ', p. 5 (power tree); ' + S['cb14'] + ':138, 339', 'spec, measured'),
        F('The cores run at about 0.52 V at 600 MHz, 23 times lower than the 12 V input, so the current is about 23 '
          'times higher: a Texas Instruments TPSM831D31 supplies the cores (3 phases, up to 120 A) and the on-chip '
          'network (1 phase, 40 A). Its four phases are the four large inductors marked "R15" on the photo.',
          S['card'] + ', p. 1 (key voltage regulators) and p. 2 (photo); ' + S['claims'] + ':34 (E9)',
          'spec, measured, inferred'),
        F('An Analog Devices LTM4680 module (up to 60 A) supplies the SRAM rail; smaller FS1406 regulators the '
          'memory, PCIe, I/O and other rails; an LTC4218 hot-swap switch with a 1 mΩ sense resistor measures the '
          'card\'s input current for the power readings.', S['card'] + ', pp. 1, 4', 'spec'),
        F('A small microcontroller (Microchip ATSAMD20, the "PMIC micro") reads the 12 V input and three regulators '
          '(cores, network, SRAM); the other rails have set points only.',
          S['card'] + ', p. 4 (block diagram); ' + S['facts'] + ' (board.meters)', 'spec, measured'),
        F('Also on the board: 64 GB of eMMC flash (a Kingston part on the photo), an FTDI UART-to-USB bridge, JTAG, '
          'DIP switches that set the boot options, and a fan header (P1).', S['card'] + ', pp. 1-3', 'spec, inferred'),
        F('Which heatsink the lab cards carry, and whether each has a fan, is not recorded; the vendor photo shows '
          'the card bare.', S['hs'] + ', section 1 ("Not recorded")', 'note'),
        F(f'A signal in the board\'s copper travels at about half the speed of light (c/√εr, εr ≈ 4 for FR-4), so '
          f'crossing the card takes about {si_time(card_w / V_PCB)}: two-thirds of a 600 MHz clock tick.',
          'physics: a buried trace\'s delay is √εr / c; εr = 4 is ASSUMED (typical FR-4 is 3.8-4.5), so the result is '
          'inferred', 'inferred'),
    ],
    'light': light(card_w, pcb=True),
    'image': {'file': 'card.webp', 'px': [720, 479], 'bytes': 75178, 'px_per_mm': 4.296,
              'credit': 'Esperanto Technologies, "PCIe Dev Card (V3)" (ET-PCIe-Dev-Card-V3.pdf, p. 2), '
                        'published in github.com/aifoundry-org/et-man',
              'licence': 'Apache License 2.0 (the et-man repository\'s LICENSE)',
              'licence_url': 'https://github.com/aifoundry-org/et-man/blob/main/LICENSE',
              'note': 'The vendor\'s photo of a dev card (SK hynix DRAM, no heatsink), not a lab card; transparent '
                      'background. The photo\'s lid measures 44.8 mm at this scale, which checks the 6.6 in width.',
              'hotspots_px': {'lid (the package)': [275, 161, 467, 356],
                              'LPDDR4X U11': [164, 167, 231, 234], 'LPDDR4X U20': [164, 286, 231, 353],
                              'LPDDR4X U12': [511, 170, 578, 237], 'LPDDR4X U21': [511, 286, 578, 353],
                              'TPSM831D31 and its four inductors (cores, network)': [253, 24, 461, 117],
                              'LTM4680 (SRAM rail)': [487, 65, 557, 132],
                              'DIP switches (boot options)': [619, 141, 674, 388],
                              'PCIe card edge': [196, 455, 662, 479]}},
    'draw': 'The photo, with SVG hotspots over it (the boxes above, in the 720 x 479 copy\'s pixels; 4.30 px per mm) '
            'and a 5 cm scale bar. Heatsink: not drawn as a fact; at most a dashed outline marked "heatsink (which one '
            'is not recorded)".',
    'child': {'id': 'package', 'box_px': [275, 161, 467, 356], 'box_mm': [64.0, 37.5, 108.7, 82.9]},
})

# ------------------------------------------------------------------ 3. the host machine
host_w = 0.45
L.append({
    'id': 'host', 'name': 'The host computer', 'parent': 'rack', 'optional': False,
    'size_m': host_w, 'frame_m': 0.5, 'size_kind': 'estimate',
    'size_note': 'An open frame holding an ATX board (30.5 x 24.4 cm) and its power supply: about 45 cm across '
                 '(estimate from the photo; the frames\' make is not recorded).',
    'blurb': 'An ordinary desktop PC built on an open frame instead of in a case. The card sits in one of its slots '
             'and gets its programs, its data and its power from it.',
    'facts': [
        F('The lab\'s three hosts: aifoundry1, an Intel Core i7-11700K (8 cores) with 128 GB; aifoundry2, a Core '
          'i5-11600 (6 cores) with 64 GB; aifoundry3, an i7-11700K with 32 GB on a single memory channel.',
          S['cb14'] + ':348; the et-lab-manifest records', 'measured'),
        F('aifoundry2\'s motherboard is a Gigabyte Z590 AORUS MASTER, an ATX board of 30.5 x 24.4 cm. The other two '
          'hosts\' BIOS versions (F5, F6) follow Gigabyte\'s naming, but their board models are not recorded.',
          'the host\'s DMI table (/sys/devices/virtual/dmi/id, read 30 Sep 2026); Gigabyte, Z590 AORUS MASTER '
          'specifications (gigabyte.com); ' + S['cb14'] + ':348', 'measured, spec, inferred'),
        F('aifoundry1 holds two ET cards, the other hosts one each.', S['hosts'], 'measured'),
        F('Each card\'s 8-lane PCIe 4.0 link goes straight to a root port on the CPU, which has 20 PCIe 4.0 lanes.',
          S['hosts'] + ' (root_port 00:01.x, the CPU\'s own PCIe ports on this platform: inferred); Intel, Core '
          'i7-11700K specifications (intel.com)', 'measured, inferred, spec'),
        F('The host CPUs are made in Intel\'s 14 nm process; the i7-11700K is rated at 125 W base power and may draw '
          'up to 251 W in turbo (its PL2), the i5-11600 at 65 W base. The whole ET card, at most 88 W, draws less than '
          'the bigger CPU\'s base power, and about a third of its turbo peak.',
          'Intel, Core i7-11700K and Core i5-11600 specifications (intel.com: 125 W and 65 W base power); the '
          'i7-11700K\'s 251 W maximum turbo power (PL2) as listed by cpu-monkey.com and techreviewer.com; '
          + S['card'] + ', p. 5', 'spec'),
        F('The host copies memory at 17.4 / 9.2 / 21.4 GB/s (aifoundry2 / 3 / 1); a program\'s staged copy to the '
          'card is limited by both that and the link: 5.2-7.8 GB/s.', S['claims'] + ':553 (E50)', 'measured'),
        F('The owner\'s photo shows open-air frames with tower coolers and EVGA and MSI power supplies; several '
          'boards carry Gigabyte AORUS logos.', 'the owner\'s rack photo (30 Sep 2026)', 'inferred'),
        F('A standard ATX power supply is 150 mm wide, 86 mm high and 140 mm deep.',
          'Intel, ATX12V Power Supply Design Guide (version 2.x), physical dimensions of the standard ATX12V supply',
          'outside source'),
    ],
    'light': light(host_w),
    # (no image: the level is a drawing of an ATX board; the rack level's photo shows the machines)
    'image': None,
    'draw': 'Drawn SVG, top view, to scale: an ATX board 305 x 244 mm (ATX spec; aifoundry2\'s board is exactly '
            'this) with the CPU socket and a tower cooler, four DIMM slots, the PCIe slots, and the ET card '
            '(167.6 x 111.8 mm) standing in a slot, drawn edge-on with a side elevation inset; an ATX power supply '
            '150 x 86 x 140 mm beside it. Scale bar 10 cm. The photo crop can cross-fade in from the rack level.',
    'child': {'id': 'card', 'note': 'the card in the board\'s first x16 slot (drawn; the slot used on each host is '
                                    'not recorded beyond its root port)'},
})

# ------------------------------------------------------------------ 4. the rack
rack_w = 1.5
L.append({
    'id': 'rack', 'name': 'The rack', 'parent': 'studio45', 'optional': False,
    'size_m': rack_w, 'frame_m': 1.8, 'size_kind': 'estimate',
    'size_note': 'About 1.5 m wide: five open frames side by side on each shelf (estimate from the photo; common '
                 'wire-shelving widths are 48-72 in). The rack\'s make and size are not recorded.',
    'blurb': 'A wire shelving rack holding about ten open-frame machines on two shelves. The lab\'s three machines, '
             'with their four ET cards, are among them; which ones is not recorded.',
    'facts': [
        F('About ten open-frame machines on two shelves, five to a shelf, some partly hidden.',
          'the owner\'s rack photo (30 Sep 2026), counted', 'inferred'),
        F('The lab\'s machines are in this rack; which three of them is not recorded.', 'the owner (30 Sep 2026)',
          'owner'),
        F('Power supplies read on the photo: EVGA 650 GS and 1000 GS, MSI MPG A750GF (650, 1,000 and 750 W).',
          'the owner\'s rack photo', 'inferred'),
        F('A "KVM#8" label and a keyboard on the shelf above: one keyboard and screen are shared between machines.',
          'the owner\'s rack photo', 'inferred'),
        F(f'Light crosses the rack in {si_time(rack_w / C)}, about {rack_w / C / T_CLK:.0f} of the chip\'s clock ticks '
          f'at 600 MHz.', S['si'], 'derived'),
        F('In the page\'s copy of the photo the machines\' tape labels are blurred: they carry host names and network '
          'addresses, which the repository keeps out of public pages.', 'AGENT.md §10', 'note'),
    ],
    'light': light(rack_w),
    'image': {'file': 'rack.webp', 'px': [1000, 988], 'bytes': os.path.getsize(
        os.path.join(IMG, 'rack.webp')),
        'credit': 'Photo: the page\'s author (the repository\'s owner), 2026; machine labels blurred',
        'licence': 'the author\'s own photo, used on his page at his request; no open licence stated',
        'note': 'From rack-photo-original.webp (1500 x 1429, no EXIF or GPS): 9 tape labels pixelated, the 53-px black '
                'band on the left cropped, resized to 1000 px, WebP q70, no EXIF/XMP/ICC. make_rack_photo.py.'},
    'draw': 'The photo. A scale bar would be an estimate: if drawn, label it "about 50 cm (estimated)". Optional: a '
            'dashed outline on the machine used for the host crop, labelled "one of the rack\'s machines".',
    'child': {'id': 'host', 'box_px': [180, 185, 490, 495], 'note': 'illustrative: not known to be a lab machine'},
})

# ------------------------------------------------------------------ 5. Studio 45
room_w = 20.0
L.append({
    'id': 'studio45', 'name': 'Studio 45', 'parent': 'sf', 'optional': False,
    'size_m': room_w, 'frame_m': 25.0, 'size_kind': 'assumed',
    'size_note': 'The room\'s size is not recorded; 20 m is an order-of-magnitude frame.',
    'blurb': 'The rack stands in Studio 45, the room in San Francisco where the lab\'s machines are. Light crosses a '
             f'room like this in about {si_time(room_w / C, 2)}, some {room_w / C / T_CLK:.0f} of the chip\'s clock '
             'ticks.',
    'facts': [
        F('The owner calls the lab\'s room, in San Francisco, Studio 45.', 'the owner (30 Sep 2026)', 'owner'),
        F('No public page ties AI Foundry\'s lab to Studio 45; the page gives only the name and the city, never an '
          'address or a position on the map.', 'AGENT.md §10; the owner\'s instruction for this level', 'note'),
    ],
    'light': light(room_w),
    'image': None,
    'draw': 'A schematic floor (not a plan of the real room: its layout is not recorded, and none is drawn): a grey '
            'floor rectangle 20 x 12 m labelled "schematic", the rack to scale (1.5 x 0.6 m) and a 1.7 m person '
            'for scale. Scale bar 5 m. No venue photo (none is openly licensed).',
    'child': {'id': 'rack', 'note': 'the rack, drawn to scale; its place in the room is not recorded'},
})

# ------------------------------------------------------------------ 6. San Francisco
sf_area = 121.51e6
sf_w = math.sqrt(sf_area)
sfb = GEO['sf']['bbox_km']
L.append({
    'id': 'sf', 'name': 'San Francisco', 'parent': 'bayarea', 'optional': False,
    'size_m': round(sf_w, -2), 'frame_m': 18_000, 'size_kind': 'derived',
    'size_note': f'√(121.51 km² of land) = {sf_w / 1000:.1f} km; the city\'s outline, islands included, spans '
                 f'{sfb[2] - sfb[0]:.1f} x {sfb[3] - sfb[1]:.1f} km on the Census map.',
    'blurb': f'The city is about 11 km across. A signal in an optical fibre crosses it in about '
             f'{si_time(sf_w / V_FIBRE)}; in that time the chip\'s clock ticks some {cycles(sf_w / V_FIBRE)} times.',
    'facts': [
        F('Land area 46.92 sq mi (121.51 km²); 873,965 people at the 2020 census.',
          'Wikipedia, "San Francisco" (from the US Census Bureau)', 'outside source'),
        F(f'Light in glass fibre travels at c/1.4682 = {V_FIBRE / 1e3:,.0f} km/s, about '
          f'{1e9 / V_FIBRE * 1e3 / 1e3:.2f} µs per km: two-thirds of its speed in vacuum.', S['corning'], 'derived'),
        F(f'Across the city ({sf_w / 1000:.0f} km): {si_time(sf_w / C)} for light in vacuum, {si_time(sf_w / V_FIBRE)} '
          f'in fibre.', S['si'] + '; ' + S['corning'], 'derived'),
        F('Esperanto Technologies, which designed the ET-SoC-1, was based in Mountain View, about 50 km to the south.',
          'Business Wire, Esperanto press release of 1 May 2023 (general-purpose SDK): "Esperanto is headquartered in Mountain View, California"', 'outside source'),
    ],
    'light': light(sf_w, fibre=True),
    'image': None,
    'draw': 'outside-geo.json "sf": the city and county outline from the Census 1:500,000 file (public domain), '
            'Farallon Islands left out; units km, local projection. Scale bar 2 km. The camera arrives at the '
            'city\'s centre (sf_centre, the usual city-centre point), NEVER at the lab\'s location.',
    'child': {'id': 'studio45', 'note': 'drawn as a small square at the city\'s centre, labelled "Studio 45 (not to '
                                        'scale; position not shown)"'},
})

# ------------------------------------------------------------------ 7. the Bay Area
bab = GEO['bayarea']['bbox_km']
bay_w = (bab[2] - bab[0]) * 1e3
bay_h = (bab[3] - bab[1]) * 1e3
L.append({
    'id': 'bayarea', 'name': 'The Bay Area', 'parent': 'california', 'optional': False,
    'size_m': round(max(bay_w, bay_h), -3), 'frame_m': 240_000, 'size_kind': 'derived',
    'size_note': f'The nine counties span {bay_w / 1e3:.0f} x {bay_h / 1e3:.0f} km on the Census outlines.',
    'blurb': 'Nine counties around San Francisco Bay, about 200 km from end to end. A fibre signal takes about a '
             f'millisecond to cross them: some {cycles(max(bay_w, bay_h) / V_FIBRE)} of the chip\'s clock ticks.',
    'facts': [
        F('Nine counties (Alameda, Contra Costa, Marin, Napa, San Francisco, San Mateo, Santa Clara, Solano, '
          'Sonoma); 6,966 sq mi (18,040 km²) of land; 7.77 million people in 2020.',
          'Wikipedia, "San Francisco Bay Area"', 'outside source'),
        F(f'Across the region ({max(bay_w, bay_h) / 1e3:.0f} km): {si_time(max(bay_w, bay_h) / C)} in vacuum, '
          f'{si_time(max(bay_w, bay_h) / V_FIBRE)} in fibre.', S['si'] + '; ' + S['corning'], 'derived'),
        F('Esperanto designed the ET-SoC-1 in Mountain View, in Santa Clara County, within this map.',
          'Business Wire, Esperanto press release of 1 May 2023', 'outside source'),
    ],
    'light': light(max(bay_w, bay_h), fibre=True),
    'image': None,
    'draw': 'outside-geo.json "bayarea": nine county outlines (Census 1:500,000, public domain), San Francisco '
            'highlighted; the bay\'s water is the gap between them. Scale bar 50 km. Optional label: Mountain View.',
    'child': {'id': 'sf', 'box_km': GEO['bayarea']['sf_bbox_km']},
})

# ------------------------------------------------------------------ 8. California (optional)
cab = GEO['california']['bbox_km']
ca_h = (cab[3] - cab[1]) * 1e3
L.append({
    'id': 'california', 'name': 'California', 'parent': 'us', 'optional': True,
    'size_m': round(ca_h, -4), 'frame_m': 1_150_000, 'size_kind': 'derived',
    'size_note': f'{(cab[2] - cab[0]):.0f} x {ca_h / 1e3:.0f} km on the equal-area map (Census 1:5,000,000).',
    'blurb': 'The state is about 1,000 km from north to south. A fibre signal runs its length in about five '
             'thousandths of a second.',
    'facts': [
        F('Area 163,696 sq mi (423,970 km²).', 'Wikipedia, "Geography of California"', 'outside source'),
        F(f'North to south on the map: {ca_h / 1e3:.0f} km, {si_time(ca_h / V_FIBRE)} in fibre.',
          'outside-geo.json (Census outlines); ' + S['corning'], 'derived'),
    ],
    'light': light(ca_h, fibre=True),
    'image': None,
    'draw': 'outside-geo.json "california" (Census 1:5,000,000, public domain), with the Bay Area\'s frame '
            '(bayarea_bbox_km) as a rectangle. Scale bar 200 km. Optional level: the zoom from the Bay Area (x5) '
            'and on to the US (x4) is smooth without it too.',
    'child': {'id': 'bayarea', 'box_km': GEO['california']['bayarea_bbox_km']},
})

# ------------------------------------------------------------------ 9. the United States
usb = GEO['us']['bbox_km']
sfnyc = GEO['meta']['sf_nyc_great_circle_km'] * 1e3
L.append({
    'id': 'us', 'name': 'The United States', 'parent': 'earth', 'optional': False,
    'size_m': 4_509_000, 'frame_m': 5_000_000, 'size_kind': 'outside source',
    'size_note': 'The longest great circle inside the lower 48 states: 2,802 mi (4,509 km), Florida to Washington.',
    'blurb': f'From coast to coast about 4,500 km. A signal in a fibre from San Francisco to New York takes about '
             f'{si_time(sfnyc / V_FIBRE, 2)} one way even on a perfectly straight cable: '
             f'{cycles(sfnyc / V_FIBRE)} clock ticks of the chip.',
    'facts': [
        F('The lower 48 states: 4,509 km on the longest great circle inside them, 2,660 km north to south, '
          '8.08 million km².', 'Wikipedia, "Contiguous United States"', 'outside source'),
        F(f'San Francisco to New York: {sfnyc / 1e3:,.0f} km on a great circle, {si_time(sfnyc / C)} for light in vacuum, '
          f'{si_time(sfnyc / V_FIBRE)} in fibre. Real cables are longer than the great circle, and routers add delay.',
          'derived from the two city centres (37.7749 N 122.4194 W; 40.7128 N 74.0060 W) on a 6,371 km sphere; '
          + S['corning'], 'derived'),
    ],
    'light': light(sfnyc, fibre=True),
    'image': None,
    'draw': 'outside-geo.json "us": the 48 states and DC (Census 1:5,000,000, public domain), Albers equal-area, '
            'California highlighted, San Francisco and New York as dots joined by the great-circle arc (its label: '
            'the fibre time). Scale bar 1,000 km.',
    'child': {'id': 'california', 'box_km': GEO['us']['california_bbox_km']},
})

# ------------------------------------------------------------------ 10. Earth
R_E = 6371.0e3
circ = 2 * math.pi * 6378.137e3
L.append({
    'id': 'earth', 'name': 'Earth', 'parent': 'moon', 'optional': False,
    'size_m': 2 * R_E, 'frame_m': 1.5e7, 'size_kind': 'outside source',
    'size_note': 'Mean diameter 12,742 km (twice NASA\'s volumetric mean radius, 6,371.000 km).',
    'blurb': f'Earth is 12,742 km across. Light could circle it in {si_time(circ / C)}: in that time the chip\'s clock '
             f'ticks {cycles(circ / C)} times.',
    'facts': [
        F('Volumetric mean radius 6,371.000 km; equatorial radius 6,378.137 km.', S['nasa_earth'], 'outside source'),
        F(f'Around the equator ({circ / 1e3:,.0f} km): {si_time(circ / C)} for light, {si_time(circ / V_FIBRE)} in '
          'fibre.', S['nasa_earth'] + '; ' + S['si'] + '; ' + S['corning'], 'derived'),
    ],
    'light': light(circ, fibre=True),
    'image': {'file': 'earth.webp', 'px': [400, 400], 'bytes': os.path.getsize(
        os.path.join(IMG, 'earth.webp')),
        'credit': 'NASA Goddard Space Flight Center, "The Blue Marble" (Visible Earth record 57723, globe_west): image '
                  'by Reto Stöckli; enhancements by Robert Simmon; MODIS data',
        'licence': 'public domain (NASA imagery is generally not subject to copyright in the US; NASA asks to be '
                   'credited as the source)',
        'source_url': 'https://eoimages.gsfc.nasa.gov/images/imagerecords/57000/57723/globe_west_2048.jpg',
        'note': 'North America centred; the disc fills about 88% of the square (measure it in the page).'},
    'draw': 'Either the photo, or outside-geo.json "earth": Natural Earth 1:110m land on an orthographic globe centred '
            'on 38 N 100 W (public domain), drawn in km with the globe\'s circle as the ocean: the US bbox is given '
            'for the zoom (us_bbox_km). Recommended: the drawn globe for the camera (exact scale, the US outline '
            'lines up), cross-fading to the photo at rest. Scale bar 2,000 km.',
    'child': {'id': 'us', 'box_km': GEO['earth']['us_bbox_km']},
})

# ------------------------------------------------------------------ 11. Earth and the Moon (optional)
moon = 384_400e3
L.append({
    'id': 'moon', 'name': 'Earth and the Moon', 'parent': 'solar', 'optional': True,
    'size_m': 2 * moon, 'frame_m': 9e8, 'size_kind': 'outside source',
    'size_note': 'The Moon\'s orbit: semimajor axis 384,400 km, so about 769,000 km across.',
    'blurb': f'The Moon is 384,400 km away. Light takes {si_time(moon / C)} to get there: {cycles(moon / C)} ticks of '
             'the chip\'s clock.',
    'facts': [
        F('The Moon\'s semimajor axis: 0.3844 million km.', S['nasa_moon'], 'outside source'),
        F(f'Earth to the Moon: {si_time(moon / C)} for light.', S['nasa_moon'] + '; ' + S['si'], 'derived'),
    ],
    'light': light(moon),
    'image': None,
    'draw': 'Drawn SVG: Earth (12,742 km) and the Moon (3,474.8 km, NASA Moon fact sheet) to scale on its orbit '
            'circle. Scale bar 100,000 km. Optional: it bridges a 60x step.',
    'child': {'id': 'earth', 'note': 'Earth at the centre'},
})

# ------------------------------------------------------------------ 12. the Solar System
nep = 30.06896348 * AU   # NSSDCA Neptune fact sheet, orbital parameters: semimajor axis (AU)
voy = 86400 * C
L.append({
    'id': 'solar', 'name': 'The Solar System', 'parent': 'stars', 'optional': False,
    'size_m': 2 * nep, 'frame_m': 1.1e13, 'size_kind': 'outside source',
    'size_note': f'Neptune\'s orbit: semimajor axis {nep / AU:.2f} au ({nep / 1e9:,.0f} million km), so about '
                 f'{2 * nep / 1e12:.1f} x 10^12 m across.',
    'blurb': f'Sunlight takes {si_time(AU / C, 2)} to reach Earth and about {si_time(nep / C, 2)} to reach Neptune. In '
             'November 2026 Voyager 1, the farthest spacecraft, will be a full light-day away.',
    'facts': [
        F(f'Earth orbits at 1 au, {si_time(AU / C)} from the Sun at the speed of light.', S['iau_au'] + '; ' + S['si'],
          'derived'),
        F(f'Neptune\'s semimajor axis: {nep / AU:.2f} au ({nep / 1e9:,.0f} million km); sunlight reaches it in '
          f'{si_time(nep / C)}.', S['nasa_nep'] + ' (orbital parameters: semimajor axis 30.06896348 AU)', 'outside source'),
        F(f'Voyager 1 reaches one light-day from Earth (25.9 billion km, {voy / AU:.0f} au) on 18 November 2026: a '
          'command sent then takes a day to arrive and the answer another day.',
          'NASA, "Where are Voyager 1 and Voyager 2 now?" (science.nasa.gov/mission/voyager/'
          'where-are-voyager-1-and-voyager-2-now/)', 'outside source'),
    ],
    'light': light(2 * nep),
    'image': None,
    'draw': 'Drawn SVG: the Sun and the eight planets\' orbits as circles to scale (semimajor axes from NASA\'s '
            'fact sheets: Mercury 0.387, Venus 0.723, Earth 1, Mars 1.524, Jupiter 5.20, Saturn 9.57, Uranus 19.17 au '
            'by those sheets\' 10^6 km values, Neptune 30.07 au by its sheet\'s semimajor axis in au), planets as labelled dots (not to scale: say so), '
            'an arrow off the frame "Voyager 1: 173 au, one light-day". Scale bar 5 au.',
    'child': {'id': 'moon', 'note': 'Earth\'s position on its 1 au orbit (for the zoom, the angle is arbitrary)'},
})

# ------------------------------------------------------------------ 13. the nearest stars (optional)
prox = 4.2 * LY
L.append({
    'id': 'stars', 'name': 'The nearest stars', 'parent': 'milkyway', 'optional': True,
    'size_m': 20 * LY, 'frame_m': 20 * LY, 'size_kind': 'assumed',
    'size_note': 'A 20-light-year frame around the Sun (a choice, not an object).',
    'blurb': 'The nearest star after the Sun, Proxima Centauri, is 4.2 light-years away: its light left it more than '
             'four years ago.',
    'facts': [
        F('Proxima Centauri is 4.2 light-years from the Sun.',
          'NASA, "Proxima Centauri microlensing prediction" (science.nasa.gov/asset/hubble/'
          'proxima-centauri-microlensing-prediction)', 'outside source'),
        F(f'One light-year is {sci(LY, 3)} m, about {round(LY / (2 * nep), -1):,.0f} times the width of Neptune\'s orbit.', S['iau_ly'], 'derived'),
    ],
    'light': light(prox),
    'image': None,
    'draw': 'Drawn SVG: the Sun at the centre, Proxima/Alpha Centauri at 4.2 ly as a labelled dot, a 4.2 ly circle; '
            'other stars only if sourced. Scale bar 5 ly. Optional: it bridges a 10^8 step (Solar System to galaxy).',
    'child': {'id': 'solar', 'note': 'the Sun at the centre'},
})

# ------------------------------------------------------------------ 14. the Milky Way
mw = 100_000 * LY
mw_frame = 135_400 * LY
L.append({
    'id': 'milkyway', 'name': 'The Milky Way', 'parent': 'localgroup', 'optional': False,
    'size_m': mw, 'frame_m': mw_frame, 'size_kind': 'outside source',
    'size_note': 'About 100,000 light-years across (NASA).',
    'blurb': 'Our galaxy: at least 100 billion stars in a disc about 100,000 light-years across. The ET-SoC-1 has '
             'about a quarter as many transistors as the galaxy has stars.',
    'facts': [
        F('A spiral galaxy about 100,000 light-years across, with at least 100 billion stars.',
          'NASA, "Beyond Our Solar System" poster (science.nasa.gov/resource/beyond-our-solar-system-poster-version-a/)',
          'outside source'),
        F('The Sun is about 26,000 light-years from the centre, in a small arm called the Orion Spur.',
          'NASA/JPL-Caltech/R. Hurt (SSC/Caltech), ssc2008-10b caption; ESO eso1339e (annotated)', 'outside source'),
        F('More than 24 billion transistors on the chip against at least 100 billion stars: about one transistor for '
          'every four stars.', S['facts'] + ' (chip.process); NASA (above)', 'derived'),
        F('The picture\'s square spans about 135,000 light-years: the page\'s builder measured it against ESO\'s '
          'annotated copy of the same artwork (eso1339e), whose distance rings are 9.45 px per 1,000 light-years.',
          'the builder\'s own measurement (outside.json, image geometry); ESO eso1339e', 'inferred'),
    ],
    'light': light(mw),
    'image': {'file': 'milkyway.webp', 'px': [480, 480], 'bytes': os.path.getsize(
        os.path.join(IMG, 'milkyway.webp')),
        'credit': 'NASA/JPL-Caltech/R. Hurt (SSC/Caltech), "Our Milky Way Gets a Makeover" (artist\'s concept, '
                  'PIA10748)',
        'licence': 'JPL image use policy: "may be used for any purpose without prior permission"; credit '
                   '"NASA/JPL-Caltech"',
        'source_url': 'https://assets.science.nasa.gov/content/dam/science/psd/photojournal/pia/pia10/pia10748/'
                      'PIA10748.jpg',
        'geometry': {'ly_per_px_at_480': 282.1, 'frame_ly': 135_400, 'sun_frac': [0.500, 0.691],
                     'centre_frac': [0.500, 0.495],
                     'how': 'same artwork and framing as ESO\'s annotated eso1339e (correlation 0.977 at scale 1.0, no '
                            'shift); its distance rings, centred on the Sun, are 9.45 px per 1,000 ly on the 1280 px '
                            'screen image; the Sun is marked at (640, 884) of 1280.'},
        'note': 'An artist\'s concept, not a photograph: nobody has seen the galaxy from outside. Say so on the page.'},
    'draw': 'The picture with an SVG overlay: a "You are here" ring at the Sun (sun_frac), a line to the centre '
            'labelled "26,000 ly", and a 20,000 ly scale bar (70.9 px on the 480 px copy).',
    'child': {'id': 'stars', 'at_frac': [0.500, 0.691]},
})

# ------------------------------------------------------------------ 15. the Local Group (Andromeda)
lg = 10e6 * LY
m31 = 2.5e6 * LY
L.append({
    'id': 'localgroup', 'name': 'The Local Group (Andromeda)', 'parent': 'laniakea', 'optional': False,
    'size_m': lg, 'frame_m': 1.1e7 * LY, 'size_kind': 'outside source',
    'size_note': 'Its galaxies are spread over a diameter of nearly 10 million light-years (NASA).',
    'blurb': 'The Milky Way\'s neighbourhood: dozens of galaxies (more than 130 are now known, most of them faint '
             'dwarfs), led by the Milky Way and Andromeda. The light we see from Andromeda left it 2.5 million years '
             'ago. There is no "Andromeda cluster": Andromeda is a galaxy, and it and the Milky Way lead this small '
             'group. True clusters, such as Virgo with over a thousand galaxies, are larger, and lie further out '
             'inside Laniakea.',
    'facts': [
        F('More than 30 galaxies spread over a diameter of nearly 10 million light-years.',
          'NASA, Imagine the Universe!, "The Local Group of Galaxies" (imagine.gsfc.nasa.gov/features/cosmic/'
          'local_group_info.html)', 'outside source'),
        F('Andromeda (M31) is about 2.5 million light-years away and spans 260,000 light-years.',
          'NASA/JPL-Caltech, PIA15416 caption (science.nasa.gov/photojournal/andromeda)', 'outside source'),
        F('The Triangulum galaxy (M33), the third largest member, is about 3 million light-years away; the Large '
          'Magellanic Cloud, a satellite of ours, about 160,000.',
          'NASA, Hubble Messier catalogue, M33; NASA APOD, 28 May 2013 (the Large Cloud of Magellan)',
          'outside source'),
        F('A collision with Andromeda, long predicted for about 4.5 billion years from now, now looks about a coin '
          'flip within 10 billion years, and under 2% within 5 billion.',
          'T. Sawala et al., Nature Astronomy (2025), "No certainty of a Milky Way-Andromeda collision"',
          'outside source'),
        F('More than 130 members are now known within a megaparsec of the group\'s centre (134 in one count), most of '
          'them faint dwarf galaxies; counted that way the group is about 5.1 Mpc (17 million light-years) across.',
          'Wikipedia, "Local Group" (read 1 Oct 2026): "a current total of 134 members is known within 1 megaparsec", '
          '"most of which are dwarf galaxies", "a total diameter of 5.11 megaparsecs (17 million light-years)"',
          'outside source'),
        F('A galaxy cluster is far larger than a group: the nearest big one, the Virgo Cluster, about 54 million '
          'light-years away, has about 1,300 (possibly up to 2,000) galaxies. The Local Group belongs to the Virgo '
          'Supercluster, which is part of Laniakea.',
          'Wikipedia, "Virgo Cluster" and "Local Group" (read 1 Oct 2026); Tully et al. 2014 (Laniakea, below)',
          'outside source'),
    ],
    'light': light(m31),
    'image': {'file': 'andromeda.webp', 'px': [480, 357], 'bytes': os.path.getsize(
        os.path.join(IMG, 'andromeda.webp')),
        'credit': 'NASA/JPL-Caltech, Galaxy Evolution Explorer (GALEX), "Andromeda" (PIA15416), ultraviolet',
        'licence': 'JPL image use policy: "may be used for any purpose without prior permission"; credit '
                   '"NASA/JPL-Caltech"',
        'source_url': 'https://d2pn8kiwq2w21t.cloudfront.net/images/jpegPIA15416.width-1024.jpg',
        'note': 'An ultraviolet mosaic, so bluer than to the eye; no scale bar on the photo (its framing in '
                'light-years is not given).'},
    'draw': 'Drawn SVG map (the zoom target): the Milky Way and Andromeda 2.5 Mly apart, M33 near Andromeda, the '
            'Magellanic Clouds at the Milky Way, dwarf galaxies as unlabelled dots only if sourced; a 1 Mly scale '
            'bar. The Andromeda photo as an inset at M31\'s position.',
    'child': {'id': 'milkyway', 'note': 'the Milky Way on the map'},
})

# ------------------------------------------------------------------ 16. Laniakea
lan = 160e6 * PC
L.append({
    'id': 'laniakea', 'name': 'Laniakea', 'parent': 'universe', 'optional': False,
    'size_m': lan, 'frame_m': 1.2 * lan, 'size_kind': 'outside source',
    'size_note': f'160 Mpc across if taken as round (Tully et al. 2014): {lan / LY / 1e6:.0f} million light-years.',
    'blurb': 'The Local Group is one small part of a supercluster of about 100,000 galaxies, about 520 million '
             'light-years across. Its name is Hawaiian for "immeasurable heaven".',
    'facts': [
        F('A region about 160 Mpc (520 million light-years) across, holding about 10^17 times the Sun\'s mass, '
          'defined by where galaxies\' motions flow inward; "lani" means heaven and "akea" spacious, immeasurable.',
          'R. B. Tully, H. Courtois, Y. Hoffman, D. Pomarède, "The Laniakea supercluster of galaxies", Nature 513, '
          '71-73 (2014), arXiv:1409.0880', 'outside source'),
        F('About 100,000 galaxies.', 'NRAO press release, 3 Sep 2014 (public.nrao.edu/news/supercluster-gbt/)',
          'outside source'),
    ],
    'light': light(lan),
    'image': None,
    'draw': 'Drawn SVG, schematic: a soft irregular outline 160 Mpc across (label "shape simplified"), flow lines '
            'converging on the Great Attractor region, the Local Group as a dot near the edge. No published map '
            'is openly licensed. Scale bar 100 million ly.',
    'child': {'id': 'localgroup', 'note': 'a dot near the edge'},
})

# ------------------------------------------------------------------ 17. the observable universe
H0, Om, OL = 67.66, 0.3111, 0.6889
h = H0 / 100
Og = 2.47282e-5 / h ** 2
Or_ = Og * (1 + 0.2271 * 3.046)


def integ(f, a0, a1, n=200000):
    # log-spaced trapezoid in a (smooth integrands)
    la0, la1 = math.log(a0), math.log(a1)
    s, prev = 0.0, None
    for i in range(n + 1):
        la = la0 + (la1 - la0) * i / n
        a = math.exp(la)
        v = f(a) * a
        if prev is not None:
            s += (prev + v) / 2 * (la1 - la0) / n
        prev = v
    return s


E = lambda a: math.sqrt(Or_ / a ** 4 + Om / a ** 3 + OL)
Dh = 299792.458 / H0  # Mpc
chi = Dh * integ(lambda a: 1 / (a * a * E(a)), 1e-10, 1.0)
age = integ(lambda a: 1 / (a * E(a)), 1e-10, 1.0) / H0 * 977.792
univ = 2 * chi * 1e6 * PC
L.append({
    'id': 'universe', 'name': 'The observable universe', 'parent': 'beyond', 'optional': False,
    'size_m': univ, 'frame_m': 1.1 * univ, 'size_kind': 'derived',
    'size_note': f'Twice the comoving distance to the particle horizon: {chi / 1e3:.2f} Gpc = {chi * 1e6 * PC / LY / 1e9:.1f} '
                 f'billion ly radius, from Planck 2018\'s parameters (H0 {H0}, Ωm {Om}, ΩΛ {OL}, radiation from '
                 f'T = 2.7255 K, Neff 3.046).',
    'blurb': 'Everything whose light has had time to reach us since the Big Bang, 13.8 billion years ago: a sphere '
             'about 92 billion light-years across, larger than 13.8 billion because space has stretched while the '
             'light travelled.',
    'facts': [
        F(f'Age {age:.2f} billion years by these parameters (Planck 2018: 13.787 ± 0.020).',
          'Planck Collaboration, "Planck 2018 results. VI. Cosmological parameters", A&A 641, A6 (2020), Table 2',
          'outside source'),
        F(f'Radius {chi * 1e6 * PC / LY / 1e9:.1f} billion light-years (comoving), diameter {sci(univ, 2)} m.',
          'derived from the Planck 2018 parameters (this script)', 'derived'),
        F('The oldest light we can see, the cosmic microwave background, left its source about 380,000 years after the '
          'Big Bang; it now has a temperature of 2.7255 K.',
          'NASA/WMAP Science Team (the nine-year map\'s caption); D. J. Fixsen, ApJ 707, 916 (2009)', 'outside source'),
        F(f'The observable universe is about {sci(univ / die_w, 1)} times wider than the chip\'s 25.6 mm die.',
          'derived: the die from facts.json (chip.die-dims)', 'derived'),
    ],
    'light': None,  # a comoving distance: light-travel time is not distance / c here
    'image': {'file': 'cmb.webp', 'px': [400, 200], 'bytes': os.path.getsize(
        os.path.join(IMG, 'cmb.webp')),
        'credit': 'NASA / WMAP Science Team, "Nine Year Microwave Sky" (WMAP 2012)',
        'licence': 'public domain (NASA)',
        'source_url': 'https://upload.wikimedia.org/wikipedia/commons/e/ed/WMAP_2012.png (from '
                      'map.gsfc.nasa.gov/media/121238/)',
        'note': 'A map of the whole sky (Mollweide projection): the inside of the sphere, not a view from outside. '
                'Transparent outside the ellipse.'},
    'draw': 'Drawn SVG: a circle 92 billion ly across with "you are here" at the centre, a thin shell at the edge '
            'labelled "the cosmic microwave background (380,000 years after the Big Bang)", and the WMAP map as an '
            'inset labelled "the whole sky as we see it". Scale bar 10 billion ly (comoving).',
    'child': {'id': 'laniakea', 'note': 'a dot at the centre (Laniakea is ~1/180 of the diameter)'},
})

# ------------------------------------------------------------------ 18. beyond (speculative)
L.append({
    'id': 'beyond', 'name': 'Beyond what we can see (speculative)', 'parent': None, 'optional': False,
    'size_m': None, 'frame_m': 3 * univ, 'size_kind': 'unknown',
    'size_note': 'Unknown. The frame is only a picture size.',
    'blurb': 'Space almost certainly goes on past the edge of what we can see, but how far is unknown. Some theories '
             'go further and propose many universes, a multiverse: a hypothesis, not an observation. (This level is the page\'s '
             'reading of the owner\'s "meta universe".)',
    'facts': [
        F('Measured space is flat to within a fraction of a percent (Ω_K = 0.001 ± 0.002), which suggests the '
          'universe extends well past the observable part.', 'Planck 2018 results VI (abstract), A&A 641, A6 (2020)',
          'outside source'),
        F('One analysis puts the whole universe at more than 251 times the volume of our Hubble sphere (99% level), '
          'under its model assumptions.',
          'M. Vardanyan, R. Trotta, J. Silk, "Applications of Bayesian model averaging to the curvature and size of '
          'the Universe", MNRAS 413, L91-L95 (2011), arXiv:1101.5476', 'outside source'),
        F('Eternal inflation and the string-theory "landscape" suggest many separate universes. Nothing observed so '
          'far confirms or rules this out.',
          'A. H. Guth, "Eternal inflation and its implications", J. Phys. A 40, 6811 (2007), arXiv:hep-th/0702178',
          'hypothesis'),
    ],
    'light': None,
    'image': None,
    'draw': 'Drawn SVG, clearly marked "speculative": our observable sphere as one small circle among a few dashed, '
            'fading ones; no scale bar (a note: "size unknown").',
    'child': {'id': 'universe', 'note': 'our observable universe, one circle'},
})

# ------------------------------------------------------------------ ladder summary
prev = die_w
for lv in L:
    s = lv['frame_m']
    lv['zoom_from_inner'] = round(s / prev, 3) if prev else None
    prev = s

meta = {
    'built': '2026-09-30, build_outside.py',
    'order': 'inside out: package, card, host, rack, Studio 45, San Francisco, Bay Area, (California), US, Earth, '
             '(Earth-Moon), Solar System, (nearest stars), Milky Way, Local Group, Laniakea, observable universe, '
             'beyond. Levels marked optional bridge long steps; the owner\'s named levels are all required.',
    'clock_hz': F_CLK, 'clock_source': S['cb14'] + ':338 (the lab cards\' usual minion clock)',
    'fibre_group_index': N_FIBRE, 'fibre_source': S['corning'],
    'kinds': ['measured', 'spec', 'derived', 'inferred', 'estimate', 'assumed', 'outside source', 'owner',
              'hypothesis', 'note'],
    'files': {'geometry': 'outside-geo.json (map outlines in km: sf, bayarea, california, us, earth)',
              'images': ['rack.webp', 'card.webp', 'earth.webp',
                         'milkyway.webp', 'andromeda.webp', 'cmb.webp']},
    'privacy': 'Studio 45 by name and city only; no address, no coordinates, no map marker; the rack photo\'s '
               'host-name and address labels blurred.',
}
out = {'meta': meta, 'levels': L}
with open(os.path.join(HERE, 'outside.json'), 'w') as f:
    json.dump(out, f, indent=1, ensure_ascii=False)
for lv in L:
    sz = 'unknown' if lv['size_m'] is None else '%.3g' % lv['size_m']
    print('%-11s size %9s m  frame %.3g  x%s' % (lv['id'], sz, lv['frame_m'], lv['zoom_from_inner']))
print('age', age, 'chi Mpc', chi)
