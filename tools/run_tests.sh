#!/usr/bin/env bash
# Regression tests for "Rod Assisted Design Customizer.scad".
#
# Renders every part type at stock defaults plus every catio preset, and fails if:
#   - OpenSCAD reports any 2-manifold warning or unknown-variable warning,
#   - any exported mesh is not edge-manifold (checked independently in python),
#   - any expected bore diameter drifts from its parameter value.
#
# Note: OpenSCAD's CGAL tessellation is not deterministic run to run, so byte
# comparison of STLs is NOT a valid test. Compare volume/area/bbox from
# measure_stl.py instead when checking that a refactor didn't change geometry.
#
# Usage: tools/run_tests.sh [output_dir]   (default: ./test-output)

set -u
cd "$(dirname "$0")/.."
SCAD="Rod Assisted Design Customizer.scad"
OUT="${1:-test-output}"
mkdir -p "$OUT"
fail=0

check_log() {
    if grep -q "2-manifold" "$1"; then echo "  FAIL: manifold warning in $2"; fail=1; fi
    if grep -q "unknown variable" "$1"; then echo "  FAIL: unknown variable in $2"; fail=1; fi
}

echo "== Part types at stock defaults =="
for t in 1 2 3 4; do
    openscad -o "$OUT/default_type$t.stl" -D "type=$t" "$SCAD" 2> "$OUT/default_type$t.log"
    check_log "$OUT/default_type$t.log" "type $t"
    python3 tools/measure_stl.py "$OUT/default_type$t.stl" > "$OUT/default_type$t.txt" \
        || { echo "  FAIL: non-manifold mesh, type $t"; fail=1; }
    echo "  type $t: $(grep -E 'volume|manifold' "$OUT/default_type$t.txt" | tr -s ' ' | tr '\n' ' ')"
done

echo "== Net anchor smoke test (default position, default part) =="
openscad -o "$OUT/anchor_default.stl" -D "netAnchorEnable=1" "$SCAD" 2> "$OUT/anchor_default.log"
check_log "$OUT/anchor_default.log" "anchor default"
python3 tools/measure_stl.py "$OUT/anchor_default.stl" \
    --bore "0,-26,-6,1,0,0,-4,4,4,anchorHole" > "$OUT/anchor_default.txt" \
    || { echo "  FAIL: non-manifold mesh with net anchor"; fail=1; }
grep -q "anchorHole: vertex dia 8.000" "$OUT/anchor_default.txt" \
    || { echo "  FAIL: anchor hole diameter drifted"; fail=1; }
echo "  $(grep anchorHole "$OUT/anchor_default.txt")"

echo "== Catio presets =="
for p in catio-corner-bottom catio-corner-top catio-tee-netanchor catio-tee-branch catio-endcap; do
    openscad -o "$OUT/$p.stl" -p catio/catio-presets.json -P "$p" "$SCAD" 2> "$OUT/$p.log"
    check_log "$OUT/$p.log" "$p"
    python3 tools/measure_stl.py "$OUT/$p.stl" > "$OUT/$p.txt" \
        || { echo "  FAIL: non-manifold mesh, $p"; fail=1; }
    echo "  $p: $(grep -E 'volume|manifold' "$OUT/$p.txt" | tr -s ' ' | tr '\n' ' ')"
done

# Socket bore spot checks: dowelDia is 23.9 in every catio preset, so the mouth
# ring of each socket must measure exactly 23.900 as a vertex circle.
python3 tools/measure_stl.py "$OUT/catio-corner-bottom.stl" \
    --bore "0,0,0,0,0,1,58,66,11.95,centerBore" \
    --bore "0,0,0,0.70711,0.70711,0,58,66,11.95,legBore" > "$OUT/bores.txt"
grep -c "vertex dia 23.900" "$OUT/bores.txt" | grep -q "^2$" \
    || { echo "  FAIL: corner socket bore drifted from 23.900"; fail=1; }
echo "  corner bores: $(grep -c 'vertex dia 23.900' "$OUT/bores.txt")/2 at 23.900"

if [ "$fail" -eq 0 ]; then echo "ALL TESTS PASSED"; else echo "TESTS FAILED"; exit 1; fi
