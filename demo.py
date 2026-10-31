"""Demo: one perimeter watch with humanity-guard.

Run: python demo.py
"""

from humanity_guard.engine import GuardianEngine

KINDS = ["real", "decoy", "glare", "noise", "real", "decoy", "real", "noise"]

eng = GuardianEngine(seed=42)
print(f"calibrated refusal threshold tau = {eng.gate.tau:.3f}")
print(f"{'scene':<7} {'coherence':>9} {'score':>7}  decision  action")
for kind in KINDS:
    event = eng.process(kind)
    action = "-"
    if event["request_id"] is not None:
        eng.human_gate.approve(event["request_id"], "operator")
        result = eng.human_gate.execute(event["request_id"])
        action = result["status"] + ":" + result["action"]
    print(
        f"{kind:<7} {event['mean_coherence']:>9.3f} {event['score']:>7.1f}  "
        f"{event['decision']:<8}  {action}"
    )
print()
print(eng.summary())
print("ledger valid:", eng.human_gate.verify_chain())
