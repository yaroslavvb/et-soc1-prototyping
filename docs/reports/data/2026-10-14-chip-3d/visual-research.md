# Research for the four-scale 3D diagram upgrade

2026-10-14 (Wed, ISO week 42). Follow-up to the chip diagram's metal,
FinFET, fin and channel views.

User request, verbatim:

> Improve the quality of these diagrams. Do some research to find good visualizations and create a higher-quality visualization with more details.

The following primary sources informed the upgrade. Page numbers below are
one-based PDF pages; named figures and printed slide numbers remove ambiguity.
The research pass read source text, labels and figure captions. PDF screenshot
requests returned image references; this record does not claim a pixel-level
comparison with those source figures. No external illustration is copied into
the visualization: the interactive geometry and section drawings are original.

## Sources and inspected references

| Source | Specific reference | Useful design evidence |
| --- | --- | --- |
| [Intel, 22nm transistor technology details, May 2011](https://download.intel.com/newsroom/kits/22nm/pdfs/22nm-Details_Presentation.pdf) | PDF pp. 4–8: planar comparison, single-fin and multiple-fin tri-gate schematics, fin/gate micrograph; p. 14: fully depleted tri-gate section | Progressively reveal the same device. Distinguish silicon, isolation, gate dielectric and gate. A common gate can control multiple connected fins. |
| [Chenming Hu, chapter 7 lecture slides](https://www.chu.berkeley.edu/wp-content/uploads/2020/01/Chenming-Hu-ch7-slides.ppt-Compatibility-Mode-Repaired.pdf) | Slides/PDF pp. 31–32: bulk and SOI FinFET cross-sections, short/tall fins; p. 38: inversion-charge density across a fin | Three gated faces; ideal rectangular tri-gate width is twice fin height plus fin thickness. Charge occupies a finite region and can be enhanced near corners. |
| [Chenming Hu, chapter 6](https://www.chu.berkeley.edu/wp-content/uploads/2020/01/Chenming-Hu_ch6-1.pdf) | PDF pp. 13, 16–18: inversion charge, Figs. 6–16/6–17 and pinch-off; p. 31, §6.9.1: velocity saturation versus pinch-off | Gate voltage controls carrier population; drain bias produces transport. Channel density can fall toward the drain, while current continues through the drain-side high-field region. |
| [Intel, 14nm technology presentation, August 2014](https://download.intel.com/newsroom/kits/14nm/pdfs/Intel_14nm_New_uArch.pdf) | PDF pp. 17–21, printed slides 17–21: fin height/pitch comparisons, taller/thinner fins, metal gate | Dimension arrows and a transverse section make geometry understandable. These Intel measurements are reference examples, not dimensions of ET-SoC-1. |
| [imec, Mitigating the thermal bottleneck in advanced interconnects](https://www.imec-int.com/en/articles/mitigating-thermal-bottleneck-advanced-interconnects) | Opening BEOL description; Fig. 4, three via-connectivity configurations; discussion of local, intermediate and global layers | Wires sit inside insulating dielectric; metal-filled vias connect neighboring levels. Wire roles and dimensions differ through the stack. |
| [imec, Can binary or ternary compounds beat Cu in future interconnect applications?](https://www.imec-int.com/en/articles/can-binary-or-ternary-compounds-beat-cu-future-interconnect-applications) | Opening copper-conductor discussion; Fig. 6, potential multilayer cross-section | A copper core needs barrier, liner and cap layers for reliability. A magnified section can make these otherwise invisible layers legible. The future alloy scheme is not adopted as ET-SoC-1 technology. |
| [TSMC, On-chip Interconnect](https://research.tsmc.com/page/on-chip-interconnect/16.html) | Research-area introduction, copper/low-k wiring | Confirms copper/low-k as appropriate generic interconnect teaching context; line and via resistance and dielectric capacitance matter. |

## Design guidance adopted for the upgrade

- Keep consistent material colors, orientation and source/drain placement from
  device overview to the fin and channel details.
- Model distinct fin silicon, high-k dielectric, metal gate, gate spacers,
  isolation, source/drain regions and contact metal. Use a cutaway or exploded
  view to reveal interfaces that otherwise occlude one another.
- Pair orbitable geometry with clear transverse and longitudinal sections.
  Use symbolic dimensions and highlight the controlled perimeter:
  `W_eff ≈ N × (2H_fin + T_fin)` for the idealized rectangular tri-gate.
- Make multiple fins share gate and terminals so fin count explains effective
  width rather than appearing to create unrelated devices.
- Show a qualitative charge-density region inside silicon, with gate-drive
  control and an explicitly fixed positive drain bias explaining their different
  roles. Particle motion supplements the density view and uses a deliberately
  slowed educational timescale.
- Give metal wiring a hierarchy of lower local and upper wider conductors,
  connected vias, dielectric context and a magnified material section.
- Retain a fixed camera distance during orbit and stable callout placement from
  the previous two interaction fixes.

## Physical scope and caveats

All geometries, layer counts, dimensions, voltage scales, densities and particle
speeds are illustrative, not a reconstructed ET-SoC-1 layout or a calibrated
device simulation. Process-node names do not supply physical gate dimensions.
Thin layers may be exaggerated to remain visible.

The model is an enhancement-mode n-channel bulk tri-gate FinFET. The gate wraps
the top and two side faces, not the bottom as in a gate-all-around device. STI
surrounds the exposed fin base while the bulk fin remains rooted in silicon.
Do not introduce nanosheets or backside power as if they were this device.

Inversion is not literally three independent wires or a zero-thickness skin.
At zero drain bias a channel may exist without net drift. For positive drain
bias, electrons move source to drain and conventional current points drain to
source. Pinch-off does not mean current stops; simple long-channel pictures also
need qualification for short-channel velocity saturation and volume inversion.
Any omitted leakage is identified as a simplification rather than a claim that
an off transistor has exactly zero current.
