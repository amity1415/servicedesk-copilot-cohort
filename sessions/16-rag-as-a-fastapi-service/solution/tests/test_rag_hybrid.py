from copilot.rag.pipeline import Document
from copilot.rag.service import VectorRag


def test_hybrid_shares_authorized_candidates_and_deduplicates_ranks():
    class Encoder:
        def encode(self, texts):
            return [[1.0, 0.0] for _ in texts]

    class Index:
        vectors = None
        keywords = None

        def publish(self, chunks, texts, encoder):
            return "generation"

        def search(self, generation, ids, vector, limit):
            self.vectors = ids
            return [(item, 1.0) for item in ids]

        def keyword(self, generation, ids, query, limit):
            self.keywords = ids
            return [(item, 1.0) for item in ids]

    index = Index()
    docs = [
        Document("public", "VPN error 809", {"audience": "employee"}, "kb.html", "a"),
        Document("restricted", "VPN error 809", {"audience": "it-staff"}, "runbook.docx", "b"),
        Document("different-code", "VPN error 806", {"audience": "employee"}, "other.html", "c"),
    ]
    rag = VectorRag(docs, retrieval_encoder=Encoder(), persistent_index=index, hybrid=True)
    answer = rag.answer("VPN error 809")
    assert index.vectors == index.keywords and len(index.vectors) == 1
    assert answer["mode"] == "hybrid-extractive"
    assert [citation["document_id"] for citation in answer["citations"]] == ["public"]
