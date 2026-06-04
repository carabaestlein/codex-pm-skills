#!/usr/bin/env python3
"""Run the daily intel email workflow.

The script collects configured source pages, asks OpenAI for a PM-oriented digest
when credentials are available, and can optionally send the result by email.
"""

from __future__ import annotations

import argparse
import datetime as dt
import email.message
import html
import html.parser
import os
import re
import smtplib
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional
from urllib.parse import urlparse
from urllib.request import Request, urlopen

import yaml

try:
    import feedparser
except ImportError:  # Feed parsing falls back to the standard library.
    feedparser = None


DEFAULT_TIMEOUT_SECONDS = 20
USER_AGENT = "codex-pm-skills/0.1 (+https://github.com)"
REPO_ROOT = Path(__file__).resolve().parents[2]


@dataclass
class SourceItem:
    label: str
    url: str
    owner: str
    owner_type: str
    title: str
    summary: str
    published: Optional[str] = None


class SimpleHTMLExtractor(html.parser.HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.title_parts: list[str] = []
        self.heading_parts: list[str] = []
        self.paragraph_parts: list[str] = []
        self._tag_stack: list[str] = []
        self._skip_depth = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, Optional[str]]]) -> None:
        if tag in {"script", "style", "nav", "footer", "header"}:
            self._skip_depth += 1
        self._tag_stack.append(tag)

    def handle_endtag(self, tag: str) -> None:
        if tag in {"script", "style", "nav", "footer", "header"} and self._skip_depth:
            self._skip_depth -= 1
        if self._tag_stack:
            self._tag_stack.pop()

    def handle_data(self, data: str) -> None:
        if self._skip_depth:
            return
        tag = self._tag_stack[-1] if self._tag_stack else ""
        text = clean_text(data)
        if not text:
            return
        if tag == "title":
            self.title_parts.append(text)
        elif tag in {"h1", "h2", "h3"}:
            self.heading_parts.append(text)
        elif tag == "p":
            self.paragraph_parts.append(text)


def load_yaml(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"Config must be a YAML mapping: {path}")
    return data


def load_config(path: Path) -> dict[str, Any]:
    workflow_config = load_yaml(path)
    global_config_path = resolve_global_config_path(path, workflow_config)
    if global_config_path and global_config_path.exists():
        merged = deep_merge(load_yaml(global_config_path), workflow_config)
    else:
        merged = workflow_config
    return normalize_config(merged)


def resolve_global_config_path(workflow_path: Path, workflow_config: dict[str, Any]) -> Optional[Path]:
    configured = workflow_config.get("global_config")
    if configured:
        candidate = Path(str(configured)).expanduser()
        if not candidate.is_absolute():
            candidate = REPO_ROOT / candidate
        if not candidate.exists() and candidate.name == "config.local.yaml":
            example = candidate.with_name("config.example.yaml")
            if example.exists():
                return example
        return candidate

    default_local = REPO_ROOT / "config.local.yaml"
    if default_local.exists():
        return default_local
    default_example = REPO_ROOT / "config.example.yaml"
    if default_example.exists():
        return default_example
    return None


def deep_merge(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    merged = dict(base)
    for key, value in override.items():
        if isinstance(value, dict) and isinstance(merged.get(key), dict):
            merged[key] = deep_merge(merged[key], value)
        else:
            merged[key] = value
    return merged


def normalize_config(config: dict[str, Any]) -> dict[str, Any]:
    product = config.get("product", {}) or {}
    audience = config.get("audience", {}) or {}
    positioning = config.get("positioning", {}) or {}

    company = dict(config.get("company", {}) or {})
    company.setdefault("name", product.get("name"))
    company.setdefault("category", product.get("category"))
    if product.get("name") and not company.get("product"):
        company["product"] = product.get("name")

    icp = company.get("icp")
    if not icp:
        inferred_icp = []
        if audience.get("primary_icp"):
            inferred_icp.append(audience["primary_icp"])
        inferred_icp.extend(audience.get("personas", []) or [])
        if inferred_icp:
            company["icp"] = inferred_icp

    if company:
        config["company"] = company
    if not config.get("themes") and positioning.get("themes"):
        config["themes"] = positioning["themes"]
    return config


def collect_sources(config: dict[str, Any], limit_per_source: int) -> list[SourceItem]:
    items: list[SourceItem] = []

    for competitor in config.get("competitors", []) or []:
        owner = competitor.get("name", "Unknown competitor")
        for source in competitor.get("sources", []) or []:
            items.extend(fetch_source(source, owner, "competitor", limit_per_source))

    for source in config.get("market_sources", []) or []:
        owner = source.get("label", "Market source")
        items.extend(fetch_source(source, owner, "market", limit_per_source))

    return dedupe_items(items)


def fetch_source(
    source: dict[str, Any],
    owner: str,
    owner_type: str,
    limit: int,
) -> list[SourceItem]:
    label = str(source.get("label") or owner)
    url = str(source.get("url") or "").strip()
    if not url:
        return []

    try:
        request = Request(url, headers={"User-Agent": USER_AGENT})
        with urlopen(request, timeout=DEFAULT_TIMEOUT_SECONDS) as response:
            status = getattr(response, "status", None) or 200
            if status >= 400:
                raise OSError(f"HTTP {status}")
            content_type = response.headers.get("content-type", "")
            body = response.read().decode(response.headers.get_content_charset() or "utf-8", errors="replace")
    except OSError as exc:
        return [
            SourceItem(
                label=label,
                url=url,
                owner=owner,
                owner_type=owner_type,
                title=f"Could not fetch {label}",
                summary=str(exc),
            )
        ]

    if "xml" in content_type or looks_like_feed(body):
        return parse_feed(body, label, url, owner, owner_type, limit)
    return parse_html(body, label, url, owner, owner_type, limit)


def looks_like_feed(text: str) -> bool:
    sample = text[:500].lower()
    return "<rss" in sample or "<feed" in sample or "<rdf" in sample


def parse_feed(
    text: str,
    label: str,
    fallback_url: str,
    owner: str,
    owner_type: str,
    limit: int,
) -> list[SourceItem]:
    if feedparser is None:
        return parse_feed_with_stdlib(text, label, fallback_url, owner, owner_type, limit)

    feed = feedparser.parse(text)
    items: list[SourceItem] = []
    for entry in feed.entries[:limit]:
        title = clean_text(entry.get("title", "Untitled update"))
        summary = clean_text(entry.get("summary", "") or entry.get("description", ""))
        items.append(
            SourceItem(
                label=label,
                url=entry.get("link", fallback_url),
                owner=owner,
                owner_type=owner_type,
                title=title,
                summary=summary[:800],
                published=entry.get("published") or entry.get("updated"),
            )
        )
    return items or [
        SourceItem(
            label=label,
            url=fallback_url,
            owner=owner,
            owner_type=owner_type,
            title=f"No feed entries found for {label}",
            summary="The source looked like a feed, but no entries were available.",
        )
    ]


def parse_feed_with_stdlib(
    text: str,
    label: str,
    fallback_url: str,
    owner: str,
    owner_type: str,
    limit: int,
) -> list[SourceItem]:
    try:
        root = ET.fromstring(text)
    except ET.ParseError:
        return parse_html(text, label, fallback_url, owner, owner_type, limit)

    items: list[SourceItem] = []
    candidates = list(root.findall(".//item")) + list(root.findall(".//{http://www.w3.org/2005/Atom}entry"))
    for entry in candidates[:limit]:
        title = child_text(entry, "title") or "Untitled update"
        link = child_text(entry, "link") or child_attr(entry, "link", "href") or fallback_url
        summary = (
            child_text(entry, "description")
            or child_text(entry, "summary")
            or child_text(entry, "{http://www.w3.org/2005/Atom}summary")
            or ""
        )
        published = (
            child_text(entry, "pubDate")
            or child_text(entry, "published")
            or child_text(entry, "{http://www.w3.org/2005/Atom}updated")
        )
        items.append(
            SourceItem(
                label=label,
                url=link,
                owner=owner,
                owner_type=owner_type,
                title=clean_text(title),
                summary=clean_text(summary)[:800],
                published=published,
            )
        )

    return items or [
        SourceItem(
            label=label,
            url=fallback_url,
            owner=owner,
            owner_type=owner_type,
            title=f"No feed entries found for {label}",
            summary="The source looked like a feed, but no entries were available.",
        )
    ]


def parse_html(
    text: str,
    label: str,
    url: str,
    owner: str,
    owner_type: str,
    limit: int,
) -> list[SourceItem]:
    extractor = SimpleHTMLExtractor()
    extractor.feed(text)
    title = clean_text(" ".join(extractor.title_parts) or label)
    summary_parts = [part for part in extractor.heading_parts[:6] + extractor.paragraph_parts[:8] if part]
    summary = "\n".join(summary_parts)

    return [
        SourceItem(
            label=label,
            url=url,
            owner=owner,
            owner_type=owner_type,
            title=title,
            summary=summary[:1600] or f"Fetched {domain_for(url)}, but no readable body text was found.",
        )
    ][:limit]


def dedupe_items(items: list[SourceItem]) -> list[SourceItem]:
    seen: set[tuple[str, str]] = set()
    unique: list[SourceItem] = []
    for item in items:
        key = (normalize_url(item.url), normalize_title(item.title))
        if key in seen:
            continue
        seen.add(key)
        unique.append(item)
    return unique


def build_digest(config: dict[str, Any], items: list[SourceItem]) -> str:
    if os.getenv("OPENAI_API_KEY"):
        try:
            return build_openai_digest(config, items)
        except Exception as exc:  # Keep scheduled runs useful even when AI fails.
            fallback = build_fallback_digest(config, items)
            return f"{fallback}\n\n## Run Note\n\nOpenAI digest generation failed: `{exc}`\n"
    return build_fallback_digest(config, items)


def build_openai_digest(config: dict[str, Any], items: list[SourceItem]) -> str:
    from openai import OpenAI

    client = OpenAI()
    model = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")
    prompt = render_prompt(config, items)

    response = client.responses.create(
        model=model,
        input=[
            {
                "role": "system",
                "content": "You create concise, source-backed competitive intelligence digests for B2B SaaS product managers.",
            },
            {"role": "user", "content": prompt},
        ],
    )
    return response.output_text


def render_prompt(config: dict[str, Any], items: list[SourceItem]) -> str:
    lookback_hours = int(config.get("digest", {}).get("lookback_hours", 24))
    source_packet = "\n\n".join(
        [
            f"Source {idx + 1}\n"
            f"Owner: {item.owner} ({item.owner_type})\n"
            f"Label: {item.label}\n"
            f"Title: {item.title}\n"
            f"Published: {item.published or 'Unknown'}\n"
            f"URL: {item.url}\n"
            f"Summary:\n{item.summary}"
            for idx, item in enumerate(items)
        ]
    )
    return f"""
Create a morning market intel digest using the competitive-market-intel skill.
Only include competitors or market actors with noteworthy activity in the last {lookback_hours} hours.
Do not include a competitor just because they are listed in the config or because a source was fetched.
If no configured competitor has a noteworthy signal in the last {lookback_hours} hours, write a short no-news digest that says so clearly.

Company:
{yaml.safe_dump(config.get("company", {}), sort_keys=False)}

Themes:
{yaml.safe_dump(config.get("themes", []), sort_keys=False)}

Digest settings:
{yaml.safe_dump(config.get("digest", {}), sort_keys=False)}

Use this format:
- Subject line
- Executive summary
- Top signals
- Watchlist
- Recommended actions
- Sources

Classify signals as Product, Packaging And Pricing, Positioning, Go-To-Market, Company And Market, or Customer Sentiment.
Keep the digest short and factual.
Do not include separate "why it matters" or "PM implication" fields.
Mark confidence as High, Medium, or Low.
Do not invent source details. If sources are weak or unavailable, say so.
Treat undated source pages as low-confidence unless the text clearly indicates a recent change.
Exclude routine marketing, evergreen content, and unchanged pages from Top signals.

Source packet:
{source_packet or "No source items were collected."}
""".strip()


def build_fallback_digest(config: dict[str, Any], items: list[SourceItem]) -> str:
    company = config.get("company", {}).get("name", "your company")
    today = dt.date.today().isoformat()
    lookback_hours = int(config.get("digest", {}).get("lookback_hours", 24))
    max_items = int(config.get("digest", {}).get("max_top_signals", 5))
    selected = items[:max_items]

    lines = [
        f"Subject: Morning Market Intel: {company} source scan needs review",
        "",
        "## Executive Summary",
        "",
    ]
    if selected:
        lines.append(f"- Collected {len(items)} source item(s) on {today}.")
        lines.append("- OpenAI digest generation was not enabled, so this run did not assess whether changes are noteworthy.")
        lines.append(f"- Review the source summaries below or rerun with `OPENAI_API_KEY` to identify noteworthy activity in the last {lookback_hours} hours.")
    else:
        lines[0] = "Subject: Morning Market Intel: No noteworthy competitor updates"
        lines.append(f"- No source items were collected on {today}.")
        lines.append(f"- No noteworthy competitor activity was found for the last {lookback_hours} hours based on the available sources.")

    lines.extend(["", "## Collected Sources Needing Review", ""])
    for idx, item in enumerate(selected, start=1):
        lines.extend(
            [
                f"### {idx}. {item.owner}: {item.title}",
                "",
                "- **Signal type:** Unclassified",
                f"- **What happened:** {first_sentence(item.summary)}",
                "- **Confidence:** Low",
                f"- **Sources:** {item.url}",
                "",
            ]
        )

    if not selected:
        lines.extend(["No collected sources require review.", ""])

    lines.extend(["## Watchlist", ""])
    for item in items[max_items : max_items + 5]:
        lines.append(f"- {item.owner}: {item.title} ({item.url})")
    if len(items) <= max_items:
        lines.append("- No additional watchlist items.")

    lines.extend(["", "## Recommended Actions", ""])
    lines.append("- Replace placeholder sources with real competitor and market URLs.")
    lines.append("- Add `OPENAI_API_KEY` to identify noteworthy activity automatically.")

    lines.extend(["", "## Sources", ""])
    for item in items:
        lines.append(f"- {item.title} - {item.url}")

    return "\n".join(lines).strip() + "\n"


def write_digest(path: Path, digest: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(digest, encoding="utf-8")


def maybe_send_email(config: dict[str, Any], digest: str, send_email: bool) -> str:
    if not send_email:
        return "Email delivery skipped. Pass --send-email to enable it."

    delivery = config.get("delivery", {}) or {}
    smtp_host = require_env("SMTP_HOST")
    smtp_port = int(os.getenv("SMTP_PORT", "587"))
    smtp_username = require_env("SMTP_USERNAME")
    smtp_password = require_env("SMTP_PASSWORD")
    sender = os.getenv("MARKET_INTEL_FROM") or delivery.get("from")
    recipient = os.getenv("MARKET_INTEL_TO") or delivery.get("to")
    if not sender or not recipient:
        raise ValueError("Email sender and recipient must be set in env or config.")

    subject = extract_subject(digest)
    body = strip_subject(digest)

    message = email.message.EmailMessage()
    message["From"] = sender
    message["To"] = recipient
    message["Subject"] = subject
    message.set_content(body)

    with smtplib.SMTP(smtp_host, smtp_port) as smtp:
        smtp.starttls()
        smtp.login(smtp_username, smtp_password)
        smtp.send_message(message)

    return f"Email sent to {recipient}."


def require_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise ValueError(f"Missing required environment variable: {name}")
    return value


def extract_subject(digest: str) -> str:
    for line in digest.splitlines():
        if line.lower().startswith("subject:"):
            return line.split(":", 1)[1].strip()
    return "Morning Market Intel"


def strip_subject(digest: str) -> str:
    lines = digest.splitlines()
    if lines and lines[0].lower().startswith("subject:"):
        return "\n".join(lines[1:]).lstrip()
    return digest


def clean_text(value: Any) -> str:
    text = html.unescape(str(value or ""))
    text = re.sub(r"<[^>]+>", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def normalize_title(title: str) -> str:
    return re.sub(r"\W+", "", title.lower())[:80]


def normalize_url(url: str) -> str:
    return url.split("#", 1)[0].rstrip("/")


def domain_for(url: str) -> str:
    return urlparse(url).netloc or url


def first_sentence(text: str) -> str:
    cleaned = clean_text(text)
    if not cleaned:
        return "Source fetched, but no readable summary was available."
    match = re.search(r"(.{1,240}?[.!?])\s", cleaned)
    if match:
        return match.group(1)
    return cleaned[:240].rstrip() + ("..." if len(cleaned) > 240 else "")


def child_text(entry: ET.Element, name: str) -> Optional[str]:
    child = entry.find(name)
    if child is None:
        return None
    return child.text


def child_attr(entry: ET.Element, name: str, attr: str) -> Optional[str]:
    child = entry.find(name)
    if child is None:
        return None
    return child.attrib.get(attr)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the daily intel email workflow.")
    parser.add_argument("--config", required=True, type=Path, help="Path to workflow YAML config.")
    parser.add_argument(
        "--output",
        default=Path("outputs/daily-intel-email.md"),
        type=Path,
        help="Where to write the digest Markdown.",
    )
    parser.add_argument(
        "--limit-per-source",
        default=5,
        type=int,
        help="Maximum items to collect from each feed-like source.",
    )
    parser.add_argument(
        "--send-email",
        action="store_true",
        help="Send the digest by email after writing it. Requires SMTP env vars.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    config = load_config(args.config)
    items = collect_sources(config, args.limit_per_source)
    digest = build_digest(config, items)
    write_digest(args.output, digest)
    delivery_result = maybe_send_email(config, digest, args.send_email)
    print(f"Wrote digest to {args.output}")
    print(delivery_result)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
