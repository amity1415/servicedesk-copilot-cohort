"""Run foundation features through the integrated application, not a session launcher."""

import json
from pathlib import Path


def register(commands):
    commands.add_parser("train", help="train the integrated classical ticket baseline")
    commands.add_parser("compare", help="compare integrated logistic and MLP classifiers")
    token = commands.add_parser("token-report", help="measure the named tokenizer")
    token.add_argument("--encoding", default="cl100k_base")
    token.add_argument("--input-price-per-million", type=float)
    token.add_argument("--output-price-per-million", type=float)
    commands.add_parser("llm-smoke", help="exercise integrated inference with a mock transport")


def execute(args, settings, reports: Path):
    if args.command in {"train", "compare"}:
        from copilot.ml.train import train

        result = train(settings.data_dir, reports, neural=args.command == "compare")
        print(
            json.dumps(
                {
                    "mode": "integrated-application",
                    "report": str(reports / "ml.json"),
                    "models": list(result["models"]),
                    "test_rows": result["test"],
                }
            )
        )
        return 0
    if args.command == "token-report":
        from copilot.ml.token_report import measure

        result = measure(
            settings.data_dir,
            reports,
            encoding_name=args.encoding,
            input_price_per_million=args.input_price_per_million,
            output_price_per_million=args.output_price_per_million,
        )
        print(
            json.dumps(
                {
                    "mode": "integrated-application",
                    "encoding": result["encoding"],
                    "report": str(reports / "tokens.json"),
                }
            )
        )
        return 0
    if args.command == "llm-smoke":
        import httpx

        from copilot.llm.classify import classify
        from copilot.llm.client import ModelClient

        def response(request):
            payload = {
                "category": "Hardware & Devices",
                "priority": "P3",
                "summary": "Laptop is slow",
            }
            return httpx.Response(
                200,
                json={
                    "choices": [{"message": {"content": json.dumps(payload)}}],
                    "usage": {"total_tokens": 20},
                },
            )

        client = ModelClient(
            "fixture",
            base_url="http://fixture.local/v1",
            api_key="fixture",
            transport=httpx.MockTransport(response),
        )
        result = classify(client, "My laptop is slow")
        reports.mkdir(parents=True, exist_ok=True)
        report = {
            "mode": "integrated-offline-fixture",
            "paid_calls": 0,
            "classification": result.model_dump(),
            "live_accuracy": None,
        }
        (reports / "llm-smoke.json").write_text(json.dumps(report, indent=2))
        print(json.dumps(report))
        return 0
    return None
