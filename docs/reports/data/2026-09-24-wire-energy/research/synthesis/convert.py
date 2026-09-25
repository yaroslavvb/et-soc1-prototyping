# Superseded by wire.json (E31/E32): this uses the E27 inputs and the provisional 3.64–3.76 mm pitch range.
# Conversion of E27 per-hop slopes to per-mm, per-transition, and voltage-scaled figures.
# Inputs: railfit.json (critique), 04a-fine-grain.md, pitch (geometry + verify), toggles.json (critique).
V = 0.485; V2 = V*V
P_C, P_LO, P_HI = 3.72, 3.64, 3.76          # mm per hop (mean pitch; verified range)
Q_C, Q_LO, Q_HI = 0.445, 0.433, 0.471       # toggles per payload bit per flit (toggles.json)
fJ = lambda pJB: pJB*1000/8                 # pJ/B -> fJ/bit
rows = {  # name: (central pJ/B/hop, lo, hi) per card; all-d and d<=6
 "board diff (random-zeros), all d": (1.05, 1.028, 1.058),
 "board diff, d<=6":                  (1.31, 1.237, 1.390),
 "board zeros, all d":                (0.70, 0.641, 0.748),
 "board zeros, d<=6":                 (0.86, 0.841, 0.887),
 "board random, all d":               (1.74, 1.668, 1.805),
 "board random, d<=6":                (2.18, 2.078, 2.277),
 "NoC rail random, all d":            (1.29, 1.261, 1.287),
 "NoC rail random, d<=6":             (1.49, 1.468, 1.506),
 "NoC rail diff, all d":              (0.78, 0.777, 0.789),
 "NoC rail diff, d<=6":               (0.89, 0.879, 0.895),
 "NoC rail zeros, all d":             (0.49, 0.484, 0.498),
 "NoC rail zeros, d<=6":              (0.60, 0.589, 0.610),
}
print(f"V^2={V2:.4f}")
for k,(c,lo,hi) in rows.items():
    b, blo, bhi = fJ(c), fJ(lo), fJ(hi)
    mm = b/P_C; mm_pitch = (b/P_HI, b/P_LO); mm_full = (blo/P_HI, bhi/P_LO)
    s = f"{k:34s} {c:.2f} pJ/B/hop = {b:5.1f} fJ/b/hop [{blo:.0f}-{bhi:.0f}] -> {mm:5.1f} fJ/b-mm pitch-only [{mm_pitch[0]:.1f}-{mm_pitch[1]:.1f}] full [{mm_full[0]:.1f}-{mm_full[1]:.1f}]"
    if "diff" in k:
        t = b/Q_C/P_C; tlo = blo/Q_HI/P_HI; thi = bhi/Q_LO/P_LO
        tp = (b/Q_C/P_HI, b/Q_C/P_LO)
        C = 2*t/V2   # fF/mm
        r50 = 0.5*t  # per random bit at q=0.5
        s += f"\n{'':34s} per transition-mm {t:.1f} pitch-only [{tp[0]:.1f}-{tp[1]:.1f}] full [{tlo:.1f}-{thi:.1f}]; per hop {b/Q_C:.0f} fJ/trans; C_eff {C:.0f} fF/mm ({2*b/Q_C/V2/1000:.2f} pF/hop); q=0.5 random-bit {r50:.1f} [{0.5*tlo:.1f}-{0.5*thi:.1f}]"
        for V0 in (0.5, 0.75, 0.8, 0.9):
            f = (V0/V)**2
            s += f"\n{'':34s}   @ {V0} V (x{f:.3f}): per trans-mm {t*f:.0f} [{tlo*f:.0f}-{thi*f:.0f}], per random bit-mm (q=.5) {r50*f:.0f} [{0.5*tlo*f:.0f}-{0.5*thi*f:.0f}]"
    if k.startswith("NoC rail random") or k.startswith("NoC rail zeros"):
        for V0 in (0.5, 0.9):
            f=(V0/V)**2; s += f"\n{'':34s}   @ {V0} V (x{f:.3f}): {mm*f:.0f} fJ/b-mm [{mm_full[0]*f:.0f}-{mm_full[1]*f:.0f}]"
    print(s)
# first principles
for C in (200,300,400):
    print(f"wire C={C} fF/mm: per trans-mm {0.5*C*V2:.1f}; per payload bit-mm at q=.445 {0.5*C*V2*Q_C:.1f}; per random bit (q=.5) {0.25*C*V2:.1f}; per hop(3.72mm) per transition {0.5*C*V2*P_C:.0f} fJ")
# Dally 100 fJ/b-mm back-scaled to 0.485 V
for V0 in (0.5,0.75,0.8,0.9):
    print(f"Dally 100 @ {V0} V -> {100*(V/V0)**2:.0f} fJ/b-mm at 0.485 V")
print("Keckler 121 fJ/random-bit-mm @0.9 -> ", round(121*(V/0.9)**2,1), "; 240/trans ->", round(240*(V/0.9)**2,1))
