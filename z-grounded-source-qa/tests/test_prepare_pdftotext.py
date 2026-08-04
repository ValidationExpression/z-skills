from __future__ import annotations

import sys
import unittest
from pathlib import Path


SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

from prepare_pdftotext import convert_text  # noqa: E402


class PreparePdfTextTests(unittest.TestCase):
    def test_paragraph_mode_adds_page_markers_and_joins_cjk_wraps(self) -> None:
        source = "第一行，\n第二行\n\nEnglish line\ncontinues here\f第二页内容\n"

        rendered = convert_text(source, title="测试资料")

        self.assertIn("# 测试资料", rendered)
        self.assertIn("## PDF Page 1", rendered)
        self.assertIn("第一行，第二行", rendered)
        self.assertIn("English line continues here", rendered)
        self.assertIn("## PDF Page 2", rendered)
        self.assertIn("第二页内容", rendered)

    def test_numbered_mode_groups_wrapped_aphorisms(self) -> None:
        source = (
            "【关于成长】\n"
            "1.先看长期\n"
            "再做选择\n"
            "2.保持坦诚\n"
            "沟通会更简单\n"
        )

        rendered = convert_text(source, title="思考摘录", mode="numbered")

        self.assertIn("### 关于成长", rendered)
        self.assertIn("1. 先看长期再做选择", rendered)
        self.assertIn("2. 保持坦诚沟通会更简单", rendered)


if __name__ == "__main__":
    unittest.main()
