#!/usr/bin/env python3
"""Acceptance tests for the wf5 reduction's VER 1-12 and the skeptic's loop-head finding.

Reads the dtf.json / reduce.txt this folder's run.sh produced on the complete data, and checks each
item of the fix verifier's list against the number the verifier independently re-derived from
runs.csv.  Run it AFTER run.sh.

    uv run -q --with numpy python test_ver_wf5.py
"""
import io
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "dtf.json")
TXT = os.path.join(HERE, "reduce.txt")

FAILS = []
N = [0]


def check(name, ok, detail=""):
    N[0] += 1
    if not ok:
        FAILS.append(name)
    print("  %-68s %s   %s" % (name, "PASS" if ok else "FAIL", detail))


def near(a, b, tol):
    return a is not None and b is not None and abs(a - b) <= tol


if not os.path.exists(OUT):
    print("dtf.json is not here: run run.sh first")
    sys.exit(2)
res = json.load(open(OUT))
txt = io.open(TXT, encoding="utf-8").read() if os.path.exists(TXT) else ""
A3 = (res.get("cards") or {}).get("aifoundry3") or {}
F = A3.get("families") or {}
D = A3.get("derived") or {}
V = dict((v["claims"], v) for v in (res.get("verdicts") or []))

print("\n[VER 1] the changed-word price and count on one §5.1 reading")
t = F.get("e_out_add_registered_R2_term") or {}
check("the d3z R2 term is priced per R2 changed word (16/op), not per source word (8)",
      near(t.get("words_per_op_the_price_is_read_on"), 16.0, 1e-9),
      "words_per_op_the_price_is_read_on = %s" % t.get("words_per_op_the_price_is_read_on"))
check("the d3z R2 term is 2.507 fJ/flip (the verifier's number), not 5.013",
      near(t.get("fJ_per_flip"), 2.507, 0.02), "got %s fJ/flip" % t.get("fJ_per_flip"))
iN = (D.get("intercept_N_W") or {}).get("value")
check("B_bridge_R2_correction_W is the intercept itself (§5.1: 'biased by exactly +0.273 W')",
      near(F.get("B_bridge_R2_correction_W"), iN, 1e-9),
      "correction %s W vs intercept %s W" % (F.get("B_bridge_R2_correction_W"), iN))
check("the bridge's R2 word count is 16/op", near(F.get("B_bridge_R2_changed_words_per_op"), 16.0, 1e-9),
      "dw = %s" % F.get("B_bridge_R2_changed_words_per_op"))
r2 = D.get("e_carry_R2_corrected") or {}
check("e_carry_R2_corrected is 3.482 +- 0.742 fJ", near(r2.get("fJ"), 3.482, 0.03)
      and near(r2.get("se_fJ"), 0.742, 0.02),
      "got %s +- %s fJ" % (r2.get("fJ"), r2.get("se_fJ")))
c54 = V.get("C54 C67 C68 C87") or {}
check("C54 reads CONFIRMED-ours on the primary AND on the R2-corrected value",
      c54.get("verdict") == "CONFIRMED-ours" and c54.get("e_carry_R2_corrected_verdict") == "CONFIRMED-ours",
      "%s / %s" % (c54.get("verdict"), c54.get("e_carry_R2_corrected_verdict")))
check("C54's basis no longer says the verdict depends on the term",
      c54.get("verdict_depends_on_the_R2_term") is False
      and "DOES NOT depend" in (c54.get("basis") or ""),
      "verdict_depends_on_the_R2_term = %s" % c54.get("verdict_depends_on_the_R2_term"))

print("\n[VER 2] C14 / C64 is reported, not scored (README §5.2)")
c14 = V.get("C14 C64") or {}
check("the C14 row carries no score", c14.get("verdict") == "not scored" and c14.get("scored") is False,
      "verdict %r" % c14.get("verdict"))
check("it is reported as agreement or disagreement", c14.get("reported_as") in ("AGREEMENT", "DISAGREEMENT"),
      "reported_as = %s" % c14.get("reported_as"))
check("and says why it is not scored", "§5.2" in (c14.get("not_scored_because") or ""),
      (c14.get("not_scored_because") or "")[:60])

print("\n[VER 3] C56 says what the joint-fit-minus-raw gap is")
g = (V.get("C56 C57 C63 C64 C86") or {}).get("joint_minus_raw_gap") or {}
check("the gap is 3.952 fJ/flip", near(g.get("gap_fJ_per_flip"), 3.952, 0.02),
      "got %s" % g.get("gap_fJ_per_flip"))
check("the bridge denominator is 1.8645e14 bits/s",
      near(g.get("bridge_denominator_bits_per_s"), 1.8645e14, 2e11),
      "got %s" % g.get("bridge_denominator_bits_per_s"))
check("the gap is 0.7369 W on that denominator", near(g.get("gap_W"), 0.7369, 0.002),
      "got %s W" % g.get("gap_W"))
check("the R2 term is 0.2283 W = 1.224 fJ and about 31% of the gap",
      near(g.get("R2_changed_word_term_W"), 0.2283, 0.002)
      and near(g.get("R2_changed_word_term_fJ_per_flip"), 1.224, 0.01)
      and near(g.get("R2_term_as_pct_of_the_gap"), 31.0, 1.0),
      "%s W, %s fJ, %s%%" % (g.get("R2_changed_word_term_W"),
                             g.get("R2_changed_word_term_fJ_per_flip"),
                             g.get("R2_term_as_pct_of_the_gap")))
check("the basis no longer says the gap IS the changed-word term",
      "The difference is the §5.1 CHANGED-WORD term" not in txt
      and "a PART of that gap, not the whole of it" in txt)

print("\n[VER 4] §8.6's replications are not pooled, and the heterogeneity result is printed")
z = V.get("E60's corner") or {}
check("replications_pooled_across_cards is False", z.get("replications_pooled_across_cards") is False,
      "%s" % z.get("replications_pooled_across_cards"))
het = z.get("heterogeneity") or {}
check("the heterogeneity check fires", z.get("replication_set_heterogeneous") is True
      and len(het.get("pairs_over_3SE") or []) == 2,
      "pairs over 3 SE: %s" % len(het.get("pairs_over_3SE") or []))
check("the two firing pairs are |t| 4.53 and 4.47 against 3.850",
      near(het.get("t_crit_3sigma"), 3.850, 0.01)
      and sorted(round(abs(h["t"]), 2) for h in (het.get("pairwise") or []) if h.get("ge_3SE"))
      == [4.47, 4.53],
      "%s" % sorted(round(abs(h["t"]), 2) for h in (het.get("pairwise") or []) if h.get("ge_3SE")))
check("Cochran's Q is about 26.5-28.7 on 3 df",
      het.get("cochran_Q_df") == 3 and 26.0 <= (het.get("cochran_Q") or 0) <= 29.0,
      "Q = %s on %s df" % (het.get("cochran_Q"), het.get("cochran_Q_df")))
check("the set is reported as opcode-dependent",
      "OPCODE-DEPENDENT" in (z.get("replication_set") or "")
      and "OPCODE-DEPENDENT" in (z.get("basis") or ""))

print("\n[VER 5] the C14 row says where the leakage slope moves its answer")
la = (c14.get("leak_arm_by_slope") or {}).get("E60") or {}
check("at E60's slope it reads 25.567 +- 0.230 fJ", near(la.get("fJ"), 25.567, 0.01)
      and near(la.get("se_fJ"), 0.230, 0.01), "got %s +- %s" % (la.get("fJ"), la.get("se_fJ")))
check("below the strict interval, inside only after its own 3-SE widening",
      la.get("in_strict_interval") is False and la.get("in_interval_after_3SE_widening") is True)
check("and the row says so in words", "MOVES THIS ROW'S ANSWER" in (c14.get("margin") or ""))

print("\n[VER 6] 'kept / set aside', not 'present'")
check("no row says 'registered passes present'", "registered passes present" not in txt)
check("the kept / set-aside wording is there, with the dirs accounted for",
      "registered passes KEPT" in txt and "No pass dir is missing" in txt)

print("\n[VER 7] e_cell's scaling test has no power here")
c61 = V.get("C61 C62 I-22") or {}
check("the basis says the test has no power", "HAVING NO POWER HERE" in (c61.get("basis") or ""))
check("and that the condition is UNTESTED rather than satisfied or failed",
      "UNTESTED" in (c61.get("basis") or ""))
check("the old 'nothing here shows the cell term scaling with h' claim is no longer asserted -- "
      "it survives only as a quotation of what the wf4 build read",
      txt.count("nothing here shows the cell term scaling") ==
      txt.count("the wf4 build read the same non-result as 'nothing here shows the cell term "
                "scaling with h'"),
      "%d occurrence(s), all attributed" % txt.count("nothing here shows the cell term scaling"))
sd = ((c61.get("scaling") or {}).get("per_bit_difference_high_minus_low") or {})
check("the paired difference is -0.186 +- 0.341 fJ/bit, |t| 0.54",
      near(sd.get("value"), -0.186, 0.01) and near(sd.get("se"), 0.341, 0.01)
      and near(abs(sd.get("t") or 0.0), 0.54, 0.02),
      "%s +- %s, |t| %s" % (sd.get("value"), sd.get("se"), sd.get("t")))

print("\n[VER 8] C79's margin to the 0.5 pJ/op boundary")
c79 = V.get("C79 C80 C90") or {}
check("the boundary is 1.65 SE away", near(c79.get("SE_to_the_0p5_boundary"), 1.65, 0.02),
      "%s SE" % c79.get("SE_to_the_0p5_boundary"))
check("the 3-SE upper bound (0.855 pJ/op) is above 0.5, so the OPEN band is not excluded",
      (c79.get("pJ_per_op_3SE_upper_bound") or 0) > 0.5
      and near(c79.get("pJ_per_op_3SE_upper_bound"), 0.855, 0.01),
      "upper bound %s pJ/op" % c79.get("pJ_per_op_3SE_upper_bound"))
check("and the margin is stated in the row", "the margin" in (c79.get("margin") or ""))

print("\n[VER 9] the ladder-intercept row names which OPEN it is")
li = V.get("the ladder intercept") or {}
check("the registered OPEN arm does not fire", li.get("registered_open_arm_fires") is False)
check("X - N per changed source word is -0.00891 +- 0.00515 W, |t| 1.73 vs 3.850",
      near(li.get("X_minus_N_per_changed_source_word_W"), -0.00891, 2e-5)
      and near(li.get("X_minus_N_per_changed_source_word_se_W"), 0.00515, 2e-5)
      and near(abs(li.get("X_minus_N_t") or 0.0), 1.73, 0.02)
      and near(li.get("X_minus_N_t_crit_3sigma"), 3.850, 0.01),
      "%s +- %s, |t| %s vs %s" % (li.get("X_minus_N_per_changed_source_word_W"),
                                  li.get("X_minus_N_per_changed_source_word_se_W"),
                                  li.get("X_minus_N_t"), li.get("X_minus_N_t_crit_3sigma")))
check("the row says this OPEN is unnamed by the §9 partition",
      "UNNAMED by the §9 partition" in (li.get("open_arm") or ""))

print("\n[VER 10] C22's margin line")
c22 = V.get("C22 C23 C26") or {}
check("1.000 is excluded at |t| 4.82 against the 4.530 window",
      near(c22.get("rho_SE_to_1p000"), 4.82, 0.02)
      and near(c22.get("rho_t_crit_3sigma"), 4.530, 0.01),
      "|t| %s vs %s" % (c22.get("rho_SE_to_1p000"), c22.get("rho_t_crit_3sigma")))
check("which is 106% of the threshold, and the row says so",
      "106" in (c22.get("margin") or ""), (c22.get("margin") or "")[:80])

print("\n[VER 11] C58's four-pass caveat")
c58 = V.get("C58 C83 C84 C91") or {}
check("the W-vs-E half rests on 4 passes, below the 6-pass floor",
      c58.get("W_vs_E_n_passes") == 4 and c58.get("pass_floor_for_a_confirmatory_item") == 6)
check("its 3-sigma-equivalent quantile is 9.22", near(c58.get("W_vs_E_t_crit_3sigma"), 9.22, 0.02),
      "%s" % c58.get("W_vs_E_t_crit_3sigma"))
check("it could not have detected a 3 W asymmetry",
      (c58.get("W_vs_E_detectable_at_3SE_W") or 0) > 3.0,
      "detectable only above %s W" % c58.get("W_vs_E_detectable_at_3SE_W"))
check("and the caveat is in the row", "four-pass caveat" in (c58.get("caveat") or ""))

print("\n[VER 12] C33's spread on §8.4's unit of replication")
c33 = V.get("C33 C37") or {}
check("the row reads the paired per-pass statistic",
      "paired per-pass" in (c33.get("spread_statistic_read") or ""),
      c33.get("spread_statistic_read"))
check("the paired fixed-pair spread is 2.666 +- 0.546 fJ, |t| 4.88 over 12 passes",
      near(c33.get("paired_spread_fJ"), 2.666, 0.01)
      and near(c33.get("paired_spread_se_fJ"), 0.546, 0.01)
      and near(abs(c33.get("paired_spread_t") or 0.0), 4.88, 0.02)
      and c33.get("paired_spread_n_passes") == 12,
      "%s +- %s, |t| %s, n=%s" % (c33.get("paired_spread_fJ"), c33.get("paired_spread_se_fJ"),
                                  c33.get("paired_spread_t"), c33.get("paired_spread_n_passes")))
check("the cross-item reading the wf4 build used (0.462, |t| 5.78) is printed beside it",
      near(c33.get("cross_item_spread_se_fJ"), 0.462, 0.01)
      and near(abs(c33.get("cross_item_spread_t") or 0.0), 5.78, 0.02),
      "%s, |t| %s" % (c33.get("cross_item_spread_se_fJ"), c33.get("cross_item_spread_t")))
mm = ((c33.get("spread") or {}).get("paired_per_pass_max_minus_min") or {})
check("the per-pass max - min reading (3.581 +- 0.647, |t| 5.54) is there too",
      near(mm.get("spread_fJ"), 3.581, 0.01) and near(mm.get("se_fJ"), 0.647, 0.01),
      "%s +- %s" % (mm.get("spread_fJ"), mm.get("se_fJ")))
check("all three readings fire the same arm", c33.get("verdict") == "OPEN")

print("\n[SKEPTIC] the two issue-rate levels follow the loop head's address mod 32")
lh = res.get("loop_head_alignment") or {}
check("the finding is re-derived from the disassembly, not quoted",
      lh.get("one_rate_per_residue") is True and lh.get("residues_distinct") is True)
check("heads at 6 (mod 32) run 0.6088 and heads at 22 run 0.5814",
      lh.get("fast_residue") == 6 and lh.get("slow_residue") == 22
      and near(lh.get("fast_rate"), 0.6088, 1e-4) and near(lh.get("slow_rate"), 0.5814, 1e-4),
      "fast %s -> %s, slow %s -> %s" % (lh.get("fast_residue"), lh.get("fast_rate"),
                                        lh.get("slow_residue"), lh.get("slow_rate")))
check("the c2 family's four opcodes pin the map one-to-one",
      sorted((lh.get("c2_by_mode") or {}).keys()) == ["300", "301", "302", "303"]
      or sorted((lh.get("c2_by_mode") or {}).keys()) == [300, 301, 302, 303],
      "modes %s" % sorted((lh.get("c2_by_mode") or {}).keys()))
check("and the four df.addr kernels agree as a count",
      (lh.get("addr_count_check") or {}).get("agrees") is True,
      "%s" % (lh.get("addr_count_check") or {}))
check("the S10 row carries it as a visible finding",
      "LOOP HEAD'S ADDRESS MOD 32" in ((V.get("S10 C16 C59") or {}).get("finding") or ""))

print("\n[verdict counts]")
from collections import Counter                                       # noqa: E402
cnt = Counter(v["verdict"] for v in (res.get("verdicts") or []))
print("  %s  (%d rows)" % (dict(sorted(cnt.items())), len(res.get("verdicts") or [])))
check("15 claim rows, every one with a verdict or an explicit 'not scored'",
      len(res.get("verdicts") or []) == 15 and all(v.get("verdict") for v in res["verdicts"]))

print("\n%d checks, %d failed" % (N[0], len(FAILS)))
for f in FAILS:
    print("  FAILED: %s" % f)
sys.exit(1 if FAILS else 0)
