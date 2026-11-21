# E224's kit, dated note 1: the order against card-e222 is ready-e224's to carry (answer 5); a no-kill reader that decides every form by where it stands on the line; two wording corrections; arm B's runbook test's count in the landed lab and the hours it can pass (no kit file changes)

*Fri 20 Nov 2026 (week 47), Pacific time. Written from about 20:37 PST by round Q237's lane `fix-e224`, before E224's registration and kit
land and before any E224 datum. No E224 card command has been sent: there is no `card-e224a` or `card-e224b` lane folder and no booking of
aifoundry1 or aifoundry2. Desk only: no card, no simulator, no device command, nothing posted. Interpreter: `/usr/bin/python3` 3.12.3 with
`-I -B`, standard library only, single-threaded inside the round's slots. Every stand-in run also ran inside `W/nodev.sh`, started with THE
QUIET DESK FLAG absent and no aifoundry2 booking or claim.*

**A dated note OUTSIDE E224's folder.** No kit file and no registered file changes for it. These stay exactly as verify-e224 checked them:

- the kit's subtree `211efcd1...`;
- `SHA256SUMS-e224-kit` (`3b8b2b91...`, 120 entries), both step 2s' KITPIN;
- the anchor lines: arm A's step 2 `210a85fe...`, arm B's `da315ba6...` (`OUT/kit-e224/land/anchor-lines-e224.txt`);
- the registration's subtree `a46c1682...` and its list `9420b5d1...` (31 entries).

The note lands with the kit commit, in `tools/claims-v3/e224-notes/` beside the registration's dated note 1. No list or pin names that
folder. Both history checks read additions under `tools/claims-v3/e224` only, and every note file's name passes their shadowing check.

It answers verify-e224's findings 1, 3, 5 and 6 and its info 9, as the orchestrator's answer 5 (`W/out/orch/e224-answers.txt`, 20:35 PST)
asks. verify-e224 (Q237's verifier of E224's registration and kit) read HOLDS WITH FIXES at 20:35 PST.

## 1. E224's order against card-e222 is carried by ready-e224's go lines (verify-e224's finding 1, medium; answer 5)

**What the kit does.** Arm B's O row (`rb/quiet_e224b.sh others --wait`) raises THE QUIET DESK FLAG only once every booking another card lane
of ours holds has its launch marker. It reads the markers from RB_LAUNCHED (`<lane>=<file>` pairs joined by `:`) and re-reads every 20 s, for
up to 520 s a call. It never waits for an orchestrator's booking (an owner `orch-...`: REPORTED only). A card lane's booking with no marker
named is waited for.

**The order the orchestrator set** (answer 3, 18:40 PST) came after the kit was written, so the kit does not hold it. verify-e224 named two
ways it can fail:

- **(a)** card-e222 holds aifoundry3 and RB_LAUNCHED names no marker for it: arm B waits for card-e222's whole booking. It can then pass its own
  O bound and lose its day.
- **(b)** card-e222 has not booked yet, or aifoundry3 sits under an `orch-*` hold: the flag goes up anyway. It then holds card-e222's step 9
  for arm B's whole session.

**Answer 5 puts the order in ready-e224's go lines, not in the kit.** This note changes nothing in the kit for it, and states it for the card
lane:

- arm B's flag waits for card-e224a's launch marker **and** card-e222's launch line;
- card-e222's launch line is read from its own launch marker, as ready-e222's go lines name it. E222's `rb/s11_session_e222.sh` writes
  `<its RB_OUT>/e222-T0-A.txt` after its LAUNCHED line. If no marker is named, it is read from `OUT/card-e222/logs/progress.txt`'s step 9
  launch;
- the wait also ends if card-e222 has returned, or if `bash W/book.sh show` shows no booking of aifoundry3 by card-e222 at 00:45 PST Sat;
- arm B never waits on an `orch-*` hold of aifoundry3, nor on card-e222's whole booking. Once card-e222 has launched, or the 00:45 bound has
  passed with no booking, arm B goes on;
- arm B's O bound is its own. The go lines say how long arm B can wait before its window would pass. Past it, arm B ends by its stop path
  (row E, `rb/end_e224b.sh`) and the orchestrator decides.

## 2. A no-kill reader that decides every form by where it stands (verify-e224's finding 6)

**The fault.** The kit's reader (`desk/nokill_e224.py`, unchanged) decides kit-e224's old forms on the WHOLE line. It reads a line as a
statement whenever the line matches its STATE words (`#`, `never`, `rule`, `words`, ...). verify-e224 found three disguised kills it
therefore read as statements (NOKILL 0):

- `timeout -k 1 10 <host>  # comment` (M4);
- `timeout -k ... --rules x` (M4c);
- `kill -9 "$PID"  # comment` (M4d).

The kit itself is clean: verify-e224 read its 16 statement lines one by one, and each is text.

**The answer: `nokill_e224_note1.py`** (this folder). It is a new reader beside the kit's, standard library only and read only:

- **It splits each line into its parts:** code, string literals, comment and (in Python) docstring. It tracks triple-quoted blocks across
  lines, and tells a docstring (one standing alone at its line's start) from a string constant, which it reads as a string.
- **It matches every form in the code part, with its string literals kept**, since a command handed to a shell sits in a string. The forms
  are kit-e224's old ones, fix-e220's shell forms and, new here, argv lists: a `timeout` token followed in the same list by `-k`,
  `--kill-after`, `-s KILL` or `--signal=KILL`, or a `kill`/`pkill`/`killall` token followed by `-9`, `-KILL`, `-SIGKILL` or `-s KILL`.
  fix-e220's Python forms are matched in the code with its strings removed.
- **It decides each hit by where it stands:**
  - in code: SENDS, whatever words the line holds;
  - in an argv list: SENDS;
  - in a string literal: a statement only when a statement word stands before the hit in that same string ("never kill -9"), or, in a .py
    file, when the string holds nothing but the form (a needle, as in `("kill -9", "timeout -k")`); else SENDS (a command string);
  - in a comment or a docstring: a statement.
- **It reads the kit's three roots plus fwgate** (the reboot gate both arms run on their boxes). fwgate holds no kill form.

| run | result |
|---|---|
| **the kit as committed** (`nokill-e224-note1.txt`) | **NOKILL-E224-NOTE1: 0 lines toward a device process**; 12 to the desk's own call tree (k6's `rb_run.py` `kill_tree()`, the same 12 the kit's reader lists); 46 lines state the rule. All 16 of the kit's reader's statement lines are statements here. Of the 30 more, 16 are the kit's own reader's docstring and pattern lines (that reader skips itself) and 14 name SIGKILL in a docstring, a comment or a Python string. |
| **its desk test** (`selftest_nokill_e224_note1.py`, `selftest-nokill-e224-note1.txt`), on a copy of the four roots | **15 of 15 PASS**: the unmutated kit (K0) and the restore (K1); verify-e224's M4, M4b, M4c and M4d, each now SENDS (the kit's reader: states, SENDS, states, states); X1, `run_e224a.py`'s host argv list given a `-k` token (the kit's reader does not list it); X2, a .py command string with a `# never` comment; X3 and X4, a quoted remote command, with and without a statement word after the form: all SENDS; U1-U5, a shell comment, an echo with "never" before the form, a docstring, a message with "no" before the form and a needle tuple: all states the rule (the kit's reader classes U5 as SENDS) |

**Known limits, stated:** a kill assembled from pieces held in variables; a needle string later joined into a command in a .py file; a shell
string that spans lines; a triple-quoted string standing alone at its line's start, which is read as a docstring even where it is a value;
and code the reader does not read.

**How the card lanes use it.** Step 2 and both preflights are unchanged and still run the kit's reader through its committed log. The
readiness lane can run `nokill_e224_note1.py <the lab at its HEAD>` as a desk read and cite its last line (want 0 toward a device process). The
kit's no-SIGKILL claim (KIT.md section 6) stands, and now on this reader too.

## 3. Two wording corrections (verify-e224's findings 3 and 5)

- **`CARD-LANE-BRIEF.md`, arm A's row 0:** "F1R the registration commit (subtree 46dde0fd) in HEAD" reads **"(subtree a46c1682)"**. `46dde0fd`
  is E220's registration subtree. The code checks `a46c16828d696f2936aa087ffb3cec94acb35f6c` (`rb/s00_step0_e224a.sh` REG_SUB,
  `rb/rb_e224a.sh` E224A_REG_SUBTREE), which is right.
- **`rb/rest_rule_e224a.sh`'s header** says the rule's lines are sent "to aifoundry3" and quotes E224.md 6 as the last session "on aifoundry3
  card 0". Read **aifoundry1** (arm A's box: steps 7 and 9 send them there). E224.md section 6's arm A row is the rule: "the first card command
  at least 40 minutes after the last session on aifoundry1 ended, either card, ours or the model session's (E220 arm A's session this afternoon
  counts), and THE REST RULE: no write under the model session's ~/claude/work/ee-*/ on aifoundry1 within the last 40 minutes". The code is
  E215 arm A's line for line and runs on aifoundry1, as E224.md 6 says.

## 4. Arm B's runbook test: its count in the landed lab, and the hours it can pass (verify-e224's info 9; a reading of this lane's)

**Its count.** `desk/selftest_rb_e224b.py` reads **91 of 91** in a checkout that holds the kit committed (verify-e224's run at 19:19 PST on
GitHub main `1a259ddc`). In that case its own condition skips P4-P6 and P14, which need the kit's files untracked to make a stand-in kit
commit. The kit's committed log (`logs/selftest-rb-e224b.txt`, 95 of 95) is from a checkout without the kit committed. The readiness lane
expects 91 in the landed lab.

**Its hours (found by this lane, REPORTED; no kit file changes).** The test can pass only when it runs **from 00:00:30 to 20:29:00 PST**.
Its window cases make G (the booking's time) from the clock less 60 s (its code: `t_window`, `fresh()` in the step-2 cases, and the gate's
section). `rb/s02_window_e224b.sh` refuses any G later than 20:29:00 PST that day (THE DAY).

- Run here at 21:03 PST, with both notes committed, it read **37 of 64 FAIL**.
- W1 printed the refusal: "G (2026-11-20 21:01:45 PST) is later than 20:29:00 PST: no booking that day".
- Every other failing case needs a window made that way. Each was refused at "no window" before the check it tests, or follows a case that
  was.

A run between 20:29:00 and 00:00:30 PST is therefore not a test of the kit. The readiness lane runs it after 00:00:30 or before 20:29:00, or
reads verify-e224's run. Arm A's runbook test takes its window from today's last minutes (23:58-23:59), so it is not affected before 23:58.

## 5. This note's files and checks

`SHA256SUMS-e224-kit-note1` lists every file of this note but itself. Its paths run from the lab's top, so `sha256sum -c` there reads OK.

| file | what it is |
|---|---|
| `KIT.md.dated-note-1.md` | this note |
| `nokill_e224_note1.py` | the reader (section 2) |
| `selftest_nokill_e224_note1.py` | its desk test, verify-e224's mutations among its 15 cases |
| `nokill-e224-note1.txt` | the reader's output on the kit at the kit commit |
| `selftest-nokill-e224-note1.txt` | the desk test's output |

**The checks with this folder in the kit commit** (on the registration commit with its dated note 1, at GitHub main `f9b24099`; logs in
`OUT/fix-e224/logs/`):

- both history checks: HISTORY OK (123 additions under `tools/claims-v3/e224` since the registration, none of this folder; no shadowing name);
- arm A's step 0 (desk-test form, the kit commit as GitHub main): 6 of 6 as stated;
- arm A's step 2, for real, under a lab-git lock file of the fix lane's own: rc 0;
- arm B's step 2 (desk-test form, a stand-in booking time of 20:20 PST): STEP2 PASS;
- arm A's runbook test (`rb/selftest_rb_e224a.sh`): SELFTEST-RB-E224A 32 of 32 PASS;
- arm B's build test: DESKTEST-BUILD-E224B 6 of 6 PASS. Its runbook test ran at 21:03 PST, after THE DAY's 20:29:00 (section 4), so it is
  not a test of the kit tonight;
- the note's reader and its desk test (section 2); `sha256sum -c` of the kit's list (120 OK) and of this note's.

SPDX-License-Identifier: Apache-2.0
