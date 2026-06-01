# L1HEADERS -- The Beacon Chain

## Table of contents

<!-- TOC -->
<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->

- [Introduction](#introduction)
- [Preset](#preset)
- [Configuration](#configuration)
- [Custom types](#custom-types)
- [Containers](#containers)
  - [New containers](#new-containers)
    - [`PendingJustifiedCheckpoint`](#pendingjustifiedcheckpoint)
  - [Modified containers](#modified-containers)
    - [`BeaconBlockBody`](#beaconblockbody)
    - [`BeaconState`](#beaconstate)
- [Helper functions](#helper-functions)
  - [Misc](#misc)
    - [`compute_upstream_timestamp_at_slot`](#compute_upstream_timestamp_at_slot)
    - [`compute_upstream_start_slot_at_epoch`](#compute_upstream_start_slot_at_epoch)
- [Beacon chain state transition function](#beacon-chain-state-transition-function)
  - [Block processing](#block-processing)
    - [New `process_upstream_chain`](#new-process_upstream_chain)
  - [Epoch processing](#epoch-processing)
    - [Modified `weigh_justification_and_finalization`](#modified-weigh_justification_and_finalization)
    - [New `promote_pending_finality`](#new-promote_pending_finality)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->
<!-- /TOC -->

## Introduction

This is the beacon chain specification to make fork-choice conditional on an upstream chain.

*Note*: This specification is built upon [Electra](../../electra/beacon_chain.md) and is under active development.

## Preset

| Name | Value | Description |
| - | - | - |
| `PENDING_FINALITY_LIMIT` | `uint64(2**10)` (=1024) | Max pending checkpoints before oldest are dropped |
| `MAX_UPSTREAM_INTERMEDIATE_HEADERS` | `uint64(2**22)` (=4,194,304) | Max upstream intermediate headers |
| `UPSTREAM_FINALIZED_CHECKPOINT_GINDEX` | `GeneralizedIndex(84)` | `get_generalized_index(UpstreamBeaconState, 'finalized_checkpoint')` |

*Note*: The generalized index is based on the upstream (Ethereum mainnet) `BeaconState` layout at the Electra fork. It must be updated if the upstream state structure changes.

## Configuration

| Name | Value | Unit |
| - | - | - |
| `UPSTREAM_GENESIS_SLOT`     | `0` | slots
| `UPSTREAM_GENESIS_TIME`     | `1606824023` | seconds
| `UPSTREAM_SECONDS_PER_SLOT` | `uint64(12)` | seconds
| `UPSTREAM_SLOTS_PER_EPOCH`  | `uint64(32)` | slots

## Custom types

| Name | SSZ equivalent | Description |
| - | - | - |
| `UpstreamFinalityBranch` | `Vector[Bytes32, floorlog2(UPSTREAM_FINALIZED_CHECKPOINT_GINDEX)]` | Merkle branch of `finalized_checkpoint` within the upstream `BeaconState` |

## Containers

### New containers

#### `PendingJustifiedCheckpoint`

```python
class PendingJustifiedCheckpoint(Container):
    source_epoch: Epoch
    checkpoint: Checkpoint
```

### Modified containers

#### `BeaconBlockBody`

```python
class BeaconBlockBody(Container):
    randao_reveal: BLSSignature
    eth1_data: Eth1Data  # Eth1 data vote
    graffiti: Bytes32  # Arbitrary data
    # Operations
    proposer_slashings: List[ProposerSlashing, MAX_PROPOSER_SLASHINGS]
    attester_slashings: List[AttesterSlashing, MAX_ATTESTER_SLASHINGS_ELECTRA]
    attestations: List[Attestation, MAX_ATTESTATIONS_ELECTRA]
    deposits: List[Deposit, MAX_DEPOSITS]
    voluntary_exits: List[SignedVoluntaryExit, MAX_VOLUNTARY_EXITS]
    sync_aggregate: SyncAggregate
    # Execution
    execution_payload: ExecutionPayload
    bls_to_execution_changes: List[SignedBLSToExecutionChange, MAX_BLS_TO_EXECUTION_CHANGES]
    blob_kzg_commitments: List[KZGCommitment, MAX_BLOB_COMMITMENTS_PER_BLOCK]
    execution_requests: ExecutionRequests
    # [New in L1HEADERS]
    upstream_head: BeaconBlockHeader
    upstream_intermediate_headers: List[BeaconBlockHeader, MAX_UPSTREAM_INTERMEDIATE_HEADERS]
    upstream_finalized_checkpoint: Checkpoint
    upstream_finalized_checkpoint_branch: UpstreamFinalityBranch
```

*Note*: `upstream_head_root` is available to the EVM through EIP-4788 (Beacon block root in the EVM) with a merkle proof from the beacon block root.

#### `BeaconState`

```python
class BeaconState(Container):
    # Versioning
    genesis_time: uint64
    genesis_validators_root: Root
    slot: Slot
    fork: Fork
    # History
    latest_block_header: BeaconBlockHeader
    block_roots: Vector[Root, SLOTS_PER_HISTORICAL_ROOT]
    state_roots: Vector[Root, SLOTS_PER_HISTORICAL_ROOT]
    historical_roots: List[Root, HISTORICAL_ROOTS_LIMIT]
    # Eth1
    eth1_data: Eth1Data
    eth1_data_votes: List[Eth1Data, EPOCHS_PER_ETH1_VOTING_PERIOD * SLOTS_PER_EPOCH]
    eth1_deposit_index: uint64
    # Registry
    validators: List[Validator, VALIDATOR_REGISTRY_LIMIT]
    balances: List[Gwei, VALIDATOR_REGISTRY_LIMIT]
    # Randomness
    randao_mixes: Vector[Bytes32, EPOCHS_PER_HISTORICAL_VECTOR]
    # Slashings
    slashings: Vector[Gwei, EPOCHS_PER_SLASHINGS_VECTOR]
    # Participation
    previous_epoch_participation: List[ParticipationFlags, VALIDATOR_REGISTRY_LIMIT]
    current_epoch_participation: List[ParticipationFlags, VALIDATOR_REGISTRY_LIMIT]
    # Finality
    # [Deprecated in L1HEADERS] No longer used; kept for SSZ compatibility
    justification_bits: Bitvector[JUSTIFICATION_BITS_LENGTH]
    previous_justified_checkpoint: Checkpoint
    current_justified_checkpoint: Checkpoint
    finalized_checkpoint: Checkpoint
    # Inactivity
    inactivity_scores: List[uint64, VALIDATOR_REGISTRY_LIMIT]
    # Sync
    current_sync_committee: SyncCommittee
    next_sync_committee: SyncCommittee
    # Execution
    latest_execution_payload_header: ExecutionPayloadHeader
    # Withdrawals
    next_withdrawal_index: WithdrawalIndex
    next_withdrawal_validator_index: ValidatorIndex
    # Deep history valid from Capella onwards
    historical_summaries: List[HistoricalSummary, HISTORICAL_ROOTS_LIMIT]
    deposit_requests_start_index: uint64
    deposit_balance_to_consume: Gwei
    exit_balance_to_consume: Gwei
    earliest_exit_epoch: Epoch
    consolidation_balance_to_consume: Gwei
    earliest_consolidation_epoch: Epoch
    pending_deposits: List[PendingDeposit, PENDING_DEPOSITS_LIMIT]
    pending_partial_withdrawals: List[PendingPartialWithdrawal, PENDING_PARTIAL_WITHDRAWALS_LIMIT]
    pending_consolidations: List[PendingConsolidation, PENDING_CONSOLIDATIONS_LIMIT]
    # [New in L1HEADERS]
    # Running justification tracker — tracks the highest justified
    # epoch independently of the promoted checkpoints.
    pending_current_justified_checkpoint: Checkpoint
    # Justified epochs waiting for upstream finality before promotion.
    # Each entry records the source (promoted justified epoch at the
    # time attesters voted) so promote_pending_finality can verify
    # supermajority links. We gate on upstream finality (not
    # justification) because upstream justification is reversible.
    pending_justified_checkpoints: List[
        PendingJustifiedCheckpoint, PENDING_FINALITY_LIMIT
    ]
    latest_upstream_head: BeaconBlockHeader
    latest_upstream_finalized_checkpoint: Checkpoint
```

## Helper functions

### Misc

#### New `compute_upstream_timestamp_at_slot`

```python
def compute_upstream_timestamp_at_slot(slot: Slot) -> uint64:
    slots_since_genesis = slot - UPSTREAM_GENESIS_SLOT
    return uint64(UPSTREAM_GENESIS_TIME + slots_since_genesis * UPSTREAM_SECONDS_PER_SLOT)
```


#### New `compute_upstream_start_slot_at_epoch`

```python
def compute_upstream_start_slot_at_epoch(epoch: Epoch) -> Slot:
    return Slot(epoch * UPSTREAM_SLOTS_PER_EPOCH)
```

## Beacon chain state transition function

### Block processing

```python
def process_block(state: BeaconState, block: BeaconBlock) -> None:
    process_block_header(state, block)
    process_withdrawals(state, block.body.execution_payload)
    process_execution_payload(state, block.body, EXECUTION_ENGINE)
    process_randao(state, block.body)
    process_eth1_data(state, block.body)
    process_operations(state, block.body)
    process_sync_aggregate(state, block.body.sync_aggregate)
    process_upstream_chain(state, block)
```

#### New `process_upstream_chain`

```python
def process_upstream_chain(state: BeaconState, block: BeaconBlock) -> None:
    upstream_head = block.body.upstream_head

    # Point to an upstream block that's in the past
    assert compute_upstream_timestamp_at_slot(upstream_head.slot) <= compute_timestamp_at_slot(block.slot)

    # Ascending upstream slots
    assert upstream_head.slot >= state.latest_upstream_head.slot

    is_first_post_fork = state.latest_upstream_head == BeaconBlockHeader()
    upstream_unchanged = upstream_head == state.latest_upstream_head

    if upstream_unchanged:
        # Same upstream head — no intermediate headers needed
        assert len(block.body.upstream_intermediate_headers) == 0
    elif not is_first_post_fork:
        # Verify chain continuity: intermediate headers + upstream_head must form
        # a contiguous chain from state.latest_upstream_head to upstream_head.
        chain = list(block.body.upstream_intermediate_headers) + [upstream_head]
        assert chain[0].parent_root == hash_tree_root(state.latest_upstream_head)
        for i in range(1, len(chain)):
            assert chain[i].parent_root == hash_tree_root(chain[i - 1])

    # Upstream finalized checkpoint must not regress
    assert (
        block.body.upstream_finalized_checkpoint.epoch
        >= state.latest_upstream_finalized_checkpoint.epoch
    )

    # Verify that upstream_finalized_checkpoint is committed in the upstream state
    assert is_valid_merkle_branch(
        leaf=hash_tree_root(block.body.upstream_finalized_checkpoint),
        branch=block.body.upstream_finalized_checkpoint_branch,
        depth=floorlog2(UPSTREAM_FINALIZED_CHECKPOINT_GINDEX),
        index=get_subtree_index(UPSTREAM_FINALIZED_CHECKPOINT_GINDEX),
        root=upstream_head.state_root,
    )

    state.latest_upstream_head = upstream_head
    state.latest_upstream_finalized_checkpoint = block.body.upstream_finalized_checkpoint
    promote_pending_finality(state)
```

### Epoch processing

#### Modified `weigh_justification_and_finalization`

*Note*: The function `weigh_justification_and_finalization` is modified
to only track justification (which epochs got 2/3 weight) and append
results to `pending_justified_checkpoints`. Each entry records the
`source_epoch` — the promoted `current_justified_checkpoint.epoch` that
attesters used as their source. The standard Casper FFG 4-case
finalization rule is removed; finalization is computed over the pending
list in `promote_pending_finality` using generalized k-finality.

```python
def weigh_justification_and_finalization(
    state: BeaconState,
    total_active_balance: Gwei,
    previous_epoch_target_balance: Gwei,
    current_epoch_target_balance: Gwei,
) -> None:
    previous_epoch = get_previous_epoch(state)
    current_epoch = get_current_epoch(state)
    old_current = state.pending_current_justified_checkpoint
    # [New in L1HEADERS] Source is what attesters used
    source_epoch = state.current_justified_checkpoint.epoch

    # Process justifications
    if previous_epoch_target_balance * 3 >= total_active_balance * 2:
        cp = Checkpoint(
            epoch=previous_epoch,
            root=get_block_root(state, previous_epoch),
        )
        state.pending_current_justified_checkpoint = cp
        # [New in L1HEADERS]
        if previous_epoch > old_current.epoch:
            state.pending_justified_checkpoints.append(
                PendingJustifiedCheckpoint(
                    source_epoch=source_epoch,
                    checkpoint=cp,
                )
            )
    if current_epoch_target_balance * 3 >= total_active_balance * 2:
        cp = Checkpoint(
            epoch=current_epoch,
            root=get_block_root(state, current_epoch),
        )
        state.pending_current_justified_checkpoint = cp
        # [New in L1HEADERS]
        state.pending_justified_checkpoints.append(
            PendingJustifiedCheckpoint(
                source_epoch=source_epoch,
                checkpoint=cp,
            )
        )

    # [Modified in L1HEADERS] Finalization deferred to
    # promote_pending_finality
```

#### New `promote_pending_finality`

*Note*: `promote_pending_finality` is called from
`process_upstream_chain` whenever new upstream finality data arrives.
It uses generalized k-finality: checkpoint J is finalized if J is the
promoted justified checkpoint, there exists a supermajority link J→T
(an entry with `source_epoch == J`), and all intermediate epochs
J+1..T-1 are justified (any source). This generalizes the standard
4-case rule to arbitrary k, which is needed because the gap between
the promoted checkpoint and the first epoch attested with that source
can span many epochs.

With perfect participation on both chains, finalization takes
approximately 2 × upstream finality delay ≈ **26 minutes**: one
upstream finality period to promote the justified checkpoint, then
one more for the first epoch attested with the new source to be
covered.

```python
def promote_pending_finality(state: BeaconState) -> None:
    upstream_finalized_timestamp = (
        compute_upstream_timestamp_at_slot(
            compute_upstream_start_slot_at_epoch(
                state.latest_upstream_finalized_checkpoint.epoch
            )
        )
    )

    def is_covered(epoch: Epoch) -> bool:
        ts = compute_timestamp_at_slot(
            compute_start_slot_at_epoch(epoch)
        )
        return ts <= upstream_finalized_timestamp

    # Collect justified epochs and source links
    justified_epochs = set()
    # source_epoch -> smallest covered target epoch
    links = {}  # source_epoch -> target_epoch, checkpoint
    for entry in state.pending_justified_checkpoints:
        justified_epochs.add(entry.checkpoint.epoch)
        if is_covered(entry.checkpoint.epoch):
            src = entry.source_epoch
            if src not in links or (
                entry.checkpoint.epoch < links[src][0]
            ):
                links[src] = (
                    entry.checkpoint.epoch,
                    entry.checkpoint,
                )

    # k-finality: find a link from current_justified to some
    # covered target T, with all intermediate epochs justified
    j = state.current_justified_checkpoint.epoch
    if j in links:
        target_epoch, target_cp = links[j]
        # Check all intermediate epochs are justified
        if all(
            e in justified_epochs
            for e in range(j + 1, target_epoch)
        ):
            state.finalized_checkpoint = (
                state.current_justified_checkpoint
            )
            state.previous_justified_checkpoint = (
                state.current_justified_checkpoint
            )
            state.current_justified_checkpoint = target_cp

    # Promote highest covered checkpoint (may skip epochs)
    for entry in reversed(
        state.pending_justified_checkpoints
    ):
        ep = entry.checkpoint.epoch
        if ep > state.current_justified_checkpoint.epoch and (
            is_covered(ep)
        ):
            state.previous_justified_checkpoint = (
                state.current_justified_checkpoint
            )
            state.current_justified_checkpoint = (
                entry.checkpoint
            )
            break

    # Prune promoted checkpoints
    state.pending_justified_checkpoints = [
        entry
        for entry in state.pending_justified_checkpoints
        if entry.checkpoint.epoch
        > state.current_justified_checkpoint.epoch
    ]
```


