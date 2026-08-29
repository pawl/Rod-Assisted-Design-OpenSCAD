#!/usr/bin/env python3
"""Render every row of a parts CSV to an STL, and report rod cut lengths.

The CSV is the part list: one row per part, one column per Customizer
parameter, so it can be kept in a spreadsheet and exported as CSV. Only the
columns you fill in are passed to OpenSCAD, so a blank cell means "use the
default in the .scad".

Two columns are metadata rather than parameters:
    name   output filename (required)
    qty    how many to print (carried into the summary, not passed to OpenSCAD)

Values containing commas, such as a screw angle list, just need normal CSV
quoting - "[0, 180]" - which is what a spreadsheet writes anyway.

Usage:
    tools/build_parts.py [parts.csv] [output_dir]      default examples/parts.csv, ./stl
    tools/build_parts.py --span 600 [parts.csv]        also print cut lengths for a
                                                       600mm centre-to-centre span
"""
import csv
import math
import os
import subprocess
import sys

SCAD = "Rod Assisted Design Customizer.scad"
META = {"name", "qty", "notes"}


def num(row, key, default=0.0):
    v = row.get(key, "")
    try:
        return float(v)
    except (TypeError, ValueError):
        return default


def rod_geometry(row):
    """How much rod a connector swallows, derived from the same formulas the
    .scad uses. Returns (rod_end_from_centre, socket_depth) in mm, or None
    when the part does not hold a rod end this way.

    A rod bottoms out on the internal stopper, whose face sits
    stopperLeg + thickness from the connector centre, so for a rail spanning
    two connectors L apart centre-to-centre:

        cut length = L - 2 * rod_end_from_centre
    """
    if row.get("type", "1").strip() not in ("", "1"):
        return None
    dowel = num(row, "dowelDia", 26)
    th = num(row, "thickness", 6)
    legdia = dowel + th * 2
    leglen = max(num(row, "lengthLeg", 50), legdia)
    stopper_en = num(row, "stopperEnable", 1)
    if stopper_en <= 0:
        return None                      # rod passes straight through
    rod_end = legdia / 2 + th            # stopperLeg + thickness
    depth = (leglen + legdia / 2) - rod_end
    return rod_end, depth


def main():
    args = sys.argv[1:]
    span = None
    if "--span" in args:
        i = args.index("--span")
        span = float(args[i + 1])
        del args[i:i + 2]
    csv_path = args[0] if args else "examples/parts.csv"
    out = args[1] if len(args) > 1 else "stl"

    os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
    if not os.path.exists(SCAD):
        sys.exit(f"cannot find {SCAD}")
    os.makedirs(out, exist_ok=True)
    sys.path.insert(0, "tools")
    from measure_stl import load_stl, key

    fail = False
    for row in csv.DictReader(open(csv_path)):
        name = (row.get("name") or "").strip()
        if not name or name.startswith("#"):
            continue
        defs = []
        for k, v in row.items():
            if k in META or v is None or not str(v).strip():
                continue
            defs += ["-D", f"{k}={str(v).strip()}"]
        stl = os.path.join(out, f"{name}.stl")
        p = subprocess.run(["openscad", "-o", stl, "--export-format", "binstl",
                            *defs, SCAD], capture_output=True, text=True)
        log = p.stderr
        if p.returncode != 0 or "ERROR" in log.upper():
            print(f"FAIL  {name}: render error")
            print("      " + "\n      ".join(log.strip().splitlines()[:3]))
            fail = True
            continue
        warns = sum(1 for l in log.splitlines() if "WARNING" in l.upper())

        tris = load_stl(stl)
        edges = {}
        vol = 0.0
        for a, b, c in tris:
            for e in ((key(a), key(b)), (key(b), key(c)), (key(c), key(a))):
                e = (min(e), max(e))
                edges[e] = edges.get(e, 0) + 1
            vol += (a[0] * (b[1] * c[2] - b[2] * c[1])
                    - a[1] * (b[0] * c[2] - b[2] * c[0])
                    + a[2] * (b[0] * c[1] - b[1] * c[0])) / 6.0
        bad = sum(1 for n in edges.values() if n != 2)
        if bad:
            print(f"FAIL  {name}: mesh not edge-manifold ({bad} bad edges)")
            fail = True
            continue

        qty = (row.get("qty") or "1").strip() or "1"
        note = f"   ({warns} render warning(s))" if warns else ""
        print(f"ok    {name:<20} qty {qty:>3}   {vol/1000:8.2f} cm^3{note}")

        g = rod_geometry(row)
        if g:
            rod_end, depth = g
            line = (f"        rod seats {rod_end:.2f} mm from centre, "
                    f"{depth:.1f} mm of it inside the socket")
            if span is not None:
                line += f"\n        cut for {span:g} mm span: {span - 2*rod_end:.2f} mm"
            print(line)

    print()
    print("All parts written to " + out + "/" if not fail else "One or more parts failed.")
    sys.exit(1 if fail else 0)


def selftest():
    """Check the cut-length formula against numbers measured from a real mesh.

    A shelf-corner at dowelDia 26 / thickness 6 / stopperEnable 1 was measured
    with tools/measure_stl.py: its bore wall runs 25.00..69.00 mm from the
    connector centre, so the rod seats at 25.00 with 44.0 mm of socket depth.
    """
    row = {"type": "1", "dowelDia": "26", "thickness": "6",
           "lengthLeg": "50", "stopperEnable": "1"}
    rod_end, depth = rod_geometry(row)
    assert abs(rod_end - 25.0) < 1e-9, rod_end
    assert abs(depth - 44.0) < 1e-9, depth
    # a through socket holds no rod end
    assert rod_geometry(dict(row, stopperEnable="0")) is None
    # non-connector types are not rail sockets
    assert rod_geometry(dict(row, type="4")) is None
    print("selftest ok: rod seats 25.00 mm, socket depth 44.0 mm, matches mesh")


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        selftest()
    else:
        main()
