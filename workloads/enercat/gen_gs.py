#!/usr/bin/env python3
"""Generate the gather/scatter modes of the energy catalogue (V3-GS, experiment E48) from one seeded list.

    python3 workloads/enercat/gen_gs.py      # writes enercat_gs.h, kernel/enercat_gs.inc, enercat_gs_modes.json

Never touches the catalogue's own generated files (enercat_modes.h, enercat_modes.json, kernel/enercat_ops.inc):
catfull imports and hashes those while it runs. The gs modes are compiled only when the build sets ENERCAT_GS
(cmake -DENERCAT_GS=ON, the separate build directory build/enercat_gs); without it the catalogue's kernel and host are
the same code as before.

What is generated:
  - the mode table (ids 400 and up): name, family, memory form (through the L1, local, global), element size;
  - the seven index patterns (unit, s2, s4, s16, line, rand, bcast): 8 vectors x 8 lanes of signed 32-bit BYTE
    offsets from a tile base, one table shared by host and kernel (the host uploads the one a launch uses);
  - the restricted-form (fg32*/fsc32*) lane fields: an injective lane -> slot map per instruction, packed as the
    instruction reads them (3/4/5-bit fields for 32/16/8-bit elements);
  - the scalar baselines (flw, fsw, amoaddl.w, amoaddg.w): the same 64 rand offsets as 12-bit immediates from
    base + 2048, for a 4 KB tile and for a 512 B working set (offsets mod 512).
"""
import json
import os
import random

HERE = os.path.dirname(os.path.abspath(__file__))
SEED = 47_2026_0925
FIRST = 400

PATTERNS = ["unit", "s2", "s4", "s16", "line", "rand", "bcast"]
TILE = {"unit": 256, "s2": 512, "s4": 1024, "s16": 4096, "line": 512, "rand": 4096, "bcast": 512}
LINES_PER_INSTR = {"unit": 0.5, "s2": 1, "s4": 2, "s16": 8, "line": 1, "rand": 8, "bcast": 1}

rng = random.Random(SEED)


def gen_patterns():
    t = {}
    t["unit"] = [4 * (8 * v + i) for v in range(8) for i in range(8)]
    t["s2"] = [8 * (8 * v + i) for v in range(8) for i in range(8)]
    t["s4"] = [16 * (8 * v + i) for v in range(8) for i in range(8)]
    t["s16"] = [64 * (8 * v + i) + 4 * rng.randrange(16) for v in range(8) for i in range(8)]
    line = []
    for v in range(8):
        words = rng.sample(range(16), 8)      # an injection of 8 of the line's 16 words
        line += [64 * v + 4 * w for w in words]
    t["line"] = line
    # rand: sigma a permutation of the tile's 64 lines, r a random word; within every vector the 8 offsets are also
    # distinct mod 256, so a working set smaller than the tile (offsets taken mod WS >= 256) never puts two lanes of
    # one instruction on the same word (scatter results stay free of lane conflicts)
    while True:
        sigma = list(range(64))
        rng.shuffle(sigma)
        rand, ok = [], True
        for v in range(8):
            for _ in range(200):
                offs = [64 * sigma[8 * v + i] + 4 * rng.randrange(16) for i in range(8)]
                if len({o % 256 for o in offs}) == 8:
                    break
            else:
                ok = False
            rand += offs
        if ok:
            break
    t["rand"] = rand
    t["bcast"] = [64 * v + 4 * r for v in range(8) for r in [rng.randrange(16)] for i in range(8)]
    for p in PATTERNS:
        assert len(t[p]) == 64 and all(0 <= o < TILE[p] and o % 4 == 0 for o in t[p]), p
    return t


def gen_fields():
    """Per element size (w, h, b): per instruction b = 0..7 an injective lane -> slot map and its packed field word."""
    out = {}
    for name, bits, slots in (("w", 3, 8), ("h", 4, 16), ("b", 5, 32)):
        perms, words = [], []
        for b in range(8):
            p = rng.sample(range(slots), 8)
            perms.append(p)
            words.append(sum(s << (bits * e) for e, s in enumerate(p)))
        out[name] = {"bits": bits, "perm": perms, "word": words}
    return out


PAT = gen_patterns()
F32 = gen_fields()
# the semantic probe's restricted-form fields (fixed, readable): words reversed; halfwords and bytes scattered
PROBE_W = [7, 6, 5, 4, 3, 2, 1, 0]
PROBE_H = [15, 12, 9, 6, 3, 0, 1, 10]
PROBE_B = [31, 26, 21, 16, 11, 6, 1, 3]
PROBE_FW = sum(s << (3 * e) for e, s in enumerate(PROBE_W))
PROBE_FH = sum(s << (4 * e) for e, s in enumerate(PROBE_H))
PROBE_FB = sum(s << (5 * e) for e, s in enumerate(PROBE_B))

# ---------------- the modes ----------------
FAM = {"GATHER": 1, "SCATTER": 2, "G32": 3, "S32": 4, "UPD": 5, "FAMO": 6, "BLD": 7, "BST": 8, "AMO": 9, "PROBE": 10}
FORM = {"": 0, "l": 1, "g": 2}
ESZ = {"w": 4, "h": 2, "b": 1}
modes = []


def mode(name, fam, form=0, elem=4, btile=0, unit="element", note=""):
    modes.append({"name": name, "mode": FIRST + len(modes), "family": fam, "form": form, "elem": elem, "btile": btile,
                  "unit": unit, "note": note})


for f in ("", "l", "g"):
    for e in ("w", "h", "b"):
        mode(f"fg{e}{f}.ps", "GATHER", FORM[f], ESZ[e],
             note={"": "gather through the L1", "l": "gather bypassing the L1, to the shire's L2",
                   "g": "gather bypassing L1 and L2, to the home (L3 slice, scratchpad or memory)"}[f])
for f in ("", "l", "g"):
    for e in ("w", "h", "b"):
        mode(f"fsc{e}{f}.ps", "SCATTER", FORM[f], ESZ[e],
             note={"": "scatter through the L1", "l": "scatter bypassing the L1, to the shire's L2",
                   "g": "scatter bypassing L1 and L2, to the home"}[f])
for e in ("w", "h", "b"):
    mode(f"fg32{e}.ps", "G32", 0, ESZ[e], note="restricted gather: one 32 B block, lanes permuted by packed fields")
for e in ("w", "h", "b"):
    mode(f"fsc32{e}.ps", "S32", 0, ESZ[e], note="restricted scatter: one 32 B block")
mode("upd", "UPD", 0, 4, unit="update", note="gather + fadd.ps 1.0 + scatter on the same indices: software scatter-add")
mode("famoaddl.pi", "FAMO", 1, 4, unit="update", note="packed atomic add, local (shire L2)")
mode("famoaddg.pi", "FAMO", 2, 4, unit="update", note="packed atomic add, global (home L3)")
for bt in (4096, 512):
    mode(f"flw.t{bt}", "BLD", 0, 4, bt, note="scalar flw, the rand offsets as immediates: the scalar-indexed baseline")
for bt in (4096, 512):
    mode(f"fsw.t{bt}", "BST", 0, 4, bt, note="scalar fsw, the rand offsets as immediates")
mode("amoaddl.w.t4096", "AMO", 1, 4, 4096, unit="update", note="scalar local atomic add per update (addi + amo)")
mode("amoaddg.w.t4096", "AMO", 2, 4, 4096, unit="update", note="scalar global atomic add per update (addi + amo)")
mode("probe", "PROBE", 0, 4, unit="probe", note="the semantic probes of the design (sign extension, fg32 fields, masks, "
     "lane conflicts, famo old values, gsc_progress)")


def boffs(bt):
    """The 64 rand offsets for a scalar baseline tile: bt = 4096 (the rand tile) or 512 (offsets mod 512)."""
    return [o % bt for o in PAT["rand"]]


# ---------------- kernel/enercat_gs.inc ----------------
def scalar_block(m):
    """The asm text of one visit's 64 scalar operations (after GS_ADV), and for flw its verify form."""
    offs = boffs(m["btile"])
    imm = [o - 2048 for o in offs]
    assert all(-2048 <= x < 2048 for x in imm)
    if m["family"] == "BLD":
        body = "".join(f"flw f{10 + j % 8}, {imm[j]}(%[b])\\n\\t" for j in range(64))
        ver = "".join(f"flw f10, {imm[j]}(%[b])\\n\\tfmv.x.w x0, f10\\n\\tnop\\n\\tfmv.x.w %[t0], f10\\n\\tadd %[acc], %[acc], %[t0]\\n\\t"
                      for j in range(64))
        return body, ver
    if m["family"] == "BST":
        return "".join(f"fsw f{10 + j % 8}, {imm[j]}(%[b])\\n\\t" for j in range(64)), None
    op = "amoaddl.w" if m["form"] == 1 else "amoaddg.w"
    return "".join(f"addi %[t0], %[b], {imm[j]}\\n\\t{op} %[t1], %[one], (%[t0])\\n\\t" for j in range(64)), None


inc = ["// Generated by gen_gs.py: the gather/scatter modes' cases (inside gs_run's switch). Do not edit.\n"]
for m in modes:
    f = m["family"]
    head = f"    case {m['mode']}: /* {m['name']} */\n"
    op = m["name"]
    if f == "GATHER":
        body = f'        GS_GATHER("{op}");\n'
    elif f == "SCATTER":
        body = f'        GS_SCATTER("{op}", {m["form"]});\n'
    elif f == "G32":
        body = f'        GS_G32("{op}");\n'
    elif f == "S32":
        body = f'        GS_S32("{op}");\n'
    elif f == "UPD":
        body = "        GS_UPD();\n"
    elif f == "FAMO":
        body = f'        GS_FAMO("{op}");\n'
    elif f == "BLD":
        blk, ver = scalar_block(m)
        body = f'        GS_BLD("{blk}", "{ver}");\n'
    elif f == "BST":
        blk, _ = scalar_block(m)
        body = f'        GS_BST("{blk}");\n'
    elif f == "AMO":
        blk, _ = scalar_block(m)
        body = f'        GS_AMO("{blk}");\n'
    else:
        body = "        GS_PROBE();\n"
    inc.append(head + body + "        break;\n")
open(os.path.join(HERE, "kernel", "enercat_gs.inc"), "w").write("".join(inc))

# ---------------- enercat_gs.h ----------------
h = ["// Generated by gen_gs.py: the gather/scatter modes (ids 400+) and their tables, shared by kernel and host.",
     "// Compiled only with ENERCAT_GS (build/enercat_gs). Do not edit; re-run gen_gs.py.",
     "#pragma once", "#include <stdint.h>",
     f"#define EC_GS_FIRST {FIRST}", f"#define EC_GS_COUNT {len(modes)}", "#define EC_GS_MAGIC 0x47530000u",
     f"#define EC_GS_SEED {SEED}ull"]
for k, v in FAM.items():
    h.append(f"#define GS_F_{k} {v}")
h.append("#define GS_FORM_L1 0\n#define GS_FORM_LOCAL 1\n#define GS_FORM_GLOBAL 2")
h.append("#define GS_SHARE_HART 0\n#define GS_SHARE_SHIRE 1\n#define GS_SHARE_CHIP 2")
h.append("#define GS_SCP_BYTES 16384u       // scratchpad table per hart (the upper 16 KB of the minion's 32 KB is hart 1's)")
h.append("#define GS_SCP_OFF (256u * 1024u)  // scratchpad tables start here (offset 0 of a shire's scratchpad faults)")
h.append("#define GS_CHECK_MIN 512u          // check bytes per participant at least (probe); gathers: 256 per verify visit")
h.append("#define GS_SENTINEL 0x5A5AC3C3u    // masked-off gather lanes keep this (the verify launches check it)")
h.append("// FP registers: only caller-saved ones (f0-f7 index vectors, f10-f17 sinks/data/addends, f28-f31), so the compiler")
h.append("// never saves/restores an FP register inside the gs code (a restore then save is itself a VPURF hazard)")
h.append("#define GS_SHIRE_TABLE (256u * 1024u)\n#define GS_CHIP_TABLE (8u * 1024u * 1024u)")
h.append("// Params buffer (host -> kernel, one per launch): int32 idx[8][8] at 0, uint64 fields[8] at 256.")
h.append("#define GS_PARAM_IDX 0\n#define GS_PARAM_F32 256\n#define GS_PARAM_BYTES 512")
sc = [m["mode"] for m in modes if m["family"] in ("BLD", "BST", "AMO")]
assert sc == list(range(sc[0], sc[-1] + 1))
h.append(f"#define EC_GS_SCALAR_LO {sc[0]}   // the scalar baselines (flw, fsw, amoadd*.w): base + 2048 + imm")
h.append(f"#define EC_GS_SCALAR_HI {sc[-1]}")
h.append(f"#define GS_PROBE_FW 0x{PROBE_FW:x}ull   // probe fg32w/fsc32w fields: lane e -> word {PROBE_W}")
h.append(f"#define GS_PROBE_FH 0x{PROBE_FH:x}ull   // probe fg32h fields: lane e -> halfword {PROBE_H}")
h.append(f"#define GS_PROBE_FB 0x{PROBE_FB:x}ull   // probe fg32b/fsc32b fields: lane e -> byte {PROBE_B}")
h.append("#ifdef __cplusplus")
h.append("struct EcGsOp { const char* name; unsigned mode; int family; int form; int elem; unsigned btile; const char* unit; const char* note; };")
h.append("static const EcGsOp EC_GS_OPS[] = {")
for m in modes:
    h.append(f'  {{"{m["name"]}", {m["mode"]}, {FAM[m["family"]]}, {m["form"]}, {m["elem"]}, {m["btile"]}, "{m["unit"]}", "{m["note"]}"}},')
h.append("};")
h.append(f"static const char* const EC_GS_PATTERNS[{len(PATTERNS)}] = {{" + ", ".join(f'"{p}"' for p in PATTERNS) + "};")
h.append(f"static const unsigned EC_GS_PAT_TILE[{len(PATTERNS)}] = {{" + ", ".join(str(TILE[p]) for p in PATTERNS) + "};")
h.append(f"static const double EC_GS_PAT_LINES[{len(PATTERNS)}] = {{" + ", ".join(str(LINES_PER_INSTR[p]) for p in PATTERNS) + "};")
h.append(f"static const int32_t EC_GS_IDX[{len(PATTERNS)}][64] = {{")
for p in PATTERNS:
    h.append("  {" + ", ".join(str(x) for x in PAT[p]) + "},")
h.append("};")
h.append("// restricted forms, per element size w/h/b: per instruction b the lane -> slot map and the packed field word")
h.append("static const int EC_GS_F32_BITS[3] = {" + ", ".join(str(F32[e]["bits"]) for e in "whb") + "};")
h.append("static const int EC_GS_F32_PERM[3][8][8] = {")
for e in "whb":
    h.append("  {" + ", ".join("{" + ", ".join(str(s) for s in p) + "}" for p in F32[e]["perm"]) + "},")
h.append("};")
h.append("static const uint64_t EC_GS_F32_WORD[3][8] = {")
for e in "whb":
    h.append("  {" + ", ".join(f"0x{w:x}ull" for w in F32[e]["word"]) + "},")
h.append("};")
h.append("#endif")
open(os.path.join(HERE, "enercat_gs.h"), "w").write("\n".join(h) + "\n")

json.dump({"seed": SEED, "first": FIRST, "modes": modes, "patterns": {p: {"tile": TILE[p], "lines_per_instr": LINES_PER_INSTR[p],
           "offsets": PAT[p]} for p in PATTERNS}, "f32": F32},
          open(os.path.join(HERE, "enercat_gs_modes.json"), "w"), indent=1)
print(f"{len(modes)} gather/scatter modes generated (ids {FIRST}-{FIRST + len(modes) - 1})")
