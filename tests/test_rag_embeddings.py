from copilot.rag.pipeline import Document
from copilot.rag.service import VectorRag


def test_neural_retrieval_preserves_error_code_and_visibility_filters():
    class EqualEmbeddings:
        def encode(self, texts):
            return [[1.0, 0.0] for _ in texts]

    documents = [
        Document("public", "VPN error 809", {"audience": "employee"}, "kb.html", "a"),
        Document("restricted", "VPN error 809", {"audience": "it-staff"}, "runbook.docx", "b"),
        Document("unrelated", "VPN error 806", {"audience": "employee"}, "other.html", "c"),
    ]
    rag = VectorRag(documents, retrieval_encoder=EqualEmbeddings())
    hits = rag.search("VPN error 809", os_name="windows", k=50)
    assert [hit.document_id for hit in hits] == ["public"]
    assert not rag.search("VPN error 987654321", os_name="windows")
    assert rag.answer("VPN error 809", os_name="windows")["mode"] == "neural-vector-extractive"
