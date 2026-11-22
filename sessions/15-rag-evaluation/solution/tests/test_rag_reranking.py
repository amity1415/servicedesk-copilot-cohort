from copilot.rag.pipeline import Document
from copilot.rag.service import VectorRag


def test_reranking_only_sees_thirty_authorized_candidates_and_preserves_current_ids():
    from copilot.rag.query import rewrite

    assert "809" in rewrite("Same problem", "Windows VPN error 809")
    mac_question = "How do I set up VPN on my Mac?"
    assert rewrite("I still have the same problem.", mac_question) == rewrite(mac_question)
    new_query = rewrite("Still seeing 806", "Windows VPN error 809")
    assert "806" in new_query and "809" not in new_query
    assert "multi-factor authentication MFA" in rewrite("mfa setup")

    class Encoder:
        def encode(self, texts):
            return [[1.0, 0.0] for _ in texts]

    class Index:
        def publish(self, chunks, texts, encoder):
            return "generation"

        def search(self, generation, ids, vector, limit):
            return [(item, 1.0) for item in ids[:limit]]

        def keyword(self, generation, ids, query, limit):
            return [(item, 1.0) for item in ids[:limit]]

    class Reranker:
        def rank(self, query, chunks):
            assert len(chunks) == 30
            assert all(chunk.metadata["audience"] == "employee" for chunk in chunks)
            return list(reversed(chunks))

    docs = [
        Document(str(i), f"Public VPN instructions {i}", {"audience": "employee"}, "kb.md", str(i))
        for i in range(36)
    ]
    docs.insert(0, Document("private", "Restricted VPN", {"audience": "it-staff"}, "rb.md", "x"))
    rag = VectorRag(
        docs,
        retrieval_encoder=Encoder(),
        persistent_index=Index(),
        hybrid=True,
        reranker=Reranker(),
    )
    assert [hit.document_id for hit in rag.search("VPN")] == ["29", "28", "27", "26", "25"]
