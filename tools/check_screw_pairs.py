#!/usr/bin/env python3
"""Verify every preset's screwAngleList contains opposing pairs.

The generator draws each screw hole as a cylinder running from the leg axis
OUTWARD to the surface (cylinder(h=legDia()/2)), so a single angle bores only
half a hole and leaves the opposite wall solid - a bolt cannot pass through.
A hole is only a through hole if for every angle a in the list, a+180 is also
in the list.

This is the defect that shipped in the endcap preset as screwAngleList [90]:
the mesh was perfectly manifold and every bore measured correctly, so
manifoldness and diameter checks all passed. The invariant is about the
parameters, not the mesh, which is why it needs its own check.
"""
import json
import sys

presets = json.load(open("catio/catio-presets.json"))["parameterSets"]
fail = False
for name, p in sorted(presets.items()):
    raw = p.get("screwAngleList", "[]")
    angles = [float(x) for x in raw.strip("[] ").split(",") if x.strip()]
    if not angles:
        print(f"ok    {name}: no screws")
        continue
    unpaired = [a for a in angles if (a + 180) % 360 not in [b % 360 for b in angles]]
    if unpaired:
        print(f"FAIL  {name}: {raw} -> angles {unpaired} have no opposite; "
              f"these bore half a hole and no bolt can pass through")
        fail = True
    else:
        print(f"ok    {name}: {raw} fully paired")
sys.exit(1 if fail else 0)
