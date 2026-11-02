# The deep zoom's generated pictures (31 Oct – 1 Nov 2026, Q135)

The owner's ask, Sat 31 Oct 2026: *"Improve the images at the higher end of the scale, milky way, observable universe,
etc, by generating appropriate prompts, generating images using AGy/antigravity and using them in place of current
diagrams in https://spacesheep.dev/@yaroslavvb/et-soc1-chip-diagram . Look at the extreme levels only (ie, above studio
45, and below individual atoms)"*.

Thirteen pictures, drawn by Antigravity (`agy -p`, its image-generator subagent, model pro) from the prompts in
`prompts.json`, now carry the levels in space and below the atom, on both pages that share the ladder (the chip diagram
and the memory levels). Each is an illustration, not a photograph or a measurement, and the page says so: the scene's tag
reads "AI illustration", and its panel credits the picture beside any photo it still shows. The drawings' numbers, seats,
rings and scale bars stay the page's own, laid over the pictures, so every zoom still lands where it did and every number
still has its fact.

## Files

| File | What |
|---|---|
| `prompts.json` | the style lines, the credit and licence the panels show, and one prompt per picture: its file, its scene(s), its width, the take used (`take`), a reference picture (`ref`) and notes |
| `draw.py` | draws each picture with `agy -p`, one at a time, into `~/.cache/agy-raw/ladder-img/<id>[-<take>].png` (out of git and Dropbox; the takes are not committed) |
| `make_webp.py` | puts each take on the night sky (screen-blended over `#070b17`, the space levels' backdrop and the particle scenes' window, so a picture's black edges are the sky's) and writes `docs/reports/ladder-img/<file>` as WebP, no metadata; `--measure` prints where a picture's light is |
| `make_refs.py` | `refs/earth-ref.png`: the page's own globe (Natural Earth's land, orthographic at 38 N 100 W, from the chip diagram's `research/outside-geo.json`), the map Antigravity painted Earth over |

## Rebuilding

```bash
cd docs/reports/data/2026-10-01-ladder/images
~/git0/flush-util/agy_signin --check        # agy must be signed in on this machine
./make_refs.py && python3 draw.py           # the pictures still missing (--only <id> --force to redraw one)
./make_webp.py                              # then the chip diagram's build (docs/reports/MIRROR.md, its row)
```

A redrawn picture is a new picture: its geometry below must be measured again (`./make_webp.py --measure <id>`, and by
eye on a gridded copy) and the scene's constants in `sources/ladder-outer.js` or `sources/ladder-inner.js` set to it.

## Where each scene places its picture

Positions are fractions of the picture (x from its left, y from its top). Space scenes are drawn in the drawing's units
(the frame `VB`, 1400 wide); particle scenes fit their square picture to the smaller side `s` of their picture box.

| Scene | Picture | Placement and seats |
|---|---|---|
| Beyond | `beyond.webp` | our universe is the middle bubble, (0.500, 0.500), radius 0.221 of the picture: on the circle `B` (radius 122), so the picture is 553 units wide; the labels sit under its lower-left and lower-right bubbles |
| The observable universe | `universe.webp` | the sphere, centre (0.500, 0.506), radius 0.465: on the drawn circle (radius 330, to scale), 710 units wide; the WMAP sky map stays as an inset |
| Laniakea | `laniakea.webp` | the cloud's radius about 0.41: on `R` (290), 707 units wide; its flow lines meet at (0.395, 0.40), where the convergence mark now is; the Local Group's mark stays at (0.204, 0.286), on the cloud's edge |
| The Local Group | `localgroup.webp`, `milkyway.webp` | Andromeda's core (0.503, 0.504) and Triangulum's (0.576, 0.205) on their places (2.5 and 3.0 million light-years from the Milky Way, to scale): the picture turned 18.05 degrees and 311.8 units wide. The Milky Way is the next level's own picture at an eighth of its size, where the jump into that level seats it (85 units, its middle 3 units under the mark), so the jump shows the same galaxy growing. The galaxies are drawn about 6 times their size (the Milky Way's disc 71 units for 12; Andromeda's 142 for 18–26), and the tag says so; the Large Magellanic Cloud moved out to just past the enlarged disc |
| The Milky Way | `milkyway.webp` | the bar's middle, the centre, at (0.500, 0.495); the disc, 100,000 light-years, 0.84 of the picture (680 units): the Sun 26,000 light-years below the centre, at (0.500, 0.713); the 20,000 light-year bar 114 units |
| The nearest stars | `stars.webp` (take b) | its Sun at (0.498, 0.498) on the frame's middle; the middle of α Centauri's three stars at (0.346, 0.354), 0.209 of the picture away, at the 4.2 light-years the mark stood for: so 703 units wide, its edges feathered. Take a put the pair 0.266 away, which would have made the picture 553 units wide, its starfield ending in a square inside the frame |
| The Solar System; Earth and the Moon | `starfield.webp` | a backdrop 1,500 units wide under the orbits, which stay drawn to scale; turned half round under Earth and the Moon. It replaced a first take of the Solar System, the Sun in a warm haze reaching past Uranus's orbit, which no real dust does |
| Earth | `earth-globe.webp` | painted over `refs/earth-ref.png`: its coastlines lie within a few pixels of the drawn ones (checked by drawing the reference's coastlines over it), its disc 0.44 of the picture as the reference's, so the US box still frames the US map the camera zooms into; 705 units wide (radius 310). In Earth and the Moon the same picture is Earth, to scale (11 units). The Blue Marble stays as the inset |
| The silicon-28 nucleus | `nucleus.webp` | the cluster's radius about 0.37 of `s`; the camera goes into the proton at its front middle, (0.502, 0.502), radius 0.077; the legend's colours sampled from the picture (proton `#d86454`, neutron `#b9b9c2`) |
| A proton | `proton.webp` | the sphere's radius 0.446; the quarks red (0.500, 0.296), green (0.676, 0.602) and blue (0.325, 0.607), labelled up, up and down (their colours stand for colour charge); the camera goes into the blue one |
| A quark; an electron | `quark.webp`, `electron.webp` | the point at the middle, its haze fading out by 0.40 of `s`, inside the measured limit's circle (0.42) |
| The Planck length | `foam.webp` | spacetime foam, a hypothesis, fills the ruler's unexplored box (`xMidYMax slice`: its dense bottom at the Planck end); the ruler stays the page's |

## What stayed drawn, and why

- The maps (the United States, California, the Bay Area, San Francisco, Bernal Heights, 29th Street): they are true maps
  from the US Census and DataSF outlines, nested to the kilometre (each zoom lands on the next map's outline), and the two
  innermost keep the studio's place unshown (AGENT.md §10). A generated picture would invent geography; none was made.
- The orbits of the Solar System and of the Moon, the 4.2 light-year circle, the drawn universe's circle, the scale bars
  and every printed number: they are the page's measurements; the pictures go under them.
- The photos the page had besides its diagrams: the WMAP sky map and the Blue Marble stay as insets. NASA/JPL-Caltech's
  artist's concept of the Milky Way and the GALEX Andromeda gave way to the generated pictures (the first was itself an
  illustration; the second would have sat on the generated Andromeda).

## Sizes

The 13 pictures are about 490 KB of WebP (`zoom_static.py` T9 now allows 900 KB for the folder, 150 KB a picture: each is
fetched only when the camera nears its level). Dropping the drawn globe's 8 KB outline from the page data and the
diagrams' code left the chip diagram 10.5 KB smaller (1,486,515 bytes of 1,500,000).
