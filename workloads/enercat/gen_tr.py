#!/usr/bin/env python3
"""Generate the V3-TR kernel cases (modes 500+) and the host's table for them: the thirteen instructions that
trap in U-mode, each beside a control of the same shape that does not.

    python3 workloads/enercat/gen_tr.py      # writes kernel/enercat_tr.inc, enercat_tr.h, enercat_tr_modes.json

Compiled only with -DENERCAT_TR=ON (build/enercat-tr): without it the kernel ELF is the catalogue's, unchanged,
because the cases are spliced into enercat.c's switch behind #ifdef and gen_ops.py's numbering is untouched —
the same arrangement gen_df.py uses for the V3-DTF modes (300+) and enercat_gs for the gathers (400+).

tools/claims-v3/tr/README.md has the experiment (E76) and why each mode exists. In short: the energy manual's
[3.1](../../docs/energy-manual/03a-every-instruction.md) lists thirteen instructions that "trapped in U-mode in a
one-off check while the catalogue was written (the card and the log of that check were not kept)", and they have
no energy figure. Two of them (`fdiv.ps`, `fsqrt.ps`) are already modes in the catalogue's own build
(EC_FDIV_PS, EC_FSQRT_PS); the other eleven have never been compiled. These cases compile all thirteen, so the
claim can be replicated with a log, and pair each with a control of the same shape and the same op count, so a
launch that completes and a launch that dies differ in one instruction.

A trap is not an exception the kernel can survive: M-mode's trap_routine emulates only `csrrs mhartid` and
delegates every other illegal instruction to S-mode, whose exception_handler saves the context, evicts the trace
buffers, sends a CM->MM exception message and calls `return_from_kernel(0, KERNEL_RETURN_EXCEPTION)`. So a mode
here either runs (and is an ordinary catalogue item with an energy) or ends that hart's kernel on its first op.
Run every TR mode with `--window 0`, which makes one iteration of the block, and `--seconds 0.001`, which makes
one launch: a control then does 64 ops and returns, and a trapping mode dies on op 1 of 64.
"""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
FIRST = 500
VSINK = ", ".join(f'"f{8 + i}"' for i in range(8))

# (name, shape, mnemonic, traps?, note)
#   vec2 / vec1: packed, sources f0..f7 rotating, sinks f8..f15 (VBLOCK / V1BLOCK shape)
#   sca2 / sca1: scalar float, sources g0..g7, eight distinct sinks
#   f2x: rd <- fs    x2f: fd <- rs    csr: rd <- CSR
MODES = [
    ("tr.fdiv.s",    "sca2", "fdiv.s",    True,  "one of the thirteen: scalar float divide"),
    ("tr.fsqrt.s",   "sca1", "fsqrt.s",   True,  "one of the thirteen: scalar float square root"),
    ("tr.fdiv.ps",   "vec2", "fdiv.ps",   True,  "one of the thirteen: packed float divide (also EC_FDIV_PS)"),
    ("tr.fsqrt.ps",  "vec1", "fsqrt.ps",  True,  "one of the thirteen: packed float square root (also EC_FSQRT_PS)"),
    ("tr.frsq.ps",   "vec1", "frsq.ps",   True,  "one of the thirteen: packed reciprocal square root"),
    ("tr.fsin.ps",   "vec1", "fsin.ps",   True,  "one of the thirteen: packed sine"),
    ("tr.fdiv.pi",   "vec2", "fdiv.pi",   True,  "one of the thirteen: packed integer divide"),
    ("tr.fdivu.pi",  "vec2", "fdivu.pi",  True,  "one of the thirteen: packed unsigned divide"),
    ("tr.frem.pi",   "vec2", "frem.pi",   True,  "one of the thirteen: packed integer remainder"),
    ("tr.fremu.pi",  "vec2", "fremu.pi",  True,  "one of the thirteen: packed unsigned remainder"),
    ("tr.fcvt.l.s",  "f2x",  "fcvt.l.s",  True,  "one of the thirteen: float to 64-bit integer"),
    ("tr.fcvt.s.l",  "x2f",  "fcvt.s.l",  True,  "one of the thirteen: 64-bit integer to float"),
    ("tr.csrr.cycle", "csr", "0xc00",     True,  "one of the thirteen: reading the cycle CSR"),
    # controls: the same shape and op count, known to run (every one is in the catalogue)
    ("tr.ctl.fmul.s",  "sca2", "fmul.s",  False, "control for the sca2 shape: 9.8 pJ in 3.1"),
    ("tr.ctl.fsgnj.s", "sca1c", "fsgnj.s", False, "control for the sca1 shape: fsgnj.s rd, rs, rs (the same source twice)"),
    ("tr.ctl.fmul.ps", "vec2", "fmul.ps", False, "control for the vec2 shape"),
    ("tr.ctl.frcp.ps", "vec1", "frcp.ps", False, "control for the vec1 shape, and the hardware reciprocal the software divide is built on"),
    ("tr.ctl.fmv.x.w", "f2x",  "fmv.x.w", False, "control for the f2x shape"),
    ("tr.ctl.fmv.w.x", "x2f",  "fmv.w.x", False, "control for the x2f shape"),
    ("tr.ctl.csrr.fccnb", "csr", "0xcc0", False, "control for the csr shape: the FCC non-blocking counter reads fine"),
]


def body(shape, op):
    """The eight-op block and the asm operands for one shape. Returns (pre, asm, outs, ins, clob)."""
    if shape == "vec2":
        pairs = [(0, 1), (2, 3), (4, 5), (6, 7), (1, 2), (3, 4), (5, 6), (7, 0)]
        asm = "\\n".join(f"{op} f{8 + i}, f{a}, f{b}" for i, (a, b) in enumerate(pairs))
        return "        load_vsrc(src);\n", asm, "", "", VSINK
    if shape == "vec1":
        asm = "\\n".join(f"{op} f{8 + i}, f{i}" for i in range(8))
        return "        load_vsrc(src);\n", asm, "", "", VSINK
    if shape == "sca2":
        asm = "\\n".join(f"{op} %{i}, %{8 + i}, %{8 + (i + 1) % 8}" for i in range(8))
        outs = ", ".join(f'"=&f"(d{i})' for i in range(8))
        ins = ", ".join(f'"f"(g{i})' for i in range(8))
        return "float d0, d1, d2, d3, d4, d5, d6, d7;", asm, outs, ins, ""
    if shape in ("sca1", "sca1c"):
        if shape == "sca1":
            asm = "\\n".join(f"{op} %{i}, %{8 + i}" for i in range(8))
        else:   # the same source twice, for a control whose mnemonic takes two
            asm = "\\n".join(f"{op} %{i}, %{8 + i}, %{8 + i}" for i in range(8))
        outs = ", ".join(f'"=&f"(d{i})' for i in range(8))
        ins = ", ".join(f'"f"(g{i})' for i in range(8))
        return "float d0, d1, d2, d3, d4, d5, d6, d7;", asm, outs, ins, ""
    if shape == "f2x":
        asm = "\\n".join(f"{op} %{i}, %{8 + i}" for i in range(8))
        outs = ", ".join(f'"=&r"(u{i})' for i in range(8))
        ins = ", ".join(f'"f"(g{i})' for i in range(8))
        return "uint64_t u0, u1, u2, u3, u4, u5, u6, u7;", asm, outs, ins, ""
    if shape == "x2f":
        asm = "\\n".join(f"{op} %{i}, %{8 + i}" for i in range(8))
        outs = ", ".join(f'"=&f"(d{i})' for i in range(8))
        ins = ", ".join(f'"r"(s{i})' for i in range(8))
        return "float d0, d1, d2, d3, d4, d5, d6, d7;", asm, outs, ins, ""
    if shape == "csr":
        asm = "\\n".join(f"csrr %{i}, {op}" for i in range(8))
        outs = ", ".join(f'"=&r"(u{i})' for i in range(8))
        return "uint64_t u0, u1, u2, u3, u4, u5, u6, u7;", asm, outs, "", ""
    raise SystemExit(f"unknown shape {shape}")


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--skip", default="", help="comma-separated mode names to leave OUT of the generated files "
                                              "(for a mnemonic this assembler does not know); the mode ids of the "
                                              "rest do not move, so a skip never renumbers anything")
    a = ap.parse_args()
    skip = {s for s in a.skip.split(",") if s}
    inc = ["// Generated by gen_tr.py: the V3-TR cases (modes 500+), spliced into enercat.c's switch under ENERCAT_TR.",
           "// Do not edit; re-run gen_tr.py." + (f" Skipped: {sorted(skip)}" if skip else "")]
    rows, table = [], []
    for k, (name, shape, op, traps, note) in enumerate(MODES):
        mode = FIRST + k
        if name in skip:
            table.append({"name": name, "mode": mode, "skipped": True, "insn": op, "shape": shape,
                          "expected_to_trap": traps, "note": note + " [SKIPPED: not assembled]"})
            continue
        pre, asm, outs, ins, clob = body(shape, op)
        inc.append(f"    case {mode}: /* {name} */")
        if shape in ("vec1", "vec2"):
            inc.append(pre.rstrip("\n"))
            inc.append(f'        RUN(__asm__ __volatile__("{asm}" : : : {clob}));')
        else:
            inc.append("        load_vsrc(src);")
            inc.append(f'        RUN(do {{ {pre}')
            inc.append(f'            __asm__ __volatile__("{asm}" : {outs}'
                       + (f' : {ins}' if ins else "") + '); }} while (0));')
        inc.append("        break;")
        rows.append(f'  {{"{name}", {mode}, {8 * 8}, "instruction", false, "{note}"}},')
        table.append({"name": name, "mode": mode, "ops_per_iter": 64, "shape": shape, "insn": op,
                      "expected_to_trap": traps, "note": note})
    with open(os.path.join(HERE, "kernel", "enercat_tr.inc"), "w") as f:
        f.write("\n".join(inc).replace("}} while (0));", "} while (0));") + "\n")
    with open(os.path.join(HERE, "enercat_tr.h"), "w") as f:
        f.write("// Generated by gen_tr.py: the V3-TR modes (ids 500+), for kernel and host. Compiled only with ENERCAT_TR.\n"
                "#pragma once\n"
                f"#define EC_TR_FIRST {FIRST}\n#define EC_TR_COUNT {len(MODES)}\n"
                "#ifdef __cplusplus\n#include <vector>\n#include \"enercat_modes.h\"\n"
                "static const std::vector<EcGenMode> EC_TR_MODES = {\n" + "\n".join(rows) + "\n};\n#endif\n")
    with open(os.path.join(HERE, "enercat_tr_modes.json"), "w") as f:
        json.dump({"first": FIRST, "modes": table}, f, indent=1)
    print(f"{len(MODES)} TR modes, {FIRST}..{FIRST + len(MODES) - 1} "
          f"({sum(1 for m in MODES if m[3])} expected to trap, {sum(1 for m in MODES if not m[3])} controls)")


if __name__ == "__main__":
    main()
