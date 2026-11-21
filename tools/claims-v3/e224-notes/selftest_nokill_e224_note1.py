#!/usr/bin/env python3
"""E224's KIT DATED NOTE 1 (lane fix-e224, round Q237, Fri 20 Nov 2026, before any E224 datum): the desk test of nokill_e224_note1.py, with
verify-e224's mutations as its cases. It copies the audited folders (tools/claims-v3/e224, E208's runner src/, the q141k runbook folder,
fwgate) of <the lab clone> into <scratch>/lab, never touching the clone, and then:
  K0  the unmutated kit: NOKILL-E224-NOTE1 0 lines toward a device process, 12 to the desk's own call tree (kill_tree in the four rb_run.py
      versions), and every line kit-e224's own reader (desk/nokill_e224.py) lists as stating the rule is a statement here too (none turned
      into a sending line); lines this reader lists as statements and kit-e224's does not are printed (REPORTED);
  then one mutation at a time (each restored from the copy's original bytes before the next), the new reader and kit-e224's reader both run:
  M4   a plain `timeout -k` host line with a trailing comment            (verify-e224's M4: kit-e224's reader MISSED it)   new: SENDS
  M4b  the same line with no comment                                     (caught by both)                                 new: SENDS
  M4c  `timeout -k ... --rules x`, the word in an argument               (verify-e224's M4c: MISSED)                      new: SENDS
  M4d  `kill -9 "$HOSTPID"   # stop the host`                            (verify-e224's M4d: MISSED)                      new: SENDS
  X1   run_e224a.py's argv list given a -k: ["timeout", "-k", "1", ...]  (an argv list: neither old form sees it)          new: SENDS
  X2   a .py command string with a trailing '# never' comment            (the old reader classes the line by its comment) new: SENDS
  X3   ssh "$BOX" "timeout -k 1 10 $HOST --test fma" in shell            (a quoted command)                               new: SENDS
  X4   the same with '--rules x' after the form                          (a statement word AFTER the form)                new: SENDS
  U1   a shell comment naming the form                                                                                    new: states
  U2   echo "never send ..." naming the form                             (a statement word before it)                     new: states
  U3   a .py docstring naming the forms                                                                                   new: states
  U4   a .py message "... (no ... -9)"                                                                                     new: states
  U5   a .py needle tuple ("kill -9", "timeout -k")                                                                        new: states
This file's code assembles the kill forms of its cases from pieces; this docstring names them as text only (neither reader's roots hold
this folder; the note's reader would read these lines as a docstring). Prints one line a case, then "SELFTEST-NOKILL-E224-NOTE1 <k> of <n>
PASS" (exit 0) or "... FAIL" (exit 1).
    /usr/bin/python3 -I -B tools/claims-v3/e224-notes/selftest_nokill_e224_note1.py <the lab clone> <scratch dir, new or empty>
Standard library only. SPDX-License-Identifier: Apache-2.0
"""
import json
import os
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
NEW = os.path.join(HERE, "nokill_e224_note1.py")
ROOTS = ("tools/claims-v3/e224", "tools/claims-v3/e208/proposal/src", "tools/claims-v3/q141k-runbook", "tools/claims-v3/fwgate")
K = "kil" + "l"
T = "time" + "out"
SESSION_B = "tools/claims-v3/e224/box/session_e224b.sh"
RUN_A = "tools/claims-v3/e224/run_e224a.py"


def run_new(lab, js):
    r = subprocess.run(["/usr/bin/python3", "-I", "-B", NEW, lab, "--json", js], capture_output=True, text=True)
    d = json.load(open(js))
    return r.returncode, r.stdout.strip().splitlines()[-1] if r.stdout.strip() else "", d


def run_old(lab):
    r = subprocess.run(["/usr/bin/python3", "-I", "-B", os.path.join(lab, "tools/claims-v3/e224/desk/nokill_e224.py"), lab],
                       capture_output=True, text=True)
    return r.returncode, r.stdout.splitlines()


def cls_new(d, key):
    for c, name in (("send", "SENDS"), ("desk", "DESK"), ("state", "states")):
        for x in d[c]:
            if x["line"].startswith(key):
                return name
    return "not listed"


def cls_old(lines, key):
    for ln in lines:
        if ln.startswith("states the rule: ") and ln[len("states the rule: "):].startswith(key):
            return "states"
        if ln.startswith("SENDS (could reach a device process): ") and ln.split(": ", 1)[1].startswith(key):
            return "SENDS"
        if ln.startswith("SENDS TO THE DESK'S OWN CALL TREE ONLY: ") and ln.split(": ", 1)[1].startswith(key):
            return "DESK"
    return "not listed"


def main(argv):
    if len(argv) != 2:
        print(__doc__)
        return 2
    src, scratch = argv
    if os.path.exists(scratch) and os.listdir(scratch):
        print(f"the scratch {scratch} is not empty: refused")
        return 2
    lab = os.path.join(scratch, "lab")
    for r in ROOTS:
        shutil.copytree(os.path.join(src, r), os.path.join(lab, r), ignore=shutil.ignore_patterns("__pycache__"))
    js = os.path.join(scratch, "new.json")
    res = []
    # K0: the unmutated kit
    rc, last, d = run_new(lab, js)
    orc, old = run_old(lab)
    old_state = [ln[len("states the rule: "):] for ln in old if ln.startswith("states the rule: ")]
    new_state = {x["line"] for x in d["state"]}
    new_send = {x["line"] for x in d["send"]}
    lost = [x for x in old_state if x not in new_state]
    extra = sorted(new_state - set(old_state))
    ok = rc == 0 and not d["send"] and len(d["desk"]) == 12 and not lost and orc == 0
    res.append(ok)
    print(f"K0 the unmutated kit: new rc {rc}, {len(d['send'])} sending, {len(d['desk'])} desk-only, {len(d['state'])} statements; kit-e224's "
          f"reader rc {orc}, {len(old_state)} statements, every one a statement here: {not lost}"
          + (f" (lost: {lost[:3]})" if lost else "") + f"; turned into sending lines: {sorted(set(old_state) & new_send)[:3] or 'none'}: "
          + ("PASS" if ok else "FAIL"))
    for x in extra:
        print(f"   REPORTED (a statement here, not listed by kit-e224's reader): {x}")
    # the cases
    sb = open(os.path.join(lab, SESSION_B)).read().split("\n")
    nb = next(i for i, ln in enumerate(sb, 1) if ln.startswith("/usr/bin/python3 -B src/run_e224b.py"))
    ra = open(os.path.join(lab, RUN_A)).read().split("\n")
    na = next(i for i, ln in enumerate(ra, 1) if ln.strip() == 'return ["' + T + '", str(to)] + argv')
    nend = len(ra) + 1
    cases = [
        ("M4", "a plain -k host line with a trailing comment (verify-e224's M4)", SESSION_B, "insert", nb,
         [T + " -k 1 10 build/rgm/host/sparsity_host --test fma   # verify-e224 M4 mutation"], nb, "SENDS"),
        ("M4b", "the same line, no comment", SESSION_B, "insert", nb, [T + " -k 1 10 build/rgm/host/sparsity_host --test fma"], nb, "SENDS"),
        ("M4c", "-k with the word 'rules' in an argument (verify-e224's M4c)", SESSION_B, "insert", nb,
         [T + " -k 1 10 build/rgm/host/sparsity_host --rules x"], nb, "SENDS"),
        ("M4d", "-9 to a pid with a plain trailing comment (verify-e224's M4d)", SESSION_B, "insert", nb,
         [K + ' -9 "$HOSTPID"   # stop the host'], nb, "SENDS"),
        ("X1", "run_e224a.py's host argv list given a -k token", RUN_A, "replace", na,
         ['        return ["' + T + '", "-k", "1", str(to)] + argv'], na, "SENDS"),
        ("X2", "a .py command string with a trailing '# never' comment", RUN_A, "replace", na,
         ['        return ["bash", "-c", "' + T + ' -k 1 10 " + " ".join(argv)]  # never'], na, "SENDS"),
        ("X3", "a quoted remote command in shell", SESSION_B, "insert", nb, ['ssh "$BOX" "' + T + ' -k 1 10 $HOST --test fma"'], nb, "SENDS"),
        ("X4", "the same with a statement word after the form", SESSION_B, "insert", nb, ['ssh "$BOX" "' + T + ' -k 1 10 $HOST --rules x"'],
         nb, "SENDS"),
        ("U1", "a shell comment naming the form", SESSION_B, "insert", nb, ["# never: " + T + " -k 1 10 <host>"], nb, "states"),
        ("U2", "echo with a statement word before the form", SESSION_B, "insert", nb, ['echo "never send ' + T + ' -k to a host"'], nb,
         "states"),
        ("U3", "a .py docstring naming the forms", RUN_A, "insert", nend,
         ["", "", "def _note1_case():", '    """a docstring: ' + K + " -9 and " + T + ' -k are never used"""', "    return None"], nend + 3,
         "states"),
        ("U4", "a .py message with 'no' before the form", RUN_A, "insert", nend,
         ["", "", "def _note1_case(self):", '    self.say("left running, recorded (no ' + K + ' -9)")', "    return None"], nend + 3,
         "states"),
        ("U5", "a .py needle tuple", RUN_A, "insert", nend,
         ["", "", "def _note1_case(t):", '    return [w for w in ("' + K + ' -9", "' + T + ' -k") if w in t]'], nend + 3, "states"),
    ]
    for cid, what, rel, how, at, new_lines, check_line, want in cases:
        p = os.path.join(lab, rel)
        orig = open(p, "rb").read()
        L = orig.decode().split("\n")
        if how == "insert":
            L[at - 1:at - 1] = new_lines
        else:
            L[at - 1:at] = new_lines
        open(p, "w").write("\n".join(L))
        key = f"{rel}:{check_line}: "
        rc, last, d = run_new(lab, js)
        orc, old = run_old(lab)
        got, oldgot = cls_new(d, key), cls_old(old, key)
        others = len(d["send"]) - (1 if got == "SENDS" else 0)
        ok = got == want and others == 0
        res.append(ok)
        print(f"{cid} {what}: new {got} (want {want}; other sending lines {others}), kit-e224's reader {oldgot}: {'PASS' if ok else 'FAIL'}")
        open(p, "wb").write(orig)
    rc, last, d = run_new(lab, js)
    ok = rc == 0 and not d["send"] and len(d["desk"]) == 12
    res.append(ok)
    print(f"K1 restored: new rc {rc}, {len(d['send'])} sending, {len(d['desk'])} desk-only: {'PASS' if ok else 'FAIL'}")
    k = sum(res)
    print(f"SELFTEST-NOKILL-E224-NOTE1 {k} of {len(res)} {'PASS' if k == len(res) else 'FAIL'}")
    return 0 if k == len(res) else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
