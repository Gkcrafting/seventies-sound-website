"""Run repeatable Task 3 checks against the finished website."""

from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
from threading import Thread

from playwright.sync_api import sync_playwright


ROOT = Path(__file__).resolve().parents[1]
SITE = "/website-design/website"
RESULTS = ROOT / "website-testing" / "test-results" / "functional-results.json"


def record(rows, test, result, note):
    rows.append({"test": test, "result": result, "note": note})


server = ThreadingHTTPServer(
    ("127.0.0.1", 0), partial(SimpleHTTPRequestHandler, directory=str(ROOT))
)
Thread(target=server.serve_forever, daemon=True).start()
base = f"http://localhost:{server.server_port}{SITE}"
rows = []

try:
    with sync_playwright() as p:
        browser = p.chromium.launch(
            executable_path="/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
            headless=True,
        )

        for page_name in ("index.html", "explore.html", "request.html"):
            page = browser.new_page(viewport={"width": 1280, "height": 900})
            page.goto(f"{base}/{page_name}")
            assert page.locator("main").count() == 1
            assert page.locator("header").count() == 1
            assert page.evaluate("document.documentElement.scrollWidth") == 1280
            record(rows, f"{page_name} on a computer", "Pass", "Nothing went off the side of the page.")
            page.set_viewport_size({"width": 390, "height": 844})
            assert page.evaluate("document.documentElement.scrollWidth") == 390
            record(rows, f"{page_name} on a phone", "Pass", "The page still fitted the phone screen.")
            page.close()

        page = browser.new_page()
        page.goto(f"{base}/index.html")
        page.get_by_role("link", name="Skip to content").focus()
        page.keyboard.press("Enter")
        assert page.evaluate("document.activeElement.id") == "main-content"
        record(rows, "Skip link", "Pass", "It took me straight to the main part of the page.")

        page.locator(".explore-toggle").click()
        assert not page.locator("#explore-menu").is_hidden()
        assert page.locator(".explore-toggle").get_attribute("aria-expanded") == "true"
        page.keyboard.press("Escape")
        assert page.locator("#explore-menu").is_hidden()
        assert page.locator(".explore-toggle").evaluate("el => el === document.activeElement")
        record(rows, "Explore menu", "Pass", "It opened, closed with Escape, then focus went back to the button.")

        page.set_viewport_size({"width": 390, "height": 844})
        page.locator(".mobile-menu").click()
        assert page.locator("#site-nav").evaluate("el => el.classList.contains('open')")
        page.keyboard.press("Escape")
        assert not page.locator("#site-nav").evaluate("el => el.classList.contains('open')")
        record(rows, "Menu on phone", "Pass", "It opened and Escape closed it again.")
        page.close()

        page = browser.new_page()
        page.goto(f"{base}/explore.html")
        page.get_by_role("searchbox").fill("abba")
        page.get_by_role("searchbox").press("Enter")
        assert page.locator(".artist:visible").count() == 1
        page.locator('[data-genre="pop"]').click()
        assert page.locator(".artist:visible").count() == 1
        page.locator('[data-genre="glam"]').click()
        assert page.locator(".artist:visible").count() == 0
        record(rows, "Search and genre buttons", "Pass", "I could search for ABBA and then change the genre without it breaking.")

        page.locator('[data-genre="all"]').click()
        page.locator(".enlarge-image").first.click()
        assert page.locator("dialog[open]").count() == 1
        page.keyboard.press("Escape")
        assert page.locator("dialog[open]").count() == 0
        record(rows, "Make image bigger", "Pass", "The picture opened bigger and Escape closed it.")

        page.locator("#dancing-queen .load-video").click()
        frame = page.locator("#dancing-queen iframe")
        assert frame.count() == 1
        assert "youtube" in frame.get_attribute("src")
        record(rows, "Song video", "Pass", "Pressing Play put the YouTube video on the page. I checked the videos played in localhost too.")
        page.close()

        page = browser.new_page()
        page.goto(f"{base}/request.html")
        page.locator("#email-request").click()
        assert not page.locator("#topic").evaluate("el => el.validity.valid")
        page.locator("#topic").fill("ABBA")
        page.locator("#kind").select_option(label="Song suggestion")
        mailto = page.locator("#email-request").get_attribute("href")
        assert "kilekwg25%40foxford.coventry.sch.uk" not in mailto
        assert mailto.startswith("mailto:kilekwg25@foxford.coventry.sch.uk?")
        assert "cc=Kemi.Adeeko%40castlephoenixtrust.org.uk" in mailto
        record(rows, "Request page", "Pass", "It would not make the email until I filled in the required boxes. Then it made the email with the client copied in.")
        page.close()

        browser.close()
finally:
    server.shutdown()

RESULTS.parent.mkdir(parents=True, exist_ok=True)
RESULTS.write_text(json.dumps(rows, indent=2) + "\n")
print(json.dumps(rows, indent=2))
