# Q140(l) registration, amendment A1 (dated Wed 4 Nov 2026, about 01:55 PST)

*Written **after** every fit, score and prediction of this lane (the registered result and the freeze, `5b98bd5c`,
01:04:31 PST) and after its verifier's report. It changes no fit, score, rule, frozen number or verdict.
[`REGISTRATION.md`](REGISTRATION.md) and [`registration.json`](registration.json) keep their text as committed in
`245caffe` (00:43:45 PST). The README's [§ Corrections after verification](README.md#corrections-after-verification)
lists every correction of this pass (C1-C9).*

1. **The registration's window (C5).** Its header gives "about 00:10-00:55 PST". From the lane's session record, as read by
   its verifier, the lane's first action was at 00:24:36 PST and it read the committed files from then on. REGISTRATION.md
   was written at 00:42:44 PST and edited at 00:43:00, and `245caffe` was committed at 00:43:45. "00:10" was wrong, and
   "00:55" was an estimate made before the commit. The order the registration claims holds: the commit precedes every
   output of the lane (the fit code was first written at 00:47:44 PST, its first output at 00:49:00).
2. **The self-test (C7).** § "What is frozen" says "A self-test checks it reproduces the fit's own predictions". The
   check that E160's 752 MHz fp16 anchor burst is left out counted the data's bursts and never compared the code's
   offset with anything. It now recomputes that offset from `m9_a2.json`'s own numbers over the bursts at 795 MHz or more,
   compares it with `predict_m9_a2.session_delta`'s, checks it differs from the mean with the 752 MHz burst counted, and
   compares all three formats with the fit's own `session_deltas_w`. Under a predictor that counts the 752 MHz burst, the
   corrected check fails where the old one passed (a scratch-only mutation test). `predict_m9_a2.py` and `m9_a2.json` are
   unchanged (sha256 `cc6fbccc…`).
3. **What the registered checks report (C1).** § "Reported, never a verdict" asks for "what M9's level terms (the fallback
   δ, no anchors ran there) would change in each miss" on E159 and E161. The committed figures (E161 −0.08 W, E159
   −1.43 to −1.49 W) apply the zeros-level term alone, β·δ at M9's T_ref of 54.38 °C, with each check's own die law kept
   (Q139(e)'s 0.442 W/°C from its 56.0 °C reference die; G3's P0 with no start-die term). M9's die-start term composed in
   place of that law reads E161 +0.24 W and E159 −2.49 / −0.95 / −0.49 W. Both are reported post hoc in
   [`corrections.txt`](corrections.txt) C1. Neither is a registered verdict, and no rule here chooses between them.
