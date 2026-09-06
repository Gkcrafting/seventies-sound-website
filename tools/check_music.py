"""Check the player from a real local web address, rather than a file URL."""

from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from threading import Thread
from playwright.sync_api import sync_playwright
import json
import sys

root = Path(__file__).resolve().parents[1]
server = ThreadingHTTPServer(
    ("127.0.0.1", 0), partial(SimpleHTTPRequestHandler, directory=str(root))
)
Thread(target=server.serve_forever, daemon=True).start()
checks = []
base_url = (
    sys.argv[1] if len(sys.argv) > 1 else f"http://localhost:{server.server_port}"
)
try:
    with sync_playwright() as p:
        browser = p.chromium.launch(
            executable_path="/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
            headless=True,
        )
        page = browser.new_page()
        page.set_default_timeout(7000)
        errors = []
        navigations = []
        page.on("framenavigated", lambda frame: navigations.append(frame.url) if frame == page.main_frame else None)
        page.on("pageerror", lambda error: errors.append(str(error)))
        page.goto(f"{base_url}/website-design/website/explore.html")
        for slug in (
            "dancing-queen", "starman", "i-feel-love", "dreams",
            "london-calling", "three-little-birds", "september",
        ):
            page.goto(f"{base_url}/website-design/website/explore.html")
            page.locator(f"#{slug} .load-video").click()
            iframe = page.locator(f"#{slug} iframe")
            assert iframe.count() == 1
            page.wait_for_timeout(12000)
            if iframe.count() == 0:
                checks.append({"song": slug, "page": page.url, "problem": "Player disappeared after page navigation/reload", "navigations": list(navigations), "errors": list(errors)})
                continue
            frame = iframe.element_handle().content_frame()
            status = frame.evaluate("""() => ({
                text: document.body.innerText.slice(0, 1000),
                response: window.ytInitialPlayerResponse?.playabilityStatus,
                playerResponse: window.ytplayer?.config?.args?.raw_player_response?.playabilityStatus,
                video: [...document.querySelectorAll('video')].map(v => ({time: v.currentTime, paused: v.paused, ready: v.readyState}))
            })""")
            checks.append(
                {
                    "song": slug,
                    "page": page.url,
                    "status": status,
                    "script_errors": list(errors),
                }
            )
        browser.close()
finally:
    server.shutdown()
(root / "website-design/draft-review/embed-checks.json").write_text(json.dumps(checks, indent=2))
print(json.dumps(checks, indent=2))
