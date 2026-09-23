#!/usr/bin/env python3
"""Generate the instruction catalogue's kernel cases and the host's mode table from one instruction list.

    python3 workloads/enercat/gen_ops.py      # writes kernel/enercat_ops.inc and enercat_modes.h

Every instruction runs in blocks of eight with rotating sources and distinct sinks. Sources are never
overwritten and sinks never read, so what the unit sees is "the next pair of operands", op after op.
Scalar sources are C variables (GCC picks registers); vector sources are f0..f7, sinks f8..f15.
"""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))

# name, shape, asm mnemonic (or template), unit, note
INT_RRR = ["add", "sub", "and", "or", "xor", "sll", "srl", "sra", "slt", "sltu", "addw", "subw", "sllw", "srlw", "sraw",
           "mul", "mulh", "mulhu", "mulhsu", "div", "divu", "rem", "remu", "mulw", "divw", "divuw", "remw", "remuw"]
INT_RRI = [("addi", 37), ("andi", 37), ("ori", 37), ("xori", 37), ("slli", 7), ("srli", 7), ("srai", 7), ("slti", 37), ("sltiu", 37), ("addiw", 37)]
FLT_RRR = ["fadd.s", "fsub.s", "fmul.s", "fmin.s", "fmax.s", "fsgnj.s", "fsgnjn.s", "fsgnjx.s"]
FLT_RRRR = ["fmadd.s", "fmsub.s", "fnmadd.s", "fnmsub.s"]
FLT_R = []
FLT_CMP = ["feq.s", "flt.s", "fle.s"]              # rd <- fs1, fs2
FLT_F2X = ["fclass.s", "fcvt.w.s", "fcvt.wu.s", "fmv.x.w"]   # rd <- fs
FLT_X2F = ["fcvt.s.w", "fcvt.s.wu", "fmv.w.x"]                # fd <- rs
VEC_RRR = ["fadd.ps", "fsub.ps", "fmul.ps", "fmin.ps", "fmax.ps", "fsgnj.ps", "fsgnjn.ps", "fsgnjx.ps",
           "feq.ps", "flt.ps", "fle.ps", "fcmovm.ps",
           "fadd.pi", "fsub.pi", "fmul.pi", "fmulh.pi", "fmulhu.pi", "fand.pi", "for.pi", "fxor.pi", "fsll.pi", "fsrl.pi", "fsra.pi",
           "fmin.pi", "fmax.pi", "fminu.pi", "fmaxu.pi", "feq.pi", "flt.pi", "fltu.pi", "fle.pi"]
VEC_RRRR = ["fmadd.ps", "fmsub.ps", "fnmadd.ps", "fnmsub.ps", "fcmov.ps"]
VEC_R = ["fexp.ps", "flog.ps", "frcp.ps", "fround.ps", "ffrc.ps", "fclass.ps", "fnot.pi",
         "fcvt.ps.pw", "fcvt.pw.ps", "fpackrepb.pi", "fpackreph.pi"]
VEC_RI = [("faddi.pi", 37), ("fandi.pi", 37), ("fslli.pi", 7), ("fsrli.pi", 7), ("fsrai.pi", 7), ("fswizz.ps", 0x1b)]
VEC_M = ["feqm.ps", "fltm.ps", "flem.ps"]          # m1 <- fs1, fs2
VEC_BCX = ["fbcx.ps"]                               # fd <- rs
VEC_BCI = [("fbci.ps", 37), ("fbci.pi", 37)]        # fd <- imm
MEM_LD = ["lb", "lh", "lw", "ld", "lbu", "lhu", "lwu"]    # rd <- OFF(base), L1-resident buffer
MEM_ST = ["sb", "sh", "sw", "sd"]                    # OFF(base) <- rs
MEM_FLD = ["flw"]
MEM_FST = ["fsw"]
MEM_VLD = ["flw.ps", "flwl.ps"]                       # flwl.ps: straight to the local L2 (the buffer is in DRAM, so this is the L2/L3 path)
MEM_VST = ["fsw.ps", "fswl.ps"]
BRANCH = [("beq_taken", "beq %8, %8, 1f\\n1:"), ("bne_nottaken", "bne %8, %8, 1f\\n1:"),
          ("blt_data", "blt %8, %9, 1f\\n1:"), ("bge_data", "bge %8, %9, 1f\\n1:"),
          ("bltu_data", "bltu %8, %9, 1f\\n1:"), ("bgeu_data", "bgeu %8, %9, 1f\\n1:")]
MISC = [("jal", "jal %0, 1f\\n1:"), ("csrr_fccnb", "csrr %0, 0xcc0"),
        ("fence", "fence"), ("nop", "nop"), ("lui", "lui %0, 0x12345"), ("auipc", "auipc %0, 0x12")]
ATOMIC = ["amoaddl.w", "amoswapl.w", "amoorl.w", "amomaxl.w", "amoaddl.d", "amoaddg.w", "amoaddg.d"]
COMPRESSED = [("c.add", "c.add %0, %8"), ("c.addi", "c.addi %0, 3"), ("c.mv", "c.mv %0, %8"), ("c.li", "c.li %0, 3"),
              ("add_norvc", "add %0, %0, %8"), ("addi_norvc", "addi %0, %0, 3")]

modes = []   # dicts: name, kind, ops_per_iter, unit, hart0_only, note


def emit_int_block(asm_op, srcs=2, imm=None):
    # 8 ops, sinks %0..%7, sources %8..%15 rotating
    lines = []
    for i in range(8):
        a, b = 8 + i, 8 + (i + 1) % 8
        if imm is not None:
            lines.append(f"{asm_op} %{i}, %{a}, {imm}")
        elif srcs == 1:
            lines.append(f"{asm_op} %{i}, %{a}")
        else:
            lines.append(f"{asm_op} %{i}, %{a}, %{b}")
    return "\\n".join(lines)


def emit_fused(asm_op):
    return "\\n".join(f"{asm_op} %{i}, %{8+i}, %{8+(i+1)%8}, %{8+(i+2)%8}" for i in range(8))


def emit_vec(asm_op, arity, imm=None, mask_out=False):
    lines = []
    for i in range(8):
        a, b, c = i, (i + 1) % 8, (i + 2) % 8
        d = f"m1" if mask_out else f"f{8+i}"
        if imm is not None:
            lines.append(f"{asm_op} {d}, f{a}, {imm}")
        elif arity == 1:
            lines.append(f"{asm_op} {d}, f{a}")
        elif arity == 2:
            lines.append(f"{asm_op} {d}, f{a}, f{b}")
        else:
            lines.append(f"{asm_op} {d}, f{a}, f{b}, f{c}")
    return "\\n".join(lines)


ISINK = ', '.join(f'"=&r"(d{i})' for i in range(8))
FSINK = ', '.join(f'"=&f"(e{i})' for i in range(8))
ISRC = ', '.join(f'"r"(s{i})' for i in range(8))
FSRC = ', '.join(f'"f"(g{i})' for i in range(8))
VSINK = '"f8", "f9", "f10", "f11", "f12", "f13", "f14", "f15"'


def case(name, body, ops=64, unit="instruction", hart0=False, note=""):
    mid = len(modes) + 100
    modes.append({"name": name, "mode": mid, "ops_per_iter": ops, "unit": unit, "hart0_only": hart0, "note": note})
    return f"    case {mid}: /* {name} */\n{body}\n        break;\n"


def run(block_asm, outs, ins, clob=""):
    c = f' : {clob}' if clob else ""
    return (f"        RUN(do {{ uint64_t d0,d1,d2,d3,d4,d5,d6,d7; float e0,e1,e2,e3,e4,e5,e6,e7; (void)d0;(void)e0;\n"
            f"            __asm__ __volatile__(\"{block_asm}\" : {outs} : {ins}{c}); }} while (0));")


out = []
for op in INT_RRR:
    out.append(case(op, run(emit_int_block(op), ISINK, ISRC), note="scalar integer"))
for op, imm in INT_RRI:
    out.append(case(op, run(emit_int_block(op, imm=imm), ISINK, ISRC), note="scalar integer, immediate"))
for op in FLT_RRR:
    out.append(case(op, run(emit_int_block(op), FSINK, FSRC), note="scalar float"))
for op in FLT_RRRR:
    out.append(case(op, run(emit_fused(op), FSINK, FSRC), note="scalar float, fused"))
for op in FLT_R:
    out.append(case(op, run(emit_int_block(op, srcs=1), FSINK, FSRC), note="scalar float, unary"))
for op in FLT_CMP:
    out.append(case(op, run(emit_int_block(op), ISINK, FSRC), note="float compare to integer"))
for op in FLT_F2X:
    out.append(case(op, run(emit_int_block(op, srcs=1), ISINK, FSRC), note="float to integer register"))
for op in FLT_X2F:
    out.append(case(op, run(emit_int_block(op, srcs=1), FSINK, ISRC), note="integer register to float"))
for op in VEC_RRR:
    out.append(case(op, "        load_vsrc(src);\n" + run(emit_vec(op, 2), "", "", VSINK), note="8-lane vector"))
for op in VEC_RRRR:
    out.append(case(op, "        load_vsrc(src);\n" + run(emit_vec(op, 3), "", "", VSINK), note="8-lane vector, fused"))
for op in VEC_R:
    out.append(case(op, "        load_vsrc(src);\n" + run(emit_vec(op, 1), "", "", VSINK), note="8-lane vector, unary"))
for op, imm in VEC_RI:
    out.append(case(op, "        load_vsrc(src);\n" + run(emit_vec(op, 2, imm=imm), "", "", VSINK), note="8-lane vector, immediate"))
for op in VEC_M:
    out.append(case(op, "        load_vsrc(src);\n" + run(emit_vec(op, 2, mask_out=True), "", "", '"memory"'), note="8-lane compare into a mask register"))
for op in VEC_BCX:
    body = "\\n".join(f"{op} f{8+i}, %{i}" for i in range(8))
    out.append(case(op, "        load_vsrc(src);\n" + run(body, "", ISRC, VSINK), note="broadcast an integer register to 8 lanes"))
for op, imm in VEC_BCI:
    body = "\\n".join(f"{op} f{8+i}, {imm}" for i in range(8))
    out.append(case(op, "        load_vsrc(src);\n" + run(body, "", "", VSINK), note="broadcast an immediate to 8 lanes"))
for op in MEM_LD:
    body = "\\n".join(f"{op} %{i}, {8*i}(%8)" for i in range(8))
    out.append(case(op, run(body, ISINK, '"r"(src)', '"memory"'), unit="load from an L1-resident 256 B buffer", note="scalar load, L1 hit"))
for op in MEM_ST:
    body = "\\n".join(f"{op} %{i}, {8*i}(%8)" for i in range(8))   # no outputs: sources are %0..%7, base %8
    out.append(case(op, run(body, "", ISRC + ', "r"(src)', '"memory"'), unit="store to an L1-resident 256 B buffer", note="scalar store, L1 hit"))
for op in MEM_FLD:
    body = "\\n".join(f"{op} %{i}, {4*i}(%8)" for i in range(8))
    out.append(case(op, run(body, FSINK, '"r"(src)', '"memory"'), note="scalar float load, L1 hit"))
for op in MEM_FST:
    body = "\\n".join(f"{op} %{i}, {4*i}(%8)" for i in range(8))
    out.append(case(op, run(body, "", FSRC + ', "r"(src)', '"memory"'), note="scalar float store, L1 hit"))
BASES = ', '.join(f'"r"(src + {32*i})' for i in range(8))   # the l.ps forms take no offset: one base per op
for op in MEM_VLD:
    if op.endswith("l.ps"):
        body = "\\n".join(f"{op} f{8+i}, 0(%{i})" for i in range(8))
        out.append(case(op, "        load_vsrc(src);\n" + run(body, "", BASES, VSINK + ', "memory"'), note="32 B vector load bypassing the L1, straight to the L2"))
    else:
        body = "\\n".join(f"{op} f{8+i}, {32*i}(%0)" for i in range(8))
        out.append(case(op, "        load_vsrc(src);\n" + run(body, "", '"r"(src)', VSINK + ', "memory"'), note="32 B vector load of the source buffer, L1 hit"))
for op in MEM_VST:
    if op.endswith("l.ps"):
        body = "\\n".join(f"{op} f{i}, 0(%{i})" for i in range(8))
        out.append(case(op, "        load_vsrc(src);\n" + run(body, "", BASES, '"memory"'), note="32 B vector store bypassing the L1, straight to the L2"))
    else:
        body = "\\n".join(f"{op} f{i}, {32*i}(%0)" for i in range(8))
        out.append(case(op, "        load_vsrc(src);\n" + run(body, "", '"r"(src)', '"memory"'), note="32 B vector store, L1 hit"))
for name, tmpl in BRANCH:
    body = "\\n".join(tmpl.replace("%8", f"%{8+i}").replace("%9", f"%{8+(i+1)%8}") for i in range(8))
    out.append(case(name, run(body, ISINK, ISRC), note="branch; the sinks are unused"))
for name, tmpl in MISC:
    body = "\\n".join(tmpl.replace("%0", f"%{i}") for i in range(8))
    out.append(case(name, run(body, ISINK, ISRC, '"memory"' if name in ("fence",) else ""), note=name))
for op in ATOMIC:
    # one word per hart, uncontended: local (l) in the shire's scratchpad, global (g) in DRAM
    # both forms on a private DRAM line: the l form resolves in this shire's L2, the g form in the line's home L3
    # (a scratchpad address raises a bus error for either)
    base = "a->slice + hart * 64"
    body = "\\n".join(f"{op} %{i}, %{8+i}, (%16)" for i in range(8))
    out.append(case(op, f"        {{ const uint64_t abase = {base};\n" + run(body, ISINK, ISRC + ', "r"(abase)', '"memory"') + " }",
                    note="atomic on a private DRAM word, uncontended: " + ("resolved in the local L2" if "l." in op else "resolved at the home L3")))
for name, tmpl in COMPRESSED:
    opt = ".option norvc\\n" if "norvc" in name else ".option rvc\\n"
    body = opt + "\\n".join(tmpl.replace("%0", f"%{i}").replace("%8", f"%{8+i}") for i in range(8)) + "\\n.option pop"
    body = ".option push\\n" + body
    # in-place: sinks initialised from sources ("+r")
    ins = ', '.join(f'"r"(s{i})' for i in range(8))
    outs = ', '.join(f'"+r"(d{i})' for i in range(8))
    pre = "        " + " ".join(f"d{i}=s{i};" for i in range(8)) + "\n"
    out.append(case(name, f"        RUN(do {{ uint64_t d0=s0,d1=s1,d2=s2,d3=s3,d4=s4,d5=s5,d6=s6,d7=s7;\n            __asm__ __volatile__(\"{body}\" : {outs} : {ins}); }} while (0));",
                    note="compressed vs uncompressed in-place form" if True else ""))

open(os.path.join(HERE, "kernel", "enercat_ops.inc"), "w").write("".join(out))
hdr = ["// Generated by gen_ops.py. Mode ids for the generated instruction cases, and the host's table.", "#pragma once",
       "#define EC_GEN_FIRST 100", f"#define EC_GEN_COUNT {len(modes)}"]
hdr.append("#ifdef __cplusplus\n#include <string>\n#include <vector>\nstruct EcGenMode { const char* name; unsigned mode; unsigned ops_per_iter; const char* unit; bool hart0; const char* note; };")
hdr.append("static const std::vector<EcGenMode> EC_GEN_MODES = {")
for m in modes:
    hdr.append(f'  {{"{m["name"]}", {m["mode"]}, {m["ops_per_iter"]}, "{m["unit"]}", {"true" if m["hart0_only"] else "false"}, "{m["note"]}"}},')
hdr.append("};\n#endif")
open(os.path.join(HERE, "enercat_modes.h"), "w").write("\n".join(hdr) + "\n")
json.dump(modes, open(os.path.join(HERE, "enercat_modes.json"), "w"), indent=1)
print(f"{len(modes)} instruction modes generated")
