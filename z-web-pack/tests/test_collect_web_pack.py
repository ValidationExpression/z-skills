from __future__ import annotations

import importlib.util
import tempfile
import unittest
from types import SimpleNamespace
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "collect_web_pack.py"
SPEC = importlib.util.spec_from_file_location("collect_web_pack", SCRIPT)
collect_web_pack = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(collect_web_pack)


class CollectWebPackTests(unittest.TestCase):
    def setUp(self):
        collect_web_pack.IMAGE_HASHES.clear()
        collect_web_pack.VIDEO_LINKS_SEEN.clear()
        collect_web_pack.FORCE_ROOTS.clear()

    def test_jina_reader_url_preserves_https_source_url(self):
        self.assertEqual(
            collect_web_pack.jina_reader_url("https://example.com/article?a=1"),
            "https://r.jina.ai/https://example.com/article?a=1",
        )

    def test_normalize_removes_tracking_parameters_without_touching_content_params(self):
        self.assertEqual(
            collect_web_pack.normalize(
                "https://Example.com/article?id=42&utm_source=newsletter&fbclid=abc&lang=zh#top"
            ),
            "https://example.com/article?id=42&lang=zh",
        )

    def test_srcset_largest_supports_density_descriptors(self):
        srcset = "small.webp 1x, medium.webp 1.5x, large.webp 2x"
        self.assertEqual(collect_web_pack._srcset_largest(srcset), "large.webp")

    def test_picture_source_can_beat_lower_resolution_img_srcset(self):
        soup = collect_web_pack.BeautifulSoup(
            """
            <picture>
              <source srcset="hero-800.webp 800w, hero-1600.webp 1600w">
              <img srcset="hero-400.webp 400w" src="hero-200.webp">
            </picture>
            """,
            "lxml",
        )
        self.assertEqual(
            collect_web_pack.patched_choose_img_url(
                soup.find("img"),
                "https://example.com/article",
            ),
            "https://example.com/hero-1600.webp",
        )

    def test_width_descriptor_beats_unrelated_low_density_candidate(self):
        soup = collect_web_pack.BeautifulSoup(
            """
            <picture>
              <source srcset="hero-2000.webp 2000w, hero-4000.webp 4000w">
              <img srcset="hero-small.webp 1x" src="hero-small.webp">
            </picture>
            """,
            "lxml",
        )
        self.assertEqual(
            collect_web_pack.patched_choose_img_url(
                soup.find("img"),
                "https://example.com/article",
            ),
            "https://example.com/hero-4000.webp",
        )

    def test_platform_video_detection_covers_handoff_platforms(self):
        html = """
        <iframe src="https://www.youtube.com/live/abcdefghijk"></iframe>
        <iframe src="https://www.instagram.com/reel/ABC123/"></iframe>
        <iframe src="https://www.douyin.com/video/123456"></iframe>
        <iframe src="https://www.facebook.com/watch?v=123456"></iframe>
        <iframe src="https://b23.tv/abc123"></iframe>
        """
        urls = collect_web_pack.collect_videos_from_html(html, "https://example.com/post")
        self.assertEqual(len(urls), 5)

    def test_probable_navigation_link_is_filtered_before_crawling(self):
        self.assertTrue(
            collect_web_pack.is_probable_navigation_link(
                {"text": "World", "url": "https://www.ft.com/world"}
            )
        )
        self.assertFalse(
            collect_web_pack.is_probable_navigation_link(
                {
                    "text": "FCA launches review of AI advice",
                    "url": "https://www.fca.org.uk/news/news-stories/ai-advice-review",
                }
            )
        )

    def test_restricted_source_still_creates_a_main_note(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            result = collect_web_pack.write_restricted_page(
                Path(tmp_dir),
                url="https://example.com/paywalled-story",
                depth=0,
                index=1,
                error="direct 403; Jina CAPTCHA",
            )
            note = Path(tmp_dir, result.filename)
            self.assertEqual(result.status, "restricted")
            self.assertEqual(result.role, "MAIN")
            self.assertTrue(note.exists())
            text = note.read_text(encoding="utf-8")
            self.assertIn("受限来源说明", text)
            self.assertIn("https://example.com/paywalled-story", text)
            self.assertIn("direct 403; Jina CAPTCHA", text)

    def test_cleanup_keeps_image_referenced_by_fallback_page(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            out_dir = Path(tmp_dir)
            assets = out_dir / "assets"
            assets.mkdir()
            image = assets / "hero.jpg"
            image.write_bytes(b"image")
            direct = SimpleNamespace(
                images=[{"status": "ok", "local_path": "assets/hero.jpg"}]
            )
            collect_web_pack.cleanup_page_images(
                out_dir,
                direct,
                keep_paths={"assets/hero.jpg"},
            )
            self.assertTrue(image.exists())

    def test_parse_args_accepts_public_support_sources(self):
        args = collect_web_pack.parse_args(
            [
                "https://example.com/paywalled-story",
                "--support-url",
                "https://public.example.org/report",
                "--support-url",
                "https://public.example.net/analysis",
            ]
        )
        self.assertEqual(
            args.support_urls,
            [
                "https://public.example.org/report",
                "https://public.example.net/analysis",
            ],
        )

    def test_long_article_with_signup_footer_is_not_marked_weak(self):
        article = ("This is substantive reporting with facts and analysis. " * 80) + "Sign up now"
        self.assertFalse(collect_web_pack._text_is_weak(article))

    def test_common_paywall_and_datadome_pages_are_marked_weak(self):
        self.assertTrue(
            collect_web_pack._text_is_weak(
                "Subscribe to continue reading. This article is only available to subscribers."
            )
        )
        self.assertTrue(
            collect_web_pack._text_is_weak(
                "Please enable JS and disable any ad blocker to continue. DataDome"
            )
        )

    def test_explicit_video_root_is_not_skipped_as_an_asset(self):
        url = "https://cdn.example.com/video.mp4"
        collect_web_pack.FORCE_ROOTS.add(url)
        skipped, reason = collect_web_pack.patched_should_skip_url(
            url,
            {"cdn.example.com"},
            False,
        )
        self.assertFalse(skipped, reason)

    def test_explicit_video_root_is_recorded_without_downloading(self):
        class NoNetworkSession:
            def get(self, *args, **kwargs):
                raise AssertionError("video root must not be fetched by web pack")

        with tempfile.TemporaryDirectory() as tmp_dir:
            out_dir = Path(tmp_dir)
            assets_dir = out_dir / "assets"
            assets_dir.mkdir()
            url = "https://cdn.example.com/video.mp4"
            result = collect_web_pack.process_page(
                NoNetworkSession(),
                url,
                0,
                out_dir,
                assets_dir,
                1,
                {"cdn.example.com"},
                False,
                [0],
                True,
            )
            self.assertEqual(result.status, "ok")
            self.assertEqual(result.videos[0]["url"], url)
            self.assertTrue(Path(out_dir, result.filename).exists())

    def test_no_jina_still_marks_weak_page_as_restricted(self):
        original = collect_web_pack.base.process_page

        def fake_process_page(session, url, depth, out_dir, assets_dir, index,
                              root_hosts, same_domain_only, global_image_index):
            filename = collect_web_pack.base.page_filename(index, "blocked", depth)
            Path(out_dir, filename).write_text(
                "# Subscribe to continue reading\n\nSign up now",
                encoding="utf-8",
            )
            return collect_web_pack.base.PageResult(
                url=url,
                final_url=url,
                title="blocked",
                filename=filename,
                status="ok",
                depth=depth,
                role=collect_web_pack.base.page_role(depth),
            )

        collect_web_pack.base.process_page = fake_process_page
        try:
            with tempfile.TemporaryDirectory() as tmp_dir:
                out_dir = Path(tmp_dir)
                assets_dir = out_dir / "assets"
                assets_dir.mkdir()
                result = collect_web_pack.process_page(
                    object(),
                    "https://example.com/blocked",
                    0,
                    out_dir,
                    assets_dir,
                    1,
                    {"example.com"},
                    False,
                    [0],
                    False,
                )
                self.assertEqual(result.status, "restricted")
                self.assertIn(
                    "受限来源说明",
                    Path(out_dir, result.filename).read_text(encoding="utf-8"),
                )
        finally:
            collect_web_pack.base.process_page = original

    def test_restricted_main_is_listed_as_main_and_not_failed(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            out_dir = Path(tmp_dir)
            page = collect_web_pack.base.PageResult(
                url="https://example.com/blocked",
                final_url="https://example.com/blocked",
                title="blocked",
                filename="MAIN-01-blocked.md",
                status="restricted",
                depth=0,
                role="MAIN",
                error="paywall",
            )
            Path(out_dir, page.filename).write_text("restricted", encoding="utf-8")
            collect_web_pack.base.write_inventory(
                out_dir,
                "restricted",
                [page.url],
                [page],
                [],
                0,
                1,
            )
            readme = Path(out_dir, "README.md").read_text(encoding="utf-8")
            reading_map = Path(out_dir, "03-reading-map.md").read_text(encoding="utf-8")
            self.assertIn("Main pages: 1", readme)
            self.assertIn("Restricted pages: 1", readme)
            self.assertIn(page.filename, reading_map)
            self.assertNotIn("No main page captured", reading_map)

    def test_access_notes_separate_successful_and_unavailable_support_sources(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            out_dir = Path(tmp_dir)
            pages = [
                collect_web_pack.base.PageResult(
                    url="https://restricted.example/story", final_url="https://restricted.example/story",
                    title="story", filename="MAIN-01-story.md", status="restricted",
                    depth=0, role="MAIN", error="captcha",
                ),
                collect_web_pack.base.PageResult(
                    url="https://public.example/report", final_url="https://public.example/report",
                    title="report", filename="LINKED-02-report.md", status="ok",
                    depth=1, role="LINKED",
                ),
                collect_web_pack.base.PageResult(
                    url="https://broken.example/report", final_url="https://broken.example/report",
                    title="broken", filename="LINKED-03-broken.md", status="restricted",
                    depth=1, role="LINKED", error="403",
                ),
            ]
            collect_web_pack.write_access_notes(
                out_dir,
                "topic",
                pages,
                ["https://public.example/report", "https://broken.example/report"],
            )
            text = Path(out_dir, "05-access-notes.md").read_text(encoding="utf-8")
            self.assertIn("LINKED-02-report.md", text)
            self.assertIn("未成功", text)
            self.assertIn("https://broken.example/report", text)

    def test_cleanup_page_images_keeps_deduplicated_assets(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            out_dir = Path(tmp_dir)
            assets = out_dir / "assets"
            assets.mkdir()
            own = assets / "own.jpg"
            shared = assets / "shared.jpg"
            own.write_bytes(b"own")
            shared.write_bytes(b"shared")
            page = collect_web_pack.base.PageResult(
                url="https://example.com", final_url="https://example.com", title="blocked",
                filename="MAIN-01-blocked.md", status="ok", depth=0, role="MAIN",
                images=[
                    {"status": "ok", "local_path": "assets/own.jpg"},
                    {"status": "ok", "local_path": "assets/shared.jpg", "note": "dedup"},
                ],
            )
            collect_web_pack.IMAGE_HASHES["own"] = "assets/own.jpg"
            collect_web_pack.IMAGE_HASHES["shared"] = "assets/shared.jpg"
            collect_web_pack.cleanup_page_images(out_dir, page)
            self.assertFalse(own.exists())
            self.assertTrue(shared.exists())
            self.assertNotIn("own", collect_web_pack.IMAGE_HASHES)
            self.assertIn("shared", collect_web_pack.IMAGE_HASHES)


if __name__ == "__main__":
    unittest.main()
