#!/usr/bin/python3
"""Automated tests of et-usaged and et-usage (tools/lab/et-usage), run as an ordinary user. No card is touched.

The daemon runs in --foreground mode against regular files in a scratch directory: fake card nodes (dev/et0_mgmt,
dev/et0_ops, dev/et1_*), lock files, and a fake sysfs tree (devnum, *_vq_stats/msg_count, and attributes it must
never read). Child processes open and close those files (flock -n <lock> timeout 5 <prog>, a holder present before
the daemon, a node deleted and recreated while held, a forked holder, a queue of short runs, a flood of opens, a
holder in another PID namespace, SIGTERM while holding); the test checks the records, now.json and the CLI.
The daemon runs under a Python audit hook that logs every file it opens: an open of a fake node, of a forbidden sysfs
attribute or of a skipped card's counters, or a write under the fake sysfs, fails the test.

usage: python3 test/test_et_usage.py [--dir DIR] [--keep]
  --dir DIR   scratch directory (created; default: a new directory under $TMPDIR)
  --keep      keep the scratch directory afterwards
"""

import argparse
import datetime
import glob
import importlib.machinery
import importlib.util
import json
import os
import pwd
import resource
import shutil
import signal
import subprocess
import sys
import tempfile
import time

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
TOOL = os.path.dirname(HERE)
DAEMON = os.path.join(TOOL, 'et-usaged')
CLI = os.path.join(TOOL, 'et-usage')
ME = pwd.getpwuid(os.getuid()).pw_name
RESULTS = []


def check(name, ok, detail=''):
    RESULTS.append((name, bool(ok)))
    print(('PASS  ' if ok else 'FAIL  ') + name + ('' if ok else '   <-- ' + str(detail)[:600]), flush=True)
    return ok


def wait_for(fn, timeout=5.0, step=0.05):
    end = time.time() + timeout
    while True:
        v = fn()
        if v or time.time() > end:
            return v
        time.sleep(step)


def write(path, text, mode=None):
    tmp = path + '.tmp-test'
    with open(tmp, 'w') as f:
        f.write(text)
    os.replace(tmp, path)
    if mode is not None:
        os.chmod(path, mode)


def load_daemon_module():
    spec = importlib.util.spec_from_loader('etusaged', importlib.machinery.SourceFileLoader('etusaged', DAEMON))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


FAKE_HOST = r'''#!/usr/bin/python3
# fake_host: opens the given paths as a card program opens /dev/et<N>_mgmt and _ops, holds them, exits.
import os, sys, time
a = sys.argv[1:]
hold, fork_after, ready = 1.0, None, None
while a and a[0].startswith('--'):
    o = a.pop(0)
    if o == '--hold': hold = float(a.pop(0))
    elif o == '--fork-after': fork_after = float(a.pop(0))
    elif o == '--ready': ready = a.pop(0)
    elif o == '--comm':
        with open('/proc/self/comm', 'w') as f:       # any bytes but NUL, 15 at most: escapes too
            f.write(a.pop(0))
fds = [os.open(p, os.O_RDONLY) for p in a]
if ready:
    open(ready, 'w').close()
child = 0
if fork_after is not None:
    time.sleep(fork_after)
    child = os.fork()            # the child inherits the fds: no open event
time.sleep(hold)
if child:
    os.waitpid(child, 0)
for fd in fds:
    os.close(fd)
'''

AUDIT_WRAP = r'''
import os, re, runpy, sys
LOG, ROOT, SKIP = os.environ['ETU_AUDIT_LOG'], os.environ['ETU_ROOT'], os.environ.get('ETU_SKIP_SYS', '')
SKIP_PCI = os.environ.get('ETU_SKIP_PCI', '')      # a --skip-pci card: no file under it may be opened, not even devnum
NODE = re.compile(r'/et\d+_(mgmt|ops)( \(deleted\))?$')
ALLOWED = re.compile(r'/(devnum|mgmt_vq_stats/msg_count|ops_vq_stats/msg_count)$')
def hook(ev, args):
    if ev != 'open' or not args or args[0] is None or isinstance(args[0], int):
        return
    p = os.fsdecode(args[0])
    mode = args[1] if len(args) > 1 else None
    flags = args[2] if len(args) > 2 and isinstance(args[2], int) else 0
    why = None
    if NODE.search(p):
        why = 'opened a card node'
    elif p.startswith(ROOT + '/sys/') or p.startswith('/sys/'):
        if (flags & (os.O_WRONLY | os.O_RDWR)) or (isinstance(mode, str) and any(c in mode for c in 'wax+')):
            why = 'wrote to sysfs'
        elif SKIP and p.startswith(SKIP + '/') and 'vq_stats' in p:
            why = 'read a skipped card counter'
        elif SKIP_PCI and (p == SKIP_PCI or p.startswith(SKIP_PCI + '/')):
            why = 'touched a --skip-pci card'
        elif not ALLOWED.search(p):
            why = 'opened a sysfs attribute outside the list'
    if why:
        with open(LOG, 'a') as f:
            f.write('%s: %s (flags %#o, mode %r)\n' % (why, p, flags, mode))
sys.addaudithook(hook)
sys.argv = sys.argv[1:]
runpy.run_path(sys.argv[0], run_name='__main__')
'''


class Env:
    def __init__(self, root):
        self.root = root
        for d in ('dev', 'lock', 'sys', 'log', 'run', 'bin', 'tmp', 'unit', 'synth'):
            os.makedirs(os.path.join(root, d), exist_ok=True)
        self.node = {(c, k): '%s/dev/et%d_%s' % (root, c, k) for c in (0, 1) for k in ('mgmt', 'ops')}
        self.lock = {c: '%s/lock/etsoc-shire%d.lock' % (root, c) for c in (0, 1)}
        for p in list(self.node.values()) + list(self.lock.values()):
            write(p, '', 0o666)
        write(root + '/dev/et0_other', '')           # a name the daemon must ignore
        self.sys = {0: root + '/sys/0000:02:00.0', 1: root + '/sys/0000:01:00.0'}
        for card, d in self.sys.items():
            for sub in ('mgmt_vq_stats', 'ops_vq_stats'):
                os.makedirs(d + '/' + sub, exist_ok=True)
                write(d + '/' + sub + '/utilization_percent', '0\n')
                write(d + '/' + sub + '/clear', '')
            write(d + '/devnum', '%d\n' % card)
            for f in ('config', 'resource0', 'utilization_percent'):
                write(d + '/' + f, '0\n')
            self.set_counts(card, 10, 100)
        self.fake_host = root + '/bin/fake_host'
        write(self.fake_host, FAKE_HOST, 0o755)
        self.wrap = root + '/bin/audit_wrap.py'
        write(self.wrap, AUDIT_WRAP)
        self.audit = root + '/audit.log'
        write(self.audit, '')

    def set_counts(self, card, mgmt, ops):
        d = self.sys[card]
        write(d + '/mgmt_vq_stats/msg_count', 'SQ0:           %d msg(s)\nCQ0:           %d msg(s)\n' % (mgmt, mgmt + 1))
        write(d + '/ops_vq_stats/msg_count',
              'SQ0:           %d msg(s)\nSQ1:           0 msg(s)\nCQ0:           %d msg(s)\n' % (ops, ops + 5))

    def daemon_args(self, log='log', run='run'):
        r = self.root
        return ['--dev-glob', r + '/dev/et[0-9]*_*', '--lock-glob', r + '/lock/etsoc-shire[0-9]*.lock',
                '--sysfs-glob', r + '/sys/0000:*', '--log-dir', r + '/' + log, '--run-dir', r + '/' + run,
                '--skip-counters', '1', '--scan-every', '2', '--act-every', '1', '--beat-every', '3',
                '--defaults', 'none']

    def records(self):
        out = []
        for f in sorted(glob.glob(self.root + '/log/*.jsonl')):
            with open(f) as fh:
                out += [json.loads(line) for line in fh if line.strip()]
        return out

    def holds(self, since=0.0, **kw):
        out = []
        for r in self.records():
            if r['t'] != 'hold' or r['end'] < since - 0.01:     # records are rounded to 1 ms
                continue
            if all(r.get(k) == v for k, v in kw.items()):
                out.append(r)
        return out

    def now(self):
        try:
            with open(self.root + '/run/now.json') as f:
                return json.load(f)
        except (OSError, ValueError):
            return None

    def now_holds(self, **kw):
        nj = self.now() or {}
        return [h for h in nj.get('holds', []) if all(h.get(k) == v for k, v in kw.items())]


def cli(args, env=None, extra_env=None):
    e = dict(os.environ, PYTHONDONTWRITEBYTECODE='1')
    if extra_env:
        e.update(extra_env)
    p = subprocess.run([sys.executable, CLI] + args, capture_output=True, text=True, env=e, timeout=60)
    return p


# ============================================================================ unit tests of the daemon's core
def unit_tests(env):
    print('\n== unit tests (the daemon imported as a module)')
    m = load_daemon_module()
    base = ['--stdout', '--dev-glob', env.root + '/dev/et[0-9]*_*',
            '--lock-glob', env.root + '/lock/etsoc-shire[0-9]*.lock']

    def fresh():
        d = m.Daemon(m.parse_args(base))
        d.reglob(watch=False)
        recs = []
        d.emit = recs.append
        return d, recs

    def batch(*evs):
        b = m.Batch()
        for ck, is_open, t in evs:
            b.add(ck, is_open, t, m.boottime())
        return b

    uid = os.getuid()
    # PID reuse: the same pid with another start time is another process.
    d, recs = fresh()
    t = time.time()
    d.apply({(100, 5000): {0: {'ops'}}}, {(100, 5000): ('prog_a', 1, uid, 'bash')}, batch(((0, 'ops'), True, t)),
            t + 0.02)
    d.apply({(100, 6000): {0: {'ops'}}}, {(100, 6000): ('prog_b', 1, uid, 'bash')},
            batch(((0, 'ops'), False, t + 1.0), ((0, 'ops'), True, t + 1.001)), t + 1.02)
    hr = [r for r in recs if r['t'] == 'hold']
    check('pid reuse: the old process\'s hold ends at its close event',
          len(hr) == 1 and hr[0]['comm'] == 'prog_a' and abs(hr[0]['end'] - (t + 1.0)) < 0.002
          and abs(hr[0]['start'] - t) < 0.002, recs)
    check('pid reuse: the new process (same pid, new start time) is a new hold from its open event',
          (100, 6000, 0) in d.holds and d.holds[(100, 6000, 0)].comm == 'prog_b'
          and abs(d.holds[(100, 6000, 0)].start - (t + 1.001)) < 0.002, list(d.holds))

    # Clock step: open holds move with the clock, and a clock record is written.
    k = (100, 6000, 0)
    s0 = d.holds[k].start
    d.off -= 3600.0
    d.check_clock()
    check('clock step: an open hold\'s start moves with the step', abs(d.holds[k].start - (s0 + 3600)) < 0.01,
          (s0, d.holds[k].start))
    check('clock step: a clock record', recs[-1]['t'] == 'clock' and abs(recs[-1]['step'] - 3600) < 0.01, recs[-1])

    # Rotation at local midnight: each record goes to the file of its own local date.
    ld = env.root + '/unit/log'
    os.makedirs(ld, exist_ok=True)
    d2 = m.Daemon(m.parse_args(['--log-dir', ld, '--run-dir', env.root + '/unit']))
    lt = time.localtime(time.time() + 86400)
    mid = time.mktime((lt.tm_year, lt.tm_mon, lt.tm_mday, 0, 0, 0, 0, 0, -1))
    d2.emit({'t': 'beat', 'v': 1, 'at': mid - 0.5, 'holding': 0})
    d2.emit({'t': 'beat', 'v': 1, 'at': mid + 0.5, 'holding': 0})
    d2.emit({'t': 'hold', 'v': 1, 'card': 0, 'start': mid - 3, 'end': mid - 0.2})
    d2.close_log()
    day1 = time.strftime('%Y-%m-%d', time.localtime(mid - 1))
    day2 = time.strftime('%Y-%m-%d', time.localtime(mid + 1))
    n1 = sum(1 for _ in open('%s/%s.jsonl' % (ld, day1)))
    n2 = sum(1 for _ in open('%s/%s.jsonl' % (ld, day2)))
    check('rotation: records before and after local midnight go to %s.jsonl and %s.jsonl' % (day1, day2),
          (n1, n2) == (2, 1), (n1, n2))
    check('rotation: log files are mode 0644', oct(os.stat('%s/%s.jsonl' % (ld, day1)).st_mode & 0o777) == '0o644',
          oct(os.stat('%s/%s.jsonl' % (ld, day1)).st_mode))

    # Unseen node opens and the races around a scan.
    d, recs = fresh()
    t = time.time()
    X = (200, 7000)
    info = {X: ('prog_x', 1, uid, 'bash')}
    # scan k: X is new, but its open event arrives only after the scan (it opened while the scan ran)
    d.apply({X: {0: {'ops'}}}, info, batch(), t)
    # scan k+1: its open event, no new holder: must not count as unseen
    d.apply({X: {0: {'ops'}}}, info, batch(((0, 'ops'), True, t + 0.01)), t + 0.1)
    # scan k+2: X went (exited during the scan) before its close event was read
    d.apply({}, {}, batch(), t + 0.2)
    # scan k+3: X's close event arrives
    d.apply({}, {}, batch(((0, 'ops'), False, t + 0.21)), t + 0.3)
    check('races: an open or close read one scan late is not an unseen hold',
          not [r for r in recs if r.get('unseen')], recs)
    # scan k+4: a real open and close between two scans
    d.apply({}, {}, batch(((0, 'ops'), True, t + 0.40), ((0, 'ops'), False, t + 0.405)), t + 0.5)
    check('unseen: the record waits a moment for a following one to join it', not [r for r in recs if r.get('unseen')]
          and 0 in d.pending, recs)
    d.flush_unseen(force=True)
    un = [r for r in recs if r.get('unseen')]
    check('unseen: an open and close between two scans is a "?" hold (start=open, end=close)',
          len(un) == 1 and un[0]['user'] == '?' and un[0]['nodes'] == ['ops'] and un[0]['opens'] == 1
          and abs(un[0]['start'] - (t + 0.40)) < 0.002 and abs(un[0]['end'] - (t + 0.405)) < 0.002, un)
    # an open, then the close only in the next batch (the process closed while the scan ran)
    recs.clear()
    d.apply({}, {}, batch(((0, 'mgmt'), True, t + 0.6)), t + 0.62)
    d.apply({}, {}, batch(((0, 'mgmt'), False, t + 0.63)), t + 0.7)
    d.flush_unseen(force=True)
    un = [r for r in recs if r.get('unseen')]
    check('unseen: an open carried to the next batch pairs with its close there',
          len(un) == 1 and un[0]['nodes'] == ['mgmt'] and abs(un[0]['start'] - (t + 0.6)) < 0.002, un)
    # a flood: 1000 opens and closes in one batch -> one record
    recs.clear()
    evs = []
    for i in range(1000):
        evs += [((0, 'ops'), True, t + 1 + i * 1e-4), ((0, 'ops'), False, t + 1 + i * 1e-4 + 5e-5)]
    d.apply({}, {}, batch(*evs), t + 1.2)
    d.flush_unseen(force=True)
    un = [r for r in recs if r.get('unseen')]
    check('flood: 1000 unseen opens in one batch make one record with opens=1000',
          len(un) == 1 and un[0]['opens'] == 1000, [(r.get('opens'), r['nodes']) for r in un])
    # lock opens are never unseen holds (every failed flock -n opens and closes the lock)
    recs.clear()
    d.apply({}, {}, batch(((0, 'lock'), True, t + 2), ((0, 'lock'), False, t + 2.001)), t + 2.1)
    d.flush_unseen(force=True)
    check('lock: an unseen open and close of a lock file writes nothing', not recs, recs)
    # an overflowed batch: no accounting
    b = batch(((0, 'ops'), True, t + 3), ((0, 'ops'), False, t + 3.001))
    b.overflow = True
    d.apply({}, {}, b, t + 3.1)
    d.flush_unseen(force=True)
    check('overflow: a batch with lost events accounts nothing', not recs, recs)
    # the lock pattern: flock opens the lock; timeout inherits it (no event of its own) in a later batch
    d, recs = fresh()
    F, T_, P = (300, 1), (301, 2), (302, 3)
    d.apply({F: {0: {'lock'}}}, {F: ('flock', 1, uid, 'bash')}, batch(((0, 'lock'), True, t)), t + 0.02)
    d.apply({F: {0: {'lock'}}, T_: {0: {'lock'}}, P: {0: {'lock', 'mgmt', 'ops'}}},
            {F: ('flock', 1, uid, 'bash'), T_: ('timeout', 300, uid, 'flock'), P: ('prog', 301, uid, 'timeout')},
            batch(((0, 'mgmt'), True, t + 0.1), ((0, 'ops'), True, t + 0.101)), t + 0.12)
    d.apply({}, {}, batch(((0, 'mgmt'), False, t + 2.0), ((0, 'ops'), False, t + 2.0), ((0, 'lock'), False,
                                                                                         t + 2.002)), t + 2.1)
    by = {r['comm']: r for r in recs if r['t'] == 'hold'}
    check('lock pattern: flock, timeout and the program each get a hold; none late, none unseen',
          set(by) == {'flock', 'timeout', 'prog'} and not any(r.get('late') or r.get('unseen') for r in recs), recs)
    check('lock pattern: timeout (no event of its own) starts at the card\'s first event and ends at the card\'s '
          'last close', abs(by['timeout']['start'] - (t + 0.1)) < 0.002 and abs(by['timeout']['end'] - (t + 2.002))
          < 0.002, by.get('timeout'))
    check('lock pattern: the program ends at its own last close; flock at the lock\'s close',
          abs(by['prog']['end'] - (t + 2.0)) < 0.002 and abs(by['flock']['end'] - (t + 2.002)) < 0.002, by)
    # a holder found by a scan with no event for its card is late
    d, recs = fresh()
    d.apply({(400, 1): {1: {'ops'}}}, {(400, 1): ('p', 1, uid, 'bash')}, batch(((0, 'ops'), True, t)), t + 5)
    check('late: a holder of a card with no event in the batch is late, start = the scan',
          d.holds[(400, 1, 1)].late and abs(d.holds[(400, 1, 1)].start - (t + 5)) < 0.002, vars_of(d, (400, 1, 1)))


def vars_of(d, k):
    h = d.holds.get(k)
    return {s: getattr(h, s) for s in h.__slots__} if h else None


# ============================================================================ the daemon, end to end
def e2e(env):
    print('\n== the daemon as a process (foreground, as uid %d)' % os.getuid())
    n = env.node
    t_begin = time.time()
    ready = env.root + '/tmp/pre.ready'
    p_pre = subprocess.Popen([env.fake_host, '--hold', '1000', '--ready', ready, n[(1, 'ops')]])
    wait_for(lambda: os.path.exists(ready), 5)
    denv = dict(os.environ, PYTHONDONTWRITEBYTECODE='1', ETU_AUDIT_LOG=env.audit, ETU_ROOT=env.root,
                ETU_SKIP_SYS=env.sys[1])
    err = open(env.root + '/daemon.err', 'w')
    # The daemon inherits fd 7 open on et1_mgmt: its own fds must never count.
    daemon = subprocess.Popen(['sh', '-c', 'exec 7<"$0"; exec "$@"', n[(1, 'mgmt')], sys.executable, env.wrap,
                               DAEMON, '--foreground'] + env.daemon_args(), stdout=err, stderr=err, env=denv)
    children = [p_pre]
    try:
        ok = wait_for(lambda: env.now() is not None, 8)
        check('start: now.json appears', ok, open(env.root + '/daemon.err').read())
        if not ok:
            return daemon
        check('start: now.json is mode 0644', oct(os.stat(env.root + '/run/now.json').st_mode & 0o777) == '0o644')
        st = [r for r in env.records() if r['t'] == 'start']
        check('start: one start record, cards [0, 1], 6 watched paths (et0_other ignored)',
              len(st) == 1 and st[0]['cards'] == [0, 1] and len(st[0]['watch']) == 6 and st[0]['pid'] == daemon.pid,
              st)
        pre = env.now_holds(pid=p_pre.pid)
        check('pre: a process holding et1_ops before the start is in now.json, pre, nodes [ops]',
              len(pre) == 1 and pre[0]['card'] == 1 and pre[0]['nodes'] == ['ops'] and pre[0].get('pre')
              and pre[0]['user'] == ME and abs(pre[0]['start'] - st[0]['at']) < 0.01, env.now())
        check('own fds: the daemon (holding et1_mgmt itself) never counts itself',
              not env.now_holds(pid=daemon.pid))

        # ---- flock -n <lock> timeout 5 <prog>
        t0 = time.time()
        p = subprocess.Popen(['flock', '-n', env.lock[0], 'timeout', '5', env.fake_host, '--hold', '1.5',
                              n[(0, 'mgmt')], n[(0, 'ops')]])
        children.append(p)
        seen = wait_for(lambda: env.now_holds(comm='fake_host', card=0), 1.2, 0.02)
        check('flock pattern: while it runs, now.json shows fake_host holding mgmt+ops+lock',
              seen and seen[0]['nodes'] == ['mgmt', 'ops'] and seen[0]['lock'] is True, env.now())
        comms = sorted(h['comm'] for h in env.now_holds(card=0))
        check('flock pattern: now.json also shows flock and timeout (lock only)', comms == ['fake_host', 'flock',
                                                                                          'timeout'], comms)
        p.wait()
        t1 = time.time()
        wait_for(lambda: len(env.holds(since=t0, card=0)) >= 3, 3)
        by = {r['comm']: r for r in env.holds(since=t0, card=0)}
        fh = by.get('fake_host', {})
        check('flock pattern: fake_host hold: nodes [mgmt, ops], lock, parent timeout, my user and uid',
              fh.get('nodes') == ['mgmt', 'ops'] and fh.get('lock') is True and fh.get('parent') == 'timeout'
              and fh.get('user') == ME and fh.get('uid') == os.getuid() and not fh.get('late'), fh)
        dur = fh.get('end', 0) - fh.get('start', 0)
        check('flock pattern: fake_host held for its 1.5 s (measured %.3f s)' % dur, 1.4 <= dur <= 1.75, fh)
        check('flock pattern: timeout and flock are lock-only holds (parents flock and python3)',
              by.get('timeout', {}).get('nodes') == [] and by.get('timeout', {}).get('parent') == 'flock'
              and by.get('flock', {}).get('lock') is True and by.get('flock', {}).get('nodes') == [], by)
        check('flock pattern: flock\'s hold covers the program\'s', by.get('flock', {}).get('start', 1e20) <=
              fh.get('start', 0) + 0.01 and by.get('flock', {}).get('end', 0) >= fh.get('end', 1e20) - 0.01
              and by['flock']['end'] <= t1 + 0.05, by)

        # ---- unseen: opens and closes faster than the debounce
        t0 = time.time()
        for _ in range(5):
            os.close(os.open(n[(0, 'ops')], os.O_RDONLY))
            time.sleep(0.3)
        for _ in range(3):
            os.close(os.open(env.lock[0], os.O_RDONLY))
            time.sleep(0.2)
        wait_for(lambda: sum(r['opens'] for r in env.holds(since=t0, unseen=True)) >= 5, 4)
        un = env.holds(since=t0, unseen=True)
        check('unseen: 5 quick open/close of et0_ops are 5 "?" holds of ops (user "?")',
              sum(r['opens'] for r in un) == 5 and all(r['user'] == '?' and r['nodes'] == ['ops'] for r in un),
              (sum(r['opens'] for r in un), [(r['nodes'], r['user'], r.get('opens')) for r in un]))
        check('unseen: 3 quick open/close of the lock write nothing',
              not [r for r in env.holds(since=t0) if not r.get('unseen')], env.holds(since=t0))

        # ---- the driver counters: an increase, a reset, a skipped card
        t0 = time.time()
        env.set_counts(0, 10, 150)
        a1 = wait_for(lambda: [r for r in env.records() if r['t'] == 'act' and r['at'] >= t0], 4)
        check('counters: +50 ops is an act record (mgmt 0, ops 50, s about 1)',
              a1 and a1[0]['card'] == 0 and a1[0]['mgmt'] == 0 and a1[0]['ops'] == 50 and 0.5 < a1[0]['s'] < 2.5, a1)
        t0 = time.time()
        env.set_counts(0, 10, 20)
        env.set_counts(1, 50, 500)
        time.sleep(2.5)
        acts = [r for r in env.records() if r['t'] == 'act' and r['at'] >= t0]
        check('counters: a counter that went down (driver reload) writes nothing', not acts, acts)
        t0 = time.time()
        env.set_counts(0, 13, 27)
        a2 = wait_for(lambda: [r for r in env.records() if r['t'] == 'act' and r['at'] >= t0], 4)
        check('counters: after the reset, the new baseline: mgmt +3, ops +7',
              a2 and (a2[0]['mgmt'], a2[0]['ops']) == (3, 7), a2)
        check('counters: never an act record for card 1 (--skip-counters 1)',
              not [r for r in env.records() if r['t'] == 'act' and r['card'] == 1])

        # ---- a node deleted and recreated while held
        ready = env.root + '/tmp/del.ready'
        p_del = subprocess.Popen([env.fake_host, '--hold', '1000', '--ready', ready, n[(0, 'ops')]])
        children.append(p_del)
        wait_for(lambda: os.path.exists(ready) and env.now_holds(pid=p_del.pid), 3)
        t0 = time.time()
        os.unlink(n[(0, 'ops')])
        write(n[(0, 'ops')], '', 0o666)
        w = wait_for(lambda: [r for r in env.records() if r['t'] == 'watch' and r['at'] >= t0
                              and n[(0, 'ops')] in r.get('added', [])], 3)
        check('recreated node: a watch record, and the new inode is watched', w, w)
        time.sleep(2.3)          # a safety-net scan runs: the holder's link now reads "... (deleted)"
        link = [os.readlink('/proc/%d/fd/%s' % (p_del.pid, fd)) for fd in os.listdir('/proc/%d/fd' % p_del.pid)]
        check('recreated node: the holder\'s fd link reads "(deleted)"', any(l.endswith(' (deleted)') for l in link),
              link)
        check('recreated node: the holder of the deleted node is still in now.json (card 0, ops)',
              env.now_holds(pid=p_del.pid, card=0), env.now())
        t0 = time.time()
        p = subprocess.Popen([env.fake_host, '--hold', '0.8', n[(0, 'ops')]])
        p.wait()
        r = wait_for(lambda: env.holds(since=t0, pid=p.pid), 3)
        check('recreated node: a new opener of the new node is seen from its open event (not late), 0.8 s',
              r and not r[0].get('late') and 0.7 <= r[0]['end'] - r[0]['start'] <= 1.0, r)
        t_kill = time.time()
        p_del.terminate()
        p_del.wait()
        r = wait_for(lambda: env.holds(since=t_kill - 1, pid=p_del.pid), 3)
        check('recreated node: the old holder\'s end comes from the close on the old inode (within 0.3 s of the kill)',
              r and r[0]['nodes'] == ['ops'] and -0.05 <= r[0]['end'] - t_kill <= 0.3, (r, t_kill))

        # ---- a late holder: a forked child inherits the fds (no open event), found by the safety-net scan
        t0 = time.time()
        p = subprocess.Popen([env.fake_host, '--hold', '2.6', '--fork-after', '0.4', n[(0, 'mgmt')]])
        p.wait()
        rs = wait_for(lambda: len(env.holds(since=t0, card=0, comm='fake_host')) >= 2, 3) and \
            env.holds(since=t0, card=0, comm='fake_host')
        late = [r for r in rs or [] if r.get('late')]
        check('late: the forked child is found by the 2 s scan and marked late; its parent is not',
              len(rs or []) == 2 and len(late) == 1 and late[0]['pid'] != p.pid, rs)

        # ---- a queue of short runs
        N = 40
        nj0 = env.now()
        t0 = time.time()
        for _ in range(N):
            subprocess.run(['flock', env.lock[0], 'timeout', '5', env.fake_host, '--hold', '0.05', n[(0, 'mgmt')],
                            n[(0, 'ops')]])
        time.sleep(2.0)          # the last unseen record is written about a second after the last run
        t1 = time.time()
        # a run is a node-holding fake_host hold, or an unseen open; a fake_host seen holding only the lock it
        # inherited from flock while its node open and close fell between two scans is a lock-only hold
        fh = env.holds(since=t0, card=0, comm='fake_host')
        seen = [r for r in fh if r['nodes']]
        un = env.holds(since=t0, card=0, unseen=True)
        total = len(seen) + sum(r['opens'] for r in un)
        check('queue: %d short runs (0.05 s each) are %d runs: %d seen, %d unseen (%d fake_host seen with the lock '
              'only)' % (N, total, len(seen), total - len(seen), len(fh) - len(seen)),
              abs(total - N) <= 3, (len(seen), [(r['opens'], r['nodes']) for r in un]))
        # (exact for seen runs; a run whose mgmt and ops events fall into two batches can be counted 0 or 2 times, and a
        # holder the walk finds before its open event is read uses up an earlier run's open. Measured on aifoundry2,
        # 8 trials each: the original daemon -2..0, this one -1..0; -3 once in a full run on a loaded host.)
        check('queue: unseen opens under one user\'s lock carry lock_user (most of them, counted in opens: unseen '
              'records of a burst are one record)',
              sum(r['opens'] for r in un if r.get('lock_user') == ME) >= 0.8 * sum(r['opens'] for r in un), un)
        nj1 = env.now()
        rate = (nj1['stats']['scans'] - nj0['stats']['scans']) / (t1 - t0)
        check('queue: at most 10 scans a second (%.1f/s)' % rate, rate <= 10.5, rate)

        # ---- a flood of opens (node and lock), then a normal run
        t0 = time.time()
        flood = subprocess.run([sys.executable, '-c',
                                'import os,sys\nfor i in range(20000):\n'
                                ' os.close(os.open(sys.argv[1],0)); os.close(os.open(sys.argv[2],0))',
                                n[(0, 'mgmt')], env.lock[0]])
        t1 = time.time()
        time.sleep(1.2)          # now.json (and its stats) is rewritten every second here
        nrec = len([r for r in env.records() if r.get('end', r.get('at', 0)) >= t0])
        check('flood: 40,000 opens and closes in %.2f s: daemon alive, %d records (at most ~10 a second)' % (
            t1 - t0, nrec), daemon.poll() is None and flood.returncode == 0 and nrec <= 10 * (t1 - t0 + 1) + 5,
              nrec)
        print('      (daemon stats: %s)' % env.now()['stats'])
        t0 = time.time()
        p = subprocess.Popen([env.fake_host, '--hold', '0.5', n[(0, 'mgmt')]])
        p.wait()
        r = wait_for(lambda: env.holds(since=t0, pid=p.pid), 3)
        check('flood: afterwards a normal run is seen as usual', r and 0.4 <= r[0]['end'] - r[0]['start'] <= 0.7, r)

        # ---- a holder in another PID (and user) namespace
        t0 = time.time()
        p = subprocess.run(['unshare', '--user', '--map-root-user', '--pid', '--fork', env.fake_host, '--hold', '0.8',
                            n[(0, 'ops')]], capture_output=True, text=True)
        if p.returncode != 0:
            print('SKIP  other PID namespace: unshare failed: %s' % p.stderr.strip())
        else:
            r = wait_for(lambda: env.holds(since=t0, comm='fake_host', card=0), 3)
            check('pid namespace: a holder in another PID namespace is logged under its host pid and host uid',
                  r and r[0]['uid'] == os.getuid() and r[0]['user'] == ME and r[0]['parent'] == 'unshare'
                  and 0.6 <= r[0]['end'] - r[0]['start'] <= 1.0, r)

        # ---- SIGTERM while holding
        ready = env.root + '/tmp/hold.ready'
        p_hold = subprocess.Popen([env.fake_host, '--hold', '1000', '--ready', ready, n[(0, 'mgmt')]])
        children.append(p_hold)
        wait_for(lambda: os.path.exists(ready) and env.now_holds(pid=p_hold.pid), 3)
        daemon.send_signal(signal.SIGTERM)
        rc = daemon.wait(10)
        check('SIGTERM: the daemon exits 0', rc == 0, rc)
        recs = env.records()
        stop = recs[-1]
        cut = [r for r in recs if r.get('cut')]
        check('SIGTERM: open holds are written with cut and end = the stop time, then the stop record',
              stop['t'] == 'stop' and {r['pid'] for r in cut} == {p_pre.pid, p_hold.pid}
              and all(abs(r['end'] - stop['at']) < 0.01 for r in cut), (stop, cut))
        pre = [r for r in cut if r['pid'] == p_pre.pid]
        check('SIGTERM: the holder present at start has pre and starts at the daemon\'s start',
              pre and pre[0].get('pre') and abs(pre[0]['start'] - st[0]['at']) < 0.01, pre)
        check('SIGTERM: now.json is removed', not os.path.exists(env.root + '/run/now.json'))
        check('own fds: no record ever names the daemon\'s pid',
              not [r for r in recs if r.get('pid') == daemon.pid and r['t'] == 'hold'])
        beats = [r for r in recs if r['t'] == 'beat']
        check('beat: heartbeats written (every 3 s here)', len(beats) >= int((stop['at'] - st[0]['at']) / 3) - 1,
              len(beats))
    finally:
        for c in children:
            if c.poll() is None:
                c.terminate()
                c.wait()
        if daemon.poll() is None:
            daemon.kill()
            daemon.wait()
        err.close()
    aud = open(env.audit).read()
    check('safety: the daemon never opened a node, a forbidden or skipped sysfs file, or wrote sysfs (audit hook)',
          aud == '', aud)
    errtxt = open(env.root + '/daemon.err').read()
    check('daemon stderr has no traceback', 'Traceback' not in errtxt, errtxt[-2000:])
    print('      (the run took %.1f s; daemon stderr in %s/daemon.err)' % (time.time() - t_begin, env.root))
    return daemon


def cli_live(env):
    print('\n== et-usage on the live test log')
    L = ['--log-dir', env.root + '/log', '--run-dir', env.root + '/run']
    p = cli(['--json', '--since', '1h'] + L)
    check('cli --json exits 0', p.returncode == 0, p.stderr)
    o = json.loads(p.stdout)
    recs = env.records()
    st = [r for r in recs if r['t'] == 'start'][0]
    sp = [r for r in recs if r['t'] == 'stop'][0]
    check('cli --json: daemon stale (stopped), stopped_at = the stop record',
          o['daemon']['state'] == 'stale' and abs(o['daemon'].get('stopped_at', 0) - sp['at']) < 0.01, o['daemon'])
    check('cli --json: coverage is one span from start to stop', len(o['coverage']) == 1
          and abs(o['coverage'][0][0] - st['at']) < 0.01 and abs(o['coverage'][0][1] - sp['at']) < 0.01,
          o['coverage'])
    c0 = o['cards'].get('0', {})
    u = c0.get('users', {}).get(ME, {})
    check('cli --json: card 0: my user with runs, fake_host among programs, a "?" user',
          u.get('runs', 0) >= 20 and 'fake_host' in u.get('programs', {}) and '?' in c0.get('users', {}), u)
    acts = [(a[2], a[3]) for a in c0.get('activity', [])]
    check('cli --json: card 0 activity has (0, 50) and (3, 7); card 1 none',
          (0, 50) in acts and (3, 7) in acts and not o['cards'].get('1', {}).get('activity'), acts)
    check('cli --json: card 1: my user (the pre holder) and no "now" (the daemon stopped)',
          ME in o['cards'].get('1', {}).get('users', {}) and o['cards']['1']['now'] == [], o['cards'].get('1'))
    check('cli --json: no line skipped', o['skipped'] == 0, o['skipped'])
    nrec = len([r for r in recs if r.get('end', r.get('at')) >= o['since']])
    p = cli(['--raw', '--since', '1h'] + L)
    lines = [ln for ln in p.stdout.split('\n') if ln]
    check('cli --raw prints every record of the window (%d)' % nrec, len(lines) == nrec, (len(lines), nrec))
    p = cli(['--since', '1h'] + L)
    out = p.stdout
    check('cli default: a summary naming card 0, me, fake_host, NOT RUNNING, logging since',
          all(s in out for s in ('Card 0', ME, 'fake_host', 'NOT RUNNING', 'logging since')), out)
    print('      --- et-usage (default output) ---\n' + '\n'.join('      ' + ln for ln in out.split('\n')))
    p = cli(['--json', '--since', '1h', '--user', ME, '--card', '0'] + L)
    o = json.loads(p.stdout)
    check('cli --user/--card filter', list(o['cards']) == ['0'] and list(o['cards']['0']['users']) == [ME],
          list(o['cards']))


# ============================================================================ the CLI on a synthetic log
def synth_log(dirpath, tz):
    """Three days of records, in local time of tz. Returns the epoch of 'now' and helper values."""
    old = os.environ.get('TZ')
    os.environ['TZ'] = tz
    time.tzset()
    try:
        def T(date, hh, mm, ss=0.0):
            y, m, d = (int(x) for x in date.split('-'))
            return time.mktime((y, m, d, hh, mm, 0, 0, 0, -1)) + ss
        D2, D1, D0 = '2026-09-28', '2026-09-29', '2026-09-30'
        now = T(D0, 12, 0)
        recs = []

        def beat(t):
            recs.append({'t': 'beat', 'v': 1, 'at': t, 'holding': 0})

        def hold(card, user, pid, comm, s, e, nodes=('ops',), lock=True, **kw):
            r = {'t': 'hold', 'v': 1, 'card': card, 'pid': pid, 'user': user, 'uid': 1000, 'comm': comm,
                 'parent': 'timeout', 'nodes': list(nodes), 'lock': lock, 'start': s, 'end': e}
            r.update(kw)
            recs.append(r)
        # span 1: D2 10:00-12:00, stopped
        recs.append({'t': 'start', 'v': 1, 'at': T(D2, 10, 0), 'host': 'synthhost', 'boot': 'b', 'pid': 1,
                     'cards': [0, 1], 'watch': []})
        for k in range(1, 12):
            beat(T(D2, 10, 0) + 600 * k)
        hold(0, 'alice', 101, 'fake_a', T(D2, 10, 10), T(D2, 10, 20))
        hold(0, 'alice', 102, 'fake_a', T(D2, 10, 20, 3), T(D2, 10, 25))
        hold(0, 'bob', 201, 'flock', T(D2, 11, 0), T(D2, 11, 5), nodes=())
        recs.append({'t': 'stop', 'v': 1, 'at': T(D2, 12, 0)})
        # span 2: D2 23:00 - D1 03:00, a 30 min silence, D1 03:30 - D1 15:00, then a start with no stop (a crash)
        recs.append({'t': 'start', 'v': 1, 'at': T(D2, 23, 0), 'host': 'synthhost', 'boot': 'b', 'pid': 2,
                     'cards': [0, 1], 'watch': []})
        t = T(D2, 23, 10)
        while t <= T(D1, 15, 0) + 1:
            if not T(D1, 3, 0) < t < T(D1, 3, 30):
                beat(t)
            t += 600
        hold(0, 'dave', 301, 'prog_d', T(D2, 23, 50), T(D1, 0, 10), nodes=('mgmt', 'ops'))
        hold(0, '?', None, '?', T(D1, 9, 0), T(D1, 9, 0, 0.01), lock=False, unseen=True, opens=2)
        recs.append({'t': 'start', 'v': 1, 'at': T(D1, 15, 30), 'host': 'synthhost', 'boot': 'b', 'pid': 3,
                     'cards': [0, 1], 'watch': []})
        t = T(D1, 15, 40)
        while t <= now - 300:
            beat(t)
            t += 600
        hold(1, 'erin', 401, 'prog_e', T(D0, 8, 0), T(D0, 8, 30))
        recs.append({'t': 'act', 'v': 1, 'card': 0, 'at': T(D0, 11, 0), 's': 60.0, 'mgmt': 1, 'ops': 20})
        recs.sort(key=lambda r: r.get('at', r.get('end')))
        files = {}
        for r in recs:
            files.setdefault(time.strftime('%Y-%m-%d', time.localtime(r.get('at', r.get('end')))), []).append(
                json.dumps(r))
        files.setdefault(D0, []).append('this is not json')
        files[D0].append(json.dumps({'t': 'hold', 'v': 2, 'card': 0, 'start': 1, 'end': 2, 'user': 'x'}))
        files[D0].append(json.dumps({'t': 'future', 'v': 1, 'at': now - 100}))
        os.makedirs(dirpath + '/log', exist_ok=True)
        os.makedirs(dirpath + '/run', exist_ok=True)
        for date, lines in files.items():
            with open('%s/log/%s.jsonl' % (dirpath, date), 'w') as f:
                f.write('\n'.join(lines) + '\n')
        nowj = {'v': 1, 'host': 'synthhost', 'at': now - 10, 'started_at': T(D1, 15, 30), 'pid': 3, 'boot': 'b',
                'cards': [0, 1], 'holds': [{'card': 0, 'pid': 501, 'user': 'carol', 'uid': 1003, 'comm': 'prog_c',
                                            'parent': 'timeout', 'nodes': ['ops'], 'lock': True, 'start': now - 600}]}
        with open(dirpath + '/run/now.json', 'w') as f:
            json.dump(nowj, f)
        return now, T, (D2, D1, D0), nowj
    finally:
        if old is None:
            del os.environ['TZ']
        else:
            os.environ['TZ'] = old
        time.tzset()


def cli_synth(env):
    print('\n== et-usage on a synthetic 3-day log (TZ=America/Los_Angeles)')
    tz = 'America/Los_Angeles'
    sd = env.root + '/synth'
    now, T, (D2, D1, D0), nowj = synth_log(sd, tz)
    L = ['--log-dir', sd + '/log', '--run-dir', sd + '/run', '--now', str(now)]
    E = {'TZ': tz}

    def js(*a, e=E):
        p = cli(['--json'] + list(a) + L, extra_env=e)
        if p.returncode != 0:
            print(p.stderr)
        return json.loads(p.stdout)
    o = js('--since', '3d')
    check('synth: daemon running (now.json 10 s old), started_at from now.json',
          o['daemon']['state'] == 'running' and o['daemon']['started_at'] == round(T(D1, 15, 30), 3), o['daemon'])
    cov = o['coverage']
    want = [[T(D2, 10, 0), T(D2, 12, 0)], [T(D2, 23, 0), T(D1, 3, 0)], [T(D1, 3, 30), T(D1, 15, 0)],
            [T(D1, 15, 30), now]]
    check('synth: coverage: a stopped span, a 30-min silence and a start with no stop end spans at the last record',
          [[round(a), round(b)] for a, b in cov] == [[round(a), round(b)] for a, b in want],
          [[time.strftime('%d %H:%M', time.localtime(x)) for x in s] for s in cov])
    c0 = o['cards']['0']
    al = [iv for iv in c0['intervals'] if iv['user'] == 'alice']
    check('synth: --gap 5 merges alice\'s two holds 3 s apart into one interval (node_s = 897 s)',
          len(al) == 1 and abs(al[0]['node_s'] - 897) < 0.01 and al[0]['procs'] == 2
          and al[0]['programs'] == {'fake_a': 2}, al)
    o1 = js('--since', '3d', '--gap', '1')
    check('synth: --gap 1 keeps them apart', len([iv for iv in o1['cards']['0']['intervals']
                                                    if iv['user'] == 'alice']) == 2)
    us = c0['users']
    check('synth: users: alice 897 s / 2 runs; bob lock-only (node_s 0, runs 0, programs flock); dave 1200 s',
          abs(us['alice']['held_s'] - 897) < 0.01 and us['alice']['runs'] == 2 and us['bob']['node_s'] == 0
          and us['bob']['runs'] == 0 and us['bob']['programs'] == {'flock': 1}
          and abs(us['dave']['held_s'] - 1200) < 0.01, us)
    check('synth: an unseen record counts its opens as runs of user "?"', us.get('?', {}).get('runs') == 2,
          us.get('?'))
    ca = [iv for iv in c0['intervals'] if iv['user'] == 'carol']
    check('synth: an open hold from now.json ends now, open: true; now lists carol',
          ca and ca[0].get('open') and ca[0]['end'] == round(now, 3) and abs(us['carol']['held_s'] - 600) < 0.01
          and c0['now'] and c0['now'][0]['user'] == 'carol', (ca, c0['now']))
    check('synth: card held_s is the union over users', abs(c0['held_s'] - (897 + 300 + 1200 + 0.01 + 600)) < 0.02,
          c0['held_s'])
    dly = c0['daily']
    check('synth: daily has the last 7 local dates, oldest first', list(dly) == [
        (datetime.date.fromisoformat(D0) - datetime.timedelta(days=k)).isoformat() for k in range(6, -1, -1)],
        list(dly))
    check('synth: daily splits dave\'s hold across local midnight (600 s + 600 s)',
          abs(dly[D2]['dave']['held_s'] - 600) < 0.01 and abs(dly[D1]['dave']['held_s'] - 600) < 0.01, dly)
    check('synth: daily_logged_s for %s is 2 h + 1 h' % D2, abs(o['daily_logged_s'][D2] - 10800) < 1,
          o['daily_logged_s'])
    check('synth: card 1: erin 1800 s; card 0 activity [at, 60, 1, 20]',
          abs(o['cards']['1']['users']['erin']['held_s'] - 1800) < 0.01
          and c0['activity'] == [[round(T(D0, 11, 0), 3), 60.0, 1, 20]], (o['cards']['1']['users'], c0['activity']))
    check('synth: a malformed line and a v2 line are skipped (2); an unknown v1 type is ignored',
          o['skipped'] == 2, o['skipped'])
    o2 = js('--since', '1h')
    check('synth: --since 1h: only carol in users; daily still has 7 days with alice on %s' % D2,
          list(o2['cards']['0']['users']) == ['carol'] and 'alice' in o2['cards']['0']['daily'][D2],
          list(o2['cards']['0']['users']))
    o3 = js('--since', '3d', e={'TZ': 'UTC'})
    d3 = o3['cards']['0']['daily']
    check('synth: TZ=UTC: same totals; dave\'s hold (23:50-00:10 PDT) falls on one UTC date',
          abs(o3['cards']['0']['users']['alice']['held_s'] - 897) < 0.01
          and abs(d3[D1]['dave']['held_s'] - 1200) < 0.01, d3.get(D1))
    o4 = js('--since', D1)
    check('synth: --since <ISO date> is local midnight', abs(o4['since'] - T(D1, 0, 0)) < 0.01, o4['since'])
    o5 = js('--since', str(int(T(D1, 12, 0))))
    check('synth: --since <epoch>', abs(o5['since'] - T(D1, 12, 0)) < 0.01, o5['since'])
    # stale and absent
    nowj2 = dict(nowj, at=now - 400)
    with open(sd + '/run/now.json', 'w') as f:
        json.dump(nowj2, f)
    o6 = js('--since', '3d')
    ca = [iv for iv in o6['cards']['0']['intervals'] if iv['user'] == 'carol']
    check('synth: now.json 400 s old: stale; carol\'s hold ends at now.json\'s time, not open; now empty',
          o6['daemon']['state'] == 'stale' and ca and not ca[0].get('open')
          and ca[0]['end'] == round(now - 400, 3) and o6['cards']['0']['now'] == [], (o6['daemon'], ca))
    p = cli(['--since', '3d', '--daily'] + L, extra_env=E)
    check('synth: default output for a stale logger says NOT RUNNING and lists the days',
          'NOT RUNNING' in p.stdout and 'By day' in p.stdout, p.stdout)
    os.makedirs(sd + '/empty', exist_ok=True)
    p = cli(['--json', '--log-dir', sd + '/empty', '--run-dir', sd + '/empty'])
    o7 = json.loads(p.stdout)
    check('synth: no log and no now.json: absent, no cards, no coverage',
          o7['daemon']['state'] == 'absent' and o7['cards'] == {} and o7['coverage'] == [], o7)
    p = cli(['--log-dir', sd + '/empty', '--run-dir', sd + '/empty'])
    check('synth: default output when absent', p.returncode == 0 and 'absent' in p.stdout, p.stdout)
    # a busy day: more than 2,000 intervals are merged further, and the output stays small
    bd = env.root + '/busy'
    os.makedirs(bd + '/log', exist_ok=True)
    t0 = now - 86400 + 60
    lines = [json.dumps({'t': 'start', 'v': 1, 'at': t0 - 1, 'host': 'h', 'boot': 'b', 'pid': 1, 'cards': [0],
                         'watch': []})]
    for i in range(3000):
        s = t0 + i * 25
        lines.append(json.dumps({'t': 'hold', 'v': 1, 'card': 0, 'pid': 10000 + i, 'user': 'u%d' % (i % 3),
                                 'uid': 1, 'comm': 'prog', 'parent': 'timeout', 'nodes': ['ops'], 'lock': True,
                                 'start': s, 'end': s + 2}))
        if i % 20 == 0:
            lines.append(json.dumps({'t': 'beat', 'v': 1, 'at': s + 3, 'holding': 0}))
    by_date = {}
    for ln in lines:
        r = json.loads(ln)
        by_date.setdefault(time.strftime('%Y-%m-%d', time.localtime(r.get('at', r.get('end')))), []).append(ln)
    for date, ls in by_date.items():
        with open('%s/log/%s.jsonl' % (bd, date), 'w') as f:
            f.write('\n'.join(ls) + '\n')
    p = cli(['--json', '--since', '26h', '--log-dir', bd + '/log', '--run-dir', bd, '--now', str(now)])
    o8 = json.loads(p.stdout)
    c = o8['cards']['0']
    check('busy: 3,000 runs: at most 2,000 intervals (merged_gap_s %s), output %d KB' % (
        c.get('merged_gap_s'), len(p.stdout) // 1024), len(c['intervals']) <= 2000 and c.get('merged_gap_s')
          and len(p.stdout) < 400 * 1024 and sum(u['runs'] for u in c['users'].values()) == 3000,
          (len(c['intervals']), c.get('merged_gap_s')))


# ============================================================================ the review fixes of 30 Sep: unit tests
def unit_fixes(env):
    print('\n== unit tests of the review fixes (the daemon imported as a module)')
    m = load_daemon_module()
    base = ['--stdout', '--dev-glob', env.root + '/dev/et[0-9]*_*',
            '--lock-glob', env.root + '/lock/etsoc-shire[0-9]*.lock']
    uid = os.getuid()

    def fresh(extra=()):
        d = m.Daemon(m.parse_args(base + list(extra)))
        d.log = lambda msg: None
        d.reglob(watch=False)
        recs = []
        d.emit = recs.append
        return d, recs

    def batch(*evs):
        b = m.Batch()
        for ck, is_open, t in evs:
            b.add(ck, is_open, t, m.boottime())
        return b

    t = time.time()
    # The driver opens a node once at a time: a seen holder's close and reopen of its own node is not a "?" run.
    d, recs = fresh()
    P = (600, 1)
    info = {P: ('prog', 1, uid, 'timeout')}
    d.apply({P: {0: {'ops', 'lock'}}}, info, batch(((0, 'ops'), True, t)), t + 0.02)
    d.apply({P: {0: {'ops', 'lock'}}}, info, batch(((0, 'ops'), False, t + 1.0), ((0, 'ops'), True, t + 1.001)),
            t + 1.02)
    d.flush_unseen(force=True)
    check('reopen: a holder seen at two scans that closes and reopens its node is not a "?" run',
          not [r for r in recs if r.get('unseen')], recs)
    d.apply({P: {0: {'ops', 'lock'}}}, info, batch(((0, 'mgmt'), True, t + 2.0), ((0, 'mgmt'), False, t + 2.005)),
            t + 2.1)
    d.flush_unseen(force=True)
    un = [r for r in recs if r.get('unseen')]
    check('reopen: a quick open and close of the other node meanwhile is one "?" run, lock_user = the lock holder',
          len(un) == 1 and un[0]['nodes'] == ['mgmt'] and un[0]['opens'] == 1 and un[0].get('lock_user') == ME, un)

    # A new holder starts at its own open, the last open of its node, not at an open carried from an earlier batch
    # (seen after the 40,000-open flood: the next run started 1.3 s early).
    d, recs = fresh()
    X = (610, 1)
    d.apply({}, {}, batch(((0, 'mgmt'), True, t)), t + 0.02)                  # its close falls in the next batch
    d.apply({X: {0: {'mgmt'}}}, {X: ('prog', 1, uid, 'bash')},
            batch(((0, 'mgmt'), False, t + 0.03), ((0, 'mgmt'), True, t + 1.3)), t + 1.32)
    d.flush_unseen(force=True)
    h = d.holds.get((610, 1, 0))
    un = [r for r in recs if r.get('unseen')]
    check('start: a new holder starts at its own open (+1.3 s), not at an open carried from the batch before',
          h and abs(h.start - (t + 1.3)) < 0.002 and len(un) == 1 and abs(un[0]['end'] - (t + 0.03)) < 0.002,
          (h and h.start - t, un))

    # Unseen records: one per burst (a poller or a queue of short runs), not one per scan.
    d, recs = fresh()
    for i in range(20):
        tt = t + i * 0.05
        d.apply({}, {}, batch(((0, 'ops'), True, tt), ((0, 'ops'), False, tt + 0.005)), tt + 0.02)
    for i in range(3):
        tt = t + 3 + i * 0.05
        d.apply({}, {}, batch(((0, 'ops'), True, tt), ((0, 'ops'), False, tt + 0.005)), tt + 0.02)
    d.flush_unseen(force=True)
    un = [r for r in recs if r.get('unseen')]
    check('unseen merge: 20 opens 50 ms apart are one record (opens 20, open of the first to close of the last); '
          'a burst 3 s later is another', [r['opens'] for r in un] == [20, 3] and abs(un[0]['start'] - t) < 0.002
          and abs(un[0]['end'] - (t + 0.955)) < 0.002, un)
    d, recs = fresh()
    A, B = (700, 1), (701, 1)
    d.apply({A: {0: {'lock'}}}, {A: ('flock', 1, uid, 'bash')}, batch(((0, 'lock'), True, t)), t + 0.01)
    d.holds[(700, 1, 0)].user = 'alice'
    d.apply({A: {0: {'lock'}}}, {}, batch(((0, 'ops'), True, t + 0.1), ((0, 'ops'), False, t + 0.105)), t + 0.12)
    d.apply({B: {0: {'lock'}}}, {B: ('flock', 1, uid, 'bash')},
            batch(((0, 'lock'), False, t + 0.2), ((0, 'lock'), True, t + 0.21)), t + 0.22)
    d.holds[(701, 1, 0)].user = 'bob'
    d.apply({B: {0: {'lock'}}}, {}, batch(((0, 'ops'), True, t + 0.3), ((0, 'ops'), False, t + 0.305)), t + 0.32)
    d.flush_unseen(force=True)
    un = [r for r in recs if r.get('unseen')]
    check('unseen merge: opens under different lock holders stay apart (lock_user alice, then bob)',
          [r.get('lock_user') for r in un] == ['alice', 'bob'], un)

    # A wall-clock step while the daemon sleeps in select, then an event: the clock is checked before the event is
    # read, so the event is not moved a second time.
    for step in (-3600.0, 3600.0):
        d, recs = fresh()
        ops = [p for p, ck in d.known.items() if ck == (0, 'ops')][0]

        class FakeIno:
            def read(self):
                return [(1, m.IN_OPEN, b'')]
        d.ino = FakeIno()
        d.wds = {1: ops}
        d.off = (time.time() - m.boottime()) - step      # the offset seen before the step
        t_ev = time.time()
        d.wake(True)                                     # select returned
        b, d.batch = d.batch, m.Batch()
        X = (500, 1)
        d.apply({X: {0: {'ops'}}}, {X: ('prog', 1, uid, 'bash')}, b, time.time())
        d.check_clock()                                  # the next pass
        h = d.holds[(500, 1, 0)]
        check('clock step %+.0f s during select: a hold opened after it starts at its open event (%+.3f s)' % (
            step, h.start - t_ev), abs(h.start - t_ev) < 0.5 and any(r['t'] == 'clock' for r in recs), h.start - t_ev)
    # ... and a step while a scan runs moves the scanned batch too.
    d, recs = fresh()
    step = -3600.0
    t_old = time.time() - step          # an open stamped by the clock before the step (an hour ahead)
    d.batch.add((0, 'ops'), True, t_old, m.boottime())

    def scan_with_step(maps=False):
        d.off = (time.time() - m.boottime()) - step     # the clock steps while the scan runs
        return {(501, 1): {0: {'ops'}}}, {(501, 1): ('prog', 1, uid, 'bash')}
    d.scan = scan_with_step
    d.do_scan()
    d.check_clock()
    h = d.holds[(501, 1, 0)]
    check('clock step during a scan: the hold starts at its open in the new clock (%+.3f s)' % (h.start - (t_old + step)),
          abs(h.start - (t_old + step)) < 0.5, h.start - (t_old + step))

    # CPU: the gap between scans is at least 10 x the last scan's duration; events on a lock file alone wait 1 s.
    d, recs = fresh()
    d.last_scan_b, d.last_scan_cpu = m.boottime(), 0.5
    g = d.scan_gap()
    d.batch.add((0, 'ops'), True, time.time(), m.boottime())
    due = d.scan_due() - d.last_scan_b
    check('scan duty: after a scan of 0.5 s of CPU the next one starts 5 s later at the earliest (gap %.2f s, due %.2f s)' % (
        g, due), abs(g - 5.0) < 1e-6 and due >= 5.0 - 1e-6, (g, due))
    d, recs = fresh()
    d.last_scan_b, d.last_scan_cpu = m.boottime(), 0.002
    d.batch.add((0, 'lock'), True, time.time(), m.boottime())
    lock_due = d.scan_due() - d.last_scan_b
    d.batch.add((0, 'mgmt'), True, time.time(), m.boottime())
    node_due = d.scan_due() - d.last_scan_b
    check('scan rate: lock-file events alone wait 1 s after the last scan (%.2f s); a node event 0.1 s (%.2f s)' % (
        lock_due, node_due), lock_due >= 0.999 and node_due <= 0.15, (lock_due, node_due))

    # /run/lock is world-writable: lock files only for cards that have a node, never a symlink; junk names ignored.
    gd = env.root + '/unitglob'
    for sub in ('dev', 'lock', 'elsewhere'):
        os.makedirs(gd + '/' + sub, exist_ok=True)
    for p in ('dev/et0_mgmt', 'dev/et0_ops', 'lock/etsoc-shire0.lock', 'dev/et3_mgmt', 'elsewhere/target'):
        write(gd + '/' + p, '')
    os.symlink(gd + '/elsewhere/target', gd + '/lock/etsoc-shire3.lock')     # card 3's lock name, a symlink
    os.symlink(gd + '/elsewhere/target', gd + '/dev/et7_ops')                # a node name, a symlink
    write(gd + '/lock/etsoc-shire7.lock', '')                                 # card 7 has no real node
    for n in range(100, 400):
        write('%s/lock/etsoc-shire%d.lock' % (gd, n), '')                     # cards that do not exist
    d = m.Daemon(m.parse_args(['--stdout', '--dev-glob', gd + '/dev/et[0-9]*_*',
                               '--lock-glob', gd + '/lock/etsoc-shire[0-9]*.lock']))
    d.log = lambda msg: None
    d.ino = m.Inotify()
    try:
        d.reglob()
        watched = sorted(os.path.relpath(p, gd) for p in d.watch)
        with open('/proc/self/fdinfo/%d' % d.ino.fd) as f:
            nwd = sum(1 for ln in f if ln.startswith('inotify wd:'))
        check('lock names: a lock is watched only for a card with a node, never through a symlink; 300 junk names '
              'ignored (%s; %d inotify watches)' % (', '.join(watched), nwd),
              watched == ['dev/et0_mgmt', 'dev/et0_ops', 'dev/et3_mgmt', 'lock/etsoc-shire0.lock'] and nwd == 6,
              (watched, nwd))
        check('lock names: a held junk lock that was deleted is no card; card 0\'s lock is card 0',
              d.match_deleted(gd + '/lock/etsoc-shire150.lock (deleted)') is None
              and d.match_deleted(gd + '/lock/etsoc-shire0.lock (deleted)') == (0, 'lock'))
    finally:
        os.close(d.ino.fd)

    check('printable: escape, control and format characters become "?"',
          m.printable('\x1b[2J\x07ok‮​ é') == '?[2J?ok?? é', m.printable('\x1b[2J\x07ok‮​'))

    # The driver's vq_stats race: an implausible jump is a new baseline, not activity.
    d, recs = fresh(['--sysfs-glob', env.root + '/sys/0000:*', '--skip-counters', '1'])
    try:
        d.counters_tick()
        env.set_counts(0, 10, 10 ** 15)
        d.counters_tick()
        env.set_counts(0, 12, 110)
        d.counters_tick()
        env.set_counts(0, 13, 117)
        d.counters_tick()
    finally:
        env.set_counts(0, 10, 100)
    acts = [(r['mgmt'], r['ops']) for r in recs if r['t'] == 'act']
    check('counters: a jump of 10^15 messages is no activity (a new baseline); the next real change is +1, +7',
          acts == [(1, 7)], acts)

    # The host's defaults file applies to every run (a manual --once too).
    df = env.root + '/unit/defaults'
    os.makedirs(env.root + '/unit', exist_ok=True)
    write(df, '# test\nET_USAGED_ARGS="--skip-counters 0 --skip-pci 0000:01:00.0"\n')
    a = m.parse_args(['--defaults', df, '--skip-counters', '1'])
    err = m.apply_defaults(a)
    check('defaults: its --skip-counters and --skip-pci add to the command line\'s',
          err is None and a.skip_counters == {0, 1} and a.skip_pci == {'0000:01:00.0'} and not a.skip_all_counters,
          (err, a.skip_counters, a.skip_pci))
    write(df, 'ET_USAGED_ARGS="--skip-counters zero\n')
    a = m.parse_args(['--defaults', df])
    err = m.apply_defaults(a)
    check('defaults: a file it cannot parse means no counter is read at all', err and a.skip_all_counters, err)
    a = m.parse_args(['--defaults', env.root + '/unit/no-such-file'])
    check('defaults: no file, nothing changes', m.apply_defaults(a) is None and not a.skip_all_counters
          and not a.skip_counters and not a.skip_pci)

    # Retention by age never removes one of the newest --keep-days files (a clock far ahead).
    today = datetime.date.today()
    ld = env.root + '/unit/ret'
    os.makedirs(ld, exist_ok=True)
    for k in range(5):
        write('%s/%s.jsonl' % (ld, today - datetime.timedelta(days=k)), '')
    d = m.Daemon(m.parse_args(['--log-dir', ld, '--run-dir', env.root + '/unit']))
    d.log = lambda msg: None
    real = m.time

    class FakeTime:
        def __getattr__(self, k):
            return getattr(real, k)

        def time(self):
            return real.time() + 400 * 86400

        def strftime(self, fmt, t=None):
            return real.strftime(fmt, t if t is not None else real.localtime(self.time()))
    m.time = FakeTime()
    try:
        d.retention()
    finally:
        m.time = real
    check('retention: a clock 400 days ahead removes none of 5 daily files', len(os.listdir(ld)) == 5, os.listdir(ld))
    ld = env.root + '/unit/ret95'
    os.makedirs(ld, exist_ok=True)
    names = ['%s.jsonl' % (today - datetime.timedelta(days=k)) for k in range(95)]
    for n in names:
        write(ld + '/' + n, '')
    d = m.Daemon(m.parse_args(['--log-dir', ld, '--run-dir', env.root + '/unit', '--keep-days', '90']))
    d.log = lambda msg: None
    d.retention()
    cutoff = time.strftime('%Y-%m-%d', time.localtime(time.time() - 90 * 86400))
    newest = set(sorted(names)[-90:])
    want = sorted(n for n in names if not (n[:10] < cutoff and n not in newest))
    left = sorted(os.listdir(ld))
    check('retention: of 95 daily files, the %d older than 90 days go' % (95 - len(want)),
          left == want and len(want) < 95, (len(left), len(want)))

    # The size cap and the free-space floor.
    ld = env.root + '/unit/cap'
    os.makedirs(ld, exist_ok=True)
    for k in range(5, 0, -1):
        write('%s/%s.jsonl' % (ld, today - datetime.timedelta(days=k)), 'x' * (300 * 1024))
    todayf = '%s/%s.jsonl' % (ld, today)
    write(todayf, 'x' * (100 * 1024))
    d = m.Daemon(m.parse_args(['--log-dir', ld, '--run-dir', env.root + '/unit', '--max-log-mb', '1',
                               '--min-free-mb', '0']))
    d.log = lambda msg: None
    d.check_space()
    left = sorted(os.listdir(ld))
    want = ['%s.jsonl' % (today - datetime.timedelta(days=k)) for k in (3, 2, 1)] + ['%s.jsonl' % today]
    check('size cap: the oldest days go until the directory is under --max-log-mb 1 (%s)' % left,
          left == want and not d.paused, left)
    write(todayf, 'x' * (2 * 1024 * 1024))
    d.check_space()
    size0 = os.path.getsize(todayf)
    d.emit({'t': 'beat', 'v': 1, 'at': time.time(), 'holding': 0})
    check('size cap: today\'s file alone over it: the older days go, and records are counted, not written',
          sorted(os.listdir(ld)) == ['%s.jsonl' % today] and d.paused and os.path.getsize(todayf) == size0
          and d.stats['dropped'] == 1, (os.listdir(ld), d.paused, d.stats['dropped']))
    d.a.max_log_mb = 100
    d.check_space()
    d.emit({'t': 'beat', 'v': 1, 'at': time.time(), 'holding': 0})
    d.close_log()
    check('size cap: with room again, records are written again', not d.paused and os.path.getsize(todayf) > size0)
    for k in (9, 8, 7):
        write('%s/%s.jsonl' % (ld, today - datetime.timedelta(days=k)), 'x' * 1024)
    before = sorted(os.listdir(ld))
    d2 = m.Daemon(m.parse_args(['--log-dir', ld, '--run-dir', env.root + '/unit', '--min-free-mb', '1e12']))
    d2.log = lambda msg: None
    d2.check_space()
    check('free space: under --min-free-mb, records are not written (%s), and no day is removed for it (a user '
          'who fills a shared disk must not erase the history)' % d2.paused,
          d2.paused and 'free' in d2.paused and sorted(os.listdir(ld)) == before, (d2.paused, before,
                                                                                    sorted(os.listdir(ld))))

    # maps: read in pieces, at most MAX_MAPS bytes of one process (vm.max_map_count is 1,048,576 on the lab hosts:
    # read whole, a user's 100,000 mappings of a long path took 200 MB, over the unit's MemoryMax=64M).
    import tracemalloc
    md = env.root + '/unitmaps'
    pad = md + '/long/' + 'y' * 200
    os.makedirs(md + '/dev', exist_ok=True)
    os.makedirs(pad, exist_ok=True)
    for p in (pad + '/f', md + '/dev/et0_mgmt', md + '/dev/et0_ops'):
        write(p, '\0' * 4096)
    mapper = r'''
import ctypes, os, sys, time
libc = ctypes.CDLL("libc.so.6", use_errno=True)
libc.mmap.restype = ctypes.c_void_p
libc.mmap.argtypes = [ctypes.c_void_p, ctypes.c_size_t, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_long]
node, pad, n = sys.argv[1], sys.argv[2], int(sys.argv[3])
fd = os.open(node, os.O_RDONLY)
libc.mmap(None, 4096, 1, 2, fd, 0)       # the node first: mmap goes down, so it is listed after the padding
os.close(fd)                             # held through the mapping only
pf = os.open(pad, os.O_RDONLY)
k = 0
while k < n and libc.mmap(None, 4096, 1, 2, pf, 0) not in (None, ctypes.c_void_p(-1).value):
    k += 1
print(k, flush=True)
time.sleep(60)
'''
    try:
        maxmap = int(open('/proc/sys/vm/max_map_count').read())
    except (OSError, ValueError):
        maxmap = 65530
    procs = []

    def maps_size(pid):
        with open('/proc/%d/maps' % pid, 'rb') as f:
            return sum(len(b) for b in iter(lambda: f.read(1 << 20), b''))
    try:
        dm = m.Daemon(m.parse_args(['--stdout', '--dev-glob', md + '/dev/et[0-9]*_*', '--lock-glob',
                                    md + '/lock/etsoc-shire[0-9]*.lock']))
        dm.log = lambda msg: None
        dm.reglob(watch=False)
        small = subprocess.Popen([sys.executable, '-c', mapper, md + '/dev/et0_ops', pad + '/f', '3000'],
                                 stdout=subprocess.PIPE, text=True)
        procs.append(small)
        gone = subprocess.Popen([sys.executable, '-c', mapper, md + '/dev/et0_mgmt', pad + '/f', '10'],
                                stdout=subprocess.PIPE, text=True)
        procs.append(gone)
        big = subprocess.Popen([sys.executable, '-c', mapper, md + '/dev/et0_ops', pad + '/f',
                                str(min(80000, maxmap - 2000))], stdout=subprocess.PIPE, text=True)
        procs.append(big)
        nsmall, _, nbig = int(small.stdout.readline()), gone.stdout.readline(), int(big.stdout.readline())
        os.unlink(md + '/dev/et0_mgmt')                    # removed while mapped: "<path> (deleted)" in maps
        msize = maps_size(small.pid)
        got_small = dm.maps_of(str(small.pid))
        got_gone = dm.maps_of(str(gone.pid))
        tracemalloc.start()
        got_big = dm.maps_of(str(big.pid))
        peak = tracemalloc.get_traced_memory()[1]
        tracemalloc.stop()
        bsize = maps_size(big.pid)
        check('maps: a node mapped after %d other mappings (%d KB of maps, past the first piece) is found; a mapped '
              'node removed since ("(deleted)") too' % (nsmall, msize // 1024),
              got_small == {(0, 'ops')} and got_gone == {(0, 'mgmt')}, (got_small, got_gone))
        check('maps: a process with %d mappings (%.0f MB of maps) is read in pieces up to %d MB: peak %.1f MB of '
              'memory, counted in maps_truncated' % (nbig, bsize / m.MB, m.MAX_MAPS // m.MB, peak / m.MB),
              peak < 2 * m.MB and dm.stats['maps_truncated'] == 1 and bsize > m.MAX_MAPS and got_big == set(),
              (peak, dm.stats['maps_truncated'], bsize, got_big))
    finally:
        for p in procs:
            p.kill()
            p.wait()

    # open.json that is not the daemon's own is ignored, not trusted.
    rd = env.root + '/unit/rec'
    os.makedirs(rd, exist_ok=True)
    d = m.Daemon(m.parse_args(['--log-dir', rd, '--run-dir', rd]))
    d.log = lambda msg: None
    write(rd + '/open.json', '{"v":1,"at":1,"holds":[{"t":"hold","card":"x"},"junk",{"t":"hold","card":0,'
          '"start":0.5,"user":"u","pid":3}]}')
    got = d.recover()
    check('recover: only well-formed holds of open.json come back, with end = its time and lost_end',
          len(got) == 1 and got[0]['end'] == 1 and got[0]['lost_end'] is True, got)
    write(rd + '/open.json', 'not json')
    check('recover: an unreadable open.json is ignored', d.recover() == [])


# ============================================================================ the review fixes: the daemon as a process
def start_daemon(env, extra=(), audit_skip_sys=None, audit_skip_pci=None, err_name='daemon.err'):
    denv = dict(os.environ, PYTHONDONTWRITEBYTECODE='1', ETU_AUDIT_LOG=env.audit, ETU_ROOT=env.root,
                ETU_SKIP_SYS=audit_skip_sys or env.sys[1], ETU_SKIP_PCI=audit_skip_pci or '')
    err = open(env.root + '/' + err_name, 'a')
    p = subprocess.Popen([sys.executable, env.wrap, DAEMON, '--foreground'] + env.daemon_args() + list(extra),
                         stdout=err, stderr=err, env=denv)
    err.close()
    return p


def run_once(env, extra=(), audit_skip_sys=None, audit_skip_pci=None):
    denv = dict(os.environ, PYTHONDONTWRITEBYTECODE='1', ETU_AUDIT_LOG=env.audit, ETU_ROOT=env.root,
                ETU_SKIP_SYS=audit_skip_sys or '', ETU_SKIP_PCI=audit_skip_pci or '')
    r = env.root
    args = ['--once', '--dev-glob', r + '/dev/et[0-9]*_*', '--lock-glob', r + '/lock/etsoc-shire[0-9]*.lock',
            '--sysfs-glob', r + '/sys/0000:*', '--log-dir', r + '/log', '--run-dir', r + '/run']
    return subprocess.run([sys.executable, env.wrap, DAEMON] + args + list(extra), capture_output=True, text=True,
                          env=denv, timeout=60)


def inotify_watches(pid):
    for fd in os.listdir('/proc/%d/fd' % pid):
        try:
            if os.readlink('/proc/%d/fd/%s' % (pid, fd)) == 'anon_inode:inotify':
                with open('/proc/%d/fdinfo/%s' % (pid, fd)) as f:
                    return sum(1 for ln in f if ln.startswith('inotify wd:'))
        except OSError:
            continue
    return None


def vm_hwm_kb(pid):
    with open('/proc/%d/status' % pid) as f:
        for ln in f:
            if ln.startswith('VmHWM:'):
                return int(ln.split()[1])
    return None


def e2e_fixes(root):
    print('\n== the review fixes, with the daemon as a process (foreground, as uid %d)' % os.getuid())
    env = Env(root)
    n = env.node
    children = []
    d = start_daemon(env)
    d2 = None
    try:
        ok = wait_for(lambda: env.now() is not None, 8)
        check('fixes: the daemon starts', ok, open(env.root + '/daemon.err').read())
        if not ok:
            return
        st = [r for r in env.records() if r['t'] == 'start']
        check('sees_all: an ordinary user cannot read other users\' fd links: false in the start record and now.json',
              st and st[0].get('sees_all') is False and env.now().get('sees_all') is False, (st, env.now()))
        check('open.json: the open holds are kept in the log directory while the daemon runs',
              os.path.exists(env.root + '/log/open.json'))

        # ---- idle, it sleeps: the log-writing daemon, and one printing records (--stdout, nothing else to write)
        def cpu_s(pid):
            f = open('/proc/%d/stat' % pid).read().rsplit(')', 1)[1].split()
            return (int(f[11]) + int(f[12])) / os.sysconf('SC_CLK_TCK')
        c0 = cpu_s(d.pid)
        so = subprocess.Popen([sys.executable, DAEMON, '--foreground', '--stdout', '--defaults', 'none',
                               '--dev-glob', env.root + '/dev/et[0-9]*_*',
                               '--lock-glob', env.root + '/lock/etsoc-shire[0-9]*.lock',
                               '--sysfs-glob', env.root + '/sys/0000:*', '--skip-counters', '1'],
                              stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        children.append(so)
        time.sleep(3.0)
        busy = (cpu_s(d.pid) - c0, cpu_s(so.pid))
        so.terminate()
        so.wait()
        check('idle: 3 s idle cost %.2f s of CPU logging, %.2f s with --stdout (a busy loop would be 3 s)' % busy,
              busy[0] < 0.5 and busy[1] < 0.8, busy)

        # ---- a second daemon on the same log directory
        p = subprocess.run([sys.executable, DAEMON, '--foreground'] + env.daemon_args(), capture_output=True,
                           text=True, timeout=20)
        check('one writer: a second et-usaged on the same log directory exits 1 at once',
              p.returncode == 1 and 'another et-usaged' in p.stderr, (p.returncode, p.stderr[-300:]))

        # ---- a process waiting in flock, and a process with the lock file open but unlocked
        t0 = time.time()
        a = subprocess.Popen(['flock', env.lock[0], env.fake_host, '--hold', '3', n[(0, 'mgmt')], n[(0, 'ops')]])
        children.append(a)
        time.sleep(0.5)
        b = subprocess.Popen(['flock', env.lock[0], env.fake_host, '--hold', '0.3', n[(0, 'mgmt')], n[(0, 'ops')]])
        children.append(b)
        u = subprocess.Popen(['sh', '-c', 'exec 9<"$0"; sleep 2', env.lock[0]])
        children.append(u)
        time.sleep(1.5)
        waiting = env.now_holds(pid=b.pid) + env.now_holds(pid=u.pid)
        a.wait()
        b.wait()
        u.wait()
        time.sleep(1.5)
        recs = env.holds(since=t0, card=0)
        a_end = min((r['end'] for r in recs if r['pid'] == a.pid), default=None)
        fb = [r for r in recs if r['pid'] == b.pid]
        check('flock waiter: a process waiting in flock, or with the lock file open unlocked, is not in now.json',
              not waiting, waiting)
        check('flock waiter: the waiter\'s flock hold starts when it got the lock (after the holder\'s ended)',
              fb and a_end is not None and fb[0]['start'] >= a_end - 0.2 and fb[0]['lock'] is True,
              {'b': fb, 'a_end': a_end})
        check('flock waiter: an unlocked open of the lock file is no hold', not [r for r in recs if r['pid'] == u.pid],
              [r for r in recs if r['pid'] == u.pid])

        # ---- a program whose name holds terminal escapes
        esc = '\x1b[2J\x1b[1;1HFREE'
        t0 = time.time()
        ready = env.root + '/tmp/esc.ready'
        e = subprocess.Popen([env.fake_host, '--comm', esc, '--hold', '2.5', '--ready', ready, n[(0, 'ops')]])
        children.append(e)
        wait_for(lambda: os.path.exists(ready) and env.now_holds(pid=e.pid), 3)
        live = env.now_holds(pid=e.pid)
        once = run_once(env, ['--defaults', 'none'])
        e.wait()
        r = wait_for(lambda: env.holds(since=t0, pid=e.pid), 3)
        o = cli(['--json', '--since', '1h', '--log-dir', env.root + '/log', '--run-dir', env.root + '/run']).stdout
        want = '?[2J?[1;1HFREE'
        check('escapes: a program named with terminal escapes is "%s" in now.json and its hold record' % want,
              live and live[0]['comm'] == want and r and r[0]['comm'] == want, (live, r))
        check('escapes: none in et-usaged --once output (which lists it)', '\x1b' not in once.stdout
              and want in once.stdout, once.stdout)
        check('escapes: none in et-usage --json output', '\\u001b' not in o and '\x1b' not in o and want in o)
        check('escapes: none in the daemon\'s own messages (--foreground)',
              '\x1b' not in open(env.root + '/daemon.err', errors='replace').read())

        # ---- /run/lock is world-writable: junk lock names, and a lock name that is a symlink
        t0 = time.time()
        log_size = sum(os.path.getsize(f) for f in glob.glob(env.root + '/log/*.jsonl'))
        w0 = inotify_watches(d.pid)
        write(env.root + '/tmp/target', '')
        os.symlink(env.root + '/tmp/target', env.root + '/lock/etsoc-shire2.lock')
        write(env.root + '/dev/et2_mgmt', '', 0o666)                 # a new card 2 whose lock name is a symlink
        wr = wait_for(lambda: [x for x in env.records() if x['t'] == 'watch' and x['at'] >= t0], 3)
        for k in range(100, 400):
            write('%s/lock/etsoc-shire%d.lock' % (env.root, k), '')
        time.sleep(1.5)
        w1 = inotify_watches(d.pid)
        grew = sum(os.path.getsize(f) for f in glob.glob(env.root + '/log/*.jsonl')) - log_size
        wrs = [x for x in env.records() if x['t'] == 'watch' and x['at'] >= t0]
        check('lock names: a new card\'s node is watched, its symlinked lock name is not (%s)' % (
            wr and wr[0].get('added')), wr and wr[0]['added'] == [env.root + '/dev/et2_mgmt'] and len(wrs) == 1
              and not any('etsoc-shire2' in p for p in wrs[0]['watch']), wrs)
        check('lock names: 300 junk etsoc-shire<N>.lock names add no watch (%s -> %s) and %d bytes of log' % (
            w0, w1, grew), w1 == w0 + 1 and grew < 3000, (w0, w1, grew))

        # ---- a lock-file poller (flock -n in a loop) starts at most a scan a second
        nj0 = env.now()
        t0 = time.time()
        subprocess.run([sys.executable, '-c', 'import os, sys, time\nend = time.time() + 3\nwhile time.time() < end:\n'
                        ' os.close(os.open(sys.argv[1], 0)); time.sleep(0.02)', env.lock[0]])
        time.sleep(1.2)
        nj1 = env.now()
        ds = nj1['stats']['scans'] - nj0['stats']['scans']
        el = time.time() - t0
        check('lock poller: 150 opens of the lock in 3 s start about 1 scan a second (%d scans in %.1f s, with the '
              '2 s safety net)' % (ds, el), ds <= el * 1.0 + el / 2 + 2, ds)

        # ---- a process with a million open files
        hard = resource.getrlimit(resource.RLIMIT_NOFILE)[1]
        N = 1000000 if hard == resource.RLIM_INFINITY else min(1000000, hard - 100)
        if N < 200000:
            print('SKIP  a million fds: RLIMIT_NOFILE hard limit %d' % hard)
        else:
            hwm0 = vm_hwm_kb(d.pid)
            ready = env.root + '/tmp/big.ready'
            big = subprocess.Popen([sys.executable, '-c', '''
import os, resource, sys, time
n, node, ready = int(sys.argv[1]), sys.argv[2], sys.argv[3]
resource.setrlimit(resource.RLIMIT_NOFILE, (n + 64, resource.getrlimit(resource.RLIMIT_NOFILE)[1]))
fd = os.open(node, os.O_RDONLY)          # the node first: a low fd
r, w = os.pipe()
for _ in range(n):
    os.dup(r)
open(ready, "w").close()
time.sleep(60)''', str(N), n[(0, 'mgmt')], ready])
            children.append(big)
            seen = wait_for(lambda: os.path.exists(ready) and env.now_holds(pid=big.pid)
                            and env.now()['stats'].get('fd_truncated', 0) > 0, 30, 0.2)
            hwm1 = vm_hwm_kb(d.pid)
            big.terminate()
            big.wait()
            check('big fd table: a process with %d fds is still seen holding its node, its table read only to '
                  '--max-fds (fd_truncated)' % N, seen, env.now())
            check('big fd table: the daemon\'s peak memory grew %.1f MB (%d -> %d MB; a full listing of a million '
                  'names costs about 55 MB)' % ((hwm1 - hwm0) / 1024, hwm0 // 1024, hwm1 // 1024),
                  hwm1 - hwm0 < 10 * 1024, (hwm0, hwm1))
            wait_for(lambda: env.holds(pid=big.pid), 10)

        # ---- the daemon killed without SIGTERM while a process holds the card, then restarted
        ready = env.root + '/tmp/crash.ready'
        t_h = time.time()
        h = subprocess.Popen([env.fake_host, '--hold', '1000', '--ready', ready, n[(0, 'ops')]])
        children.append(h)
        wait_for(lambda: os.path.exists(ready) and env.now_holds(pid=h.pid), 3)
        time.sleep(2.5)                        # open.json is rewritten every second here (--act-every 1)
        t_k = time.time()
        d.send_signal(signal.SIGKILL)
        d.wait()
        with open(env.root + '/log/open.json') as f:
            oj = json.load(f)
        check('crash: open.json lists the hold after a SIGKILL', any(x['pid'] == h.pid for x in oj['holds']), oj)
        os.unlink(env.root + '/run/now.json')      # systemd removes the RuntimeDirectory of a failed service
        d2 = start_daemon(env)
        wait_for(lambda: env.now() is not None and env.now_holds(pid=h.pid), 8)
        time.sleep(1.0)
        h.terminate()
        h.wait()
        wait_for(lambda: len(env.holds(pid=h.pid)) >= 2, 3)
        d2.send_signal(signal.SIGTERM)
        d2.wait(10)
        hr = sorted(env.holds(pid=h.pid), key=lambda x: x['start'])
        lost = [x for x in hr if x.get('lost_end')]
        pre = [x for x in hr if x.get('pre')]
        check('crash: the next start writes the hold with lost_end, from its open to the last open.json (%s)' % (
            [(round(x['start'] - t_h, 2), round(x['end'] - t_k, 2)) for x in lost]),
              len(lost) == 1 and abs(lost[0]['start'] - t_h) < 0.5 and t_k - 1.6 <= lost[0]['end'] <= t_k + 0.05
              and len(pre) == 1, hr)
        o = json.loads(cli(['--json', '--since', '1h', '--log-dir', env.root + '/log',
                            '--run-dir', env.root + '/run']).stdout)
        held = sum(max(0, min(iv['end'], t_k) - max(iv['start'], t_h)) for iv in o['cards']['0']['intervals']
                   if iv['user'] == ME)
        logged = sum(max(0, min(b_, t_k) - max(a_, t_h)) for a_, b_ in o['coverage'])
        check('crash: et-usage shows the card held, not idle, while it was logged before the kill (held %.2f s of '
              'logged %.2f s)' % (held, logged), held >= logged - 0.3 and logged > 1.0, (held, logged))
        check('crash: a clean stop removes open.json', not os.path.exists(env.root + '/log/open.json'))
        errtxt = open(env.root + '/daemon.err').read()
        check('crash: the restarted daemon says what it wrote for the dead run', 'died without SIGTERM' in errtxt,
              errtxt[-1500:])
    finally:
        for c in children:
            if c.poll() is None:
                c.terminate()
                c.wait()
        for p in (d, d2):
            if p is not None and p.poll() is None:
                p.kill()
                p.wait()

    aud = open(env.audit).read()
    errtxt = open(env.root + '/daemon.err').read()
    check('fixes: the daemons never opened a node or a forbidden sysfs file (audit hook); no traceback',
          aud == '' and 'Traceback' not in errtxt, (aud, errtxt[-1500:]))

    # ---- the host's defaults file: a manual --once reads nothing it forbids (under the audit hook)
    write(env.audit, '')
    df = env.root + '/defaults'
    write(df, 'ET_USAGED_ARGS="--skip-counters 0 --skip-pci %s"\n' % os.path.basename(env.sys[1]))
    p = run_once(env, ['--defaults', df], audit_skip_sys=env.sys[0], audit_skip_pci=env.sys[1])
    aud = open(env.audit).read()
    check('defaults: et-usaged --once honours the host file: nothing of the --skip-pci card, not even devnum, and '
          'no counter of the --skip-counters card (audit hook)', p.returncode == 0 and aud == ''
          and 'nothing read (--skip-pci)' in p.stdout and 'card 0: counters not read' in p.stdout, (aud, p.stdout))
    write(df, 'ET_USAGED_ARGS="--skip-counters zero\n')
    write(env.audit, '')
    p = run_once(env, ['--defaults', df], audit_skip_sys=env.root + '/sys')
    aud = open(env.audit).read()
    check('defaults: with a file it cannot parse, --once reads no counter at all (audit hook)',
          p.returncode == 0 and aud == '' and 'counters not read' in p.stdout, (aud, p.stdout, p.stderr))


# ============================================================================ the review fixes: et-usage
def write_log(d, recs, now_doc=None):
    os.makedirs(d + '/log', exist_ok=True)
    os.makedirs(d + '/run', exist_ok=True)
    files = {}
    for r in recs:
        t = r.get('at', r.get('end'))
        files.setdefault(time.strftime('%Y-%m-%d', time.localtime(t)), []).append(
            json.dumps(r, separators=(',', ':')))
    for date, lines in files.items():
        with open('%s/log/%s.jsonl' % (d, date), 'w') as f:
            f.write('\n'.join(lines) + '\n')
    if now_doc is not None:
        with open(d + '/run/now.json', 'w') as f:
            json.dump(now_doc, f)


def hold_rec(card, user, pid, comm, s, e, nodes=('ops',), lock=True, **kw):
    r = {'t': 'hold', 'v': 1, 'card': card, 'pid': pid, 'user': user, 'uid': 1000, 'comm': comm,
         'parent': 'timeout', 'nodes': list(nodes), 'lock': lock, 'start': round(s, 3), 'end': round(e, 3)}
    r.update(kw)
    return r


def cli_fixes(env):
    print('\n== et-usage: the review fixes')
    root = env.root + '/clifix'
    now = time.time()

    def js(d, *a):
        p = cli(['--json', '--log-dir', d + '/log', '--run-dir', d + '/run', '--now', str(now)] + list(a))
        if p.returncode != 0:
            print(p.stderr)
        return json.loads(p.stdout), p.stdout

    # --json stays under 200 KB for the whole output: a busy CI day on one and on two cards.
    since = now - 26 * 3600
    for ncards in (1, 2):
        d = '%s/size%d' % (root, ncards)
        recs = [{'t': 'start', 'v': 1, 'at': since + 10, 'host': 'h', 'boot': 'b', 'pid': 1,
                 'cards': list(range(ncards)), 'watch': []}]
        for i in range(1990):
            s = since + 60 + i * 45.0
            for c in range(ncards):
                recs.append(hold_rec(c, 'ci-runner', 100000 + i, 'test_%02d' % (i % 12), s, s + 2,
                                     nodes=('mgmt', 'ops')))
            if i % 10 == 0:
                recs.append({'t': 'beat', 'v': 1, 'at': s + 3, 'holding': 0})
        for k in range(1560):
            recs.append({'t': 'act', 'v': 1, 'card': 0, 'at': since + 60 * k + 30, 's': 60.0, 'mgmt': 12, 'ops': 3400})
        recs.sort(key=lambda r: r.get('at', r.get('end')))
        write_log(d, recs)
        o, out = js(d, '--since', '26h')
        c0 = o['cards']['0']
        check('output size: %d card(s) x 1990 runs 45 s apart + 1560 activity minutes: %d KB <= 200 KB, '
              'merged_gap_s %s, totals kept (held_s %.0f)' % (ncards, len(out) // 1024, o.get('merged_gap_s'),
                                                             c0['held_s']),
              len(out) <= 200 * 1024 and o.get('merged_gap_s') and c0.get('merged_gap_s') == o['merged_gap_s']
              and abs(c0['held_s'] - 1990 * 2) < 0.5 and c0['users']['ci-runner']['runs'] == 1990, len(out))

    # An unseen record's lock_user reaches --json.
    d = root + '/lockuser'
    write_log(d, [{'t': 'start', 'v': 1, 'at': now - 3000, 'host': 'h', 'boot': 'b', 'pid': 1, 'cards': [0],
                   'watch': []},
                  hold_rec(0, 'alice', 11, 'flock', now - 1000, now - 990, nodes=()),
                  hold_rec(0, '?', None, '?', now - 999, now - 998.99, lock=False, unseen=True, opens=3,
                           lock_user='alice'),
                  {'t': 'beat', 'v': 1, 'at': now - 100, 'holding': 0}])
    o, _ = js(d)
    q = [iv for iv in o['cards']['0']['intervals'] if iv['user'] == '?']
    check('lock_user: the "?" interval says lock_user alice; users["?"] has lock_users {alice: 3}',
          q and q[0].get('lock_user') == 'alice' and o['cards']['0']['users']['?'].get('lock_users') == {'alice': 3},
          (q, o['cards']['0']['users'].get('?')))

    # Coverage: a running daemon's silence of an hour is a hole; a forward clock step is not.
    d = root + '/hang'
    s = now - 4 * 3600
    recs = [{'t': 'start', 'v': 1, 'at': s, 'host': 'h', 'boot': 'b', 'pid': 1, 'cards': [0], 'watch': []}]
    t = s
    while t < now - 60:
        t += 600
        if not now - 3 * 3600 < t < now - 2 * 3600:
            recs.append({'t': 'beat', 'v': 1, 'at': t, 'holding': 0})
    write_log(d, recs, {'v': 1, 'host': 'h', 'at': now - 5, 'started_at': s, 'holds': [], 'cards': [0]})
    o, _ = js(d, '--since', '5h')
    check('coverage: an hour with no record from a daemon running now is not logged (%d spans)' % len(o['coverage']),
          len(o['coverage']) == 2 and abs(o['coverage'][-1][1] - now) < 0.01, o['coverage'])
    d = root + '/clockcov'
    s = now - 7200
    recs = [{'t': 'start', 'v': 1, 'at': s, 'host': 'h', 'boot': 'b', 'pid': 1, 'cards': [0], 'watch': []}]
    t = s
    while t < s + 1800:
        t += 600
        recs.append({'t': 'beat', 'v': 1, 'at': t, 'holding': 0})
    t += 1200 + 30
    recs.append({'t': 'clock', 'v': 1, 'at': t, 'step': 1200.0})
    while t < now - 60:
        t += 600
        recs.append({'t': 'beat', 'v': 1, 'at': t, 'holding': 0})
    write_log(d, recs, {'v': 1, 'host': 'h', 'at': now - 5, 'started_at': s, 'holds': [], 'cards': [0]})
    o, _ = js(d, '--since', '3h')
    check('coverage: a +20 min clock step (a clock record) does not split a running daemon\'s span',
          len(o['coverage']) == 1, o['coverage'])

    # lost_end: a hold written again as a real one counts once; alone, it is an interval flagged lost_end.
    d = root + '/lost'
    write_log(d, [{'t': 'start', 'v': 1, 'at': now - 900, 'host': 'h', 'boot': 'b', 'pid': 1, 'cards': [0],
                   'watch': []},
                  hold_rec(0, 'alice', 21, 'prog', now - 800, now - 700),
                  hold_rec(0, 'alice', 21, 'prog', now - 800, now - 750, lost_end=True),
                  hold_rec(0, 'bob', 22, 'prog', now - 600, now - 500, lost_end=True),
                  {'t': 'start', 'v': 1, 'at': now - 400, 'host': 'h', 'boot': 'b', 'pid': 2, 'cards': [0],
                   'watch': []},
                  {'t': 'beat', 'v': 1, 'at': now - 100, 'holding': 0}])
    o, _ = js(d)
    us = o['cards']['0']['users']
    bob = [iv for iv in o['cards']['0']['intervals'] if iv['user'] == 'bob']
    check('lost_end: counted once next to the real record (alice 100 s, 1 run); alone, an interval with lost_end',
          abs(us['alice']['held_s'] - 100) < 0.01 and us['alice']['runs'] == 1 and bob and bob[0].get('lost_end'),
          (us, bob))

    # Names with escapes never reach the output as control characters.
    d = root + '/esc'
    write_log(d, [{'t': 'start', 'v': 1, 'at': now - 900, 'host': 'h\x1b', 'boot': 'b', 'pid': 1, 'cards': [0],
                   'watch': []},
                  hold_rec(0, 'mal\x1b]0;x\x07', 31, '\x1b[2Jevil', now - 800, now - 700),
                  {'t': 'beat', 'v': 1, 'at': now - 100, 'holding': 0}])
    o, out = js(d)
    p = cli(['--log-dir', d + '/log', '--run-dir', d + '/run', '--now', str(now)])
    check('escapes: user, program and host names in the log come out printable in --json and the summary',
          '\\u001b' not in out and '\\u0007' not in out and '\x1b' not in p.stdout and '\x07' not in p.stdout
          and '?[2Jevil' in out, (out[:400], p.stdout[:400]))

    # Reading: a byte budget, with the part not read said, and the memory of a big log.
    d = root + '/big'
    os.makedirs(d + '/log', exist_ok=True)
    os.makedirs(d + '/run', exist_ok=True)
    t0 = now - 8 * 86400
    files = {}
    t = t0
    line = ('{"t":"hold","v":1,"card":0,"pid":null,"user":"?","uid":null,"comm":"?","parent":"?","nodes":["mgmt"],'
            '"lock":false,"start":%.3f,"end":%.3f,"unseen":true,"opens":1}')
    while t < now:                               # a poller every 3 s for 8 days: about 43 MB
        files.setdefault(time.strftime('%Y-%m-%d', time.localtime(t)), []).append(line % (t, t + 0.004))
        if int(t - t0) % 600 == 0:
            files[time.strftime('%Y-%m-%d', time.localtime(t))].append('{"t":"beat","v":1,"at":%.3f,"holding":0}' % t)
        t += 3.0
    for date, ls in files.items():
        with open('%s/log/%s.jsonl' % (d, date), 'w') as f:
            f.write('\n'.join(ls) + '\n')
    with open(d + '/run/now.json', 'w') as f:
        json.dump({'v': 1, 'host': 'h', 'at': now - 5, 'started_at': t0, 'holds': [], 'cards': [0]}, f)
    size = sum(os.path.getsize(x) for x in glob.glob(d + '/log/*.jsonl'))
    wrap = ('import resource, runpy, sys\nsys.argv = sys.argv[1:]\ntry:\n    runpy.run_path(sys.argv[0], '
            'run_name="__main__")\nexcept SystemExit:\n    pass\nsys.stderr.write("MAXRSS %d\\n" % '
            'resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)\n')
    tt = time.time()
    p = subprocess.run([sys.executable, '-c', wrap, CLI, '--json', '--since', '26h', '--log-dir', d + '/log',
                        '--run-dir', d + '/run', '--now', str(now)], capture_output=True, text=True, timeout=120)
    dt = time.time() - tt
    rss = int(p.stderr.split('MAXRSS')[-1]) // 1024
    o = json.loads(p.stdout)
    check('reading: %.0f MB of log over 8 days (a poller every 3 s): --json --since 26h in %.1f s, %d MB peak; '
          'the default 64 MB budget reads it all' % (size / 1e6, dt, rss),
          p.returncode == 0 and 'truncated_before' not in o and dt < 15 and rss < 250
          and o['cards']['0']['users']['?']['runs'] > 25000, (dt, rss, o.get('truncated_before')))
    o, _ = js(d, '--since', '26h', '--max-read-mb', '8')
    tb = o.get('truncated_before')
    dl = o['cards']['0']['daily']
    check('reading: --max-read-mb 8 reads the newest 8 MB, says truncated_before, and covers nothing before it',
          tb and o['coverage'] and o['coverage'][0][0] >= tb - 0.01 and not dl[min(dl)]
          and o['cards']['0']['users']['?']['runs'] > 1000, (tb, o['coverage'][:2]))


# ============================================================================ the review fixes: unit and install files
def files_fixes(env):
    print('\n== the unit file and install.sh')
    unit = open(os.path.join(TOOL, 'et-usaged.service')).read()
    kv = {}
    for ln in unit.split('\n'):
        if '=' in ln and not ln.startswith('#'):
            k, v = ln.split('=', 1)
            kv.setdefault(k.strip(), v.strip())
    caps = {'CAP_SYS_PTRACE', 'CAP_DAC_READ_SEARCH'}
    check('unit: runs as the et-usage user with exactly CAP_SYS_PTRACE and CAP_DAC_READ_SEARCH (ambient = bounding)',
          kv.get('User') == 'et-usage' and set(kv.get('AmbientCapabilities', '').split()) == caps
          and set(kv.get('CapabilityBoundingSet', '').split()) == caps and 'DynamicUser' not in kv, kv)
    if shutil.which('systemd-analyze'):
        v = env.root + '/unit-verify.service'
        write(v, unit.replace('ExecStart=/usr/local/sbin/et-usaged', 'ExecStart=' + DAEMON))
        p = subprocess.run(['systemd-analyze', 'verify', v], capture_output=True, text=True, timeout=60)
        errs = [ln for ln in (p.stdout + p.stderr).split('\n') if ln.strip() and 'unit-verify' in ln]
        check('unit: systemd-analyze verify is clean', p.returncode == 0 and not errs, p.stdout + p.stderr)
    else:
        print('SKIP  systemd-analyze verify: no systemd-analyze')
    src = env.root + '/srccheck/tool'
    os.makedirs(src)
    for f in ('et-usaged', 'et-usage', 'et-usaged.service', 'install.sh'):
        shutil.copy(os.path.join(TOOL, f), src)
    os.chmod(src, 0o755)
    os.chmod(os.path.dirname(src), 0o755)
    p1 = subprocess.run(['bash', src + '/install.sh', '--check-source'], capture_output=True, text=True)
    os.chmod(os.path.dirname(src), 0o777)
    p2 = subprocess.run(['bash', src + '/install.sh', '--check-source'], capture_output=True, text=True)
    os.chmod(os.path.dirname(src), 0o755)
    os.chmod(src + '/et-usaged', 0o777)
    p3 = subprocess.run(['bash', src + '/install.sh', '--check-source'], capture_output=True, text=True)
    os.chmod(src + '/et-usaged', 0o755)
    if p1.returncode != 0:
        print('SKIP  install.sh --check-source: the scratch directory\'s parents are not trusted here: %s'
              % p1.stdout.strip())
    else:
        check('install.sh --check-source: refuses a source another user could change (a world-writable directory '
              'above it, or a world-writable program)', p2.returncode == 1 and 'writable by every user' in p2.stdout
              and p3.returncode == 1 and 'et-usaged: writable by every user' in p3.stdout, (p2.stdout, p3.stdout))


def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('--dir', help='scratch directory')
    ap.add_argument('--keep', action='store_true')
    a = ap.parse_args()
    root = a.dir or tempfile.mkdtemp(prefix='et-usage-test-')
    if a.dir:
        if os.path.exists(root):
            shutil.rmtree(root)
        os.makedirs(root)
    root = os.path.abspath(root)
    print('scratch: ' + root)
    env = Env(root)
    t0 = time.time()
    try:
        unit_tests(env)
        unit_fixes(env)
        e2e(env)
        cli_live(env)
        cli_synth(env)
        e2e_fixes(root + '/fixes')
        cli_fixes(env)
        files_fixes(env)
    finally:
        npass = sum(1 for _, ok in RESULTS if ok)
        nfail = len(RESULTS) - npass
        print('\n== %d passed, %d failed (%.0f s)' % (npass, nfail, time.time() - t0))
        for name, ok in RESULTS:
            if not ok:
                print('   FAILED: ' + name)
        if not a.keep and nfail == 0:
            shutil.rmtree(root, ignore_errors=True)
    return 1 if nfail else 0


if __name__ == '__main__':
    sys.exit(main())
