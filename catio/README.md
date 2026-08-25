# Catio build files

Parameter presets and build notes for an outdoor cat enclosure framed from
3/4" EMT conduit, using the connector generator in this repo
("Rod Assisted Design Customizer.scad") plus the net anchor feature.

STLs and preview renders are build outputs, so they are not committed -
regenerate any part from the presets with one command (see Regenerating and
testing below).

Frame: 36" x 36" footprint. Top and walls are netting. Design load is wind,
not cats (~25 lb structure, no climbing load).

## Calibration these presets assume

Do not reuse these numbers with different tube, filament, or wall settings.

- Measured EMT OD: **23.30 mm** with calipers (ANSI nominal is 23.42; trust
  the measurement). The welded seam runs slightly fatter, so 23.30 is a floor.
- This printer + PCTG shrinks holes by **~0.30 mm** (verified: 23.67 modeled
  bore measured 23.37 printed).
- Working tolerance: **0.60 mm** -> `dowelDia = 23.30 + 0.60 = 23.9`.
- Printed socket lands ~23.55-23.60, i.e. 0.25-0.30 mm clearance: a loose
  slip fit, on purpose. The screw carries the load; the socket only aligns.
  Never hammer PCTG parts on - layer cracks are invisible.
- Faceting note: at `$fn = 50` the modeled 23.90 bore is a polygon whose
  across-flats width is 23.85, so the effective tolerance is ~0.55. Already
  accounted for in the numbers above.
- The README's generic +0.1-0.2 mm tolerance advice is calibrated for a
  different setup and produces an interference fit here.

## Print profile

0.2 mm layers, 6 walls, 40% gyroid, brim on, PCTG at 260-270 C, low fan.
Print flat-bottom-down exactly as the STLs are oriented; everything is
support-free (teardropped holes, 45-degree features). Changing walls or
material invalidates the tolerance calibration.

## Outdoor durability (research findings, not yet field-verified)

The geometry is not the weak point outdoors - the material and finish are.

- **Do not print these black.** This is the sharper constraint for PCTG
  specifically, and the more actionable of the two. Dark plastic in direct
  summer sun measures 68-82 C on an exposed surface. PCTG's heat deflection temperature
  is ~76 C, right inside that band, so a black
  part can sit at or above its HDT on hot afternoons. HDT is measured under
  load and these parts carry almost none (the bolt takes the shear), so this
  is a slow creep and socket-ovalling risk across seasons, not sudden
  collapse - but it is free to avoid.
- **UV: PCTG has real margin over PETG, but is not UV-stable.** This matters
  because the vivid failure reports are PETG, not PCTG. One documented case
  lost usable PETG in **about a year** under strong summer UV plus sub-zero
  winters, the parts holding their shape but going stiff and snapping "when
  stressed ever so slightly". Do not read that as a PCTG timeline. The
  difference is structural rather than marketing: photo-degradation of these
  copolyesters proceeds by chain scission, and studies find **higher
  trans-CHDM content significantly improves photostability** (better
  mechanical retention, less chain scission). PCTG is the CHDM-rich member of
  the family, so it degrades slower by construction, and it starts tougher,
  which means further to fall before it turns brittle. It still is not
  stabilized against UV, so coat it - just treat this as extending service
  life rather than as a countdown.
- **The two pull opposite ways.** Black pigment blocks UV at the surface but
  absorbs heat; light colors stay cooler but let UV penetrate deeper.
  Resolve it with a coating instead of pigment: print a light or mid tone and
  paint it. Opaque beats clear - the practitioner consensus is that the
  thicker and more opaque the coating, the longer the part lasts, with
  **zinc-oxide-based paint** best because zinc oxide absorbs UV (it is the
  active ingredient in sunscreen). **Marine/chandlery paint** is the easy
  place to buy that, since boat coatings are formulated for doubled UV off
  the water. Automotive clear coat is the fallback. Plan a touch-up coat
  about once a year in strong sun.
- **Paint after assembly, not before.** A builder using the same tubing
  spray painted every part first and reported scratching a lot of it
  back off during assembly. Dry-fit, drill, disassemble, paint, then do final
  assembly gently - or just touch up afterward.
- **ASA would solve both** (HDT ~85-102 C, inherently UV stable, and it is
  what the upstream author used). It is not recommended here because it
  invalidates this calibration - ASA shrinks considerably more than PCTG, so
  `dowelDia` would need re-deriving from a fresh test print, and these
  flat-bottomed parts warp badly without an enclosure.
- **Thermal fit is a non-issue** (calculated, PCTG 65e-6/K vs steel 12e-6/K):
  socket clearance runs 0.256 mm at -15 C to 0.369 mm at 75 C, so it never
  binds on the tube. A 36" steel rail grows 0.82 mm across that swing, which
  the loose sockets absorb. The deliberately loose fit pays off here.

## Parts

| Preset | Qty | Use |
|---|---|---|
| `catio-corner-bottom` | 4 | Bottom corners. Center bore is open so the post passes through and bears directly on the ground (rod in compression, per the author's guidance). |
| `catio-corner-top` | 4 | Top corners, installed flipped (center leg down over the post). The stopper shelf closes the bore against rain and takes wind uplift in compression. |
| `catio-tee-netanchor` | 4-6 | Net tie-off points slid onto the top rails before assembly (no stoppers, rail passes through). Rotate so the lug points where you want, then screw. |
| `catio-tee-branch` | 0 | Only needed for a stepped-height frame; a uniform-height box does not use it. Structural tee: post passes through the colinear sockets, branch socket takes a rail at 90 degrees. For side rails meeting the back posts at 48". |
| `catio-endcap` | 6 | Feet under the four posts (spreads load, protects the surface underneath), plus 2 spare. A closed box has no other exposed tube ends. |

All connector sockets: bore 23.9, wall 3.5 mm, ~46 mm rod engagement on
corners. Net anchor lug: 10 mm hole (~9.7 printed), sized for cord, zip ties,
or small S-hooks. On corners the lug sits at the flat-bottom end of the
vertical barrel, on the outside face of the corner - flipped top corners put
it up top where the net edge wants to tie.

## Hardware (1/4-20)

- Screw pockets are **countersinks**: 7.0 mm shaft holes (~6.7 printed) opening
  to a 14 mm cone at the surface, both screws of a socket in line, so one bolt
  passes through the whole joint.
- Use **1/4-20 x 1.5" stainless flat head socket cap screws + nylock nuts**.
  Flat heads seat flush in the cone. Earlier versions of these presets used a
  13 mm counterbore, which cut the full 3.5 mm wall and left a 0-0.35 mm
  crescent of plastic around the breakthrough - thinner than one extrusion.
  The countersink ramps from the shaft hole out to full wall thickness at 45
  degrees instead, so there is no knife edge.
- The cone puts plastic in the clamp path, so **snug them, do not crank**. The
  nylock provides retention and the bolt shank carries shear through the steel
  tube either way.
- Screws are on the SIDES of the rails (`screwAngleList = [90, 270]`), so
  nothing protrudes into the netting that drapes over the top.
- **Seal the drilled holes.** Drilling cuts through the EMT's galvanizing and
  exposes bare steel at the hole edge, which is where rust starts. Dab cold
  galvanizing compound or zinc-rich primer in each hole before bolting.
- **Galvanic corrosion here is a non-issue** - do not spend money on it.
  Zinc and stainless sit close together on the electrochemical series;
  galvanized-to-stainless contact is not considered a serious risk outside
  marine environments, and trade practice (Unistrut with stainless bolts,
  galvanized truss plates with stainless screws) relies on exactly this pair.
  Plain rust at the drilled holes is the real corrosion risk, hence the note
  above. The countersink helps incidentally: head and nut bear on plastic, so
  metal-to-metal contact is just the shank at the hole.
- **Use anti-seize on the stainless threads.** Stainless galls against
  stainless, and hardware-store stainless is soft enough to strip easily.
  A dab of anti-seize on the threads costs nothing and saves a seized nut.
- Assembly: dry-fit, then drill 1/4" straight through both tube walls using
  the printed holes as the jig, then bolt. Nylock protrudes ~5 mm past its
  pocket on the far side - keep that side facing sideways/down.

## Netting attachment (from a comparable build)

A builder who enclosed a similar space with the same 3/4" EMT described the
method that worked, and it is not point anchors:

> fold the netting around the EMT conduit, then weave paracord through the
> mesh to secure the free end back to the main panel, making a pocket for the
> conduit

So the **primary attachment is a continuous paracord-laced pocket** wrapping
each rail, backed up with zip ties - the distributed approach commercial cat
netting kits also use (anchor every 12-18", add a mid-span tension line on
long spans). Netting was 3/4" stainless-reinforced cat netting.

That reframes the net anchor lug: it is **not** the main attachment, and the
tee count is flexible. The pocket cannot continue *through* a connector, so
the lug earns its place exactly where the wrap breaks - at corners, for
tying off a pocket run, for the border rope, and for guy lines. Build the
pockets first and add tees only where a run terminates.

The same build used 45-degree and adjustable-angle connectors to add bracing,
which is worth remembering given wind is the design load here.

### Choosing the mesh

Cat netting sells in three tiers, and the gap between them is large:

1. **Plain nylon monofilament** - garden/bird netting. Cheapest, and the
   category reinforced products define themselves against.
2. **HDPE** - marketed as roughly three times more durable than nylon.
3. **Steel-wire reinforced / bite resistant** - rated around 220 lb tensile.

Mesh size is the part where garden netting is already fine: commercial cat
netting runs about 3 cm, so 1 inch (2.5 cm) is if anything slightly finer.
The difference is strand strength, not aperture.

Monofilament is also the entanglement-prone form. Netting is sorted into
monofilament and multi-strand precisely because multi-strand is thick and
smooth enough that animals pull free, while monofilament catches claws and
limbs. Prefer multi-strand, and prefer reinforced edging - it spreads tension
so the pocket can be pulled tight without loading single fixings.

Supervision changes the risk materially: an attended enclosure turns a breach
from an escape into something noticed and fixed. Tier 1 netting is defensible
for a supervised shakedown; it is not what to leave up permanently.

## Assembly order and structure notes

1. Slide net-anchor tees onto the top rails BEFORE closing the frame - they
   cannot be added later (sockets are closed rings).
2. Bottom corners: post drops through the open corner bore onto the ground
   (or onto an endcap used as a foot). Corner flat bottom sits flush.
3. Top corners flipped: stopper side up, post seats against the shelf.
4. Keep rods in compression; shear stays perpendicular to printed layers in
   the as-printed orientation (author's structural guidance - see main README).
5. Wind is the design load: decide on cross-connector bracing after the frame
   is up (type 3 in the generator; no preset yet on purpose). The bottom
   corner lugs also take guy lines or a zip-tied skirt.

## Regenerating and testing

```
tools/build_stls.sh         # regenerate every print-ready STL into catio/stl/
tools/run_tests.sh          # renders all types + presets, checks manifoldness and bores
tools/measure_stl.py x.stl  # measure any bore, verify mesh is edge-manifold
```

`build_stls.sh` is the one to reach for after changing a preset or pulling new
upstream changes: it reads the preset names straight out of the JSON, exports
binary STLs, and refuses to call a part good if the render warned or the mesh
is not manifold. It prints each part's mass in PCTG so a preset that silently
changed shows up as a changed weight. To export a single part by hand:

```
openscad -o out.stl -p catio/catio-presets.json -P catio-corner-bottom "Rod Assisted Design Customizer.scad"
```

Note: OpenSCAD's render is not deterministic run to run, so compare volume,
area, and measured bores from `tools/measure_stl.py`, never raw STL bytes.
