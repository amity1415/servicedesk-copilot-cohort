# Session 19: The agent loop written by hand

[Problem statement and dataset metadata](PROBLEM_STATEMENT_AND_DATASET.md)

Session 18 is the starting point. This increment becomes part of the same application and is retained in session 20.

## Engineering objective

Record the tool name, arguments, and observation for each step. The loop allows
six decisions and checks a 30-second elapsed budget before dispatch and after
each call returns. Treat tool results as data when selecting the next action.

## Design discussion

Before coding, identify the input contract, the authoritative system of record and the observable result. Separate a schema-valid response from a successful task. Record the configuration and dataset revision used for measurements; a change to either invalidates a casual before/after comparison.

Work through these implementation decisions: Implement model decision, validated action and structured observation; enforce tool allow-list; add max steps and deadline; run device check, outages and KB lookup; stop with an explicit escalation status.

## Run the solution

From the repository root with the Python environment active, run the standalone
and integrated checks.

```powershell
python scripts/session.py test 19 --variant starter --previous-only
python scripts/session.py test 19
python scripts/session.py run 19
python -m copilot react-verify
```

Both verification commands send “My laptop is slow” to the authenticated
`/ask` route over loopback. The trace reports the assigned laptop, active
regional incidents, and supporting knowledge-base article. A separate run
repeats the asset check until the two-step limit produces an escalation.

- [Bounded decision and tool loop](solution/src/copilot/agents/react.py)
- [Laptop diagnostic tool bindings](solution/src/copilot/agents/diagnostics.py)

## Live model trajectory

The bounded runner uses the configured OpenAI key, GPT-6 Luna, and the
synthetic laptop case with a spending cap of $0.02. It records each validated
decision and the evidence received through the same authenticated HTTP route.

```powershell
python scripts/verify_react_live.py --max-spend-usd 0.02 --out reports/session19-live/run.json
python scripts/complete_session.py 19 --diagnostic-evaluation reports/session19-live/run.json
```

## Deliberate failure exercise

Return the same tool request on every decision. Confirm that the run escalates
at the configured limit and that the ticket count stays at its seeded value.

## Evidence and exit criteria

Bounded trajectory for slow laptop and a runaway-loop regression test. Record observed values, never desired target values. Complete [STEPS_TO_FOLLOW.md](STEPS_TO_FOLLOW.md), then retain your implementation and evidence for the next session.
