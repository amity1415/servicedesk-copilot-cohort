import pytest

from copilot.cli import main


@pytest.mark.parametrize("command,neural", [("train", False), ("compare", True)])
def test_main_cli_invokes_integrated_training(monkeypatch, tmp_path, command, neural):
    calls = []

    def train(data, reports, neural=False):
        calls.append(neural)
        return {"models": {}, "test": 10}

    monkeypatch.setattr("copilot.ml.train.train", train)
    monkeypatch.chdir(tmp_path)
    assert main([command]) == 0
    assert calls == [neural]


def test_main_cli_token_report_forwards_explicit_prices(monkeypatch, tmp_path):
    calls = []

    def measure(data, reports, **kwargs):
        calls.append(kwargs)
        return {"encoding": kwargs["encoding_name"]}

    monkeypatch.setattr("copilot.ml.token_report.measure", measure)
    monkeypatch.chdir(tmp_path)
    assert (
        main(
            [
                "token-report",
                "--encoding",
                "o200k_base",
                "--input-price-per-million",
                "0.4",
                "--output-price-per-million",
                "1.6",
            ]
        )
        == 0
    )
    assert calls[0]["input_price_per_million"] == 0.4
    assert calls[0]["output_price_per_million"] == 1.6
