#!/usr/bin/env python3
"""Unit tests of the lab dashboard's collector (collect.py) and the probe's process filter (remote.sh). Standard library
only, no host is contacted:

    python3 tools/lab/dashboard/tests/test_collect.py        (LAB_DASH_TEST_DIR: where scratch files go)

They pin the fixes of 30 September 2026's reviews: render.py never refuses what the collector wrote; ssh's keepalive
timeout is a timeout; a machine's DOWN time is its own; a reboot after an outage is not "planned"; the approval
back-off never hides another failure; people's status, "doing" and holds come from machines that answered; a terminal
logs a person in, a seconds-old session with no terminal does not; lingering user managers are not people; the headline
names a machine that is not up and never counts old data; the fingerprint ignores ssh wording and idle crossings; the
current history slot is the latest run; login colours stay with their logins."""
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
    col.owner, col.maintainer = "owner", "owner"
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


if __name__ == "__main__":
    unittest.main(verbosity=1)
