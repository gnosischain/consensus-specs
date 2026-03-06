from .typing import PresetBaseName, SpecForkName

#
# SpecForkName
#

# Some of the Spec module functionality is exposed here to deal with phase-specific changes.
PHASE0 = SpecForkName("phase0")
ALTAIR = SpecForkName("altair")
BELLATRIX = SpecForkName("bellatrix")
CAPELLA = SpecForkName("capella")
DENEB = SpecForkName("deneb")
ELECTRA = SpecForkName("electra")
FULU = SpecForkName("fulu")

#
# SpecFork settings
#

# The forks that are deployed on Gnosis
GNOSIS_FORKS = (PHASE0, ALTAIR, BELLATRIX, CAPELLA, DENEB, ELECTRA)
LATEST_FORK = GNOSIS_FORKS[-1]
# The forks that pytest can run with.
ALL_PHASES = (
    # Formal forks
    *GNOSIS_FORKS,
    FULU,
)
# The forks that have light client specs
LIGHT_CLIENT_TESTING_FORKS = [item for item in GNOSIS_FORKS if item != PHASE0] + [FULU]
# The forks that output to the test vectors.
TESTGEN_FORKS = (*GNOSIS_FORKS, FULU)
# Forks allowed in the test runner `--fork` flag, to fail fast in case of typos
ALLOWED_TEST_RUNNER_FORKS = ALL_PHASES

# NOTE: the same definition as in `pysetup/md_doc_paths.py`
PREVIOUS_FORK_OF = {
    # post_fork_name: pre_fork_name
    PHASE0: None,
    ALTAIR: PHASE0,
    BELLATRIX: ALTAIR,
    CAPELLA: BELLATRIX,
    DENEB: CAPELLA,
    ELECTRA: DENEB,
    FULU: ELECTRA,
}

# For fork transition tests
POST_FORK_OF = {
    # pre_fork_name: post_fork_name
    PHASE0: ALTAIR,
    ALTAIR: BELLATRIX,
    BELLATRIX: CAPELLA,
    CAPELLA: DENEB,
    DENEB: ELECTRA,
    ELECTRA: FULU,
    FULU: GLOAS,
    GLOAS: HEZE,
}

ALL_PRE_POST_FORKS = POST_FORK_OF.items()
DENEB_TRANSITION_UPGRADES_AND_AFTER = {
    key: value for key, value in POST_FORK_OF.items() if key not in [PHASE0, ALTAIR, BELLATRIX]
}
ELECTRA_TRANSITION_UPGRADES_AND_AFTER = {
    key: value
    for key, value in POST_FORK_OF.items()
    if key not in [PHASE0, ALTAIR, BELLATRIX, CAPELLA]
}
AFTER_DENEB_PRE_POST_FORKS = DENEB_TRANSITION_UPGRADES_AND_AFTER.items()
AFTER_ELECTRA_PRE_POST_FORKS = ELECTRA_TRANSITION_UPGRADES_AND_AFTER.items()

#
# Config and Preset
#
GNOSIS = PresetBaseName("gnosis")

# Only gnosis is available
ALL_PRESETS = (GNOSIS)


#
# Number
#
UINT64_MAX = 2**64 - 1
