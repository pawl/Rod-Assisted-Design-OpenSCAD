# Parts list and batch export

The part list is a CSV: one row per part, one column per Customizer parameter.
Keep it in a spreadsheet, export as CSV, and rebuild everything with one
command. No GUI, and nothing to learn beyond the parameter names already in
the .scad.

```
tools/build_parts.py                                   # examples/parts.csv -> ./stl
tools/build_parts.py my-parts.csv my-stl-dir           # or point it anywhere
tools/build_parts.py --span 600 examples/parts.csv     # also print rod cut lengths
```

```
ok    3-8th-4way-90deg     qty   1      15.37 cm^3   (2 render warning(s))
        rod seats 10.90 mm from centre, 22.0 mm of it inside the socket
        cut for 600 mm span: 578.20 mm
ok    shelf-corner         qty   4     114.99 cm^3   (2 render warning(s))
        rod seats 25.00 mm from centre, 44.0 mm of it inside the socket
        cut for 600 mm span: 550.00 mm
ok    shelf-tee            qty   2      66.15 cm^3
ok    shelf-foot           qty   4      25.12 cm^3
```

## The CSV

Only the columns you fill in are passed to OpenSCAD, so **a blank cell means
"use the default in the .scad"**. Look at `shelf-foot` in the example: it is an
end cap, so the connector columns are left empty.

Two columns are metadata rather than parameters:

| column | meaning |
|---|---|
| `name` | output filename, required |
| `qty` | how many to print, carried into the summary |

A value containing commas, like a screw angle list, just needs normal CSV
quoting - `"[0, 180]"` - which is what a spreadsheet writes anyway.

## Rod cut lengths

The one number a spreadsheet cannot work out on its own is how much rod each
connector swallows, because that comes from the socket geometry. A rod bottoms
out on the internal stopper, whose face sits `stopperLeg + thickness` from the
connector centre, so for a rail spanning two connectors:

```
cut length = centre-to-centre span - 2 x (rod seat from centre)
```

`--span` does that arithmetic, or take the "rod seats N mm from centre" figure
into a spreadsheet column and let it drive a whole cut list. Sockets with
`stopperEnable = 0` are skipped, since the rod passes straight through and its
length is set by the layout rather than the connector.

This is checked, not asserted. For a `shelf-corner` at dowelDia 26 and
thickness 6 the formula predicts the rod seats 25.00 mm from centre with
44.0 mm of socket depth; measuring the rendered mesh gives a bore wall running
25.00..69.00 mm from centre, so 25.00 and 44.0. `tools/build_parts.py
--selftest` pins the formula to those measured numbers.

## Checking, not just exporting

Each part is verified after it renders. The build fails on an OpenSCAD error or
a mesh that is not edge-manifold, and reports warnings without stopping.

Volumes are printed because OpenSCAD does not validate parameter values: a
nonsense value is accepted silently and renders altered geometry with no
warning at all, so the checks catch broken *renders*, not broken *parameters*.
A part that quietly changed shows a changed volume.

`tools/measure_stl.py` does the mesh checking and is useful on its own:

```
tools/measure_stl.py part.stl
tools/measure_stl.py part.stl --bore "0,0,0,0,0,1,58,66,11.95,centreBore"
```

It reports volume, area, bounding box, and whether every edge is shared by
exactly two triangles, and exits nonzero if not.

## The 3/8" row reproduces the STL in this repo

`3-8th-4way-90deg` is a reconstruction of the parameters behind
`3-8th 4-way connector #8 cs screw flat 90 degree.stl`, recovered by measuring
that mesh:

| | bounding box | volume |
|---|---|---|
| committed STL | x/y +-28.14, z -6.90..32.90 | 15369.178 mm^3 |
| this row | x/y +-28.14, z -6.90..32.90 | 15373.470 mm^3 |

Bounding box matches exactly on all six values, volume within 0.03%. How the
numbers were recovered, in case it is useful for documenting other parts:

- bore and outer radii about the centre axis gave `dowelDia` 9.8 and an outer
  15.8, so `thickness` 3.0; a third radius at 6.9 gave `chamfer` 1.0
- outermost vertices clustered at three angles 90 degrees apart, so `legNum` 3
  with `horzAngle` 90 (the "4-way" of the filename counts the centre leg)
- flats on the outer legs at z +-6.9 against a 7.9 radius gave
  `flatTopDepth` and `flatBottomDepth` of 1.0
- the top face at z 32.9 gave `centerLegLength` 25, and the leg tips the same
  25 for `lengthLeg`
- the centre bore starting at z 10.9 rather than the part bottom means a
  stopper, and its depth matches `stopperEnable` 2
- the screw hole spans z 18.9..22.9, so 3.8 across, centred at 20.9, putting
  `screwOffset` at 12
- the ribs were found by rendering it and looking, after a first pass measured
  the wrong zone and wrongly concluded there were none

Anything leaving no trace in the mesh cannot be recovered, so values like
`screwCBDia` stay at their defaults.

Note the committed STL is not edge-manifold (16 edges shared by four faces),
so the two are not byte-comparable.
