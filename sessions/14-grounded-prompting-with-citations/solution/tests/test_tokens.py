import json

import pytest

from copilot.ml.token_report import measure


class ByteEncoding:
    def encode(self, text):
        return list(text.encode("ascii"))

    def decode(self, ids):
        return bytes(ids).decode("ascii")


def test_cost_stays_unknown_without_explicit_prices(tmp_path):
    (tmp_path / "tickets").mkdir()
    (tmp_path / "kb").mkdir()
    row = {"short_description": "VPN", "description": "error 809"}
    (tmp_path / "tickets/historical_tickets.jsonl").write_text(json.dumps(row) + "\n")
    report = measure(
        tmp_path, tmp_path / "reports", encoding=ByteEncoding(), encoding_name="fixture-ascii"
    )
    assert report["tickets"]["count"] == 1
    assert report["cost_estimate"] is None
    assert report["identifier_examples"]["KB-1018"]["token_ids"] == list(b"KB-1018")


def test_partial_or_negative_prices_are_rejected(tmp_path):
    with pytest.raises(ValueError):
        measure(tmp_path, tmp_path, input_price_per_million=1)
    with pytest.raises(ValueError):
        measure(tmp_path, tmp_path, input_price_per_million=-1, output_price_per_million=1)


def test_neural_comparison_fits_both_targets(tmp_path):
    from copilot.ml.train import train

    data = tmp_path / "data/tickets"
    data.mkdir(parents=True)
    rows = [
        {
            "short_description": f"family {i}",
            "description": "vpn network" if i % 2 else "slow laptop",
            "category": "Network & VPN" if i % 2 else "Hardware & Devices",
            "priority": "P2" if i % 3 else "P3",
        }
        for i in range(80)
    ]
    (data / "historical_tickets.jsonl").write_text("\n".join(json.dumps(row) for row in rows))
    result = train(tmp_path / "data", tmp_path / "reports", neural=True)
    assert set(result["models"]) == {
        "category:logistic",
        "priority:logistic",
        "category:mlp",
        "priority:mlp",
    }
    assert all("confusion_matrix" in value for value in result["models"].values())
