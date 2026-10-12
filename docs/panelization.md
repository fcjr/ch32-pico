# Five prototype panels

The requested batch is five panels with four identical boards each, for 20
complete boards. KiKit 1.8.1 produces a nominal 93 x 71 mm panel from the saved
routing checkpoint. This fits inside a 100 x 100 mm size envelope; it does not
establish eligibility for a promotional price. JLC must quote the four-layer,
1 mm, ENIG, castellated design and panelized assembly.

```sh
make panel-dependencies
make panel-preview
make cost-review
```

The configuration is code in `hardware/panel.py`. Four boards sit in one row
with 3 mm routed gaps, 7 mm top/bottom rails and 3 mm clearance to those rails.
Each board has one 3 mm breakaway tab at each short end. No tab touches a
castellated side. Three tooling holes and three fiducials are on the rails.
The mousebites are 0.5 mm drills at 1 mm pitch, offset outward 0.2 mm. Trim
remaining tab material flush after depaneling to restore the Pico envelope.
Panel rigidity and the tab details still need JLC's manufacturing review.

[JLC's assembly capabilities](https://jlcpcb.com/capabilities/pcb-assembly-capabilities)
exclude castellated holes from Economic PCBA. This board therefore requires
**Standard PCBA**, regardless of the small prototype quantity. The panel has
rails and fiducials and exceeds Standard's 70 x 70 mm minimum by 1 mm in its
short dimension; the original nominal 70 mm panel was too close to that limit.
Individual boards keep their original dimensions and all four mounting holes.
Milled slots and mousebites preserve the castellated sides.
Enter one design repeated four times per customer-supplied panel,
with an order quantity of five panels. Use the panel BOM/CPL with panel Gerbers;
do not ask JLC to repeat them four times again. The five-panel batch contains
20 copies of every single-board BOM item, plus assembly attrition.

The generated `build/panel-preview/` includes the KiCad panel, front SVG,
Gerber ZIP, drills, 17-row BOM, 132-row CPL and a hash manifest. DRC has zero
violations and zero open connections. Each copy's pads, net assignments,
component rotations and trace/via geometry are checked against the source
board before and after zone fill. JLC's assembly model rotations remain pending.

Dependencies are pinned in `scripts/kikit-requirements.txt`. The local virtual
environment uses KiCad's Python without altering or re-signing the installed
app. The wrapper keeps a wx application alive and rejects null native board
loads. Absolute file paths avoid a KiCad project-load working-directory issue
that otherwise caused KiKit to pass a failed reload to the native zone filler.
The script also restores the source's explicit default netclass because KiKit
1.8.1 replaced it with KiCad's 0.20 mm default during project transfer.

Regenerate the panel after any circuit or placement change. The preview is
for engineering and JLC assembly review, not an order release.
