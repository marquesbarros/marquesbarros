"""Local browser checks. Run with Python + Playwright, no site dependencies.

Start python -m http.server 8765 --bind 127.0.0.1 in the repository first.
"""
import base64
import hashlib
import unittest
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import unquote, urlsplit

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
BASE = "http://127.0.0.1:8765/"
PAGES = ("index.html", "curriculo.html", "en/index.html", "en/cv.html")


class References(HTMLParser):
    def __init__(self):
        super().__init__()
        self.paths = []
        self.ids = []
        self.canonical = []
        self.languages = set()

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if "id" in attrs:
            self.ids.append(attrs["id"])
        for key in ("src", "href"):
            if key in attrs:
                self.paths.append(attrs[key])
        if attrs.get("rel") == "canonical":
            self.canonical.append(attrs["href"])
        if attrs.get("rel") == "alternate":
            self.languages.add(attrs.get("hreflang"))


class SiteChecks(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pw = sync_playwright().start()
        cls.browser = cls.pw.chromium.launch()

    @classmethod
    def tearDownClass(cls):
        cls.browser.close()
        cls.pw.stop()

    def context(self, **options):
        context = self.browser.new_context(**options)
        # Checks must also work offline; only the local static server is allowed.
        context.route("**/*", lambda route: route.continue_()
                      if route.request.url.startswith(BASE) else route.abort())
        self.addCleanup(context.close)
        return context

    def test_navigation_and_images_work_without_javascript(self):
        context = self.context(java_script_enabled=False)
        for path in PAGES:
            with self.subTest(page=path):
                page = context.new_page()
                self.assertEqual(page.goto(BASE + path).status, 200)
                self.assertTrue(page.get_by_role("navigation").first.is_visible())
                self.assertEqual(page.locator("h1").count(), 1)
                for img in page.locator("img").all():
                    img.scroll_into_view_if_needed()
                page.wait_for_function("Array.from(document.images).every(i => i.complete)")
                self.assertEqual(page.locator("img").evaluate_all(
                    "imgs => imgs.filter(i => !i.naturalWidth || !i.alt || !i.width || !i.height).length"), 0)
                self.assertEqual(page.locator("iframe").count(), 0)
                for anchor in page.locator('a[href*="#"]').all():
                    href = anchor.get_attribute("href")
                    target, fragment = href.split("#", 1)
                    target_page = page if not target else context.new_page()
                    if target:
                        target_page.goto(page.url.rsplit("/", 1)[0] + "/" + target)
                    self.assertEqual(target_page.locator(f'[id="{fragment}"]').count(), 1, href)
                    if target:
                        target_page.close()
                page.close()

    def test_responsive_layout_and_console(self):
        context = self.context(reduced_motion="reduce")
        for path in PAGES:
            for width in (320, 360, 390, 768, 1024, 1440):
                with self.subTest(page=path, width=width):
                    page = context.new_page()
                    page.set_viewport_size({"width": width, "height": 900})
                    errors = []
                    page.on("pageerror", lambda error: errors.append(str(error)))
                    self.assertEqual(page.goto(BASE + path).status, 200)
                    self.assertLessEqual(page.evaluate("document.documentElement.scrollWidth"), width)
                    self.assertEqual(errors, [])
                    self.assertEqual(page.locator(".topography").evaluate_all(
                        "els => els.filter(e => getComputedStyle(e).animationName !== 'none').length"), 0)
                    page.close()

    def test_mobile_menu_keyboard_and_resize(self):
        page = self.context(viewport={"width": 390, "height": 844}).new_page()
        page.goto(BASE)
        page.keyboard.press("Tab")
        self.assertEqual(page.locator(":focus").get_attribute("class"), "skip")
        button = page.get_by_role("button", name="Menu")
        button.focus()
        page.keyboard.press("Enter")
        self.assertEqual(button.get_attribute("aria-expanded"), "true")
        page.keyboard.press("Escape")
        self.assertEqual(button.get_attribute("aria-expanded"), "false")
        self.assertTrue(button.evaluate("e => e === document.activeElement"))
        button.click()
        page.get_by_role("navigation").get_by_role("link", name="Pesquisa", exact=True).click()
        self.assertEqual(button.get_attribute("aria-expanded"), "false")
        self.assertEqual(page.locator(":focus").get_attribute("id"), "pesquisa")
        page.set_viewport_size({"width": 1440, "height": 900})
        self.assertTrue(page.get_by_role("navigation").get_by_role("link", name="Pesquisa", exact=True).is_visible())

    def test_scientific_figures_are_byte_identical(self):
        for name in ("saa-targets", "tcc-prediction", "riima-interface"):
            source = base64.b64decode("".join(p.read_text().strip()
                for p in sorted((ROOT / "assets" / name).glob("chunk-*.txt"))))
            self.assertEqual(hashlib.sha256(source).digest(),
                hashlib.sha256((ROOT / "assets" / (name + ".webp")).read_bytes()).digest())

    def test_local_resources_and_language_metadata(self):
        for name in PAGES:
            with self.subTest(page=name):
                file = ROOT / name
                parsed = References()
                parsed.feed(file.read_text(encoding="utf-8"))
                self.assertEqual(len(parsed.ids), len(set(parsed.ids)))
                self.assertEqual(len(parsed.canonical), 1)
                self.assertEqual(parsed.languages, {"pt-BR", "en", "x-default"})
                for ref in parsed.paths:
                    url = urlsplit(ref)
                    if not url.scheme and url.path:
                        self.assertTrue((file.parent / unquote(url.path)).exists(), ref)


if __name__ == "__main__":
    unittest.main(verbosity=2)
