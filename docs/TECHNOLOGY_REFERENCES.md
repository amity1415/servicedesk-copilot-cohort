# SDK and protocol references

Checked during implementation on 17 November 2026. Dependency ranges deliberately
bound major versions. Update examples and run contract tests before upgrading.

- [MCP Python SDK v1 documentation](https://py.sdk.modelcontextprotocol.io/v1/)
  and [v1 branch README](https://github.com/modelcontextprotocol/python-sdk/tree/v1.x).
  This project uses `FastMCP` from the supported v1 line, bounded by `<2`.
  Current v2 examples use a different server class; do not mix those imports.
- [A2A Python SDK](https://github.com/a2aproject/a2a-python).
  The HR reference uses AgentExecutor, TaskUpdater, DefaultRequestHandler and
  A2AStarletteApplication from the installed 0.3 SDK.
- [LangGraph persistence](https://docs.langchain.com/oss/python/langgraph/persistence)
  and [PostgresSaver setup](https://reference.langchain.com/python/langgraph/checkpoint/postgres/PostgresSaver/setup).
  Keep the saver context open for the graph's full serving lifetime.

Local validation uses actual installed SDKs. It does not claim compatibility with
arbitrary future releases or a deployed remote partner.
