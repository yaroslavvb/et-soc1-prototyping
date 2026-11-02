#!/usr/bin/env python3
"""E115's corrections after verification (Sun 1 Nov 2026): every number the README's Corrections section cites,
recomputed from committed files only. Desk work: no card, no new measurement, no frozen file read for anything but
its numbers. Standard library only.

    python3 docs/reports/data/2026-11-01-e115-blind-pool/corrections-check.py > docs/reports/data/2026-11-01-e115-blind-pool/corrections-check.txt

Sections: C1 the gate tiles, by side and pattern (the lanes read from each float tile's bytes); C2 E103's x_e_g;
C3 int8's bias; C4 the registered sensitivity labels; C5 the sums, R1's line and the pool's independence;
F the data and frozen files, unchanged since the data commit.
"""
import hashlib
import json
import os
import struct
import subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
DATA = "docs/reports/data/2026-11-01-e115-blind-pool"
E103 = "docs/reports/data/2026-11-01-e103-model-blind-test"
Q133B = "docs/reports/data/2026-11-01-q133b-power-model"
BLIND3 = "tools/claims-v3/kinds/blind3"
DATA_COMMIT = "ad06ad92"


def load(rel):
    with open(os.path.join(REPO, rel), encoding="utf-8") as f:
        return json.load(f)


def lanes(rel):
    """An fp32 tile file (A then B, 1,024 bytes each, 16x16 little-endian words; B[k][j]). Lane l reads B column l on
    the first micro-op of an A row and column l+8 on the second (blind3's mapping, make_blind3.py STEADY_COLS)."""
    raw = open(os.path.join(REPO, rel), "rb").read()
    assert len(raw) == 2048 and "/fp32/" in rel, (rel, len(raw))
    a = struct.unpack("<256f", raw[:1024])
    b = struct.unpack("<256f", raw[1024:])
    bz = [[b[k * 16 + j] == 0.0 for j in range(16)] for k in range(16)]
    cols = [j for j in range(16) if all(bz[k][j] for k in range(1, 16))]
    state = {}
    for l in range(8):
        c1, c2 = l in cols, (l + 8) in cols
        state[l] = "held off" if (c1 and c2) else ("live" if not (c1 or c2) else "switches")
    return {"B_cols_zero_rows_1_15": cols, "B_row0_zeros": sum(bz[0]), "A_zeros": sum(1 for x in a if x == 0.0),
            "lanes": state, "switching": sum(v == "switches" for v in state.values()),
            "zero_share_B": round(sum(map(sum, bz)) / 256, 4)}


def sha(rel):
    return hashlib.sha256(open(os.path.join(REPO, rel), "rb").read()).hexdigest()


def sha_at(commit, rel):
    try:
        blob = subprocess.run(["git", "-C", REPO, "show", f"{commit}:{rel}"], capture_output=True, check=True).stdout
        return hashlib.sha256(blob).hexdigest()
    except Exception:
        return None


def main():
    sc = load(f"{DATA}/scored-nodips.json")
    arms = load(f"{DATA}/scored-nodips-arms.json")
    pe = load("tools/claims-v3/e115/predictions-e115.json")
    b3 = load(f"{BLIND3}/blind3.json")["tiles"]
    b3 = b3 if isinstance(b3, dict) else {f"{t['type']}.{t['kind']}": t for t in b3}
    tab = sc["primary"]["table"]
    rules = sc["primary"]["rules"]

    print("E115 corrections-check (the registered fallback reading: dips removed, a3 footing; scored-nodips.json)")
    print()
    print("C1. The gate tiles, by side and pattern (scored-nodips.json primary.table; pattern from blind3.json 'group',")
    print("    lanes from the tile's bytes for the float B-gate tiles)")
    gated = [k for k, v in tab.items() if v["open_case"] == "gated-kinds" or k == "fp32.x_logu_bsteady"]
    for k in sorted(gated):
        v = tab[k]
        line = (f"  {k:24s} D {v['D']:7.3f}  M5 {v['M5']:7.3f} [{v['lo95']:.2f}, {v['hi95']:.2f}]  D-M5 {v['err_M5']:+.3f}"
                f"  {'inside' if v['inside_M5'] else 'OUTSIDE'}  | {b3[k]['group']}")
        print(line)
        if k.startswith("fp32."):
            L = lanes(f"{BLIND3}/{b3[k]['file']}")
            print(f"      B columns zero in rows 1-15 {L['B_cols_zero_rows_1_15']}, A words zero {L['A_zeros']}:"
                  f" lanes {L['lanes']}")
    for name, c in rules["E115-R4"]["contrasts"].items():
        if "g_blanes" in name or "x_logu" in name:
            print(f"  registered contrast {name}: measured {c['measured_w']:+.3f} +- {c['ci95_w']:.3f} W, M5 {c['M5_w']:+.3f}"
                  f" [{c['lo95']:+.2f}, {c['hi95']:+.2f}], {c['verdict']} (both tiles fp32)")
    fl = [k for k in gated if not k.startswith("int8.")]
    print("  float B-lane gate tiles outside: ", [k for k in fl if not tab[k]["inside_M5"]])
    print("  inside: ", [(k, round(tab[k]["err_M5"], 3)) for k in gated if tab[k]["inside_M5"]])
    print()

    print("C2. E103's fp32.x_e_g (aifoundry1 card 1; E103 README lines 11, 28, 60, 115)")
    L = lanes("tools/claims-v3/kinds/e103/tiles/fp32/x_e_g.bin")
    print(f"  tile tools/claims-v3/kinds/e103/tiles/fp32/x_e_g.bin: B columns zero in rows 1-15 {L['B_cols_zero_rows_1_15']},"
          f" B row 0 zeros {L['B_row0_zeros']}, A zeros {L['A_zeros']}, zero share of B words {L['zero_share_B']}")
    print(f"  lanes (l reads column l, then l+8): {L['lanes']}: {L['switching']} of 8 switch each micro-op")
    s103 = load(f"{E103}/scored.json")
    t = s103["primary"]["table"]["fp32.x_e_g"]
    print(f"  E103 primary (leak {s103['primary']['leak']['mode']} W/C): D {t['D']:.3f} +- {t['ci95']:.3f}, M4 {t['M']:.3f}"
          f" [{t['lo95']:.2f}, {t['hi95']:.2f}], D - M4 {t['D'] - t['M']:+.3f}")
    r9 = s103["primary"]["rules"].get("E103-R9", {})
    print(f"  E103-R9 (gated kinds) verdict: {r9.get('verdict')}")
    spread = {a: round(v["table"]["fp32.x_e_g"]["D"] - v["table"]["fp32.x_e_g"]["M"], 3)
              for a, v in s103.get("arms", {}).items() if "fp32.x_e_g" in v.get("table", {})}
    print(f"  D - M4 at E103's arms: {spread}")
    lk = load(f"{Q133B}/loko.json")
    hits = []
    def walk(o):
        if isinstance(o, dict):
            if o.get("key") == "fp32.x_e_g" and o.get("exp") == "E103":
                hits.append({kk: (round(vv, 3) if isinstance(vv, float) else vv) for kk, vv in o.items()})
            for vv in o.values():
                walk(vv)
        elif isinstance(o, list):
            for vv in o:
                walk(vv)
    walk(lk)
    for h in hits:
        print(f"  loko.json (M5's training rows include it): {h}")
    print()

    print("C3. int8's bias (scored-nodips.json primary.rules.E115-R2, primary.table)")
    r2 = rules["E115-R2"]
    i8 = {k: v["err_M5"] for k, v in tab.items() if k.startswith("int8.")}
    print(f"  rms {r2['rms_w']:.4f} W, bias (predicted - measured) {r2['bias_pred_minus_meas_w']:+.4f} W, verdict {r2['verdict']}")
    print(f"  D - M5 per tile: { {k: round(v, 3) for k, v in sorted(i8.items())} }")
    print(f"  tiles below the model: {sum(1 for v in i8.values() if v < 0)} of {len(i8)}; mean D - M5 {sum(i8.values()) / len(i8):+.4f} W")
    print()

    print("C4. The registered sensitivity labels (scored-nodips-arms.json primary.rules; anchor footing from scored-nodips.json)")
    txt = open(os.path.join(REPO, "tools/claims-v3/e115/README.md"), encoding="utf-8").read()
    print(f"  registration says 'arm-sensitive or footing-sensitive': {'arm-sensitive or footing-sensitive' in txt.replace(chr(10), ' ')}")
    af = sc["anchor_footing"]["rules"]
    for r, v in arms["primary"]["rules"].items():
        print(f"  {r}: verdict {v['verdict']}; footing_sensitive {v.get('footing_sensitive')}; arm_sensitive {v.get('arm_sensitive')}")
    print(f"  anchor footing: R1 rms {af['E115-R1']['rms_w']:.4f} W ({af['E115-R1']['verdict']}); R5 gap {af['E115-R5']['gap_w']:+.4f}"
          f" [{af['E115-R5']['lo95']:+.4f}, {af['E115-R5']['hi95']:+.4f}] ({af['E115-R5']['verdict']})")
    print("  the arms that move R3, R4 and S1 are nodips_leak*: run after the data on the dips-removed reduction (README Departures)")
    print()

    print("C5. The sums, R1's line, the pool's independence")
    for k in ["fp32.s_pair0", "fp32.s_bridge", "fp32.s_drift12"]:
        v = tab[k]
        print(f"  {k:16s} D {v['D']:.3f}  M5 {v['M5']:.3f} [{v['lo95']:.3f}, {v['hi95']:.3f}]  D-M5 {v['err_M5']:+.3f}"
              f"  below the upper bound by {v['hi95'] - v['D']:.3f} W  | {b3[k]['group']}")
    for k in ["fp32.s_bhalf_alt", "fp32.c_near_rand"]:
        t = s103["primary"]["table"][k]
        print(f"  E103 {k}: D - M4 {t['D'] - t['M']:+.3f} W")
    print(f"  R1's frozen line (predictions-e115.json rules.E115-R1.planned_interval.hi95): {pe['rules']['E115-R1']['planned_interval']['hi95']:.5f} W;"
          f" measured {rules['E115-R1']['rms_w']:.5f} W; over by {rules['E115-R1']['rms_w'] - pe['rules']['E115-R1']['planned_interval']['hi95']:.4f} W")
    print(f"  registration: 'independence of the pool is half met' present: {'independence of the pool is half met' in txt.replace(chr(10), ' ')};"
          f" 'it says so wherever it reports' present: {'it says so wherever it reports' in txt.replace(chr(10), ' ')}")
    print()

    print(f"F. Data and frozen files: sha256 now, and the same at the data commit {DATA_COMMIT}")
    for rel in [f"{DATA}/scored.json", f"{DATA}/scored-nodips.json", f"{DATA}/scored-nodips-arms.json", f"{DATA}/e115.json",
                f"{DATA}/e115-nodips.json", f"{DATA}/results.md", f"{DATA}/results-nodips.md", f"{DATA}/results-nodips-arms.md",
                "tools/claims-v3/e115/predictions-e115.json", "tools/claims-v3/e115/README.md", f"{BLIND3}/blind3.json",
                f"{BLIND3}/predictions-blind3.json", f"{BLIND3}/contrasts-blind3.json"]:
        now, then = sha(rel), sha_at(DATA_COMMIT, rel)
        print(f"  {now[:12]}  {'same' if then == now else ('DIFFERENT' if then else 'no git')}  {rel}")


if __name__ == "__main__":
    main()
