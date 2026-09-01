# ProofGate Deployment Evidence

## GenLayer Studio

Tested contract deployment:

- Contract: `0x5114A0E318C3E54767EF21356Fdf0F25a0dd1661`
- Explorer: https://explorer-studio.genlayer.com/address/0x5114A0E318C3E54767EF21356Fdf0F25a0dd1661
- Deployment result: `FINALIZED`
- Deployment transaction: `0xb781ef1e4368599d0557ce8c122fe76b2e786356982e5d0f9ed458438b7f79f5`

## Live request flow

A request was created through the deployed contract:

- `create_request(requirement, evidence_url)` returned request ID `1`.
- The transaction reached `FINALIZED` with `ACCEPTED` consensus.
- Evidence URL used: `https://docs.genlayer.com/`
- Requirement used: `The official GenLayer documentation describes Intelligent Contracts as smart contracts that can use AI and non-deterministic operations.`

The request was then evaluated through **Normal (Full Consensus)**:

- `evaluate(1)` returned `SUCCESS` and finalized the request.
- Consensus produced the bounded verdict `UNRESOLVED`.
- A non-empty evidence hash was committed.
- `get_request(1)` returned `finalized: true` and the stored verdict/hash.

## Interpretation

`UNRESOLVED` is an intentional valid outcome in ProofGate. It means the semantic evidence gate did not establish the requirement with sufficient confidence. The contract does not convert uncertainty into a false positive.

The important deployment properties demonstrated by this run are the complete request lifecycle, real GenLayer nondeterministic execution, validator consensus, bounded output, evidence hashing, and immutable finalization.

## Reproduction

1. Deploy `contracts/proof_gate.py` in GenLayer Studio.
2. Use Normal (Full Consensus), not Leader Only.
3. Call `create_request()` with a requirement and public HTTP(S) evidence URL.
4. Call `evaluate()` with the returned request ID.
5. Call `get_request()` to inspect the finalized receipt.
