#!/usr/bin/env python3
"""E180 (the kit's dated note 1, KIT.md.dated-note-1.md section 5): the desk test of check_elf_e180.py, on a real objdump listing.

    python3 -B tools/claims-v3/e180/selftest_elf_e180.py [--listing docs/reports/data/2026-10-21-dtf/proof/enercat-df-aifoundry2.dis.txt]

The listing is the committed disassembly of the enercat kernel built with the box toolchain's objdump (E61's V3-DTF proof, 7eb1ec79: an
aifoundry2 build of 21 Oct 2026 that holds every generated mode, mode 160 among them, and neither 261 nor 262). The cases:
  E0  the real listing: 261 and 262 UNREAD (absent), the control mode 160 PASS, exit 0;
  E1  a listing for 261 made from it: mode 160's real loop, its body rewritten to 261's (fadd.ps fs0,fs0,ft0 ...), and the zeroing block
      (fxor.pi fs0,ft0,ft0 ...) placed where 261's source puts it, after load_vsrc's real flw.ps lines and before cycles(): PASS (the
      40 real instructions before the loop include the compiler's save and restore of fs0 and fs1, f8 and f9, around the case: before
      the zeroing block, as they must be);  E2 the same with fadd.pi (262's form): PASS;
  E3  a write to f9 inside the loop, after the body: FAIL;  E4 a write to f10 between the zeroing block and the loop: FAIL;
  E5  a call inside the loop: FAIL;  E6 no zeroing block: UNREAD;  E7 the body twice: UNREAD;
  E8  the body printed with a trailing rounding mode (",dyn"): PASS.
Prints one line a case and "SELFTEST-ELF-E180 PASS: n of n"; exit 1 on any failure. Standard library only; it writes only in a
temporary directory.
SPDX-License-Identifier: Apache-2.0
"""
import argparse
import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.dont_write_bytecode = True
import check_elf_e180 as ce  # noqa: E402

DEFAULT = os.path.join(HERE, "..", "..", "..", "docs", "reports", "data", "2026-10-21-dtf", "proof", "enercat-df-aifoundry2.dis.txt")
ABI_OF = {v: k for k, v in ce.ABI.items()}


def fmt(addr, mn, ops):
    return f"  {addr:x}:\t00000000          \t{mn}\t{','.join(ops)}"


def build(lines, ins, mn_body, rm=False, stray_in_loop=False, stray_before=False, call=False, nozero=False, twice=False):
    body = [ce.norm(o) for o in ce.M160["body"]] * 8
    i = ce.find(ins, body)[0]
    j = i + len(body)
    tail = ins[j:j + 30]
    br = next(k for k, t in enumerate(tail) if t[1].startswith("b") and t[2] and int(t[2][-1].split()[0], 16) <= ins[i][0])
    head = int(tail[br][2][-1].split()[0], 16)
    k_head = next(k for k, t in enumerate(ins) if t[0] == head)
    pre = ins[k_head - 40:k_head]
    # the zeroing block goes where 261's source puts it: right after load_vsrc's last flw.ps, before cycles() and the loop
    last_ld = max(q for q, t in enumerate(pre) if t[1] == "flw.ps")
    out = []
    for q, t in enumerate(pre):
        out.append(fmt(t[0], t[1], t[2]))
        if q == last_ld:
            if not nozero:
                for r in range(8):
                    out.append(fmt(t[0] + 1, "fxor.pi", [ABI_OF[8 + r], "ft0", "ft0"]))
            if stray_before:
                out.append(fmt(t[0] + 1, "fxor.pi", ["fa0", "ft1", "ft1"]))
    for t in ins[k_head:i]:
        out.append(fmt(t[0], t[1], t[2]))
    for q in range(len(body)):
        t = ins[i + q]
        lane = q % 8
        ops = [ABI_OF[8 + lane], ABI_OF[8 + lane], ABI_OF[lane]] + (["dyn"] if rm else [])
        out.append(fmt(t[0], mn_body, ops))
    if stray_in_loop:
        out.append(fmt(ins[j - 1][0] + 1, "fadd.ps", ["fs1", "ft0", "ft0"]))
    for q, t in enumerate(tail[:br + 1]):
        if call and q == 0:
            out.append(fmt(t[0] - 1, "jal", ["ra", "8005801020 <entry_point>"]))
        out.append(fmt(t[0], t[1], t[2]))
    if twice:
        base = tail[br][0] + 0x1000
        for q in range(len(body)):
            lane = q % 8
            out.append(fmt(base + 4 * q, mn_body, [ABI_OF[8 + lane], ABI_OF[8 + lane], ABI_OF[lane]]))
    return "\n".join(out) + "\n"


def run(path, extra=()):
    r = subprocess.run([sys.executable, "-B", os.path.join(HERE, "check_elf_e180.py"), path] + list(extra), capture_output=True, text=True)
    lines = r.stdout.splitlines()
    verdict = {}
    for ln in lines:
        for m in ("261", "262", "160"):
            if f"mode {m}:" in ln:
                verdict[m] = ln.split()[0]
    return r.returncode, verdict, lines


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--listing", default=DEFAULT)
    a = ap.parse_args()
    lines = open(a.listing, errors="replace").read()
    ins = ce.parse(a.listing)
    cases = []
    with tempfile.TemporaryDirectory() as t:
        rc, v, out = run(a.listing, ["--also-160"])
        cases.append(("E0 the real listing", rc == 0 and v == {"261": "UNREAD", "262": "UNREAD", "160": "PASS"}, out[-1]))
        specs = [("E1 261 as built", "fadd.ps", {}, "261", "PASS", 0),
                 ("E2 262 as built", "fadd.pi", {}, "262", "PASS", 0),
                 ("E3 a write to f9 inside the loop", "fadd.ps", {"stray_in_loop": True}, "261", "FAIL", 1),
                 ("E4 a write to f10 between the zeroing and the loop", "fadd.ps", {"stray_before": True}, "261", "FAIL", 1),
                 ("E5 a call inside the loop", "fadd.ps", {"call": True}, "261", "FAIL", 1),
                 ("E6 no zeroing block", "fadd.ps", {"nozero": True}, "261", "UNREAD", 0),
                 ("E7 the body twice", "fadd.ps", {"twice": True}, "261", "UNREAD", 0),
                 ("E8 a trailing rounding mode", "fadd.ps", {"rm": True}, "261", "PASS", 0)]
        for name, mn, kw, mode, want, want_rc in specs:
            p = os.path.join(t, "case.txt")
            open(p, "w").write(build(lines, ins, mn, **kw))
            rc, v, out = run(p)
            line = next((ln for ln in out if f"mode {mode}:" in ln), "(no line)")
            cases.append((name, v.get(mode) == want and rc == want_rc, line))
    n = sum(1 for _, ok, _ in cases if ok)
    for name, ok, line in cases:
        print(f"{'PASS' if ok else 'FAIL'} {name}: {line[:200]}")
    print(f"SELFTEST-ELF-E180 {'PASS' if n == len(cases) else 'FAIL'}: {n} of {len(cases)}")
    sys.exit(0 if n == len(cases) else 1)


if __name__ == "__main__":
    main()
