# Instructor notes — session 25

## 0–20 minutes: technical discussion

Use this claim as the opening question: Approval is a durable state transition bound to exact arguments and the authorized approver. Ask engineers to name a counterexample and the boundary where the claim stops holding. Spend no time defining AI or replaying introductory demos. Use the existing Larkhaven data and the preceding session's evidence.

Explain the mechanism: Approval is a durable state transition bound to exact arguments and the authorized approver. Editing an approved action invalidates approval. Licence allocation and final status must commit atomically.

## 20–75 minutes: build and investigation

Walk through the first source file, then let pairs implement the increment using [the numbered steps](STEPS_TO_FOLLOW.md). One engineer changes code while the other predicts observable effects and checks assumptions. Swap roles halfway through.

Demonstrate this failure before the solution: Approve as analyst instead of the named manager, replay a decision and race two claims for the final seat. Discuss which check belongs in deterministic code and which requires model or human judgement. For live work, confirm keys, Docker and model downloads before class; keep the offline experiment available when a service is unavailable, and explicitly defer that live gate.

## 75–90 minutes: evidence review

Require: Request 4 end state plus unauthorized, replay and seat-capacity tests. Have each pair explain one observed error, one tradeoff and one remaining uncertainty. Do not accept screenshots of plausible answers as proof of persisted effects.

## Stretch task

Repeat the experiment with one controlled change and preserve the original run. Report the quality or safety change together with its latency and operational cost. Use a held-out example when tuning is involved.

## Handoff

Retain the same contracts and regression suite in session 26. Open an ADR when an alternative is chosen; include the measurements, configuration and rejected tradeoff.
