# policies/

Rules the shipped agent must follow, kept as data so they are reviewed like code and never buried in a prompt.

| File | Created in | Holds |
| --- | --- | --- |
| `actions.yaml` | Session 17 | Every action the agent can take, with its risk tier: read, low-risk write or approval-required |
| `approvals.yaml` | Session 25 | Who approves each approval-required action |
| `guardrails.yaml` | Session 28 | Input and output checks and their thresholds |
| `tool_permissions.yaml` | Session 32 | Which role may call which tool |

The risk tiers match the ones printed on every runbook in `data/runbooks/`. Not to be confused with `data/policies/`, which holds the company's IT policy documents that the assistant retrieves.
