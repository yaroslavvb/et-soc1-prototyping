#!/usr/bin/env python3
"""E76, the part that needs no card: what a U-mode trap costs, counted from the firmware that handles it.

    python3 tools/claims-v3/tr/static_cost.py --out <dir>        # static.json + static.txt

The board meter cannot answer "how much energy does one trap cost". A trap ends the kernel on that hart
(see README.md), so there is one trap per hart per launch, one launch per process, and a process is ~1 s: the
per-trap energy the instruction count implies (tens of microjoules over the chip) is three to four orders of
magnitude under what a 10 Hz board meter resolves in a 1 s window. What CAN be done exactly is to count the
instructions the handling path executes, and to price them from the catalogue
(docs/energy-manual/03a-every-instruction.md: 5.1-10.5 pJ for the common scalar ops, 6.2 pJ for `add` on zeros).

This script counts, from the firmware ELFs installed on the box (/opt/et/lib/esperanto-fw/*/*.elf) and the
compiler's own soft-float library:

  1. the **trap path**: the instruction counts of `trap_routine` (M-mode: emulates `csrrs mhartid`, delegates
     everything else to S-mode), the M-mode `trap_handler` entry/exit, and S-mode `exception_handler` plus what
     it calls (context save, trace eviction, the CM->MM message, `return_from_kernel`);
  2. the **software substitutes**: `__divsf3`, `__mulsf3`, `__floatdisf`, `__fixsfdi` and `sqrtf` in libgcc /
     libm as the toolchain ships them, because a C kernel that writes `a / b` or `sqrtf(x)` on this silicon gets
     one of these, not the trapping instruction.

Everything is a count of instructions, with the symbol it came from, so a reader can re-price it against any
version of the catalogue. Nothing here is measured energy and nothing here claims to be.
"""
import argparse
import glob
import json
import os
import re
import subprocess

OBJDUMPS = ["/opt/et/riscv64-unknown-elf/bin/objdump", "riscv64-unknown-elf-objdump", "objdump"]
FW = ["/opt/et/lib/esperanto-fw/MachineMinion/MachineMinion.elf",
      "/opt/et/lib/esperanto-fw/WorkerMinion/WorkerMinion.elf",
      "/opt/et/lib/esperanto-fw/MasterMinion/MasterMinion.elf"]
TRAP_SYMS = ["trap_routine", "trap_handler", "exception_handler", "send_exception_message",
             "return_from_kernel", "syscall_handler", "Trace_Evict_CM_Buffer", "Trace_Evict_UMode_Buffer",
             "CM_To_MM_Save_Execution_Context", "CM_To_MM_Iface_Unicast_Send", "Trace_Execution_Stack"]
SOFT_SYMS = ["__divsf3", "__mulsf3", "__addsf3", "__floatdisf", "__floatundisf", "__fixsfdi", "__fixunssfdi",
             "sqrtf", "__divdf3", "sinf", "__ieee754_sqrtf", "__ieee754_sinf", "__ieee754_rem_pio2f",
             "__kernel_sinf", "fmodf", "__ieee754_fmodf"]
# The thirteen that trap in U-mode (docs/energy-manual/03a-every-instruction.md). If one of these turns up
# INSIDE a library routine, then ordinary C that calls that routine dies on this silicon, which is a practical
# finding and not a detail: 14-card-behaviour.md already records that "a double anywhere in a kernel" traps.
TRAPPING = ["fdiv.s", "fsqrt.s", "fdiv.ps", "fsqrt.ps", "frsq.ps", "fsin.ps", "fdiv.pi", "fdivu.pi",
            "frem.pi", "fremu.pi", "fcvt.l.s", "fcvt.s.l", "rdcycle"]


def objdump():
    for o in OBJDUMPS:
        if os.path.isabs(o):
            if os.access(o, os.X_OK):
                return o
        else:
            try:
                subprocess.run([o, "--version"], capture_output=True, timeout=20, check=True)
                return o
            except (OSError, subprocess.SubprocessError):
                continue
    return None


def counts(od, elf, syms, want_mnemonics=False):
    """{symbol: instructions} for every wanted symbol present in elf, from objdump -d.

    With want_mnemonics, returns ({symbol: n}, err, {symbol: {mnemonic: n}}) so a routine can be checked for the
    thirteen that trap."""
    try:
        r = subprocess.run([od, "-d", elf], capture_output=True, text=True, timeout=300)
    except (OSError, subprocess.SubprocessError) as e:
        return {}, f"objdump failed: {e}"
    out, cur, mn = {}, None, {}
    head = re.compile(r"^[0-9a-f]+ <([^>]+)>:")
    insn = re.compile(r"^\s+[0-9a-f]+:\s+[0-9a-f ]+\t(\S+)")
    for line in r.stdout.splitlines():
        m = head.match(line)
        if m:
            name = m.group(1)
            # A compiler-local label (.L0, .LVL3, .L1) opens a new <name>: header inside the SAME function, so
            # a parser that resets here counts only up to the first branch target: __divsf3 then reads 12
            # instructions instead of its real length. Keep the current symbol across local labels.
            if name.startswith("."):
                continue
            cur = name if any(name == s or name.startswith(s + ".") for s in syms) else None
            if cur:
                out.setdefault(cur, 0)
                mn.setdefault(cur, {})
            continue
        if cur:
            i = insn.match(line)
            if i:
                out[cur] += 1
                mn[cur][i.group(1)] = mn[cur].get(i.group(1), 0) + 1
    return (out, "", mn) if want_mnemonics else (out, "")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    od = objdump()
    res = {"objdump": od, "trap_path": {}, "soft_float": {}, "notes": []}
    if not od:
        res["notes"].append("no objdump found: nothing counted")
    else:
        for elf in FW:
            if not os.path.exists(elf):
                res["notes"].append(f"missing firmware ELF {elf}")
                continue
            c, err = counts(od, elf, TRAP_SYMS)
            if err:
                res["notes"].append(f"{elf}: {err}")
            res["trap_path"][os.path.basename(elf)] = c
        libs = []
        for pat in ("/opt/et/riscv64-unknown-elf/lib/**/libgcc.a", "/opt/et/**/libgcc.a",
                    "/opt/et/riscv64-unknown-elf/**/libm.a", "/opt/et/**/libm.a"):
            libs += glob.glob(pat, recursive=True)
        res["soft_float_trapping"] = {}
        for lib in sorted(set(libs))[:6]:
            c, err, mn = counts(od, lib, SOFT_SYMS, want_mnemonics=True)
            if err:
                res["notes"].append(f"{lib}: {err}")
            if c:
                res["soft_float"][lib] = c
                for sym, ops in mn.items():
                    hit = {k: v for k, v in ops.items() if k in TRAPPING}
                    if hit:
                        res["soft_float_trapping"].setdefault(os.path.basename(lib), {})[sym] = hit
                    res.setdefault("soft_float_mnemonics", {}).setdefault(os.path.basename(lib), {})[sym] = ops
        if not libs:
            res["notes"].append("no libgcc.a / libm.a found under /opt/et: the software substitute counts are "
                                "not available on this box")
    # the catalogue's per-instruction energies, for pricing the counts (03a-every-instruction.md, random data)
    res["catalogue_pJ_per_instruction"] = {"add": 9.7, "addi": 8.9, "and": 9.6, "lw": None, "nop": 5.4,
                                           "mul": 43.4, "div": 157.2, "fmul.s": None,
                                           "note": "random-operand means over nine measurements on three cards; "
                                                   "a mixed scalar path is 6-11 pJ per instruction"}
    res["per_trap_estimate"] = {
        "formula": "instructions on the handling hart x pJ per instruction; one trap per hart per launch",
        "pJ_per_instruction_band": [6, 11],
        "note": "multiply by 1,024 or 2,048 harts for the whole-chip cost of a launch in which every hart traps"}
    json.dump(res, open(os.path.join(a.out, "static.json"), "w"), indent=1)
    with open(os.path.join(a.out, "static.txt"), "w") as f:
        for elf, c in res["trap_path"].items():
            for s, n in sorted(c.items()):
                f.write(f"trap  {elf:22s} {s:34s} {n:6d} instructions\n")
        for lib, c in res["soft_float"].items():
            for s, n in sorted(c.items()):
                f.write(f"soft  {os.path.basename(lib):22s} {s:34s} {n:6d} instructions\n")
        for lib, syms in res.get("soft_float_trapping", {}).items():
            for s, hit in sorted(syms.items()):
                f.write(f"TRAPS {lib:22s} {s:34s} uses {hit} -- C that calls it dies in U-mode\n")
        for n in res["notes"]:
            f.write(f"note  {n}\n")
    print(open(os.path.join(a.out, "static.txt")).read(), end="")
    tot = sum(sum(c.values()) for c in res["trap_path"].values())
    print(f"total instructions in the named trap-path symbols: {tot}")


if __name__ == "__main__":
    main()
