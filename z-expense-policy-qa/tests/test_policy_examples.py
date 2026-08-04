from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = SKILL_ROOT / "scripts" / "search_evidence.py"
CORPUS = SKILL_ROOT / "references" / "corpus"


class PolicyExampleTests(unittest.TestCase):
    def search(self, queries: list[str]) -> dict[str, object]:
        command = [sys.executable, str(SCRIPT), "--source", str(CORPUS)]
        for query in queries:
            command.extend(["--query", query])
        command.extend(["--top-k", "6", "--format", "json"])
        result = subprocess.run(command, text=True, capture_output=True, check=False)
        self.assertEqual(result.returncode, 0, result.stderr)
        return json.loads(result.stdout)

    def combined_content(self, payload: dict[str, object]) -> str:
        evidence = payload["evidence"]
        return "\n".join(item["content"] for item in evidence)

    def test_late_night_taxi_limit_and_materials(self) -> None:
        payload = self.search(["21:30", "120 元", "加班记录", "常住地址"])
        content = self.combined_content(payload)
        self.assertIn("每次上限为 120 元", content)
        self.assertIn("行程单、发票、支付记录、当日加班记录", content)

    def test_chengdu_hotel_limit(self) -> None:
        payload = self.search(["成都", "B 类城市", "450 元", "住宿"])
        content = self.combined_content(payload)
        self.assertIn("B 类城市 450 元", content)
        self.assertIn("成都", content)

    def test_personal_invoice_and_late_submission(self) -> None:
        payload = self.search(["个人抬头", "超过 15", "重开", "延迟原因"])
        content = self.combined_content(payload)
        self.assertIn("应先联系商家重开", content)
        self.assertIn("部门负责人说明延迟原因", content)


if __name__ == "__main__":
    unittest.main()
