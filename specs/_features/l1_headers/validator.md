# L1HEADERS -- Honest Validator

## Table of contents

<!-- TOC -->
<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->

- [Introduction](#introduction)
- [Prerequisites](#prerequisites)
- [Modified proposer duty](#modified-proposer-duty)
    - [Constructing the `BeaconBlockBody`](#constructing-the-beaconblockbody)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->
<!-- /TOC -->

## Introduction

This document represents the changes to be made in the code of an "honest validator" to implement L1HEADERS.

## Prerequisites

This document is an extension of the [Electra -- Honest Validator](../../electra/validator.md) guide.
All behaviors and definitions defined in this document, and documents it extends, carry over unless explicitly noted or overridden.

All terminology, constants, functions, and protocol mechanics defined in the updated Beacon Chain doc of [L1HEADERS](./beacon-chain.md) are requisite for this document and used throughout.

## Modified proposer duty

#### Constructing the `BeaconBlockBody`

To propose, the validator include in the block the upstream chain head.

1. Run fork-choice handler `on_upstream_head`. Lock the handler to prevent additional runs during block proposal
2. Compute the parent root with `get_proposer_head` as spec-ed 
3. Set `block.body.upstream_head = upstream_block`, where
    * `upstream_block` is the return value of `get_target_upstream_canonical_block(slot)` and `slot` is the proposal slot.
4. Set `block.body.upstream_finalized_checkpoint` and `block.body.upstream_finalized_checkpoint_branch` from `retrieve_upstream_finalized_checkpoint_with_proof(upstream_block.state_root)`.

```python
def retrieve_upstream_finalized_checkpoint_with_proof(
    state_root: Root
) -> Tuple[Checkpoint, UpstreamFinalityBranch]:
    # `retrieve_upstream_finalized_checkpoint_with_proof` is implementation dependent.
    # It returns the upstream chain finalized checkpoint and its Merkle proof against
    # the given upstream beacon state root.
    #
    # Implementations MAY retrieve the checkpoint via the beacon API
    # `/eth/v1/beacon/states/{state_id}/finality_checkpoints` and compute the proof
    # using `compute_merkle_proof(upstream_state, UPSTREAM_FINALIZED_CHECKPOINT_GINDEX)`.
```

