from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = SKILL_ROOT / "scripts" / "search_evidence.py"


class SearchEvidenceTests(unittest.TestCase):
    def run_search(
        self,
        sources: list[Path],
        queries: list[str],
        *,
        top_k: int = 5,
        regex: bool = False,
    ) -> subprocess.CompletedProcess[str]:
        command = [sys.executable, str(SCRIPT)]
        for source in sources:
            command.extend(["--source", str(source)])
        for query in queries:
            command.extend(["--query", query])
        command.extend(["--top-k", str(top_k), "--format", "json"])
        if regex:
            command.append("--regex")
        return subprocess.run(command, text=True, capture_output=True, check=False)

    def test_directory_sources_are_discovered_and_broad_evidence_ranks_first(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            corpus = Path(temp_dir)
            (corpus / "strategy.md").write_text(
                "# Strategy\n\n"
                "Open source lowers adoption cost and creates a path to revenue.\n\n"
                "Revenue matters after the ecosystem becomes useful.\n",
                encoding="utf-8",
            )
            (corpus / "notes.txt").write_text(
                "Open source can also improve recruiting.\n",
                encoding="utf-8",
            )

            result = self.run_search([corpus], ["open source", "revenue"])

            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(result.stdout)
            self.assertEqual(payload["meta"]["source_files"], 2)
            self.assertEqual(
                payload["evidence"][0]["matched_terms"],
                ["open source", "revenue"],
            )
            self.assertIn("adoption cost", payload["evidence"][0]["content"])

    def test_returns_complete_paragraph_and_location_metadata(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            source = Path(temp_dir) / "interview.md"
            source.write_text(
                "# Interview\n\n"
                "## PDF Page 7\n\n"
                "[00:12:34]\n\n"
                "Alice: Small teams move faster because communication paths stay short. "
                "\nThis second sentence must remain in the same evidence block.\n",
                encoding="utf-8",
            )

            result = self.run_search([source], ["communication paths"])

            self.assertEqual(result.returncode, 0, result.stderr)
            evidence = json.loads(result.stdout)["evidence"][0]
            self.assertEqual(evidence["location"]["document"], "interview.md")
            self.assertEqual(evidence["location"]["page"], 7)
            self.assertEqual(evidence["location"]["timestamp"], "00:12:34")
            self.assertEqual(evidence["location"]["section"], "Interview")
            self.assertEqual(evidence["location"]["speaker"], "Alice")
            self.assertIn("second sentence", evidence["content"])
            self.assertGreater(evidence["location"]["line_end"], evidence["location"]["line_start"])

    def test_duplicate_content_is_deduplicated_and_locations_are_preserved(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            corpus = Path(temp_dir)
            duplicate = "Evidence quality improves when every claim keeps a source location.\n"
            (corpus / "one.md").write_text(duplicate, encoding="utf-8")
            (corpus / "two.md").write_text(duplicate, encoding="utf-8")

            result = self.run_search([corpus], ["source location"])

            self.assertEqual(result.returncode, 0, result.stderr)
            evidence = json.loads(result.stdout)["evidence"]
            self.assertEqual(len(evidence), 1)
            self.assertEqual(len(evidence[0]["additional_locations"]), 1)
            documents = {
                evidence[0]["location"]["document"],
                evidence[0]["additional_locations"][0]["document"],
            }
            self.assertEqual(documents, {"one.md", "two.md"})

    def test_adjacent_matched_paragraphs_are_merged(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            source = Path(temp_dir) / "decision.md"
            source.write_text(
                "# Decision\n\n"
                "The launch criterion is customer retention.\n\n"
                "The main risk is support capacity during the first month.\n\n"
                "A separate appendix starts here.\n",
                encoding="utf-8",
            )

            result = self.run_search([source], ["customer retention", "support capacity"])

            self.assertEqual(result.returncode, 0, result.stderr)
            evidence = json.loads(result.stdout)["evidence"]
            self.assertEqual(len(evidence), 1)
            self.assertEqual(len(evidence[0]["block_ids"]), 2)
            self.assertIn("launch criterion", evidence[0]["content"])
            self.assertIn("main risk", evidence[0]["content"])

    def test_no_hit_distinguishes_query_miss_from_source_absence(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            source = Path(temp_dir) / "notes.md"
            source.write_text("The source discusses hiring and team design.\n", encoding="utf-8")

            result = self.run_search([source], ["quantum networking"])

            self.assertEqual(result.returncode, 1)
            payload = json.loads(result.stdout)
            self.assertEqual(payload["evidence"], [])
            self.assertIn("does not prove", payload["meta"]["note"])
            self.assertIn("rewrite", payload["meta"]["note"])

    def test_regex_queries_are_supported_explicitly(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            source = Path(temp_dir) / "roadmap.md"
            source.write_text(
                "The roadmap covers model version 3.2 and model version 3.3.\n",
                encoding="utf-8",
            )

            result = self.run_search([source], [r"version 3\.[23]"], regex=True)

            self.assertEqual(result.returncode, 0, result.stderr)
            evidence = json.loads(result.stdout)["evidence"]
            self.assertEqual(len(evidence), 1)
            self.assertEqual(evidence[0]["matched_terms"], [r"version 3\.[23]"])


if __name__ == "__main__":
    unittest.main()
