"""Audit the actual corpus with the shared retrieval visibility predicate."""

from copilot.rag.loaders import is_allowed
from copilot.rag.service import documents_from


def verify_metadata(data):
    documents = documents_from(data)
    scopes = {
        f"{role}-{os_name}": {
            doc.id
            for doc in documents
            if is_allowed(doc.metadata, role=role, os_name=os_name, region="APAC")
        }
        for role in ("employee", "analyst")
        for os_name in ("macos", "windows")
    }
    for os_name in ("macos", "windows"):
        employee = scopes[f"employee-{os_name}"]
        analyst = scopes[f"analyst-{os_name}"]
        if not employee < analyst or any(article.startswith("RB-") for article in employee):
            raise RuntimeError("Employee and analyst visibility did not preserve audience policy")
        if "POL-003_v4.0" not in employee or "POL-003_v3.2" in analyst:
            raise RuntimeError("Policy register did not select the current revision")
    if not {"KB-1017"} <= scopes["employee-macos"] - scopes["employee-windows"]:
        raise RuntimeError("The Mac VPN article did not respect the OS filter")
    return {
        "mode": "metadata-visibility-verification",
        "documents": len(documents),
        "scopes": {name: sorted(articles) for name, articles in scopes.items()},
    }
