"""Grouped ticket classification experiments with explicit feature boundaries."""

from __future__ import annotations

import json
import time
from pathlib import Path


def read_examples(data: Path) -> list[dict]:
    path = data / "tickets/historical_tickets.jsonl"
    return [
        json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()
    ]


def request_text(row: dict) -> str:
    """Outcome labels, resolution and assignment details never enter X."""
    return row["short_description"] + " " + row["description"]


def split_examples(rows: list[dict], seed: int = 42):
    from sklearn.model_selection import GroupShuffleSplit

    groups = [r["short_description"].lower().strip() for r in rows]
    train_ids, test_ids = next(
        GroupShuffleSplit(n_splits=1, test_size=0.2, random_state=seed).split(rows, groups=groups)
    )
    return train_ids, test_ids


def features(train_text: list[str], test_text: list[str]):
    from sklearn.feature_extraction.text import TfidfVectorizer

    vectorizer = TfidfVectorizer(ngram_range=(1, 2), max_features=12000)
    return vectorizer, vectorizer.fit_transform(train_text), vectorizer.transform(test_text)


def train(data: Path, reports: Path) -> dict:
    from sklearn.cluster import MiniBatchKMeans
    from sklearn.linear_model import LogisticRegression
    from sklearn.metrics import classification_report, confusion_matrix

    rows = read_examples(data)
    train_ids, test_ids = split_examples(rows)
    vectorizer, x_train, x_test = features(
        [request_text(rows[i]) for i in train_ids], [request_text(rows[i]) for i in test_ids]
    )
    groups = [r["short_description"].lower().strip() for r in rows]
    report = {
        "split": "short-description-group holdout",
        "seed": 42,
        "train": len(train_ids),
        "test": len(test_ids),
        "group_overlap": len({groups[i] for i in train_ids} & {groups[i] for i in test_ids}),
        "feature_fields": ["short_description", "description"],
        "models": {},
    }
    for target in ("category", "priority"):
        y_train = [rows[i][target] for i in train_ids]
        y_test = [rows[i][target] for i in test_ids]
        models = {"logistic": LogisticRegression(max_iter=500, random_state=42)}
        for name, model in models.items():
            start = time.monotonic()
            model.fit(x_train, y_train)
            predicted = model.predict(x_test)
            metrics = classification_report(y_test, predicted, output_dict=True, zero_division=0)
            labels = sorted(set(y_test) | set(predicted))
            weakest = min(labels, key=lambda label: metrics[label]["f1-score"])
            report["models"][f"{target}:{name}"] = {
                "metrics": metrics,
                "labels": labels,
                "confusion_matrix": confusion_matrix(y_test, predicted, labels=labels).tolist(),
                "weakest_class": weakest,
                "weakness_hypothesis": (
                    "Inspect support and errors; ambiguous requests, unseen template "
                    "groups or noisy labels may contribute. F1 alone does not identify the cause."
                ),
                "elapsed_s": time.monotonic() - start,
            }
    clusters = MiniBatchKMeans(n_clusters=min(8, len(train_ids)), random_state=42, n_init=3).fit(
        x_train
    )
    terms = vectorizer.get_feature_names_out()
    report["clusters"] = [
        [terms[i] for i in centre.argsort()[-8:][::-1]] for centre in clusters.cluster_centers_
    ]
    reports.mkdir(parents=True, exist_ok=True)
    (reports / "ml.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    return report
