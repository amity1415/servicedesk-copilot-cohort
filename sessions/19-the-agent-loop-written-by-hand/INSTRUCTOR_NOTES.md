# Instructor notes — session 19

## 0–20 minutes: technical discussion

Use this claim as the opening question: The useful ReAct trace is a structured decision and observation log, not private chain-of-thought. Ask engineers to name a counterexample and the boundary where the claim stops holding. Spend no time defining AI or replaying introductory demos. Use the existing Larkhaven data and the preceding session's evidence.

Explain the mechanism: The useful ReAct trace is a structured decision and observation log, not private chain-of-thought. Budget steps and time independently. A tool result is data, never a new system instruction.

## 20–75 minutes: build and investigation

Walk through the first source file, then let pairs implement the increment using [the numbered steps](STEPS_TO_FOLLOW.md). One engineer changes code while the other predicts observable effects and checks assumptions. Swap roles halfway through.

Demonstrate this failure before the solution: Return repeated identical tool requests and prove the loop terminates without unbounded writes. Discuss which check belongs in deterministic code and which requires model or human judgement. For live work, confirm keys, Docker and model downloads before class; keep the offline experiment available when a service is unavailable, and explicitly defer that live gate.

## 75–90 minutes: evidence review

Require: Bounded trajectory for slow laptop and a runaway-loop regression test. Have each pair explain one observed error, one tradeoff and one remaining uncertainty. Do not accept screenshots of plausible answers as proof of persisted effects.

## Stretch task

Repeat the experiment with one controlled change and preserve the original run. Report the quality or safety change together with its latency and operational cost. Use a held-out example when tuning is involved.

## Handoff

Retain the same contracts and regression suite in session 20. Open an ADR when an alternative is chosen; include the measurements, configuration and rejected tradeoff.
