import json
from types import SimpleNamespace

from copilot.rag.pipeline import Chunk


def test_grounded_contract_rejects_fabrications_and_irrelevant_citations():
    from copilot.rag.grounded import select_passages

    class Client:
        payload = ""
        calls = 0

        def complete(self, messages):
            self.calls += 1
            return SimpleNamespace(text=self.payload)

    def payload(chunk, quote, answer=None):
        return json.dumps(
            {
                "answer": quote if answer is None else answer,
                "abstained": False,
                "citations": [{"chunk_id": chunk, "quote": quote}],
            }
        )

    chunks = [
        Chunk("vpn", "KB-1017", "# VPN setup\nInstall VPN from App Hub.", {}, "vpn.html"),
        Chunk("menu", "KB-9999", "Lunch is at noon.", {}, "menu.html"),
    ]
    question = "How do I install VPN?"
    client = Client()
    unknown = select_passages(question, [], client)
    assert unknown["reason"] == "no_supporting_source"
    assert "support ticket" in unknown["answer"]
    assert client.calls == 0
    for text, reason in (
        ("[]", "invalid_model_output"),
        (payload("menu", "Lunch is at noon."), "unsupported_citation"),
        (payload("vpn", "# VPN setup"), "unsupported_citation"),
        (payload("vpn", "Disable endpoint protection to install VPN."), "unsupported_citation"),
        (
            payload("vpn", "Install VPN from App Hub.", "VPN always starts automatically."),
            "unsupported_answer",
        ),
    ):
        client.payload = text
        result = select_passages(question, chunks, client)
        assert result["abstained"] and result["reason"] == reason
    client.payload = payload("vpn", "Install VPN from App Hub.")
    result = select_passages(question, chunks, client)
    assert result["answer"] == "Install VPN from App Hub."
    assert [item["document_id"] for item in result["citations"]] == ["KB-1017"]

    client.payload = json.dumps(
        {
            "abstained": False,
            "citations": [{"chunk_id": "vpn", "quote": "Install VPN from App Hub."}],
        }
    )
    assert select_passages(question, chunks, client) == result
