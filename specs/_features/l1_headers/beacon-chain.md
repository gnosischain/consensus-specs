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
| `PENDING_FINALITY_LIMIT` | `uint64(2**10)` (=1024) | Max pending checkpoints (~13.6 hours of Gnosis epochs) |
| `MAX_UPSTREAM_INTERMEDIATE_HEADERS` | `uint64(2**6)` (=64) | Max upstream headers between consecutive Gnosis blocks |
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
    justification_bits: Bitvector[JUSTIFICATION_BITS_LENGTH]
    previous_justified_checkpoint: Checkpoint
    current_justified_checkpoint: Checkpoint
    finalized_checkpoint: Checkpoint
    # [New in L1HEADERS] Pending finality — computed by standard Casper FFG but not yet
    # promoted, waiting for upstream finality. We gate on upstream finality (not justification)
    # because upstream justification is reversible and a rollback would force slashable votes.
    # Accumulated as lists since upstream finality may arrive at any point.
    pending_justified_checkpoints: List[Checkpoint, PENDING_FINALITY_LIMIT]
    pending_finalized_checkpoints: List[Checkpoint, PENDING_FINALITY_LIMIT]
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

*Note*: The function `weigh_justification_and_finalization` is modified to accumulate justification and finalization results in pending lists instead of applying them directly. The only diff from the standard function is the `[New in L1HEADERS]` block at the end.

```python
def weigh_justification_and_finalization(state: BeaconState,
                                         total_active_balance: Gwei,
                                         previous_epoch_target_balance: Gwei,
                                         current_epoch_target_balance: Gwei) -> None:
    previous_epoch = get_previous_epoch(state)
    current_epoch = get_current_epoch(state)
    old_previous_justified_checkpoint = state.previous_justified_checkpoint
    old_current_justified_checkpoint = state.current_justified_checkpoint
    old_finalized_checkpoint = state.finalized_checkpoint  # [New in L1HEADERS]

    # Process justifications
    state.previous_justified_checkpoint = state.current_justified_checkpoint
    state.justification_bits[1:] = state.justification_bits[:JUSTIFICATION_BITS_LENGTH - 1]
    state.justification_bits[0] = 0b0
    if previous_epoch_target_balance * 3 >= total_active_balance * 2:
        state.current_justified_checkpoint = Checkpoint(epoch=previous_epoch,
                                                        root=get_block_root(state, previous_epoch))
        state.justification_bits[1] = 0b1
    if current_epoch_target_balance * 3 >= total_active_balance * 2:
        state.current_justified_checkpoint = Checkpoint(epoch=current_epoch,
                                                        root=get_block_root(state, current_epoch))
        state.justification_bits[0] = 0b1

    # Process finalizations
    bits = state.justification_bits
    # The 2nd/3rd/4th most recent epochs are justified, the 2nd using the 4th as source
    if all(bits[1:4]) and old_previous_justified_checkpoint.epoch + 3 == current_epoch:
        state.finalized_checkpoint = old_previous_justified_checkpoint
    # The 2nd/3rd most recent epochs are justified, the 2nd using the 3rd as source
    if all(bits[1:3]) and old_previous_justified_checkpoint.epoch + 2 == current_epoch:
        state.finalized_checkpoint = old_previous_justified_checkpoint
    # The 1st/2nd/3rd most recent epochs are justified, the 1st using the 3rd as source
    if all(bits[0:3]) and old_current_justified_checkpoint.epoch + 2 == current_epoch:
        state.finalized_checkpoint = old_current_justified_checkpoint
    # The 1st/2nd most recent epochs are justified, the 1st using the 2nd as source
    if all(bits[0:2]) and old_current_justified_checkpoint.epoch + 1 == current_epoch:
        state.finalized_checkpoint = old_current_justified_checkpoint

    # [New in L1HEADERS] Accumulate results into pending lists, then revert.
    # Real checkpoints advance only through promote_pending_finality().
    if state.current_justified_checkpoint.epoch > old_current_justified_checkpoint.epoch:
        state.pending_justified_checkpoints.append(state.current_justified_checkpoint)
    if state.finalized_checkpoint.epoch > old_finalized_checkpoint.epoch:
        state.pending_finalized_checkpoints.append(state.finalized_checkpoint)
    state.previous_justified_checkpoint = old_previous_justified_checkpoint
    state.current_justified_checkpoint = old_current_justified_checkpoint
    state.finalized_checkpoint = old_finalized_checkpoint
```

#### New `promote_pending_finality`

*Note*: `promote_pending_finality` is called from `process_upstream_chain` whenever new upstream finality data arrives. It promotes the highest pending checkpoint whose timestamp is covered by upstream finality. We gate on upstream **finality** (not justification) because upstream justification is reversible — if it rolled back, attesters would be forced into slashable votes.

```python
def promote_pending_finality(state: BeaconState) -> None:
    upstream_finalized_timestamp = compute_upstream_timestamp_at_slot(
        compute_upstream_start_slot_at_epoch(state.latest_upstream_finalized_checkpoint.epoch)
    )

    for cp in reversed(state.pending_justified_checkpoints):
        cp_timestamp = compute_timestamp_at_slot(compute_start_slot_at_epoch(cp.epoch))
        if cp_timestamp <= upstream_finalized_timestamp:
            state.previous_justified_checkpoint = state.current_justified_checkpoint
            state.current_justified_checkpoint = cp
            state.pending_justified_checkpoints = [
                x for x in state.pending_justified_checkpoints if x.epoch > cp.epoch
            ]
            break

    for cp in reversed(state.pending_finalized_checkpoints):
        cp_timestamp = compute_timestamp_at_slot(compute_start_slot_at_epoch(cp.epoch))
        if cp_timestamp <= upstream_finalized_timestamp:
            state.finalized_checkpoint = cp
            state.pending_finalized_checkpoints = [
                x for x in state.pending_finalized_checkpoints if x.epoch > cp.epoch
            ]
            break
```


