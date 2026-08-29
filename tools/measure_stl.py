#!/usr/bin/env python3
"""Measure cylindrical bores and check mesh manifoldness of an STL export.

Pure-python (no dependencies). Used to regression-test the RAD OpenSCAD
generator: verifies socket/screw bore diameters land where the parameters
say they should, and that the exported mesh is edge-manifold (every edge
shared by exactly two triangles), catching OpenSCAD "not a valid 2-manifold"
geometry deterministically.

Usage:
  measure_stl.py FILE.stl                          # manifold check + bbox
  measure_stl.py FILE.stl --bore ox,oy,oz,dx,dy,dz,smin,smax,rexp,name ...

Each --bore probes a cylindrical surface: axis through origin (ox,oy,oz)
with direction (dx,dy,dz), using vertices whose axial coordinate s lies in
[smin,smax] and radial distance within +/-1.2mm of expected radius rexp.
Reports the fitted vertex-circle diameter and the effective across-flats
diameter for the polygonized circle (what a rod actually feels), assuming
the segment count given by --fn (default 50).
"""
import math
import struct
import sys


def load_stl(path):
    with open(path, "rb") as f:
        head = f.read(5)
        f.seek(0)
        if head == b"solid":
            # Could still be binary with a 'solid' header; sniff for ASCII keyword.
            blob = f.read()
            if b"facet normal" in blob[:2000]:
                return load_ascii(blob)
        data = f.read()
    return load_binary(data)


def load_binary(data):
    (n,) = struct.unpack_from("<I", data, 80)
    tris = []
    off = 84
    for _ in range(n):
        vals = struct.unpack_from("<12f", data, off)
        tris.append((vals[3:6], vals[6:9], vals[9:12]))
        off += 50
    return tris


def load_ascii(blob):
    tris = []
    cur = []
    for line in blob.decode("ascii", "replace").splitlines():
        line = line.strip()
        if line.startswith("vertex"):
            _, x, y, z = line.split()
            cur.append((float(x), float(y), float(z)))
            if len(cur) == 3:
                tris.append(tuple(cur))
                cur = []
    return tris


def key(v, q=1e-4):
    return (round(v[0] / q), round(v[1] / q), round(v[2] / q))


def manifold_report(tris):
    edges = {}
    for a, b, c in tris:
        ka, kb, kc = key(a), key(b), key(c)
        for e in ((ka, kb), (kb, kc), (kc, ka)):
            e = (min(e), max(e))
            edges[e] = edges.get(e, 0) + 1
        if ka == kb or kb == kc or ka == kc:
            print("  DEGENERATE triangle at", a)
    bad = {e: n for e, n in edges.items() if n != 2}
    return len(edges), bad


def norm(v):
    m = math.sqrt(sum(x * x for x in v))
    return tuple(x / m for x in v)


def bore(tris, origin, axis, smin, smax, rexp, name, fn):
    axis = norm(axis)
    seen = set()
    radii = []
    for tri in tris:
        for v in tri:
            k = key(v)
            if k in seen:
                continue
            seen.add(k)
            rel = (v[0] - origin[0], v[1] - origin[1], v[2] - origin[2])
            s = sum(r * a for r, a in zip(rel, axis))
            if not (smin <= s <= smax):
                continue
            rad2 = sum(r * r for r in rel) - s * s
            rad = math.sqrt(max(rad2, 0.0))
            if abs(rad - rexp) <= 1.2:
                radii.append(rad)
    if not radii:
        print(f"  {name}: NO VERTICES FOUND (expected r={rexp})")
        return
    radii.sort()
    dmin, dmax = 2 * radii[0], 2 * radii[-1]
    counts = {}
    for r in radii:
        counts[round(r, 3)] = counts.get(round(r, 3), 0) + 1
    rmode = max(counts, key=counts.get)
    dmode = 2 * rmode
    flats = dmode * math.cos(math.pi / fn)
    print(
        f"  {name}: vertex dia {dmode:.3f} (mode, {counts[rmode]}/{len(radii)} verts; "
        f"range {dmin:.3f}..{dmax:.3f}), across-flats {flats:.3f}"
    )


def main():
    args = sys.argv[1:]
    path = args.pop(0)
    fn = 50
    probes = []
    while args:
        a = args.pop(0)
        if a == "--fn":
            fn = int(args.pop(0))
        elif a == "--bore":
            parts = args.pop(0).split(",")
            probes.append(
                (
                    tuple(float(x) for x in parts[0:3]),
                    tuple(float(x) for x in parts[3:6]),
                    float(parts[6]),
                    float(parts[7]),
                    float(parts[8]),
                    parts[9],
                )
            )
        else:
            raise SystemExit(f"unknown arg {a}")
    tris = load_stl(path)
    xs = [v[i] for t in tris for v in t for i in (0,)]
    ys = [v[1] for t in tris for v in t]
    zs = [v[2] for t in tris for v in t]
    vol = 0.0
    area = 0.0
    for a, b, c in tris:
        cx = (
            (b[1] - a[1]) * (c[2] - a[2]) - (b[2] - a[2]) * (c[1] - a[1]),
            (b[2] - a[2]) * (c[0] - a[0]) - (b[0] - a[0]) * (c[2] - a[2]),
            (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0]),
        )
        area += 0.5 * math.sqrt(sum(x * x for x in cx))
        vol += (
            a[0] * (b[1] * c[2] - b[2] * c[1])
            - a[1] * (b[0] * c[2] - b[2] * c[0])
            + a[2] * (b[0] * c[1] - b[1] * c[0])
        ) / 6.0
    print(f"{path}")
    print(f"  triangles: {len(tris)}")
    print(f"  volume: {vol:.3f} mm^3   area: {area:.3f} mm^2")
    print(
        f"  bbox: x [{min(xs):.2f},{max(xs):.2f}] y [{min(ys):.2f},{max(ys):.2f}] "
        f"z [{min(zs):.2f},{max(zs):.2f}]"
    )
    nedges, bad = manifold_report(tris)
    if bad:
        worst = list(bad.items())[:8]
        print(f"  NON-MANIFOLD: {len(bad)}/{nedges} bad edges, e.g. {worst}")
    else:
        print(f"  manifold: OK ({nedges} edges, all shared exactly twice)")
    for origin, axis, smin, smax, rexp, name in probes:
        bore(tris, origin, axis, smin, smax, rexp, name, fn)
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
