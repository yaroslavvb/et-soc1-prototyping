"""E212 (reg-e212, Q208): the lab's audit of the proposal's src/ for a kill path, as a listing (reads only; Python's own modules).

    /usr/bin/python3 -I -B audit_kill_e212.py <src dir>        (prints the listing; paths relative to the src dir's parent)

Part 1, the kill words: every line of every text file holding SIGKILL, kill -9, kill -KILL, kill -s KILL, timeout -k,
  timeout --kill-after, timeout -s / --signal, os.kill, killpg, .kill(, .terminate(, pkill or killall.
Part 2, every process launch: subprocess.Popen / run / call / check_call / check_output, os.system, os.exec*, os.spawn*,
  os.fork, popen / system / fork / exec* calls in C and C++; in shell files every line with timeout N, setsid, nohup or exec,
  or ending in a background '&'; in Python files every command list holding the timeout program ("timeout").
Part 3, every signal use: send_signal, signal.signal, sigaction, std::signal, signal(, raise(, kill(, trap.
Part 4, the subprocess.run calls with a timeout= argument (on its line or the next two): CPython's run() kills its child with
  SIGKILL when that timeout expires (Lib/subprocess.py, run(): process.kill() in its TimeoutExpired branch), and on any other
  exception raised while it waits (its bare except branch), so each is listed with what its child is.
Each part prints file:line: the line (stripped, cut at 160 characters). The reading of each site is in E212.md section 9. (E208's audit_kill_e208.py, with this experiment's names.)
"""
import os
import re
import sys

src = os.path.abspath(sys.argv[1])
top = os.path.dirname(src)
files = []
for root, dirs, fs in os.walk(src):
    dirs[:] = sorted(d for d in dirs if d != '__pycache__')
    for f in sorted(fs):
        p = os.path.join(root, f)
        try:
            t = open(p, encoding='utf-8').read()
        except UnicodeDecodeError:
            continue
        files.append((os.path.relpath(p, top), t.splitlines()))

KILL = re.compile(r'SIGKILL|\bkill\s+-9\b|\bkill\s+-KILL\b|\bkill\s+-s\s*KILL\b|\btimeout\s+(-k|--kill-after)\b|'
                  r'\btimeout\s+(-s|--signal)\b|\bos\.kill\b|killpg|\.kill\(|\.terminate\(|\bpkill\b|\bkillall\b')
PYLAUNCH = re.compile(r'subprocess\.(Popen|run|call|check_call|check_output)\b|\bos\.(system|exec\w*|spawn\w*|fork)\b')
CLAUNCH = re.compile(r'\b(popen|system|fork|execv\w*|execl\w*)\s*\(')
SHLAUNCH = re.compile(r'\btimeout\s+\d|\bsetsid\b|\bnohup\b|^\s*exec\b|[;&|]\s*exec\b|&\s*$')
PYTIMEOUT = re.compile(r'["\']timeout["\']')
SIG = re.compile(r'send_signal|signal\.signal|\bsigaction\b|std::signal|\bsignal\s*\(|\braise\s*\(|\bkill\s*\(|^\s*trap\b')
TIMEOUT_ARG = re.compile(r'\btimeout\s*=')


def show(rel, i, ln):
    s = ln.strip()
    return '%s:%d: %s' % (rel, i + 1, s if len(s) <= 160 else s[:157] + '...')


def part(title, pick):
    out = []
    for rel, lines in files:
        for i, ln in enumerate(lines):
            if pick(rel, ln):
                out.append(show(rel, i, ln))
    print('== %s: %d line(s)' % (title, len(out)))
    for x in out:
        print('  ' + x)
    print()


print('# E212: the kill-path audit of %s (%d text files)' % (os.path.basename(src), len(files)))
print()
part('1. kill words (SIGKILL, kill -9, timeout -k, os.kill, killpg, .kill(, .terminate(, pkill, killall)',
     lambda rel, ln: bool(KILL.search(ln)))
part('2a. process launches in Python files', lambda rel, ln: rel.endswith('.py') and bool(PYLAUNCH.search(ln)))
part('2b. process launches in C and C++ files',
     lambda rel, ln: rel.endswith(('.c', '.cpp', '.h')) and bool(CLAUNCH.search(ln)) and not ln.strip().startswith('//'))
part('2c. programs started under timeout, setsid, nohup or exec, or in the background, in shell files',
     lambda rel, ln: rel.endswith('.sh') and not ln.lstrip().startswith('#') and bool(SHLAUNCH.search(ln)))
part('2d. the timeout program in a Python command list ("timeout", N, ...)',
     lambda rel, ln: rel.endswith('.py') and bool(PYTIMEOUT.search(ln)))
part('3. signal uses', lambda rel, ln: bool(SIG.search(ln)))
out = []
for rel, lines in files:
    if not rel.endswith('.py'):
        continue
    for i, ln in enumerate(lines):
        if re.search(r'subprocess\.run\(', ln):
            window = ' '.join(lines[i:i + 3])
            out.append(('WITH timeout=' if TIMEOUT_ARG.search(window) else 'no timeout=  ') + '  ' + show(rel, i, ln))
print('== 4. subprocess.run calls, with or without a timeout= argument (on the line or the next two): %d' % len(out))
for x in out:
    print('  ' + x)
