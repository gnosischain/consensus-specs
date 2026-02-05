#!/bin/bash
# Check that gnosis preset + config in this repo match the canonical source at gnosischain/specs

set -e

SPECS_BASE="https://raw.githubusercontent.com/gnosischain/specs/master/consensus"
TMPDIR=$(mktemp -d)
FAIL=0

# Preset files that exist in canonical specs
PRESET_FILES="phase0 altair bellatrix capella deneb electra fulu"

for f in $PRESET_FILES; do
    echo "Checking preset/$f.yaml..."
    curl -sf "$SPECS_BASE/preset/gnosis/$f.yaml" -o "$TMPDIR/$f.yaml"
    if ! diff -q "presets/gnosis/$f.yaml" "$TMPDIR/$f.yaml" > /dev/null 2>&1; then
        echo "MISMATCH: presets/gnosis/$f.yaml differs from gnosischain/specs"
        diff "presets/gnosis/$f.yaml" "$TMPDIR/$f.yaml" || true
        FAIL=1
    fi
done

echo "Checking config/gnosis.yaml..."
curl -sf "$SPECS_BASE/config/gnosis.yaml" -o "$TMPDIR/config.yaml"
if ! diff -q "configs/gnosis.yaml" "$TMPDIR/config.yaml" > /dev/null 2>&1; then
    echo "MISMATCH: configs/gnosis.yaml differs from gnosischain/specs"
    diff "configs/gnosis.yaml" "$TMPDIR/config.yaml" || true
    FAIL=1
fi

rm -rf "$TMPDIR"

if [ $FAIL -ne 0 ]; then
    echo "Gnosis preset/config NOT in sync with gnosischain/specs"
    exit 1
else
    echo "Gnosis preset/config in sync."
fi
