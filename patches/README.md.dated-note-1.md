# Dated note 1 beside patches/README.md (Fri 6 Nov 2026, week 45): patch 0003 on a card, and its hazards

*Beside [`README.md`](README.md), which it edits nowhere. Written by the records round after Q147 (Q148(r)), from the firmware desk study
[`tools/claims-v3/fw-q147/`](../tools/claims-v3/fw-q147/README.md) (`8060a8f5`, with its dated notes 1 and 2) and its verifier. Desk
only: nothing here touched a card.*

**The README's last row says** that running `0003-pmc-configure-syscall-353f20e.patch` on a card "needs a signed firmware image, which
the open tree cannot produce". That is no longer the barrier: rebuilt, non-public 0.22.0 images have booted on the lab's cards since
7-10 Oct 2026 (the study's section 4 and its dated note 1). The barrier is the path: putting the patch on a card is a firmware update that
rewrites the card's other flash bank and runs the PMIC update, then a card reset that may power-cycle the card (a definite power cycle
after an update that wrote the PMIC), and the same again to undo it. The lab's rules forbid both, `dmcmd_audit` reads NO-GO on the two
commands (both WRITE), and the study found the patch would not help the open problems anyway. **Not attempted; NO-GO.**

**The patch's own hazards** (the study's section 4, confirmed by its verifier in the source at et-platform `836a4ab60`):

1. **It never restores the boot events.** The firmware zeroes `hpmcounter4`-`8` before each launch but sets their events only at boot,
   so one kernel's choice persists into every later kernel on those harts, other users' included, and, through the neighbourhood sums,
   into what neighbouring harts read.
2. **It writes raw monitor control words, interrupt bits included.** Its shire-cache and memory-shire writes pass the caller's control
   word unchanged, so they can set the overflow-interrupt enables (bits 3, 7 and 20 of the shire-cache monitor's control register), which
   the stock firmware never sets; and the Master Minion samples those same counters for the management statistics.
3. **Its monitor kinds reach any shire.** The shire-cache bank kind (shire 0-32, bank 0-3) and the memory-shire kind (0-7) take any
   shire, not only the caller's own.

A version for a card would restore the boot defaults at kernel return, mask the interrupt bits, and limit the writes to the caller's own
shire; and it would still need the owner's word for one named card and window, and the firmware maintainer's own authorization and
execution, as the study's section 5 says.

SPDX-License-Identifier: Apache-2.0
