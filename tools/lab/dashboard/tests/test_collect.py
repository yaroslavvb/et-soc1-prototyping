#!/usr/bin/env python3
"""Unit tests of the lab dashboard's collector (collect.py) and the probe's process filter (remote.sh). Standard library
only, no host is contacted:

    python3 tools/lab/dashboard/tests/test_collect.py        (LAB_DASH_TEST_DIR: where scratch files go)

They pin the fixes of 30 September 2026's reviews: render.py never refuses what the collector wrote; ssh's keepalive
timeout is a timeout; a machine's DOWN time is its own; a reboot after an outage is not "planned"; the approval
back-off never hides another failure; people's status, "doing" and holds come from machines that answered; a terminal
logs a person in, a seconds-old session with no terminal does not; lingering user managers are not people; the headline
names a machine that is not up and never counts old data; the fingerprint ignores ssh wording and idle crossings; the
current history slot is the latest run; login colours stay with their logins; et-usage's final format (a lost end, lock
hints, a pause, a cut log, a busy log's cut lists) maps onto the page's fields."""
import argparse
import importlib.util
import json
import os
import re
import subprocess
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
DASH = os.path.dirname(HERE)
os.environ.setdefault("LAB_DASH_CONFIG", os.path.join(HERE, "no-config"))  # never the real config.json


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


C = load("collect", os.path.join(DASH, "collect.py"))
R = load("render", os.path.join(DASH, "page", "render.py"))
WORK = os.environ.get("LAB_DASH_TEST_DIR") or tempfile.mkdtemp(prefix="labdash-test-")
os.makedirs(WORK, exist_ok=True)


def bare(now=1790800000.0, out=None):
    """A Collector without a run: the state and settings the methods under test read."""
    col = C.Collector.__new__(C.Collector)
    col.args = argparse.Namespace(from_raw=None, sample_dry=False, no_backoff=False, quiet=True, card_sample=False,
                                  health=False, hosts=None, now=None, owner="owner")
    col.now = now
    col.t_wall = now
    with open(os.path.join(DASH, "lab.json")) as f:
        col.lab = json.load(f)
    col.out = out or tempfile.mkdtemp(dir=WORK)
    col.config, col.acks, col.known = {}, {}, {}
    col.state = {"hosts": {}, "cards": {}, "alerts_since": {}}
    col.owner, col.maintainer, col.visibility = "owner", "owner", "public"
    col.priv = C.Privacy("owner")
    col.errors = []
    col.this_host = "aifoundry2"
    col.tailscale = {}
    col.alerts = {}
    col.sample_enabled = False
    col.sample_plan = {}
    col.nodewatch_buckets = {}
    col.prev_run_ms = None
    return col


class Privacy(unittest.TestCase):
    STRINGS = ["01.1.1.1", "1.1.1.01", "prog 10.0.0.7 x", "see http:// here", "x@1abc.com", "a_.ts.net",
               "login.tailscale.com/a/xyz", "user@example.org", "fe80::1", "https://a.b/c"]

    def test_render_never_refuses_a_scrubbed_string(self):
        pr = C.Privacy("owner")
        for s in self.STRINGS:
            out = pr.scrub(s)
            self.assertEqual(R.privacy_check({"x": out}), [], "%r scrubbed to %r, which render.py refuses" % (s, out))
            self.assertEqual(pr.check({"x": out}), [], "%r scrubbed to %r, which collect.py refuses" % (s, out))

    def test_collect_checks_what_render_checks(self):
        pr = C.Privacy("owner")
        for s in self.STRINGS:
            if R.privacy_check({"x": s}):
                self.assertTrue(pr.check({"x": s}), "%r: render.py refuses it, collect.py's check does not" % s)

    def test_program_names_pass(self):
        col = bare()
        self.assertEqual(col.prog("01.1.1.1"), "<ipv4>")
        self.assertEqual(R.privacy_check({"p": col.programs({"01.1.1.1": 2, "sgemm_host": 1})}), [])

    def test_units_are_not_addresses(self):
        pr = C.Privacy("owner")
        for u in ("apport-coredump-hook@3-2211-1000.service", "getty@tty1.service", "user@1000.service"):
            self.assertEqual(pr.check({"u": u}), [], u)
            self.assertEqual(R.privacy_check({"u": u}), [], u)


class Ssh(unittest.TestCase):
    def test_keepalive_is_a_timeout(self):
        self.assertEqual(C.classify_ssh_error("Timeout, server aifoundry1 not responding.\r\n", 255), "timeout")
        self.assertEqual(C.classify_ssh_error("ssh: connect to host x port 22: Connection timed out", 255), "timeout")
        self.assertEqual(C.classify_ssh_error("ssh: connect to host x port 22: No route to host", 255), "unreachable")


class Liveness(unittest.TestCase):
    def run_states(self, steps):
        """steps: [(now, fresh, err, ts)] with ts None or (online, last_seen_ms); returns the host state after each"""
        col, hs, out = bare(), {}, []
        for now, fresh, err, ts in steps:
            col.now = now
            col.tailscale = {"aifoundry1": {"online": ts[0], "last_seen_ms": ts[1], "self": False}} if ts else {}
            if fresh:
                hs["last_ok_ms"] = C.ms(now)
            col.liveness("aifoundry1", hs, fresh, err, False)
            out.append(dict(hs))
        return out

    def test_down_since_is_tailscale_last_seen_not_the_approval(self):
        t = 1790800000.0
        st = self.run_states([(t, True, None, (True, None)),
                              (t + 600, False, "approval needed", (True, None)),
                              (t + 1200, False, "timeout", (False, C.ms(t + 1000)))])
        self.assertEqual(st[1]["state"], "approval needed")
        self.assertEqual(st[2]["state"], "down")
        self.assertEqual(st[2]["down_since_ms"], C.ms(t + 1000))

    def test_unreachable_after_an_approval_starts_then(self):
        t = 1790800000.0
        st = self.run_states([(t, True, None, None), (t + 600, False, "approval needed", (True, None)),
                              (t + 1200, False, "timeout", (True, None))])
        self.assertEqual(st[2]["state"], "unreachable")
        self.assertEqual(st[2]["down_since_ms"], C.ms(t + 1200))

    def test_no_tailscale_view_is_not_kept(self):
        t = 1790800000.0
        st = self.run_states([(t, False, "timeout", (True, None)), (t + 600, False, "timeout", None)])
        self.assertIsNotNone(st[0]["tailscale"])
        self.assertIsNone(st[1]["tailscale"])


class Backoff(unittest.TestCase):
    def test_another_failure_clears_the_approval_backoff(self):
        col = bare()
        hs = col.state["hosts"].setdefault("aifoundry3", {})
        col.build({"aifoundry3": ("", "approval needed", 100, False)})
        self.assertGreater(hs["next_try_ms"], C.ms(col.now))  # tried again in an hour
        col.now += 60
        col.build({"aifoundry3": ("", "timeout", 8000, False)})  # update.sh now (--no-backoff): a timeout
        self.assertIsNone(hs["next_try_ms"])  # so the next cron run probes it, and shows it unreachable
        self.assertEqual(hs["state"], "unreachable")


class Reboot(unittest.TestCase):
    def test_after_an_outage_is_not_planned(self):
        col = bare()
        hs = {"boot_id": "a" * 36, "last_ok_ms": C.ms(col.now - 1800), "state": "down",
              "down_since_ms": C.ms(col.now - 1700), "block": {"kernel": {"reboot_pending": True}}}
        col.detect_reboot("aifoundry1", hs, {"uptime_s": 120.0, "boot": "b" * 36})
        self.assertFalse(hs["reboot"]["planned"])
        self.assertEqual(hs["reboot"]["after"]["state"], "down")

    def test_pending_and_answering_is_planned(self):
        col = bare()
        hs = {"boot_id": "a" * 36, "last_ok_ms": C.ms(col.now - 600), "state": "up",
              "block": {"kernel": {"reboot_pending": True}}}
        col.detect_reboot("aifoundry1", hs, {"uptime_s": 120.0, "boot": "b" * 36})
        self.assertTrue(hs["reboot"]["planned"])
        self.assertIsNone(hs["reboot"]["after"])

    def test_first_run_records_a_recent_boot(self):
        col = bare()
        hs = {}
        col.detect_reboot("aifoundry1", hs, {"uptime_s": 1800.0, "boot": "c" * 36})
        self.assertIsNone(hs["reboot"]["planned"])
        self.assertEqual(hs["reboot"]["at_ms"], C.ms(col.now - 1800))
        again = dict(hs["reboot"])
        col.now += 600
        col.detect_reboot("aifoundry1", hs, {"uptime_s": 2400.0, "boot": "c" * 36})
        self.assertEqual(hs["reboot"], again)  # the same boot is recorded once

    def test_long_uptime_records_nothing(self):
        col, hs = bare(), {}
        col.detect_reboot("aifoundry1", hs, {"uptime_s": 5 * 86400.0, "boot": "c" * 36})
        self.assertNotIn("reboot", hs)


class People(unittest.TestCase):
    def secs(self, sessions, pts=(), procs=()):
        return {"sessions": [json.dumps(sessions)], "pts": list(pts), "procs": list(procs)}

    def test_terminal_without_session_logs_in(self):
        people, _, _ = C.p_people(self.secs([], ["1019 alice 1790799700"], ["procs 1019 alice 12 0 shell,agent"]),
                                  {"now": 1790800000}, 1790800000)
        e = people["alice"]
        self.assertEqual(bare().person_status(e), "active")  # a terminal used 5 min ago
        self.assertEqual(C.doing_of(e), ["agent"])

    def test_brief_session_without_terminal(self):
        s = [{"session": "c9", "uid": 1019, "user": "bob", "tty": None, "state": "active"}]
        people, _, _ = C.p_people(self.secs(s, [], ["procs 1019 bob 2 0 -", "sessage c9 4"]), {"now": 1790800000},
                                  1790800000)
        self.assertEqual(people["bob"]["sessions"], 0)
        self.assertEqual(bare().person_status(people["bob"]), "processes only")
        people, _, _ = C.p_people(self.secs(s, [], ["procs 1019 bob 2 0 -", "sessage c9 400"]), {"now": 1790800000},
                                  1790800000)
        self.assertEqual(bare().person_status(people["bob"]), "active")

    def test_doing_shell_and_other(self):
        self.assertEqual(C.doing_of({"doing": [], "shell": True}), ["shell"])
        self.assertEqual(C.doing_of({"doing": [], "shell": False}), ["other"])
        self.assertEqual(C.doing_of({"doing": []}), ["shell"])  # an entry from before shells were reported
        self.assertIsNone(C.doing_of({"doing": None}))

    def test_a_machine_that_did_not_answer_never_makes_status_current(self):
        col = bare()
        hosts = {"aifoundry1": {"reachable": False}, "aifoundry2": {"reachable": True}}
        hp = {"aifoundry1": {"alice": {"sessions": 1, "ttys": 1, "idle_min": 1, "procs": 9, "doing": ["build"],
                                       "shell": True, "notty_sessions": 0, "closing": 0}},
              "aifoundry2": {"bob": {"sessions": 0, "ttys": 1, "idle_min": 50, "procs": 3, "doing": [], "shell": True,
                                     "notty_sessions": 0, "closing": 0}}}
        cards = {"aifoundry1-c1": {"host": "aifoundry1", "stale": True,
                                   "holder": {"who": [{"login": "alice", "node": "/dev/et1_ops", "etime_s": 60}]}}}
        ppl = {p["login"]: p for p in col.people_view(hp, hosts, cards, {"cards": {}})}
        self.assertEqual(ppl["alice"]["status"], "unknown")
        self.assertIsNone(ppl["alice"]["doing"])
        self.assertTrue(ppl["alice"]["card_holds"][0]["stale"])
        self.assertEqual(ppl["bob"]["status"], "idle")
        self.assertEqual(ppl["bob"]["doing"], ["shell"])


class Probe(unittest.TestCase):
    """remote.sh's @@procs awk on invented ps lines (pid sid uid etimes user cgroup comm)."""

    def awk(self, lines):
        with open(os.path.join(DASH, "remote.sh")) as f:
            src = f.read()
        m = re.search(r"t 10 ps -eo pid=,sid=,uid=,etimes=,user:32=,cgroup:512=,comm= \| awk (.*?) '\n(.*?)'\n", src, re.S)
        self.assertIsNotNone(m, "the procs pipeline in remote.sh")
        prog = m.group(2)
        dev = re.search(r"^DEV_COMM='([^']*)'", src, re.M).group(1)
        r = subprocess.run(["awk", "-v", "s=c1", "-v", "sid=999", "-v", "anc= 1 ", "-v", "re=" + dev, prog],
                           input="\n".join(lines) + "\n", capture_output=True, text=True, check=True)
        return r.stdout.split("\n")

    def test_lingering_user_manager_is_not_a_person(self):
        u = "0::/user.slice/user-1045.slice/user@1045.service"
        out = self.awk([
            "10 10 1045 900 m45 %s/init.scope systemd" % u,
            "11 11 1045 900 m45 %s/init.scope (sd-pam)" % u,
            "12 12 1045 900 m45 %s/session.slice/pipewire.service pipewire" % u,
            "13 13 1045 900 m45 %s/app.slice/snap.snapd-desktop-integration.snapd-desktop-integration.service user-session-he" % u,
            "20 20 1019 900 alice 0::/user.slice/user-1019.slice/user@1019.service/app.slice/snap.tmux.tmux-1.scope tmux: server",
            "21 21 1019 900 alice 0::/user.slice/user-1019.slice/user@1019.service/app.slice/snap.tmux.tmux-1.scope bash",
            "22 21 1019 900 alice 0::/user.slice/user-1019.slice/user@1019.service/app.slice/snap.tmux.tmux-1.scope claude",
            "30 30 1020 5 bob 0::/user.slice/user-1020.slice/session-c7.scope scp",
            "31 31 1022 0 dan 0::/user.slice/user-1022.slice/session-c8.scope rsync",
            "40 40 1021 900 carol 0::/user.slice/user-1021.slice/user@1021.service/app.slice/run-x.service sgemm_host",
        ])
        procs = {ln.split()[2]: ln.split() for ln in out if ln.startswith("procs ")}
        self.assertNotIn("m45", procs)
        self.assertEqual(procs["alice"][3:], ["3", "0", "shell,agent"])
        self.assertIn("sessage c7 5", out)
        self.assertIn("sessage c8 0", out)  # a session seconds old is reported, with age 0
        self.assertEqual(procs["carol"][3:5], ["1", "1"])  # a device process counts wherever it runs


class Status(unittest.TestCase):
    def alert(self, aid, level, scope, title, host=None, stale=False):
        return {"id": aid, "level": level, "scope": scope, "host": host, "card": None, "title": title, "known": None,
                "ack": None, "stale": stale}

    def test_headline_names_a_machine_that_is_not_up(self):
        st = bare().status_view([self.alert("a", "bad", "host", "/home 99% used", "aifoundry1"),
                                 self.alert("b", "warn", "host-down", "aifoundry3: approval needed", "aifoundry3"),
                                 self.alert("c", "warn", "host", "1 failed unit(s)", "aifoundry2")])
        self.assertIn("aifoundry3: approval needed", st["headline"])
        self.assertTrue(st["headline"].startswith("1 problem: aifoundry1 /home 99% used; 2 warnings"))

    def test_old_data_is_not_counted(self):
        st = bare().status_view([self.alert("a", "bad", "host-down", "aifoundry1 DOWN since 14:41", "aifoundry1"),
                                 self.alert("b", "bad", "host", "/home 99% used", "aifoundry1", stale=True)])
        self.assertEqual(st["counts"]["bad"], 1)
        self.assertEqual(st["counts"]["old"], 1)
        self.assertNotIn("/home", st["headline"])


class Fingerprint(unittest.TestCase):
    def data(self, err, status):
        return {"hosts": {"aifoundry1": {"reachable": False, "state": "down", "error": err}},
                "cards": {}, "usage": {}, "alerts": [], "collector": {"halted": None},
                "people": [{"login": "alice", "status": status,
                            "hosts": {"aifoundry2": {"sessions": 1, "ttys": 1}}}]}

    def test_ignores_ssh_wording_and_idle_crossings(self):
        col = bare()
        a = col.fingerprint(self.data("timeout", "active"))
        self.assertEqual(a, col.fingerprint(self.data("unreachable", "active")))
        self.assertEqual(a, col.fingerprint(self.data("timeout", "idle")))


class History(unittest.TestCase):
    def test_current_slot_is_the_latest_run(self):
        col = bare(now=1790800000.0)
        col.append_history({"t": int(col.now) - 120, "h": {"aifoundry1": {"up": 1, "warn": 0}}, "c": {}})
        h = col.history_view({"t": int(col.now), "h": {"aifoundry1": {"up": 3, "warn": 0}}, "c": {}})
        self.assertEqual(h["hosts"]["aifoundry1"]["up"][-1], 3)


class Colors(unittest.TestCase):
    def usage(self, users):
        return {"cards": {"aifoundry2": {"users": {u: {"held_s": s} for u, s in users.items()}, "now": [], "daily": []}}}

    def test_a_colour_stays_with_its_login(self):
        col = bare()
        a = col.login_colors(self.usage({"alice": 10, "bob": 5}), {}, {"cards": {}})
        b = col.login_colors(self.usage({"alice": 10, "bob": 5, "aaron": 500, "carl": 50}), {}, {"cards": {}})
        self.assertEqual(a["alice"], b["alice"])
        self.assertEqual(a["bob"], b["bob"])
        self.assertEqual(len(set(b.values())), 3)
        self.assertEqual(len(b), 3)  # three slots; the fourth login is "others"
        c = col.login_colors(self.usage({"dana": 1}), {}, {"cards": {}})  # a new login takes an absent login's slot
        self.assertIn("dana", c)


class Usage(unittest.TestCase):
    """et-usage's final format (v 1 with the review fixes), from the testdata's real et-usage --json output
    (testdata/make_usage.py) and, for the fields only a very busy log makes, a hand-made answer."""

    def block(self, path, host, now):
        with open(os.path.join(DASH, "testdata", path)) as f:
            up = C.p_usage(C.sections(f.read())["usage"])
        col = bare(now=now)
        return col, col.usage_block(host, up)

    def test_lost_end_and_lock_hints(self):
        col, u = self.block("run3/raw-aifoundry1.txt", "aifoundry1", 1790798700.0)
        ivs = u["cards"]["aifoundry1-c1"]["intervals"]
        self.assertTrue(any(iv.get("lost_end") and iv["user"] == "user-a" for iv in ivs))  # the power loss
        self.assertEqual({iv.get("lock_user") for iv in ivs if iv["user"] == "?"} - {None}, {"user-a", "owner"})
        self.assertNotIn("lock_user", [k for iv in ivs if iv["user"] != "?" for k in iv])
        self.assertEqual(u["cards"]["aifoundry1-c1"]["unseen_lock"], ["user-a", "owner"])
        self.assertEqual(u["logger"], "running")
        # "bad user!" fails the login rule, and its program name is an address: neither leaves the collector
        self.assertNotIn("bad user!", json.dumps(u))
        self.assertNotIn("10.0.0.7", json.dumps(u))

    def test_paused_and_cut(self):
        col, u = self.block("raw-aifoundry2.txt", "aifoundry2", 1790797500.0)
        self.assertEqual(u["logger"], "running")
        self.assertEqual(u["paused"], "low free space, 310 MB free")   # without the log directory's path
        self.assertTrue(u["truncated_before_ms"])
        col.state["hosts"]["aifoundry2"] = {"usage": u, "last_ok_ms": C.ms(col.now)}
        hosts = {"aifoundry2": {"reachable": True}}
        cards = {cid: {"host": h} for cid, h in (("aifoundry2", "aifoundry2"),)}
        view = col.usage_view(hosts, cards)
        self.assertEqual(view["hosts"]["aifoundry2"]["paused"], u["paused"])
        col.derive_alerts({"aifoundry2": {"reachable": True, "state": "up"}}, {}, [], view)
        self.assertEqual(col.alerts["host:aifoundry2:usage"]["level"], "warn")
        self.assertIn("paused", col.alerts["host:aifoundry2:usage"]["title"])
        self.assertIn("since", col.alerts["host:aifoundry2:usage"]["detail"])   # since the last record
        self.assertEqual(col.alerts["host:aifoundry2:usage-cut"]["level"], "info")

    def test_stale_after_a_pause(self):
        col, u = self.block("run3/raw-aifoundry2.txt", "aifoundry2", 1790798700.0)
        self.assertEqual((u["logger"], u["paused"]), ("stale", "low free space, 310 MB free"))
        self.assertEqual(u["merged_gap_s"], 60)   # the whole log read: over 200 KB, merged by et-usage

    def test_the_live_monitors_unseen_opens_are_left_out(self):
        """et-usage logs the live monitor's 4 ms management-node reads as "?" opens, 3,600 an hour: they are no
        one's use. A few real unseen opens (and a login's own runs) stay."""
        iv = lambda u, a, b, n: {"user": u, "start": a, "end": b, "node_s": 1.0, "lock_s": 0, "procs": n, "programs": {"?": n}}
        j = {"v": 1, "host": "aifoundry3", "now": 1790797200.0, "since": 1790703600.0,
             "daemon": {"state": "running", "alive_at": 1790797190.0, "started_at": 1790700000.0},
             "logging_since": 1790700000.0, "coverage": [[1790703600.0, 1790797200.0]], "merged_gap_s": 60.0,
             "cards": {"0": {"intervals": [iv("?", 1790790000.0, 1790793600.0, 3600),   # the monitor: 1 a second
                                           iv("?", 1790794000.0, 1790794030.0, 6),      # six real unseen opens
                                           iv("?", 1790794100.0, 1790794102.0, 3),      # a once-a-second fragment
                                           dict(iv("?", 1790794200.0, 1790794201.0, 40), lock_user="bob"),  # 40 in a second
                                           iv("alice", 1790795000.0, 1790795003.0, 3)],
                             "activity": [], "users": {}, "held_s": 3.0, "node_s": 3.0, "merged_gap_s": 60.0, "now": [],
                             "daily": {"2026-10-02": {"?": {"held_s": 40.0, "node_s": 40.0, "runs": 15000},
                                                      "alice": {"held_s": 3.0, "node_s": 3.0, "runs": 3}},
                                       "2026-10-01": {"?": {"held_s": 0.1, "node_s": 0.1, "runs": 8}}}}}}
        u = bare(now=1790797500.0).usage_block("aifoundry3", {"installed": True, "json": j})
        c = u["cards"]["aifoundry3"]
        self.assertEqual([(x["user"], x["runs"]) for x in c["intervals"]], [("?", 6), ("?", 40), ("alice", 3)])
        days = {d["date"]: d["users"] for d in c["daily"]}
        self.assertEqual(sorted(days["2026-10-02"]), ["alice"])
        self.assertEqual(days["2026-10-01"]["?"]["runs"], 8)

    def test_a_busy_logs_cut_lists(self):
        j = {"v": 1, "host": "aifoundry2", "now": 1790797200.0, "since": 1790703600.0,
             "daemon": {"state": "running", "alive_at": 1790797190.0, "started_at": 1790700000.0},
             "logging_since": 1790700000.0, "coverage": [[1790703600.0, 1790797200.0]], "merged_gap_s": 3600.0,
             "cards": {"0": {"intervals": [{"user": "alice", "start": 1790790000.0, "end": 1790793600.0, "node_s": 900.0,
                                            "lock_s": 900.0, "procs": 40,
                                            "programs": {"a": 9, "b": 8, "c": 7, "d": 6, "e": 5, "(others)": 5}}],
                             "activity": [[1790796900.0, 240.0, 3, 900]], "activity_bin_s": 900,
                             "users": {}, "held_s": 900.0, "node_s": 900.0, "now_more": 7, "merged_gap_s": 3600.0,
                             "now": [{"user": "alice", "pid": 1, "comm": "a", "parent": "timeout", "nodes": ["ops"],
                                      "lock": True, "start": 1790797000.0}], "daily": {}}}}
        u = bare(now=1790797500.0).usage_block("aifoundry2", {"installed": True, "json": j})
        c = u["cards"]["aifoundry2"]
        self.assertEqual((c["now_more"], c["activity_bin_s"], c["merged_gap_s"]), (7, 900, 3600))
        self.assertEqual(list(c["intervals"][0]["programs"])[-1], "(others)")   # kept, and last
        self.assertEqual(c["intervals"][0]["programs"]["(others)"], 5)
        self.assertEqual(c["activity"], [[1790796900000, 240.0, 903]])
        self.assertEqual(C.top_programs({"p%d" % k: 10 - k for k in range(10)}, 8)["(others)"], 3)


if __name__ == "__main__":
    unittest.main(verbosity=1)
