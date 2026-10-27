# Q129 — the firmware gate every raised-TDP arm has to pass, read correctly

Tue 27 Oct 2026 (week 44). **Desk only: no card was opened, claimed or set for this.** A correction to a
firmware hazard that was first written up with the wrong mechanism, the wrong field and the wrong direction.

The governor work of Q129 (E69, `docs/reports/data/2026-10-27-e69-governor-knob/`) moves the static TDP level on
one card. A first pass over the firmware reported that the power-throttle check held *both* the measured average
card power *and* the TDP level in a 16-bit milliwatt value, that such a value **saturates** just above the default
65 W cap, and that the consequence was that a raised-cap arm would be "not interpretable". Each of those three
claims is wrong, and the direction of the error matters: the real failure mode is **less throttling, not more**.

## What the public source says

All of the following is in the open `et-platform` repository (`aifoundry-org/et-platform`, Apache-2.0), at the
`device-bootloaders` version that matches the firmware the lab's cards report, **BL2 0.22.0**:

| Fact | Where |
|---|---|
| The averaged system power field is a **16-bit value in units of 10 mW** (so the field itself reaches 655.35 W) | `et-trace/include/et-trace/layout.h:467` |
| The conversion to milliwatts is a plain `×10` macro, `POWER_10MW_TO_MW(pwr_10mw) (pwr_10mw * 10)` | `device-bootloaders/src/ServiceProcessorBL2/include/thermal_pwr_mgmt.h:35` |
| In 0.22.0 both locals of the throttle check are 32-bit: `uint32_t avg_soc_pwr_mW = (uint32_t)(POWER_10MW_TO_MW(…))` and `uint32_t tdp_level_mW` | `…/services/thermal_pwr_mgmt.c:869-871` |
| The throttle-**down** branch fires on `avg_soc_pwr_mW > tdp_level_mW`; the throttle-**up** branch on `avg_soc_pwr_mW < tdp_level_mW` | `…/thermal_pwr_mgmt.c:898` and `:910` |
| The default software-managed cap is **65 W**, the thermal default **65 °C**, and a compile-time guard requires the catastrophic threshold to exceed the software cap | `…/include/thermal_pwr_mgmt.h:41,48,50` |
| A conversion in exactly this function was **fixed after 0.21.0** (released 2024-09-25): the changelog entry is `[SW-22147] Fix conversion in check_power_throttle_conditions function`, listed under *Unreleased*, i.e. in the 0.22.0 line | `device-bootloaders/CHANGELOG.md` |

The pre-0.22.0 tree is not reproduced here; it was read in a private source review, which found the earlier
conversion narrowing the **measured average** (only the average — the TDP level was already a 32-bit local) to a
16-bit milliwatt type.

## The mechanism, and why the direction matters

A C cast to a 16-bit type **wraps**; it does not saturate. 65,535 mW is 65.535 W, so on a build whose throttle
check narrows the measured average to 16 bits:

- below ~65.5 W the comparison behaves normally;
- **above 65.536 W the average wraps to a small number** — 66.0 W reads as 0.464 W. The throttle-**down** test
  (`avg > tdp`) goes false and the throttle-**up** test (`avg < tdp`) goes **true**, so the firmware's power arm
  stops limiting and starts **raising** the clock while the card is over its cap.

So a raised cap on such a build is not merely uninterpretable: above 65.5 W there is effectively **no firmware
power throttle at all**, and the power arm pushes the wrong way. What still guards such a build:

1. the **thermal** arm, which is evaluated first in the same function and is unaffected;
2. the boot-time PMIC catastrophic power alarm (the firmware's hardware threshold constant);
3. whatever the host harness enforces — in this workflow, the 85 W board-power abort.

**Lowering** the cap or the threshold keeps the average under the wrap and is unaffected either way. That is one
more reason lowering is the safe direction, as the field manual says.

## The gate, restated

Before any arm that **raises** the TDP level:

1. read the card's reported firmware/BL2 version fresh (`DM_CMD_GET_MODULE_FIRMWARE_REVISIONS`);
2. find the source revision that matches it, and confirm the throttle check's conversion is the 32-bit one — i.e.
   that the build is at or after the `SW-22147` entry. A build before it must be treated as having **no firmware
   power throttle above 65.5 W**;
3. re-read the two setter paths at that same revision for the field manual's rule 8 (they must write service-
   processor RAM and nothing else), rather than at whatever revision is newest;
4. keep a host-side power abort armed regardless, because guard (3) above is the only one under our control.

**For the card E69 used:** it reports BL2 0.22.0, the 0.22.0 tree carries the 32-bit conversion, and the rule-8
read was done at 0.22.0 (`tools/claims-v3/knob/CHANGE-RECORD.md`). E69's raised-cap arm is therefore
interpretable, subject to the build-identity residual that record already names — a reported "0.22.0" does not
prove which 0.22.0 binary is on the card, and the card exposes no build hash.

## What this changes

Nothing numeric in Q128's chain: no pJ moves. It changes a **safety gate** and one sentence of the open-questions
list — the hazard is an *absent* power limiter above 65.5 W on an older build, not an over-eager one, and the
gate's test is the conversion's width at the card's own revision.
