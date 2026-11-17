#!/usr/bin/env python3
"""E211 (Q204): make rgm211, THE SECOND KERNEL, from rgm136 (tools/claims-v3/e136/rgm136, E136's committed tree, never edited) by exact,
asserted edits. mm-kernel2's transform (Q202, s02_make_rgm211.py: the swapped walk and the two host arms) plus critic-kernel2's fixes 2 and 5
(Q202): a walk tag the kernel writes and the host checks, and every argument refusal made before the device opens. Desk; standard library.

    python3 -I -B tools/claims-v3/e211/make_rgm211.py <rgm136 tree> <new folder>     makes the tree (refuses an existing folder)
    python3 -I -B tools/claims-v3/e211/make_rgm211.py --check                         re-makes it from the lab's rgm136 into a temporary folder
                                                                                     and compares it with tools/claims-v3/e211/rgm211 byte for byte

WHAT CHANGES (and nothing else):
  sparsity_args.h  SP_GEMM_NB_OUTER 0x400 (with SP_GEMM_LARGE: walk the C blocks nb outer, mb inner) and SP_WALK_TAG_NM, the walk tag;
                   SpResult.aux's comment names the tag.
  kernel           run_gemm_large_nm = run_gemm_large's text with its two outer loops swapped (for nb { for mb { ... } }): the partition, the
                   cooperative loads and their groups, the order inside an op, the first/last accumulation bits, the TensorStore and the final
                   waits are run_gemm_large's; after its timed section (after o->cycles and o->count) it writes SP_WALK_TAG_NM to o->aux, which
                   entry_point copies to every participating hart's result line (it does so for every mode; run_gemm_large never writes aux, so
                   rgm136's walk leaves 0 there: Out is zero-initialised and the host zeroes the results buffer before every launch).
                   entry_point dispatches SP_GEMM_LARGE | SP_GEMM_NB_OUTER to it. run_gemm_large itself is not edited.
  host             two arms beside gemmL: gemmLn<MB>x<NB>x<KB> (SP_GEMM_NB_OUTER: the nb-outer walk, cooperative loads) and gemmLnc<MB>x<NB>x<KB>
                   (gemmL with every minion loading for itself: coop 0, run_gemm_large's own non-cooperative branch, compiled in rgm136's ELF
                   since E136). THE WALK CHECK: for every large-GEMM launch the host counts the participating harts whose aux is the tag; a
                   gemmLn launch is ok only if every reporting hart carries the tag, a gemmL or gemmLnc launch only if every one carries 0; each
                   launch's SPARSITY line prints "walk" (nm / mn / none), "walk_tagged" and "walk_ok", and the check line prints "walk" and
                   "walk_launches_bad" and is ok only if the C check holds and no launch's walk was wrong; the process exits 1 otherwise. So a
                   gemmLn process given rgm136's ELF (which ignores 0x400 and runs gemmL's walk, with a check that passes) fails.
                   THE EARLY REFUSALS: validateArm() runs in main() before Session opens the device and creates the runtime (whose creation
                   sends an abort on every queue of every card it enumerates): the type, the arm (parseArm), the per-shire rule, tenb's gen, the
                   gen, and every tile file's 2 x 1,024 bytes; testArm parses the same arm again.
  README.md        a header naming the copy and the changes.
SPDX-License-Identifier: Apache-2.0
"""
import filecmp
import os
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", "..", ".."))
SRC_REL = "tools/claims-v3/e136/rgm136"
DST_REL = "tools/claims-v3/e211/rgm211"
TAG = "0x453231314E4D574Bull"   # 'E','2','1','1','N','M','W','K'


def edit(path, old, new, count=1):
    s = open(path).read()
    n = s.count(old)
    if n != count:
        sys.exit(f"make_rgm211: anchor found {n} times (want {count}) in {path}: {old[:90]!r}")
    open(path, "w").write(s.replace(old, new))


def make(src, dst):
    if os.path.exists(dst):
        sys.exit(f"make_rgm211: {dst} exists: make a new folder")
    shutil.copytree(src, dst)

    # ---------------------------------------------------------------- kernel arguments
    h = os.path.join(dst, "sparsity_args.h")
    edit(h, "#define SP_GEMM_LARGE 0x200u\n",
         "#define SP_GEMM_LARGE 0x200u\n"
         "// E211 (rgm211): with SP_GEMM_LARGE, walk the C blocks nb outer and mb inner (run_gemm_large_nm). Everything inside a C block is\n"
         "// run_gemm_large's: the same partition, cooperative loads and groups, op order, accumulation bits and TensorStore.\n"
         "#define SP_GEMM_NB_OUTER 0x400u\n"
         "// E211: run_gemm_large_nm writes this tag to every participating hart's aux after its timed section; run_gemm_large leaves 0.\n"
         f"#define SP_WALK_TAG_NM {TAG}\n")
    edit(h, "  uint64_t aux;      // SP_DIVERGE: vector (or scalar) loop iterations executed; SP_GEMV: slices computed\n",
         "  uint64_t aux;      // SP_DIVERGE: vector (or scalar) loop iterations executed; SP_GEMV: slices computed; E211 gemmLn: SP_WALK_TAG_NM\n")

    # ---------------------------------------------------------------- kernel: run_gemm_large_nm
    k = os.path.join(dst, "kernel", "sparsity.c")
    s = open(k).read()
    start = s.index("static void run_gemm_large(")
    end = s.index("/* ---------------------------------------------------------------- SP_FMA */")
    body = s[start:end]
    old_loops = ("        for (uint64_t mb = 0; mb < MB; ++mb) {\n"
                 "            for (uint64_t nb = 0; nb < NB; ++nb) {\n")
    new_loops = ("        for (uint64_t nb = 0; nb < NB; ++nb) {\n"
                 "            for (uint64_t mb = 0; mb < MB; ++mb) {\n")
    if body.count(old_loops) != 1:
        sys.exit("make_rgm211: run_gemm_large's outer loops not found once")
    nm = body.replace("static void run_gemm_large(", "static void run_gemm_large_nm(").replace(old_loops, new_loops)
    tail = "    o->cycles = cycles() - t0;\n    o->count = op;\n}\n"
    if nm.count(tail) != 1:
        sys.exit("make_rgm211: run_gemm_large's tail not found once")
    nm = nm.replace(tail, "    o->cycles = cycles() - t0;\n    o->count = op;\n"
                          "    o->aux = SP_WALK_TAG_NM;   /* E211: the walk tag, after the timed section; the host checks it on every hart */\n}\n")
    nm = ("/* E211 (rgm211): SP_GEMM_LARGE | SP_GEMM_NB_OUTER. run_gemm_large's text with its two outer loops swapped: the minion walks the C\n"
          "   blocks nb outer, mb inner, so a column tile's B panel is met in consecutive C blocks (again at every mb) and a row tile's A panel once\n"
          "   per C block, again only at the next nb: the far operand is A, not B. Everything else is run_gemm_large's, and after the timed section\n"
          "   it writes the walk tag SP_WALK_TAG_NM to aux. */\n") + nm
    s = s[:end] + nm + s[end:]
    old_disp = ("        if (args->layout & SP_GEMM_LARGE) {   /* E136 */\n"
                "            run_gemm_large(args, shire, minion, &o);\n"
                "        } else {\n")
    new_disp = ("        if ((args->layout & SP_GEMM_LARGE) && (args->layout & SP_GEMM_NB_OUTER)) {   /* E211 */\n"
                "            run_gemm_large_nm(args, shire, minion, &o);\n"
                "        } else if (args->layout & SP_GEMM_LARGE) {   /* E136 */\n"
                "            run_gemm_large(args, shire, minion, &o);\n"
                "        } else {\n")
    if s.count(old_disp) != 1:
        sys.exit("make_rgm211: the dispatch not found once")
    s = s.replace(old_disp, new_disp)
    open(k, "w").write(s)

    # ---------------------------------------------------------------- host: the two arms (mm-kernel2's edits)
    m = os.path.join(dst, "host", "main.cpp")
    edit(m, "  bool large = false;   // E136: SP_GEMM_LARGE\n",
         "  bool large = false;   // E136: SP_GEMM_LARGE\n"
         "  bool nbOuter = false; // E211: SP_GEMM_NB_OUTER (gemmLn: the C blocks nb outer, mb inner)\n")
    old_parse = ("  else if (s.arm.rfind(\"gemmL\", 0) == 0) {   // E136: gemmL<MB>x<NB>x<KB>, nothing after it\n    s.gemm = s.coop = s.large = true;\n"
                 "    s.layout = SP_LAYOUT_BYCOL;\n    const char* p = s.arm.c_str() + 5;\n")
    new_parse = ("  else if (s.arm.rfind(\"gemmL\", 0) == 0) {   // E136: gemmL<MB>x<NB>x<KB>, nothing after it; E211: gemmLn (nb outer), gemmLnc (no cooperation)\n"
                 "    s.gemm = s.coop = s.large = true;\n"
                 "    s.layout = SP_LAYOUT_BYCOL;\n"
                 "    size_t skip = 5;\n"
                 "    if (s.arm.rfind(\"gemmLnc\", 0) == 0) { s.coop = false; skip = 7; }       // E211: every minion loads for itself, rgm136's walk\n"
                 "    else if (s.arm.rfind(\"gemmLn\", 0) == 0) { s.nbOuter = true; skip = 6; }  // E211: the nb-outer walk, cooperative loads\n"
                 "    const char* p = s.arm.c_str() + skip;\n")
    edit(m, old_parse, new_parse)
    edit(m, "      a.layout |= SP_GEMM_LARGE;\n",
         "      a.layout |= SP_GEMM_LARGE;\n"
         "      if (s.nbOuter) a.layout |= SP_GEMM_NB_OUTER;                // E211\n")
    edit(m, "//          gemmL<MB>x<NB>x<KB>  E136 (rgm136): a large GEMM,",
         "//          gemmLn<MB>x<NB>x<KB>, gemmLnc<MB>x<NB>x<KB>  E211 (rgm211): gemmL with the C blocks walked nb outer, mb inner (SP_GEMM_NB_OUTER), and\n"
         "//                      gemmL with every minion loading for itself (coop 0); the check is gemmL's; every large-GEMM launch's walk tag is checked\n"
         "//          gemmL<MB>x<NB>x<KB>  E136 (rgm136): a large GEMM,")

    # ---------------------------------------------------------------- host: THE WALK CHECK (critic-kernel2 fix 2)
    edit(m, "  a.out = a.out ? a.out : dev.put(\"unused\", nullptr, 64);\n  int bad = 0;\n",
         "  a.out = a.out ? a.out : dev.put(\"unused\", nullptr, 64);\n  int bad = 0;\n"
         "  int walkBad = 0;   // E211: launches whose walk tag was not the arm's (gemmLn: SP_WALK_TAG_NM on every hart; gemmL, gemmLnc: 0)\n"
         "  const char* walkName = !s.large ? \"none\" : s.nbOuter ? \"nm\" : \"mn\";\n")
    edit(m, ("    const Summary sm = summarize(L, harts);\n    const uint64_t ops = iters * opsPerPass;\n"
             "    const bool ok = L.ok && sm.bad == 0 && sm.tensorErrors == 0;\n"),
         ("    const Summary sm = summarize(L, harts);\n    const uint64_t ops = iters * opsPerPass;\n"
          "    uint64_t tagged = 0, zeroed = 0;   // E211: the walk tag on every reporting hart\n"
          "    for (uint64_t h : harts) {\n"
          "      const auto& r = L.res[h];\n"
          "      if (r.magic != SP_MAGIC || r.hart != h) continue;\n"
          "      tagged += r.aux == SP_WALK_TAG_NM;\n"
          "      zeroed += r.aux == 0;\n"
          "    }\n"
          "    const bool walkOk = !s.large || (sm.reported > 0 && (s.nbOuter ? tagged == sm.reported : zeroed == sm.reported));\n"
          "    walkBad += !walkOk;\n"
          "    const bool ok = L.ok && sm.bad == 0 && sm.tensorErrors == 0 && walkOk;\n"))
    edit(m, ("                \"\\\"ghz\\\":%.4f,\\\"tensor_errors\\\":%llu,\\\"result\\\":\\\"unchecked\\\",\\\"ok\\\":%s}\\n\",\n"
             "                s.arm.c_str(), s.gen.c_str(), o.type.c_str(), o.values.c_str(), int(s.tenb), harts.size(),\n"
             "                (unsigned long long)o.shireMask, (unsigned long long)ops, (unsigned long long)iters, launchNo, (unsigned long long)sm.cmax,\n"
             "                sm.cmean, cpoNow, L.wallS, L.t0Ms, L.t1Ms, L.ghz,\n"
             "                (unsigned long long)sm.tensorErrors, ok ? \"true\" : \"false\");\n"),
         ("                \"\\\"ghz\\\":%.4f,\\\"tensor_errors\\\":%llu,\\\"walk\\\":\\\"%s\\\",\\\"walk_tagged\\\":%llu,\\\"walk_ok\\\":%s,\\\"result\\\":\\\"unchecked\\\",\\\"ok\\\":%s}\\n\",\n"
          "                s.arm.c_str(), s.gen.c_str(), o.type.c_str(), o.values.c_str(), int(s.tenb), harts.size(),\n"
          "                (unsigned long long)o.shireMask, (unsigned long long)ops, (unsigned long long)iters, launchNo, (unsigned long long)sm.cmax,\n"
          "                sm.cmean, cpoNow, L.wallS, L.t0Ms, L.t1Ms, L.ghz,\n"
          "                (unsigned long long)sm.tensorErrors, walkName, (unsigned long long)tagged, walkOk ? \"true\" : \"false\", ok ? \"true\" : \"false\");\n"))
    edit(m, "  const bool ok = n.within == n.words;\n  bad += !ok;\n",
         "  const bool ok = n.within == n.words && walkBad == 0;   // E211: and no launch's walk tag was wrong\n  bad += !ok;\n")
    edit(m, ("              \"\\\"t_start_ms\\\":%lld,\\\"t_end_ms\\\":%lld,\\\"ghz\\\":0,\\\"words\\\":%llu,\\\"exact\\\":%llu,\\\"within\\\":%llu,\\\"result\\\":\\\"%s\\\",\\\"ok\\\":%s}\\n\",\n"
             "              s.arm.c_str(), s.gen.c_str(), o.type.c_str(), harts.size(), lastCpo, tc0, tc1, (unsigned long long)n.words,\n"
             "              (unsigned long long)n.exact, (unsigned long long)n.within, verdict, ok ? \"true\" : \"false\");\n"),
         ("              \"\\\"t_start_ms\\\":%lld,\\\"t_end_ms\\\":%lld,\\\"ghz\\\":0,\\\"words\\\":%llu,\\\"exact\\\":%llu,\\\"within\\\":%llu,\\\"walk\\\":\\\"%s\\\",\\\"walk_launches_bad\\\":%d,\\\"result\\\":\\\"%s\\\",\\\"ok\\\":%s}\\n\",\n"
          "              s.arm.c_str(), s.gen.c_str(), o.type.c_str(), harts.size(), lastCpo, tc0, tc1, (unsigned long long)n.words,\n"
          "              (unsigned long long)n.exact, (unsigned long long)n.within, walkName, walkBad, verdict, ok ? \"true\" : \"false\");\n"))

    # ---------------------------------------------------------------- host: THE EARLY REFUSALS (critic-kernel2 fix 5)
    edit(m, "int testArm(const Options& o, Session& dev) {\n",
         "// E211 (rgm211): every refusal testArm makes on its arguments alone, made in main() before Session opens the device and creates the\n"
         "// runtime (whose creation sends an abort on every queue of every card it enumerates). testArm parses the same arm again.\n"
         "void validateArm(const Options& o) {\n"
         "  (void)typeOf(o.type);\n"
         "  const ArmSpec s = parseArm(o.values);\n"
         "  if (s.gemm && o.perShire != 32) throw std::runtime_error(\"gemm needs --per-shire 32: every minion of a coop group must take part\");\n"
         "  if (s.tenb && s.gen != \"tiles\") throw std::runtime_error(\"tenb runs one tile: gen must be tiles\");\n"
         "  if (s.gen != \"tiles\" && s.gen != \"randn\" && s.gen != \"sparse50\" && s.gen != \"sparse25\" && s.gen != \"e37\")\n"
         "    throw std::runtime_error(\"--values: unknown gen \" + s.gen);\n"
         "  for (const auto& p : s.files) {\n"
         "    std::ifstream f(p, std::ios::binary);\n"
         "    std::vector<char> buf(2 * SP_TILE_BYTES);\n"
         "    f.read(buf.data(), std::streamsize(buf.size()));\n"
         "    if (!f) throw std::runtime_error(\"cannot read 2 x 1024 bytes of tiles from \" + p);\n"
         "  }\n"
         "}\n\n"
         "int testArm(const Options& o, Session& dev) {\n")
    edit(m, "    Session dev(o, elf);\n",
         "    if (o.test == \"fma\" && isArmValues(o.values)) validateArm(o);   // E211: before the device opens\n"
         "    Session dev(o, elf);\n")

    # ---------------------------------------------------------------- README
    r = os.path.join(dst, "README.md")
    old = open(r).read()
    open(r, "w").write(
        "# rgm211: E211's second kernel - a copy of `tools/claims-v3/e136/rgm136` with its C-block walk swapped\n\n"
        "Made by `tools/claims-v3/e211/make_rgm211.py` from rgm136 as committed (rgm136 itself is never edited; `../rgm211.diff` is the whole "
        "difference). Two arms beside rgm136's `gemmL<MB>x<NB>x<KB>`: `gemmLn<MB>x<NB>x<KB>` walks the C blocks nb outer, mb inner "
        "(`SP_GEMM_NB_OUTER`, `run_gemm_large_nm`, which writes the walk tag `SP_WALK_TAG_NM` to every hart's `aux` after its timed section), "
        "and `gemmLnc<MB>x<NB>x<KB>` is gemmL with every minion loading for itself (coop 0, rgm136's own compiled branch; E211 runs it on "
        "rgm136's ELF). The host checks the walk tag on every large-GEMM launch (a gemmLn launch needs the tag on every hart, a gemmL or gemmLnc "
        "launch 0) and refuses a malformed arm, type, per-shire count, gen or tile file before it opens the device. Nothing else differs from "
        "rgm136. E211's registration (`../E211.md`) gives the build commands and the identities.\n\n" + old)
    return dst


def check():
    src = os.path.join(REPO, SRC_REL)
    have = os.path.join(REPO, DST_REL)
    with tempfile.TemporaryDirectory() as td:
        made = make(src, os.path.join(td, "rgm211"))
        bad = []
        for root, _, files in os.walk(made):
            for f in files:
                rel = os.path.relpath(os.path.join(root, f), made)
                other = os.path.join(have, rel)
                if not os.path.isfile(other) or not filecmp.cmp(os.path.join(root, f), other, shallow=False):
                    bad.append(rel)
        for root, _, files in os.walk(have):
            for f in files:
                rel = os.path.relpath(os.path.join(root, f), have)
                if not os.path.isfile(os.path.join(made, rel)):
                    bad.append("extra: " + rel)
    if bad:
        print("make_rgm211 --check: DIFFERS:", ", ".join(sorted(bad)))
        return 1
    print("make_rgm211 --check: PASS (the committed rgm211 tree is make_rgm211.py's output from rgm136 as committed, byte for byte)")
    return 0


if __name__ == "__main__":
    if sys.argv[1:] == ["--check"]:
        sys.exit(check())
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    print("rgm211 made at", make(sys.argv[1], sys.argv[2]))
