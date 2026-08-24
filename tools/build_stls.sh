#!/usr/bin/env bash
# Regenerate print-ready STLs for every preset in catio/catio-presets.json.
#
# Preset names are read from the JSON, so adding or renaming a preset needs no
# change here. Exports are binary STL (compact, what slicers want) and each one
# is checked for render warnings and for mesh manifoldness before being counted
# as good.
#
# Usage: tools/build_stls.sh [output_dir]     (default: catio/stl, gitignored)
#
# Caveat worth knowing: OpenSCAD does NOT validate values in a parameter file.
# A nonsense value (a string where a number belongs, say) is accepted silently
# and renders altered geometry with no warning, so these checks catch broken
# RENDERS, not broken PARAMETERS. Eyeball the reported gram weights - a preset
# that suddenly changes mass is the tell.

set -uo pipefail
cd "$(dirname "$0")/.."

SCAD="Rod Assisted Design Customizer.scad"
PRESETS="catio/catio-presets.json"
OUT="${1:-catio/stl}"
mkdir -p "$OUT"

names=$(python3 -c "
import json
print(' '.join(json.load(open('$PRESETS'))['parameterSets']))
") || { echo "cannot read $PRESETS"; exit 1; }

fail=0
for p in $names; do
    log=$(mktemp)
    if ! openscad -o "$OUT/$p.stl" --export-format binstl \
                  -p "$PRESETS" -P "$p" "$SCAD" 2>"$log"; then
        echo "FAIL  $p: openscad exited nonzero"; sed -n '1,5p' "$log"; fail=1
        rm -f "$log"; continue
    fi
    if grep -qiE 'warning|error' "$log"; then
        echo "FAIL  $p: render warnings"; grep -iE 'warning|error' "$log" | head -3; fail=1
    fi
    rm -f "$log"

    if info=$(python3 tools/measure_stl.py "$OUT/$p.stl"); then
        vol=$(echo "$info" | sed -n 's/.*volume: \([0-9.]*\).*/\1/p')
        grams=$(python3 -c "print(f'{$vol/1000*1.23:.0f}')")   # PCTG ~1.23 g/cm3
        printf 'ok    %-22s %6s kB  ~%s g PCTG\n' \
               "$p" "$(( $(stat -c%s "$OUT/$p.stl") / 1000 ))" "$grams"
    else
        echo "FAIL  $p: mesh is not manifold"; fail=1
    fi
done

echo
if [ "$fail" -eq 0 ]; then
    echo "All presets exported to $OUT/"
else
    echo "One or more presets failed."; exit 1
fi
