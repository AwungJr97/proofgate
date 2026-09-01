# ProofGate Design Decisions

## 1. Bounded verdicts

The semantic boundary returns exactly `VALID`, `INVALID`, or `UNRESOLVED`. Free-form model text is never accepted as contract state.

## 2. Frozen inputs

The requirement and evidence URL are stored when the request is created. Evaluation reads those stored values instead of accepting replacement text during judgment. This prevents an evaluator from changing the question or evidence after a request exists.

## 3. Consensus before state transition

Nondeterministic web retrieval and semantic assessment happen inside the GenLayer consensus boundary. Persistent state is updated only after the consensus call returns a bounded result.

## 4. Evidence hash as an integrity anchor

The evidence excerpt used for judgment is hashed with SHA-256. Validators reproduce the hash from their own retrieval and reject a leader result when the hash differs. The finalized hash is retained with the verdict so downstream consumers can see exactly which evidence snapshot the attestation refers to.

## 5. Conservative uncertainty

Unavailable, contradictory, ambiguous, or insufficient evidence produces `UNRESOLVED`. It is never promoted to `VALID` by fallback logic. This is important for evidence-gated workflows where a false positive is more dangerous than a retryable uncertainty.

## 6. Finalization guard

A finalized request cannot be evaluated again. This prevents an arbitrary caller from repeatedly replacing an attestation and makes the result a stable state transition.

## 7. Deterministic lifecycle

Request creation, ID allocation, ownership, status storage, and finalization are deterministic contract operations. Only the interpretation of external evidence crosses the nondeterministic consensus boundary.

## 8. Reusable interface

`get_request()` returns the requirement, evidence URL, owner, status, evidence hash, and finalization state. `get_status()` provides a smaller read path for downstream consumers. No frontend or backend is required to consume the primitive.

## 9. Composition target

ProofGate is intentionally narrower than an end-to-end application. A downstream contract can use the finalized status as an evidence gate while keeping its own deterministic business rules separate from semantic interpretation.

## 10. Known limitation

ProofGate does not guarantee that a web source remains truthful or unchanged. The attestation is tied to the evidence retrieved during consensus, and the stored hash makes that limitation explicit rather than hiding it.
