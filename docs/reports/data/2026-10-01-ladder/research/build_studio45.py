#!/usr/bin/env python3
"""Write studio45.json: the facts of the levels between San Francisco and the rack (1 Oct 2026, the owner's
"Studio 45 is located on 29th Street, in Bernal Heights"): Bernal Heights, 29th Street and Studio 45 itself. The
research behind each is in research-studio45.md beside this file (written the same day; its working files, the
DataSF and USGS downloads, stayed in the session's work directory).

Every fact: id, statement, kind (one of the nine: owner, outside, derived, ...), source (publisher, title and date),
url (only where the URL carries no address), note (the arithmetic or the caveat).

Privacy (AGENT.md §10 and the owner's words, which give only the street and the neighbourhood): no statement, source,
URL or note may carry a house number, a block, a point or coordinates of the studio, or a link to a listing that
shows its address. The script refuses a number before "29th", a ZIP code, a latitude or longitude, the listing
sites' domains and any link but the public-data sources'. Events at the venue wait for the owner's answer (DESIGN
Q1) and are not here.
"""
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
C = 299792458.0          # m/s, exact
CLOCK = 600e6            # Hz, the cards' usual clock (the chip diagram's outside.json meta.clock_hz)

F = []


def fact(fid, statement, kind, source, url=None, note=None):
    F.append({'id': fid, 'statement': statement, 'kind': kind, 'source': source, 'url': url, 'note': note})


def light(m):
    t = m / C
    return t, t * CLOCK


SITE = "Studio 45's own website and event listings (read 1 Oct 2026; not linked here: their pages give the street address)"
DATASF = 'City and County of San Francisco, DataSF (Open Data Commons PDDL)'

# ---- Studio 45
fact('s45.1', "The lab's rack stands in Studio 45, the owner's name for the place, which is on 29th Street in Bernal Heights, San Francisco.",
     'owner', 'the owner, 1 Oct 2026')
fact('s45.2', 'Studio 45 is a co-working and event space for people who build physical things: "space, tools, and resources for the hardware community".',
     'outside', SITE)
fact('s45.3', 'It has two floors of co-working space, a wood shop, 3D printers, a metal CNC mill, a laser cutter and a 4 x 8 ft three-axis CNC router, with assembly space in a street-level warehouse and courtyard.',
     'outside', SITE)
fact('s45.4', 'It opened with a launch party on 9 December 2021, as "San Francisco\'s newest co-working space for people who make real things for a living".',
     'outside', 'SF Station, event listing "Studio 45 Launch" (9 Dec 2021; not linked here: it gives the street address)')
fact('s45.5', 'It describes itself as a coworking space for the hardware community "at the intersection of The Mission and Bernal Heights", and hosts the monthly SF Hardware Meetup.',
     'outside', 'SF Hardware Meetup event listings (2025-2026; not linked here: they give the street address)')
fact('s45.6', 'The building at its address is about 37 m deep and 9 m wide (325 m² on the ground) and 6 to 8 m tall: two storeys.',
     'derived', DATASF + ', Building Footprints (ynuv-fyni; a 2010 3D model split at parcel lines)',
     note='Length and width of the footprint polygon and its roof heights (median 6.0 m, highest 8.3 m), read by the '
          'venue\'s public address; only these dimensions were kept. The courtyard and event spaces may reach onto '
          'neighbouring lots. Where in the building the rack stands is not recorded.')
t, n = light(37)
fact('s45.7', f'Light crosses the building\'s 37 m in {t * 1e9:.0f} ns: {n:.0f} ticks of the chip\'s 600 MHz clock.',
     'derived', 'the building\'s length (s45.6) divided by the speed of light; the 600 MHz clock of the lab\'s cards',
     note=f'37 m / 299,792,458 m/s = {t * 1e9:.1f} ns; x 600 MHz = {n:.1f}')
fact('s45.8', 'A 4 x 8 ft CNC router cuts a 1.22 x 2.44 m sheet: the size of the bed drawn here.',
     'derived', 'the venue\'s "4\'x8\' 3-axis CNC with a tool changer" (s45.3) in metres', note='4 ft = 1.219 m, 8 ft = 2.438 m')
# the building inside (13 Oct 2026, the owner: "for Studio 45, maybe you can find the original plans to make it more
# realistic. The lab is on the second floor, indeed"). No plan set is online; the venue's own public 3D tour carries
# measured plans of both floors, and the city's records give the rest (research in the private notes of that day).
TOUR = "Studio 45's public 3D tour (Matterport), its measured plans of both floors (scanned 2 June 2026; not linked here: the tour gives the street address)"
fact('s45.9', 'The lab is on the building\'s upper floor.', 'owner', 'the owner, 13 Oct 2026')
fact('s45.10', 'Inside, the ground floor is one room 36.1 m long and 8.5 m wide. The upper floor is a mezzanine at each end, 17.1 m and 9.8 m long, with 9.3 m between them open from the floor to the roof: the warehouse.',
     'outside', TOUR,
     note='The plans\' walls, in metres: ground floor 36.05 x 8.48 m inside; upper floor from 0 to 17.1 m and from 26.4 to '
          '36.1 m along the building, nothing between. They agree with the city\'s footprint (s45.6) to within 0.6 m, the '
          'thickness of the walls.')
fact('s45.11', 'Downstairs, one end has a lounge and kitchen with a long table, small meeting rooms and a stair; the middle is the warehouse, open to the roof, with the second stair; the other end is the wood shop, with the 4 x 8 ft CNC router.',
     'outside', TOUR, note='The rooms read from the tour\'s top-down plan pictures; the machines named from the venue\'s list (s45.3).')
fact('s45.12', 'Upstairs at the lounge end: the co-working room with two long shared desks, a conference room, a small meeting room and a bathroom; at the shop end, one large room with a hard floor, about 9.7 by 8.1 m.',
     'outside', TOUR)
fact('s45.13', 'The lounge end most likely faces 29th Street: the front of the house at the door, the shop at the back beside the yard. The plans carry no compass.',
     'inferred', 'the order of the rooms in the tour\'s plans (s45.11), and the yard behind the building (s45.16)',
     note='A lounge, kitchen and small meeting rooms are what a door opens onto; the shop and its big machines sit at the '
          'far end, against the yard. A pallet lane runs from the lounge end down one side to the warehouse, as the '
          'venue\'s "street level shipping and receiving" needs. The other way round is possible.')
fact('s45.14', 'The lab is most likely the large hard-floored room upstairs at the shop end: the only upstairs room with a hard floor, over the shop, with its own stair. Which room it is has not been recorded.',
     'inferred', 'the owner\'s "upper floor" (s45.9) and the tour\'s plans (s45.12)',
     note='Of the upstairs rooms, the others are the co-working room (wood floor, two long desks), a conference room, a '
          'meeting room and a bathroom; this one has a sealed grey floor, benches and shelving, and sits over the shop.')
fact('s45.15', 'The building went up in 1985, a one-storey shop by its permit and later a post office; the upper floor is a mezzanine.',
     'outside', DATASF + ', Building Permits (i98e-djp9) and the Assessor-Recorder\'s property roll (wv5m-vpq2); SF Planning records (y673-d69b)',
     note='The new-building permit was completed on 29 Nov 1985; a 2023 permit adds sprinklers "under an existing mezzanine". '
          'The roll still says one storey, as the 1985 permit did.')
fact('s45.16', 'Behind the building its lot runs on another 2.3 to 10 m: a yard, most likely the venue\'s courtyard.',
     'derived', DATASF + ', Parcels (acdm-wktn) with Building Footprints (ynuv-fyni)',
     note='The lot is five-sided and its back edge slants: 2.3 m beyond the building\'s back wall on one side, 7.4 m on the '
          'other, 10 m at its point (the two maps registered on the street line). That it is the courtyard is inferred.')
fact('s45.17', 'With the roof about 6 m up, the upper floor stands about 3.3 m above the ground floor.',
     'inferred', 'the roof height (s45.6) shared by two floors, the upper one about 2.7 m to the ceiling',
     note='The city\'s model gives the roof 6.05 m above the ground (median). The plans give no heights: 3.3 m below and '
          '2.7 m above is an estimate, a usual split for a mezzanine under a flat roof.')

# ---- Bernal Heights
fact('b.1', 'Bernal Heights is a residential hill neighbourhood in south-eastern San Francisco, south of the Mission, bounded by Cesar Chavez Street (north), San Jose Avenue (west), US 101 (east) and I-280 (south).',
     'outside', 'Wikipedia, "Bernal Heights, San Francisco" (read 1 Oct 2026, citing UCSC Critical Sustainabilities); SF Chronicle, 29 Aug 2021',
     url='https://en.wikipedia.org/wiki/Bernal_Heights,_San_Francisco')
fact('b.2', 'Its area is 2.79 km², 2.3% of the city\'s land, about 2.2 km east to west and 2.0 km north to south.',
     'derived', DATASF + ', Analysis Neighborhoods (j2bu-swwd)',
     note='Area and extent of the "Bernal Heights" polygon on the San Francisco map\'s projection (equirectangular at '
          '37.76 N); 2.79 / 121.51 km² of land = 2.3%.')
fact('b.3', 'About 26,140 people live there (2012-2016), some 3% of the city.',
     'outside', 'SF Planning, "San Francisco Neighborhoods: Socio-Economic Profiles, American Community Survey 2012-2016" (Sept 2018), p. 10',
     note='26,140 of 873,965 (2020 census) is 3.0%. Wikipedia gives 25,125 for 2019 (city-data.com).')
fact('b.4', 'The hill\'s summit is 142 m (466 ft) above sea level, about half the height of Mount Davidson, the city\'s highest point (283 m).',
     'derived', 'USGS 3DEP 1 m lidar elevation model (flown 4 Mar 2023, NAVD88) through the USGS Elevation Point Query Service; SF Planning, Conditional Use Authorization 2010.0306C (466 ft)',
     url='https://epqs.nationalmap.gov/',
     note='The highest ground within 80 m of the GNIS summit point (GNIS 1658039): 141.99 m. Other published values: 433 ft (1958) and "475+ ft" (USGS 7.5\' topo, NGVD29).')
fact('b.5', 'Bernal Heights Park covers the hilltop: 26.3 acres (10.7 ha), with a 50-foot telecommunications tower at the top.',
     'outside', DATASF + ', Recreation and Parks Properties (gtr9-ntp6); Wikipedia, "Bernal Heights Summit" (SF Planning)',
     url='https://en.wikipedia.org/wiki/Bernal_Heights_Summit')
fact('b.6', 'The hill is folded layers of red radiolarian chert: microcrystalline quartz, silicon dioxide, made from the silica shells of plankton about a millimetre across (0.5 to 1.5 mm) that settled on the deep-sea floor 200 to 100 million years ago.',
     'outside', 'National Park Service, Presidio of San Francisco, "Chert" (the shells "0.5 to 1.5 mm"); Golden Gate National Recreation Area, "Chert FAQ" ("0.5-1 mm"); Wikipedia, "Bernal Heights Summit" and "Chert"',
     url='https://www.nps.gov/prsf/learn/nature/chert.htm')
fact('b.7', 'Silicon for chips is refined from silica, silicon dioxide like the hill\'s quartz: reduced to silicon metal, then purified into the "ultra-high-purity" polysilicon of semiconductor grade.',
     'outside', 'USGS, Mineral Commodity Summaries 2025, Silicon',
     url='https://pubs.usgs.gov/periodicals/mcs2025/mcs2025-silicon.pdf')
t, n = light(2200)
fact('b.8', f'Light crosses the neighbourhood\'s 2.2 km in {t * 1e6:.1f} µs: {n:,.0f} ticks of the chip\'s clock.',
     'derived', 'the neighbourhood\'s width (b.2) divided by the speed of light; the cards\' 600 MHz clock',
     note=f'2,200 m / c = {t * 1e6:.2f} µs; x 600 MHz = {n:.0f}')
fact('b.9', 'It is named after José Cornelio Bernal, who received the Rancho Rincon de las Salinas y Potrero Viejo land grant in 1839.',
     'outside', 'Wikipedia, "Bernal Heights, San Francisco" (read 1 Oct 2026)', url='https://en.wikipedia.org/wiki/Bernal_Heights,_San_Francisco')

# ---- 29th Street
fact('st.1', '29th Street is 1.29 km long. It runs east from Diamond Street, at the foot of Diamond Heights, through Noe Valley to Mission Street, where the Mission meets Bernal Heights.',
     'derived', DATASF + ', Streets - Active and Retired (3psu-pn9h, Public Works centrelines)',
     note='The sum of its nine centreline segments: 1,293 m. (Not 29th Avenue, in the Richmond and Sunset.)')
fact('st.2', 'It falls about 95 m along its length, from 126 m above sea level at Diamond Street to about 30 m at its east end; the steepest part is the top, 34 m down in the first 140 m (about 24%).',
     'derived', 'USGS 3DEP 1 m lidar elevation model through the Elevation Point Query Service, sampled every 40 m along the street',
     url='https://epqs.nationalmap.gov/', note='research/epqs_29th.out: 28 samples, distances and heights only')
t, n = light(1293)
fact('st.3', f'Light runs the street\'s length in {t * 1e6:.2f} µs: {n:,.0f} ticks of the chip\'s clock.',
     'derived', 'the street\'s length (st.1) divided by the speed of light; the cards\' 600 MHz clock',
     note=f'1,293 m / c = {t * 1e6:.3f} µs; x 600 MHz = {n:.0f}')

# ---- privacy checks: no house number before "29th", no ZIP code, no coordinates, no listing site
BAD = [(re.compile(r'\b\d{1,5}\s+29th\b', re.I), 'a house number before 29th'),
       (re.compile(r'\b941\d\d\b'), 'a ZIP code'),
       (re.compile(r'\b3[67]\.\d{3,}|\b-?12[12]\.\d{3,}'), 'a latitude or longitude'),
       (re.compile(r'luma\.com|lu\.ma|sfstation\.com|coworkingcafe|globenewswire|eventcreate|https?://(?!(?:[a-z0-9-]+\.)*(?:wikipedia\.org|nps\.gov|usgs\.gov|sfgov\.org|sf\.gov|sfplanning\.org|datasf\.org|data\.sfgov\.org|epqs\.nationalmap\.gov|census\.gov|naturalearthdata\.com|ucsc\.edu|sfchronicle\.com)\b)', re.I), 'a link other than the public-data sources (a listing could give the address)')]
for f in F:
    for field in ('statement', 'source', 'url', 'note'):
        v = f.get(field) or ''
        for rx, what in BAD:
            if rx.search(v):
                raise SystemExit(f'{f["id"]} {field}: {what}: {v[:120]}')
KINDS = {'measured', 'spec', 'derived', 'inferred', 'outside', 'generic', 'owner', 'hypothesis', 'unknown'}
assert all(f['kind'] in KINDS for f in F)
out = {'meta': {'written': '2026-10-01', 'by': 'build_studio45.py', 'n_facts': len(F),
                'privacy': 'The street and the neighbourhood, as the owner gave them; never a house number, a block, a point or coordinates of the studio.'},
       'facts': F}
json.dump(out, open(os.path.join(HERE, 'studio45.json'), 'w'), indent=1, ensure_ascii=False)
print('wrote studio45.json', len(F), 'facts')
