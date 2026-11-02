#!/usr/bin/env python3
"""Tests of dmcmd_audit.py (Q136(w), 2 Nov 2026; corrected after verification the same day). Stdlib only:
python3 tools/claims-v3/test_dmcmd_audit.py -v

Each test writes a small runner into a temporary directory and checks what the audit lists and its verdict. The last
tests read real files of this repository (skipped when run outside it). TestForms, TestVariants and TestWrappers are
the verifier's probes of 2 Nov: forms of SET_STATS_RUN_CONTROL that are not the ruled reset, ettelem builds outside
the reviewed ones, unknown subcommands, and wrappers that forward their arguments."""
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
        self.assertEqual(self.cmds(res, "NO-GO"), ["STATS_RESET"])
        rc, res = self.audit("--allow", "STATS_RESET", f)
        self.assertEqual(rc, A.EXIT_GO)
        self.assertEqual(self.cmds(res, "ALLOWED WRITE"), ["STATS_RESET"])
        rc, res = self.audit("--allow", "SET_STATS_RUN_CONTROL", f)  # the old token: read as STATS_RESET, and said so
        self.assertEqual(rc, A.EXIT_GO)
        self.assertEqual(res["allow"], ["STATS_RESET"])
        self.assertTrue(any("read as STATS_RESET" in n for n in res["notes"]))

    def test_reset_ms_zero_is_no_reset(self):
        f = self.write("run.sh", 'ETTELEM=build/ettelem/ettelem\n"$ETTELEM" sample --seconds 10 --reset-ms 0\n')
        rc, res = self.audit(f)
        self.assertEqual(rc, A.EXIT_GO)
        self.assertNotIn("STATS_RESET", self.cmds(res))

    def test_forwarded_args_may_carry_a_reset(self):
        f = self.write("lib.sh", 'ETTELEM=build/ettelem/ettelem\nstart() { "$ETTELEM" sample --seconds "$2" "$@" > x; }\n')
        rc, res = self.audit(f)
        self.assertEqual(rc, A.EXIT_NOGO)
        rec = [r for r in res["records"] if r["command"] == "STATS_RESET"][0]
        self.assertTrue(rec["conditional"])

    def test_reset_passed_to_a_wrapper(self):
        f = self.write("run.sh", 'start_sampler "$OUT/tel" 1800 --reset-ms "$P_reset_ms"\n')
        rc, res = self.audit(f)
        self.assertEqual(rc, A.EXIT_NOGO)
        self.assertEqual(self.cmds(res), ["STATS_RESET"])

    def test_variant_that_refuses_the_reset_sends_none(self):
        f = self.write("run.sh", 'ETT=build/ettelem-e118/ettelem\n"$ETT" sample --seconds 5 --reset-ms 1000\n')
        rc, res = self.audit(f)
        self.assertEqual(rc, A.EXIT_GO, res)
        self.assertNotIn("STATS_RESET", self.cmds(res))
        self.assertNotIn("GET_ASIC_VOLTAGE", self.cmds(res))
        self.assertTrue(any("refuses" in n for n in res["notes"]))

    def test_unknown_binary_lists_the_union_and_is_no_go(self):
        f = self.write("run.sh", '"$SOMEBIN" sample --seconds 5  # no ettelem path known\nx=ettelem\n$x residency 2 3\n')
        rc, res = self.audit(f)
        self.assertIn("GET_MODULE_RESIDENCY_THROTTLE_STATES", self.cmds(res))  # what it would send, if a reviewed build
        self.assertEqual(rc, A.EXIT_NOGO)  # but which build runs is not visible
        self.assertEqual(self.cmds(res, "NO-GO"), ["VARIANT_UNRESOLVED"])

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
        self.assertEqual(rc, A.EXIT_NOGO)  # $bin is set at run time: the build is not visible
        self.assertIn("GET_MODULE_VOLTAGE", self.cmds(res))  # an unknown binary: the union of the variants, listed
        self.assertEqual(self.cmds(res, "NO-GO"), ["VARIANT_UNRESOLVED"])
        stock = REPO / "tools/ettelem/ettelem.cpp"
        if stock.exists():  # the runner names the source its binary was built from, and the hash matches
            rc, res = self.audit("--variant-source", f"unresolved={stock}", f)
            self.assertEqual(rc, A.EXIT_GO, res)

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
        rc, res = self.audit("--allow", "STATS_RESET", f)
        self.assertEqual(rc, A.EXIT_NOGO)
        self.assertEqual(self.cmds(res, "NO-GO"), ["SET_DM_TRACE_RUN_CONTROL", "SPST_TRACE_CONTROL"])
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
        self.assertIn("STATS_RESET", self.cmds(res))
        f2 = self.write("r.py", 'ETT = "build/ettelem/ettelem"\nrun([ETT,\n     "sample",\n     "--reset-ms", "500"])\n')
        rc, res = self.audit(f2)
        self.assertIn("STATS_RESET", self.cmds(res))


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


class TestForms(Base):
    """SET_STATS_RUN_CONTROL's forms: only the ruled statistics reset (type 1, control 2) is STATS_RESET."""

    def test_dev_mngt_service_stats_forms_are_not_the_ruled_reset(self):
        cases = {"a_spst_enable.sh": ('DEVMNGT=/opt/et/bin/dev_mngt_service\n"$DEVMNGT" -n 0 -t SPST:enable\n',
                                      "SPST_TRACE_CONTROL", "control 1"),
                 "b_spst_reset.sh": ('/opt/et/bin/dev_mngt_service -n 0 -t SPST:reset\n', "SPST_RESET", "control 7"),
                 "b2_spst_reset_off.sh": ('/opt/et/bin/dev_mngt_service -n 0 -t SPST:disable,reset\n', "SPST_RESET",
                                          "control 6"),
                 "c_mmst_reset.sh": ('/opt/et/bin/dev_mngt_service -n 0 -t MMST:reset\n', "MMST_CONTROL", "type 2"),
                 "d_spst_off.sh": ('/opt/et/bin/dev_mngt_service -n 0 -t SPST:disable\n', "SPST_TRACE_CONTROL",
                                   "control 0")}
        for name, (text, form, ctl) in cases.items():
            f = self.write(name, text)
            for token in ("STATS_RESET", "SET_STATS_RUN_CONTROL"):
                rc, res = self.audit("--allow", token, f)
                self.assertEqual(rc, A.EXIT_NOGO, (name, token))
                self.assertEqual(self.cmds(res, "NO-GO"), [form], name)
            self.assertIn(ctl, res["records"][0]["detail"], name)

    def test_operations_after_a_comma_are_read(self):
        f = self.write("x.sh", '/opt/et/bin/dev_mngt_service -n 0 -t SPST:extract,reset\n'
                               '/opt/et/bin/dev_mngt_service -n 0 -t SP:disable,extract\n')
        rc, res = self.audit(f)
        self.assertEqual(rc, A.EXIT_NOGO)
        got = {(r["line"], r["command"]) for r in res["records"]}
        self.assertEqual(got, {(1, "TRACE_EXTRACT"), (1, "SPST_RESET"), (2, "SET_DM_TRACE_RUN_CONTROL"),
                               (2, "TRACE_EXTRACT")})

    def test_extract_alone_is_a_read(self):
        f = self.write("x.sh", '/opt/et/bin/dev_mngt_service -n 0 -t SPST:extract\n/opt/et/bin/dev_mngt_service -n 0 -t MM:enable\n')
        rc, res = self.audit(f)
        self.assertEqual((rc, self.cmds(res)), (A.EXIT_GO, ["TRACE_EXTRACT"]))  # MM takes no control: nothing sent

    def test_a_form_the_checker_cannot_see_is_never_allowed(self):
        f = self.write("x.sh", '/opt/et/bin/dev_mngt_service -n 0 -o 62\n'
                               '/opt/et/bin/dev_mngt_service -n 0 -m DM_CMD_SET_STATS_RUN_CONTROL\n')
        rc, res = self.audit("--allow", "STATS_RESET", f)
        self.assertEqual(rc, A.EXIT_NOGO)
        self.assertEqual(self.cmds(res, "NO-GO"), ["SET_STATS_RUN_CONTROL"])
        self.assertTrue(all("not provably the ruled statistics reset" in r["verdict"] for r in res["records"]))

    def test_reviewed_variant_source_resets_as_the_ruled_form(self):
        src = REPO / "tools/ettelem/ettelem.cpp"
        if not src.exists():
            self.skipTest("not in the lab repository")
        rc, res = self.audit("--allow", "STATS_RESET", src)
        self.assertEqual(self.cmds(res, "ALLOWED WRITE"), ["STATS_RESET"])  # its --reset-ms is the ruled form
        self.assertEqual(self.cmds(res, "NO-GO"), ["SET_DM_TRACE_CONFIG"])  # its loglevel is a write


class TestVariants(Base):
    """An ettelem binary outside the reviewed builds, or a subcommand a reviewed build lacks, is NO-GO."""

    def test_new_build_dir_is_unreviewed(self):  # the verifier's k_newvariant.sh
        f = self.write("k.sh", '#!/bin/bash\nbuild/ettelem-e999/ettelem tdp 0\nbuild/ettelem-e999/ettelem threshold set 70\n'
                               'build/ettelem-e999/ettelem fwver\n')
        rc, res = self.audit("--allow", "STATS_RESET", f)
        self.assertEqual(rc, A.EXIT_NOGO)
        lines = sorted(r["line"] for r in res["records"] if r["command"] == "UNREVIEWED_VARIANT")
        self.assertEqual(lines, [2, 3, 4])
        self.assertNotIn("GET_MODULE_TEMPERATURE_THRESHOLDS", self.cmds(res))  # no reviewed meaning is lent to it

    def test_new_build_dir_in_python(self):  # the verifier's l_newvariant.py and o_py_attr.py
        f = self.write("l.py", 'import subprocess\nET = "build/ettelem-e999/ettelem"\nsubprocess.run([ET, "setfreq", "800"])\n')
        rc, res = self.audit(f)
        self.assertEqual((rc, self.cmds(res, "NO-GO")), (A.EXIT_NOGO, ["UNREVIEWED_VARIANT"]))
        g = self.write("o.py", 'import subprocess\nclass R:\n    def __init__(s): s.ettelem = "build/ettelem-x/ettelem"\n'
                               '    def go(s): subprocess.run([s.ettelem, "loglevel", "info"])\n')
        rc, res = self.audit(g)
        self.assertEqual(rc, A.EXIT_NOGO)
        self.assertIn("UNREVIEWED_VARIANT", self.cmds(res, "NO-GO"))

    def test_unknown_subcommand_of_a_reviewed_build(self):  # the verifier's i_unknown_sub.sh
        f = self.write("i.sh", '#!/bin/bash\nbuild/ettelem/ettelem tdp 0\n')
        rc, res = self.audit(f)
        self.assertEqual((rc, self.cmds(res, "NO-GO")), (A.EXIT_NOGO, ["UNKNOWN_SUBCOMMAND"]))
        g = self.write("j.sh", 'ETTELEM=build/ettelem/ettelem\n"$ETTELEM" residency 2 3\n')  # stock has no residency
        rc, res = self.audit(g)
        self.assertEqual((rc, self.cmds(res, "NO-GO")), (A.EXIT_NOGO, ["UNKNOWN_SUBCOMMAND"]))

    def test_the_hpl_build_is_dv2s(self):
        f = self.write("h.py", 'ETT = os.path.join(root, "build/ettelem-hpl/ettelem")\nrun([ETT, "residency", "2", "3"])\n')
        rc, res = self.audit(f)
        self.assertEqual(rc, A.EXIT_GO, res)
        self.assertIn("variant ettelem-dv2", res["records"][0]["detail"])

    def test_variant_source_binds_a_build_dir_by_hash(self):
        dv2 = REPO / "tools/claims-v3/dv2/ettelem-dv2/ettelem.cpp"
        if not dv2.exists():
            self.skipTest("not in the lab repository")
        f = self.write("v.sh", 'ETT=build/ettelem-e999/ettelem\n"$ETT" residency 2 3\n"$ETT" config\n')
        rc, res = self.audit(f)
        self.assertEqual((rc, self.cmds(res, "NO-GO")), (A.EXIT_NOGO, ["UNREVIEWED_VARIANT"]))
        rc, res = self.audit("--variant-source", f"build/ettelem-e999/={dv2}", f)
        self.assertEqual(rc, A.EXIT_GO, res)
        self.assertEqual(res["variant_sources"], {"ettelem-e999": "ettelem-dv2"})
        other = self.write("changed.cpp", dv2.read_text() + "\n// edited\n")
        rc, res = self.audit("--variant-source", f"build/ettelem-e999/={other}", f)
        self.assertEqual(rc, A.EXIT_NOGO)  # a source that matches no reviewed variant binds nothing
        self.assertTrue(any("matches no reviewed variant" in n for n in res["notes"]))
        g = self.write("w.sh", 'ETT=build/ettelem-e999/ettelem\n"$ETT" tdp 0\n')
        rc, res = self.audit("--variant-source", f"build/ettelem-e999/={dv2}", g)
        self.assertEqual((rc, self.cmds(res, "NO-GO")), (A.EXIT_NOGO, ["UNKNOWN_SUBCOMMAND"]))

    def test_two_calls_on_one_line_are_both_classified(self):
        f = self.write("t.sh", 'ETT=build/ettelem-dv2/ettelem\n"$ETT" config > c.json; "$ETT" loglevel info\n')
        rc, res = self.audit(f)
        self.assertEqual(rc, A.EXIT_NOGO)
        self.assertIn("GET_MODULE_STATIC_TDP_LEVEL", self.cmds(res))
        self.assertEqual(self.cmds(res, "NO-GO"), ["SET_DM_TRACE_CONFIG"])

    def test_file_handling_and_prose_are_not_calls(self):
        f = self.write("p.py", 'ETT = "build/ettelem/ettelem"\nblob = open(ETT, "rb").read()\nok = os.path.isfile(ETT)\n'
                               'log("ettelem builds differ")\nlabels = [("ettelem", ETT)]\n')
        g = self.write("p.sh", 'ETT=build/ettelem/ettelem\n[ -x "$ETT" ] || die "no ettelem build"\nsha256sum "$ETT" x\n'
                               'echo "ettelem refused: bad args"\n')
        rc, res = self.audit(f, g)
        self.assertEqual((rc, res["records"]), (A.EXIT_GO, []))

    def test_variable_from_a_sourced_file(self):
        self.write("lib.sh", 'ETTELEM=build/ettelem/ettelem\n')
        self.write("dv2lib.sh", 'ETTELEM=${DV2_ETTELEM:-build/ettelem-dv2/ettelem}\n')
        b = self.write("x/block.sh", '. "$(dirname "${BASH_SOURCE[0]}")/../lib.sh"\n. "$(dirname "${BASH_SOURCE[0]}")/../dv2lib.sh"\n'
                                     '"$ETTELEM" residency 2 3\n')
        rc, res = self.audit(self.d / "lib.sh", self.d / "dv2lib.sh", b)
        self.assertEqual(rc, A.EXIT_GO, res)  # the last sourced file that sets ETTELEM wins: dv2, which has residency


class TestWrappers(Base):
    """Arguments forwarded to ettelem: the wrapper is listed, and its calls are classified through it."""

    def test_shell_function_wrapper(self):  # the shape of tools/claims-v3/dv2/z2.sh
        f = self.write("z.sh", 'ETT=build/ettelem-dv2/ettelem\nrun() {   # run <name> <out> <args...>\n'
                               '  local name=$1 out=$2; shift 2\n  timeout 10 "$ETT" "$@" > "$out"\n}\n'
                               'run uptime "$OUT/uptime.jsonl" uptime\nrun residency "$OUT/r.jsonl" residency 2 3 4 5 6\n')
        rc, res = self.audit(f)
        self.assertEqual(rc, A.EXIT_NOGO)
        self.assertIn("WRAPPER", self.cmds(res))
        rec = [r for r in res["records"] if r["command"] == "GET_MODULE_RESIDENCY_THROTTLE_STATES"]
        self.assertEqual([r["line"] for r in rec], [7])
        self.assertIn("SP_ERROR_LOG", rec[0]["tags"])
        self.assertIn("GET_MODULE_UPTIME", self.cmds(res, "ok"))

    def test_python_wrapper_with_an_unknown_subcommand(self):  # the verifier's n_py_wrapper.py, with a new word
        f = self.write("n.py", 'import subprocess\nTOOL = "/srv/tree/build/ettelem-hpl/ettelem"\n'
                               'def tool(*a):\n    return subprocess.run([TOOL, *a])\ntool("loglevel", "info")\n'
                               'tool("setfreq", "800")\ntool("config")\n')
        rc, res = self.audit(f)
        self.assertEqual(rc, A.EXIT_NOGO)
        nogo = {(r["line"], r["command"]) for r in res["records"] if r["verdict"].startswith("NO-GO")}
        self.assertEqual(nogo, {(5, "SET_DM_TRACE_CONFIG"), (6, "UNKNOWN_SUBCOMMAND")})
        self.assertIn("GET_MODULE_STATIC_TDP_LEVEL", self.cmds(res, "ok"))

    def test_a_scanned_guard_program_is_classified_at_its_own_lines(self):  # E128's ettelem_guard.sh shape
        guard = self.write("ettelem_guard.sh", '#!/usr/bin/env bash\nREAL=build/ettelem/ettelem\ncase "${1:-}" in\n'
                                               '  config) exec "$REAL" config ;;\n  sample) shift; exec "$REAL" sample --seconds 2 ;;\n'
                                               '  *) exit 97 ;;\nesac\n')
        block = self.write("block.sh", f'ETTELEM={guard}\n"$ETTELEM" config\n"$ETTELEM" loglevel info\n')
        rc, res = self.audit(block, guard)
        self.assertEqual(rc, A.EXIT_GO, res)  # the guard sends config and sample only, as its own lines show
        self.assertEqual({r["file"] for r in res["records"]}, {str(guard)})
        rc, res = self.audit(block)  # without the guard among the files, what it runs is not visible
        self.assertEqual(rc, A.EXIT_NOGO)
        self.assertIn("VARIANT_UNRESOLVED", self.cmds(res, "NO-GO"))


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
            rc = A.main(["--markdown", "--allow", "STATS_RESET", str(f)])
        self.assertEqual(rc, A.EXIT_GO)
        self.assertIn("## Device commands sent", out.getvalue())
        self.assertIn("| `STATS_RESET` | WRITE | write |", out.getvalue())

    def test_usage_errors(self):
        with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
            self.assertEqual(A.main([]), A.EXIT_USAGE)
            self.assertEqual(A.main([str(self.d / "missing.sh")]), A.EXIT_USAGE)
            self.assertEqual(A.main(["--allow", "NOT_A_COMMAND", str(self.write("x.sh", "true\n"))]), A.EXIT_USAGE)
            for never in A.NEVER_ALLOW:  # an unreviewed build or subcommand is never cleared by --allow
                self.assertEqual(A.main(["--allow", never, str(self.d / "x.sh")]), A.EXIT_USAGE)
            self.assertEqual(A.main(["--variant-source", "nokey", str(self.d / "x.sh")]), A.EXIT_USAGE)
            self.assertEqual(A.main(["--variant-source", "unresolved=" + str(self.d / "missing.cpp"),
                                     str(self.d / "x.sh")]), A.EXIT_USAGE)

    def test_files_from(self):
        a = self.write("a.sh", 'ETTELEM=build/ettelem/ettelem\n"$ETTELEM" config\n')
        lst = self.write("list.txt", f"{a}\n\n")
        rc, res = self.audit("--files-from", lst)
        self.assertEqual((rc, res["files"]), (A.EXIT_GO, [str(a)]))


if __name__ == "__main__":
    unittest.main()
