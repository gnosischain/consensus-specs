from .constants import (
    ALL_PHASES,
    GNOSIS,
)
from .typing import (
    PresetBaseName,
    Spec,
    SpecForkName,
)

# NOTE: Gnosis only
ALL_EXECUTABLE_SPEC_NAMES = ALL_PHASES

# import the spec for each fork and preset
for fork in ALL_EXECUTABLE_SPEC_NAMES:
    exec(
        f"from eth_consensus_specs.{fork} import gnosis as spec_{fork}_gnosis"
    )

# this is the only output of this file
spec_targets: dict[PresetBaseName, dict[SpecForkName, Spec]] = {
    GNOSIS: {fork: eval(f"spec_{fork}_gnosis") for fork in ALL_EXECUTABLE_SPEC_NAMES},
}