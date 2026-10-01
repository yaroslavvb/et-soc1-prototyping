# Atoms to quarks, and the wrap: research notes (1 Oct 2026)


> **Corrected on 1 Oct 2026 (the ladder's build):** the channel is now TSMC N7's published 6 x 16.5 x 52 nm
> (process.json: n7.fin-width, n7.leff, n7.fin-height), not the 6 x 20 x 45 nm inferred before: about 257,000 atoms,
> 5 x 10^-8 thermally freed electrons, 0.05 to 5.1 dopant atoms, 22 million quarks and 3.6 million electrons.
> `particles.json` is rebuilt with these numbers; the text below keeps the first draft's.

What this covers: the ladder's levels below the silicon crystal (the chip diagram's innermost node today is
`lib.si`, one 0.543 nm unit cell, in `inside.json`), down through the silicon atom, its inner electrons, the
silicon-28 nucleus, a proton or neutron, a quark (and, as a side branch, an electron) to the Planck length; a
dopant-atom side branch for the electronics; and the wrap that closes the ladder into a circle: zooming out past
"beyond what we can see" (`beyond` in `outside.json`) leads, through Glashow's cosmic uroboros, to the Planck length and
the quarks, and Up from there climbs back through the atom and the FinFET into a memory cell or a compute cell.

Files:

- `particles.json`: the levels, the early-universe time track (`epochs`), the stellar origin of the chip's silicon
  (`stardust`), shared constants, and the proposed loop links. Built by `build_particles.py` (all derived numbers are
  computed there from the sourced inputs; rerun it after changing any input).
- `particles-src/`: local copies of what was read (NIST pages, PDG 2026 tables and reviews as PDF and text, IAEA query
  results, arXiv abstracts, the Primack and Abrams chapter, the TSMC and IBM patents, the Ioffe pages).

Kinds follow the chip page's vocabulary (DESIGN.md section 4.2): `outside` (a published source), `generic` (a
textbook), `derived` (arithmetic on sourced numbers; badge "model"), `inferred` (rests on an inference, such as the
chip page's inferred 6 x 20 x 45 nm channel; badge "inference"), `hypothesis` (speculative), `unknown`. The wrap
level's size kind is `conceptual`: it has no size.

---

## 1. Primary sources used, and what each gave

| key | source | values taken |
|---|---|---|
| codata | NIST, 2022 CODATA recommended values (physics.nist.gov/cuu, each constant's page) | Si lattice parameter a = 5.431 020 511(89) x 10^-10 m; proton rms charge radius 0.840 75(64) fm; Planck length 1.616 255(18) x 10^-35 m, Planck time 5.391 247(60) x 10^-44 s; electron mass 9.109 383 7139(28) x 10^-31 kg = 0.510 998 950 69 MeV; e = 1.602 176 634 x 10^-19 C (exact); proton 938.272 089 43 MeV, neutron 939.565 421 94 MeV; Bohr radius 52.917 721 054 pm; classical electron radius 2.817 940 3205 fm; k = 8.617 333 262 x 10^-5 eV/K; hbar c = 197.326 9804 MeV fm; u = 1.660 539 068 92 x 10^-27 kg |
| nist-iso | NIST Atomic Weights and Isotopic Compositions, Si | Si-28 27.976 926 534 65(44) u, 92.223(19)%; Si-29 4.685(8)%; Si-30 3.092(11)%; standard atomic weight [28.084, 28.086] |
| nist-asd | NIST Atomic Spectra Database, ionization energies Si I-XIV | ground state [Ne]3s2 3p2 (3P0); successive ionization energies 8.15168, 16.34585, 33.49300, 45.14179, 166.767, ... 2437.658, 2673.178 eV |
| iaea | IAEA LiveChart data service, 28Si | rms charge radius 3.1224(24) fm (Angeli & Marinova, ADNDT 99, 69 (2013)); binding energy 8447.7445 keV per nucleon and mass 27.976 926 534 42 u (AME2020); stable |
| pdg | Particle Data Group 2026 (F. Takahashi et al., Int. J. Mod. Phys. A 41, 2630011 (2026)): summary tables and reviews 2, 15, 22, 24 | m_u = 2.16 +/- 0.07 MeV, m_d = 4.70 +/- 0.07 MeV (MS-bar, 2 GeV); gluon mass 0 (theoretical; "a mass as large as a few MeV may not be precluded"); proton radius (mu-p Lamb shift) 0.840 75(64) fm, with the note that mu-p and e-p values are "much too different to average"; proton lifetime > 2.4 x 10^34 yr (p -> e+ pi0); neutron mean life 878.3 +/- 0.4 s; neutron <r^2> = -0.1155(17) fm^2; electron (g-2)/2 = 1159.652 180 62(12) x 10^-6, EDM < 0.041 x 10^-28 e cm, lifetime > 6.6 x 10^28 yr; number of neutrino types 2.996 +/- 0.007; T0 = 2.7255(6) K; n_gamma = 410.73 cm^-3; eta = 6.04(12) x 10^-10; Yp = 0.2448(33); z* = 1089.92(25), t* = 372.6(10) kyr; t0 = 13.797(23) Gyr; t T_MeV^2 = 2.4 N(T)^-1/2 (eq. 22.44) and the N(T) table (4N = 69 just below the QCD transition, 205 just above, 427 above the top mass); BBN "at the end of the first three minutes", nuclei form once T falls to about 0.1 MeV, abundances fixed by t ~ 180 s, no significant heavier nuclei; baryogenesis needs B, C and CP violation and departure from equilibrium; confinement: physical states are colour singlets |
| zeus | ZEUS Collaboration, Phys. Lett. B 757, 468 (2016), arXiv:1604.01280 | 95% CL upper limit on the effective quark radius 0.43 x 10^-16 cm = 4.3 x 10^-19 m |
| gabrielse | Gabrielse group page "Limit on Electron Substructure" (Northwestern CFP), citing D. Bourilkov, PRD 64, 071701(R) (2001) | LEP contact-interaction search at the 10 TeV scale: electron radius R < 2 x 10^-20 m; the g-factor agreement with point-particle QED as the substructure test |
| yang | Y.-B. Yang et al., PRL 121, 212001 (2018) | proton mass: quark energy 33(4)(4)%, glue field energy 37(5)(4)%, trace anomaly 23(1)(1)%, quark condensate (u, d, s masses) 9(2)(1)% |
| durr | S. Duerr et al., Science 322, 1224 (2008) | lattice QCD reproduces the light hadron (proton, neutron) masses |
| krane | K. S. Krane, Introductory Nuclear Physics (1988), ch. 3 | R = R0 A^(1/3), R0 about 1.2 fm |
| hossenfelder | S. Hossenfelder, Living Rev. Relativ. 16, 2 (2013) | whether a minimal length exists is open; thought experiments and approaches to quantum gravity suggest one |
| planck1899 | M. Planck, Sitzungsber. Preuss. Akad. Wiss. Berlin (1899), 440-480 | origin of the natural units |
| primack | J. R. Primack and N. E. Abrams, The View from the Center of the Universe (Riverhead, 2006), ch. 6 "What Size is the Universe? The Cosmic Uroboros" (chapter text at ncatlab.org/nlab/files/PrimackSizeOfUniverse.pdf) | the uroboros: tail tip = Planck length (~10^-33 cm), head = cosmic horizon (~10^28 cm), "about 60 orders of magnitude"; "Adapting an idea of Sheldon Glashow"; two meanings (gravity may link largest and smallest; at the start of the Big Bang head and tail nearly touched); humans "just about at the center"; note 4: Glashow's first version reproduced in T. Ferris, NYT Magazine, 26 Sep 1982, p. 38; see Glashow with B. Bova, Interactions (1988), ch. 14 |
| planck-vi, planck-x | Planck 2018 VI (A&A 641, A6) and X (A&A 641, A10) | base LambdaCDM (as in outside.json); n_s = 0.9649 +/- 0.0042, r < 0.056: data fit simple slow-roll inflation |
| fixsen | D. J. Fixsen, ApJ 707, 916 (2009) | T0 = 2.72548(57) K |
| nasa | NASA Science: "Cosmic History" (science.nasa.gov/universe/overview/), "Big Bang and the Evolution of the Universe" (Physics of the Cosmos), "COBE's Top Discoveries" | CMB at 380,000 years when "the universe had cooled enough that atomic nuclei could capture electrons"; "the oldest light we can observe"; fluctuations are "seeds that grew into the galaxies"; COBE: variations of 1 part in 100,000; nucleosynthesis in the first minutes |
| hotqcd | A. Bazavov et al. (HotQCD), PLB 795, 15 (2019) | QCD chiral crossover T_c = 156.5 +/- 1.5 MeV |
| ew | M. D'Onofrio and K. Rummukainen, PRD 93, 025003 (2016) | Standard Model electroweak crossover T_c = 159.5 +/- 1.5 GeV |
| cern2017 | CERN press release, "Quark Matter 2017: understanding the early universe" (9 Feb 2017) | lead-lead collisions recreate the quark-gluon plasma, "temperatures more than 100,000 times hotter than the centre of the Sun" |
| leconte | G. Leconte-Chevillard, Synthese 207 (2026), doi:10.1007/s11229-026-05476-2 | Zel'dovich's "the universe is the poor man's accelerator"; 1970s helium-4 limit on lepton families |
| ssg | G. Steigman, D. N. Schramm, J. E. Gunn, PLB 66, 202 (1977) | cosmological (helium) limit on the number of neutrino types (not read; cited via leconte) |
| johnson | J. A. Johnson, Science 363, 474 (2019) | silicon from exploding massive stars, with a share from exploding white dwarfs |
| woosley | S. E. Woosley, A. Heger, T. A. Weaver, RMP 74, 1015 (2002) | oxygen burning in massive stars makes silicon |
| connelly | J. N. Connelly et al., Science 338, 651 (2012) | oldest solar-system solids 4567.30 +/- 0.16 Myr |
| usgs | L. A. Corathers (USGS), Geotimes (2003) | silicon: second most abundant element in Earth's crust, more than 25% by weight |
| ioffe | Ioffe Institute NSM Archive, Si pages | band gap 1.12 eV (300 K); n_i = 1 x 10^10 cm^-3; density 2.329 g/cm3; dielectric constant 11.7; electron affinity 4.05 eV; donor ionization energies P 0.045, As 0.054, Sb 0.043 eV; acceptor B 0.045 eV |
| clementi | E. Clementi and D. L. Raimondi, J. Chem. Phys. 38, 2686 (1963) (via Wikipedia's table, checked against the raw table) | Si effective nuclear charge 1s 13.575, 2s 9.020, 2p 9.945, 3s 4.903, 3p 4.285 |
| cordero | B. Cordero et al., Dalton Trans. 2008, 2832 | covalent radii Si 111(2), P 107(3), B 84(3), As 119(4), Ge 120(4) pm |
| kittel | C. Kittel, Introduction to Solid State Physics, 8th ed., ch. 3 Table 1 | Si cohesive energy 4.63 eV per atom (from memory of the standard table; worth a glance if a copy is at hand) |
| tsmc-pat | TSMC, US 11,107,923 B2 (priority 14 Jun 2019) | n-type S/D: Si, SiC, SiCP, SiP ("tensile strain"); p-type S/D: SiGe, first layer 10-40% Ge, second 20-80% Ge, dopants B, BF2, In at 5 x 10^20 to 1 x 10^22 cm^-3 ("compressive strain"); wells: n-type P, As, Sb and p-type B, BF2, In, at or below 10^18 (typically 10^16-10^18) cm^-3; LDD 10^15-10^19 cm^-3; contact metals listed generically (W, Co, Cu ... with Ti/TiN liners) |
| ibm-pat | IBM, US 10,431,502 B1 (priority 16 Apr 2018) | "In 7 nm node technology and beyond, contact resistivity of less than 2e-9 ohm cm2 is desired for both nFET and pFET"; Si:P and SiGe:B source/drain contacts |
| tdf2016 | C. Edwards, Tech Design Forums, 24 Oct 2016 (on Wu et al., TSMC, IEDM 2016 paper 2.6) | "an epitaxially raised source and drain design that strains the transistor channel"; "a contact structure designed to reduce resistance"; 0.027 um2 SRAM; 256 Mbit SRAM to 0.5 V |

Not found or not usable: TSMC's own research page and the IEDM 2016 paper text (403 or paywalled); the PhilArchive
copy of Leconte-Chevillard (Cloudflare; Crossref gave the bibliographic record); NASA's old WMAP pages (moved to
science.nasa.gov); Rudnick and Gao's crust table (PDF blocked; the USGS statement is used instead).

## 2. The levels (inside to out on the main path)

Sizes and zooms as in `particles.json` (frame = 1.5 x size unless noted; zoom = this frame / child frame).

| id | what | size | kind | frame | zoom to child |
|---|---|---|---|---|---|
| `lib.si` (exists) | unit cell | 0.543 nm | outside | (5.43e-10) | 1.54 to p.atom |
| `p.atom` | a silicon atom | 0.2352 nm (sqrt(3)/4 a: neighbour spacing) | derived | 3.53e-10 | 5.5 |
| `p.dopant` (side) | P or B in a Si site | same | derived | 3.53e-10 | |
| `p.core` (optional) | the 10 inner electrons | 42.6 pm (2 x 4 a0 / 9.945) | derived | 6.39e-11 | 5,860 (the empty jump) |
| `p.nucleus` | Si-28 nucleus | 7.29 fm (2 x 1.2 x 28^(1/3)); measured rms 3.1224 fm, uniform-sphere diameter 8.06 fm | outside (formula) | 1.09e-14 | 4.3 |
| `p.nucleon` | proton (neutron) | 1.6815 fm (2 x 0.84075) | outside | 2.52e-15 | 1,950 |
| `p.quark` | a quark | none known; < 4.3 x 10^-19 m radius | outside (bound) | 1.29e-18 | 5 x 10^16 |
| `p.electron` (side) | an electron | none known; < 2 x 10^-20 m | outside (bound) | 6e-20 | 2.5 x 10^15 |
| `p.planck` | Planck length | 1.616 x 10^-35 m | outside | 2.42e-35 | conceptual |
| `p.wrap` | the cosmic uroboros | no size | conceptual | none | conceptual |

Key verified or derived numbers by level (full text in `particles.json`):

- **Atom.** 14 electrons, 2-8-4; the four valence electrons cost 8.15, 16.35, 33.49, 45.14 eV to remove, the
  fifth 166.8 eV, the last 2,673 eV (NIST ASD). Neighbour spacing 0.235 nm, 49.9 atoms/nm3 = 5.0 x 10^22 cm^-3
  (derived from CODATA a). Cohesive energy 4.63 eV/atom, about 2.3 eV per bond (Kittel). Isotopes 92.2/4.7/3.1%.
  **Electronics:** band gap 1.12 eV vs kT = 25.85 meV (43x); n_i about 10^10 cm^-3 = one free electron per
  5 x 10^12 atoms; the inferred 6 x 20 x 45 nm channel (about 270,000 atoms, `inside.json`) holds on average
  5 x 10^-8 thermally freed electrons, i.e. none: it conducts only when the gate pulls electrons in from the source.
  All the chip's channels: at least 6 x 10^15 atoms, 0.3 to 1 microgram (inferred; >24 billion transistors).
- **Dopant (electronics).** Donors P 45 meV, As 54 meV; acceptor B 45 meV (Ioffe), about 2 kT, so nearly all
  ionized. TSMC patent: n-type S/D Si:P or SiCP (tensile), p-type S/D SiGe with 10-80% Ge doped with boron at
  5 x 10^20 to 10^22 cm^-3 (compressive); wells 10^16-10^18 cm^-3. 10^21 cm^-3 = one dopant per nm3 = 1 atom in 50;
  10^22 = 1 in 5. Heavy doping makes the metal-semiconductor (Schottky) barrier thin enough to tunnel; 7 nm target
  contact resistivity < 2 x 10^-9 ohm cm2 (IBM patent). In the channel, 10^16-10^18 cm^-3 would be 0.05-5.4
  dopant atoms: random dopant counts would scatter thresholds, hence nearly undoped fins with work-function-metal
  threshold setting (generic; N7's channel doping is not published: unknown).
- **Inner electrons.** 1s peak at a0/13.575 = 3.9 pm; 2p at 4 a0/9.945 = 21 pm (hydrogen-like with Clementi's
  effective charges; valid for nodeless orbitals only, so no 3s/3p numbers are printed). Outer electrons around
  118 pm: 5 to 30 times farther out.
- **Nucleus.** 14 p + 14 n, stable. R = 1.2 A^(1/3) = 3.64 fm (diameter 7.3 fm); measured rms 3.1224 fm (equivalent
  uniform sphere R = 4.03 fm, so r0 = 1.33 fm for this light nucleus: the 1.2 fm rule is a rough average). 99.97%
  of the atom's mass. Density 2.3 x 10^17 kg/m3 (a teaspoon about 1.1 billion tonnes). Atom/nucleus width about
  32,000 (a 1 cm marble nucleus gives a 320 m atom). Binding 8.448 MeV/nucleon, 237 MeV total, 0.9% mass defect;
  a million times the chemical/electronic energies.
- **Nucleon.** r_p = 0.84075 fm (and the proton radius puzzle); m_p/m_e = 1836; uud / udd; free neutron 878.3 s,
  stable in Si-28; neutron <r^2> negative; proton lifetime > 2.4 x 10^34 yr. 84 valence quarks per Si-28 atom
  (42 u + 42 d); about 23 million quarks and 3.8 million electrons in one channel (inferred).
- **Quark.** Radius < 4.3 x 10^-19 m (ZEUS), so the proton is at least 1,955 times wider; u 2.16, d 4.70 MeV
  (MS-bar 2 GeV; scheme-dependent), 2u + d = 9.0 MeV = 1% of the proton; lattice breakdown 9/33/37/23% (Yang);
  lattice reproduces the mass (Duerr); gluons massless in theory, eight colour states; confinement. Uncertainty
  estimate hbar c / 0.84 fm = 235 MeV per quark (inferred, order of magnitude).
- **Electron.** e exact; m_e; radius < 2 x 10^-20 m (LEP); g measured to about 1 part in 10^13 and consistent with
  a point particle; EDM < 4.1 x 10^-30 e cm, i.e. its charge is centred to within 4.1 x 10^-32 m (derived); the
  classical radius 2.818 fm is not its size; stable (> 6.6 x 10^28 yr); 1 C = 6.24 x 10^18 electrons.
- **Planck length.** 1.616 x 10^-35 m, 5.39 x 10^-44 s; Planck 1899; whether it is a minimum is open (hypothesis);
  the quark limit is 3 x 10^16 Planck lengths: 16 powers of ten unexplored; Planck length to the observable
  universe's diameter (8.739 x 10^26 m, `outside.json`) is 61.7 powers of ten.

## 3. The wrap, designed honestly

**What the uroboros is.** Primack and Abrams (2006, ch. 6), "adapting an idea of Sheldon Glashow", draw a serpent
swallowing its tail: the tail's tip is the Planck length, the head the cosmic horizon, "about 60 orders of
magnitude" apart. They give two meanings: (1) gravity, irrelevant from bacteria to atoms, becomes strong again at the
tail's tip, so it may link the largest and smallest sizes (string theory and quantum gravity; untested); (2) at the
start of the Big Bang the largest scale was not much larger than the smallest; the serpent's body filled in as the
universe expanded. Their note 4 credits Glashow's first version to a 1982 New York Times Magazine article by Tim Ferris
and to Glashow's book Interactions (1988, ch. 14); neither was read directly, so the page should credit "Sheldon
Glashow's idea, as drawn by Primack and Abrams" and draw its own ring, not copy their art.

**What is not true, and the page must say so.** Zooming out past the observable universe does not reach quarks:
space does not loop back, and nothing in measured physics lies "past" the observable universe in the ladder's sense
(`beyond` already marks the multiverse as speculative). The ring is a picture. Proposed wording on `p.wrap`:
"This is not further out in space. The ring is a picture of all the sizes at once; the links across it are physics."
The readout shows "conceptual link" (no size), and the move should animate along the ring rather than as a zoom.

**What is true, and makes the ring more than a picture** (all sourced, in `epochs` and `stardust`):

1. *Looking out is looking back.* The farthest light, the CMB, left at z* = 1089.92, 372,600 years after the Big Bang,
   when the universe was 2,973 K (derived) and the region that is now our observable universe was 85 million
   light-years across (derived). Further back: the first nuclei at about three minutes and 0.1 MeV (1.2 billion K),
   that region then about 200 light-years across (derived); quarks bound into protons and neutrons at the QCD
   crossover, 156.5 MeV (1.8 x 10^12 K), 14-24 microseconds after the Big Bang, the region 3,700-5,300 AU across
   (derived via PDG eq. 22.44 and entropy conservation); the Higgs field took its value at 159.5 GeV, about 9 ps,
   the region about 3 AU across; before the Planck time (5.4 x 10^-44 s) known physics stops. So "out" in the ladder
   meets "small and hot" in time: the early universe was "the poor man's accelerator" (Zel'dovich).
2. *A neat coincidence of scales:* at the QCD crossover the typical thermal wavelength hbar c / kT = 1.26 fm is the
   size of a proton (derived; order of magnitude).
3. *The universe as an accelerator, with a result:* helium made in the first minutes limited the number of neutrino
   types in 1977 (Steigman, Schramm, Gunn); LEP and SLC later measured 2.996 +/- 0.007 (PDG). The LHC recreates the
   quark-gluon plasma with lead collisions, more than 100,000 times hotter than the Sun's core (CERN 2017).
4. *The chip's own atoms link the top and bottom.* Its protons and neutrons first formed at the QCD crossover; no
   silicon came out of the Big Bang (nothing heavier than lithium); silicon was made by oxygen burning in massive
   stars and spread by supernovae (and some white-dwarf explosions); the Solar System formed from that enriched gas
   4,567 million years ago; silicon is more than 25% of Earth's crust. So the atoms in the chip's fins were forged in
   stars of the Milky Way (inference built on these sources). This is the one link on the ring that is a physical
   history, not an analogy.
5. *Galaxies from the tiny:* the CMB's 1-part-in-100,000 variations (COBE) were the seeds of galaxies (NASA); in
   the leading theory, inflation (supported by Planck 2018's n_s and r, not proven), those seeds were quantum
   fluctuations stretched from sub-atomic to cosmic size. Mark as hypothesis.
6. *Matter itself:* about 1.66 billion CMB photons per baryon (eta = 6.04 x 10^-10); in the standard reading a tiny
   matter excess survived annihilation and became every proton, the chip's included (inferred); why is unknown.
7. *The middle of the ring:* the log-midpoint between the Planck length and the observable universe is 0.12 mm,
   about a minion's 4 KB L1 data cache or one shire SRAM panel (chip sizes are the page's order-of-magnitude
   inferences). Primack and Abrams put humans near the centre with their round numbers; with exact values the
   centre is about 4 powers of ten below human size, so the page should state the 0.12 mm and not repeat "humans
   are at the centre" as fact.

**Proposed loop** (`particles.json` `loop`). Up (zoom out): `universe -> beyond -> p.wrap -> p.planck -> p.quark ->
p.nucleon -> p.nucleus -> p.core -> p.atom -> lib.si -> lib.channel -> lib.fin -> lib.finfet -> lib.sram6t (memory)
or lib.fa (compute) -> a placed instance (shire.panel.array or vpu.lane.fma.tree) -> ... -> die -> package -> ...
-> universe`. In (double-click): the reverse, with `p.planck -> p.wrap -> beyond -> universe`, so the tail tip leads
into the head both ways. Side branches: `p.atom -> p.electron -> p.planck` and `p.dopant` beside `p.atom`. The memory
or compute exit can be offered as two buttons on the wrap, alternate per turn, or follow the way the viewer came
down (default: the memory cell). The epochs can be a strip on the wrap level ("looking out = looking back") or steps
between `beyond` and `p.planck`; they are times and temperatures, not sizes, so the readout must switch units or
show "conceptual" there. The long steps (`p.core -> p.nucleus` about 5,900x through empty space, `p.quark ->
p.planck` about 5 x 10^16 through unexplored scales) should be "jump" moves with a drawn factor far below the true
one, as the outside ladder does for its long steps.

## 4. Caveats and open questions

- The channel volume (6 x 20 x 45 nm), fins per transistor, N7's channel doping and N7's actual source/drain recipe are
  not published; the patent figures are embodiments, not N7 statements. Facts that rest on them are `inferred`.
- Quark masses are scheme-dependent (MS-bar at 2 GeV); "1% of the proton" is an illustration, the lattice 9% figure is
  the better-defined statement.
- The proton radius: CODATA 2022 and PDG's mu-p value agree at 0.84075 fm; PDG still declines to average e-p values.
- Region sizes at past epochs assume the Standard Model's degrees of freedom and entropy conservation (derived, model).
- The Kittel cohesive energy (4.63 eV) and the Krane R0 (1.2 fm) are textbook values not re-read today.
- Nothing in these levels touches the owner's location, accounts or infrastructure; the pages stay public-safe.
