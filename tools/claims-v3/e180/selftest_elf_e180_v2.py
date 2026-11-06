#!/usr/bin/env python3
"""E180 (the kit's dated note 2, KIT.md.dated-note-2.md section 1): the desk test of check_elf_e180_v2.py, on listings built from a real
objdump listing, with both of the box's modes in one listing.

    python3 -B tools/claims-v3/e180/selftest_elf_e180_v2.py [--listing docs/reports/data/2026-10-21-dtf/proof/enercat-df-aifoundry2.dis.txt]

The listing is the committed disassembly of the enercat kernel built with the box toolchain's objdump (E61's V3-DTF proof, 7eb1ec79). Each
case is that whole real listing followed by one or two generated cases made from mode 160's own case as the compiler laid it out (104
instructions: the fsw saves of fs0 and fs1, mov.m.x, load_vsrc's eight flw.ps, cycles(), ld/li/add, the 64-op loop, cycles() and bltu, the
flw restores and the j to the join), its body rewritten to 261's (fadd.ps fs0,fs0,ft0 ...) or 262's (fadd.pi ...) form and the zeroing block
(fxor.pi fs0,ft0,ft0 ...) placed where their source puts it, after load_vsrc's last flw.ps. That form, and the compiler's reverse mode order
(each generated case 104 instructions before the previous mode's, 43 of 43 pairs in the real listing), are the kit verifier's (kitv-e180,
work/adv_elf.py and layout_order.py). The cases, with the A1-7 reading wanted (and v1's, where it shows a fault):
  F0  the real listing alone: 261 and 262 UNREAD (absent), the control 160 PASS, exit 0;
  F1  262 then 261, adjacent (the box's order): both PASS (v1: 261 UNREAD, the zeroing block found twice: the major fault, shown);
  F2  261 then 262, adjacent: both PASS (v1: 262 UNREAD);  F3 the two more than 400 instructions apart: both PASS;
  F4  261's zeroing block inside the loop (the branch goes back to it): FAIL (v1: UNREAD, the fail-open, shown);
  F5  a store fsw fs0,44(sp) between the zeroing block and the loop: PASS with a remark (v1: FAIL);
  F6  a reload flw fs0,44(sp) there, a real write: FAIL;  F7 a read fmv.x.w a1,fs1 in the loop: PASS with E61's remark (v1: FAIL);
  F8  the zeroing block twice in the case: PASS, the nearest (v1: UNREAD);  F9 a write to f9 inside the loop: FAIL;
  F10 a write to f10 between the block and the loop: FAIL;  F11 a call inside the loop: FAIL;  F12 a call between: FAIL;
  F13 262 then 261 with 261's own zeroing block missing: 261 UNREAD (262's block, behind its loop and j, is not taken), 262 PASS;
  F14 the body twice: UNREAD;  F15 the loop's backward branch missing: UNREAD;  F16 a trailing rounding mode (",dyn"): PASS;
  F17 no listing (the file absent), and F18 an empty one: 261 and 262 UNREAD, exit 0.
Prints one line a case and "SELFTEST-ELF-E180-V2 PASS: n of n"; exit 1 on any failure. Standard library only; it writes only in a
temporary directory.
SPDX-License-Identifier: Apache-2.0
"""
import argparse
import os
import re
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.dont_write_bytecode = True
import check_elf_e180 as ce  # noqa: E402

DEFAULT = os.path.join(HERE, "..", "..", "..", "docs", "reports", "data", "2026-10-21-dtf", "proof", "enercat-df-aifoundry2.dis.txt")
ABI_OF = {v: k for k, v in ce.ABI.items()}
ZERO = [("fxor.pi", [ABI_OF[8 + r], "ft0", "ft0"]) for r in range(8)]


def real_case(ins):
    """mode 160's whole case in the real listing: from its fsw fs0 save to the j after its loop"""
    body = [ce.norm(o) for o in ce.M160["body"]] * 8
    i = ce.find(ins, body)[0]
    start = max(k for k in range(i) if ins[k][1] == "fsw" and ins[k][2][:1] == ["fs0"])
    end = next(k for k in range(i + 64, i + 120) if ins[k][1] == "j")
    return ins[start:end + 1], i - start


def mk_case(case, k_body, size, mn, base, zero="after_load", between=None, in_loop=None, twice=False, rm=False, no_branch=False):
    """one generated case as [addr, mnemonic, ops] rows from mode 160's real case; returns (rows, the next free address)"""
    out, a, fix = [], base, None
    last_ld = max(q for q, t in enumerate(case[:k_body]) if t[1] == "flw.ps")
    body_at = None
    for q, t in enumerate(case):
        if q == k_body:
            if zero == "loop_head":
                fix = a
                for z in ZERO:
                    out.append([a, z[0], list(z[1])]); a += 4
            body_at = a
        if k_body <= q < k_body + 64:
            lane = (q - k_body) % 8
            out.append([a, mn, [ABI_OF[8 + lane], ABI_OF[8 + lane], ABI_OF[lane]] + (["dyn"] if rm else [])]); a += 4
            continue
        if t[1] == "bltu" and no_branch:
            out.append([a, "nop", []]); a += 4
        else:
            out.append([a, t[1], list(t[2])]); a += size.get(t[0], 4)
        if q == k_body + 64 and in_loop:
            out.append([a, in_loop[0], list(in_loop[1])]); a += 4
        if q == last_ld:
            if twice:
                for z in ZERO:
                    out.append([a, z[0], list(z[1])]); a += 4
                out.append([a, "nop", []]); a += 4
            if zero in ("after_load",):
                for z in ZERO:
                    out.append([a, z[0], list(z[1])]); a += 4
            if between:
                out.append([a, between[0], list(between[1])]); a += 4
    tgt = fix if fix is not None else body_at
    for r in out:
        if r[1] == "bltu":
            r[2] = r[2][:-1] + [f"{tgt:x} <entry_point+0x0>"]
    return out, a


def write(path, raw, cases, extra_body=None):
    with open(path, "w") as f:
        for line in raw:              # the real listing first: mode 160 (the control) and the rest of the kernel
            f.write(line + "\n")
        for c in cases:
            for addr, mn, ops in c:
                f.write(f"  {addr:x}:\t00000000          \t{mn}\t{','.join(ops)}\n")


def run(script, path, extra=("--also-160",)):
    r = subprocess.run([sys.executable, "-B", os.path.join(HERE, script), path] + list(extra), capture_output=True, text=True)
    v = {}
    lines = {}
    for ln in r.stdout.splitlines():
        for m in ("261", "262", "160"):
            if f"mode {m}:" in ln and ln.split()[:1] and ln.split()[0] in ("PASS", "FAIL", "UNREAD"):
                v[m] = ln.split()[0]
                lines[m] = ln
    return r.returncode, v, lines, r.stdout


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--listing", default=DEFAULT)
    a = ap.parse_args()
    raw = open(a.listing, errors="replace").read().splitlines()
    ins = ce.parse(a.listing)
    size = {}
    for line in raw:
        m = re.match(r"\s*([0-9a-f]+):\s+([0-9a-f]+)\s+", line)
        if m:
            size[int(m.group(1), 16)] = len(m.group(2)) // 2
    case, k_body = real_case(ins)
    base = max(t[0] for t in ins) + 0x100
    res = []

    def check(name, got, want, detail):
        ok = got == want
        res.append(ok)
        print(f"{'PASS' if ok else 'FAIL'} {name}: got {got}, want {want}; {detail[:230]}")

    def mk(mn, b, **kw):
        return mk_case(case, k_body, size, mn, b, **kw)

    with tempfile.TemporaryDirectory() as t:
        rc, v, L, out = run("check_elf_e180_v2.py", a.listing)
        check("F0 the real listing alone (v2)", (rc, v.get("261"), v.get("262"), v.get("160")), (0, "UNREAD", "UNREAD", "PASS"),
              out.splitlines()[-1])
        specs = []
        c262, x = mk("fadd.pi", base)
        c261, _ = mk("fadd.ps", x)
        specs.append(("F1 262 then 261, adjacent (the box's order)", [c262, c261], ("PASS", "PASS", 0), ("UNREAD", "PASS")))
        c261, x = mk("fadd.ps", base)
        c262, _ = mk("fadd.pi", x)
        specs.append(("F2 261 then 262, adjacent", [c261, c262], ("PASS", "PASS", 0), ("PASS", "UNREAD")))
        c261, x = mk("fadd.ps", base)
        pad = [[x + 4 * k, "addi", ["a0", "a0", "1"]] for k in range(420)]
        c262, _ = mk("fadd.pi", x + 4 * 420)
        specs.append(("F3 the two more than 400 instructions apart", [c261, pad, c262], ("PASS", "PASS", 0), ("PASS", "PASS")))
        c, _ = mk("fadd.ps", base, zero="loop_head")
        specs.append(("F4 261's zeroing block inside the loop", [c], ("FAIL", "UNREAD", 1), ("UNREAD", "UNREAD")))
        c, _ = mk("fadd.ps", base, between=("fsw", ["fs0", "44(sp)"]))
        specs.append(("F5 a store of fs0 between the zeroing block and the loop", [c], ("PASS", "UNREAD", 0), ("FAIL", "UNREAD")))
        c, _ = mk("fadd.ps", base, between=("flw", ["fs0", "44(sp)"]))
        specs.append(("F6 a reload of fs0 between (a write)", [c], ("FAIL", "UNREAD", 1), ("FAIL", "UNREAD")))
        c, _ = mk("fadd.ps", base, in_loop=("fmv.x.w", ["a1", "fs1"]))
        specs.append(("F7 a read of fs1 inside the loop", [c], ("PASS", "UNREAD", 0), ("FAIL", "UNREAD")))
        c, _ = mk("fadd.ps", base, twice=True)
        specs.append(("F8 the zeroing block twice in the case", [c], ("PASS", "UNREAD", 0), ("UNREAD", "UNREAD")))
        c, _ = mk("fadd.ps", base, in_loop=("fadd.ps", ["fs1", "ft0", "ft0"]))
        specs.append(("F9 a write to f9 inside the loop", [c], ("FAIL", "UNREAD", 1), ("FAIL", "UNREAD")))
        c, _ = mk("fadd.ps", base, between=("fxor.pi", ["fa0", "ft1", "ft1"]))
        specs.append(("F10 a write to f10 between the block and the loop", [c], ("FAIL", "UNREAD", 1), ("FAIL", "UNREAD")))
        c, _ = mk("fadd.ps", base, in_loop=("jal", ["ra", "8005801020 <entry_point>"]))
        specs.append(("F11 a call inside the loop", [c], ("FAIL", "UNREAD", 1), ("FAIL", "UNREAD")))
        c, _ = mk("fadd.ps", base, between=("jal", ["ra", "8005801020 <entry_point>"]))
        specs.append(("F12 a call between the block and the loop", [c], ("FAIL", "UNREAD", 1), ("PASS", "UNREAD")))
        c262, x = mk("fadd.pi", base)
        c261, _ = mk("fadd.ps", x, zero="none")
        specs.append(("F13 262 then 261, 261's own zeroing block missing", [c262, c261], ("UNREAD", "PASS", 0), ("FAIL", "PASS")))
        c261, x = mk("fadd.ps", base)
        c261b, _ = mk("fadd.ps", x + 0x400)
        specs.append(("F14 the body twice", [c261, c261b], ("UNREAD", "UNREAD", 0), ("UNREAD", "UNREAD")))
        c, _ = mk("fadd.ps", base, no_branch=True)
        specs.append(("F15 the loop's backward branch missing", [c], ("UNREAD", "UNREAD", 0), ("UNREAD", "UNREAD")))
        c, _ = mk("fadd.ps", base, rm=True)
        specs.append(("F16 a trailing rounding mode", [c], ("PASS", "UNREAD", 0), ("PASS", "UNREAD")))
        for n, (name, cases, want, want_v1) in enumerate(specs, 1):
            p = os.path.join(t, f"f{n}.dis.txt")
            write(p, raw, cases)
            rc, v, L, out = run("check_elf_e180_v2.py", p)
            rc1, v1r, _L1, _o1 = run("check_elf_e180.py", p)
            got = (v.get("261"), v.get("262"), rc)
            detail = " | ".join(L.get(m, "(no line)")[:110] for m in ("261", "262")) + f" | control 160 {v.get('160')}"
            check(name, got + (v.get("160"),), want + ("PASS",), detail)
            check(f"   v1 on the same listing ({name.split()[0]})", (v1r.get("261"), v1r.get("262")), want_v1,
                  "v1's reading, kept beside: " + ("the fault, shown" if (v1r.get("261"), v1r.get("262")) != want[:2] else "as v2"))
        rc, v, L, out = run("check_elf_e180_v2.py", os.path.join(t, "absent.dis.txt"))
        check("F17 no listing (the file absent)", (rc, v.get("261"), v.get("262")), (0, "UNREAD", "UNREAD"), L.get("261", ""))
        p = os.path.join(t, "empty.dis.txt")
        open(p, "w").close()
        rc, v, L, out = run("check_elf_e180_v2.py", p)
        check("F18 an empty listing", (rc, v.get("261"), v.get("262")), (0, "UNREAD", "UNREAD"), L.get("261", ""))
    n = sum(res)
    print(f"SELFTEST-ELF-E180-V2 {'PASS' if n == len(res) else 'FAIL'}: {n} of {len(res)}")
    sys.exit(0 if n == len(res) else 1)


if __name__ == "__main__":
    main()
