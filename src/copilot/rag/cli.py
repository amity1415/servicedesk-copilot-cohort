"""Session-aware RAG commands shared by cumulative projects and the main CLI."""

from __future__ import annotations

import json
import os
from dataclasses import asdict
from pathlib import Path


def register(commands, stage=8):
    demo = commands.add_parser("rag-demo", help="run the actual baseline retrieval pipeline")
    demo.add_argument("--question", default="How do I set up VPN on my Mac?")
    ask = commands.add_parser("rag-ask", help="retrieve and cite authorized source passages")
    ask.add_argument("question")
    ask.add_argument("--os", choices=["macos", "windows", "any"])
    ask.add_argument("--role", choices=["employee", "analyst", "admin"], default="employee")
    if stage >= 6:
        commands.add_parser("rag-ingest", help="ingest all supported sources repeatably")
    if stage >= 7:
        inspect = commands.add_parser("rag-chunks", help="inspect actual chunk text and boundaries")
        inspect.add_argument(
            "--strategy",
            default="recursive",
            choices=(
                ["fixed", "recursive", "semantic", "parent-child"]
                if stage >= 8
                else ["fixed", "recursive"]
            ),
        )
    if stage >= 8:
        commands.add_parser("rag-model-prepare", help="download and pin the public CPU model")
    if stage >= 9:
        commands.add_parser("rag-embedding-compare", help="compare two local embedding models")
        commands.add_parser("rag-embedding-model-prepare", help="prepare the second CPU model")
    if stage >= 10:
        commands.add_parser("rag-postgres-verify", help="verify retrieval in a pgvector database")
    if stage >= 11:
        commands.add_parser("rag-metadata-verify", help="verify retrieval visibility")
    if stage >= 12:
        commands.add_parser("rag-hybrid-compare", help="compare PostgreSQL retrieval rankings")
    if stage >= 13:
        commands.add_parser("rag-reranker-prepare", help="prepare the pinned CPU cross-encoder")
        commands.add_parser("rag-rerank-compare", help="measure reranking recall and p95 latency")
    if stage >= 14:
        commands.add_parser("rag-grounded-verify", help="exercise the offline citation contract")
    if stage >= 15:
        evaluation = commands.add_parser("rag-evaluate", help="compare both local RAG pipelines")
        evaluation.add_argument("--dataset", type=Path, help="evaluation cases in JSON Lines")
    if stage >= 16:
        commands.add_parser("rag-http-verify", help="exercise the local API and Streamlit chat")
    if stage >= 5:
        commands.add_parser("rag-benchmark", help="measure the session's chunking strategies")


def execute(args, settings, stage=8):
    if not args.command.startswith("rag-"):
        return None
    from copilot.rag.service import VectorRag, baseline_directory, benchmark, documents_from

    reports = Path(os.getenv("COHORT_REPORT_DIR", "reports/integrated/rag"))
    reports.mkdir(parents=True, exist_ok=True)
    data = settings.data_dir
    if args.command == "rag-model-prepare":
        from copilot.rag.semantic_encoder import prepare_model

        result = prepare_model()
    elif args.command == "rag-embedding-model-prepare":
        from copilot.rag.semantic_encoder import model_directory, prepare_model

        pin = Path(__file__).resolve().parents[3] / "policies/embedding_model_l12.json"
        if not pin.is_file():
            raise FileNotFoundError(pin)
        result = prepare_model(model_directory().with_name("minilm-l12"), pin)
    elif args.command == "rag-embedding-compare":
        from copilot.rag.embedding_benchmark import compare_embeddings

        result = compare_embeddings(data)
    elif args.command == "rag-postgres-verify":
        from copilot.rag.postgres_benchmark import verify_postgres

        result = verify_postgres(data, settings.database_url.get_secret_value())
    elif args.command == "rag-metadata-verify":
        from copilot.rag.metadata_report import verify_metadata

        result = verify_metadata(data)
    elif args.command == "rag-hybrid-compare":
        from copilot.rag.hybrid_benchmark import compare_hybrid

        result = compare_hybrid(data)
    elif args.command == "rag-reranker-prepare":
        from copilot.rag.reranker import prepare_reranker

        result = prepare_reranker()
    elif args.command == "rag-rerank-compare":
        from copilot.rag.reranker_benchmark import compare_reranker

        result = compare_reranker(data)
    elif args.command == "rag-grounded-verify":
        from copilot.rag.grounded_fixture import verify_grounded_fixture

        result = verify_grounded_fixture(data)
    elif args.command == "rag-evaluate":
        from copilot.rag.evaluation import dataset_path, evaluate

        result = evaluate(data, args.dataset or dataset_path(data))
    elif args.command == "rag-http-verify":
        from copilot.api.verify import verify_http_service

        result = verify_http_service(data)
    elif args.command == "rag-ingest":
        from copilot.rag.loaders import ingest

        output = reports / "documents.json"
        first = ingest(data, output)
        second = ingest(data, output)
        if first["skipped"] or second["changed"]:
            raise RuntimeError("ingestion skipped sources or was not idempotent")
        result = {"first": first, "repeat": second}
    elif args.command == "rag-chunks":
        from copilot.rag.chunking import make_chunks

        encoder = None
        if args.strategy == "semantic":
            from copilot.rag.semantic_encoder import OnnxEncoder

            encoder = OnnxEncoder()
        documents = documents_from(data)
        parts = [c for doc in documents for c in make_chunks(doc, args.strategy, encoder=encoder)]
        (reports / "chunks.jsonl").write_text(
            "".join(json.dumps(asdict(c)) + "\n" for c in parts), encoding="utf-8"
        )
        result = {
            "documents": len(documents),
            "chunks": len(parts),
            "strategy": args.strategy,
            "inspection": str(reports / "chunks.jsonl"),
        }
    elif args.command == "rag-benchmark":
        strategies = ["fixed"] if stage <= 6 else ["fixed", "recursive"]
        encoder = None
        if stage >= 8:
            from copilot.rag.semantic_encoder import OnnxEncoder

            encoder = OnnxEncoder()
            strategies.extend(["semantic", "parent-child"])
        result = benchmark(data, strategies, baseline=stage == 5, encoder=encoder)
    else:
        strategy = "fixed" if stage <= 6 else "recursive"
        rag = VectorRag.from_data(data, strategy, baseline=stage == 5)
        question = args.question
        os_name = getattr(args, "os", None) or ("macos" if "mac" in question.lower() else None)
        result = rag.answer(question, role=getattr(args, "role", "employee"), os_name=os_name)
        if args.command == "rag-demo":
            result["document_count"] = len(rag.documents)
            result["question_file"] = str(baseline_directory(data) / "questions.jsonl")
            result["bare_model_comparison"] = "not run; no paid provider called"
    output = reports / f"{args.command}.json"
    output.write_text(json.dumps(result, indent=2), encoding="utf-8")
    if args.command in {"rag-ask", "rag-demo"}:
        print(json.dumps(result, indent=2))
    elif args.command == "rag-evaluate":
        print(json.dumps({"report": str(output), "splits": result["splits"]}, indent=2))
    else:
        print(
            json.dumps(
                {
                    "command": args.command,
                    "report": str(output),
                    "mode": result.get("mode"),
                    "strategies": list(result.get("strategies", {})),
                }
            )
        )
    return 0
