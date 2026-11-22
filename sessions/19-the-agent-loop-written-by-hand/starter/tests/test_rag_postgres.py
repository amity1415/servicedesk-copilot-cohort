from copilot.rag.pipeline import Document
from copilot.rag.service import VectorRag


def test_pgvector_receives_only_authorized_matching_chunks():
    class Encoder:
        def encode(self, texts):
            return [[1.0, 0.0] for _ in texts]

    class Index:
        def publish(self, chunks, texts, encoder):
            assert len(chunks) == len(texts) == 3
            return "generation"

        def search(self, generation, allowed_ids, vector, limit):
            assert generation == "generation"
            assert vector == [1.0, 0.0]
            assert len(allowed_ids) == 1
            return [(allowed_ids[0], 1.0)]

    documents = [
        Document("public", "VPN error 809", {"audience": "employee"}, "kb.html", "a"),
        Document("restricted", "VPN error 809", {"audience": "it-staff"}, "runbook.docx", "b"),
        Document("unrelated", "VPN error 806", {"audience": "employee"}, "other.html", "c"),
    ]
    rag = VectorRag(documents, retrieval_encoder=Encoder(), persistent_index=Index())
    answer = rag.answer("VPN error 809")
    assert answer["mode"] == "pgvector-extractive"
    assert [citation["document_id"] for citation in answer["citations"]] == ["public"]
