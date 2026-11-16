#!/usr/bin/env python3
"""Tests of dmcmd_audit_v2.py, dmcmd_table_v2.json and make_dmcmd_table_v2.py (Q188, Sun 15 Nov 2026). Stdlib only:
python3 tools/claims-v3/test_dmcmd_audit_v2.py -v

v2 reclassifies two read queries, GET_MODULE_FIRMWARE_REVISIONS (14) and GET_FRU (71), from WRITE to READ (pmic "read")
by the owner's rulings of Sun 15 Nov 2026, and nothing else. These tests show: the two are READ and GO (by name, by
code, as raw constants, in the lab's own form), and still NO-GO under --deny-pmic-read; every other WRITE of v1 is the
same entry in v2 and NO-GO one by one, by name and by code, the firmware-modifying and state-changing ones named
(firmware update, version counter, boot certificates, FRU and part-number sets, cache config and VMIN LUT, the card
reset, voltage and frequency sets, the PCIe sets and resets, the Master Minion reset, every MDI write, the bare
statistics run control, the governor's two sets); v2 differs from v1 in exactly two command entries and its header,
line for line; v1's audit, table and tests stay at their pinned sha256 and v1's 55 tests still pass, unchanged, in a
subprocess; the v1 -> v2 audit diff is confined to the lines its docstring names; each of the two entries scopes its
source claim to the service processor's side and rests the PMIC's side on the owner's ruling; and on real files of this
repository the three senders that sent only the query read GO while the five that send real writes stay NO-GO."""
import difflib
import hashlib
import io
import json
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import dmcmd_audit as A1  # noqa: E402
import dmcmd_audit_v2 as A2  # noqa: E402
import make_dmcmd_table_v2 as G  # noqa: E402

REPO = HERE.parent.parent
V1_TABLE = HERE / "dmcmd_table.json"
V2_TABLE = HERE / "dmcmd_table_v2.json"
E144_TABLE = HERE / "e144" / "dmcmd_table_e144.json"
PINS = {  # v1's three files and E144's table, unchanged since 32e9c109 and 13799873 (35 committed hash lists pin v1's
    # audit and 29 its table)
    "dmcmd_table.json": "50168632931fd8c1fab40794cbaaac6aca3d31f01d4367d8a21fcf69c0bdc638",
    "dmcmd_audit.py": "f29e91ca97705454f67c46c28974a085c5bb70ff43e940538b1f670b88ae844e",
    "test_dmcmd_audit.py": "05ca512304323854c8ab880408df61f008dd805ef056dec8d6333fffd1f94fd2",
    "e144/dmcmd_table_e144.json": "a5a5ed8583df6def59c5a6cbf205d7c99b92159d70b93348844b8c851c0c7282",
}
RULING = {
    "2026-11-15 15:07:01 PST": ("Firmware revisions query was a false positive. It should have never been forbidden. "
                                "Reading operations and firmware are always allowed."),
    "2026-11-15 15:09:49 PST": ("Yeah, fix the corresponding guards. I don't want to modify firmware, but commands which "
                                "read firmware should be fine."),
}
RECLASSIFIED = ("GET_MODULE_FIRMWARE_REVISIONS", "GET_FRU")
# the brief's list, one by one: firmware, flash, OTP, PMIC NVM, persistent configuration, resets, voltages, clocks,
# links, debug state, statistics control, and the governor's two sets
NAMED_WRITES = ("SET_FIRMWARE_UPDATE", "SET_FIRMWARE_VERSION_COUNTER", "SET_SP_BOOT_ROOT_CERT", "SET_SW_BOOT_ROOT_CERT",
                "SET_FRU", "SET_MODULE_PART_NUMBER", "SET_SHIRE_CACHE_CONFIG", "SET_VMIN_LUT", "RESET_ETSOC",
                "SET_MODULE_VOLTAGE", "SET_FREQUENCY", "SET_PCIE_RESET", "SET_PCIE_MAX_LINK_SPEED",
                "SET_PCIE_LANE_WIDTH", "SET_PCIE_RETRAIN_PHY", "MM_RESET", "MDI_SELECT_HART", "MDI_UNSELECT_HART",
                "MDI_RESET_HART", "MDI_HALT_HART", "MDI_RESUME_HART", "MDI_SET_BREAKPOINT", "MDI_UNSET_BREAKPOINT",
                "MDI_ENABLE_SINGLE_STEP", "MDI_DISABLE_SINGLE_STEP", "MDI_WRITE_GPR", "MDI_WRITE_CSR", "MDI_WRITE_MEM",
                "SET_STATS_RUN_CONTROL", "SET_MODULE_STATIC_TDP_LEVEL", "SET_MODULE_TEMPERATURE_THRESHOLDS")
LAB_FORM = ("timeout 10 /opt/et/bin/dev_mngt_service -m DM_CMD_GET_MODULE_FIRMWARE_REVISIONS -n 0 -u 5000 "
            "< /dev/null > fw.out 2>&1\n")


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def load(p):
    return json.loads(Path(p).read_text())


class Base(unittest.TestCase):
    def setUp(self):
        self.d = Path(tempfile.mkdtemp(prefix="dmcmd-audit-v2-test-"))

    def tearDown(self):
        shutil.rmtree(self.d, ignore_errors=True)

    def write(self, name, text):
        p = self.d / name
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text)
        return p

    def run_main(self, mod, *args):
        out, err = io.StringIO(), io.StringIO()
        with redirect_stdout(out), redirect_stderr(err):
            rc = mod.main(["--json", *map(str, args)])
        return rc, json.loads(out.getvalue())

    def audit(self, *args):
        return self.run_main(A2, *args)

    def audit_v1(self, *args):
        return self.run_main(A1, *args)

    def cmds(self, res, verdict_prefix=None):
        return sorted({r["command"] for r in res["records"]
                       if verdict_prefix is None or r["verdict"].startswith(verdict_prefix)})


class TestTheTwoReadsAreReads(Base):
    """v1's three tests that v2 inverts (test_revisions_query_by_name_is_a_pmic_write, test_revisions_query_by_code,
    test_raw_ioctl_client_constants), GET_FRU beside them, and the lab's own form."""

    def test_revisions_query_by_name_is_a_read(self):
        f = self.write("gate.sh", 'DMS=/opt/et/bin/dev_mngt_service\n'
                                  'timeout 20 "$DMS" -m DM_CMD_GET_MODULE_FIRMWARE_REVISIONS -n 0 -u 5000\n')
        rc, res = self.audit(f)
        self.assertEqual(rc, A2.EXIT_GO, res)
        rec = [r for r in res["records"] if r["command"] == "GET_MODULE_FIRMWARE_REVISIONS"][0]
        self.assertEqual((rec["cls"], rec["pmic"], rec["verdict"]), ("READ", "read", "ok"))
        rc1, res1 = self.audit_v1(f)  # v1 unchanged: still NO-GO on the same file
        self.assertEqual(rc1, A1.EXIT_NOGO)
        self.assertEqual(self.cmds(res1, "NO-GO"), ["GET_MODULE_FIRMWARE_REVISIONS"])

    def test_revisions_query_by_code(self):
        f = self.write("gate.sh", '/opt/et/bin/dev_mngt_service -o 14 -n 0\n/opt/et/bin/dev_mngt_service --code=33 -n 0\n')
        rc, res = self.audit(f)
        self.assertEqual(rc, A2.EXIT_GO, res)
        self.assertEqual(self.cmds(res), ["GET_MODULE_FIRMWARE_REVISIONS", "GET_MODULE_POWER"])
        self.assertTrue(all(r["verdict"] == "ok" for r in res["records"]))

    def test_raw_ioctl_client_constants(self):
        f = self.write("c.py", 'PUSH_SQ = 1\nCMD_POWER, CMD_FW = 33, 14\nGET_SP_STATS = 60\n')
        rc, res = self.audit(f)
        self.assertEqual(rc, A2.EXIT_GO, res)
        self.assertEqual(self.cmds(res), ["GET_MODULE_FIRMWARE_REVISIONS", "GET_MODULE_POWER", "GET_SP_STATS"])

    def test_get_fru_by_name_and_by_code(self):
        f = self.write("fru.sh", '/opt/et/bin/dev_mngt_service -m DM_CMD_GET_FRU -n 0 -u 5000\n'
                                 '/opt/et/bin/dev_mngt_service -o 71 -n 0 -u 5000\n')
        rc, res = self.audit(f)
        self.assertEqual(rc, A2.EXIT_GO, res)
        self.assertEqual({(r["line"], r["command"], r["cls"], r["pmic"]) for r in res["records"]},
                         {(1, "GET_FRU", "READ", "read"), (2, "GET_FRU", "READ", "read")})
        rc1, _ = self.audit_v1(f)
        self.assertEqual(rc1, A1.EXIT_NOGO)

    def test_the_lab_form_is_go_with_no_allow_list_and_no_allowed_write(self):
        f = self.write("fwread.sh", LAB_FORM)
        rc, res = self.audit(f)
        self.assertEqual(rc, A2.EXIT_GO, res)
        self.assertEqual(res["allow"], [])
        self.assertEqual([r["verdict"] for r in res["records"]], ["ok"])  # never an "ALLOWED WRITE"

    def test_deny_pmic_read_still_refuses_both(self):
        f = self.write("both.sh", LAB_FORM + '/opt/et/bin/dev_mngt_service -m DM_CMD_GET_FRU -n 0 -u 5000\n')
        rc, res = self.audit("--deny-pmic-read", f)
        self.assertEqual(rc, A2.EXIT_NOGO)
        self.assertEqual(self.cmds(res, "NO-GO"), ["GET_FRU", "GET_MODULE_FIRMWARE_REVISIONS"])
        self.assertTrue(all("PMIC read denied" in r["verdict"] for r in res["records"]))

    def test_v1_with_table_v2_gives_the_same_verdicts(self):  # v1 reads any table through --table: v2 only names itself
        f = self.write("fwread.sh", LAB_FORM)
        rc1, res1 = self.audit_v1("--table", V2_TABLE, f)
        rc2, res2 = self.audit(f)
        self.assertEqual((rc1, res1["records"]), (rc2, res2["records"]))


class TestEveryOtherWriteStillRefused(Base):
    def test_every_named_write_is_v1s_write_entry(self):
        t1, t2 = load(V1_TABLE), load(V2_TABLE)
        for name in NAMED_WRITES:
            with self.subTest(name=name):
                self.assertEqual(t2["commands"][name]["class"], "WRITE")
                self.assertEqual(t2["commands"][name], t1["commands"][name])

    def test_the_writes_are_v1s_writes_less_the_two(self):
        t1, t2 = load(V1_TABLE), load(V2_TABLE)
        w1 = {n for n, c in t1["commands"].items() if c["class"] == "WRITE"}
        w2 = {n for n, c in t2["commands"].items() if c["class"] == "WRITE"}
        self.assertEqual(w1 - w2, set(RECLASSIFIED))
        self.assertEqual(w2 - w1, set())
        self.assertEqual(len(w2), 38)
        self.assertTrue(set(NAMED_WRITES) <= w2)
        mdi_writes = {n for n in w2 if n.startswith("MDI_")}
        self.assertEqual(len(mdi_writes), 12)
        self.assertTrue(mdi_writes <= set(NAMED_WRITES))  # every MDI write is in the named list

    def test_each_write_refused_by_name(self):
        t2 = load(V2_TABLE)
        for name, c in sorted(t2["commands"].items(), key=lambda kv: kv[1]["id"]):
            if c["class"] != "WRITE":
                continue
            with self.subTest(name=name):
                f = self.write(f"w_{name}.sh", f"timeout 10 /opt/et/bin/dev_mngt_service -m DM_CMD_{name} -n 0 -u 5000\n")
                rc, res = self.audit(f)
                self.assertEqual(rc, A2.EXIT_NOGO, name)
                self.assertEqual(self.cmds(res, "NO-GO"), [name])
                self.assertTrue(res["records"][0]["verdict"].startswith("NO-GO: WRITE not in the allow-list"), name)

    def test_each_write_refused_by_code(self):
        t2 = load(V2_TABLE)
        for name, c in sorted(t2["commands"].items(), key=lambda kv: kv[1]["id"]):
            if c["class"] != "WRITE":
                continue
            with self.subTest(name=name):
                f = self.write(f"o_{c['id']}.sh", f"/opt/et/bin/dev_mngt_service -o {c['id']} -n 0 -u 5000\n")
                rc, res = self.audit(f)
                self.assertEqual(rc, A2.EXIT_NOGO, name)
                self.assertEqual(self.cmds(res, "NO-GO"), [name])

    def test_each_named_write_refused_in_c_and_python(self):
        for name in NAMED_WRITES:
            with self.subTest(name=name):
                c = self.write(f"c_{name}.cpp", f"int code = DM_CMD_{name};\n")
                p = self.write(f"p_{name}.py", f'run(["/opt/et/bin/dev_mngt_service", "-m", "DM_CMD_{name}", "-n", "0"])\n')
                for f in (c, p):
                    rc, res = self.audit(f)
                    self.assertEqual(rc, A2.EXIT_NOGO, (name, f.name))
                    self.assertIn(name, self.cmds(res, "NO-GO"))

    def test_the_mdi_reads_stay_reads_and_the_writes_writes(self):
        t1, t2 = load(V1_TABLE), load(V2_TABLE)
        for name, c in t2["commands"].items():
            if name.startswith("MDI_"):
                with self.subTest(name=name):
                    self.assertEqual(c, t1["commands"][name])

    def test_the_bare_statistics_run_control_is_never_allowed(self):
        f = self.write("x.sh", '/opt/et/bin/dev_mngt_service -n 0 -o 62\n'
                               '/opt/et/bin/dev_mngt_service -n 0 -m DM_CMD_SET_STATS_RUN_CONTROL\n')
        for token in ("STATS_RESET", "SET_STATS_RUN_CONTROL"):
            rc, res = self.audit("--allow", token, f)
            self.assertEqual(rc, A2.EXIT_NOGO)
            self.assertEqual(self.cmds(res, "NO-GO"), ["SET_STATS_RUN_CONTROL"])
            self.assertTrue(all("not provably the ruled statistics reset" in r["verdict"] for r in res["records"]))

    def test_the_statistics_reset_only_by_name(self):
        f = self.write("run.sh", 'ETTELEM=build/ettelem/ettelem\n"$ETTELEM" sample --seconds 10 --reset-ms 1000\n')
        rc, res = self.audit(f)
        self.assertEqual((rc, self.cmds(res, "NO-GO")), (A2.EXIT_NOGO, ["STATS_RESET"]))
        rc, res = self.audit("--allow", "STATS_RESET", f)
        self.assertEqual((rc, self.cmds(res, "ALLOWED WRITE")), (A2.EXIT_GO, ["STATS_RESET"]))

    def test_the_governor_sets_need_their_own_allowance(self):
        f = self.write("gov.sh", '/opt/et/bin/dev_mngt_service -m DM_CMD_SET_MODULE_STATIC_TDP_LEVEL -n 0 -u 5000\n'
                                 '/opt/et/bin/dev_mngt_service -m DM_CMD_SET_MODULE_TEMPERATURE_THRESHOLDS -n 0 -u 5000\n')
        rc, res = self.audit(f)
        self.assertEqual(rc, A2.EXIT_NOGO)
        self.assertEqual(self.cmds(res, "NO-GO"), ["SET_MODULE_STATIC_TDP_LEVEL", "SET_MODULE_TEMPERATURE_THRESHOLDS"])
        rc, res = self.audit("--allow", "GET_MODULE_FIRMWARE_REVISIONS", f)  # a read in the list allows no write
        self.assertEqual(rc, A2.EXIT_NOGO)

    def test_forms_and_host_writes_unchanged(self):
        f = self.write("h.sh", '/opt/et/bin/dev_mngt_service -n 0 -t SPST:enable\n/opt/et/bin/dev_mngt_service -n 0 -t SPST:reset\n'
                               '/opt/et/bin/dev_mngt_service -n 0 -t MMST:reset\necho 1 > /sys/bus/pci/devices/0000:01:00.0/reset\n'
                               'setpci -s 00:01.0 CAP_EXP+10.w=0020\nsudo modprobe -r et_soc1\nsudo reboot\net-reset 0\n')
        rc1, res1 = self.audit_v1(f)
        rc2, res2 = self.audit(f)
        self.assertEqual(rc2, A2.EXIT_NOGO)
        self.assertEqual(self.cmds(res2, "NO-GO"), ["HOST_REBOOT", "MMST_CONTROL", "MODULE_LOAD", "RESET_ETSOC",
                                                    "SETPCI_WRITE", "SPST_RESET", "SPST_TRACE_CONTROL", "SYSFS_WRITE"])
        self.assertEqual((rc1, res1["records"]), (rc2, res2["records"]))

    def test_set_fru_stays_a_write_beside_get_fru(self):
        f = self.write("fru2.sh", '/opt/et/bin/dev_mngt_service -m DM_CMD_GET_FRU -n 0 -u 5000\n'
                                  '/opt/et/bin/dev_mngt_service -m DM_CMD_SET_FRU -n 0 -u 5000\n')
        rc, res = self.audit(f)
        self.assertEqual(rc, A2.EXIT_NOGO)
        self.assertEqual(self.cmds(res, "NO-GO"), ["SET_FRU"])
        self.assertEqual(self.cmds(res, "ok"), ["GET_FRU"])


class TestTableV2(Base):
    def test_v2_differs_from_v1_in_exactly_the_two_entries_and_the_header(self):
        t1, t2 = load(V1_TABLE), load(V2_TABLE)
        diff = sorted(n for n in t1["commands"] if t1["commands"][n] != t2["commands"].get(n))
        self.assertEqual(diff, sorted(RECLASSIFIED))
        self.assertEqual(set(t2["commands"]), set(t1["commands"]))
        for k in ("source", "classes", "common_side_effects", "forms", "pseudo", "tools"):
            self.assertEqual(t2[k], t1[k], k)
        self.assertEqual(set(t2) - set(t1), {"supersedes", "ruling", "v2_changes", "v2_classes_note"})
        for name in RECLASSIFIED:
            e1, e2 = t1["commands"][name], t2["commands"][name]
            self.assertEqual((e1["class"], e1["pmic"], e2["class"], e2["pmic"]), ("WRITE", "write", "READ", "read"))
            for k in e1:  # every v1 key kept, unchanged but class, pmic and what (v1's what kept as v1_what)
                if k not in ("class", "pmic", "what"):
                    self.assertEqual(e2[k], e1[k], (name, k))
            self.assertEqual(e2["v1_what"], e1["what"])

    def test_the_two_carry_the_ruling_and_the_handler_lines(self):
        t2 = load(V2_TABLE)
        want = {"GET_MODULE_FIRMWARE_REVISIONS": ("firmware_update.c:1091-1092", "firmware_update.c:862-917",
                                                  "pmic_controller.c:952-974", ":2543", ":2549", ":2585-2587", ":2591",
                                                  "pmic_hal.h:66-77", ":2706", ":3219", "common/main.c:189, :240"),
                "GET_FRU": ("asset_track.c:204-205", "asset_track.c:96-100", "pmic_controller.c:2412-2445", ":2419",
                            ":2424", ":2430-2431", ":2438", "pmic_hal.h:87-92", ":2485-2486", ":2501-2502",
                            "common/main.c:210, :240")}
        for name, cites in want.items():
            e = t2["commands"][name]
            with self.subTest(name=name):
                self.assertEqual(e["ruling"], RULING)
                text = " ".join(e["evidence"])
                for c in cites:
                    self.assertIn(c, text)
                self.assertEqual(e["reclassified"]["from"], {"class": "WRITE", "pmic": "write"})
                self.assertEqual(e["reclassified"]["to"], {"class": "READ", "pmic": "read"})
                self.assertIn("836a4ab", e["evidence_source"])
                self.assertTrue(e["pmic_command_writes"])

    def test_the_two_scope_their_source_claim_to_the_service_processor(self):
        # verify-guards' finding 8: the source shows the service processor's side only; the PMIC's rests on the ruling
        t2 = load(V2_TABLE)
        for name, cite in (("GET_MODULE_FIRMWARE_REVISIONS", "common/main.c:189, from :240"),
                           ("GET_FRU", "common/main.c:210, from :240")):
            with self.subTest(name=name):
                what = t2["commands"][name]["what"]
                self.assertNotIn("changes nothing on the card", what)
                self.assertIn("From the source (et-platform 836a4ab) it changes nothing persistent on the service "
                              "processor's side", what)
                self.assertIn("on the PMIC's side the READ rests on the owner's ruling", what)
                self.assertIn(cite, what)

    def test_the_header_names_v1_and_why(self):
        t2 = load(V2_TABLE)
        self.assertEqual(t2["schema"], "dmcmd-table/2")
        self.assertEqual(t2["supersedes"]["path"], "tools/claims-v3/dmcmd_table.json")
        self.assertEqual(t2["supersedes"]["sha256"], PINS["dmcmd_table.json"])
        self.assertIn("false positive", t2["supersedes"]["why"])
        for k, v in RULING.items():
            self.assertEqual(t2["ruling"][k], v)

    def test_table_v2_is_complete_against_the_enum(self):
        t = A2.Table(A2.DEFAULT_TABLE)
        self.assertEqual(A2.DEFAULT_TABLE.name, "dmcmd_table_v2.json")
        ids = {c["id"] for c in t.commands.values()}
        self.assertEqual(ids, set(range(0, 75)) | set(range(128, 145)))
        counts = {}
        for name, c in t.commands.items():
            self.assertIn(c["class"], ("READ", "WRITE", "UNSUPPORTED", "UNCLASSIFIED"), name)
            counts[c["class"]] = counts.get(c["class"], 0) + 1
            if c["class"] == "WRITE":
                self.assertTrue(c.get("reaches"), name)
        self.assertEqual(counts, {"READ": 48, "WRITE": 38, "UNSUPPORTED": 5, "UNCLASSIFIED": 1})

    def test_every_other_v1_line_is_byte_identical(self):
        a = V1_TABLE.read_text().split("\n")
        b = V2_TABLE.read_text().split("\n")
        changed = []
        for tag, i1, i2, j1, j2 in difflib.SequenceMatcher(None, a, b, autojunk=False).get_opcodes():
            if tag != "equal":
                changed += [(i + 1) for i in range(i1, i2)]
        lines = {n: a[n - 1] for n in changed}
        self.assertEqual(sorted(changed), [2, 3, 4, 42, 99], lines)  # schema, title, written; 14; 71
        self.assertTrue(lines[42].startswith('    "GET_MODULE_FIRMWARE_REVISIONS": '))
        self.assertTrue(lines[99].startswith('    "GET_FRU": '))

    def test_the_generator_makes_the_committed_v2(self):
        with redirect_stdout(io.StringIO()):
            self.assertEqual(G.main(["--check"]), 0)
        self.assertEqual(G.V1_SHA, PINS["dmcmd_table.json"])

    def test_the_generator_from_e144(self):
        out = self.d / "dmcmd_table_kit.json"
        with redirect_stdout(io.StringIO()):
            self.assertEqual(G.main(["--base", "e144", "--out", str(out)]), 0)
        te, tk = load(E144_TABLE), load(out)
        diff = sorted(n for n in te["commands"] if te["commands"][n] != tk["commands"][n])
        self.assertEqual(diff, sorted(RECLASSIFIED))
        self.assertEqual(tk["commands"]["GET_ASIC_PVT_SAMPLES"]["class"], "READ")  # E144's own classification kept
        self.assertEqual(tk["supersedes"]["sha256"], PINS["e144/dmcmd_table_e144.json"])
        self.assertIn("--base e144 from tools/claims-v3/e144/dmcmd_table_e144.json", tk["written"])  # finding 10
        self.assertNotIn("(v1)", tk["written"])
        for name in RECLASSIFIED:
            self.assertEqual((tk["commands"][name]["class"], tk["commands"][name]["pmic"]), ("READ", "read"))

    def test_the_generator_refuses_to_overwrite_the_pinned_tables(self):
        for target in (V1_TABLE, V2_TABLE, E144_TABLE):
            with self.subTest(target=target.name), redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
                with self.assertRaises(SystemExit) as cm:
                    G.main(["--base", "e144", "--out", str(target)])
                self.assertEqual(cm.exception.code, 2)
        with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
            with self.assertRaises(SystemExit):
                G.main(["--out", str(self.d / "elsewhere.json")])  # v1's v2 goes only to its committed path


class TestPinsAndV1(Base):
    def test_v1_and_e144_at_their_pinned_sha256(self):
        for rel, want in PINS.items():
            with self.subTest(rel=rel):
                self.assertEqual(sha(HERE / rel), want)

    def test_v1_tests_pass_unchanged(self):
        p = subprocess.run([sys.executable, "-B", str(HERE / "test_dmcmd_audit.py")], capture_output=True, text=True,
                           cwd=str(REPO), timeout=600)
        tail = p.stderr.strip().splitlines()[-3:]
        self.assertEqual(p.returncode, 0, p.stderr[-2000:])
        self.assertIn("Ran 55 tests", p.stderr)
        self.assertEqual(tail[-1], "OK", tail)

    def test_the_audit_diff_is_confined_to_the_named_lines(self):
        a = (HERE / "dmcmd_audit.py").read_text().split("\n")
        b = (HERE / "dmcmd_audit_v2.py").read_text().split("\n")
        changed, groups = [], []
        for tag, i1, i2, j1, j2 in difflib.SequenceMatcher(None, a, b, autojunk=False).get_opcodes():
            if tag != "equal":
                changed += [(i + 1) for i in range(i1, i2)]
                groups.append(b[j1:j2])
        # the docstring's head, usage, table and --deny-pmic-read lines; DEFAULT_TABLE; the own-files set; markdown()
        self.assertEqual(changed, [2, 6, 9, 30, 59, 1032, 1167])
        doc_end = a.index('"""', 1) + 1  # v1's module docstring closes on line 49
        self.assertEqual(doc_end, 49)
        self.assertTrue(all(n < doc_end for n in changed[:4]))
        self.assertEqual(groups[4], ['DEFAULT_TABLE = HERE / "dmcmd_table_v2.json"'])
        self.assertEqual(groups[5], ['        own = {HERE / n for n in ("dmcmd_audit.py", "test_dmcmd_audit.py",',
                                     '                                  "dmcmd_audit_v2.py", "test_dmcmd_audit_v2.py")}'])
        self.assertEqual(groups[6], ['             f"Checked with `tools/claims-v3/dmcmd_audit_v2.py` against '
                                     '`{audit.t.path.name}` (et-platform "'])
        doc = " ".join(" ".join(g) for g in groups[:4])
        for v in RULING.values():  # the docstring quotes both rulings verbatim (wrapped)
            self.assertIn(" ".join(v.split()), " ".join(doc.split()))
        self.assertIn("it skips v1's two files and its own two, four in all", " ".join(doc.split()))  # finding 9

    def test_the_audit_skips_its_own_files(self):
        rc, res = self.audit(HERE / "dmcmd_audit_v2.py", HERE / "test_dmcmd_audit_v2.py", HERE / "dmcmd_audit.py",
                             HERE / "test_dmcmd_audit.py")
        self.assertEqual((rc, res["records"]), (A2.EXIT_GO, []))
        self.assertEqual(sum("the audit's own code" in n for n in res["notes"]), 4)

    def test_the_generator_sends_nothing(self):
        for mod in (A1, A2):
            rc, res = self.run_main(mod, HERE / "make_dmcmd_table_v2.py")
            self.assertEqual((rc, res["records"]), (0, []))


class TestMarkdown(Base):
    def test_markdown_names_v2_and_its_table(self):
        f = self.write("fwread.sh", LAB_FORM)
        out, err = io.StringIO(), io.StringIO()
        with redirect_stdout(out), redirect_stderr(err):
            rc = A2.main(["--markdown", str(f)])
        self.assertEqual(rc, A2.EXIT_GO)
        self.assertIn("Checked with `tools/claims-v3/dmcmd_audit_v2.py` against `dmcmd_table_v2.json`", out.getvalue())
        self.assertIn("| `GET_MODULE_FIRMWARE_REVISIONS` | READ | read | 1 | ok |", out.getvalue())


class TestRealFiles(Base):
    """The repository's own senders of the query (survey-guards' list, Q188): the three that sent only the query read
    GO under v2 (NO-GO under v1); the five that send real writes stay NO-GO under v2, for those writes alone."""

    def setUp(self):
        super().setUp()
        if not (REPO / "tools/claims-v3/e114/run_e114.sh").exists():
            self.skipTest("not in the lab repository")

    def test_query_only_senders_go_under_v2(self):
        for rel in ("tools/claims-v3/e114/run_e114.sh", "tools/claims-v3/kspeed/e84/run_e84.sh",
                    "tools/claims-v3/hlp/run_e79.sh"):
            with self.subTest(rel=rel):
                rc2, res2 = self.audit(REPO / rel)
                self.assertEqual(rc2, A2.EXIT_GO, rel)
                self.assertIn("GET_MODULE_FIRMWARE_REVISIONS", self.cmds(res2, "ok"))
                rc1, res1 = self.audit_v1(REPO / rel)
                self.assertEqual((rc1, self.cmds(res1, "NO-GO")), (A1.EXIT_NOGO, ["GET_MODULE_FIRMWARE_REVISIONS"]))

    def test_real_writers_stay_no_go_for_their_writes(self):
        want = {"tools/claims-v3/lq6/gov_e72.py": ["SET_MODULE_STATIC_TDP_LEVEL"],
                "tools/claims-v3/nv/block.sh": ["SET_MODULE_VOLTAGE", "VARIANT_UNRESOLVED"],
                "tools/claims-v3/nv/stubs/stub-dms": ["SET_MODULE_VOLTAGE"],
                "tools/claims-v3/tel/block.sh": ["SET_DM_TRACE_CONFIG", "STATS_RESET", "VARIANT_UNRESOLVED"],
                "tools/claims-v3/e131/make_predictions_e131.py": ["SET_DM_TRACE_CONFIG", "SET_STATS_RUN_CONTROL",
                                                                  "STATS_RESET"]}
        for rel, nogo in want.items():
            with self.subTest(rel=rel):
                rc, res = self.audit(REPO / rel)
                self.assertEqual((rc, self.cmds(res, "NO-GO")), (A2.EXIT_NOGO, nogo))
                self.assertNotIn("GET_MODULE_FIRMWARE_REVISIONS", self.cmds(res, "NO-GO"))

    def test_fwgate_is_go_under_v2_and_no_go_under_v1(self):
        fw = REPO / "tools/claims-v3/fwgate"
        if not fw.exists():
            self.skipTest("no fwgate")
        rc2, res2 = self.audit(fw)
        self.assertEqual(rc2, A2.EXIT_GO, [r for r in res2["records"] if r["verdict"].startswith("NO-GO")])
        self.assertEqual(self.cmds(res2), ["GET_MODULE_FIRMWARE_REVISIONS"])
        self.assertEqual(res2["allow"], [])
        rc1, res1 = self.audit_v1(fw)
        self.assertEqual((rc1, self.cmds(res1, "NO-GO")), (A1.EXIT_NOGO, ["GET_MODULE_FIRMWARE_REVISIONS"]))
        rc3, _ = self.audit("--deny-pmic-read", fw)
        self.assertEqual(rc3, A2.EXIT_NOGO)


if __name__ == "__main__":
    unittest.main()
