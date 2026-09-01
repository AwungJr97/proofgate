# ProofGate Design Decisions

## 1. Bounded verdicts
The semantic boundary returns exactly `VALID`, `INVALID`, or `UNRESOLVED`. Free-form model text is not accepted as contract state.

## 2. Frozen inputs
The requirement and evidence URL are stored when the request is created. Evaluation reads those stored values instead of accepting replacement text during judgment.

## 3. Consensus before state transition
Nondeterministic evidence inspection happens before the contract writes the verdict. The persistent state transition is deterministic after consensus.

## 4. Conservative uncertainty
Unavailable, contradictory, or insufficient evidence produces `UNRESOLVED`. It is never promoted to `VALID` by fallback logic.

## 5. Finalization guard
A finalized request cannot be evaluated again. This prevents an arbitrary caller from repeatedly replacing an attestation.

## 6. Reusable interface
The request/status getters expose a compact receipt-like state that downstream applications can consume without depending on a frontend.

## 7. Verification boundary
The repository separates deterministic invariant tests from runner-specific consensus integration tests. Deployment evidence will be added only after the exact source has passed the target GenLayer runner.
