# 0001. One use case for the whole program: an IT Service Desk Copilot

- Status: accepted
- Date: 2026-11-15
- Session: 1

## Context

The program builds one enterprise use case from the RAG module to the end, with no separate capstone. The use case has to give every syllabus topic real work to do: private documents to retrieve from, a system of record to query, a ticketing system to act on, actions risky enough to need approval, and historical data to evaluate against.

## Options

| Option | Fits the three systems named for MCP | Domain knowledge learners need | Data to prepare |
| --- | --- | --- | --- |
| IT service desk copilot | Yes: documents, database, ticketing | None | Moderate |
| Motor insurance claims copilot | Yes, with a case system as ticketing | A primer on deductibles and exclusions | Large |
| Customer support, procurement, plant maintenance | Yes | Some | Moderate to large |

## Decision

Build the IT Service Desk Copilot for a fictional company, Larkhaven Group, on fully synthetic data.

## Consequences

- Learners need no domain training, and the data can be shared freely.
- Six acceptance requests define done; `data/personas.md` fixes the people and devices behind them.
- The synthetic knowledge base is cleaner than a real one. The data pack adds deliberate rough edges, listed in `data/README.md`, to compensate.
- The same shape works for the other domains, so the repository layout can be reused if the domain changes.
