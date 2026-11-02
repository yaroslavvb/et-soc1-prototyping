#!/usr/bin/env python3
"""Tests of dmcmd_audit.py (Q136(w), 2 Nov 2026). Stdlib only: python3 tools/claims-v3/test_dmcmd_audit.py -v

Each test writes a small runner into a temporary directory and checks what the audit lists and its verdict. The last
tests read real files of this repository (skipped when run outside it)."""
import io
import json
import shutil
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import dmcmd_audit as A  # noqa: E402

REPO = HERE.parent.parent


class Base(unittest.TestCase):
    def setUp(self):
        self.d = Path(tempfile.mkdtemp(prefix="dmcmd-audit-test-"))

    def tearDown(self):
        shutil.rmtree(self.d, ignore_errors=True)

    def write(self, name, text):
        p = self.d / name
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text)
        return p

    def audit(self, *args):
        out, err = io.StringIO(), io.StringIO()
        with redirect_stdout(out), redirect_stderr(err):
            rc = A.main(["--json", *map(str, args)])
        return rc, json.loads(out.getvalue())

    def cmds(self, res, verdict_prefix=None):
        return sorted({r["command"] for r in res["records"]
                       if verdict_prefix is None or r["verdict"].startswith(verdict_prefix)})


class TestEttelem(Base):
    def test_stock_sample_reads_only_go(self):
        f = self.write("run.sh", 'ETTELEM=build/ettelem/ettelem\n"$ETTELEM" sample --seconds 10 --every-ms 100 > t.jsonl\n')
        rc, res = self.audit(f)
        self.assertEqual(rc, A.EXIT_GO)
        self.assertEqual(self.cmds(res), ["GET_ASIC_FREQUENCIES", "GET_ASIC_VOLTAGE", "GET_MODULE_CURRENT_TEMPERATURE",
                                          "GET_MODULE_POWER", "GET_MODULE_VOLTAGE", "GET_SP_STATS"])
        self.assertTrue(all(r["cls"] == "READ" for r in res["records"]))

    def test_reset_is_a_write_allowed_only_by_name(self):
        f = self.write("run.sh", 'ETTELEM=build/ettelem/ettelem\n"$ETTELEM" sample --seconds 10 --reset-ms 1000\n')
        rc, res = self.audit(f)
        self.assertEqual(rc, A.EXIT_NOGO)
        self.assertEqual(self.cmds(res, "NO-GO"), ["SET_STATS_RUN_CONTROL"])
        rc, res = self.audit("--allow", "SET_STATS_RUN_CONTROL", f)
        self.assertEqual(rc, A.EXIT_GO)
        self.assertEqual(self.cmds(res, "ALLOWED WRITE"), ["SET_STATS_RUN_CONTROL"])

    def test_reset_ms_zero_is_no_reset(self):
        f = self.write("run.sh", 'ETTELEM=build/ettelem/ettelem\n"$ETTELEM" sample --seconds 10 --reset-ms 0\n')
        rc, res = self.audit(f)
        self.assertEqual(rc, A.EXIT_GO)
        self.assertNotIn("SET_STATS_RUN_CONTROL", self.cmds(res))

    def test_forwarded_args_may_carry_a_reset(self):
        f = self.write("lib.sh", 'ETTELEM=build/ettelem/ettelem\nstart() { "$ETTELEM" sample --seconds "$2" "$@" > x; }\n')
        rc, res = self.audit(f)
        self.assertEqual(rc, A.EXIT_NOGO)
        rec = [r for r in res["records"] if r["command"] == "SET_STATS_RUN_CONTROL"][0]
        self.assertTrue(rec["conditional"])

    def test_reset_passed_to_a_wrapper(self):
        f = self.write("run.sh", 'start_sampler "$OUT/tel" 1800 --reset-ms "$P_reset_ms"\n')
        rc, res = self.audit(f)
        self.assertEqual(rc, A.EXIT_NOGO)
        self.assertEqual(self.cmds(res), ["SET_STATS_RUN_CONTROL"])

    def test_variant_that_refuses_the_reset_sends_none(self):
        f = self.write("run.sh", 'ETT=build/ettelem-e118/ettelem\n"$ETT" sample --seconds 5 --reset-ms 1000\n')
        rc, res = self.audit(f)
        self.assertEqual(rc, A.EXIT_GO, res)
        self.assertNotIn("SET_STATS_RUN_CONTROL", self.cmds(res))
        self.assertNotIn("GET_ASIC_VOLTAGE", self.cmds(res))
        self.assertTrue(any("refuses" in n for n in res["notes"]))

    def test_unknown_variant_takes_the_union(self):
        f = self.write("run.sh", '"$SOMEBIN" sample --seconds 5  # no ettelem path known\nx=ettelem\n$x residency 2 3\n')
        rc, res = self.audit(f)
        self.assertIn("GET_MODULE_RESIDENCY_THROTTLE_STATES", self.cmds(res))

    def test_loglevel_is_a_write(self):
        f = self.write("run.sh", 'ETTELEM=build/ettelem-dv2/ettelem\n"$ETTELEM" loglevel info\n')
        rc, res = self.audit("--allow", "SET_STATS_RUN_CONTROL", f)
        self.assertEqual(rc, A.EXIT_NOGO)
        self.assertEqual(self.cmds(res, "NO-GO"), ["SET_DM_TRACE_CONFIG"])

    def test_residency_raw_4_to_6_is_no_go(self):
        f = self.write("run.sh", 'ETTELEM=build/ettelem-dv2/ettelem\nhold10 "$ETTELEM" residency 2 3 4 5 6 > r.jsonl\n')
        rc, res = self.audit(f)
        self.assertEqual(rc, A.EXIT_NOGO)
        rec = [r for r in res["records"] if r["command"] == "GET_MODULE_RESIDENCY_THROTTLE_STATES"][0]
        self.assertIn("SP_ERROR_LOG", rec["tags"])
        self.assertEqual(rec["cls"], "READ")

    def test_residency_2_3_is_go(self):
        f = self.write("run.py", 'ETT = "build/ettelem-dv2/ettelem"\nrun(["timeout", "10", ETT, "residency", "2", "3"])\n')
        rc, res = self.audit(f)
        self.assertEqual(rc, A.EXIT_GO, res)

    def test_residency_states_from_a_variable(self):
        f = self.write("run.py", 'self.ettelem = "build/ettelem-e77/ettelem"\n'
                                 'rc = self.tool("residency", *[str(x) for x in self.p["states"]])\n')
        rc, res = self.audit(f)
        self.assertEqual(rc, A.EXIT_NOGO)
        rec = [r for r in res["records"] if r["command"] == "GET_MODULE_RESIDENCY_THROTTLE_STATES"][0]
        self.assertIn("RESIDENCY_STATES_UNRESOLVED", rec["tags"])
        rc, res = self.audit("--allow", "RESIDENCY_STATES_UNRESOLVED", f)
        self.assertEqual(rc, A.EXIT_GO)

    def test_reviewed_exception_waives_one_finding_on_one_line(self):
        f = self.write("hpl.py", 'ETT = "build/ettelem-dv2/ettelem"\n'
                                 'run(["timeout", "10", ETT, "residency", "2", "3", "4", "5", "6"])\n'
                                 'run(["timeout", "10", ETT, "residency", "4"])\n')
        why = f"{f}:2:SP_ERROR_LOG=patched at run time to raw 2 3 (run_x.py:42)"
        rc, res = self.audit("--except", why, f)
        self.assertEqual(rc, A.EXIT_NOGO)  # line 3 is not excepted
        verdicts = {r["line"]: r["verdict"] for r in res["records"]}
        self.assertTrue(verdicts[2].startswith("EXCEPTED"), verdicts)
        self.assertTrue(verdicts[3].startswith("NO-GO"), verdicts)
        self.assertEqual(res["excepts"], [why])
        out, err = io.StringIO(), io.StringIO()
        with redirect_stdout(out), redirect_stderr(err):
            A.main(["--markdown", "--except", why, str(f)])
        self.assertIn("Excepted after review", out.getvalue())
        with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
            self.assertEqual(A.main(["--except", "no-line-number", str(f)]), A.EXIT_USAGE)

    def test_exception_by_command_name(self):
        f = self.write("g.sh", '/opt/et/bin/dev_mngt_service -m DM_CMD_GET_MODULE_FIRMWARE_REVISIONS -n 0\n')
        rc, _ = self.audit("--except", f"{f}:1:GET_MODULE_FIRMWARE_REVISIONS=unreachable: inside a function never called", f)
        self.assertEqual(rc, A.EXIT_GO)

    def test_dict_get_is_not_a_wrapper_call(self):
        f = self.write("run.py", 'ETT = "build/ettelem-e77/ettelem"\nx = q.get("residency")\nprint("config")\n')
        rc, res = self.audit(f)
        self.assertEqual(res["records"], [])

    def test_a_word_check_is_not_a_call(self):
        f = self.write("run.sh", 'ETT=build/ettelem-e84/ettelem\n'
                                 'for w in residency sptrace config sample; do grep -a -q -- "$w" "$ETT" && echo ok; done\n')
        rc, res = self.audit(f)
        self.assertEqual((rc, res["records"]), (A.EXIT_GO, []))

    def test_a_call_inside_a_quoted_command(self):
        f = self.write("remote.sh", '# runs the host ettelem build\nbin=$HOME/${DASH_SAMPLE_BIN:-}\n'
                                    'cmd="flock -n 9; exec timeout 10 nice -n 10 $bin sample --seconds 2 --every-ms 500"\n')
        rc, res = self.audit(f)
        self.assertEqual(rc, A.EXIT_GO)
        self.assertIn("GET_MODULE_VOLTAGE", self.cmds(res))  # an unknown binary: the union of the variants

    def test_deny_pmic_read(self):
        stock = self.write("a.sh", 'ETTELEM=build/ettelem/ettelem\n"$ETTELEM" config\n')
        rc, res = self.audit("--deny-pmic-read", stock)
        self.assertEqual(rc, A.EXIT_NOGO)
        self.assertEqual(self.cmds(res, "NO-GO"), ["GET_ASIC_VOLTAGE"])
        e77 = self.write("b.sh", 'ETTELEM=build/ettelem-e77/ettelem\n"$ETTELEM" config\n"$ETTELEM" sample --seconds 2\n')
        rc, res = self.audit("--deny-pmic-read", e77)
        self.assertEqual(rc, A.EXIT_GO, res)


class TestDevMngtService(Base):
    def test_revisions_query_by_name_is_a_pmic_write(self):
        f = self.write("gate.sh", 'DMS=/opt/et/bin/dev_mngt_service\n'
                                  'timeout 20 "$DMS" -m DM_CMD_GET_MODULE_FIRMWARE_REVISIONS -n 0 -u 5000\n')
        rc, res = self.audit("--allow", "SET_STATS_RUN_CONTROL", f)
        self.assertEqual(rc, A.EXIT_NOGO)
        rec = [r for r in res["records"] if r["command"] == "GET_MODULE_FIRMWARE_REVISIONS"][0]
        self.assertEqual((rec["cls"], rec["pmic"]), ("WRITE", "write"))

    def test_revisions_query_by_code(self):
        f = self.write("gate.sh", '/opt/et/bin/dev_mngt_service -o 14 -n 0\n/opt/et/bin/dev_mngt_service --code=33 -n 0\n')
        rc, res = self.audit(f)
        self.assertEqual(rc, A.EXIT_NOGO)
        self.assertEqual(self.cmds(res), ["GET_MODULE_FIRMWARE_REVISIONS", "GET_MODULE_POWER"])

    def test_code_from_a_variable_is_dynamic(self):
        f = self.write("gate.sh", 'DMS=/opt/et/bin/dev_mngt_service\n"$DMS" -o "$CODE" -n 0\n')
        rc, res = self.audit(f)
        self.assertEqual(rc, A.EXIT_NOGO)
        self.assertEqual(self.cmds(res), ["DYNAMIC"])

    def test_trace_operations(self):
        f = self.write("t.sh", 'DEVMNGT=/opt/et/bin/dev_mngt_service\n"$DEVMNGT" -n 0 -t SPST:extract\n'
                               '"$DEVMNGT" -n 0 -t SPST:enable; RESET_USED=\n"$DEVMNGT" -n 0 -t SP:disable,extract\n')
        rc, res = self.audit(f)
        self.assertEqual(rc, A.EXIT_NOGO)
        self.assertEqual(self.cmds(res, "NO-GO"), ["SET_DM_TRACE_RUN_CONTROL", "SET_STATS_RUN_CONTROL"])
        self.assertIn("TRACE_EXTRACT", self.cmds(res, "ok"))

    def test_wrapper_is_listed_for_a_person(self):
        f = self.write("w.py", 'DEVMNGT = "/opt/et/bin/dev_mngt_service"\n'
                               'def dm(cmd):\n    return run([DEVMNGT, "-m", cmd, "-n", "0"])\n'
                               'dm("DM_CMD_GET_VMIN_LUT")\n')
        rc, res = self.audit(f)
        self.assertEqual(rc, A.EXIT_GO)
        self.assertEqual(self.cmds(res), ["GET_VMIN_LUT", "WRAPPER"])

    def test_dynamic_name(self):
        f = self.write("w.py", 'name = "POWER"\ncmd = f"DM_CMD_GET_MODULE_{name}"\nother = "DM_CMD_" + name\n')
        rc, res = self.audit(f)
        self.assertEqual(rc, A.EXIT_NOGO)
        self.assertEqual(self.cmds(res), ["DYNAMIC"])

    def test_unknown_name_is_unclassified(self):
        f = self.write("w.sh", '/opt/et/bin/dev_mngt_service -m DM_CMD_GET_SOMETHING_NEW -n 0\n')
        rc, res = self.audit(f)
        self.assertEqual(rc, A.EXIT_NOGO)
        self.assertEqual(res["records"][0]["cls"], "UNCLASSIFIED")


class TestCommentsAndDocs(Base):
    def test_comments_and_docstrings_are_not_sends(self):
        f = self.write("r.py", '"""This runner never sends DM_CMD_GET_MODULE_FIRMWARE_REVISIONS nor\n'
                               'DM_CMD_SET_MODULE_STATIC_TDP_LEVEL."""\n'
                               '# not DM_CMD_RESET_ETSOC either\nx = 1  # nor ettelem loglevel debug\n')
        rc, res = self.audit(f)
        self.assertEqual((rc, res["records"]), (A.EXIT_GO, []))

    def test_cpp_comments(self):
        f = self.write("t.cpp", '// DM_CMD_SET_MODULE_VOLTAGE in a comment\n/* DM_CMD_RESET_ETSOC\n   still a comment */\n'
                                'int x = DM_CMD_GET_MODULE_POWER; // a real use\n')
        rc, res = self.audit(f)
        self.assertEqual(self.cmds(res), ["GET_MODULE_POWER"])

    def test_shell_hash_inside_quotes_is_not_a_comment(self):
        f = self.write("r.sh", 'echo "#" ; /opt/et/bin/dev_mngt_service -m DM_CMD_SET_MODULE_VOLTAGE -v 1\n')
        rc, res = self.audit(f)
        self.assertEqual(self.cmds(res), ["SET_MODULE_VOLTAGE"])

    def test_markdown_and_json_are_not_scanned(self):
        md = self.write("README.md", "Sends DM_CMD_GET_MODULE_FIRMWARE_REVISIONS.\n")
        js = self.write("p.json", '{"rule": "never DM_CMD_RESET_ETSOC"}\n')
        rc, res = self.audit(md, js)
        self.assertEqual((rc, res["records"]), (A.EXIT_GO, []))

    def test_continuation_lines_are_joined(self):
        f = self.write("r.sh", 'ETTELEM=build/ettelem/ettelem\n"$ETTELEM" sample \\\n  --seconds 5 \\\n  --reset-ms 500\n')
        rc, res = self.audit(f)
        self.assertIn("SET_STATS_RUN_CONTROL", self.cmds(res))
        f2 = self.write("r.py", 'ETT = "build/ettelem/ettelem"\nrun([ETT,\n     "sample",\n     "--reset-ms", "500"])\n')
        rc, res = self.audit(f2)
        self.assertIn("SET_STATS_RUN_CONTROL", self.cmds(res))


class TestRawAndHost(Base):
    def test_raw_ioctl_client_constants(self):
        f = self.write("c.py", 'PUSH_SQ = 1\nCMD_POWER, CMD_FW = 33, 14\nGET_SP_STATS = 60\n')
        rc, res = self.audit(f)
        self.assertEqual(rc, A.EXIT_NOGO)
        self.assertEqual(self.cmds(res), ["GET_MODULE_FIRMWARE_REVISIONS", "GET_MODULE_POWER", "GET_SP_STATS"])

    def test_raw_client_without_constants_is_dynamic(self):
        f = self.write("c.py", 'PUSH_SQ = 1\nsend(fd, PUSH_SQ, code)\n')
        rc, res = self.audit(f)
        self.assertEqual(self.cmds(res), ["DYNAMIC"])

    def test_host_writes(self):
        f = self.write("h.sh", 'echo 1 > /sys/bus/pci/devices/0000:01:00.0/reset\nsetpci -s 00:01.0 CAP_EXP+10.w=0020\n'
                               'setpci -s 00:01.0 CAP_EXP+30.w\nsudo modprobe -r et_soc1\nsudo reboot\n'
                               'et-reset 0\net-reset --dry-run 0\necho "do not reboot or et-reset"\n')
        rc, res = self.audit(f)
        self.assertEqual(rc, A.EXIT_NOGO)
        self.assertEqual(self.cmds(res), ["HOST_REBOOT", "MODULE_LOAD", "RESET_ETSOC", "SETPCI_WRITE", "SYSFS_WRITE"])
        lines = sorted(r["line"] for r in res["records"])
        self.assertEqual(lines, [1, 2, 4, 5, 6])


class TestReviewedSources(Base):
    def test_e118_source_is_taken_from_the_table(self):
        src = REPO / "tools/claims-v3/e118/ettelem-e118/ettelem.cpp"
        if not src.exists():
            self.skipTest("not in the lab repository")
        rc, res = self.audit(src)
        self.assertEqual(rc, A.EXIT_GO, res)  # its unreachable SET_DM_TRACE_CONFIG (:373) is not counted
        self.assertNotIn("SET_DM_TRACE_CONFIG", self.cmds(res))
        changed = self.write("ettelem.cpp", src.read_text() + "\n// edited\n")
        rc, res = self.audit(changed)
        self.assertEqual(rc, A.EXIT_NOGO)  # a changed copy is scanned, and the dead code then counts
        self.assertIn("SET_DM_TRACE_CONFIG", self.cmds(res, "NO-GO"))

    def test_e89_raw_client_is_unclassified(self):
        src = REPO / "tools/claims-v3/e89/pvt_sample.py"
        if not src.exists():
            self.skipTest("not in the lab repository")
        rc, res = self.audit(src)
        self.assertEqual(rc, A.EXIT_NOGO)
        self.assertEqual(self.cmds(res, "NO-GO"), ["GET_ASIC_PVT_SAMPLES"])

    def test_table_is_complete_against_the_enum(self):
        t = A.Table(A.DEFAULT_TABLE)
        ids = {c["id"] for c in t.commands.values()}
        self.assertEqual(ids, set(range(0, 75)) | set(range(128, 145)))
        for name, c in t.commands.items():
            self.assertIn(c["class"], ("READ", "WRITE", "UNSUPPORTED", "UNCLASSIFIED"), name)
            if c["class"] == "WRITE":
                self.assertTrue(c.get("reaches"), name)

    def test_real_gov_e72_sends_the_revisions_query(self):
        src = REPO / "tools/claims-v3/lq6/gov_e72.py"
        if not src.exists():
            self.skipTest("not in the lab repository")
        rc, res = self.audit(src)
        recs = [r for r in res["records"] if r["command"] == "GET_MODULE_FIRMWARE_REVISIONS"]
        self.assertEqual([r["line"] for r in recs], [156])

    def test_markdown_output(self):
        f = self.write("run.sh", 'ETTELEM=build/ettelem/ettelem\n"$ETTELEM" sample --seconds 1 --reset-ms 1000\n')
        out, err = io.StringIO(), io.StringIO()
        with redirect_stdout(out), redirect_stderr(err):
            rc = A.main(["--markdown", "--allow", "SET_STATS_RUN_CONTROL", str(f)])
        self.assertEqual(rc, A.EXIT_GO)
        self.assertIn("## Device commands sent", out.getvalue())
        self.assertIn("| `SET_STATS_RUN_CONTROL` | WRITE | write |", out.getvalue())

    def test_usage_errors(self):
        with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
            self.assertEqual(A.main([]), A.EXIT_USAGE)
            self.assertEqual(A.main([str(self.d / "missing.sh")]), A.EXIT_USAGE)
            self.assertEqual(A.main(["--allow", "NOT_A_COMMAND", str(self.write("x.sh", "true\n"))]), A.EXIT_USAGE)


if __name__ == "__main__":
    unittest.main()
