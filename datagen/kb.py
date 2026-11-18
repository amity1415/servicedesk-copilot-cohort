"""Turn topics into knowledge-base articles and write them as Markdown or HTML.

Two formats on purpose: Markdown files carry their metadata as YAML front
matter, HTML files carry it in <meta> tags and wrap the article in the portal's
navigation and footer, which a parser has to strip (session 6).
"""

from __future__ import annotations

import csv
import html
import json
import random
from dataclasses import dataclass
from datetime import date, timedelta
from pathlib import Path

from datagen.company import AS_OF, OS_LABELS, REGIONS
from datagen.content import TOPICS
from datagen.content.policies import CURRENT as CURRENT_POLICIES
from datagen.model import Topic

FIRST_ID = 1001
OS_TITLE_SUFFIX = {
    "windows": " on Windows",
    "macos": " on macOS",
    "ios": " on iPhone and iPad",
    "android": " on Android",
}
STEPS_HEADING = {"how-to": "Steps", "troubleshooting": "Resolution", "reference": "Key points"}
AUDIENCE_LABEL = {"employee": "All employees", "it-staff": "IT staff only"}
POLICY_TITLES = {policy.id: policy.title for policy in CURRENT_POLICIES}


@dataclass(frozen=True)
class Article:
    id: str
    topic: Topic
    os: str  # windows | macos | ios | android | any
    region: str  # global | AMER | EMEA | APAC
    title: str
    summary: str
    steps: tuple[str, ...]
    symptoms: tuple[str, ...]
    causes: tuple[str, ...]
    notes: tuple[str, ...]
    version: str
    effective_date: date
    last_reviewed: date
    fmt: str  # md | html

    @property
    def filename(self) -> str:
        # Named by ID only, as a knowledge-base export would be. Short names also keep
        # paths inside the Windows 260-character limit when the repository sits deep.
        return f"{self.id}.{self.fmt}"

    @property
    def metadata(self) -> dict[str, object]:
        """The fields a retriever filters on. Same keys in both file formats."""
        return {
            "id": self.id,
            "title": self.title,
            "type": self.topic.kind,
            "system": self.topic.system,
            "category": self.topic.category,
            "subcategory": self.topic.subcategory,
            "os": self.os,
            "region": self.region,
            "audience": self.topic.audience,
            "version": self.version,
            "effective_date": self.effective_date.isoformat(),
            "last_reviewed": self.last_reviewed.isoformat(),
            "owner": self.topic.group,
            "status": "current",
            "error_codes": list(self.topic.codes),
            "related_policy": self.topic.policy,
        }


def _region_fields(region_code: str) -> dict[str, str]:
    region = REGIONS[region_code]
    return {
        "region_name": region.name,
        "support_hours": region.support_hours,
        "phone": region.phone,
        "tech_bar": region.tech_bar,
        "guest_ssid": region.guest_ssid,
        "printer_queue": region.printer_queue,
        "room_panel": region.room_panel,
    }


def build_articles(seed: int) -> list[Article]:
    """One article per operating system or per region of each topic, in a stable order."""
    rng = random.Random(f"{seed}:kb")
    articles: list[Article] = []

    def add(topic: Topic, os_name: str, region: str, title: str, fill: dict[str, str] | None):
        def text(value: str) -> str:
            return value.format_map(fill) if fill else value

        number = FIRST_ID + len(articles)
        effective = date(2025, 1, 6) + timedelta(days=rng.randrange(0, 640))
        reviewed = min(AS_OF, effective + timedelta(days=rng.randrange(0, 75)))
        articles.append(
            Article(
                id=f"KB-{number}",
                topic=topic,
                os=os_name,
                region=region,
                title=text(title),
                summary=text(topic.summary),
                steps=tuple(text(step) for step in topic.steps[os_name]),
                symptoms=tuple(text(item) for item in topic.symptoms),
                causes=tuple(text(item) for item in topic.causes),
                notes=tuple(text(item) for item in topic.notes),
                version=f"{rng.randint(1, 3)}.{rng.randint(0, 4)}",
                effective_date=effective,
                last_reviewed=reviewed,
                fmt="html" if number % 3 == 0 else "md",
            )
        )

    for topic in TOPICS:
        if topic.by_region:
            for code, region in REGIONS.items():
                add(topic, "any", code, f"{topic.title} ({region.name})", _region_fields(code))
        else:
            several = len(topic.steps) > 1
            for os_name in topic.steps:
                suffix = OS_TITLE_SUFFIX[os_name] if several else ""
                add(topic, os_name, "global", topic.title + suffix, None)
    return articles


def find_article(
    articles: list[Article], topic_key: str, os_name: str, region: str
) -> Article | None:
    """The article a given employee would be sent for a topic."""
    candidates = [article for article in articles if article.topic.key == topic_key]
    if not candidates:
        return None
    for article in candidates:
        if article.region == region or article.os == os_name:
            return article
    return candidates[0]


def _applies_to(article: Article) -> str:
    os_label = "Any operating system" if article.os == "any" else OS_LABELS[article.os]
    region = "All regions" if article.region == "global" else REGIONS[article.region].name
    return f"{os_label} | {region} | {AUDIENCE_LABEL[article.topic.audience]}"


def _closing(article: Article) -> str | None:
    topic = article.topic
    if topic.kind == "reference":
        return None
    if topic.audience == "it-staff":
        return f"Escalate to the {topic.group} lead and record what you have already checked."
    return (
        f"Raise a ticket in HelpHub under {topic.category}, {topic.subcategory}. "
        f"It is handled by {topic.group}. Include the exact error message and your asset tag."
    )


def _policy_line(article: Article) -> str | None:
    policy_id = article.topic.policy
    if not policy_id:
        return None
    return f"Related policy: {policy_id} {POLICY_TITLES[policy_id]}."


def render_markdown(article: Article) -> str:
    lines = ["---"]
    for key, value in article.metadata.items():
        lines.append(f"{key}: {json.dumps(value)}")
    lines += ["---", "", f"# {article.title}", "", article.summary, ""]
    lines += [f"**Applies to:** {_applies_to(article)}", ""]
    if article.symptoms:
        lines += ["## Symptoms", ""] + [f"- {item}" for item in article.symptoms] + [""]
    if article.causes:
        lines += ["## Likely causes", ""] + [f"- {item}" for item in article.causes] + [""]
    lines += [f"## {STEPS_HEADING[article.topic.kind]}", ""]
    if article.topic.kind == "reference":
        lines += [f"- {step}" for step in article.steps]
    else:
        lines += [f"{number}. {step}" for number, step in enumerate(article.steps, start=1)]
    lines.append("")
    if article.notes:
        lines += ["## Good to know", ""] + [f"- {item}" for item in article.notes] + [""]
    closing = _closing(article)
    if closing:
        lines += ["## Still not working?", "", closing, ""]
    policy = _policy_line(article)
    if policy:
        lines += [f"*{policy}*", ""]
    return "\n".join(lines)


def render_html(article: Article) -> str:
    esc = html.escape
    meta = "\n".join(
        f'  <meta name="kb:{key}" content="{esc(json.dumps(value) if isinstance(value, list) else str(value or ""))}">'
        for key, value in article.metadata.items()
    )

    def bullet_list(items: tuple[str, ...], ordered: bool = False) -> str:
        tag = "ol" if ordered else "ul"
        rows = "\n".join(f"        <li>{esc(item)}</li>" for item in items)
        return f"      <{tag}>\n{rows}\n      </{tag}>"

    body = [f"      <h1>{esc(article.title)}</h1>"]
    body.append(f'      <p class="summary">{esc(article.summary)}</p>')
    body.append(
        f'      <p class="applies"><strong>Applies to:</strong> {esc(_applies_to(article))}</p>'
    )
    if article.symptoms:
        body += ["      <h2>Symptoms</h2>", bullet_list(article.symptoms)]
    if article.causes:
        body += ["      <h2>Likely causes</h2>", bullet_list(article.causes)]
    body.append(f"      <h2>{STEPS_HEADING[article.topic.kind]}</h2>")
    body.append(bullet_list(article.steps, ordered=article.topic.kind != "reference"))
    if article.notes:
        body += ["      <h2>Good to know</h2>", bullet_list(article.notes)]
    closing = _closing(article)
    if closing:
        body += ["      <h2>Still not working?</h2>", f"      <p>{esc(closing)}</p>"]
    policy = _policy_line(article)
    if policy:
        body.append(f'      <p class="policy"><em>{esc(policy)}</em></p>')
    article_html = "\n".join(body)

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>{esc(article.title)} | HelpHub Knowledge Base</title>
{meta}
  <link rel="stylesheet" href="/assets/helphub.css">
</head>
<body>
  <header class="site-header">
    <a class="logo" href="/">HelpHub</a>
    <nav>
      <a href="/kb">Knowledge base</a>
      <a href="/requests">My requests</a>
      <a href="/status">Service status</a>
      <a href="/contact">Contact the service desk</a>
    </nav>
    <form class="search" action="/kb/search"><input name="q" placeholder="Search the knowledge base"></form>
  </header>
  <nav class="breadcrumb">
    <a href="/kb">Knowledge base</a> &gt; <a href="/kb/c">{esc(article.topic.category)}</a> &gt; {esc(article.topic.subcategory)}
  </nav>
  <main>
    <article id="{article.id}">
{article_html}
    </article>
    <aside class="feedback">
      <p>Was this article helpful?</p>
      <button type="button">Yes</button> <button type="button">No</button>
      <p class="views">Viewed 0 times in the last 30 days</p>
    </aside>
  </main>
  <footer class="site-footer">
    <p>{article.id} | Version {article.version} | Last reviewed {article.last_reviewed.isoformat()} | Owner: {esc(article.topic.group)}</p>
    <p>Larkhaven Group internal use only. Do not share outside the company.</p>
    <p><a href="/privacy">Privacy</a> | <a href="/accessibility">Accessibility</a> | <a href="/kb/feedback">Suggest an article</a></p>
  </footer>
</body>
</html>
"""


def write_articles(articles: list[Article], out_dir: Path) -> None:
    """Write one file per article plus index.csv, which maps IDs to titles for people."""
    out_dir.mkdir(parents=True, exist_ok=True)
    for article in articles:
        text = render_html(article) if article.fmt == "html" else render_markdown(article)
        (out_dir / article.filename).write_text(text, encoding="utf-8", newline="\n")
    with (out_dir / "index.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(["id", "title", "file"])
        for article in articles:
            writer.writerow([article.id, article.title, article.filename])
