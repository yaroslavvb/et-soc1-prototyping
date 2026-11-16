# The form of E199's data README (the card lane fills it at step 12; KIT.md section 9)

*E199's kit (Q191, lane `kit-e199`, Sun 15 Nov 2026, before any E199 datum). The card lane copies this form to
`docs/reports/data/<day>-e199-intbits-aifoundry1-c1/README.md` and fills every `<...>` from the session's own files (the wrapper's
`session/session.log`, `run/gate.jsonl`, `facts-e199.json`, the build record) and the day's runbook log; nothing is filled from memory. It
holds no forecast number of any sealed forecast and no score: step 13's outputs (E199's transport verdicts) are committed by a records lane
after the data commit, in their own files. Every figure says which it is: **measured** (this session's records), **registered** (E199.md,
E192.md), **desk check of code**, **REPORTED**.*

```
# E199 data: E192's reference session on aifoundry1 card 1, <day> (<RAN FULL | STOPPED | GATE-STOPPED>)

## Results first (measured; no forecast number, no score here)
- Passes complete: <k> of 9 (pass 0 the registered warm-up); launches recorded <n>; card time <s> s = <m> card-minutes from the first
  card command, the start config read (cap 65; registered about 60, E192 measured 59.52).
- The sampler: <pvt | ettelem> (<why, the wrapper's own words>); THE IDENTITY GATE (a): <IDENT-A line>; (b): <the gate's identity_b
  counts>; the end config read: <its line> (recorded).
- The smoke gate: <GO | STOP: why>; any STOP: <who, why, when>; the watch: <no other card named or held | the STOP>; card 1's live stops:
  <none fired | the line>; peaks: board <W> W, minshire[0] <C> C (measured; predicted peak 60.90 W registered, card 1's line 65 W).
- 600 MHz: <n of n samples> (card 1 does not raise its clock: docs/findings/14-card-behaviour.md).

## Registered against happened (E199.md sections 2-11; E192.md sections 3-10 by reference)
| item | registered | happened |
|---|---|---|
| card, clock, selection | aifoundry1 card 1, 600 MHz as found, ET_DEVICES=1, card 1's lock | <...> |
| the order | `order-e199-aifoundry1.txt` (E192's rule for hostname aifoundry1) | <the dry pass's E199-DRY line; the order run: SAME / differs at ...> |
| the smoke, the passes, the gaps | E192's (3 smoke runs; 36 runs a pass; 30 s gaps with the holder check) | <...> |
| stops | card 1's 65 W / 70 C beside E192's own | <...> |
| cap, rests | 65 card-minutes; 40 minutes before and after on aifoundry1 | <the rest line of step 9; the end> |
| window | G = the booking <time>; last start <HH:MM>, last end <HH:MM> | <first card command, session end> |
| post | waived by the owner's standing words of Sun 15 Nov 2026 10:22:36 PST | no post |
| sealed card-1 freeze lines | E199.md's freeze line 2: the model session's sealed card-1 forecast (1c5d8fa3..., posted 01:28:51 PST Mon 16 Nov 2026, registered before the land); a later one only by a dated note at tools/claims-v3/sealed-card1/e199-freeze-lines.md committed before this day | <step 2's line: E199.md line 2, and the later note (none / the sha256 named)> |

## Departures, dated
<each with its reason, or "none">

## The day's records
- The build on aifoundry1 (`build/BUILD-E199.txt`): kernel ELF <sha>, .text <sha>, host <sha>, beside E192's desk build and E192's card-day
  build (reported, never judged); check_elf "loops 16, bad 0"; loop_order 16 of 16; the arm table byte for byte; ET_DEVICES in the host,
  the reader and the heater.
- The box's manifest, COPY EXACT (step 11), our own box login masked as `<box-login>`, the scrub, k6's desk-path gate.
- Device commands sent (`dmcmd_audit`, the plain chain GO with the stock table; the per-sensor chain <GO with E144's table | not used>):
  `ettelem config` (the start and end reads), `ettelem sample` or `pvt_sample.py` (READs only), the hosts and the heater on card 1's ops
  node; no statistics reset, no set of any kind, no firmware query, nothing to card 0.
- The commits: the data commit (this directory); the records lane's commit of step 13's outputs (intbits-e199.json, checks-e199.json,
  scores-e199.json, the unfiltered reduction).
```

SPDX-License-Identifier: Apache-2.0
