# Outside the chip, up to the universe: research for the chip diagram's outer levels (30 Sep 2026)

For the owner's request of 30 Sep 2026 (~16:25 PDT) on
[The ET-SoC-1, interactively](https://spacesheep.dev/@yaroslavvb/et-soc1-chip-diagram): zoom out from the chip to the
card, the rack, Studio 45, San Francisco, the US, Earth, the Milky Way, Andromeda, and the universe.
This file is the research; `outside.json` is the data the page is built from (every level: size, a beginner line,
facts with their source and kind, image, drawing plan, where the next level in sits).

## Files (written in the session's work directory, ~/claude/work/chipzoom/; since the build of 30 September the
scripts and the JSON are in this directory, the images in `docs/reports/chip-diagram-img/` under short names: rack.webp,
card.webp, earth.webp, milkyway.webp, andromeda.webp, cmb.webp; the rack photo's redaction has nine labels since the
design's review and ten since the final check of 1 October, see make_rack_photo.py)

| File | What |
|---|---|
| `outside.json` | 18 levels, package to "beyond". Built by `outside/build_outside.py` (all derived numbers computed there). |
| `outside-geo.json` | Map outlines as SVG path data in km, with true scale: San Francisco, the nine Bay Area counties, California, the 48 states, an Earth globe. Built by `outside/make_geo.py`; previews in `outside/geo/preview-*.png`. 42.7 KB. |
| `rack-photo-page.webp` | The owner's rack photo for the page: 1000 x 988, 145.9 KB, no EXIF/XMP/ICC, **8 machine labels blurred** (they carry host names and LAN IP addresses). `outside/make_rack_photo.py`. |
| `card-photo-page.webp` | The vendor's dev-card photo (et-man, Apache-2.0), 720 x 479, transparent background, 75.2 KB. Also serves the package level (crop). |
| `earth-bluemarble-page.webp` | NASA Blue Marble (west), 400 x 400, 19.3 KB, public domain. |
| `milkyway-pia10748-page.webp` | NASA/JPL-Caltech/R. Hurt Milky Way artist's concept, 480 x 480, 8.4 KB. |
| `andromeda-pia15416-page.webp` | NASA/JPL-Caltech GALEX Andromeda, 480 x 357, 19.3 KB. |
| `cmb-wmap9-page.webp` | NASA/WMAP nine-year sky map, 400 x 200, transparent outside the ellipse, 22.7 KB. |
| `outside/` | Working files: the scripts, the downloaded sources (Census shapefiles, Natural Earth, the NASA/ESO images, the dev-card PDF's extracted images, the Laniakea paper), crops used to check the photo. |

## The ladder

Sizes in metres. "Frame" is a suggested view width for the camera; "x" is the zoom factor from the level inside it
(the die, 25.6 mm, for the package). Optional levels bridge long steps; every level the owner named is required.

| id | Level | Size (m) | Kind of size | Frame (m) | x | Image |
|---|---|---|---|---|---|---|
| package | The package | 0.045 | spec (datasheet Fig. 9-1) | 0.06 | 2.3 | crop of the card photo + drawn |
| card | The PCIe card | 0.1676 | spec (6.6 in, dev-card drawing) | 0.19 | 3.2 | vendor photo (Apache-2.0) |
| host | The host computer | 0.45 | estimate | 0.5 | 2.6 | drawn (+ crop of the rack photo) |
| rack | The rack | 1.5 | estimate | 1.8 | 3.6 | the owner's photo |
| studio45 | Studio 45 | 20 | assumed | 25 | 14 | drawn, schematic |
| sf | San Francisco | 1.1e4 | derived (√ land area) | 1.8e4 | 720 | drawn map (Census) |
| bayarea | The Bay Area | 2.19e5 | derived (Census outlines) | 2.4e5 | 13 | drawn map (Census) |
| california | California (optional) | 1.06e6 | derived | 1.15e6 | 4.8 | drawn map (Census) |
| us | The United States | 4.509e6 | outside source | 5.0e6 | 4.3 | drawn map (Census) |
| earth | Earth | 1.2742e7 | outside source (NASA) | 1.5e7 | 3.0 | drawn globe (Natural Earth) + Blue Marble |
| moon | Earth and the Moon (optional) | 7.69e8 | outside source (NASA) | 9e8 | 60 | drawn |
| solar | The Solar System | 9.03e12 (Neptune's orbit) | outside source (NASA) | 1.1e13 | 12,000 | drawn |
| stars | The nearest stars (optional) | 1.9e17 (20 ly frame) | assumed | 1.9e17 | 17,000 | drawn |
| milkyway | The Milky Way | 9.46e20 (100,000 ly) | outside source (NASA) | 1.28e21 | 6,800 | NASA/JPL artist's concept |
| localgroup | The Local Group (Andromeda) | 9.46e22 (10 Mly) | outside source (NASA) | 1.04e23 | 81 | drawn map + GALEX Andromeda |
| laniakea | Laniakea | 4.94e24 (160 Mpc) | outside source (Tully et al. 2014) | 5.9e24 | 57 | drawn, schematic |
| universe | The observable universe | 8.74e26 (92 Gly) | derived (Planck 2018 parameters) | 9.6e26 | 162 | drawn + WMAP map |
| beyond | Beyond (speculative) | unknown | hypothesis | 2.6e27 | 2.7 | drawn, marked speculative |

"Andromeda Cluster" is taken as the Local Group (there is no Andromeda cluster; the Local Group panel says so);
"meta universe" as the observable universe plus one speculative level, which the page names as the owner's word.

**For the camera.** Five steps are long: Studio 45 to San Francisco (x720), Earth to the Moon's orbit (x60), the
Moon's orbit to the Solar System (x12,000), the Solar System to the nearest stars (x17,000) and on to the galaxy
(x6,800). Without the optional levels, the Solar System to the Milky Way is x10^8. A leg's time should grow with the
log of the ratio but be capped (memory-levels' `legNew` shares a capped move's time out by nominal widths), and the
nearly empty frames in between need a cue (a scale bar that keeps counting, or the powers of ten).

## The levels, briefly (full facts, sources and kinds in outside.json)

**Package.** 45.0 x 45.0 mm FCBGA, 44.8 mm lid, at most 3.95 mm tall, 2,494 balls of 0.50 mm (datasheet Fig. 9-1,
p. 33; the heatsink page already cites the same). More than 30,000 bumps to the die (Hot Chips 33, via the heatsink
page), so the substrate fans out about 12 bumps per ball: the beginner's "why a package". The die, 570 mm²
(25.6 x 22.2 mm), sits under the lid; its position is not documented (drawn centred, labelled). The vendor photo's
lid reads "ET-SoC-1 ... A0 ... 2217 ES TT TAIWAN" (Table 10-1 explains the scheme except "TT"); the lab cards'
markings are not recorded. The datasheet has no thermal ratings. Light crosses the die in 0.085 ns; one 600 MHz tick
is 50 cm of light.

**Card.** ET-PCIe Dev Card V3: 6.6 x 4.4 in (167.6 x 111.8 mm), x16 card edge carrying x8 Gen 4 (measured on all four
lab cards: 16 GT/s x8; DMA 12.5-12.6 GB/s to the card, E50). Four LPDDR4X packages, 256 bits, 32 GB (peak 119.5 GB/s
on these cards, whose firmware runs the DRAM at 3,733 MT/s on every card (dram.rate-card, dram.peak-card); the
datasheet's 4,266 MT/s would give 136.5 GB/s; tensor loads measured at 75 GB/s). 12 V in, at most 7.3 A / 88 W (p. 5); highest draw on record 87.8 W;
idle 19-36 W by card. The cores run at about 0.52 V at 600 MHz (E9): 23 times below 12 V, so 23 times the current.
The TI TPSM831D31 (3 phases up to 120 A for the cores, 1 phase 40 A for the network): **its four phases are the four
"R15" inductors on the photo** (inferred; a nice thing to point at): three of them feed the cores, the fourth the
on-chip network. LTM4680 (SRAM, 60 A), FS1406s (other rails), LTC4218
hot-swap with a 1 mΩ sense resistor, ATSAMD20 "PMIC micro" (reads the 12 V input and three regulators). eMMC (a
Kingston part on the photo, U17), FTDI UART-USB (U28), DIP switches, JTAG, fan header P1. **Not recorded: the lab
cards' heatsinks and fans** (the heatsink page, §1); the vendor photo shows the card bare, with SK hynix DRAM (a
second photo in the same PDF shows Micron). Photo hotspot boxes are in outside.json (720 x 479 px, 4.30 px/mm; the
photo's lid measures 44.8 mm at that scale, a check on the 6.6 in width).

**Host.** From the repository: aifoundry1 i7-11700K, 128 GB; aifoundry2 i5-11600, 64 GB; aifoundry3 i7-11700K, 32 GB
on one channel (14-card-behaviour.md:348); aifoundry1 has two cards (hosts.txt). New today: **aifoundry2's board is a
Gigabyte Z590 AORUS MASTER** (read from this host's world-readable DMI table, /sys/devices/virtual/dmi/id: vendor,
board name, BIOS F5; no card access, no sudo), an ATX board of 30.5 x 24.4 cm (Gigabyte). aifoundry1's and
aifoundry3's boards were not read (that needs a Tailscale login); their BIOS versions F5/F6 follow Gigabyte's naming,
and the photo shows AORUS boards. The host CPUs are Intel 14 nm with 20 PCIe 4.0 lanes, the i7-11700K rated 125 W
base power and up to 251 W in turbo (PL2; i5-11600 65 W base): the whole ET card's 88 W maximum is below the bigger
CPU's base power and about a third of its turbo peak. An ATX supply is 150 x 86 x 140 mm (the ATX12V design guide). Host memcpy 17.4 / 9.2 / 21.4
GB/s. The frame size (~45 cm) is an estimate.

**Rack.** The owner's photo: a chrome wire shelving rack, about ten open-frame machines on two shelves (five a
shelf, some partly hidden), tower coolers (Cooler Master logos), Gigabyte AORUS boards, EVGA 650 GS / 1000 GS and
MSI MPG A750GF supplies, a "KVM#8" label and a keyboard on the shelf above. About 1.5 m wide (estimate; make and size
not recorded). **Which machines are the lab's three is not recorded.** (Four of the supplies carry a sticker of the
E.T. film's moon-and-bicycle silhouette. It might mark the ET machines, but that is a guess: ask, do not print it.)

**Studio 45.** The page gives only the owner's word: the lab's room, in San Francisco, is called Studio 45. **No
public page links AI Foundry, Ainekko or Esperanto to it.** Public listings and event pages describe the venue, but
they show its street address, and after the facts review of 1 October the page cites none of them: it adds nothing
to the zoom and would make the place easy to find (AGENT.md §10). The page never marks a position on the SF map: the
Studio 45 inset sits beside the city's outline, off the map. Its size is not recorded: the 20 m frame is an
assumption, and the drawing is labelled schematic.

**San Francisco.** 46.92 sq mi (121.51 km²) of land, so about 11 km across (Wikipedia from the Census); fibre at
c/1.4682 (Corning SMF-28e+) is 4.90 µs per km: 54 µs across the city, some 32,000 ticks of the chip's clock.
Esperanto was headquartered in Mountain View, about 50 km south (Business Wire, 1 May 2023): the chip was designed on
the Bay Area map.

**Bay Area.** Nine counties, 18,040 km² of land, 7.77 million people (Wikipedia); 204 x 219 km on the Census outlines;
about 1 ms in fibre.

**California (optional).** 423,970 km²; about 1,060 km north to south on the map; 5.2 ms in fibre.

**United States.** 4,509 km on the longest great circle inside the lower 48 (Wikipedia). SF to New York 4,129 km on a
great circle (computed from the two city centres): 13.8 ms for light, **20.2 ms in fibre, one way, on a straight
cable** (the brief's "~20 ms across the US"); real routes are longer.

**Earth.** Mean radius 6,371.000 km, equatorial 6,378.137 km (NASA fact sheet): 12,742 km across; light around the
equator in 134 ms, 80 million ticks.

**Earth and the Moon (optional).** 384,400 km (NASA): 1.28 s for light, 770 million ticks.

**Solar System.** Neptune's semimajor axis 30.07 au, about 4,498 million km (NASA fact sheet's orbital parameters:
30.06896348 AU; the same sheet's 4,514.953 x 10^6 km is 30.18 au, a different epoch's elements): light 4.2 h; to
Earth 8.3 min. **Voyager 1 reaches one light-day from Earth on 18 November 2026** (NASA), seven weeks after this
page: a timely beginner fact.

**Nearest stars (optional).** Proxima Centauri 4.2 light-years (NASA).

**Milky Way.** About 100,000 light-years across, at least 100 billion stars (NASA): the chip's 24 billion transistors
are about one per four stars. The Sun is about 26,000 ly from the centre, in the Orion Spur. The NASA picture is an
artist's concept (say so). Its geometry was measured: it has the same artwork and framing as ESO's annotated version
(eso1339e; correlation 0.977 at scale 1, no shift), whose distance rings put the frame at about 135,400 ly (the builder's own measurement: inferred) and the Sun
at (0.500, 0.691) of the square: the page can draw its own "you are here" and scale bar.

**Local Group.** More than 30 galaxies over nearly 10 million light-years (NASA Imagine the Universe); counted to
today's faint dwarfs, 134 members within a megaparsec and 5.11 Mpc (17 million ly) across (Wikipedia, "Local Group",
read 1 Oct 2026). There is no "Andromeda cluster": Andromeda is a galaxy, which with the Milky Way leads this group;
the nearest true cluster, Virgo (about 1,300 galaxies, 54 million ly away), lies further out inside Laniakea. Andromeda 2.5
million ly away, 260,000 ly across (NASA/JPL PIA15416 caption); M33 3 million ly; the LMC 160,000 ly. The collision
once dated to ~4.5 billion years is now about 50% within 10 billion years and under 2% within 5 (Sawala et al.,
Nature Astronomy 2025, "No certainty of a Milky Way-Andromeda collision").

**Laniakea.** 160 Mpc (about 520 million ly) across if taken as round, 10^17 solar masses, defined by the watershed of
galaxy flows (Tully, Courtois, Hoffman & Pomarède, Nature 513, 71, 2014); about 100,000 galaxies (NRAO release);
Hawaiian for "immeasurable heaven".

**Observable universe.** Radius 46.2 billion ly comoving, diameter 8.7 x 10^26 m, computed here from Planck 2018's
parameters (H0 67.66, Ωm 0.3111, radiation from 2.7255 K, Neff 3.046), which also give an age of 13.79 billion years
(Planck: 13.787 ± 0.020). The CMB left its source ~380,000 years after the Big Bang; 2.7255 K today (Fixsen 2009).
No light-travel time is given for this level: its size is a comoving distance.

**Beyond (speculative).** Space is flat to Ω_K = 0.001 ± 0.002 (Planck 2018 with BAO), so it very likely extends far
past the horizon; one Bayesian analysis gives more than 251 Hubble volumes (Vardanyan, Trotta & Silk 2011), under its
assumptions. A multiverse (eternal inflation, the string landscape; Guth 2007) is a hypothesis, not an observation.
Size unknown; no scale bar.

## Images: credits and licences

| File | Credit | Licence |
|---|---|---|
| rack-photo-page.webp | Photo: the page's author (the repository's owner), 2026; machine labels blurred | His own photo, used on his page at his request; no open licence stated |
| card-photo-page.webp | Esperanto Technologies, "PCIe Dev Card (V3)" (ET-PCIe-Dev-Card-V3.pdf, p. 2), in github.com/aifoundry-org/et-man | Apache License 2.0 (that repository's LICENSE) |
| earth-bluemarble-page.webp | NASA Goddard Space Flight Center, "The Blue Marble" (Visible Earth 57723, globe_west): image by Reto Stöckli, enhancements by Robert Simmon, MODIS data | Public domain (NASA content is generally not copyrighted in the US; credit NASA) |
| milkyway-pia10748-page.webp | NASA/JPL-Caltech/R. Hurt (SSC/Caltech), PIA10748 (artist's concept) | JPL image use policy: any purpose without prior permission; credit "NASA/JPL-Caltech" |
| andromeda-pia15416-page.webp | NASA/JPL-Caltech, GALEX, PIA15416 (ultraviolet) | JPL image use policy, as above |
| cmb-wmap9-page.webp | NASA / WMAP Science Team, "Nine Year Microwave Sky" | Public domain (NASA) |
| outside-geo.json | US Census Bureau 2023 cartographic boundary files (county 1:500k, state 1:5M); Natural Earth 1:110m land | Public domain (both) |

Not used: ESA/Gaia and Planck images (CC BY-SA 3.0 IGO: usable with credit, but share-alike, and NASA's
public-domain equivalents exist); ESO's annotated Milky Way (used only to measure the NASA picture's geometry); no
Laniakea image is openly licensed (the Nature figure and the CEA/SDvision renderings are not), so it is drawn.

## The rack photo: what was done, and a finding

- The original (1500 x 1429 WebP) has no EXIF, XMP or GPS; its only metadata is a plain sRGB ICC profile.
- **It shows eight tape labels on the machines, and at full resolution some are partly legible as host names and
  what look like private IP addresses (10.x.x.x).** AGENT.md §10 keeps IPs out of public pages, so the page copy
  pixelates and blurs all eight (`make_rack_photo.py` lists the boxes; checked at 3x zoom that no character
  survives). The PSU barcode stickers and the "KVM#8" label are illegible or harmless and left alone.
- Then: the 53-px black band on the left cropped, resized to 1000 px wide (Lanczos), a 0.5-px blur (the carpet's
  texture is what costs bytes), WebP q70: 145.9 KB, written with no EXIF/XMP/ICC.
- **The original should not be published anywhere as is.**

## Budget

The built page is 681.6 KB now. The six images are 290.8 KB, 387.8 KB as base64; outside-geo.json 42.7 KB: about
430 KB for the outside levels, so about 1.11 MB before the inside levels (a parallel stage's inside.json is 256 KB of
data) and the camera code. Easy savings if needed: the rack photo at 900 px (~125 KB), the Earth photo dropped in
favour of the drawn globe (-26 KB as base64), the Bay Area at 0.6 km tolerance.

## Drawing notes for the builder

- Every drawn level gets a true scale bar (the geo data is in km; photos carry px/mm or ly/px in outside.json).
- Label unstroked text while the camera moves (engineering note 3 of the brief).
- The zoom into San Francisco lands on the city's centre point, never on the lab; Studio 45 is drawn as a small
  schematic square labelled "position not shown".
- The host level is drawn from the ATX standard (305 x 244 mm; aifoundry2's board is exactly that), the card upright
  in a slot; an ATX supply is 150 x 86 x 140 mm (the ATX12V design guide: an outside source to cite if drawn).
- The Milky Way and the Local Group are artist's concepts or maps: say so under each.
- The CMB map is the whole sky seen from inside, not the universe seen from outside: say so.
- "Beyond" is speculative and says so in its title.

## Unknowns, and questions for the owner or the lab

1. Which three machines in the rack are the lab's (and are the E.T.-sticker supplies the ET machines?).
2. The lab cards' heatsinks and fans (also open in the thermal-camera plan, question 4).
3. The rack's make and size; the room's size (Studio 45).
4. aifoundry1's and aifoundry3's board models (a read of /sys/devices/virtual/dmi/id/board_name on each).
5. The lab cards' own package markings and DRAM maker (a photo of a lab card would settle both).
6. Whether the owner wants his name in the rack photo's credit ("Photo: Yaroslav Bulatov") or "the author".

## Sources

Repository: `docs/findings/14-card-behaviour.md` (:138 peak power, :338 clock, :339 idle, :348 hosts),
`docs/findings/05-claims.md` (:34 core voltage, :155 DRAM rate, :550-553 PCIe and copies),
`docs/reports/data/2026-09-27-pcie/hosts.txt`, `docs/reports/data/2026-09-27-chip-diagram/facts.json` (L47,
dram.channels, board.meters, chip.die-area, chip.die-dims, chip.process), `docs/reports/sources/esperanto-without-heatsink.body.html`
(§1, refs [3] Hot Chips 33, R1, R2), AGENT.md §10. Vendor: ET-SoC-1 Preliminary Datasheet Rev 1.0 (Fig. 9-1 p. 33,
Table 10-1 p. 34, §9.1) and ET-PCIe-Dev-Card-V3.pdf (pp. 1-5, 8, 10), both in github.com/aifoundry-org/et-man (read
from the main checkout's `external/et-man`, read-only). The host's DMI table (aifoundry2, 30 Sep 2026).

Outside: BIPM SI Brochure (c); IAU 2012 B2 (au), IAU 2015 B2 (pc); Corning SMF-28e+ product sheet (group index
1.4682); Gigabyte Z590 AORUS MASTER specifications; Intel Core i7-11700K / i5-11600 specifications (the 11700K's 251 W PL2 as cpu-monkey.com and techreviewer.com
list it); Intel ATX12V Power Supply Design Guide; Wikipedia: San Francisco, San Francisco Bay Area, Geography of
California, Contiguous United States, Local Group, Virgo Cluster; Business Wire, Esperanto
release of 1 May 2023; NASA NSSDCA Earth, Moon and Neptune fact sheets; NASA "Where are
Voyager 1 and Voyager 2 now?"; NASA Hubble, Proxima Centauri microlensing prediction; NASA "Beyond Our Solar System"
poster; NASA/JPL-Caltech ssc2008-10b / PIA10748 and ESO eso1339e; NASA Imagine the Universe, The Local Group; NASA/JPL
PIA15416; NASA Hubble Messier 33; NASA APOD 2013-05-28; Sawala et al., Nature Astronomy (2025); Tully et al., Nature
513, 71 (2014), arXiv:1409.0880; NRAO release, 3 Sep 2014; Planck 2018 results VI, A&A 641, A6 (2020),
arXiv:1807.06209; Fixsen, ApJ 707, 916 (2009); NASA/WMAP nine-year map; Vardanyan, Trotta & Silk, MNRAS 413, L91
(2011), arXiv:1101.5476; Guth, J. Phys. A 40, 6811 (2007), arXiv:hep-th/0702178; NASA image guidelines; JPL image
use policy; US Census Bureau cartographic boundary files 2023; Natural Earth.
