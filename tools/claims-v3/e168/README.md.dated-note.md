# Dated note on E168's kit README `README.md` (Wed 4 Nov 2026, week 45, begun 10:27 PST, before any E168 data)

Written beside the README and not inside it. [`README.md`](README.md) is E168's registration of the run, committed and pushed in
`a0310012` at 09:38:43 PST, so its bytes stay as registered. No data of any E163-E169 run exists and no card has been claimed for them
(Q141 is desk only), so this correction is a dated note committed now, before any E168 data, claim or launch. Nothing here changes a
hold, a gate, a stop, a cap, a rule, a prediction or a reading, and no frozen file changes.

- **The times.** The README's header says it was "written on the Intel about 09:20-09:50 PST". That runs past its own commit: the file
  was last written at 09:36:05 PST and committed at 09:38:43 PST. The two other headers slipped the same way:
  - amendment A2 says "about 09:25 PST"; it was written by 09:16:57 and committed in `226249e1` at 09:18:35, as its dated note says;
  - that dated note's own header says "about 09:45 PST"; it was written by 09:39:59 and committed in `d86cafa6` at 09:40:30.

  Each was an estimate written before the work, not read from the clock after it (Q140(e)'s C1 slip, as in E166's and E167's notes).
  The order stands: A2, then the kit, then the note, all before any E168 data or claim.
- **The cap** (§ Card-minutes, "The cap"). The README names one rule: `run_e119.py` starts a run only if its planned time fits the
  58-minute cap. That rule alone does not bound the session, because a hold's plan leaves out its gate's wait. Two other limits do.
  - **The start rule** (`run_e119.py` lines 58-72) compares the session's elapsed time plus `plan_s` with the cap. `plan_s` is
    processes × (seconds + 1.2) + tail + 25 (`run_hpl.py` lines 186-187), 141.4 s for every hold. It has no gate term. The gate waits
    after the check, inside the run (`run_hpl.py` lines 703-711): at most 360 s cold and 300 s warm.
  - **The in-flight guard binds the cap.** `run_hpl.py`'s guard (lines 674-680), which `run_e119.py` keeps, ends the session once
    its elapsed time passes the cap (`done:max_card_min`, exit 0, the end queries read). It runs every 0.2 s while a gate waits
    (`wait_until`, lines 687-700) and before every process. So a hold admitted near the cap whose gate then waits is cut in flight
    and is not scored (the cut rule). The session ends at most one process (its 9.5 s budget, under `timeout 10`) and its end queries past the cap.
  - **The toy-card check** ([`logs/cap-test-dry.txt`](logs/cap-test-dry.txt); `run_e168.py --dry`, no device):
    - With `--max-card-min 2.5`, A2's hold was admitted (141.4 s fits 150 s) and its cold gate waited on the toy card's 51 °C. The
      session ended `done:max_card_min` at 151 s, with no work launch.
    - With 2.3 min, the start rule cut the hold at once (`done:cap_cuts_tail`).
  - **The whole queue.** The queue sets each session's cap to the lesser of 58 min and the time left before the slot's end minus
    3 min (`queue_e168.py` lines 96 and 398-399). So the smoke, the stop tests and the session end by about 63 min after the slot's
    start, plus that one process and the end queries, as the README says.
    - The slot's hard stop is the backstop: the session's stop-file at the slot's end minus 120 s, SIGTERM at minus 30 s
      (`queue_e168.py` lines 38-40 and 232-242).
    - Either way the run stays inside the 66-minute slot and the claim's 1.5 h.
  - **"The cap can only cut [the tenth hold], never one of the nine"** holds for a session that starts on time and runs without a
    resume.
    - The nine end by about 31.6 min of session time as planned, or 41.1 min with every cold gate at its 360 s. That is 17 min
      inside the cap. A2's hold ends by 38.0 min (49.5 at the bounds).
    - A late session gets the time left as its cap. That happens when the queue has waited for the card (up to the slot's end minus
      25 min), or when a resumed `s2` runs after another user's login ended `s1`. The cut then falls from the tail of the protocol's
      order: A2's hold first, then I's int8 holds, then H's.
- **The audit's file set** (§ Self-test, dry pass, audit; [`logs/dmcmd-audit.txt`](logs/dmcmd-audit.txt)).
  - It leaves out `tools/claims-v3/kinds/e78_common.py`, which `kinds/e101_common.py` imports (line 25). That file imports only the
    standard library and sends nothing. E159's audit had the same gap.
  - Re-run with it, and with this directory as it now stands: [`logs/dmcmd-audit-2.txt`](logs/dmcmd-audit-2.txt). The result is
    **GO**: 19 send sites, every one READ, 0 disallowed, the same reviewed exception.
- **A rest floor above 46 °C.** A desk check, not registered: [`posthoc_floor_e168.py`](posthoc_floor_e168.py) →
  [`logs/posthoc-floor.txt`](logs/posthoc-floor.txt). It runs Q140(q)'s frozen `run_model`, unchanged, with the chain's rest anchor at
  46.0-48.0 °C. At 46.0 °C it reproduces `predictions-e168.json`'s `both_nominal_starts` exactly.
  - **At 47 °C** (E161's measured floor on this card, [`logs/rest-chain.txt`](logs/rest-chain.txt)):
    - G4 reads cold 37.660 W at a 54.662 °C window die, and warm55 36.480 W at 56.733 °C;
    - so dW_G4 = +1.180 W, and A2's band h = 0.590 W.
  - **A law in the absolute die** reads −0.911 to −1.035 W at k_D 0.44-0.50 W/°C on G4's die gap. Run through the model as the
    registration's T_D, it reads −1.562 to −1.865 W. Both are OPPOSITE SIGN.
  - **From 46 to 48 °C,** all 30 cases read OPPOSITE SIGN; the closest lies 0.295 W past −h.
  - So on a day when the cold gates time out at a 47 °C floor, A2 keeps all three readings. The scorer reads each hold's measured
    start and needs no change.
  - This corrects the kit lane's own result, which said that at a 47 °C floor A2 could not reach OPPOSITE SIGN. That estimate was in
    no committed file.
