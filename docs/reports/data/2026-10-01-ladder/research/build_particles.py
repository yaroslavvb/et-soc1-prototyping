#!/usr/bin/env python3
"""Build particles.json: the ladder's levels below the silicon crystal (atom, nucleus,
nucleon, quark, electron, Planck length) and the wrap from the outermost level back to
them (the cosmic uroboros), with an early-universe time track.

Every printed number is a fact with a kind (DESIGN.md section 4.2 vocabulary:
measured, spec, derived, inferred, outside, generic, owner, hypothesis, unknown;
badges: derived -> "model", inferred -> "inference", outside -> "outside source",
generic -> "outside source - textbook", hypothesis -> "speculative").
Derived numbers are computed here from the sourced inputs, so they can be re-checked.

Sources read 1 Oct 2026; local copies under particles-src/.
Run: python3 build_particles.py  (writes particles.json next to this file)
"""
import json, math, os

HERE = os.path.dirname(os.path.abspath(__file__))

# ---------------------------------------------------------------- sourced inputs
# CODATA 2022 (NIST values pages)
A_SI = 5.431020511e-10        # m, lattice parameter of silicon
R_P = 0.84075e-15             # m, proton rms charge radius
L_P = 1.616255e-35            # m, Planck length
T_P = 5.391247e-44            # s, Planck time
M_E_KG = 9.1093837139e-31     # kg
M_E_MEV = 0.51099895069       # MeV
M_P_MEV = 938.27208943        # MeV
M_N_MEV = 939.56542194        # MeV
E_CHARGE = 1.602176634e-19    # C, exact
A0 = 5.29177210544e-11        # m, Bohr radius
R_E_CLASSICAL = 2.8179403205e-15  # m
K_B_EV = 8.617333262e-5       # eV/K, exact
HBARC = 197.3269804           # MeV fm
U_KG = 1.66053906892e-27      # kg, atomic mass constant
M_E_U = 548.579909044e-6      # u (PDG 2026)
K_PER_MEV = 1.160451812e10    # K per MeV (CODATA eV-kelvin relationship)
# NIST isotopic compositions / IAEA LiveChart (AME2020, Angeli & Marinova 2013)
M_SI28_U = 27.97692653442     # u (AME2020 via IAEA)
RMS_SI28 = 3.1224             # fm, rms charge radius
BA_SI28 = 8.4477445           # MeV per nucleon
# NIST ASD ionization energies of Si (eV): Si I .. Si XIV
IE = [8.15168, 16.34585, 33.49300, 45.14179, 166.767, 205.279, 246.57, 303.59,
      351.28, 401.38, 476.273, 523.415, 2437.65805, 2673.177958]
# Clementi & Raimondi 1963 effective nuclear charges for Si
ZEFF_1S, ZEFF_2P = 13.575, 9.945
# PDG 2026
M_U, M_D = 2.16, 4.70         # MeV (MS-bar, 2 GeV)
ETA = 6.04e-10                # baryon-to-photon ratio (BBN)
N_GAMMA = 410.73              # CMB photons per cm^3
T0 = 2.7255                   # K
Z_STAR = 1089.92              # redshift of last scattering
T_STAR_KYR = 372.6            # age at z*, kyr
# other outside sources
Q_RADIUS = 0.43e-18           # m, ZEUS 2016 95% CL upper limit on effective quark radius
E_RADIUS = 2e-20              # m, LEP contact-interaction bound (via Gabrielse group page)
EDM_E_CM = 0.041e-28          # e cm, PDG 2026 electron EDM limit
TC_QCD = 156.5                # MeV, HotQCD 2019
TC_EW = 159.5e3               # MeV, D'Onofrio & Rummukainen 2016
BAND_GAP = 1.12               # eV at 300 K (Ioffe NSM archive)
N_I = 1e10                    # cm^-3 intrinsic carriers at 300 K (Ioffe)
# the channel at TSMC N7's published fin and gate (process.json: n7.fin-width 6 nm, n7.leff 16.5 nm, n7.fin-height
# 52 nm; 1 Oct 2026, replacing the chip page's earlier inference of 6 x 20 x 45 nm)
CH_W, CH_L, CH_H = 6, 16.5, 52  # nm
# the outside ladder (outside.json): observable universe diameter, derived from Planck 2018
U_DIAM = 8.738988638177877e26  # m
LY = 9.4607304725808e15        # m
AU = 1.495978707e11            # m

# ---------------------------------------------------------------- derived
bond = math.sqrt(3) / 4 * A_SI
n_si = 8 / A_SI ** 3                                  # atoms per m^3
n_si_cm3 = n_si * 1e-6
r1s = A0 / ZEFF_1S                                    # hydrogenic most-probable radius, 1s
r2p = 4 * A0 / ZEFF_2P                                # hydrogenic most-probable radius, 2p
R_nuc = 1.2 * 28 ** (1 / 3)                           # fm, R0 A^(1/3)
R_unif_meas = math.sqrt(5 / 3) * RMS_SI28             # fm, uniform sphere with the measured rms
m_nuc_u = M_SI28_U - 14 * M_E_U
frac_nuc = m_nuc_u / M_SI28_U
rho_nuc = m_nuc_u * U_KG / (4 / 3 * math.pi * (R_nuc * 1e-15) ** 3)
atom_over_nuc = bond / (2 * R_nuc * 1e-15)
B_tot = BA_SI28 * 28
uud = 2 * M_U + M_D
qbound_over_planck = Q_RADIUS / L_P
orders_total = math.log10(U_DIAM / L_P)
log_mid = math.sqrt(U_DIAM * L_P)
kT300 = K_B_EV * 300
V_ch_nm3 = CH_W * CH_L * CH_H
atoms_ch = V_ch_nm3 * n_si * 1e-27
gs0 = 2 + 7 / 8 * 2 * 3 * 4 / 11                       # entropy dof today, 3.909


def region(T_K, gs):
    """Physical diameter then of the region that is today's observable universe
    (entropy conservation: a T gs^(1/3) = const)."""
    return U_DIAM * (gs0 / gs) ** (1 / 3) * T0 / T_K


def t_of_T(T_MeV, N):
    """PDG Big-Bang cosmology eq. 22.44: t T_MeV^2 = 2.4 N^(-1/2) (seconds)."""
    return 2.4 / math.sqrt(N) / T_MeV ** 2


def sig(x, n=3):
    return float(f"{x:.{n}g}")


def sci(x, d=1):
    """'5.0 x 10^22' style, for text."""
    e = math.floor(math.log10(abs(x)))
    m = x / 10 ** e
    if round(m, d) >= 10:
        m /= 10
        e += 1
    return f"{m:.{d}f} x 10^{e}"


def rnd(x, n=2):
    """round to n significant figures, as an integer with thousands separators"""
    return f"{int(float(f'{x:.{n}g}')):,}"


# ---------------------------------------------------------------- sources
S = {
    "codata": "NIST, 2022 CODATA recommended values of the fundamental physical constants, physics.nist.gov/cuu/Constants (each constant's values page, read 1 Oct 2026)",
    "nist-iso": "NIST, Atomic Weights and Isotopic Compositions for Silicon, physics.nist.gov/cgi-bin/Compositions/stand_alone.pl?ele=Si (read 1 Oct 2026)",
    "nist-asd": "NIST Atomic Spectra Database, Ground levels and ionization energies, spectra Si I to Si XIV, physics.nist.gov/cgi-bin/ASD/ie.pl (read 1 Oct 2026)",
    "iaea": "IAEA Nuclear Data Section, LiveChart of Nuclides data service, 28Si ground state (nds.iaea.org/relnsd/v1/data?fields=ground_states&nuclides=28si, read 1 Oct 2026): charge radius from I. Angeli and K. P. Marinova, At. Data Nucl. Data Tables 99, 69 (2013); mass and binding energy from AME2020 (M. Wang et al., Chinese Phys. C 45, 030003 (2021))",
    "krane": "K. S. Krane, Introductory Nuclear Physics (Wiley, 1988), ch. 3: R = R0 A^(1/3) with R0 about 1.2 fm",
    "pdg-q": "Particle Data Group, F. Takahashi et al., Int. J. Mod. Phys. A 41, 2630011 (2026), summary table: quarks (pdg.lbl.gov/2026/tables/rpp2026-sum-quarks.pdf)",
    "pdg-b": "Particle Data Group, F. Takahashi et al., Int. J. Mod. Phys. A 41, 2630011 (2026), summary table: N baryons (p, n) (pdg.lbl.gov/2026/tables/rpp2026-sum-baryons.pdf)",
    "pdg-l": "Particle Data Group, F. Takahashi et al., Int. J. Mod. Phys. A 41, 2630011 (2026), summary table: leptons (pdg.lbl.gov/2026/tables/rpp2026-sum-leptons.pdf)",
    "pdg-g": "Particle Data Group, F. Takahashi et al., Int. J. Mod. Phys. A 41, 2630011 (2026), summary table: gauge and Higgs bosons, gluon (pdg.lbl.gov/2026/tables/rpp2026-sum-gauge-higgs-bosons.pdf)",
    "pdg-qm": "Particle Data Group (2026), review 15, Quark Model (C. Amsler, V. Crede et al., rev. Aug 2025), sec. 15.1-15.2",
    "pdg-astro": "Particle Data Group (2026), review 2, Astrophysical Constants and Parameters (D. E. Groom, D. Scott, rev. Aug 2025), Table 2.1",
    "pdg-bb": "Particle Data Group (2026), review 22, Big-Bang Cosmology (K. A. Olive, J. A. Peacock, rev. Aug 2025), sec. 22.3.2 (eq. 22.44, table of N(T)) and 22.3.6 (baryogenesis)",
    "pdg-bbn": "Particle Data Group (2026), review 24, Big Bang Nucleosynthesis (B. D. Fields, P. Molaro, S. Sarkar, rev. Aug 2025), sec. 24.1-24.2",
    "zeus": "ZEUS Collaboration, \"Limits on the effective quark radius from inclusive ep scattering at HERA\", Phys. Lett. B 757, 468 (2016), arXiv:1604.01280",
    "gabrielse": "G. Gabrielse group (Northwestern Center for Fundamental Physics), \"Limit on Electron Substructure\", cfp.physics.northwestern.edu/gabrielse-group/electron-substructure.html, citing D. Bourilkov, Phys. Rev. D 64, 071701(R) (2001) for the LEP contact-interaction limit",
    "yang": "Y.-B. Yang et al. (chiQCD), \"Proton mass decomposition from the QCD energy momentum tensor\", Phys. Rev. Lett. 121, 212001 (2018), arXiv:1808.08677",
    "durr": "S. Duerr et al., \"Ab initio determination of light hadron masses\", Science 322, 1224 (2008), arXiv:0906.3599",
    "hossenfelder": "S. Hossenfelder, \"Minimal length scale scenarios for quantum gravity\", Living Rev. Relativ. 16, 2 (2013), arXiv:1203.6191",
    "planck1899": "M. Planck, \"Ueber irreversible Strahlungsvorgaenge\", Sitzungsberichte der Koeniglich Preussischen Akademie der Wissenschaften zu Berlin (1899), pp. 440-480 (natural units of length, mass, time and temperature)",
    "primack": "J. R. Primack and N. E. Abrams, The View from the Center of the Universe (Riverhead, 2006), ch. 6, \"What Size is the Universe? The Cosmic Uroboros\" (chapter text: ncatlab.org/nlab/files/PrimackSizeOfUniverse.pdf)",
    "glashow": "S. L. Glashow's cosmic uroboros, as credited by Primack and Abrams (ch. 6, note 4): first version reproduced in T. Ferris, New York Times Magazine, 26 Sep 1982, p. 38; see also S. L. Glashow with B. Bova, Interactions (Warner Books, 1988), ch. 14 (not read directly)",
    "planck-vi": "Planck Collaboration, \"Planck 2018 results. VI. Cosmological parameters\", A&A 641, A6 (2020)",
    "planck-x": "Planck Collaboration, \"Planck 2018 results. X. Constraints on inflation\", A&A 641, A10 (2020), arXiv:1807.06211",
    "fixsen": "D. J. Fixsen, \"The temperature of the cosmic microwave background\", ApJ 707, 916 (2009)",
    "nasa-history": "NASA Science, \"Cosmic History\", science.nasa.gov/universe/overview/ (read 1 Oct 2026)",
    "nasa-cobe": "NASA Science, \"COBE's Top Discoveries\", science.nasa.gov/mission/cobe/science/ (read 1 Oct 2026)",
    "nasa-bb": "NASA Science, Physics of the Cosmos, \"Big Bang and the Evolution of the Universe\", science.nasa.gov/astrophysics/programs/physics-of-the-cosmos/big-bang-and-the-evolution-of-the-universe/ (read 1 Oct 2026)",
    "hotqcd": "A. Bazavov et al. (HotQCD), \"Chiral crossover in QCD at zero and non-zero chemical potentials\", Phys. Lett. B 795, 15 (2019), arXiv:1812.08235",
    "ew": "M. D'Onofrio and K. Rummukainen, \"Standard model cross-over on the lattice\", Phys. Rev. D 93, 025003 (2016), arXiv:1508.07161",
    "cern2017": "CERN press release, \"Quark Matter 2017: understanding the early universe\", 9 Feb 2017, home.cern",
    "leconte": "G. Leconte-Chevillard, \"'The poor man's accelerator', or how the primordial universe became a testing ground for particle physics\", Synthese 207 (2026), doi:10.1007/s11229-026-05476-2",
    "ssg": "G. Steigman, D. N. Schramm, J. E. Gunn, \"Cosmological limits to the number of massive leptons\", Phys. Lett. B 66, 202 (1977)",
    "johnson": "J. A. Johnson, \"Populating the periodic table: Nucleosynthesis of the elements\", Science 363, 474 (2019)",
    "woosley": "S. E. Woosley, A. Heger, T. A. Weaver, \"The evolution and explosion of massive stars\", Rev. Mod. Phys. 74, 1015 (2002)",
    "connelly": "J. N. Connelly et al., \"The absolute chronology and thermal processing of solids in the solar protoplanetary disk\", Science 338, 651 (2012)",
    "usgs": "L. A. Corathers (USGS), \"Mineral resource of the month: silicon\", Geotimes (2003), usgs.gov/publications/mineral-resource-month-silicon",
    "ioffe": "Ioffe Institute, NSM Archive, \"Silicon (Si): basic parameters\" and \"band structure and carrier concentration\" (www.ioffe.ru/SVA/NSM/Semicond/Si/), compiled from Sze, Shur and others",
    "sze": "S. M. Sze and K. K. Ng, Physics of Semiconductor Devices, 3rd ed. (Wiley, 2007), ch. 1 (crystal, bands, donors and acceptors)",
    "kittel": "C. Kittel, Introduction to Solid State Physics, 8th ed. (Wiley, 2005), ch. 3, Table 1 (cohesive energies): Si 4.63 eV per atom",
    "clementi": "E. Clementi and D. L. Raimondi, \"Atomic screening constants from SCF functions\", J. Chem. Phys. 38, 2686 (1963): Si Zeff 1s 13.575, 2p 9.945 (as tabulated in Wikipedia, \"Effective nuclear charge\")",
    "cordero": "B. Cordero et al., \"Covalent radii revisited\", Dalton Trans. 2008, 2832: Si 111(2) pm, P 107(3), B 84(3), As 119(4), Ge 120(4)",
    "tsmc-pat": "TSMC, US Patent 11,107,923 B2, \"Source/drain regions of FinFET devices and methods of forming same\" (priority 14 Jun 2019), description (a patent's embodiments, not a statement about N7)",
    "ibm-pat": "IBM, US Patent 10,431,502 B1, \"Maskless epitaxial growth of phosphorus-doped Si and boron-doped SiGe (Ge) for advanced source/drain contact\" (priority 16 Apr 2018), background",
    "tdf2016": "C. Edwards, \"7nm finFET process techniques lead IEDM lineup\", Tech Design Forums, 24 Oct 2016 (on S.-Y. Wu et al., TSMC, IEDM 2016 paper 2.6)",
    "chip:chip.process": "docs/reports/data/2026-09-27-chip-diagram/facts.json (chip.process): TSMC 7 nm, more than 24 billion transistors (Esperanto, Hot Chips 33 and IEEE Micro 2022)",
    "inside": "the chip diagram's own tree (docs/reports/data/2026-09-27-chip-diagram/research/inside.json: lib.channel, lib.si)",
    "outside": "the chip diagram's outside ladder (docs/reports/data/2026-09-27-chip-diagram/research/outside.json: universe, beyond)",
}


def F(text, kind, *refs, topic=None, note=None):
    f = {"text": text, "kind": kind, "refs": list(refs),
         "source": "; ".join(S[r] if r in S else r for r in refs)}
    if topic:
        f["topic"] = topic
    if note:
        f["note"] = note
    return f


# ---------------------------------------------------------------- levels
levels = []

levels.append({
    "id": "p.atom",
    "name": "A silicon atom",
    "attach": "below lib.si (the silicon crystal's unit cell)",
    "parent": "lib.si",
    "child": "p.core",
    "child_alt": ["p.electron", "p.dopant"],
    "optional": False,
    "size_m": sig(bond, 4),
    "frame_m": sig(1.5 * bond, 3),
    "size_kind": "derived",
    "size_note": f"the distance between neighbouring atoms in the crystal, sqrt(3)/4 x a = {bond*1e9:.4f} nm (a from CODATA 2022); each atom's share is a sphere of radius {bond/2*1e12:.1f} pm. Measured covalent radius 111 pm (Cordero 2008).",
    "blurb": "One of the crystal's atoms: a tiny nucleus with 14 electrons around it. Only the outer four take part in bonds and in electronics; the other ten sit deep inside, held 20 to 300 times more tightly.",
    "facts": [
        F("Silicon has 14 electrons: 2 in the first shell, 8 in the second and 4 in the third (ground configuration 1s2 2s2 2p6 3s2 3p2).", "outside", "nist-asd"),
        F(f"Removing the outer four electrons one at a time costs {IE[0]:.2f}, {IE[1]:.2f}, {IE[2]:.2f} and {IE[3]:.2f} eV; the fifth, the first of the inner ten, costs {IE[4]:.1f} eV, and the last (1s) electron {IE[13]:,.0f} eV.", "outside", "nist-asd", topic="electronics"),
        F("The four outer (valence) electrons each pair with an electron of a neighbouring atom: four covalent bonds pointing to the corners of a tetrahedron, which is what builds the diamond-cubic crystal.", "generic", "sze", topic="electronics"),
        F(f"In the crystal neighbouring atoms are {bond*1e9:.3f} nm apart, and there are {n_si*1e-27:.1f} atoms in every cubic nanometre ({sci(n_si_cm3)} per cm3).", "derived", "codata"),
        F("Breaking the crystal into free atoms costs 4.63 eV per atom: about 2.3 eV per bond, since each atom shares four bonds and each bond has two ends.", "generic", "kittel"),
        F("Natural silicon is 92.22% silicon-28, 4.69% silicon-29 and 3.09% silicon-30; its standard atomic weight is 28.084-28.086.", "outside", "nist-iso"),
        F(f"Band gap {BAND_GAP} eV at 300 K: an electron needs that much energy to leave its bond and move freely. The thermal energy kT at 300 K is {kT300*1000:.2f} meV, {BAND_GAP/kT300:.0f} times smaller.", "outside", "ioffe", "codata", topic="electronics",
          note="kT derived from the Boltzmann constant (exact)"),
        F(f"So pure silicon at room temperature has only about 10^10 free electrons per cm3: one for every {sci(n_si_cm3/N_I,0)} atoms.", "derived", "ioffe", "codata", topic="electronics"),
        F(f"A FinFET channel of about {CH_W} x {CH_L} x {CH_H} nm holds about {rnd(atoms_ch, 3)} silicon atoms and, on average, {sci(V_ch_nm3*1e-21*N_I,0)} thermally freed electrons: none. The transistor conducts only when the gate voltage pulls electrons in from the heavily doped source.", "inferred", "inside", "ioffe", topic="electronics",
          note="the channel's size is the chip page's inference (TSMC does not publish N7's); the conduction picture is the textbook MOSFET (Sze ch. 6)"),
        F(f"With more than 24 billion transistors and about {rnd(atoms_ch, 3)} atoms per fin's channel, the chip's channels hold at least {sci(24e9*atoms_ch,0)} silicon atoms: about {24e9*atoms_ch*M_SI28_U*U_KG*1e9:.1f} micrograms if each transistor has one fin, about a microgram if three. That is all the silicon that actually switches.", "inferred", "inside", "chip:chip.process",
          note="the transistor count is Esperanto's; fins per transistor and N7's channel size are not published, so this is an order of magnitude"),
        F(f"Its share of the crystal (a sphere of radius {bond/2*1e12:.0f} pm) is about {rnd(atom_over_nuc)} times wider than its nucleus.", "derived", "codata", "krane"),
    ],
    "draw": "Drawn SVG: the atom at the centre with its four bonds to the neighbours' edges (tetrahedral, 109.5 degrees, drawn in projection); a soft cloud for the four valence electrons; a small bright core labelled \"10 inner electrons and the nucleus\"; a scale bar of 0.1 nm. Reuses lib.si's ball-and-stick style.",
    "zoom_from_inner": None,
})

levels.append({
    "id": "p.dopant",
    "name": "A dopant atom (phosphorus or boron)",
    "attach": "a sibling of p.atom: an atom of the source or drain (lib.sd if the ladder adds it) or, rarely, of the channel",
    "parent": "lib.si",
    "child": "p.core",
    "child_alt": [],
    "optional": True,
    "size_m": sig(bond, 4),
    "frame_m": sig(1.5 * bond, 3),
    "size_kind": "derived",
    "size_note": "a substituted atom takes a silicon atom's place in the lattice; covalent radii P 107 pm, B 84 pm, As 119 pm, Ge 120 pm, Si 111 pm (Cordero 2008)",
    "blurb": "A foreign atom in a silicon atom's place. Phosphorus brings five outer electrons, one more than the bonds need, and that spare electron is free to carry current; boron brings three, leaving a gap (a hole) that carries current the other way. This is how a transistor's source and drain are made to conduct.",
    "facts": [
        F("Phosphorus and arsenic are donors in silicon: the spare electron is held by only 0.045 eV (P) or 0.054 eV (As). Boron is an acceptor, at 0.045 eV.", "outside", "ioffe", topic="electronics"),
        F(f"Those energies are only about 2 kT at room temperature (2 kT = {2*kT300*1000:.0f} meV), so nearly every dopant atom has given up (or taken) its electron.", "generic", "sze", "codata", topic="electronics"),
        F("In a TSMC FinFET patent, the n-type source/drain is epitaxial silicon or silicon carbide with phosphorus (Si:P, SiCP), which pulls the channel under tension; the p-type source/drain is silicon-germanium (10-40% germanium in the first layer, 20-80% in the second) doped with boron (5 x 10^20 to 10^22 per cm3 in the second layer), which squeezes the channel.", "outside", "tsmc-pat", topic="electronics",
          note="a patent's embodiments; TSMC does not say which apply to N7. Tension speeds electrons and compression speeds holes."),
        F("TSMC's IEDM 2016 7 nm paper describes epitaxially raised sources and drains that strain the channel, and a contact structure designed to reduce resistance.", "outside", "tdf2016"),
        F(f"10^21 dopant atoms per cm3 is one per cubic nanometre, among {n_si*1e-27:.0f} silicon atoms: about 1 atom in {n_si_cm3/1e21:.0f}. At 10^22, one in {n_si_cm3/1e22:.0f}.", "derived", "codata", topic="electronics"),
        F("So much doping is needed at the contacts: a metal on lightly doped silicon forms a barrier (a Schottky barrier); heavy doping makes it thin enough for electrons to tunnel through. For 7 nm-class technology a contact resistivity below 2 x 10^-9 ohm cm2 is the stated goal.", "outside", "ibm-pat", "sze", topic="electronics"),
        F(f"The same patent dopes the wells under the fins at 10^16 to 10^18 per cm3. At those levels a {CH_W} x {CH_L} x {CH_H} nm channel would hold on average {V_ch_nm3*1e-21*1e16:.2f} to {V_ch_nm3*1e-21*1e18:.1f} dopant atoms, among some {rnd(atoms_ch, 3)} silicon atoms: a handful at most, and their random number and place would make every transistor different. FinFET channels are therefore left nearly undoped and the threshold voltage is set by the gate metal instead.", "inferred", "tsmc-pat", "inside", "sze", topic="electronics",
          note="whether N7 dopes its channels, and how much, is not published (unknown); the count is arithmetic on an inferred volume and the patent's well range"),
    ],
    "draw": "Drawn SVG: the crystal view of p.atom with one atom recoloured (P or B, toggle), its spare electron (or hole) drawn as a large faint orbit several atoms wide; caption \"1 atom in 50 in the source and drain; maybe none in the channel\".",
    "zoom_from_inner": None,
})

levels.append({
    "id": "p.core",
    "name": "The inner electrons",
    "attach": "between p.atom and p.nucleus (a bridging level, like the outside ladder's optional levels)",
    "parent": "p.atom",
    "child": "p.nucleus",
    "child_alt": [],
    "optional": True,
    "size_m": sig(2 * r2p, 3),
    "frame_m": sig(3 * r2p, 3),
    "size_kind": "derived",
    "size_note": f"twice the most probable radius of a 2p electron in a hydrogen-like model with Clementi's effective charge 9.945: 4 a0 / 9.945 = {r2p*1e12:.1f} pm; the two 1s electrons peak at a0 / 13.575 = {r1s*1e12:.1f} pm",
    "blurb": "Ten electrons fill the first two shells, packed close around the nucleus. They are held so tightly that chemistry and electronics never move them; they only screen most of the nucleus's charge from the outer four.",
    "facts": [
        F(f"The 1s pair sits about {r1s*1e12:.1f} pm from the nucleus and the 2s and 2p eight about {r2p*1e12:.0f} pm: the outer four, around {bond/2*1e12:.0f} pm, are some 5 to 30 times farther out.", "derived", "clementi", "codata",
          note="hydrogen-like estimate with effective nuclear charges; good for the nodeless 1s and 2p orbitals"),
        F("The 1s electrons feel almost the full nuclear charge (an effective 13.6 of 14); the 3p electrons feel only 4.3, because the inner ten stand in between.", "outside", "clementi"),
        F(f"The innermost electron of a silicon atom is bound by {IE[13]:,.0f} eV, more than 300 times an outer electron's {IE[0]:.2f} eV.", "outside", "nist-asd"),
        F("An electron in an atom is not a little ball on an orbit: the shells are clouds of probability, and the radii here are where each cloud is densest.", "generic", "sze"),
    ],
    "draw": "Drawn SVG: radial-density rings (1s small and bright, 2s/2p a ring at about 21 pm), the valence cloud as a faint rim at the frame's edge; a scale bar of 10 pm.",
    "zoom_from_inner": None,
})

levels.append({
    "id": "p.nucleus",
    "name": "The silicon-28 nucleus",
    "attach": "the centre of p.atom",
    "parent": "p.core",
    "child": "p.nucleon",
    "child_alt": [],
    "optional": False,
    "size_m": sig(2 * R_nuc * 1e-15, 3),
    "frame_m": sig(3 * R_nuc * 1e-15, 3),
    "size_kind": "outside",
    "size_note": f"diameter from R = 1.2 fm x 28^(1/3) = {R_nuc:.2f} fm (Krane); the measured rms charge radius is {RMS_SI28} fm, which a uniform sphere of radius {R_unif_meas:.2f} fm would have. A nucleus has a soft edge, so any radius is a convention.",
    "blurb": "Fourteen protons and fourteen neutrons, packed together by the strong force: a thirty-thousandth of the atom's width but 99.97% of its mass. Nothing in a chip ever touches it.",
    "facts": [
        F("Silicon-28: 14 protons and 14 neutrons, stable.", "outside", "iaea"),
        F(f"Nuclear radius R = R0 A^(1/3) with R0 about 1.2 fm: for A = 28, R = {R_nuc:.2f} fm, about {2*R_nuc:.1f} fm across.", "generic", "krane"),
        F(f"Measured rms charge radius {RMS_SI28} +/- 0.0024 fm.", "outside", "iaea"),
        F(f"The nucleus holds {frac_nuc*100:.2f}% of the atom's mass; the 14 electrons, {100-frac_nuc*100:.3f}%.", "derived", "iaea", "pdg-l"),
        F(f"Its density is about {sci(rho_nuc)} kg per m3: a teaspoon (5 mL) of nuclear matter would weigh about {rho_nuc*5e-6/1e12:.1f} billion tonnes.", "derived", "iaea", "krane"),
        F(f"If the nucleus were a 1 cm marble, the atom's share of the crystal would be about {rnd(atom_over_nuc*0.01)} m across: an atom is almost all empty space.", "derived", "codata", "krane"),
        F(f"Binding energy {BA_SI28:.3f} MeV per nucleon, {B_tot:.0f} MeV in all: the nucleus weighs {B_tot/931.49410372/M_SI28_U*100:.1f}% less than its 28 separate parts (E = mc^2).", "outside", "iaea"),
        F(f"That is about a million times the energy of the outer electrons ({IE[0]:.2f} eV) or of a chemical bond (about 2.3 eV): why chemistry, and electronics, never change a nucleus.", "derived", "iaea", "nist-asd", "kittel"),
    ],
    "draw": "Drawn SVG: a cluster of 28 overlapping spheres (14 proton-coloured, 14 neutron-coloured) with a soft edge; scale bar 1 fm; a small inset showing the atom with the nucleus as an invisible dot (\"this is 1/32,000 of the atom\").",
    "zoom_from_inner": None,
})

levels.append({
    "id": "p.nucleon",
    "name": "A proton (and its twin, the neutron)",
    "attach": "one of the 28 nucleons in p.nucleus",
    "parent": "p.nucleus",
    "child": "p.quark",
    "child_alt": [],
    "optional": False,
    "size_m": sig(2 * R_P, 4),
    "frame_m": sig(3 * R_P, 3),
    "size_kind": "outside",
    "size_note": "twice the proton's rms charge radius, 0.84075(64) fm (CODATA 2022; PDG 2026)",
    "blurb": "A proton is three quarks (up, up, down) held by gluons; a neutron is up, down, down. Unlike the electron, it has a real size, because it is a bound state, and most of its mass is the energy of what goes on inside.",
    "facts": [
        F("Proton rms charge radius 0.84075 +/- 0.00064 fm.", "outside", "codata", "pdg-b"),
        F("Older electron-scattering measurements gave about 0.88 fm; muonic-hydrogen spectroscopy gave 0.84 fm, the 'proton radius puzzle'. The Particle Data Group still notes that the two kinds of measurement are not averaged.", "outside", "pdg-b"),
        F(f"Proton mass {M_P_MEV:.3f} MeV/c^2, neutron {M_N_MEV:.3f} MeV/c^2: each about {M_P_MEV/M_E_MEV:.0f} times an electron's.", "outside", "codata", "pdg-b"),
        F("Quark content: proton uud, neutron udd. Charges +2/3 e for up and -1/3 e for down give +1 and 0.", "outside", "pdg-b", "pdg-q"),
        F("A free neutron decays in 878.3 +/- 0.4 s on average; bound in silicon-28 it is stable.", "outside", "pdg-b", "iaea"),
        F("The neutron has no charge, but its charge is spread unevenly: its mean-square charge radius is negative (-0.1155 fm^2), meaning a positive core and a negative outer part.", "outside", "pdg-b"),
        F("No proton has ever been seen to decay: its lifetime exceeds 2.4 x 10^34 years for the decay to a positron and a pion (the universe is 1.4 x 10^10 years old).", "outside", "pdg-b", "pdg-astro"),
        F(f"Each silicon-28 atom holds 42 up and 42 down quarks (84 in all); a {CH_W} x {CH_L} x {CH_H} nm channel's ~{rnd(atoms_ch, 3)} atoms hold some {atoms_ch*84/1e6:.0f} million quarks and {atoms_ch*14/1e6:.1f} million electrons.", "inferred", "pdg-b", "inside",
          note="the per-atom count is arithmetic (derived); the channel count rests on the inferred channel size"),
    ],
    "draw": "Drawn SVG: a soft sphere 1.68 fm across with three coloured dots (red, green, blue: colour charge, not real colours) joined by wavy gluon lines, and faint quark-antiquark pairs; caption \"the dots are drawn far too big: a quark is less than 1/2000 of this\".",
    "zoom_from_inner": None,
})

levels.append({
    "id": "p.quark",
    "name": "A quark",
    "attach": "one of the three quarks drawn in p.nucleon",
    "parent": "p.nucleon",
    "child": "p.planck",
    "child_alt": [],
    "optional": False,
    "size_m": None,
    "size_bound_m": 2 * Q_RADIUS,
    "frame_m": sig(3 * Q_RADIUS, 3),
    "size_kind": "outside",
    "size_note": "no size has ever been measured: the 95% upper limit on a quark's effective radius is 0.43 x 10^-16 cm = 4.3 x 10^-19 m (ZEUS 2016). The frame shows the limit, not the quark.",
    "blurb": "As far as any experiment can tell, a quark is a point. The disc here is only the limit: if a quark has a size, it is smaller than this, under a two-thousandth of the proton. Quarks are never found alone; pull one out and the energy makes new quarks.",
    "facts": [
        F("Upper limit on the effective quark radius: 4.3 x 10^-19 m (95% confidence), from electron-proton collisions at HERA.", "outside", "zeus"),
        F(f"The proton is at least {R_P/Q_RADIUS:,.0f} times wider than a quark could be.", "derived", "codata", "zeus"),
        F(f"Masses (MS-bar at 2 GeV): up {M_U:.2f} +/- 0.07 MeV, down {M_D:.2f} +/- 0.07 MeV. Two ups and a down add to {uud:.1f} MeV: {uud/M_P_MEV*100:.0f}% of the proton's {M_P_MEV:.1f} MeV.", "derived", "pdg-q", "pdg-b",
          note="quark masses depend on the scheme and scale they are quoted at; the simple sum is an illustration"),
        F("A lattice-QCD breakdown of the proton's mass: the quarks' masses (through the quark condensate, u, d and s) give 9%, the quarks' energy of motion 33%, the gluon field's energy 37%, and the 'trace anomaly' 23%.", "outside", "yang"),
        F("Lattice QCD computes the proton's and neutron's masses from the quark and gluon theory, matching experiment.", "outside", "durr"),
        F("Gluons carry the strong force between quarks; they are massless in theory (a mass of a few MeV is not excluded) and come in eight colour states.", "outside", "pdg-g", "pdg-qm"),
        F("Colour is believed to be permanently confined: only colourless combinations (three quarks, or a quark and an antiquark) exist on their own.", "outside", "pdg-qm"),
        F(f"Squeezing quarks into 0.84 fm gives them energies around hbar c / r = {HBARC/0.84075:.0f} MeV each: why most of a proton's mass is energy rather than quark mass.", "inferred", "codata", "pdg-b",
          note="an uncertainty-principle estimate, order of magnitude only"),
    ],
    "draw": "Drawn SVG: a dashed circle labelled \"limit: 4.3 x 10^-19 m\" with a point at the centre that never grows; a scale bar of 10^-19 m; a side note \"no experiment has found any size\". Same treatment for p.electron.",
    "zoom_from_inner": None,
})

levels.append({
    "id": "p.electron",
    "name": "An electron",
    "attach": "one of the 14 electrons of p.atom (a side branch: double-click an electron cloud)",
    "parent": "p.atom",
    "child": "p.planck",
    "child_alt": [],
    "optional": False,
    "size_m": None,
    "size_bound_m": 2 * E_RADIUS,
    "frame_m": sig(3 * E_RADIUS, 3),
    "size_kind": "outside",
    "size_note": "no size has ever been measured: a search for contact interactions at the LEP collider puts any radius below 2 x 10^-20 m (as quoted by the Gabrielse group). The frame shows the limit.",
    "blurb": "The particle that carries every current in the chip. Its charge and mass are known to 10 digits, but no experiment has found any size: as far as we know it is a point. The 'cloud' of the atom is where the electron is likely to be, not the electron itself.",
    "facts": [
        F(f"Charge -1.602176634 x 10^-19 C, exactly (it defines the coulomb since 2019); mass {M_E_KG*1e31:.4f} x 10^-31 kg = {M_E_MEV:.5f} MeV/c^2.", "outside", "codata", topic="electronics"),
        F("A radius limit below 2 x 10^-20 m, from contact-interaction searches at LEP at the 10 TeV scale.", "outside", "gabrielse"),
        F("Its magnetic moment is measured to about 1 part in 10^13 ((g-2)/2 = 0.00115965218062(12)) and agrees with the theory of a point particle; an electron made of smaller parts would spoil that agreement.", "outside", "pdg-l", "gabrielse"),
        F(f"The electron is round: its electric dipole moment is below 4.1 x 10^-30 e cm (PDG 2026), so its charge sits within {sci(EDM_E_CM*1e-2,1)} m of its centre (dipole moment divided by its charge).", "derived", "pdg-l"),
        F("The 'classical electron radius', 2.818 fm, is a length built from its charge and mass, not its size.", "outside", "codata"),
        F("Stable: its lifetime exceeds 6.6 x 10^28 years.", "outside", "pdg-l"),
        F(f"Every coulomb that flows through the chip is {sci(1/E_CHARGE,2)} electrons.", "derived", "codata", topic="electronics"),
    ],
    "draw": "As p.quark: a dashed circle labelled \"limit: 2 x 10^-20 m\" around a point; scale bar 10^-20 m.",
    "zoom_from_inner": None,
})

levels.append({
    "id": "p.planck",
    "name": "The Planck length",
    "attach": "the floor of the ladder, below p.quark and p.electron",
    "parent": "p.quark",
    "child": "p.wrap",
    "child_alt": [],
    "optional": False,
    "size_m": L_P,
    "frame_m": sig(1.5 * L_P, 3),
    "size_kind": "outside",
    "size_note": "Planck length sqrt(hbar G / c^3) = 1.616255(18) x 10^-35 m (CODATA 2022)",
    "blurb": "The length built from gravity, quantum mechanics and the speed of light. Here, physicists expect space and time themselves to need a quantum description that nobody has yet; whether anything can be smaller is unknown. Between the quark's limit and here lie 16 powers of ten that no experiment has reached.",
    "facts": [
        F("Planck length 1.616255 x 10^-35 m; Planck time 5.391247 x 10^-44 s.", "outside", "codata"),
        F("Max Planck introduced these natural units of length, mass, time and temperature in 1899.", "outside", "planck1899"),
        F(f"The quark's radius limit is {sci(qbound_over_planck,0)} times the Planck length: some {math.log10(qbound_over_planck):.0f} powers of ten that no experiment has probed.", "derived", "zeus", "codata"),
        F("Whether the Planck length is a smallest possible length is an open question: thought experiments and several approaches to quantum gravity suggest a minimal length, and none is confirmed.", "hypothesis", "hossenfelder"),
        F(f"From the Planck length to the observable universe's diameter is {orders_total:.1f} powers of ten.", "derived", "codata", "outside"),
    ],
    "draw": "Drawn SVG, marked \"theory\": a foam-like texture fading in (labelled \"spacetime here may not be smooth; no one knows\"), no particles; a scale bar of 10^-35 m. The readout's mantissa shows 1.6 x 10^-35 m.",
    "zoom_from_inner": None,
})

levels.append({
    "id": "p.wrap",
    "name": "The cosmic uroboros (a conceptual link)",
    "attach": "above beyond (the outermost level) and below p.planck: the join that closes the ladder into a circle",
    "parent": "p.planck",
    "child": "beyond",
    "child_alt": ["e.cmb"],
    "optional": False,
    "size_m": None,
    "frame_m": None,
    "size_kind": "conceptual",
    "size_note": "Not a size. This step is a picture of all the scales at once, not a place: zooming out past the observable universe does not lead to anything physical, and the circle is an idea, not a continuation of space.",
    "blurb": "A serpent swallowing its tail: the physicist Sheldon Glashow's picture of all the sizes in nature, from the Planck length at the tail to the observable universe at the head. The circle is a way of seeing, not a place: the largest and smallest scales are joined by physics, not by distance. Looking far out is looking back in time, to an early universe that was a sea of quarks.",
    "honesty": "The page must say on this level, in words: \"This is not further out in space. The ring is a picture; the links across it are physics.\" The readout shows \"conceptual link\" instead of a size, and the move animates along the ring, not as a zoom.",
    "facts": [
        F("Joel Primack and Nancy Ellen Abrams, adapting an idea of Sheldon Glashow (Nobel 1979), drew the 'Cosmic Uroboros': the tip of the tail is the Planck length, the head is the cosmic horizon, about 60 powers of ten apart.", "outside", "primack", "glashow"),
        F("Their first meaning: gravity, negligible from bacteria to atoms, becomes strong again at the tail's tip, so it may link the largest and smallest sizes (a hope of quantum gravity and string theory, not yet tested).", "hypothesis", "primack"),
        F("Their second meaning: at the very beginning of the Big Bang the largest scale, the horizon, was not much larger than the smallest; the serpent's body filled in as the universe expanded.", "hypothesis", "primack",
          note="the horizon's growth from near-Planck size rests on extrapolating known physics back to the Planck time"),
        F("Looking out is looking back: the farthest light we can see, the cosmic microwave background, left 380,000 years after the Big Bang; before that the universe was hot, dense and opaque.", "outside", "nasa-bb", "nasa-history"),
        F("The early universe is 'the poor man's accelerator' (Zel'dovich): its first minutes reached energies that test particle physics.", "outside", "leconte"),
        F("Example: the helium made in the first three minutes limited how many kinds of neutrino could exist (Steigman, Schramm and Gunn, 1977); collider measurements of the Z boson later counted 2.996 +/- 0.007.", "outside", "ssg", "leconte", "pdg-l"),
        F(f"On a logarithmic scale the middle of the whole ladder, between the Planck length and the observable universe, is {log_mid*1e3:.2f} mm: about the size of a minion's 4 KB L1 data cache or one SRAM panel of the shire cache in this chip.", "derived", "codata", "outside", "inside",
          note="the two chip sizes are the chip page's order-of-magnitude inferences"),
        F("Primack and Abrams place human size near the centre of the uroboros, with their round numbers (10^-33 cm to 10^28 cm).", "outside", "primack"),
    ],
    "draw": "Drawn SVG, marked \"a picture, not a place\": a ring (the serpent) with the page's own levels as ticks around it at log-scale positions (Planck, quark, proton, nucleus, atom, fin, FinFET, cell, minion, shire, die, card, rack, Studio 45, San Francisco, Earth, Sun, Milky Way, Laniakea, observable universe), the head (universe) touching the tail (Planck). Three labelled chords across the ring: \"looking out = looking back in time\" (universe to quarks), \"the chip's atoms were made in stars\" (Milky Way to atom), \"gravity at both ends?\" (dashed: hypothesis). Our own drawing, not a copy of Glashow's or Primack's artwork.",
    "zoom_from_inner": None,
})

# ---------------------------------------------------------------- the time track (the wrap's content)
epochs = []
T_star_K = T0 * (1 + Z_STAR)
d_star = U_DIAM / (1 + Z_STAR)
epochs.append({
    "id": "e.cmb",
    "name": "The oldest light: 372,600 years",
    "time_s": T_STAR_KYR * 1e3 * 3.15576e7,
    "temperature_K": sig(T_star_K, 4),
    "region_m": sig(d_star, 3),
    "facts": [
        F("Last scattering at redshift z* = 1089.92 +/- 0.25, age 372.6 +/- 1.0 thousand years (Planck 2018 base model).", "outside", "pdg-astro", "planck-vi"),
        F(f"Then the universe was 1 + z* = {1+Z_STAR:.0f} times hotter than the CMB's {T0} K today: {T_star_K:,.0f} K, cool enough for electrons and nuclei to form atoms.", "derived", "pdg-astro", "fixsen", "nasa-history"),
        F(f"The region that is now our observable universe was then {d_star/LY/1e6:.0f} million light-years across.", "derived", "pdg-astro", "outside",
          note="today's comoving diameter divided by 1 + z*"),
        F("Its temperature varied by about 1 part in 100,000 from place to place (COBE): the seeds that grew into galaxies.", "outside", "nasa-cobe", "nasa-history"),
        F(f"That light is still all around: about {N_GAMMA:.0f} CMB photons in every cubic centimetre of space, at {T0} K.", "outside", "pdg-astro", "fixsen"),
        F("In the leading theory, inflation, those seeds began as quantum fluctuations on sub-atomic scales, stretched to the size of galaxies: the smallest scales shaping the largest. Planck's measurements fit simple inflation models; inflation is not proven.", "hypothesis", "planck-x"),
    ],
})
epochs.append({
    "id": "e.bbn",
    "name": "The first nuclei: about three minutes",
    "time_s": 180,
    "temperature_K": sig(0.1 * K_PER_MEV, 2),
    "region_m": sig(region(0.1 * K_PER_MEV, gs0), 2),
    "facts": [
        F("Deuterium, helium-3, helium-4 and lithium-7 were made at the end of the first three minutes, once the temperature fell to about 0.1 MeV (1.2 billion K); nuclear reactions were fixed by about 180 s.", "outside", "pdg-bbn"),
        F("Primordial helium is 24.5% of the ordinary matter by mass (Yp = 0.2448 +/- 0.0033). No silicon was made: nuclei heavier than lithium do not form in significant amounts.", "outside", "pdg-astro", "pdg-bbn"),
        F(f"The region that is now our observable universe was then about {round(region(0.1*K_PER_MEV, gs0)/LY, -2):.0f} light-years across.", "derived", "pdg-bb", "outside",
          note="entropy conservation, a T g*s^(1/3) constant, with g*s = 3.91 after electron-positron annihilation"),
        F(f"There are about {1/ETA/1e9:.2f} billion CMB photons for every proton or neutron (eta = 6.04 x 10^-10).", "derived", "pdg-astro", "pdg-bbn"),
        F("The universe holds matter and almost no antimatter: in the standard reading, matter outnumbered antimatter by a tiny margin early on, and the leftover makes every proton and neutron, including the chip's.", "inferred", "pdg-bb", "pdg-bbn"),
        F("Why there was a margin at all (baryogenesis) is unknown: it needs baryon-number violation, C and CP violation and a departure from equilibrium, and several mechanisms are viable.", "unknown", "pdg-bb"),
    ],
})
t_qcd_lo, t_qcd_hi = t_of_T(TC_QCD, 205 / 4), t_of_T(TC_QCD, 69 / 4)
d_qcd_lo, d_qcd_hi = region(TC_QCD * K_PER_MEV, 205 / 4), region(TC_QCD * K_PER_MEV, 69 / 4)
epochs.append({
    "id": "e.qcd",
    "name": "Quarks become protons: about 20 microseconds",
    "time_s": sig((t_qcd_lo + t_qcd_hi) / 2, 2),
    "temperature_K": sig(TC_QCD * K_PER_MEV, 3),
    "region_m": sig((d_qcd_lo + d_qcd_hi) / 2, 2),
    "facts": [
        F("Above about 156.5 MeV (1.8 x 10^12 K) quarks and gluons are not bound into protons and neutrons: a quark-gluon plasma. Lattice QCD puts the crossover at 156.5 +/- 1.5 MeV.", "outside", "hotqcd", "pdg-bb"),
        F(f"The universe cooled through it {t_qcd_lo*1e6:.0f}-{t_qcd_hi*1e6:.0f} microseconds after the Big Bang.", "derived", "pdg-bb", "hotqcd",
          note="PDG eq. 22.44 with N = 51.25 just above and 17.25 just below the transition"),
        F(f"The region that is now our observable universe was then about {round(d_qcd_lo/AU,-2):,.0f} to {round(d_qcd_hi/AU,-2):,.0f} times the Earth-Sun distance across (under a tenth of a light-year).", "derived", "pdg-bb", "outside"),
        F(f"At that temperature a typical particle's wavelength, hbar c / kT = {HBARC/TC_QCD:.2f} fm, is the size of a proton: the universe's 'microscope' and the proton's size meet.", "derived", "codata", "hotqcd", "pdg-b",
          note="an order-of-magnitude comparison"),
        F("The protons and neutrons in the chip's nuclei first formed in this transition; billions of years later, stars built them into silicon.", "inferred", "pdg-bb", "johnson"),
        F("The LHC recreates this plasma by colliding lead nuclei, at temperatures more than 100,000 times the centre of the Sun.", "outside", "cern2017"),
    ],
})
t_ew = t_of_T(TC_EW, 427 / 4)
d_ew = region(TC_EW * K_PER_MEV, 427 / 4)
epochs.append({
    "id": "e.ew",
    "name": "Particles get their masses: about 10 picoseconds",
    "time_s": sig(t_ew, 2),
    "temperature_K": sig(TC_EW * K_PER_MEV, 2),
    "region_m": sig(d_ew, 2),
    "facts": [
        F("The Standard Model's electroweak crossover, when the Higgs field takes its value, is at 159.5 +/- 1.5 GeV (lattice).", "outside", "ew"),
        F(f"That was about {t_ew*1e12:.0f} picoseconds after the Big Bang, when the region that is now our observable universe was about {d_ew/AU:.0f} times the Earth-Sun distance across.", "derived", "pdg-bb", "ew", "outside",
          note="PDG eq. 22.44 with all Standard Model particles, N = 106.75"),
        F("In the Standard Model the electron and the quarks get their masses from the Higgs field. The electron's mass sets the size of every atom (the Bohr radius is inversely proportional to it), and so the size of the chip's transistors.", "generic", "pdg-bb", "codata"),
    ],
})
epochs.append({
    "id": "e.planck",
    "name": "The Planck time: 5 x 10^-44 seconds",
    "time_s": T_P,
    "temperature_K": None,
    "region_m": None,
    "facts": [
        F("Planck time 5.391247 x 10^-44 s: before it, known physics cannot describe the universe.", "outside", "codata"),
        F("What happened at or before the Planck time, and whether 'before' means anything, is unknown.", "unknown", "hossenfelder"),
    ],
})

# where the chip's silicon came from: the physical link from the stars to the atoms
stardust = {
    "id": "e.stars",
    "name": "The chip's silicon was made in stars",
    "facts": [
        F("Silicon is made in massive stars, by oxygen burning late in their lives, and spread by their supernova explosions; exploding white dwarfs make some too.", "outside", "johnson", "woosley"),
        F("The Sun and its planets formed from gas already enriched by earlier stars; the oldest solids in the Solar System are 4,567.30 +/- 0.16 million years old.", "outside", "connelly", "primack"),
        F("Silicon is the second most abundant element in Earth's crust, more than 25% by weight.", "outside", "usgs"),
        F("So the silicon atoms in the chip's fins were forged in stars of the Milky Way more than 4.6 billion years ago, from protons and neutrons formed in the first 20 microseconds: a physical link between the ladder's top and bottom.", "inferred", "johnson", "connelly", "hotqcd"),
    ],
}

constants = {
    "e_C": E_CHARGE, "k_B_eV_per_K": K_B_EV, "kT_300K_eV": round(kT300, 6),
    "hbar_c_MeV_fm": HBARC, "a0_m": A0, "r_e_classical_m": R_E_CLASSICAL,
    "a_Si_m": A_SI, "Si_bond_m": bond, "Si_atoms_per_nm3": n_si * 1e-27,
    "Si_band_gap_eV_300K": BAND_GAP, "Si_ni_per_cm3_300K": N_I,
    "planck_length_m": L_P, "planck_time_s": T_P,
    "source": "CODATA 2022 (NIST), Ioffe NSM archive; Si_bond and atoms per nm3 derived",
}

loop = {
    "note": "Proposed links that close the ladder into a circle. 'up' is the Up button (zoom out), 'in' the default double-click (zoom in). Existing ids are from inside.json and outside.json.",
    "up": [
        ["universe", "beyond"], ["beyond", "p.wrap"], ["p.wrap", "p.planck"], ["p.planck", "p.quark"],
        ["p.quark", "p.nucleon"], ["p.nucleon", "p.nucleus"], ["p.nucleus", "p.core"], ["p.core", "p.atom"],
        ["p.electron", "p.atom"], ["p.dopant", "lib.si"], ["p.atom", "lib.si"], ["lib.si", "lib.channel"],
        ["lib.channel", "lib.fin"], ["lib.fin", "lib.finfet"],
        ["lib.finfet", "lib.sram6t (memory exit) or lib.fa (compute exit)"],
        ["lib.sram6t", "shire.panel.array (an L2/L3 SRAM panel of shire 0)"],
        ["lib.fa", "vpu.lane.fma.tree (the compressor tree of minion 0's FMA, lane 0)"],
    ],
    "in": [
        ["lib.si", "p.atom"], ["p.atom", "p.core"], ["p.core", "p.nucleus"], ["p.nucleus", "p.nucleon"],
        ["p.nucleon", "p.quark"], ["p.quark", "p.planck"], ["p.electron", "p.planck"],
        ["p.planck", "p.wrap"], ["p.wrap", "beyond"], ["beyond", "universe"],
    ],
    "exits": "On the way back up from the wrap, lib.finfet's Up goes to a memory cell or a compute cell: the page can alternate per turn of the circle, or follow whichever the viewer came down through, defaulting to the memory cell. The wrap level can offer both as buttons ('into a memory cell', 'into a compute transistor').",
    "readout": "From beyond to p.planck the readout leaves sizes: it shows 'conceptual link' on p.wrap, and the epochs (if shown) give time and temperature, not size. From p.planck up to p.quark the readout runs through 16 powers of ten marked 'unexplored'.",
    "optional_time_track": "e.cmb, e.bbn, e.qcd, e.ew, e.planck can be drawn as a strip on p.wrap (looking out = looking back), or as steps between beyond and p.planck; they are times, not sizes.",
}

# zoom ratios along the main inward path (this frame / child frame), like outside.json's zoom_from_inner
byid = {l["id"]: l for l in levels}
LIB_SI_FRAME = 5.43e-10   # inside.json lib.si size_m (no frame given)
for l in levels:
    ch = byid.get(l["child"])
    if l["frame_m"] and ch and ch.get("frame_m"):
        l["zoom_from_inner"] = round(l["frame_m"] / ch["frame_m"], 3)
zoom_into_atom = round(LIB_SI_FRAME / byid["p.atom"]["frame_m"], 3)
byid["p.atom"]["zoom_from_parent"] = zoom_into_atom
byid["p.atom"]["zoom_note"] = "the jump from p.core to p.nucleus is the long empty one (about 1,000x) and from p.quark to p.planck the longest (about 10^16x); like the outside ladder's long steps, they should be 'jump' moves with a drawn factor much smaller than the true one."

out = {
    "meta": {
        "built": "2026-10-01, build_particles.py",
        "what": "The ladder below the silicon crystal (atom, inner electrons, nucleus, nucleon, quark, electron, Planck length), a dopant side branch, and the wrap that closes the ladder into a circle (the cosmic uroboros), with an early-universe time track and the stellar origin of the chip's silicon.",
        "order": "inside out on the main path: p.planck < p.quark < p.nucleon < p.nucleus < p.core < p.atom (< lib.si in inside.json); side branches p.electron (under p.atom) and p.dopant (beside p.atom); p.wrap joins beyond (outside.json) to p.planck.",
        "kinds": ["measured", "spec", "derived", "inferred", "outside", "generic", "owner", "hypothesis", "unknown", "conceptual (size_kind only)"],
        "badges": {"derived": "model", "inferred": "inference", "outside": "outside source", "generic": "outside source - textbook", "hypothesis": "speculative", "unknown": "unknown"},
        "fields": {
            "parent": "the Up target in the closed loop",
            "child": "the default double-click target",
            "child_alt": "other parts a double-click can enter",
            "size_m": "characteristic size; null when no size is known (then size_bound_m is the experimental upper limit, a diameter)",
            "frame_m": "the width of the view",
            "zoom_from_inner": "this frame / child frame",
            "facts[].refs": "keys into meta.sources; facts[].source repeats them in full",
            "facts[].topic": "'electronics' marks the facts that explain how the chip works",
        },
        "honesty": "The wrap is a conceptual link, not a physical continuation of space: nothing lies 'past' the observable universe in the sense of the ladder, and the page says so on the wrap level. The physical links it shows are real and sourced: looking out is looking back in time (the CMB, the first nuclei, the quark-gluon plasma), the chip's silicon was made in stars, and inflation (a hypothesis) would make the galaxies' seeds quantum fluctuations.",
        "public": "No access paths, addresses, people or accounts; every outside fact is a published source.",
        "sources": S,
    },
    "levels": levels,
    "epochs": epochs,
    "stardust": stardust,
    "constants": constants,
    "loop": loop,
}

with open(os.path.join(HERE, "particles.json"), "w") as f:
    json.dump(out, f, indent=1, ensure_ascii=False)
    f.write("\n")

# a short self-check printout
nf = sum(len(l["facts"]) for l in levels) + sum(len(e["facts"]) for e in epochs) + len(stardust["facts"])
print("levels", len(levels), "epochs", len(epochs), "facts", nf)
for l in levels:
    print(f"  {l['id']:11s} size {l['size_m']!s:>12} frame {l['frame_m']!s:>10} zoom {l['zoom_from_inner']}")
for e in epochs:
    print(f"  {e['id']:9s} t {e['time_s']:.3g} s  T {e['temperature_K']}  region {e['region_m']}")
