from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SKILL_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = SKILL_ROOT / "search_source.py"

SPEC = importlib.util.spec_from_file_location("search_source", SCRIPT)
assert SPEC and SPEC.loader
search_source = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = search_source
SPEC.loader.exec_module(search_source)


class SearchSourceTests(unittest.TestCase):
    def write_fixture(self, directory: Path) -> tuple[Path, Path]:
        source = directory / "transcript.md"
        source.write_text(
            """## PDF Page 1

梁文锋

[00:00:01]

开源是一种长期策略。我们选择开源，也会考虑商业模式和合理利润。

只谈商业化会把问题说窄，真正重要的是愿景和长期目标。

## PDF Page 2

[00:01:00]

商业模式需要克制，盈利不是唯一目标。

同一句重复证据。

同一句重复证据。
""",
            encoding="utf-8",
        )
        index = directory / "topic-index.md"
        index.write_text(
            """| Topic | PDF pages | Approx. timestamps / notes |
|---|---:|---|
| Open source and business model | 1-2 | strategy, profit, long term |
""",
            encoding="utf-8",
        )
        return source, index

    def test_multi_term_result_ranks_broader_evidence_first(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            source, index = self.write_fixture(Path(tmp))
            _, results = search_source.search(
                ["开源", "商业模式", "利润"],
                source=source,
                topic_index=index,
                top_k=5,
            )
        self.assertGreaterEqual(len(results), 2)
        self.assertEqual(results[0].page, 1)
        self.assertEqual(results[0].matched_terms, ["开源", "商业模式", "利润"])

    def test_returns_complete_paragraph_and_metadata(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            source, index = self.write_fixture(Path(tmp))
            _, results = search_source.search(
                ["长期目标"],
                source=source,
                topic_index=index,
            )
        self.assertEqual(
            results[0].content,
            "只谈商业化会把问题说窄，真正重要的是愿景和长期目标。",
        )
        self.assertEqual(results[0].timestamp, "00:00:01")
        self.assertEqual(results[0].speaker, "梁文锋")
        self.assertTrue(results[0].block_ids[0].startswith("p001-b"))
        self.assertEqual(len(results[0].content_hash), 12)

    def test_duplicate_content_is_removed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            source, index = self.write_fixture(Path(tmp))
            meta, results = search_source.search(
                ["重复证据"],
                source=source,
                topic_index=index,
                top_k=10,
            )
        self.assertEqual(meta["unique_results"], 1)
        self.assertEqual(len(results), 1)

    def test_empty_search_warns_that_absence_is_unproven(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            source, index = self.write_fixture(Path(tmp))
            meta, results = search_source.search(
                ["完全不存在的词"],
                source=source,
                topic_index=index,
            )
        self.assertEqual(results, [])
        self.assertIn("不能证明", str(meta["note"]))

    def test_cli_json_is_an_evidence_object(self) -> None:
        completed = subprocess.run(
            [
                sys.executable,
                str(SCRIPT),
                "开源",
                "愿景",
                "--top-k",
                "2",
                "--format",
                "json",
            ],
            check=True,
            capture_output=True,
            text=True,
        )
        payload = json.loads(completed.stdout)
        self.assertEqual(payload["meta"]["query_terms"], ["开源", "愿景"])
        self.assertLessEqual(len(payload["evidence"]), 2)
        required = {
            "document",
            "page",
            "section",
            "matched_terms",
            "score",
            "content",
            "block_ids",
            "content_hash",
        }
        self.assertTrue(required.issubset(payload["evidence"][0]))


if __name__ == "__main__":
    unittest.main()
