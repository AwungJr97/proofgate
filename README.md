# ProofGate

Consensus-backed evidence attestation primitive for GenLayer.

ProofGate is a standalone Intelligent Contract designed to let other contracts and applications request a semantic verification of evidence against a frozen requirement. The contract keeps the semantic judgment inside GenLayer consensus and the security-sensitive lifecycle in deterministic contract state.

## Design goals

- Bounded semantic outcome: `VALID`, `INVALID`, or `UNRESOLVED`.
- Frozen requirement and evidence reference before evaluation.
- Deterministic request state and authorization rules.
- Finalized attestations cannot be overwritten.
- `UNRESOLVED` does not silently become a positive or negative attestation.
- Reusable read methods for downstream contracts.

## Intended uses

ProofGate is intended as a reusable primitive for evidence-gated workflows such as bounty verification, milestone attestations, governance evidence, compliance checks, and agent task completion.

## Current status

Initial repository scaffold. Contract implementation, tests, and deployment evidence will be added only after the consensus design is validated against the current GenLayer runner and SDK behavior.
