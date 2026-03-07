#!/bin/bash
# Check that gnosis preset + config in this repo match the canonical source at gnosischain/specs

set -e

SPECS_BASE="https://raw.githubusercontent.com/gnosischain/specs/master/consensus"
TMPDIR=$(mktemp -d)
trap 'rm -rf "$TMPDIR"' EXIT
FAIL=0

# Strip commas between digits
normalize() {
    perl -pe 's/(?<=\d),(?=\d)//g'
}

# Compare two files after normalizing numeric formatting
check_sync() {
    local local_file="$1"
    local remote_file="$2"
    if ! diff -q <(normalize < "$local_file") <(normalize < "$remote_file") > /dev/null 2>&1; then
        echo "MISMATCH: $local_file differs from gnosischain/specs"
        diff <(normalize < "$local_file") <(normalize < "$remote_file") || true
        FAIL=1
    fi
}

# Preset files that exist in canonical specs
PRESET_FILES="phase0 altair bellatrix capella deneb electra fulu"

for f in $PRESET_FILES; do
    echo "Checking preset/$f.yaml..."
    curl -sf "$SPECS_BASE/preset/gnosis/$f.yaml" -o "$TMPDIR/$f.yaml"
    check_sync "presets/gnosis/$f.yaml" "$TMPDIR/$f.yaml"
done

echo "Checking config/gnosis.yaml..."
curl -sf "$SPECS_BASE/config/gnosis.yaml" -o "$TMPDIR/config.yaml"
check_sync "configs/gnosis.yaml" "$TMPDIR/config.yaml"

if [ $FAIL -ne 0 ]; then
    echo "Gnosis preset/config NOT in sync with gnosischain/specs"
    exit 1
else
    echo "Gnosis preset/config in sync."
fi
