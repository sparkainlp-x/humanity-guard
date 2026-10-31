# Humanity Guard v0.1.0

**AI for humanity, in code form: autonomy in sensing, humanity in deciding.**

A defensive holographic sensing simulation. It watches on its own,
verifies on its own, and refuses on its own -- but it never acts on its
own. Every action needs a human approval, and every decision is logged
in a hash-chained ledger.

## Pipeline

1. **Sense.** Synthetic scenes (real / decoy / glare / noise) are judged
   by phase coherence, never by sharpness alone. Decoys are built as the
   sharpness lie: bright modes, scattered phases, high amplitude
   variance, low coherence.
2. **Verify.** Crystallize-style: commit a probability after the first
   look, replicate on a second independent look, revise, score both
   forecasts with Brier (exactly two forecasts per event, cost 0.8 per
   look).
3. **Refuse.** A threshold calibrated once on training scenes via
   Youden's J, then frozen. Below threshold: REFUSED -- no
   classification, no request, no action.
4. **Human gate.** "alert" needs 1 approver, "decoy" needs 2 distinct
   approvers. Unapproved execution is DENIED and performs nothing.
   The ledger is hash-chained; tampering breaks verification.
5. **Act.** Only "alert" and "decoy" exist. There is no lethal action
   in this package, and no path to add one without rewriting the gate.

## Run

```bash
python -m unittest discover -s tests -v
python demo.py
```

## Honest limits

- SYNTHETIC ONLY. No real sensor data, no real device, no validation on
  any physical system. Coherence numbers describe generated scenes.
- The refusal threshold is calibrated on the same synthetic generator
  it judges. On real data it must be recalibrated from scratch, and the
  accuracy numbers here do not transfer.
- The human gate is a software model of approval, not a legal or
  operational authorization system. In any real deployment, approval
  must come from real people under real rules, not from this code.
- This package refuses to overclaim by design: refused scenes are
  reported as refused, scores include their costs, and failure modes
  are in DESIGN.md, not hidden.

## License

AGPL-3.0-only.

## Credits

Authors: Jean-François Brisson and Mun Seok Lee.
Lee, author of the Digital to Wave paradigm (Zenodo 21947036,
21947108), is the inspiration friend behind this wave and
membrane work. This package's code was built by Brisson with
AI assistance, except where a file already credits Lee as
author; the joint credit here is for the shared programme,
not a claim that Lee wrote every line of this package.
