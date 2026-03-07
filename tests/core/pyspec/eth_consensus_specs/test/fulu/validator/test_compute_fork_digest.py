from eth_consensus_specs.test.context import (
    single_phase,
    spec_test,
    with_config_overrides,
    with_fulu_and_later,
)


@with_fulu_and_later
@spec_test
@single_phase
@with_config_overrides(
    {
        "BLOB_SCHEDULE": [
            {"EPOCH": 9, "MAX_BLOBS_PER_BLOCK": 9},
            {"EPOCH": 100, "MAX_BLOBS_PER_BLOCK": 100},
            {"EPOCH": 150, "MAX_BLOBS_PER_BLOCK": 175},
            {"EPOCH": 200, "MAX_BLOBS_PER_BLOCK": 200},
            {"EPOCH": 250, "MAX_BLOBS_PER_BLOCK": 275},
            {"EPOCH": 300, "MAX_BLOBS_PER_BLOCK": 300},
        ],
    },
)
def test_compute_fork_digest(spec):
    test_cases = [
        # Different epochs and blob limits:
        {
            "epoch": 9,
            "fork_version": "0x06000064",
            "genesis_validators_root": b"\x00" * 32,
            "expected_fork_digest": "0xc98245cc",
        },
        {
            "epoch": 10,
            "fork_version": "0x06000064",
            "genesis_validators_root": b"\x00" * 32,
            "expected_fork_digest": "0xc98245cc",
        },
        {
            "epoch": 11,
            "fork_version": "0x06000064",
            "genesis_validators_root": b"\x00" * 32,
            "expected_fork_digest": "0xc98245cc",
        },
        {
            "epoch": 99,
            "fork_version": "0x06000064",
            "genesis_validators_root": b"\x00" * 32,
            "expected_fork_digest": "0xc98245cc",
        },
        {
            "epoch": 100,
            "fork_version": "0x06000064",
            "genesis_validators_root": b"\x00" * 32,
            "expected_fork_digest": "0xbddff67f",
        },
        {
            "epoch": 101,
            "fork_version": "0x06000064",
            "genesis_validators_root": b"\x00" * 32,
            "expected_fork_digest": "0xbddff67f",
        },
        {
            "epoch": 150,
            "fork_version": "0x06000064",
            "genesis_validators_root": b"\x00" * 32,
            "expected_fork_digest": "0xe80b285d",
        },
        {
            "epoch": 199,
            "fork_version": "0x06000064",
            "genesis_validators_root": b"\x00" * 32,
            "expected_fork_digest": "0xe80b285d",
        },
        {
            "epoch": 200,
            "fork_version": "0x06000064",
            "genesis_validators_root": b"\x00" * 32,
            "expected_fork_digest": "0xbb00b73c",
        },
        {
            "epoch": 201,
            "fork_version": "0x06000064",
            "genesis_validators_root": b"\x00" * 32,
            "expected_fork_digest": "0xbb00b73c",
        },
        {
            "epoch": 250,
            "fork_version": "0x06000064",
            "genesis_validators_root": b"\x00" * 32,
            "expected_fork_digest": "0x2c4b8966",
        },
        {
            "epoch": 299,
            "fork_version": "0x06000064",
            "genesis_validators_root": b"\x00" * 32,
            "expected_fork_digest": "0x2c4b8966",
        },
        {
            "epoch": 300,
            "fork_version": "0x06000064",
            "genesis_validators_root": b"\x00" * 32,
            "expected_fork_digest": "0xa8a8ae60",
        },
        {
            "epoch": 301,
            "fork_version": "0x06000064",
            "genesis_validators_root": b"\x00" * 32,
            "expected_fork_digest": "0xa8a8ae60",
        },
        # Different genesis validators roots:
        {
            "epoch": 9,
            "fork_version": "0x06000064",
            "genesis_validators_root": b"\x01" * 32,
            "expected_fork_digest": "0x940fb013",
        },
        {
            "epoch": 9,
            "fork_version": "0x06000064",
            "genesis_validators_root": b"\x02" * 32,
            "expected_fork_digest": "0x20c7d3c0",
        },
        {
            "epoch": 9,
            "fork_version": "0x06000064",
            "genesis_validators_root": b"\x03" * 32,
            "expected_fork_digest": "0x4461c7fe",
        },
        {
            "epoch": 100,
            "fork_version": "0x06000064",
            "genesis_validators_root": b"\x01" * 32,
            "expected_fork_digest": "0xe05203a0",
        },
        {
            "epoch": 100,
            "fork_version": "0x06000064",
            "genesis_validators_root": b"\x02" * 32,
            "expected_fork_digest": "0x549a6073",
        },
        {
            "epoch": 100,
            "fork_version": "0x06000064",
            "genesis_validators_root": b"\x03" * 32,
            "expected_fork_digest": "0x303c744d",
        },
        # Different fork versions
        {
            "epoch": 9,
            "fork_version": "0x06000065",
            "genesis_validators_root": b"\x00" * 32,
            "expected_fork_digest": "0x8cf67aaa",
        },
        {
            "epoch": 9,
            "fork_version": "0x07000064",
            "genesis_validators_root": b"\x00" * 32,
            "expected_fork_digest": "0x0070fb81",
        },
        {
            "epoch": 9,
            "fork_version": "0x07000065",
            "genesis_validators_root": b"\x00" * 32,
            "expected_fork_digest": "0x2aee3c0a",
        },
        {
            "epoch": 100,
            "fork_version": "0x06000065",
            "genesis_validators_root": b"\x00" * 32,
            "expected_fork_digest": "0xf8abc919",
        },
        {
            "epoch": 100,
            "fork_version": "0x07000064",
            "genesis_validators_root": b"\x00" * 32,
            "expected_fork_digest": "0x742d4832",
        },
        {
            "epoch": 100,
            "fork_version": "0x07000065",
            "genesis_validators_root": b"\x00" * 32,
            "expected_fork_digest": "0x5eb38fb9",
        },
    ]

    for case in test_cases:
        # Override function to return fork version in test case
        spec.compute_fork_version = lambda _: case["fork_version"]
        # Compute the fork digest given the inputs from the test case
        fork_digest = spec.compute_fork_digest(case["genesis_validators_root"], case["epoch"])
        # Check that the computed fork digest matches our expected value
        assert f"0x{fork_digest.hex()}" == case["expected_fork_digest"]
