# { "Depends": "py-genlayer:9b8kjyda2ycxyq4ea6g4yfpnydxhd52gqba5rb8dw7krkh5mn9p0" }

import genlayer as gl
from genlayer.types import Address

VALID = "VALID"
INVALID = "INVALID"
UNRESOLVED = "UNRESOLVED"
PENDING = "PENDING"


class ProofGate(gl.contract.Contract):
    """Reusable semantic evidence-attestation primitive.

    A requester freezes a requirement and an evidence URL. Evaluation is the
    only nondeterministic boundary: validators independently fetch the source
    and classify whether the evidence satisfies the frozen requirement.
    Everything after consensus is deterministic and immutable.
    """

    next_request_id: int
    requirements: gl.storage.TreeMap[int, str]
    evidence_urls: gl.storage.TreeMap[int, str]
    owners: gl.storage.TreeMap[int, Address]
    statuses: gl.storage.TreeMap[int, str]
    finalized: gl.storage.TreeMap[int, bool]

    def __init__(self) -> None:
        self.next_request_id = 1
        self.requirements = gl.storage.TreeMap()
        self.evidence_urls = gl.storage.TreeMap()
        self.owners = gl.storage.TreeMap()
        self.statuses = gl.storage.TreeMap()
        self.finalized = gl.storage.TreeMap()

    @gl.public.write
    def create_request(self, requirement: str, evidence_url: str) -> int:
        if not requirement.strip():
            raise gl.vm.UserError("Requirement cannot be empty")
        if not evidence_url.startswith(("https://", "http://")):
            raise gl.vm.UserError("Evidence URL must use http or https")

        request_id = self.next_request_id
        self.next_request_id += 1
        self.requirements[request_id] = requirement
        self.evidence_urls[request_id] = evidence_url
        self.owners[request_id] = gl.message.sender_address
        self.statuses[request_id] = PENDING
        self.finalized[request_id] = False
        return request_id

    @gl.public.write
    def evaluate(self, request_id: int) -> str:
        if request_id <= 0 or request_id >= self.next_request_id:
            raise gl.vm.UserError("Unknown request")
        if self.finalized.get(request_id, False):
            raise gl.vm.UserError("Request is already finalized")
        if self.statuses.get(request_id, PENDING) != PENDING:
            raise gl.vm.UserError("Request is not pending")

        requirement = self.requirements[request_id]
        evidence_url = self.evidence_urls[request_id]

        def leader_fn():
            response = gl.nondet.web.get(evidence_url)
            if response.status_code < 200 or response.status_code >= 300:
                return {"verdict": UNRESOLVED}
            source = response.body.decode("utf-8")
            prompt = f"""
You are an evidence verifier operating inside a consensus-backed contract.

Frozen requirement:
{requirement}

Evidence source URL:
{evidence_url}

Evidence source content:
{source[:16000]}

Classify ONLY whether the evidence source satisfies the frozen requirement.
Do not invent facts. If the source is unavailable, contradictory,
insufficient, or the requirement cannot be established from the source,
return UNRESOLVED. Return INVALID when the source affirmatively fails.

Return JSON only: {{"verdict":"VALID|INVALID|UNRESOLVED"}}
"""
            result = gl.nondet.exec_prompt(prompt, response_format="json")
            verdict = result.get("verdict", UNRESOLVED)
            if verdict not in (VALID, INVALID, UNRESOLVED):
                verdict = UNRESOLVED
            return {"verdict": verdict}

        def validator_fn(leader_result) -> bool:
            if not isinstance(leader_result, gl.vm.Return):
                return False
            leader_data = leader_result.calldata
            if not isinstance(leader_data, dict):
                return False
            leader_verdict = leader_data.get("verdict")
            if leader_verdict not in (VALID, INVALID, UNRESOLVED):
                return False
            own = leader_fn()
            return own.get("verdict") == leader_verdict

        result = gl.vm.run_nondet_unsafe(leader_fn, validator_fn)
        verdict = result["verdict"]
        if verdict not in (VALID, INVALID, UNRESOLVED):
            raise gl.vm.UserError("Consensus returned an invalid verdict")

        # Persistent state changes happen only after consensus.
        self.statuses[request_id] = verdict
        self.finalized[request_id] = True
        return verdict

    @gl.public.view
    def get_request(self, request_id: int) -> dict:
        if request_id <= 0 or request_id >= self.next_request_id:
            raise gl.vm.UserError("Unknown request")
        return {
            "request_id": request_id,
            "requirement": self.requirements[request_id],
            "evidence_url": self.evidence_urls[request_id],
            "owner": self.owners[request_id].as_hex,
            "status": self.statuses[request_id],
            "finalized": self.finalized[request_id],
        }

    @gl.public.view
    def get_status(self, request_id: int) -> str:
        if request_id <= 0 or request_id >= self.next_request_id:
            raise gl.vm.UserError("Unknown request")
        return self.statuses[request_id]
