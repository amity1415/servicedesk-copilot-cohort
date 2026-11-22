import json

from copilot.ml.train import features, request_text, split_examples, train


def test_labels_and_resolution_cannot_leak_into_features():
    row = {
        "short_description": "Cannot connect",
        "description": "VPN fails",
        "category": "Network & VPN",
        "resolution_notes": "KB-1018",
        "assignment_group": "Network Operations",
    }
    before = request_text(row)
    row.update(category="Security", resolution_notes="ADMIN SECRET", assignment_group="Other")
    assert request_text(row) == before
    assert "KB-1018" not in before


def test_template_groups_do_not_cross_holdout():
    rows = [
        {"short_description": f"Template {i // 3}", "description": "Request"} for i in range(60)
    ]
    train_ids, test_ids = split_examples(rows)
    assert {rows[i]["short_description"] for i in train_ids}.isdisjoint(
        {rows[i]["short_description"] for i in test_ids}
    )


def test_vocabulary_does_not_learn_test_text():
    vectorizer, _, matrix = features(["vpn fails", "device slow"], ["unseenheldouttoken"])
    assert "unseenheldouttoken" not in vectorizer.vocabulary_
    assert matrix.nnz == 0


def test_training_writes_measured_report_on_small_fixture(tmp_path):
    data = tmp_path / "data/tickets"
    data.mkdir(parents=True)
    rows = [
        {
            "short_description": f"request family {i}",
            "description": "vpn network" if i % 2 else "laptop device",
            "category": "Network & VPN" if i % 2 else "Hardware & Devices",
            "priority": "P2" if i % 3 else "P3",
        }
        for i in range(80)
    ]
    (data / "historical_tickets.jsonl").write_text("\n".join(json.dumps(row) for row in rows))
    result = train(tmp_path / "data", tmp_path / "reports")
    assert result["group_overlap"] == 0
    assert result["train"] + result["test"] == 80
    assert set(result["models"]) == {"category:logistic", "priority:logistic"}
    assert (tmp_path / "reports/ml.json").is_file()
    assert all(
        0 <= value["metrics"]["macro avg"]["f1-score"] <= 1 for value in result["models"].values()
    )
