# { "Depends": "py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6" }

from genlayer import *
import hashlib
import re

VALID = "VALID"
INVALID = "INVALID"
UNRESOLVED = "UNRESOLVED"
PENDING = "PENDING"


class ProofGate(gl.Contract):
    """Consensus-backed semantic evidence attestation primitive."""

    next_request_id: u256
    requirements: TreeMap[u256, str]
    evidence_urls: TreeMap[u256, str]
    statuses: TreeMap[u256, str]
    evidence_hashes: TreeMap[u256, str]
    finalized: TreeMap[u256, bool]

    def __init__(self):
        # GenLayer storage collections are zero-initialized automatically.
        self.next_request_id = u256(1)

    @gl.public.write
    def create_request(self, requirement: str, evidence_url: str) -> u256:
        if not requirement.strip():
            raise gl.UserError("Requirement cannot be empty")
        if not evidence_url.startswith(("https://", "http://")):
            raise gl.UserError("Evidence URL must use http or https")

        request_id = self.next_request_id
        self.next_request_id += u256(1)
        self.requirements[request_id] = requirement
        self.evidence_urls[request_id] = evidence_url
        self.statuses[request_id] = PENDING
        self.evidence_hashes[request_id] = ""
        self.finalized[request_id] = False
        return request_id

    @gl.public.write
    def evaluate(self, request_id: u256) -> str:
        if request_id == 0 or request_id >= self.next_request_id:
            raise gl.UserError("Unknown request")
        if self.finalized[request_id]:
            raise gl.UserError("Request is already finalized")
        if self.statuses[request_id] != PENDING:
            raise gl.UserError("Request is not pending")

        requirement = self.requirements[request_id]
        evidence_url = self.evidence_urls[request_id]

        def assess_source():
            response = gl.nondet.web.get(evidence_url)
            source = response.body.decode("utf-8")
            evidence = re.sub(r"\s+", " ", source).strip()[:12000]
            if not evidence:
                return {"verdict": UNRESOLVED, "evidence_hash": ""}

            evidence_hash = hashlib.sha256(evidence.encode("utf-8")).hexdigest()
            prompt = f"""
You are a conservative evidence verifier.
Requirement: {requirement}
Evidence URL: {evidence_url}
Evidence content: {evidence}

Use only the supplied evidence. Do not invent facts.
Return VALID when the evidence clearly establishes the requirement.
Return INVALID only when it clearly contradicts the requirement.
Otherwise return UNRESOLVED.
Return JSON only: {{"verdict":"VALID|INVALID|UNRESOLVED"}}
"""
            result = gl.nondet.exec_prompt(prompt, response_format="json")
            verdict = result.get("verdict", UNRESOLVED) if isinstance(result, dict) else UNRESOLVED
            if verdict not in (VALID, INVALID, UNRESOLVED):
                verdict = UNRESOLVED
            return {"verdict": verdict, "evidence_hash": evidence_hash}

        def validator_fn(leader_result):
            if not isinstance(leader_result, gl.vm.Return):
                return False
            data = leader_result.calldata
            if not isinstance(data, dict):
                return False
            leader_hash = data.get("evidence_hash")
            leader_verdict = data.get("verdict")
            if leader_verdict not in (VALID, INVALID, UNRESOLVED) or not leader_hash:
                return False

            response = gl.nondet.web.get(evidence_url)
            source = response.body.decode("utf-8")
            evidence = re.sub(r"\s+", " ", source).strip()[:12000]
            validator_hash = hashlib.sha256(evidence.encode("utf-8")).hexdigest()
            return validator_hash == leader_hash

        result = gl.vm.run_nondet_unsafe(assess_source, validator_fn)
        if not isinstance(result, dict):
            raise gl.UserError("Invalid consensus result")

        verdict = result.get("verdict")
        evidence_hash = result.get("evidence_hash", "")
        if verdict not in (VALID, INVALID, UNRESOLVED) or not evidence_hash:
            raise gl.UserError("Consensus returned an invalid attestation")

        self.statuses[request_id] = verdict
        self.evidence_hashes[request_id] = evidence_hash
        self.finalized[request_id] = True
        return verdict

    @gl.public.view
    def get_request(self, request_id: u256) -> dict:
        if request_id == 0 or request_id >= self.next_request_id:
            raise gl.UserError("Unknown request")
        return {
            "request_id": request_id,
            "requirement": self.requirements[request_id],
            "evidence_url": self.evidence_urls[request_id],
            "status": self.statuses[request_id],
            "evidence_hash": self.evidence_hashes[request_id],
            "finalized": self.finalized[request_id],
        }

    @gl.public.view
    def get_status(self, request_id: u256) -> str:
        if request_id == 0 or request_id >= self.next_request_id:
            raise gl.UserError("Unknown request")
        return self.statuses[request_id]
