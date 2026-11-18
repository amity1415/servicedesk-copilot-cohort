# Confirmed implementation choices

Confirmed by the instructor on 18 November 2026:

- Git hosting: GitHub owner amity1415. Selected repository name servicedesk-copilot-cohort, private. The repository has not been created/pushed because the GitHub connection is not installed yet.
- Model provider: OpenAI. The instructor will configure an API key locally; no secret is requested in chat.
- Build/deployment environment: local Docker Desktop and the existing local Jenkins installation.
- Ports: Jenkins 8080, Copilot API 8082, chat UI 8501.

We continue with local-only Git checkpoints and offline provider fixtures. Paid calls
remain disabled in session checks. A live evaluation needs an explicit model,
request/token ceiling and configured spending guard before it runs. Provider key
configuration belongs only in the ignored `.env` or a scoped Jenkins credential.

The first implementation batch supplies real cumulative starter/solution code for
sessions 01–04. The next batch is baseline RAG plus trusted ingestion/chunking
for sessions 05–08. Docker engine/Jenkins agent configuration are verified separately
before container or CI deployment work, rather than inferred from their installation.

The instructor was advised to rotate the key exposed in chat. That key was not written to project files or used for paid requests. A replacement should be configured locally, never committed.

## 2026-11-18: instructor-authorized RAG batch

Build sessions 05–08 together, then validate the complete batch before marking it
complete. Keep session 04 live acceptance pending. Preserve per-session cumulative
Git tags and explicit evidence. Use recursive chunking by default: it tied fixed
Recall@5 with fewer chunks on draft labels; semantic complexity did not improve it.
