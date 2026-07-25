#!/usr/bin/env python3
"""Retrieve ranked, paragraph-level evidence from the supplied transcript."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "references" / "transcript-by-page.md"
TOPIC_INDEX = ROOT / "references" / "topic-index.md"

PAGE_RE = re.compile(r"^## PDF Page (\d+)\s*$")
TIMESTAMP_RE = re.compile(r"^\[(\d{2}:\d{2}:\d{2})\]\s*$")
SENTENCE_END_RE = re.compile(r"[。！？!?；;：:]$")
SPEAKER_LABELS = {
    "梁文锋",
    "投资者/提问者",
    "主持人/现场",
    "现场/未明",
}


@dataclass(frozen=True)
class Topic:
    name: str
    pages: tuple[int, ...]
    notes: str


@dataclass
class Block:
    block_id: str
    document: str
    page: int
    timestamp: str | None
    speaker: str | None
    content: str
    index: int


@dataclass
class Evidence:
    document: str
    page: int
    timestamp: str | None
    section: str
    speaker: str | None
    block_ids: list[str]
    matched_terms: list[str]
    score: int
    content: str
    previous_context: str
    next_context: str
    content_hash: str
    index: int

    def public_dict(self) -> dict[str, object]:
        result = asdict(self)
        result.pop("index", None)
        return result


def normalize_text(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip()


def content_hash(value: str) -> str:
    normalized = re.sub(r"\W+", "", value, flags=re.UNICODE).lower()
    return hashlib.sha1(normalized.encode("utf-8")).hexdigest()[:12]


def parse_page_spec(value: str) -> tuple[int, ...]:
    pages: set[int] = set()
    for part in re.split(r"[,，、]\s*", value.strip()):
        match = re.fullmatch(r"(\d+)(?:\s*[-–—]\s*(\d+))?", part)
        if not match:
            continue
        start = int(match.group(1))
        end = int(match.group(2) or start)
        pages.update(range(min(start, end), max(start, end) + 1))
    return tuple(sorted(pages))


def load_topics(path: Path = TOPIC_INDEX) -> list[Topic]:
    topics: list[Topic] = []
    if not path.exists():
        return topics
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        if not raw_line.startswith("|") or raw_line.startswith("|---"):
            continue
        cells = [cell.strip() for cell in raw_line.strip("|").split("|")]
        if len(cells) < 3 or cells[0] == "Topic":
            continue
        pages = parse_page_spec(cells[1])
        if pages:
            topics.append(Topic(cells[0], pages, cells[2]))
    return topics


def parse_transcript(path: Path = SOURCE) -> list[Block]:
    """Split the transcript into complete Markdown paragraphs with metadata."""
    lines = path.read_text(encoding="utf-8").splitlines()
    blocks: list[Block] = []
    page = 0
    page_block = 0
    timestamp: str | None = None
    speaker: str | None = None
    paragraph: list[str] = []

    def flush() -> None:
        nonlocal page_block, paragraph, timestamp, speaker
        content = normalize_text(" ".join(paragraph))
        paragraph = []
        if not content or page == 0:
            return
        if content in SPEAKER_LABELS:
            speaker = content
            return
        timestamp_match = TIMESTAMP_RE.fullmatch(content)
        if timestamp_match:
            timestamp = timestamp_match.group(1)
            return
        if content.startswith("梁文锋投资者交流会 · 说话人整理版"):
            return
        if re.fullmatch(r"\d+", content):
            return
        page_block += 1
        blocks.append(
            Block(
                block_id=f"p{page:03d}-b{page_block:03d}",
                document=path.name,
                page=page,
                timestamp=timestamp,
                speaker=speaker,
                content=content,
                index=len(blocks),
            )
        )

    for raw_line in lines:
        page_match = PAGE_RE.match(raw_line)
        if page_match:
            flush()
            page = int(page_match.group(1))
            page_block = 0
            continue
        stripped = raw_line.strip()
        if stripped in SPEAKER_LABELS:
            flush()
            speaker = stripped
            continue
        if not stripped:
            flush()
            continue
        paragraph.append(stripped)
    flush()
    return blocks


def compile_patterns(queries: Iterable[str], regex: bool) -> list[tuple[str, re.Pattern[str]]]:
    patterns: list[tuple[str, re.Pattern[str]]] = []
    seen: set[str] = set()
    for raw_query in queries:
        query = normalize_text(raw_query)
        key = query.lower()
        if not query or key in seen:
            continue
        seen.add(key)
        expression = query if regex else re.escape(query)
        patterns.append((query, re.compile(expression, re.I)))
    return patterns


def topic_names_for_page(page: int, topics: list[Topic]) -> list[str]:
    return [topic.name for topic in topics if page in topic.pages]


def relevant_topic_pages(
    patterns: list[tuple[str, re.Pattern[str]]], topics: list[Topic]
) -> set[int]:
    pages: set[int] = set()
    for topic in topics:
        haystack = f"{topic.name} {topic.notes}"
        if any(pattern.search(haystack) for _, pattern in patterns):
            pages.update(topic.pages)
    return pages


def score_block(
    block: Block,
    patterns: list[tuple[str, re.Pattern[str]]],
    topics: list[Topic],
    preferred_pages: set[int],
) -> tuple[int, list[str], str]:
    matches: list[str] = []
    score = 0
    page_topics = topic_names_for_page(block.page, topics)
    topic_text = " ".join(page_topics)

    for term, pattern in patterns:
        occurrences = len(pattern.findall(block.content))
        if occurrences:
            matches.append(term)
            score += 2 + min(occurrences, 3)
            if len(term) >= 2:
                score += 4
        if pattern.search(topic_text):
            score += 5

    if len(matches) > 1:
        score += (len(matches) - 1) * 2
    if block.page in preferred_pages:
        score += 3
    if 80 <= len(block.content) <= 1200:
        score += 1

    section = " / ".join(page_topics) if page_topics else f"PDF Page {block.page}"
    return score, matches, section


def preview(blocks: list[Block], index: int, direction: int, limit: int = 180) -> str:
    candidate = index + direction
    if candidate < 0 or candidate >= len(blocks):
        return ""
    value = blocks[candidate].content
    return value if len(value) <= limit else value[: limit - 1] + "…"


def merge_adjacent(items: list[Evidence]) -> list[Evidence]:
    """Merge neighboring hit paragraphs before ranking and deduplication."""
    if not items:
        return []
    ordered = sorted(items, key=lambda item: item.index)
    merged: list[Evidence] = []
    for item in ordered:
        if (
            merged
            and merged[-1].page == item.page
            and item.index == merged[-1].index + len(merged[-1].block_ids)
        ):
            current = merged[-1]
            current.block_ids.extend(item.block_ids)
            current.matched_terms = list(
                dict.fromkeys([*current.matched_terms, *item.matched_terms])
            )
            current.score = max(current.score, item.score) + 1
            current.content = f"{current.content}\n\n{item.content}"
            current.next_context = item.next_context
            current.content_hash = content_hash(current.content)
            continue
        merged.append(item)
    return merged


def search(
    queries: Iterable[str],
    *,
    source: Path = SOURCE,
    topic_index: Path = TOPIC_INDEX,
    regex: bool = False,
    top_k: int = 5,
) -> tuple[dict[str, object], list[Evidence]]:
    blocks = parse_transcript(source)
    topics = load_topics(topic_index)
    patterns = compile_patterns(queries, regex)
    if not patterns:
        raise ValueError("At least one non-empty query is required")
    preferred_pages = relevant_topic_pages(patterns, topics)

    hits: list[Evidence] = []
    for block in blocks:
        score, matched_terms, section = score_block(
            block, patterns, topics, preferred_pages
        )
        if not matched_terms:
            continue
        hits.append(
            Evidence(
                document=block.document,
                page=block.page,
                timestamp=block.timestamp,
                section=section,
                speaker=block.speaker,
                block_ids=[block.block_id],
                matched_terms=matched_terms,
                score=score,
                content=block.content,
                previous_context=preview(blocks, block.index, -1),
                next_context=preview(blocks, block.index, 1),
                content_hash=content_hash(block.content),
                index=block.index,
            )
        )

    merged = merge_adjacent(hits)
    deduped: dict[str, Evidence] = {}
    for item in merged:
        existing = deduped.get(item.content_hash)
        if existing is None or item.score > existing.score:
            deduped[item.content_hash] = item
    ranked = sorted(
        deduped.values(),
        key=lambda item: (-item.score, -len(item.matched_terms), item.page, item.index),
    )[: max(1, top_k)]

    meta: dict[str, object] = {
        "document": source.name,
        "query_terms": [term for term, _ in patterns],
        "searched_blocks": len(blocks),
        "matched_blocks": len(hits),
        "unique_results": len(deduped),
        "returned_results": len(ranked),
        "top_k": max(1, top_k),
        "note": (
            "当前查询表达式未命中；这不能证明原始资料没有相关内容。"
            "请改写查询、增加同义词，或读取主题相关页面全文。"
            if not ranked
            else "结果按关键词覆盖、短语命中、主题页推荐和段落完整度排序。"
        ),
    }
    return meta, ranked


def print_text(meta: dict[str, object], results: list[Evidence]) -> None:
    print("Queries:", " | ".join(str(item) for item in meta["query_terms"]))
    print(
        "Search:",
        f"{meta['searched_blocks']} blocks, "
        f"{meta['unique_results']} unique matches, "
        f"returning {meta['returned_results']}",
    )
    print("Note:", meta["note"])
    for number, item in enumerate(results, start=1):
        location = f"PDF page {item.page}"
        if item.timestamp:
            location += f", {item.timestamp}"
        print(f"\n--- Evidence {number} | score {item.score} | {location} ---")
        print("Section:", item.section)
        print("Matched:", ", ".join(item.matched_terms))
        print("Block:", ", ".join(item.block_ids))
        print(item.content)


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Search one or more query expressions and return ranked, "
            "paragraph-level evidence."
        )
    )
    parser.add_argument(
        "queries",
        nargs="+",
        help='3-8 search expressions are recommended, e.g. "商业化" "盈利" "赚钱"',
    )
    parser.add_argument("--regex", action="store_true", help="treat queries as regex")
    parser.add_argument("--top-k", type=int, default=5)
    parser.add_argument(
        "--format",
        choices=("text", "json"),
        default="text",
        dest="output_format",
    )
    args = parser.parse_args()

    meta, results = search(
        args.queries,
        regex=args.regex,
        top_k=args.top_k,
    )
    if args.output_format == "json":
        print(
            json.dumps(
                {
                    "meta": meta,
                    "evidence": [item.public_dict() for item in results],
                },
                ensure_ascii=False,
                indent=2,
            )
        )
    else:
        print_text(meta, results)
    return 0 if results else 1


if __name__ == "__main__":
    raise SystemExit(main())
