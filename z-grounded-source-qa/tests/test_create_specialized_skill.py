from __future__ import annotations

import argparse
import json
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

from create_specialized_skill import create_skill  # noqa: E402


class CreateSpecializedSkillTests(unittest.TestCase):
    def make_args(self, root: Path, source: Path) -> argparse.Namespace:
        return argparse.Namespace(
            name="z-demo-policy-qa",
            title="示例制度助手",
            mode="policy",
            source=[source],
            output_root=root,
            description=None,
            trigger=["报销制度", "差旅标准"],
            question=["晚上加班打车能不能报销"],
            profile_file=None,
            source_note="这是用于测试的模拟制度",
        )

    def test_creates_self_contained_skill_with_manifest_and_evals(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source = root / "policy.md"
            source.write_text("# 制度\n\n晚间打车需要发票和加班记录\n", encoding="utf-8")

            target = create_skill(self.make_args(root / "skills", source))

            self.assertEqual(target.name, "z-demo-policy-qa")
            self.assertTrue((target / "SKILL.md").is_file())
            self.assertTrue((target / "scripts" / "search_evidence.py").is_file())
            self.assertTrue((target / "references" / "corpus" / "policy.md").is_file())
            skill_text = (target / "SKILL.md").read_text(encoding="utf-8")
            self.assertIn("name: z-demo-policy-qa", skill_text)
            self.assertIn("结论（可以／不可以／有条件／资料不足）", skill_text)

            manifest = json.loads(
                (target / "references" / "source-manifest.json").read_text(
                    encoding="utf-8"
                )
            )
            self.assertEqual(manifest["sources"][0]["file"], "policy.md")
            self.assertEqual(len(manifest["sources"][0]["sha256"]), 64)

            evals = json.loads(
                (target / "evals" / "evals.json").read_text(encoding="utf-8")
            )
            self.assertEqual(evals["evals"][0]["prompt"], "晚上加班打车能不能报销")

    def test_refuses_to_overwrite_existing_skill(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source = root / "policy.md"
            source.write_text("制度内容", encoding="utf-8")
            args = self.make_args(root / "skills", source)
            create_skill(args)

            with self.assertRaises(FileExistsError):
                create_skill(args)

    def test_rejects_invalid_skill_name(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source = root / "policy.md"
            source.write_text("制度内容", encoding="utf-8")
            args = self.make_args(root / "skills", source)
            args.name = "Bad Skill"

            with self.assertRaises(ValueError):
                create_skill(args)


if __name__ == "__main__":
    unittest.main()
