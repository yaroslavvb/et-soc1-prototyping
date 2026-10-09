#!/usr/bin/env python3
"""Unit tests of the lab dashboard's box-side keeper (keeper.py). Standard library only, fully offline: no host is
contacted, no spacesheep command is run, no systemd unit is written outside the scratch HOME, and `update.sh`,
`crontab` and the anonymous page fetch are all stub scripts.

    python3 tools/lab/dashboard/tests/test_keeper.py        (LAB_DASH_TEST_DIR: where scratch files go)

They pin what the keeper of 8 October 2026 was written for: it reads update.sh's own run line, it never blocks on
update.sh (a stale page must not cost it its minute), it repairs only within its rate limits, it does nothing at
all while deploys are halted, and nothing it pushes to the public stream carries a login name, a path or an
address — checked with collect.py's own privacy check, so the two can never drift."""
import contextlib
import importlib.util
import io
import json
import os
import re
import stat
import tempfile
import time
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
DASH = os.path.dirname(HERE)
os.environ.setdefault("LAB_DASH_CONFIG", os.path.join(HERE, "no-config"))  # never the real config.json


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


K = load("keeper", os.path.join(DASH, "keeper.py"))
C = load("collect", os.path.join(DASH, "collect.py"))   # for its privacy check, which the keeper must never trip
WORK = os.environ.get("LAB_DASH_TEST_DIR") or tempfile.mkdtemp(prefix="labkeeper-test-")
os.makedirs(WORK, exist_ok=True)

STAMP = "%Y-%m-%dT%H:%M:%S%z"
SPACE = "00000000-1111-2222-3333-444444444444"   # invented: the real uuid belongs in MIRROR.md, not here
PAGE = ('<!doctype html><html><head><title>AI Foundry lab</title></head><body><script>\n'
        'const D = {"schema":1,"generated_at":"2026-10-08T15:32:04-07:00","generated_ms":%d,'
        '"collector":{"host":"%s","code":"b66f8ac","took_s":1.4,"heartbeat_min":60,"stale_after_min":80},'
        '"hosts":{}};\n</script></body></html>')


def script(path, body):
    with open(path, "w") as f:
        f.write("#!/bin/bash\n" + body)
    os.chmod(path, os.stat(path).st_mode | stat.S_IXUSR)
    return path


class Box:
    """A scratch lab box: its cache, its config, and stubs for update.sh, crontab and the anonymous fetch."""

    def __init__(self, cron_line=True, space=True, config=None, page_age_min=3.0, page_host="aifoundry2",
                 fetch_status="200", update_body="exit 0"):
        self.dir = tempfile.mkdtemp(dir=WORK)
        self.cache = os.path.join(self.dir, "cache")
        self.conf = os.path.join(self.dir, "conf")
        for d in (self.cache, self.conf):
            os.makedirs(d, 0o700, exist_ok=True)
        self.calls = os.path.join(self.dir, "calls")        # one line per stub invocation
        self.crontab_file = os.path.join(self.dir, "crontab.txt")
        with open(self.crontab_file, "w") as f:
            f.write("* * * * * /home/user/nodewatch/nodewatch.sh tick >/dev/null 2>&1\n")
            if cron_line:
                f.write("2-59/10 * * * * /home/user/claude/x/tools/lab/dashboard/update.sh run "
                        ">/dev/null 2>&1 # lab-dashboard\n")
        if space:
            with open(os.path.join(self.conf, "space"), "w") as f:
                f.write("%s\n" % SPACE)
        if config is not None:
            with open(os.path.join(self.conf, "config.json"), "w") as f:
                json.dump(config, f)
        self.update = script(os.path.join(self.dir, "update.sh"),
                             'printf "update %s\\n" "$*" >> "%s"\n%s\n' % ("%s", self.calls, update_body))
        self.crontab = script(os.path.join(self.dir, "crontab"),
                              'printf "crontab %s\\n" "$*" >> "%s"\n'
                              'if [ "$1" = -l ]; then cat "%s"; else cat > /dev/null; fi\n'
                              % ("%s", self.calls, self.crontab_file))
        self.page_body = PAGE % (K.now_ms(time.time() - page_age_min * 60), page_host) \
            if page_age_min is not None else "<html>nothing</html>"
        self.page_file = os.path.join(self.dir, "page.html")
        with open(self.page_file, "w") as f:
            f.write(self.page_body)
        self.fetch = script(os.path.join(self.dir, "fetch"),
                            'printf "fetch %s\\n" "$*" >> "%s"\necho %s\ncat "%s"\n'
                            % ("%s", self.calls, fetch_status, self.page_file))

    def env(self, **extra):
        e = {"HOME": self.dir, "USER": "owner", "PATH": "/usr/bin:/bin",
             "LAB_DASH_CACHE": self.cache, "LAB_DASH_CONFIG": self.conf,
             "LAB_DASH_UPDATE": self.update, "LAB_DASH_CRONTAB": self.crontab,
             "LAB_DASH_FETCH": self.fetch, "LAB_DASH_HOST": "aifoundry2"}
        e.update(extra)
        return e

    def keeper(self, now=None, **extra):
        return K.Keeper(env=self.env(**extra), now=now)

    def log(self, lines):
        with open(os.path.join(self.cache, "update.log"), "w") as f:
            f.write("".join(l + "\n" for l in lines))

    def run_line(self, ago_min, deploy="ok", mode="run", vis="public", fp="1c6e4a266b2f"):
        t = time.strftime(STAMP, time.localtime(time.time() - ago_min * 60))
        return ("%s %s took=1.4s hosts=3/3 alerts=bad0/warn1/info2 fp=%s vis=%s deploy=%s"
                % (t, mode, fp, vis, deploy))

    def said(self):
        try:
            with open(self.calls) as f:
                return f.read().splitlines()
        except OSError:
            return []

    def update_publishes(self, host="aifoundry2"):
        """Make the stub update.sh publish: when it runs, the page the fetch stub serves becomes a fresh one."""
        fresh = os.path.join(self.dir, "fresh.html")
        with open(fresh, "w") as f:
            f.write(PAGE % (K.now_ms(time.time()), host))
        script(self.update, 'printf "update %s\\n" "$*" >> "%s"\ncp "%s" "%s"\n'
               % ("%s", self.calls, fresh, self.page_file))

    def wait_for(self, call, s=5.0):
        """A detached `update.sh run` writes its line a moment after the keeper has returned: that it returned
        first is the point (test_tick_never_waits_for_update_sh), so look for the line, do not wait for it."""
        end = time.time() + s
        while time.time() < end and call not in self.said():
            time.sleep(0.05)
        return self.said()


class Scrub(unittest.TestCase):
    NASTY = ["FAILED(deploy to https://%s.spacesheep.app/ refused for owner)" % SPACE,
             "skipped(HALT: ssh to 203.0.113.7 failed; see /home/alice/.cache/lab-dashboard/update.log)",
             "FAILED(auth: user@example.org on lab-host.tailnet-name.ts.net)",
             "FAILED(login.tailscale.com/a/xyz)", "01.1.1.1 and 1.1.1.01", "x@1abc.com", "see http:// here",
             "fe80::1", "ether 02:42:ac:11:00:02", "~/.config/lab-dashboard/space is empty"]

    def test_collect_py_accepts_everything_the_keeper_scrubs(self):
        pr = C.Privacy("owner")
        for s in self.NASTY:
            out = K.scrub(s, owner="owner")
            self.assertEqual(pr.check({"x": out}), [], "%r scrubbed to %r, which collect.py refuses" % (s, out))

    def test_the_login_and_every_path_are_gone(self):
        out = K.scrub("FAILED(/home/owner/claude/x: owner cannot write)", owner="owner")
        self.assertNotIn("/home", out)
        self.assertNotIn("owner", out)

    def test_the_run_lines_own_counters_survive(self):
        self.assertEqual(K.scrub("hosts=3/3 alerts=bad0/warn1/info2 took=1.4s"),
                         "hosts=3/3 alerts=bad0/warn1/info2 took=1.4s")

    def test_cut_and_printable(self):
        self.assertEqual(len(K.scrub("x" * 300, 140)), 140)
        self.assertEqual(K.scrub("a\x07b\x00c"), "abc")

    def test_the_whole_status_json_is_public_safe(self):
        b = Box(config={"owner": "owner"})
        b.log([b.run_line(90, deploy="FAILED(deploy https://x.spacesheep.app/ for /home/alice: 10.0.0.7)")])
        with open(os.path.join(b.cache, "deploy.state"), "w") as f:
            f.write("%d 1c6e4a266b2f\n" % (time.time() - 7200))
        snap = b.keeper().status()
        self.assertEqual(C.Privacy("owner").check(snap), [])
        self.assertNotIn("spacesheep.app", json.dumps(snap))   # the space's uuid is never published


class Role(unittest.TestCase):
    def test_none_without_a_space(self):
        self.assertEqual(Box(space=False).keeper().role(), "none")

    def test_primary_with_a_space(self):
        self.assertEqual(Box().keeper().role(), "primary")

    def test_standby_from_config(self):
        self.assertEqual(Box(config={"standby_after_min": 120}).keeper().role(), "standby")

    def test_standby_from_the_environment_wins(self):
        b = Box(config={"standby_after_min": 120})
        self.assertEqual(b.keeper(LAB_DASH_STANDBY_AFTER_MIN="95").standby_after_min(), 95)
        self.assertEqual(b.keeper(LAB_DASH_STANDBY_AFTER_MIN="").standby_after_min(), 120)   # empty is unset

    def test_a_setting_update_sh_refuses_is_not_a_standby(self):
        # update.sh takes a whole number of minutes, 90 or more (below one heartbeat a standby would take over from
        # a live primary), and refuses every run with exit 2 otherwise, writing no run line at all: such a box
        # collects nothing, so the keeper reports only the setting and repairs nothing (it would otherwise start a
        # run every 20 min into a refusal)
        for bad in (10, 30, 89, 45.5, 0, "soon"):
            b = Box(config={"standby_after_min": bad})
            snap = b.keeper().status()
            self.assertEqual(snap["role"], "none", bad)
            self.assertTrue(any("is not a whole number of minutes, 90 or more" in w for w in snap["warn"]), bad)
            self.assertEqual(b.keeper().repairs(snap), [], bad)
        self.assertEqual(Box(config={"standby_after_min": 90}).keeper().role(), "standby")

    def test_a_standby_is_not_the_active_collector_while_the_primary_deploys(self):
        b = Box(config={"standby_after_min": 120}, page_host="aifoundry2")
        k = b.keeper(LAB_DASH_HOST="aifoundry3")
        self.assertFalse(k.active_collector("standby", {"host": "aifoundry2", "age_min": 30.0}))
        self.assertTrue(k.active_collector("standby", {"host": "aifoundry2", "age_min": 130.0}))
        self.assertTrue(k.active_collector("standby", {"host": "aifoundry3", "age_min": 5.0}))
        self.assertTrue(k.active_collector("primary", {"host": "aifoundry2", "age_min": 5.0}))


class Log(unittest.TestCase):
    def test_the_real_run_line(self):
        b = Box()
        # the two shapes update.sh:537 writes, plus lines it writes that are not runs
        b.log(["2026-10-08T15:22:04-0700 run skipped: another run holds the lock",
               "2026-10-08T15:22:09-0700 visibility check: the list said public; row: {}",
               "2026-10-08T15:32:04-0700 run took=1.4s hosts=3/3 alerts=bad0/warn1/info2 fp=1c6e4a266b2f "
               "vis=missing deploy=skipped(visibility unverified: list missing)",
               "2026-10-08T15:42:11-0700 now took=8.2s hosts=2/3 alerts=bad1/warn0/info1 fp=ab12cd34ef56 "
               "vis=public deploy=ok (before it: visibility was private, set public: done)"])
        last, last_cron, since, recent = b.keeper().read_runs()
        self.assertEqual((last["mode"], last["vis"]), ("now", "public"))
        self.assertTrue(last["deploy"].startswith("ok (before it:"))
        self.assertEqual(last_cron["vis"], "missing")
        self.assertEqual(K.local(last_cron["at_ms"], "%H:%M"), "15:32")
        self.assertEqual(since, 0)              # the newest line deployed
        self.assertEqual(len(recent), 2)

    def test_runs_since_deploy_counts_only_after_the_newest_ok(self):
        b = Box()
        b.log([b.run_line(90, deploy="ok"), b.run_line(70, deploy="skipped(unchanged; last 14:02)"),
               b.run_line(50, deploy="skipped(visibility unverified: list missing)"),
               b.run_line(30, deploy="skipped(visibility unverified: list missing)")])
        self.assertEqual(b.keeper().read_runs()[2], 3)

    def test_an_empty_field_does_not_hide_a_run(self):
        # took=, hosts= and alerts= come from `dj`, a python expression over data.json that prints nothing when it
        # throws; the keeper reads none of them, so an empty one must not make the run invisible
        b = Box()
        b.log(["2026-10-08T15:32:04-0700 run took= hosts= alerts= fp=1c6e4a266b2f vis=public deploy=ok"])
        self.assertEqual(b.keeper().read_runs()[0]["deploy"], "ok")
        b.log(["2026-10-08T15:32:04-0700 run skipped: another run holds the lock"])   # still not a run
        self.assertIsNone(b.keeper().read_runs()[0])

    def test_no_log_is_no_run(self):
        last, last_cron, since, recent = Box().keeper().read_runs()
        self.assertEqual((last, last_cron, since, recent), (None, None, 0, []))

    def test_deploy_state(self):
        b = Box()
        t = int(time.time()) - 3600
        with open(os.path.join(b.cache, "deploy.state"), "w") as f:
            f.write("%d 1c6e4a266b2f\n" % t)
        self.assertEqual(b.keeper().read_deploy_state(), {"at_ms": t * 1000, "fp": "1c6e4a266b2f"})

    def test_a_broken_deploy_state_is_no_deploy(self):
        b = Box()
        with open(os.path.join(b.cache, "deploy.state"), "w") as f:
            f.write("never\n")
        self.assertIsNone(b.keeper().read_deploy_state())

    def test_the_deadlock_verdict_names_its_fix(self):
        b = Box()
        b.log([b.run_line(5, deploy="skipped(visibility unverified: list missing)")])
        snap = b.keeper().status()
        self.assertIn("top-50 deadlock", " ".join(snap["warn"]))
        self.assertIn("update the checkout (git pull --ff-only)", snap["fix"])

    def test_a_newer_update_sh_is_not_the_deadlock(self):
        # the update.sh that fixed it writes a longer verdict for the same list answer: that is a box whose
        # checkout is current, so "git pull" is not the fix
        b = Box()
        b.log([b.run_line(5, deploy="skipped(visibility unverified: list missing, signed-out request: "
                                    "unverified: anonymous request answered 503)")])
        snap = b.keeper().status()
        self.assertNotIn("update the checkout (git pull --ff-only)", snap["fix"])
        b2 = Box()
        b2.log([b2.run_line(5, deploy="ok (before it: visibility public (signed-out request; not among the "
                                      "newest 50 in the list))")])
        self.assertEqual(b2.keeper().status()["warn"], [])

    def test_three_failed_deploys_are_a_warning(self):
        b = Box()
        b.log([b.run_line(25, deploy="ok"), b.run_line(21, deploy="FAILED(rate_limited deploy/86400)"),
               b.run_line(11, deploy="FAILED(rate_limited deploy/86400)"),
               b.run_line(1, deploy="FAILED(rate_limited deploy/86400)")])
        self.assertIn("the last 3 runs failed to deploy: FAILED(rate_limited deploy/86400)",
                      b.keeper().status()["warn"])


class Page(unittest.TestCase):
    def test_the_read_is_parsed(self):
        p = Box(page_age_min=7.0, page_host="aifoundry3").keeper().page()
        self.assertEqual(p["host"], "aifoundry3")
        self.assertAlmostEqual(p["age_min"], 7.0, delta=0.5)
        self.assertIsNone(p["err"])

    def test_it_is_cached_for_ten_minutes_then_read_again(self):
        b = Box()
        t = time.time()
        b.keeper(now=t).page()
        b.keeper(now=t + 540).page()                     # 9 minutes: the cache answers
        self.assertEqual(sum(1 for l in b.said() if l.startswith("fetch")), 1)
        b.keeper(now=t + 660).page()                     # 11 minutes: read again
        self.assertEqual(sum(1 for l in b.said() if l.startswith("fetch")), 2)

    def test_the_cached_age_grows_with_the_clock(self):
        b, t = Box(page_age_min=1.0), time.time()
        b.keeper(now=t).page()
        self.assertAlmostEqual(b.keeper(now=t + 300).page()["age_min"], 6.0, delta=0.5)

    def test_a_failed_read_is_an_error_not_an_age(self):
        b = Box(fetch_status="404")
        p = b.keeper().page()
        self.assertIsNone(p["age_min"])
        self.assertEqual(p["err"], "HTTP 404")

    def test_a_page_without_the_data_block(self):
        self.assertEqual(Box(page_age_min=None).keeper().page()["err"], "no generated_ms in the page")

    def test_no_space_is_no_read(self):
        b = Box(space=False)
        self.assertEqual(b.keeper().page()["err"], "no space configured")
        self.assertEqual(b.said(), [])

    def test_a_collector_host_that_is_not_a_short_name_never_reaches_the_stream(self):
        # the host is read off a page over the public internet and goes straight onto a public stream. collect.py
        # writes a short name (collect.py:955), but the keeper does not get to trust that.
        for host in ("lab-host.tailnet-name.ts.net", "203.0.113.7"):
            b = Box(page_host=host, config={"owner": "owner"})
            b.log([b.run_line(3)])
            snap = b.keeper().status()
            self.assertIsNone(snap["page"]["host"], host)
            self.assertEqual(C.Privacy("owner").check(snap), [], host)
            self.assertNotIn(host, json.dumps(snap))

    def test_the_fix_that_names_the_stale_pages_collector_is_safe_too(self):
        b = Box(config={"standby_after_min": 180, "owner": "owner"}, page_age_min=120.0, page_host="203.0.113.7")
        b.log([b.run_line(3)])
        snap = b.keeper(LAB_DASH_HOST="aifoundry3").status()
        self.assertTrue(any("the collector on the other box has stopped" in f for f in snap["fix"]))
        self.assertEqual(C.Privacy("owner").check(snap), [])

    def test_the_body_read_stops_at_its_deadline(self):
        # urlopen's timeout bounds each recv, not the whole body: a trickling origin must not hold a tick open
        class Trickle:
            def read(self, n):
                time.sleep(0.2)
                return b"x" * 16

        t0 = time.time()
        self.assertTrue(K.read_bounded(Trickle(), 0.5))
        self.assertLess(time.time() - t0, 2.0)


class Repairs(unittest.TestCase):
    def setUp(self):
        self.keepers = []

    def tearDown(self):
        # The repairs leave `update.sh run` running on purpose, and the keeper never waits for it. A test reaps
        # the stub, so Popen's destructor does not warn about a child nobody waited for (on a box the tick
        # process exits at once and init reaps it).
        for k in self.keepers:
            for p in k._started:
                p.kill()
                p.wait()

    def tick(self, b, **kw):
        k = b.keeper(**kw)
        self.keepers.append(k)
        snap = k.status()
        return snap, k.repairs(snap)

    def test_r1_installs_a_missing_cron_line_once_an_hour(self):
        b = Box(cron_line=False)
        b.log([b.run_line(3)])
        snap, done = self.tick(b)
        self.assertFalse(snap["cron"]["installed"])
        self.assertIn("the lab-dashboard cron line is missing from this box's crontab", snap["warn"])
        self.assertTrue(any("--install-cron" in d for d in done))
        self.assertIn("update --install-cron", b.said())
        snap2, done2 = self.tick(b)                                  # at once again: the limit holds
        self.assertEqual([d for d in done2 if "--install-cron" in d], [])
        snap3, done3 = self.tick(b, now=time.time() + 3700)          # an hour later: again
        self.assertTrue(any("--install-cron" in d for d in done3))

    def test_r2_starts_a_run_when_cron_has_not_for_25_minutes(self):
        b = Box()
        b.log([b.run_line(31)])
        snap, done = self.tick(b)
        self.assertIn("no cron run for 31 min (it runs every 10)", snap["warn"])
        self.assertIn("update run", b.wait_for("update run"))
        self.assertTrue(any("started update.sh run" in d for d in done))

    def test_r2_is_quiet_while_cron_is_running(self):
        b = Box()
        b.log([b.run_line(4)])
        snap, done = self.tick(b)
        self.assertEqual(done, [])
        self.assertEqual(snap["warn"], [])
        self.assertNotIn("update run", b.said())

    def test_r2_ignores_a_now_run_that_a_person_made(self):
        b = Box()
        b.log([b.run_line(40, mode="run"), b.run_line(2, mode="now")])
        snap, done = self.tick(b)
        self.assertIn("no cron run for 40 min (it runs every 10)", snap["warn"])
        self.assertEqual(snap["last_run"]["mode"], "now")            # the newest line is still the one reported

    def test_r2_and_r3_share_one_twenty_minute_limit(self):
        b = Box()
        b.log([b.run_line(31)])
        t = time.time()
        self.assertTrue(self.tick(b, now=t)[1])
        self.assertEqual([d for d in self.tick(b, now=t + 600)[1] if "update.sh run" in d], [])   # 10 min
        self.assertTrue(any("update.sh run" in d for d in self.tick(b, now=t + 1300)[1]))         # 21 min

    def test_r3_starts_a_run_for_a_stale_page_and_names_the_verdict(self):
        b = Box(page_age_min=120.0)
        b.log([b.run_line(3, deploy="skipped(visibility unverified: list missing)")])
        snap, done = self.tick(b)
        self.assertTrue(any("the page is 120 min old" in d for d in done))
        self.assertIn("the published page is 120 min old (it reads STALE at 80)", snap["warn"])
        self.assertTrue(any("the newest run says deploy=skipped(visibility unverified: list missing)" in w
                            for w in snap["warn"]))

    def test_r3_leaves_the_primarys_page_to_the_primary(self):
        b = Box(config={"standby_after_min": 180}, page_age_min=120.0, page_host="aifoundry2")
        b.log([b.run_line(3)])
        snap, done = self.tick(b, LAB_DASH_HOST="aifoundry3")
        self.assertEqual(done, [])                                   # 120 min < standby_after_min 180
        self.assertTrue(any("the collector on aifoundry2 has stopped" in f for f in snap["fix"]))

    def test_r3_takes_over_past_standby_after_min(self):
        b = Box(config={"standby_after_min": 90}, page_age_min=120.0, page_host="aifoundry2")
        b.log([b.run_line(3)])
        snap, done = self.tick(b, LAB_DASH_HOST="aifoundry3")
        self.assertTrue(any("the page is 120 min old" in d for d in done))

    def test_a_standing_by_box_is_not_judged_on_its_runs(self):
        # update.sh's standby gate returns before it writes the run line (update.sh:420 and :537), so a box that
        # is standing by correctly has no run line at all: that is not a dead cron
        b = Box(config={"standby_after_min": 90}, page_age_min=4.0, page_host="aifoundry2")
        b.log(["2026-10-08T15:22:04-0700 standby: aifoundry2 published 4 min ago; this machine takes over "
               "after 90 min"])
        snap, done = self.tick(b, LAB_DASH_HOST="aifoundry3")
        self.assertEqual((snap["role"], snap["warn"], done), ("standby", [], []))
        self.assertNotIn("update run", b.said())

    def test_two_keepers_do_not_share_one_temp_file(self):
        # keeper-state.json is written by every repair, and a person's `repair` lives for minutes beside the
        # minute's tick: one shared "<path>.new" and the loser's os.replace raises
        b = Box()
        mine = os.path.join(b.cache, "keeper-state.json")
        theirs = "%s.new.%d" % (mine, os.getpid() + 1)
        with open(theirs, "w") as f:
            f.write("half a file")
        K.write_atomic(mine, "{}")
        self.assertTrue(os.path.exists(theirs))              # another keeper's temp is left alone
        with open(mine) as f:
            self.assertEqual(f.read(), "{}")

    def test_a_missing_update_sh_is_reported_not_raised(self):
        # a tick that raises pushes no line, and the keeper would go quiet exactly when the checkout is broken
        b = Box()
        b.log([b.run_line(31)])
        os.remove(b.update)
        snap, done = self.tick(b)
        self.assertTrue(any("update.sh could not be started" in w for w in snap["warn"]))
        self.assertTrue(any("could not be started" in d for d in done))

    def test_r4_halt_warns_and_does_nothing(self):
        b = Box(cron_line=False, page_age_min=300.0)
        b.log([b.run_line(90, deploy="skipped(HALT from the private mode: was exposed)")])
        open(os.path.join(b.cache, "HALT"), "w").close()
        snap, done = self.tick(b)
        self.assertTrue(snap["halt"])
        self.assertEqual(done, [])
        self.assertEqual([l for l in b.said() if l.startswith("update ")], [])
        self.assertIn("a person checks the space and runs update.sh resume", snap["fix"])

    def test_r4_exposed_does_nothing_either(self):
        b = Box(cron_line=False)
        open(os.path.join(b.cache, "EXPOSED"), "w").close()
        snap, done = self.tick(b)
        self.assertTrue(snap["exposed"])
        self.assertEqual(done, [])

    def test_a_box_with_no_dashboard_repairs_nothing(self):
        b = Box(space=False, cron_line=False)
        snap, done = self.tick(b)
        self.assertEqual((snap["role"], snap["warn"], done), ("none", [], []))

    def test_a_repair_is_logged_and_remembered(self):
        b = Box()
        b.log([b.run_line(31)])
        snap, done = self.tick(b)
        self.assertIn("started update.sh run", snap["repair"]["what"])
        with open(os.path.join(b.cache, "keeper.log")) as f:
            self.assertIn("started update.sh run detached (no cron run for 31 min)", f.read())
        with open(os.path.join(b.cache, "keeper-state.json")) as f:
            state = json.load(f)
        self.assertIn("update_run_ms", state)
        self.assertIn("started update.sh run", b.keeper().status()["repair"]["what"])   # read back next tick

    def test_the_keeper_log_rotates_at_256_kb(self):
        b = Box()
        path = os.path.join(b.cache, "keeper.log")
        with open(path, "w") as f:
            f.write("x" * (257 * 1024))
        b.keeper().log("a repair")
        self.assertTrue(os.path.exists(path + ".1"))
        self.assertLess(os.path.getsize(path), 1024)

    def test_tick_never_waits_for_update_sh(self):
        b = Box(update_body='sleep 10\nexit 0')
        b.log([b.run_line(31)])
        t0 = time.time()
        k = b.keeper()
        self.keepers.append(k)
        snap = k.status()
        k.repairs(snap)
        self.assertLess(time.time() - t0, 5.0, "tick waited for update.sh")
        self.assertIn("update run", b.wait_for("update run"))        # the detached child did start


class Tick(unittest.TestCase):
    """`tick`: the one line a minute. It is printed whatever else happens, and it is printed in time."""

    def line(self, k):
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            rc = K.cmd_tick(k)
        return rc, json.loads(buf.getvalue().strip())

    def test_the_line_is_printed_even_when_a_repair_raises(self):
        b = Box()
        b.log([b.run_line(3)])
        k = b.keeper()

        def boom(*a, **kw):
            raise OSError("no space left on device")

        k.repairs = boom
        rc, snap = self.line(k)
        self.assertEqual(rc, 0)
        self.assertIn("the repairs raised OSError", snap["warn"])
        self.assertEqual(snap["schema"], 1)

    def test_a_tick_works_to_one_deadline(self):
        k = Box().keeper()
        self.assertEqual(k.budget(K.PAGE_TIMEOUT_S), K.PAGE_TIMEOUT_S)        # a person's status has no deadline
        k.deadline = time.monotonic() + 6
        self.assertLessEqual(k.budget(K.PAGE_TIMEOUT_S), 6)
        k.deadline = time.monotonic() + K.LEG_MIN_S - 1     # too little left to be worth starting
        self.assertEqual(k.budget(K.PAGE_TIMEOUT_S), 0)
        k.deadline = time.monotonic() - 1
        self.assertEqual(k.budget(K.PAGE_TIMEOUT_S), 0)

    def test_a_leg_with_no_time_left_is_skipped_and_said(self):
        b = Box()
        b.log([b.run_line(3)])
        k = b.keeper()
        k.deadline = time.monotonic() - 1
        snap = k.status()
        self.assertIsNone(snap["cron"]["installed"])
        self.assertIsNone(snap["page"]["age_min"])
        self.assertEqual([l for l in b.said() if l.startswith("fetch")], [])
        self.assertTrue(any("ran out of its" in w for w in snap["warn"]))
        # and the page cache is not poisoned with a read that never happened
        self.assertFalse(os.path.exists(os.path.join(b.cache, "keeper-page.json")))


class Repair(unittest.TestCase):
    """`repair`: what a person, or a watchdog elsewhere, runs over ssh when the page stops."""

    def run_it(self, b, force=False, **extra):
        buf, k = io.StringIO(), b.keeper(**extra)
        with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(buf):
            rc = K.cmd_repair(k, force)
        return rc, buf.getvalue(), k

    def test_the_foreground_now_is_the_only_run_it_starts(self):
        # R2/R3's detached `update.sh run` takes update.sh's lock without waiting, and `now` waits only 60 s for
        # it (update.sh:412-416), so repair would lose the race to its own child on the very freeze it was run for
        b = Box(page_age_min=200.0)
        b.log([b.run_line(200)])
        b.update_publishes()
        rc, out, k = self.run_it(b)
        self.assertEqual([l for l in b.said() if l.startswith("update ")], ["update now"])
        self.assertEqual(k._started, [])
        self.assertEqual(rc, 0, out)

    def test_a_second_now_within_ten_minutes_needs_force(self):
        # every `now` deploys, whatever the fingerprint says (update.sh:490, :493), against a daily cap
        b = Box(page_age_min=200.0)
        b.log([b.run_line(200)])
        with open(os.path.join(b.cache, "keeper-state.json"), "w") as f:
            json.dump({"update_now_ms": K.now_ms(time.time() - 120)}, f)
        rc, out, k = self.run_it(b)
        self.assertEqual((rc, [l for l in b.said() if l.startswith("update ")]), (1, []))
        self.assertIn("--force", out)
        b.update_publishes()
        rc, out, k = self.run_it(b, force=True)
        self.assertEqual((rc, [l for l in b.said() if l.startswith("update ")]), (0, ["update now"]))

    def test_it_runs_nothing_while_deploys_are_halted(self):
        b = Box(page_age_min=300.0)
        b.log([b.run_line(90, deploy="skipped(HALT from the private mode: was exposed)")])
        open(os.path.join(b.cache, "HALT"), "w").close()
        rc, out, k = self.run_it(b)
        self.assertEqual((rc, [l for l in b.said() if l.startswith("update ")]), (1, []))
        self.assertIn("update.sh resume", out)


class Install(unittest.TestCase):
    def box(self):
        b = Box()
        for rel in (".local/node/bin/node", ".local/ss-stream/node_modules/spacesheep/bin/spacesheep.js",
                    ".config/spacesheep/config.json"):
            p = os.path.join(b.dir, rel)
            os.makedirs(os.path.dirname(p), exist_ok=True)
            open(p, "w").close()
        return b

    def dry(self, b):
        """--dry-run prints; it must run no command at all, least of all systemctl."""
        buf, ran, real = io.StringIO(), [], K.subprocess.run
        K.subprocess.run = lambda *a, **kw: ran.append(a[0]) or real(*a, **kw)
        try:
            with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(buf):
                rc = K.cmd_install(b.keeper(), True)
        finally:
            K.subprocess.run = real
        self.assertEqual([c for c in ran if c and c[0] in ("systemctl", "loginctl")], [])
        return rc, buf.getvalue()

    def test_dry_run_prints_the_unit_and_runs_nothing(self):
        b = self.box()
        rc, out = self.dry(b)
        self.assertEqual(rc, 0)
        self.assertIn("would write %s/.config/systemd/user/lab-dashboard-keeper.service" % b.dir, out)
        self.assertIn('"stream" "aifoundry-dash/aifoundry2" "--every" "60s" "--" "/usr/bin/python3"', out)
        self.assertIn(os.path.join(DASH, "keeper.py") + '" "tick" "--json"', out)
        self.assertIn("Restart=always", out)
        self.assertIn("RestartSec=5", out)
        self.assertIn("StartLimitIntervalSec=0", out)
        self.assertIn("WantedBy=default.target", out)
        self.assertIn("After=network-online.target", out)
        self.assertIn("StandardOutput=append:%s/keeper-stream.log" % b.cache, out)
        self.assertIn("would make %s" % b.cache, out)
        self.assertIn("would then run:\n  systemctl --user daemon-reload", out)
        self.assertIn("loginctl show-user owner -p Linger", out)
        self.assertFalse(os.path.exists(os.path.join(b.dir, ".config/systemd/user/lab-dashboard-keeper.service")))

    def test_it_makes_the_directory_the_units_log_goes_in(self):
        # systemd refuses to start a unit whose StandardOutput=append: directory is missing, and on a box where
        # the dashboard has never run (aifoundry1, aifoundry3) nothing has made ~/.cache/lab-dashboard
        b = self.box()
        os.rmdir(b.cache)
        ran, real = [], K.subprocess.run

        class Done:
            returncode, stdout, stderr = 0, "Linger=yes", ""

        K.subprocess.run = lambda *a, **kw: (ran.append(list(a[0])), Done())[1]
        try:
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(buf):
                rc = K.cmd_install(b.keeper(), False)
        finally:
            K.subprocess.run = real
        self.assertEqual(rc, 0)
        self.assertTrue(os.path.isdir(b.cache))
        self.assertTrue(os.path.exists(os.path.join(b.dir, ".config/systemd/user", K.UNIT)))
        self.assertEqual([c[:3] for c in ran], [["systemctl", "--user", "daemon-reload"],
                                                ["systemctl", "--user", "enable"],
                                                ["loginctl", "show-user", "owner"]])

    def test_it_reuses_the_node_the_live_stream_unit_names(self):
        b = self.box()
        node = os.path.join(b.dir, "other-node")
        js = os.path.join(b.dir, "other-spacesheep.js")
        for p in (node, js):
            open(p, "w").close()
        d = os.path.join(b.dir, ".config/systemd/user")
        os.makedirs(d, exist_ok=True)
        with open(os.path.join(d, "spacesheep-stream-aifoundry-aifoundry2.service"), "w") as f:
            f.write('[Service]\nExecStart="%s" "%s" "stream" "aifoundry/aifoundry2" "--run" "x"\n' % (node, js))
        rc, out = self.dry(b)
        self.assertIn('ExecStart="%s" "%s" "stream"' % (node, js), out)
        self.assertIn("Environment=\"PATH=%s:" % b.dir, out)         # the node directory comes first

    def test_it_refuses_without_the_cli(self):
        b = Box()                                                    # no node, no spacesheep.js, no key
        rc, out = self.dry(b)
        self.assertEqual(rc, 1)
        self.assertIn("is missing", out)

    def test_it_refuses_without_a_key(self):
        b = self.box()
        os.remove(os.path.join(b.dir, ".config/spacesheep/config.json"))
        rc, out = self.dry(b)
        self.assertEqual(rc, 1)
        self.assertIn("`spacesheep login` is a person's step", out)


class Snapshot(unittest.TestCase):
    def test_the_json_is_one_line_and_has_every_field(self):
        b = Box(config={"owner": "owner"})
        b.log([b.run_line(3)])
        snap = b.keeper().status()
        self.assertEqual(set(snap), {"schema", "host", "hl", "t", "keeper", "role", "cron", "last_run",
                                     "runs_since_deploy", "last_deploy", "page", "halt", "exposed", "repair",
                                     "warn", "fix"})
        self.assertEqual((snap["schema"], snap["host"], snap["role"]), (1, "aifoundry2", "primary"))
        self.assertTrue(re.match(r"^[0-9a-f]{6,40}$|^nogit$", snap["keeper"]))
        self.assertNotIn("\n", json.dumps(snap, separators=(",", ":")))

    def test_the_headline_survives_the_stream_lists_cut(self):
        # `spacesheep streams` shows only about the first 250 characters of a value, so "hl" sits near the front
        # and says the one thing a watchdog needs: the first warning, or that all is well
        b = Box(config={"owner": "owner"})
        b.log([b.run_line(3)])
        line = json.dumps(b.keeper().status(), separators=(",", ":"))
        self.assertLess(line.index('"hl":'), 120)
        head = json.loads(line)["hl"]
        self.assertTrue(head.startswith("ok primary: ran 3 min ago"), head)
        b = Box(config={"owner": "owner"}, cron_line=False)
        b.log([b.run_line(3)])
        snap = b.keeper().status()
        self.assertTrue(snap["hl"].startswith("WARN 1: the lab-dashboard cron line is missing"), snap["hl"])
        self.assertLessEqual(len(snap["hl"]), K.HL_MAX)

    def test_a_standby_that_stands_by_says_so_in_its_headline(self):
        b = Box(config={"standby_after_min": 90}, page_age_min=12.0, page_host="aifoundry2")
        snap = b.keeper(LAB_DASH_HOST="aifoundry3").status()
        self.assertEqual(snap["warn"], [])
        self.assertEqual(snap["hl"], "ok standby: aifoundry2's page is 12 min old")

    def test_a_crontab_that_cannot_be_read_is_not_a_missing_line(self):
        b = Box()
        script(b.crontab, 'echo "crontab: command not found" >&2\nexit 127\n')
        b.log([b.run_line(3)])
        snap = b.keeper().status()
        self.assertIsNone(snap["cron"]["installed"])
        self.assertIn("the crontab could not be read", snap["warn"])


if __name__ == "__main__":
    unittest.main(verbosity=1)
