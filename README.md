# ProofGate

**ProofGate** is a standalone GenLayer Intelligent Contract primitive for consensus-backed semantic evidence attestation.

It lets a caller freeze a human-readable requirement together with an evidence URL, then asks GenLayer validators to independently inspect the same source and agree on a bounded verdict:

- `VALID` — the supplied evidence clearly establishes the requirement.
- `INVALID` — the supplied evidence clearly contradicts the requirement.
- `UNRESOLVED` — the evidence is unavailable, ambiguous, contradictory, or insufficient.

The contract stores the request and finalized attestation onchain. A finalized request cannot be evaluated again, so a caller cannot silently replace an existing result.

## Why this is a reusable primitive

ProofGate separates **semantic consensus** from **deterministic state management**:

1. `create_request()` freezes the requirement and evidence URL and assigns an owner.
2. `evaluate()` performs nondeterministic web retrieval and semantic assessment inside the GenLayer consensus boundary.
3. Validators independently retrieve the same source, reproduce the evidence hash, and validate the leader's bounded verdict.
4. Only the consensus result is committed to persistent contract state.
5. `get_request()` and `get_status()` expose a compact receipt-like interface for downstream contracts and applications.

This pattern is useful anywhere an onchain workflow needs a defensible semantic evidence gate, including bounty verification, milestone attestations, governance evidence, compliance workflows, and agent task completion.

## Contract state

Each request stores:

| Field | Purpose |
| --- | --- |
| `requirement` | Frozen semantic condition to verify |
| `evidence_url` | Frozen public evidence source |
| `owner` | Address that created the request |
| `status` | `PENDING`, `VALID`, `INVALID`, or `UNRESOLVED` |
| `evidence_hash` | SHA-256 hash of the evidence excerpt used for judgment |
| `finalized` | Prevents repeated evaluation after settlement |

## Consensus design

The semantic boundary is deliberately narrow. The model does not write arbitrary text to state; it can only produce one of three allowed verdicts. The validator function independently fetches and extracts the evidence, checks that the evidence hash matches the leader result, and performs its own bounded acceptance check.

A source that cannot be reliably established is not converted into a positive attestation. This makes `UNRESOLVED` a first-class outcome rather than a hidden fallback.

## Source

- Contract: [`contracts/proof_gate.py`](contracts/proof_gate.py)
- Design decisions: [`DECISIONS.md`](DECISIONS.md)
- Deterministic tests: [`tests/test_proof_gate.py`](tests/test_proof_gate.py)

## Studio deployment evidence

The current tested deployment is available in GenLayer Studio Explorer:

**Contract:** `0x5114A0E318C3E54767EF21356Fdf0F25a0dd1661`

The deployment transaction finalized successfully. A live request was then created and evaluated through the Studio full-consensus execution path. The evaluation returned `UNRESOLVED` with a non-empty evidence hash and `finalized: true`; this is a valid conservative outcome when the evidence cannot be established with sufficient confidence.

See [`DEPLOYMENT.md`](DEPLOYMENT.md) for the exact transaction evidence and reproducible flow.

## Scope and limitations

ProofGate does not claim that an external website is permanently truthful. It attests only to the evidence retrieved and semantically assessed during the consensus execution. Web content can change between requests, which is why the evidence hash is stored with the finalized result.

The contract has no frontend, backend, custody, token transfer, or financial settlement logic. It is intentionally a reusable contract primitive that other applications can compose.
