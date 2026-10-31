"""Human gate: no action without human approval, fail-closed, audited.

Rules, adapted from AgentGate for this prototype:
  * Every action (alert, decoy) needs a request first.
  * "alert" needs 1 approver; "decoy" needs 2 distinct approvers.
  * An action executes ONLY if its quorum is met. Anything else is
    DENIED, recorded, and performs nothing. There is no override path.
  * Every request, approval, execution, and denial is appended to a
    hash-chained ledger: entry hash = sha256(prev_hash + canonical
    entry). Tampering with any entry breaks every later hash, and
    verify_chain() detects it.

This gate is the whole point of the "AI for humanity" mission in code
form: autonomy in sensing, humanity in deciding.
"""

from __future__ import annotations

import hashlib
import json

QUORUM = {"alert": 1, "decoy": 2}


def _canonical(entry: dict) -> str:
    return json.dumps(entry, sort_keys=True, separators=(",", ":"))


def _hash(prev_hash: str, entry: dict) -> str:
    return hashlib.sha256((prev_hash + _canonical(entry)).encode()).hexdigest()


class HumanGate:
    """Approval gate with a hash-chained audit ledger."""

    def __init__(self):
        self._requests: dict[str, dict] = {}
        self.ledger: list[dict] = []
        self._prev_hash = "0" * 64
        self._counter = 0

    def _log(self, kind: str, **fields) -> dict:
        entry = {"kind": kind, **fields}
        record = {
            "prev_hash": self._prev_hash,
            "entry": entry,
            "hash": _hash(self._prev_hash, entry),
        }
        self.ledger.append(record)
        self._prev_hash = record["hash"]
        return record

    def request(self, action: str, detail: str = "") -> str:
        """Open an action request. Returns its request id."""
        if action not in QUORUM:
            raise ValueError(f"unknown action: {action!r}")
        self._counter += 1
        request_id = f"req-{self._counter}"
        self._requests[request_id] = {
            "action": action,
            "detail": detail,
            "approvers": [],
        }
        self._log("requested", request_id=request_id, action=action, detail=detail)
        return request_id

    def approve(self, request_id: str, approver: str) -> bool:
        """Record one approver. Returns True if the quorum is now met."""
        req = self._requests.get(request_id)
        if req is None:
            raise KeyError(f"unknown request: {request_id!r}")
        if approver not in req["approvers"]:
            req["approvers"].append(approver)
        self._log("approved", request_id=request_id, approver=approver)
        return len(req["approvers"]) >= QUORUM[req["action"]]

    def execute(self, request_id: str) -> dict:
        """Execute only if quorum is met; otherwise deny and do nothing."""
        req = self._requests.get(request_id)
        if req is None:
            raise KeyError(f"unknown request: {request_id!r}")
        if len(req["approvers"]) >= QUORUM[req["action"]]:
            self._log(
                "executed",
                request_id=request_id,
                action=req["action"],
                approvers=list(req["approvers"]),
            )
            return {"status": "executed", "action": req["action"]}
        self._log("denied", request_id=request_id, action=req["action"])
        return {"status": "denied", "action": req["action"]}

    def verify_chain(self) -> bool:
        """True iff every ledger hash links correctly to its predecessor."""
        prev = "0" * 64
        for record in self.ledger:
            if record["prev_hash"] != prev:
                return False
            if record["hash"] != _hash(prev, record["entry"]):
                return False
            prev = record["hash"]
        return True
