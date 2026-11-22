# Confirmed implementation choices

Confirmed by the instructor on 18 November 2026:

- Git hosting: the selected destination is the private GitHub repository
  `amity1415/servicedesk-copilot-cohort`. It was created on 22 November 2026.
  The workspace tracks it as `origin`, and authenticated Git access was verified
  before the first push.
- Model provider: OpenAI. The instructor will configure an API key locally; no secret is requested in chat.
- Build/deployment environment: local Docker Desktop and the existing local Jenkins installation.
- Ports: Jenkins 8080, Copilot API 8082, chat UI 8501.

Routine session checks use offline provider fixtures. A live evaluation uses an
explicit model ID and request, token and spend ceilings.
Provider key configuration belongs in the ignored `.env` or a scoped Jenkins
credential.

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

## 2026-11-22: publish each completed session

For each remaining session, complete its dependencies and run the standalone
acceptance checks and integrated application regression suite. Commit the verified
implementation and evidence, push to the private GitHub repository, and confirm the
remote branch contains the completion commit before beginning the next session.

## 2026-11-22, Session 14 model and budget

Use GPT-6 Luna (`gpt-6-luna`) for grounded passage selection. Request JSON
output with reasoning disabled and the standard processing tier. Record the
provider's returned model ID in the live evidence. The application uses the
published ID, which is currently undated.
[GPT-6 Luna](https://developers.openai.com/api/docs/models/gpt-6-luna)

Keep each live run to two requests and a 7,000-input-token ceiling per question.
The first run also capped output at 400 tokens. Both replies hit that cap and
failed validation, with an estimated cost of $0.00067 across the two requests.
The revised prompt returns only the excerpts and abstention status. The app
assembles the display answer. At a 550-output-token ceiling, the retry reserves
$0.00230 for both calls. The input calculation uses the published $0.125
cache-write rate for the full token allowance. The output rate is $0.50 per
million tokens. Recheck these rates when budgeting a later session.
[OpenAI pricing](https://developers.openai.com/api/docs/pricing)
