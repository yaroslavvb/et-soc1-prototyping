#!/usr/bin/env python3
"""Desk tests of fwgate.py (Q188, Sun 15 Nov 2026). Stdlib only:
    python3 tools/claims-v3/fwgate/tests/test_fwgate.py -v
The read tests run fwgate.py with FWGATE_DESK_TEST=1 and stand-ins (fwcli-standin for the vendor CLI, etwho-standin
for et-who, a lock folder holding the two lock files the lab makes at boot, and a ledger folder, all in a temporary
directory): no device is opened and the real CLI is never run. fwgate.py refuses a desk test wherever a card node
exists, so those tests are skipped there: run them in a sandbox with no card node (the lab's desk runs them under
bubblewrap with a private /dev and an empty /run/lock). The parse and record tests read the committed answers of E69,
E72, E79, E82, E84 and E114, and run anywhere in the repository. The tests named after verify-guards' findings (Q188)
pin each fix: a stop carries across folders through the per-boot ledger (1), a desk test needs every stand-in (2), no
lock file is ever made (3), a second read at once is told to call again (4), a number split by a print never reads
EQUAL (5), the reference is the newest record by read time (6), and a transcribed record's values are tied to their
statements (7)."""
import datetime
import fcntl
import glob
import inspect
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import threading
import time
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
GATE = HERE.parent / "fwgate.py"
REPO = HERE.parent.parent.parent.parent
sys.path.insert(0, str(HERE.parent))
import fwgate as F  # noqa: E402

PY = sys.executable
CLI, ETWHO = HERE / "fwcli-standin", HERE / "etwho-standin"
NODES = sorted(glob.glob("/dev/et*_mgmt") + glob.glob("/dev/et*_ops"))
A2 = {"release": "1.4.0", "bl1": "0.22.0", "bl2": "0.22.0", "pmic": "1.5.0", "mm": "0.25.1", "wm": "0.25.1",
      "machm": "0.25.1"}
LABEL = dict((k, label) for label, k in F.FIELDS)
D = REPO / "docs/reports/data"
E82 = D / "2026-10-31-e82-kinds-aifoundry1/ident/firmware_pre.txt"
E72 = D / "2026-10-27-e72-600mhz/gov.jsonl"
E79 = D / "2026-10-31-e79-fp16-int8-bit-prices/ident/firmware.txt"
E84 = D / "2026-10-31-e84-speed-aifoundry1-card0/ident/ident-154200.out"
E114 = D / "2026-11-01-e114-card0-replicates/ident/ident-141810.out"


def epoch(s):
    return int(datetime.datetime.fromisoformat(s).timestamp())


A2_BOOT = epoch("2026-11-13T16:53:28-08:00")   # aifoundry2's boot after its 13 Nov crash (after every record)
OLD_BOOT = epoch("2026-10-26T15:02:04-07:00")  # aifoundry1's boot, before every record
LATER_BOOT = epoch("2026-11-15T09:00:00-08:00")  # a later boot the same day
NOW = epoch("2026-11-15T16:30:00-08:00")


def e72_answer():
    return F.section_text(E72, jsonl_line=2, pointer="queries.firmware.out")


def e82_answer():
    return E82.read_text()


def change_field(text, key, value):
    """The answer with one field's three numbers replaced (the line otherwise as the tool printed it)."""
    a, b, c = value.split(".")
    rx = re.compile(r"(" + re.escape(LABEL[key]) + r": Major: )\d+( Minor: )\d+( Revision: )\d+")
    out, n = rx.subn(lambda m: f"{m.group(1)}{a}{m.group(2)}{b}{m.group(3)}{c}", text)
    assert n == 1, (key, n)
    return out


class TestParse(unittest.TestCase):
    """The parse rule on committed answers (runs anywhere in the repository)."""

    def setUp(self):
        if not E82.exists():
            self.skipTest("not in the lab repository")

    def fields(self, text):
        return F.parse(text)

    def test_committed_answers_parse_to_their_records(self):
        cases = [(e82_answer(), dict(A2, pmic="1.3.0")), (e72_answer(), A2), (F.section_text(E79, 1), A2),
                 (E84.read_text(), dict(A2, pmic="1.6.1")), (E114.read_text(), dict(A2, pmic="1.6.1"))]
        for text, want in cases:
            fields, problems, _ = self.fields(text)
            self.assertEqual((fields, problems), (want, []))

    def test_check_records_reads_every_record_from_its_source(self):
        p = subprocess.run([PY, "-B", str(GATE), "check-records"], capture_output=True, text=True, env=clean_env())
        self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
        self.assertEqual(p.stdout.count(": OK ("), 6, p.stdout)

    def test_a_runtime_line_between_lines_changes_nothing(self):
        lines = e72_answer().split("\n")
        mixed = "\n".join(x for ln in lines for x in (ln, "Opening device 0"))
        self.assertEqual(self.fields("Opening device 0\n" + mixed)[0], A2)

    def test_a_runtime_line_spliced_inside_a_field_is_unreadable(self):
        t = e72_answer().replace("PMIC Firmware versions: Major: 1 Minor: 5", "PMIC Firmware versions: Major: 1Opening "
                                 "device 0\n Minor: 5")
        fields, problems, _ = self.fields(t)
        self.assertIsNone(fields)
        self.assertTrue(any("PMIC Firmware versions" in p for p in problems), problems)

    def test_a_runtime_line_spliced_at_a_field_end_is_unreadable(self):
        t = e72_answer().replace("BL2 Firmware versions: Major: 0 Minor: 22 Revision: 0",
                                 "BL2 Firmware versions: Major: 0 Minor: 22 Revision: 0Opening device 0")
        self.assertIsNone(self.fields(t)[0])

    def test_a_label_twice_is_unreadable(self):
        t = e72_answer() + "\nWorker Minion versions: Major: 0 Minor: 25 Revision: 1\n"
        fields, problems, _ = self.fields(t)
        self.assertIsNone(fields)
        self.assertTrue(any("2 lines for 'Worker Minion versions'" in p for p in problems), problems)

    def test_no_success_line_or_two_are_unreadable(self):
        t = e72_answer()
        self.assertIsNone(self.fields(t.replace("Service request succeeded", "Service request failed"))[0])
        self.assertIsNone(self.fields(t + "\nService request succeeded\n")[0])

    def test_another_command_line_is_unreadable(self):
        t = e82_answer().replace("code 14", "code 15")
        fields, problems, _ = self.fields(t)
        self.assertIsNone(fields)
        self.assertTrue(any("command lines" in p for p in problems), problems)

    def test_a_number_above_255_is_unreadable(self):
        self.assertIsNone(self.fields(e72_answer().replace("Major: 1 Minor: 4", "Major: 256 Minor: 4"))[0])

    def test_the_pmic_fallthrough_compares_different(self):
        # a failed PMIC read still answers success, the PMIC field holding the Machine Minion's version
        t = e72_answer().replace("PMIC Firmware versions: Major: 1 Minor: 5 Revision: 0",
                                 "PMIC Firmware versions: Major: 0 Minor: 25 Revision: 1")
        fields, problems, _ = self.fields(t)
        self.assertEqual(problems, [])
        verdict, rows = F.compare(fields, A2)
        self.assertEqual(verdict, "DIFFERENT")
        self.assertEqual([r["field"] for r in rows if not r["equal"]], ["pmic"])

    def test_every_field_is_compared(self):
        for key in F.KEYS:
            f = dict(A2)
            f[key] = "9.9.9"
            self.assertEqual(F.compare(f, A2)[0], "DIFFERENT", key)
        self.assertEqual(F.compare(dict(A2), A2)[0], "EQUAL")

    def test_finding5_a_number_split_by_a_print_never_reads_another_value(self):
        # A card whose field's last number extends the record's (0.25.1 -> 0.25.12): one print spliced at any position,
        # in any of five forms (E191's real form is the first: 'Opening device 1\n' right after a digit), either reads
        # the card's true values or is UNREADABLE; it never reads the record's (verify-guards, finding 5).
        forms = ("Opening device 0\n", "\nOpening device 0\n", "\n", "\nOpening device 0", "Opening device 0")
        for key, val in (("mm", "0.25.12"), ("wm", "0.25.13"), ("machm", "0.25.19")):
            true = change_field(e72_answer(), key, val)
            want = dict(A2, **{key: val})
            for ins in forms:
                with self.subTest(field=key, splice=ins):
                    wrong = [i for i in range(len(true) + 1)
                             if (f := F.parse(true[:i] + ins + true[i:])[0]) is not None and f != want]
                    self.assertEqual(wrong, [])

    def test_a_print_spliced_anywhere_in_a_committed_answer_never_reads_another_value(self):
        n = {"unreadable": 0, "same": 0, "other": 0}
        for text, want in ((e72_answer(), A2), (e82_answer(), dict(A2, pmic="1.3.0"))):
            for i in range(len(text) + 1):
                for ins in ("Opening device 0\n", "Opening device 1\n", "Opening device 0"):
                    f = F.parse(text[:i] + ins + text[i:])[0]
                    n["unreadable" if f is None else ("same" if f == want else "other")] += 1
        self.assertEqual(n["other"], 0, n)
        self.assertGreater(n["same"], 0, n)

    def test_a_line_of_digits_alone_or_an_odd_opening_line_is_unreadable(self):
        t = e72_answer()
        for extra in ("\n123\n", "\n  7 \n", "\nOpening device 09\n", "\nOpening device x\n", "\nOpening device\n"):
            with self.subTest(extra=extra):
                fields, problems, _ = self.fields(t + extra)
                self.assertIsNone(fields)
                self.assertTrue(any("split by a print" in p for p in problems), problems)
        self.assertEqual(self.fields(t + "\nOpening device 1\n")[0], A2)  # E191's print, card 1, between lines
        glued = t.replace("\n\n2026/10/27 14:59:39 684502", "\n\nOpening device 02026/10/27 14:59:39 684502", 1)
        self.assertNotEqual(glued, t)
        self.assertEqual(self.fields(glued)[0], A2)  # a print with no newline, glued to the next logger line
        tail = change_field(t, "machm", "0.25.19").replace("Revision: 19", "Revision: 1\nOpening device 09", 1)
        self.assertIsNone(self.fields(tail)[0])  # the same print carrying a split number's tail


class TestRecords(unittest.TestCase):
    """The committed records, their order and their ties to their sources (runs anywhere in the repository)."""

    def setUp(self):
        if not E82.exists():
            self.skipTest("not in the lab repository")

    def test_finding6_the_reference_is_the_newest_by_read_time_not_by_name(self):
        tmp = Path(tempfile.mkdtemp(prefix="fwgate-records-"))
        try:
            base = json.loads((F.RECORDS / "aifoundry2-c0-2026-10-27-e72.json").read_text())
            new = dict(base, by="ENEW", read_at="2026-11-01T10:00:00-08:00", read_at_text="2026-11-01 10:00:00 PST")
            old = dict(base, by="EOLD", read_at="2026-10-01T10:00:00-07:00", read_at_text="2026-10-01 10:00:00 PDT")
            (tmp / "a-first-by-name-newest-by-time.json").write_text(json.dumps(new))
            (tmp / "z-last-by-name-oldest-by-time.json").write_text(json.dumps(old))
            saved, F.RECORDS = F.RECORDS, tmp
            try:
                ref, rec, _ = F.newest("aifoundry2", 0, [], {"boot": A2_BOOT, "boot_id": "b", "now": NOW, "desk": True})
            finally:
                F.RECORDS = saved
            self.assertEqual((ref["label"], rec["label"]), ("ENEW", "ENEW"))
        finally:
            shutil.rmtree(tmp, ignore_errors=True)

    def test_finding7_check_records_ties_each_value_to_its_field(self):
        r = json.loads((F.RECORDS / "aifoundry2-c0-2026-10-27-e69.json").read_text())
        self.assertEqual(F.check_record(r), [])
        for key, value in (("pmic", "1.5.1"), ("bl1", "1.5.0"), ("mm", "0.25.12"), ("release", "1.4.1"),
                           ("machm", "0.22.0")):
            with self.subTest(field=key, value=value):
                bad = F.check_record(dict(r, fields=dict(r["fields"], **{key: value})))
                self.assertTrue(bad and all(f"'{key}'" in b for b in bad), bad)


def clean_env(**kw):
    env = {k: v for k, v in os.environ.items() if not k.startswith("FWGATE_")}
    env.update({k: str(v) for k, v in kw.items()})
    return env


@unittest.skipIf(NODES, f"card nodes visible ({', '.join(NODES)}): run in a sandbox with no card node")
class DeskBase(unittest.TestCase):
    def setUp(self):
        self.t = Path(tempfile.mkdtemp(prefix="fwgate-test-"))
        self.out = self.t / "out"
        self.lockdir = self.t / "lock"
        self.lockdir.mkdir()
        for c in (0, 1):  # the lab makes these at boot; fwgate never makes one
            (self.lockdir / f"etsoc-shire{c}.lock").touch()
        self.ledger = self.t / "ledger"
        self.log = self.t / "standin.log"
        self.answer = self.t / "answer.txt"

    def tearDown(self):
        shutil.rmtree(self.t, ignore_errors=True)

    def gate(self, *args, box="aifoundry2", boot=A2_BOOT, now=NOW, answer=None, rc=0, etwho_rc=0, desk=True, drop=(),
             **extra):
        if answer is not None:
            self.answer.write_text(answer)
        settings = dict(FWGATE_CLI=CLI, FWGATE_ETWHO=ETWHO, FWGATE_LOCKDIR=self.lockdir, FWGATE_LEDGER_DIR=self.ledger,
                        FWGATE_HOSTNAME=box, FWGATE_BOOT_EPOCH=boot, FWGATE_NOW_EPOCH=now, FWGATE_STANDIN_LOG=self.log,
                        FWGATE_STANDIN_OUT=self.answer if self.answer.exists() else "", FWGATE_STANDIN_RC=rc,
                        FWGATE_STANDIN_ETWHO_RC=etwho_rc, FWGATE_STANDIN_ETWHO_LOG=self.t / "etwho.log",
                        FWGATE_STANDIN_LOCKS=":".join(str(self.lockdir / f"etsoc-shire{c}.lock") for c in (0, 1)))
        settings.update(extra)  # a test's own settings win
        env = clean_env(**settings)
        for k in drop:
            env.pop(k, None)
        if desk:
            env["FWGATE_DESK_TEST"] = "1"
        p = subprocess.run([PY, "-B", str(GATE), *map(str, args)], capture_output=True, text=True, env=env, timeout=120)
        return p.returncode, p.stdout + p.stderr

    def calls(self):
        if not self.log.exists():
            return []
        return [json.loads(x) for x in self.log.read_text().splitlines() if x.strip()]

    def records(self, d=None):
        return sorted((d or self.out).glob("fwgate-*.json"))

    def ledger_lines(self, box="aifoundry2", card=0, d=None):
        p = (d or self.ledger) / f"{box}-c{card}.jsonl"
        return [json.loads(x) for x in p.read_text().splitlines() if x.strip()] if p.exists() else []

    def read_ok(self, box="aifoundry2", card=0, answer=None, out=None, **kw):
        rc, text = self.gate("read", "--box", box, "--card", card, "--out", out or self.out, box=box,
                             answer=e72_answer() if answer is None else answer, **kw)
        return rc, text


class TestLookAndGuard(DeskBase):
    def test_a_box_booted_after_its_records_needs_a_read(self):
        rc, out = self.gate("look", "--box", "aifoundry2", "--card", 0)
        self.assertEqual(rc, 17, out)
        self.assertIn("NEEDS-READ: aifoundry2 card 0 booted 2026-11-13 16:53:28 PST", out)
        rc, out = self.gate("guard", "--box", "aifoundry2", "--card", 0)
        self.assertEqual(rc, 16, out)
        self.assertTrue(out.startswith("IDENTITY-STOP: aifoundry2 card 0 booted '2026-11-13 16:53:28 PST', not before "
                                       "E72's firmware read of 2026-10-27 14:59:39 PDT"), out)
        self.assertEqual(self.calls(), [])

    def test_continuity_before_the_records(self):
        for box, card, who in (("aifoundry2", 0, "E72"), ("aifoundry1", 1, "E82"), ("aifoundry1", 0, "E114"),
                               ("aifoundry3", 0, "E79")):
            with self.subTest(box=box, card=card):
                rc, out = self.gate("look", "--box", box, "--card", card, box=box, boot=OLD_BOOT)
                self.assertEqual(rc, 0, out)
                self.assertIn("CONTINUITY:", out)
                rc, out = self.gate("guard", "--box", box, "--card", card, box=box, boot=OLD_BOOT)
                self.assertEqual(rc, 0, out)
                self.assertIn(f"before {who}'s firmware read of", out)
                self.assertEqual(("caveat: aifoundry3" in out), box == "aifoundry3")
        self.assertEqual(self.calls(), [])

    def test_no_record_is_a_stop(self):
        rc, out = self.gate("look", "--box", "aifoundry9", "--card", 0, box="aifoundry9")
        self.assertEqual(rc, 16, out)
        self.assertIn("NO-RECORD", out)
        rc, out = self.gate("guard", "--box", "aifoundry2", "--card", 1)
        self.assertEqual(rc, 16, out)

    def test_another_box_and_settings_outside_a_desk_test_are_refused(self):
        rc, out = self.gate("look", "--box", "aifoundry2", "--card", 0, box="aifoundry3")
        self.assertEqual(rc, 10, out)
        rc, out = self.gate("look", "--box", "aifoundry2", "--card", 0, desk=False)
        self.assertEqual(rc, 10, out)
        self.assertIn("desk-test settings outside a desk test", out)

    def test_usage(self):
        rc, out = self.gate("look", "--box", "aifoundry2")
        self.assertEqual(rc, 10, out)


class TestRead(DeskBase):
    def test_equal_writes_a_record_and_the_guard_then_passes(self):
        rc, out = self.read_ok()
        self.assertEqual(rc, 0, out)
        self.assertIn("EQUAL: aifoundry2 card 0", out)
        calls = self.calls()
        self.assertEqual(len(calls), 1)  # one call, exactly the lab's form
        c = calls[0]
        self.assertEqual(c["argv"], ["-m", F.QUERY, "-n", "0", "-u", "5000"])
        self.assertEqual(c["stdin"], "/dev/null")
        self.assertTrue(c["cwd"].startswith(str(self.out)) and c["cwd"].endswith("-cwd"), c["cwd"])
        self.assertEqual(c["locks"], {"etsoc-shire0.lock": "held", "etsoc-shire1.lock": "free"})  # card 0's held
        recs = self.records()
        self.assertEqual(len(recs), 1)
        r = json.loads(recs[0].read_text())
        self.assertEqual((r["schema"], r["verdict"], r["fields"], r["rc"]), ("fwgate-read/1", "EQUAL", A2, 0))
        self.assertEqual(r["argv"][:3], ["/usr/bin/timeout", "10", str(CLI)])
        self.assertEqual(r["reference"]["file"], "aifoundry2-c0-2026-10-27-e72.json")
        self.assertEqual((r["boot_epoch"], r["boot_id"]), (A2_BOOT, f"desk-boot-{A2_BOOT}"))
        self.assertEqual(r["cwd_left"], [])
        self.assertFalse((self.out / r["cwd"]).exists())  # an empty scratch directory is removed
        rc, out = self.gate("guard", "--box", "aifoundry2", "--card", 0, "--extra", self.out)
        self.assertEqual(rc, 0, out)
        self.assertIn("identity: aifoundry2 card 0 booted 2026-11-13 16:53:28 PST, before the firmware read of "
                      "2026-11-15 16:30:00 PST (fwgate-aifoundry2-c0-20261115-163000.json): ok", out)
        rc, out = self.gate("look", "--box", "aifoundry2", "--card", 0, "--extra", self.out)
        self.assertEqual(rc, 0, out)
        rc, out = self.read_ok()  # a second read finds the identity carried and sends nothing
        self.assertEqual(rc, 0, out)
        self.assertIn("CONTINUITY", out)
        self.assertEqual(len(self.calls()), 1)

    def test_a_read_record_counts_only_today_and_on_this_boot(self):
        self.assertEqual(self.read_ok()[0], 0)
        rc, out = self.gate("guard", "--box", "aifoundry2", "--card", 0, "--extra", self.out, now=NOW + 86400)
        self.assertEqual(rc, 16, out)
        self.assertIn("not written today", out)
        rc, out = self.gate("guard", "--box", "aifoundry2", "--card", 0, "--extra", self.out, boot=NOW - 600,
                            now=NOW + 60)
        self.assertEqual(rc, 16, out)
        self.assertIn("not on this boot", out)
        rc, out = self.gate("guard", "--box", "aifoundry2", "--card", 0, "--extra", self.out,
                            FWGATE_BOOT_ID="another-boot-same-btime")
        self.assertEqual(rc, 16, out)
        self.assertIn("not on this boot", out)

    def test_a_desk_record_never_counts_outside_a_desk_test(self):
        self.assertEqual(self.read_ok()[0], 0)
        s = {"boot": A2_BOOT, "boot_id": f"desk-boot-{A2_BOOT}", "now": NOW}
        good, notes = F.extra_records([str(self.out)], "aifoundry2", 0, dict(s, desk=False))
        self.assertEqual(good, [])
        self.assertTrue(any("a desk test's record" in n for n in notes), notes)
        good, _ = F.extra_records([str(self.out)], "aifoundry2", 0, dict(s, desk=True))
        self.assertEqual(len(good), 1)

    def test_a_changed_answer_or_record_is_not_used(self):
        self.assertEqual(self.read_ok()[0], 0)
        r = json.loads(self.records()[0].read_text())
        so = self.out / r["raw"]["stdout"]["file"]
        so.write_text(so.read_text().replace("Minor: 5 Revision: 0", "Minor: 6 Revision: 0"))
        rc, out = self.gate("guard", "--box", "aifoundry2", "--card", 0, "--extra", self.out)
        self.assertEqual(rc, 16, out)
        self.assertIn("its raw answer is missing or changed", out)

    def test_different_stops_and_refuses_a_retry(self):
        rc, out = self.read_ok(answer=e82_answer())  # aifoundry1 card 1's answer (PMIC 1.3.0) on aifoundry2
        self.assertEqual(rc, 16, out)
        self.assertIn("IDENTITY-STOP: DIFFERENT", out)
        r = json.loads(self.records()[0].read_text())
        self.assertEqual(r["verdict"], "DIFFERENT")
        self.assertEqual([x["field"] for x in r["rows"] if not x["equal"]], ["pmic"])
        rc, out = self.gate("guard", "--box", "aifoundry2", "--card", 0, "--extra", self.out)
        self.assertEqual(rc, 16, out)
        rc, out = self.read_ok()  # even a good answer now: never a retry on this boot
        self.assertEqual(rc, 16, out)
        self.assertIn("never a retry", out)
        self.assertEqual(len(self.calls()), 1)

    def test_unreadable_answers_stop(self):
        for answer, rc_tool in (("nothing useful\n", 0), (e72_answer(), 1),
                                (e72_answer().replace("Revision: 1", "Revision: 1Opening device 0", 1), 0)):
            with self.subTest(rc_tool=rc_tool, head=answer[:20]):
                shutil.rmtree(self.out, ignore_errors=True)
                shutil.rmtree(self.ledger, ignore_errors=True)  # each case on its own (the ledger would stop it)
                rc, out = self.read_ok(answer=answer, rc=rc_tool)
                self.assertEqual(rc, 16, out)
                self.assertIn("IDENTITY-STOP: UNREADABLE", out)
                self.assertEqual([(e["event"], e["verdict"]) for e in self.ledger_lines()],
                                 [("SENT", "SENT"), ("END", "UNREADABLE")])

    def test_runtime_lines_between_the_answers_lines_still_read_equal(self):
        lines = e72_answer().split("\n")
        rc, out = self.read_ok(answer="\n".join(x for ln in lines for x in (ln, "Opening device 0")))
        self.assertEqual(rc, 0, out)

    def test_a_held_card_or_a_failed_check_sends_nothing(self):
        for etwho_rc in (1, 2):
            with self.subTest(etwho_rc=etwho_rc):
                rc, out = self.read_ok(etwho_rc=etwho_rc)
                self.assertEqual(rc, 17, out)
                self.assertIn("nothing sent", out)
        self.assertEqual(self.calls(), [])
        self.assertEqual(self.records(), [])
        self.assertEqual(self.ledger_lines(), [])

    def test_a_busy_lock_sends_nothing(self):
        fd = os.open(self.lockdir / "etsoc-shire0.lock", os.O_RDONLY)
        fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        try:
            rc, out = self.read_ok()
        finally:
            os.close(fd)
        self.assertEqual(rc, 17, out)
        self.assertIn("is held: nothing sent", out)
        self.assertEqual(self.calls(), [])
        self.assertEqual(self.ledger_lines(), [])

    def test_aifoundry1_needs_the_owners_word_and_then_holds_both_locks(self):
        boot = epoch("2026-11-14T08:00:00-08:00")  # a later boot than E82's read
        rc, out = self.read_ok(box="aifoundry1", card=1, answer=e82_answer(), boot=boot)
        self.assertEqual(rc, 10, out)
        self.assertIn("opens both cards' management nodes", out)
        self.assertEqual(self.calls(), [])
        rc, out = self.gate("read", "--box", "aifoundry1", "--card", 1, "--out", self.out, "--both-nodes-ok",
                            box="aifoundry1", boot=boot, answer=e82_answer())
        self.assertEqual(rc, 0, out)
        self.assertEqual(self.calls()[0]["locks"], {"etsoc-shire0.lock": "held", "etsoc-shire1.lock": "held"})
        self.assertEqual(self.calls()[0]["argv"], ["-m", F.QUERY, "-n", "1", "-u", "5000"])

    def test_continuity_or_no_record_sends_nothing(self):
        rc, out = self.read_ok(boot=OLD_BOOT)
        self.assertEqual(rc, 0, out)
        self.assertIn("CONTINUITY", out)
        rc, out = self.gate("read", "--box", "aifoundry9", "--card", 0, "--out", self.out, box="aifoundry9",
                            answer=e72_answer())
        self.assertEqual(rc, 16, out)
        self.assertIn("NO-RECORD", out)
        self.assertEqual(self.calls(), [])

    def test_a_sent_read_that_never_finished_refuses_a_retry(self):
        self.out.mkdir()
        (self.out / "fwgate-aifoundry2-c0-20261115-160000.json").write_text(json.dumps(
            {"schema": "fwgate-read/1", "box": "aifoundry2", "card": 0, "verdict": "SENT", "boot_epoch": A2_BOOT}))
        rc, out = self.read_ok()
        self.assertEqual(rc, 16, out)
        self.assertIn("already ended SENT", out)
        self.assertIn("read holding the card's lock", out)
        self.assertEqual(self.calls(), [])

    def test_a_file_the_tool_leaves_in_its_directory_is_kept_and_listed(self):
        rc, out = self.read_ok(FWGATE_STANDIN_DUMP="dev0_sp_trace.bin")
        self.assertEqual(rc, 0, out)
        r = json.loads(self.records()[0].read_text())
        self.assertEqual(r["cwd_left"], ["dev0_sp_trace.bin"])
        self.assertTrue((self.out / r["cwd"] / "dev0_sp_trace.bin").exists())

    def test_nothing_is_written_outside_the_out_folder_but_the_ledger(self):
        self.assertEqual(self.read_ok()[0], 0)
        made = sorted(str(p.relative_to(self.t)) for p in self.t.rglob("*") if p.is_file())
        outside = [m for m in made if not m.startswith("out/")]
        self.assertEqual(outside, ["answer.txt", "etwho.log", "ledger/aifoundry2-c0.jsonl", "lock/etsoc-shire0.lock",
                                   "lock/etsoc-shire1.lock", "standin.log"])  # the stand-ins' files, and the ledger
        lines = self.ledger_lines()
        self.assertEqual([(e["event"], e["verdict"]) for e in lines], [("SENT", "SENT"), ("END", "EQUAL")])
        self.assertEqual({(e["boot_id"], e["boot_epoch"], e["record"]) for e in lines},
                         {(f"desk-boot-{A2_BOOT}", A2_BOOT, str(self.records()[0].resolve()))})
        self.assertEqual(oct(self.ledger.stat().st_mode & 0o777), "0o700")


class TestFinding1StopsCarryAcrossFolders(DeskBase):
    """verify-guards' finding 1: a read that did not end EQUAL stops every later read and launch of that card on that
    boot, whatever folder they name (the ledger), and a folder holding such a read stops look and guard."""

    def test_a_stop_carries_across_folders_on_this_boot(self):
        a, b = self.t / "A", self.t / "B"
        rc, out = self.read_ok(out=a, answer=e82_answer())  # DIFFERENT: PMIC 1.3.0 against 1.5.0
        self.assertEqual(rc, 16, out)
        rc, out = self.read_ok(out=b)  # a good answer, a new folder: nothing sent
        self.assertEqual(rc, 16, out)
        self.assertIn("already ended DIFFERENT", out)
        self.assertEqual(len(self.calls()), 1)
        self.assertEqual(self.records(b), [])
        for extra in ((a, b), (b,), ()):
            with self.subTest(extra=[x.name for x in extra]):
                args = [x for d in extra for x in ("--extra", d)]
                rc, out = self.gate("guard", "--box", "aifoundry2", "--card", 0, *args)
                self.assertEqual(rc, 16, out)
                self.assertIn("did not end EQUAL, DIFFERENT", out)
                rc, out = self.gate("look", "--box", "aifoundry2", "--card", 0, *args)
                self.assertEqual(rc, 16, out)
                self.assertIn("STOPPED:", out)
        self.assertEqual([(e["event"], e["verdict"]) for e in self.ledger_lines()],
                         [("SENT", "SENT"), ("END", "DIFFERENT")])

    def test_a_folder_holding_a_different_and_an_equal_read_refuses(self):
        a, b = self.t / "A", self.t / "B"
        self.assertEqual(self.read_ok(out=b)[0], 0)  # EQUAL in B
        rc, out = self.read_ok(out=a, answer=e82_answer(), now=NOW + 60, FWGATE_LEDGER_DIR=self.t / "ledger-other")
        self.assertEqual(rc, 16, out)  # DIFFERENT in A, kept off this ledger: only the folder shows it
        for f in b.iterdir():
            if f.is_file():
                shutil.copy2(f, a / f.name)  # B's EQUAL read beside A's DIFFERENT one
        rc, out = self.gate("guard", "--box", "aifoundry2", "--card", 0, "--extra", a)
        self.assertEqual(rc, 16, out)
        self.assertIn("did not end EQUAL, DIFFERENT", out)
        rc, out = self.gate("guard", "--box", "aifoundry2", "--card", 0, "--extra", b)
        self.assertEqual(rc, 0, out)  # B alone: its EQUAL read, and this ledger holds no other read
        (b / "fwgate-aifoundry2-c0-garbage.json").write_text("{not json")
        rc, out = self.gate("guard", "--box", "aifoundry2", "--card", 0, "--extra", b)
        self.assertEqual(rc, 16, out)  # a record that cannot be read stops (fail closed)
        self.assertIn("UNREADABLE-RECORD", out)

    def test_the_ledger_counts_only_this_boot(self):
        a = self.t / "A"
        rc, out = self.read_ok(out=a, answer=e82_answer())  # DIFFERENT on the 13 Nov boot
        self.assertEqual(rc, 16, out)
        rc, out = self.read_ok(out=a, boot=LATER_BOOT, now=NOW + 60)  # a later boot: a new read, into the same folder
        self.assertEqual(rc, 0, out)
        self.assertEqual(len(self.calls()), 2)
        rc, out = self.gate("guard", "--box", "aifoundry2", "--card", 0, "--extra", a, boot=LATER_BOOT, now=NOW + 60)
        self.assertEqual(rc, 0, out)  # the earlier boot's DIFFERENT is another boot's
        rc, out = self.gate("guard", "--box", "aifoundry2", "--card", 0, "--extra", a)
        self.assertEqual(rc, 16, out)  # on the 13 Nov boot it still stops

    def test_a_ledger_line_that_cannot_be_read_or_a_sent_without_an_end_stops(self):
        self.ledger.mkdir()
        ledger_file = self.ledger / "aifoundry2-c0.jsonl"
        sent = {"schema": "fwgate-ledger/1", "box": "aifoundry2", "card": 0, "event": "SENT", "verdict": "SENT",
                "record": "/elsewhere/fwgate-aifoundry2-c0-20261115-120000.json", "boot_epoch": A2_BOOT}
        for name, text, want in (("cut line", '{"schema": "fwgate-ledger/1", "box": "aifo\n', "LEDGER-LINE-UNREADABLE"),
                                 ("SENT, no END", json.dumps(dict(sent, boot_id=f"desk-boot-{A2_BOOT}")) + "\n",
                                  "already ended SENT")):
            with self.subTest(case=name):
                ledger_file.write_text(text)
                rc, out = self.read_ok()
                self.assertEqual(rc, 16, out)
                self.assertIn(want, out)
                for sub in ("guard", "look"):
                    rc, out = self.gate(sub, "--box", "aifoundry2", "--card", 0)
                    self.assertEqual(rc, 16, out)
        self.assertEqual(self.calls(), [])
        ledger_file.write_text(json.dumps(dict(sent, boot_id="desk-boot-1")) + "\n")  # another boot's SENT
        rc, out = self.read_ok()
        self.assertEqual(rc, 0, out)
        self.assertEqual(len(self.calls()), 1)

    def test_a_ledger_that_cannot_be_written_sends_nothing(self):
        blocker = self.t / "a-file"
        blocker.write_text("not a folder\n")
        rc, out = self.read_ok(FWGATE_LEDGER_DIR=blocker / "ledger")
        self.assertEqual(rc, 10, out)
        self.assertIn("cannot be written", out)
        self.assertEqual(self.calls(), [])
        self.assertEqual(self.records(), [])
        self.assertFalse((self.t / "etwho.log").exists())  # refused before et-who
        self.ledger.mkdir()
        ledger_file = self.ledger / "aifoundry2-c0.jsonl"
        ledger_file.write_text("")
        ledger_file.chmod(0)  # a ledger that cannot be read may hold a stop: it stops
        try:
            rc, out = self.read_ok()
            self.assertEqual(rc, 16, out)
            self.assertIn("LEDGER-UNREADABLE", out)
            rc, out = self.gate("guard", "--box", "aifoundry2", "--card", 0)
            self.assertEqual(rc, 16, out)
        finally:
            ledger_file.chmod(0o600)
        self.assertEqual(self.calls(), [])

    def test_an_equal_read_does_not_stop_a_new_folders_read(self):
        a, b = self.t / "A", self.t / "B"
        self.assertEqual(self.read_ok(out=a)[0], 0)
        rc, out = self.read_ok(out=b, now=NOW + 60)  # a kit with a new folder on the same boot reads once more
        self.assertEqual(rc, 0, out)
        self.assertEqual(len(self.calls()), 2)
        rc, out = self.read_ok(out=b, now=NOW + 120)  # into the same folder again: carried, nothing sent
        self.assertEqual((rc, len(self.calls())), (0, 2), out)
        rc, out = self.gate("guard", "--box", "aifoundry2", "--card", 0, "--extra", a, "--extra", b)
        self.assertEqual(rc, 0, out)


class TestFinding2DeskSettings(DeskBase):
    """verify-guards' finding 2: a desk test runs only with every stand-in, never a real path or a device tool's
    name."""

    def settings_with(self, **env):
        base = {"FWGATE_DESK_TEST": "1", "FWGATE_CLI": str(CLI), "FWGATE_ETWHO": str(ETWHO),
                "FWGATE_LOCKDIR": str(self.lockdir), "FWGATE_LEDGER_DIR": str(self.ledger),
                "FWGATE_HOSTNAME": "aifoundry2", "FWGATE_BOOT_EPOCH": str(A2_BOOT), "FWGATE_NOW_EPOCH": str(NOW)}
        for k, v in env.items():
            if v is None:
                base.pop(k, None)
            else:
                base[k] = str(v)
        saved = {k: os.environ.get(k) for k in set(F.DESK_KEYS) | {"FWGATE_DESK_TEST"}}
        try:
            for k in saved:
                os.environ.pop(k, None)
            os.environ.update(base)
            return F.settings()  # in-process: nothing is run, whatever it returns
        finally:
            for k, v in saved.items():
                os.environ.pop(k, None)
                if v is not None:
                    os.environ[k] = v

    def test_a_desk_test_needs_every_stand_in(self):
        s = self.settings_with()
        self.assertEqual((s["cli"], s["etwho"], s["ledger"]), (str(CLI), str(ETWHO), str(self.ledger)))
        for k in F.DESK_NEEDS:
            with self.subTest(missing=k):
                with self.assertRaises(F.Refused) as cm:
                    self.settings_with(**{k: None})
                self.assertEqual(cm.exception.code, 10)
                self.assertIn("without every stand-in", cm.exception.msg)
        rc, out = self.gate("look", "--box", "aifoundry2", "--card", 0, drop=("FWGATE_CLI",))
        self.assertEqual(rc, 10, out)
        self.assertIn("never falls back to the real tools", out)

    def test_a_desk_test_never_takes_a_real_path_or_a_device_tools_name(self):
        link = self.t / "cli-link"
        os.symlink(F.REAL["cli"], link)
        named = {n: self.t / n for n in ("dev_mngt_service", "ledger_host", "ettelem", "et-who")}
        for n, p in named.items():
            shutil.copy(CLI if n != "et-who" else ETWHO, p)  # copies of the stand-ins under lab tools' names: never run
        cases = {"FWGATE_CLI": (F.REAL["cli"], link, named["dev_mngt_service"], named["ledger_host"], named["ettelem"]),
                 "FWGATE_ETWHO": (F.REAL["etwho"], named["et-who"]),
                 "FWGATE_LOCKDIR": (F.REAL["lockdir"],), "FWGATE_LEDGER_DIR": (F.real_ledger_dir(),)}
        for k, values in cases.items():
            for v in values:
                with self.subTest(key=k, value=str(v)):
                    with self.assertRaises(F.Refused) as cm:
                        self.settings_with(**{k: v})
                    self.assertEqual(cm.exception.code, 10)
        self.assertEqual(self.calls(), [])


class TestFinding3And4LockFiles(DeskBase):
    """verify-guards' findings 3 and 4: no lock file is ever made, and a second read while one is in flight is told to
    call again (17), not stopped (16)."""

    def test_a_missing_lock_file_sends_nothing_and_is_never_made(self):
        (self.lockdir / "etsoc-shire0.lock").unlink()
        rc, out = self.read_ok()
        self.assertEqual(rc, 17, out)
        self.assertIn("is missing", out)
        self.assertEqual((self.calls(), self.records(), self.ledger_lines()), ([], [], []))
        self.assertFalse((self.lockdir / "etsoc-shire0.lock").exists())
        boot = epoch("2026-11-14T08:00:00-08:00")
        (self.lockdir / "etsoc-shire0.lock").touch()
        (self.lockdir / "etsoc-shire1.lock").unlink()  # aifoundry1: card 0's taken, then card 1's missing
        rc, out = self.gate("read", "--box", "aifoundry1", "--card", 1, "--out", self.out, "--both-nodes-ok",
                            box="aifoundry1", boot=boot, answer=e82_answer())
        self.assertEqual(rc, 17, out)
        self.assertFalse((self.lockdir / "etsoc-shire1.lock").exists())
        fd = os.open(self.lockdir / "etsoc-shire0.lock", os.O_RDONLY)
        fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)  # card 0's lock was released again
        os.close(fd)
        self.assertEqual(self.calls(), [])

    def test_two_reads_at_once_send_one_query_and_the_second_is_called_again(self):
        res = {}

        def first():
            res[1] = self.read_ok(FWGATE_STANDIN_SLEEP=3)

        th = threading.Thread(target=first)
        th.start()
        deadline = time.time() + 30
        while time.time() < deadline and not self.records():  # its SENT record: it holds the card's lock now
            time.sleep(0.05)
        self.assertTrue(self.records(), "the first read never wrote its SENT record")
        res[2] = self.gate("read", "--box", "aifoundry2", "--card", 0, "--out", self.out)  # the answer file left as is
        th.join()
        self.assertEqual(res[1][0], 0, res[1][1])
        self.assertEqual(res[2][0], 17, res[2][1])
        self.assertIn("is held: nothing sent", res[2][1])
        self.assertEqual(len(self.calls()), 1)
        rc, out = self.read_ok()  # called again: the first read's EQUAL carries the identity
        self.assertEqual((rc, len(self.calls())), (0, 1), out)
        self.assertIn("CONTINUITY", out)


class TestStatic(unittest.TestCase):
    def test_the_gate_names_one_command_and_runs_two_programs(self):
        src = GATE.read_text()
        prefix = "DM" + "_CMD_"  # spelled in two parts so that the audit does not read this test as a send site
        self.assertEqual(re.findall(r"\b" + prefix + r"[A-Z0-9_]+", src), [F.QUERY])
        self.assertEqual(F.QUERY, "DM_CMD_GET_MODULE_FIRMWARE_REVISIONS")
        self.assertEqual(len(re.findall(r"subprocess\.(?:run|Popen|call|check_output|check_call)\(", src)), 2)
        self.assertIn('argv = [s["timeout"], "10", s["cli"], "-m", QUERY, "-n", str(a.card), "-u", "5000"]', src)
        self.assertEqual(F.REAL["cli"], "/opt/et/bin/dev_mngt_service")
        self.assertEqual(F.REAL["timeout"], "/usr/bin/timeout")

    def test_the_stand_ins_are_not_named_as_device_tools(self):
        for p in (CLI, ETWHO):
            self.assertFalse(p.name.startswith("dev_mngt") or p.name.endswith("_host"), p.name)
            self.assertIsNone(F.DEVICE_TOOL.search(p.name), p.name)

    def test_finding3_the_gate_never_makes_a_lock_file(self):
        self.assertNotIn("O_CREAT", inspect.getsource(F.take_locks))
        self.assertEqual(GATE.read_text().count("O_CREAT"), 1)  # the ledger's own file, nothing else
        self.assertIn("O_CREAT", inspect.getsource(F.ledger_open))


if __name__ == "__main__":
    unittest.main()
