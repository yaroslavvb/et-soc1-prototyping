# First-principles wire energy at the ET-SoC-1 NoC voltage, plus scaling of literature numbers.
V = 0.485  # ET-SoC-1 NoC rail (die_mv.noc)
V2 = V*V
print(f"V={V} V, V^2={V2:.4f}")

# Capacitance per mm (fF/mm). Wire-only from sources; repeater multiplier from Ho 2003 Table 4.2
cw = {"ASAP7 M3 (lowest)":155.6, "ASAP7 signal avg":165.8, "ASAP7 M6 (highest M2-M7)":187.4, "rule of thumb 0.2 fF/um":200.0}
rep = {"EDP-optimal repeaters (x1.34)":1.34, "delay-optimal repeaters (x1.87)":1.87}
print("\nC_total = C_wire * repeater factor; energies at V=0.485 V")
print(f"{'C_wire':32s} {'repeaters':34s} {'C_tot fF/mm':>11s} {'1/2CV2 fJ/mm':>13s} {'CV2 fJ/mm':>10s} {'rand bit fJ/b-mm':>17s}")
for kn,c in cw.items():
    for rn,r in rep.items():
        ct = c*r
        print(f"{kn:32s} {rn:34s} {ct:11.0f} {0.5*ct*V2:13.1f} {ct*V2:10.1f} {0.25*ct*V2:17.1f}")
for c in (200,300,400):
    print(f"round C_tot={c} fF/mm: per transition (heat, CV^2/2) {0.5*c*V2:.1f} fJ/mm; per 0->1 supply draw (CV^2) {c*V2:.1f}; per random bit (CV^2/4) {0.25*c*V2:.1f} fJ/bit-mm")

def scale(E, V0): return E*(V/V0)**2
print("\nScaling literature numbers to 0.485 V (E ~ V^2, C fixed):")
lit = [
 ("Keckler 2011 40nm per transition", 240, 0.9),
 ("Keckler 2011 40nm per random bit (x0.5)", 120, 0.9),
 ("Keckler 2011 10nm HF per transition", 150, 0.75),
 ("Keckler 2011 10nm LV per transition", 115, 0.65),
 ("Dally 2014/17 10nm 174pJ/(256b*10mm)", 174/2.56, 0.7),
 ("Dally 2018 CV^2 wire upper (40 fJ/b-mm), V unknown ~0.9?", 40, 0.9),
 ("Ho 2003 0.18um 1.8V toggling (984 fJ/transition-mm)", 984, 1.8),
 ("Dally 2023 100 fJ/b-mm if at 0.5 V", 100, 0.5),
 ("Dally 2023 100 fJ/b-mm if at 0.75 V", 100, 0.75),
 ("Dally 2023 100 fJ/b-mm if at 0.9 V", 100, 0.9),
 ("FlooNoC 12nm 0.8V 18.75 fJ/bit/hop", 18.75, 0.8),
]
for n,E,V0 in lit:
    print(f"  {n:60s} {E:7.1f} fJ @ {V0} V -> {scale(E,V0):6.1f} fJ @ 0.485 V (factor {(V/V0)**2:.3f})")

print("\nImplied capacitance of literature numbers:")
print(f"  Keckler 240 fJ/transition @0.9V: C = {240/0.81:.0f} fF/mm if E=CV^2, {2*240/0.81:.0f} fF/mm if E=CV^2/2")
print(f"  Keckler 150 @0.75: {150/0.5625:.0f} / {2*150/0.5625:.0f};  115 @0.65: {115/0.4225:.0f} / {2*115/0.4225:.0f}")
print(f"  Ho 984 fJ/transition-mm @1.8V: C = {984/3.24:.0f} (CV^2) / {2*984/3.24:.0f} (CV^2/2) fF/mm")
for V0 in (0.5,0.75,0.9):
    print(f"  Dally 100 fJ/b-mm at {V0} V: C = {100/(0.25*V0**2):.0f} fF/mm if random data (CV^2/4 per bit); {100/(0.5*V0**2):.0f} if one transition per bit (CV^2/2)")
print(f"  Dally 2018 20-40 fJ/b-mm with C=200 fF/mm, random (CV^2/4): V = {(20/(0.25*200))**0.5:.2f}-{(40/(0.25*200))**0.5:.2f} V; if CV^2 per bit: V={(20/200)**0.5:.2f}-{(40/200)**0.5:.2f} V")

print("\nDally per-bit-mm figures recomputed from worked examples:")
print(f"  AHA2023 slide 31: 4.8 pJ/b / 48 mm = {4800/48:.0f} fJ/b-mm; 1.6 pJ/b / 16 mm = {1600/16:.0f}")
print(f"  CACM2022: 1.9 pJ/(64b*1mm) = {1900/64:.1f} fJ/b-mm; 77 pJ/(64b*40mm) = {77000/64/40:.1f}; 57.4 pJ/(64b*30mm) = {57400/64/30:.1f}")
print(f"  CACM2020: 0.022 fJ*sqrt(S) check: 2*100fJ/mm*sqrt(0.013um^2)= {2*100*(0.013e-6)**0.5:.4f} fJ; S=800Mbit -> {50+0.022*(8e8)**0.5:.0f} fJ")
print(f"  Keckler2011: 256b*10mm*0.5*240fJ = {256*10*0.5*240/1000:.0f} pJ (table: 310 pJ)")
print(f"  SC12 28nm: 26pJ/256b = {26000/256:.0f} fJ/b (~1 mm); 256pJ/(256b*10mm) = {256000/2560:.0f}; 1nJ/(256b*20mm)={1e6/256/20:.0f}, /(256b*40mm)={1e6/256/40:.0f}")
print(f"  FlooNoC: 0.15 pJ/B/hop = {150/8:.2f} fJ/bit/hop; hop 0.75 mm -> {150/8/0.75:.1f} fJ/b-mm; hop 1.5 mm -> {150/8/1.5:.1f}")

print("\nET-SoC-1 measured numbers as equivalent switched capacitance at 0.485 V (random data => CV^2/4 per bit):")
for n,E in (("random-zero difference 131 fJ/bit/hop",131.0),("NoC rail random 1.29 pJ/B/hop = 161 fJ/bit/hop",1290/8)):
    C = E/(0.25*V2)
    print(f"  {n}: C_eff = {C:.0f} fF per payload bit per hop = {C/300:.1f} mm of 0.3 pF/mm repeated wire (or {C/200:.1f} mm at 0.2 pF/mm)")
print("\nIllustrative only: wire-only expectation per payload bit per hop (C_tot 0.2-0.4 pF/mm, random data):")
for L in (1,2,3,4,5):
    print(f"  hop {L} mm: {0.25*200*V2*L:.0f}-{0.25*400*V2*L:.0f} fJ/bit/hop (central 0.3 pF/mm: {0.25*300*V2*L:.0f})")
