# Dated note 2 on E169's amendment, `REGISTRATION-A2.md` (Wed 4 Nov 2026, week 45, Q141(s)'s fix pass, after the lane's verifier)

*This note is written beside the amendment, not inside it. A2 (E169) stays frozen as committed in `217c94a2` (09:22:23 PST). The first
dated note, [`REGISTRATION-A2.md.dated-note.md`](REGISTRATION-A2.md.dated-note.md), stays as committed in `2bf8f092` (09:47:26 PST).*

*This is a dated amendment, **committed before any E169 data exists and before any claim**. No `docs/reports/data/*-e169-*` exists at
any commit or on disk, and no card has run an E169 shape. It answers faults 1, 2, 5 and 7 of the lane's verifier (Wed 4 Nov, about
09:52-10:16 PST).*

*It changes no rule, number, prediction, design or code. The scorer, the queue and the protocols are byte-identical to their hash list
([`frozen-sha256-e169.txt`](frozen-sha256-e169.txt), 54 OK). Each item says what the registered rule and the frozen scorer already do,
and which words now stand beside them. [`selftest_notes_e169.py`](selftest_notes_e169.py) →
[`selftest-notes.txt`](selftest-notes.txt) checks every claim below (34 checks, ALL PASS).*

## 1. A negative step reads UNRESOLVED (S4's table, its last rows)

S4 gives each decisive pair a presence:

- PRESENT above +3.0 points;
- ABSENT inside [−3.0, +3.0];
- "else UNRESOLVED".

Take a decisive pair whose whole 95% interval lies below −3.0 points. That is **a negative step**: P runs faster per op than N, which
none of SM, ISO and STRICT predicts. Its presence is UNRESOLVED, so **the verdict reads UNRESOLVED**. S4's rule says so, and
`score_e169.py` computes it.

The table's "what it says" for UNRESOLVED, "a presence crosses its edge", names only one of the two ways. From now on it reads:
**"a presence crosses an edge of [−3.0, +3.0], or a decisive pair shows a negative step"**.

- **How it prints.** The scorer prints a negative step as the pair reading "NONE OF THE THREE: below every zone (ISO's lowest)", with
  presence UNRESOLVED and size NOT SM. The run's README names that pair "a negative step" and gives its interval.
- **The verdict stays UNRESOLVED.** It is never read as NO STEP, as MIXED or as a stride step. On that pair a negative step refutes
  SM's size (size NOT SM, printed). It is not ISO's or STRICT's "no step" either.
- **On P2/N2** (reported, never counted), a negative step reads the same way and changes no verdict.
- **Checked** in [`selftest-notes.txt`](selftest-notes.txt) § 1:
  - six made-up sessions: both decisive pairs at −6%; one of them at −6% with the other at SM's step, at a step SM does not size, or
    at none; one on the −3.0 edge; and P2/N2 at −6%;
  - a sweep of 222 more. A decisive presence is UNRESOLVED exactly when its interval holds −3.0 or +3.0 points, or lies wholly below
    −3.0 points, and never for both reasons. The verdict is UNRESOLVED exactly then.

## 2. A pass split across two sessions counts (S1)

S1 counts a pass when both its bursts ran in it, each with at least 5 launches at or above 790 MHz. It does not ask that the two ran
in one session. A2's "Why a step rule" says a step is measured "in one session, minutes apart". That describes the design; it is not
a condition.

**How a split arises.** If another user's login ends a session (exit 3), the queue resumes as `s2` (up to `s6`). It skips the runs
already recorded (E101_SKIP_DONE). A run is recorded only when it ends (`run_hpl.py:802`), so each run sits in exactly one session. A
run lost in flight is run again and counted once. A pass whose P and N bursts then fall in two sessions **still counts**: S1 says so,
and the frozen scorer computes it when it is given every session directory.

- **Named in the write-up.** Such a pass's step crosses a session boundary, so the run's README names each one.
- **Spread from the gap shows.** S2's interval uses the passes' own sd whenever it is above σ0, so any extra spread from the gap widens
  the interval instead of hiding.
- **Each burst is still gated.** It starts from the cool gate (≤ 55 °C), and T800 still uses only launches at or above 790 MHz. Between
  sessions, E158 repeated E146's T800 within −0.31% to +0.29% (A2 S2).
- **Score every session directory.** See [`README.md.dated-note.md`](README.md.dated-note.md), box step 7.
- **Checked** in § 2. E158's committed session was cut in two inside its pass 2, as a resume would leave it. On the two sessions:
  - `reduce_e169` reproduces E158's `results.json` exactly: the per-pass and per-shape T800s, the launch counts, the cycles per op, the
    cells and the checks of C;
  - E158's own registered `score()` reproduces its rules and errors;
  - the step rule reads E158's four committed collapses as it does on one session. `K6n4`/`K6n3` is among them, with its pass-2 bursts
    in two sessions.

## 3. B7's point: measured / SM − 1 within 3%

§ B7 says "SM's frozen T800 within 3% of the measured T800". `49575094` and `predictions-e169.json` › `rules` say "SM's (frozen) T800
within 3%". The frozen scorer reads it as **|T800_measured / T800_SM − 1| ≤ 3%**, relative to SM's frozen T800 (`score_e169.b7`). That
is E158's convention (`reduce_e158.py:175`, `abs(T8 / p - 1) <= point_rel`), and § B7 is read that way.

- **Where the readings differ.** The two readings differ only within about 0.1 point of the edge: from −3.00% to −2.91%, and from
  +3.00% to +3.09%. B7 is expected to fail by 6-45%.
- **Checked** in § 5: +3.05% fails and −2.95% passes. The other reading would pass the first and fail the second.

## 4. The tree checked before A2 was `4286f0a8`, A2's parent

A2's preface says the log was checked at 09:15 PST "at `8eb3be71`, equal to origin". The lane's clone was at `8eb3be71`. But origin/main
had moved to `0830f65b` at 09:11:53 PST, and A2 (`217c94a2`, committed 09:22:23, pushed 09:22:27) landed on `4286f0a8` (on origin from
09:18:59).

None of the five commits in between names E169 in its message or adds an E169 path:

- `0830f65b`, Q141(t);
- `2b450e66`, E166;
- `7ba987b3`, E167;
- `226249e1`, A2 (E168);
- `4286f0a8`, E164.

So the claim holds at A2's parent: no E169 data and no E169 kit existed before A2. Records cite `4286f0a8` as the tree checked.

## 5. The first dated note's header

[`REGISTRATION-A2.md.dated-note.md`](REGISTRATION-A2.md.dated-note.md)'s header says "about 09:50 PST". It was committed at
09:47:26 PST (`2bf8f092`, pushed 09:47:29).
