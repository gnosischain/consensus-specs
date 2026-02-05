from typing import (
    Dict,
)
from .constants import (
    GNOSIS,
    ALL_PHASES,
)
from .typing import (
    PresetBaseName,
    SpecForkName,
    Spec,
)


# NOTE: gnosis only
ALL_EXECUTABLE_SPEC_NAMES = ALL_PHASES

# import the spec for each fork and preset
for fork in ALL_EXECUTABLE_SPEC_NAMES:
    exec(f"from eth2spec.{fork} import gnosis as spec_{fork}_gnosis")

# this is the only output of this file
spec_targets: Dict[PresetBaseName, Dict[SpecForkName, Spec]] = {
    GNOSIS: {fork: eval(f"spec_{fork}_gnosis") for fork in ALL_EXECUTABLE_SPEC_NAMES},
}
