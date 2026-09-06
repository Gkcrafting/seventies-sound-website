from pathlib import Path
from playwright.sync_api import sync_playwright
import json

out = Path("planning-and-research/research-notes")
sites = {
    "abba": "https://abbasite.com/",
    "great70s": "https://thegreat70s.com/70s-pop-music.html",
    "rockhall": "https://rockhall.com/inductees/inductees/",
}
results = []
with sync_playwright() as p:
    browser = p.chromium.launch(
        executable_path="/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
        headless=True,
    )
    for name, url in sites.items():
        for label, width, height in [("desktop", 1440, 1000), ("mobile", 390, 844)]:
            page = browser.new_page(
                viewport={"width": width, "height": height}, device_scale_factor=1
            )
            try:
                response = page.goto(url, wait_until="domcontentloaded", timeout=60000)
                page.wait_for_timeout(3000)
                for text in ["Do not consent", "Deny", "REJECT"]:
                    button = page.get_by_role("button", name=text, exact=True)
                    if button.count() and button.first.is_visible():
                        button.first.click()
                        page.wait_for_timeout(800)
                        break
                page.screenshot(path=str(out / f"{name}-{label}.png"))
                results.append(
                    {
                        "site": name,
                        "viewport": label,
                        "url": page.url,
                        "status": response.status,
                        "width": width,
                        "scrollWidth": page.evaluate(
                            "document.documentElement.scrollWidth"
                        ),
                    }
                )
            except Exception as e:
                results.append({"site": name, "error": str(e)})
            page.close()
    browser.close()
(out / "observations.json").write_text(json.dumps(results, indent=2))
print(json.dumps(results, indent=2))
