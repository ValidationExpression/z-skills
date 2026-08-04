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

    def test_first_class_train_without_preapproval(self) -> None:
        payload = self.search(["高铁", "二等座", "高于制度标准", "2 个工作日"])
        content = self.combined_content(payload)
        self.assertIn("高铁和动车原则上报销二等座", content)
        self.assertIn("可核验的标准席位价格", content)
        self.assertIn("2 个工作日内补充说明", content)

    def test_business_entertainment_approval_and_materials(self) -> None:
        payload = self.search(["业务招待", "1,000 元", "财务负责人", "参与人名单"])
        content = self.combined_content(payload)
        self.assertIn("单次预算超过 1,000 元", content)
        self.assertIn("餐饮发票、消费明细、支付记录和参与人名单", content)

    def test_overseas_travel_is_explicitly_unsupported(self) -> None:
        payload = self.search(["境外差旅", "外币汇率", "书面咨询", "自行推定"])
        content = self.combined_content(payload)
        self.assertIn("本制度没有规定境外差旅标准", content)
        self.assertIn("不能根据相近条款自行推定", content)


if __name__ == "__main__":
    unittest.main()
