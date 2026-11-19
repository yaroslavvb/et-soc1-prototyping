# Addendum 1 to DECLARED-layout.md (post hoc, written Thu 19 Nov 2026 about 09:25 PST, after s04's scores and s06's look)

Written after the declared forms were scored (work/s04_eval.json) and after the pair-ordering look (scripts/s06_order.py), so nothing
below is blind to those numbers. It adds (1) a placebo check that decides whether the declared rule's winner earns its place, and (2)
two more one-constant features, scored the same way and held to the same rule plus the placebo check.

(1) Placebo check. The rule's winner earns its place only if its LOLO (b) is lower than that of at least 95 of 100 placebo features
made by permuting its own feature's values among the subset points (seeded 20261119 + i), each fitted and scored exactly as the form
(two-stage, the same folds), and lower than both one-constant layout-class indicators (compact: n = 4R; spread: R = min(8, n)).
If it does not, the result is NOT FROZEN.

(2) G1 = Phi_hopmean: (110 + 12 h_mean(mask)) / (110 + 12 h_mean(full)) - 1, the active shires' mean L3 latency over the 32 homes
against the full chip's. G2 = Phi_share: n_A / n_A,full - n_B / n_B,full with n_A = n / R and n_B = n / C the active shires asking
each A and each B tile (zero at the full mask: 4 and 8): positive when A is the more widely shared operand. A G form is kept by the
declared rule and then the placebo check above; the overall winner is the lowest LOLO (b) among forms that pass both.
