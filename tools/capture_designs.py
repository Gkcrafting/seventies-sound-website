from pathlib import Path
import json
from playwright.sync_api import sync_playwright

root = Path(__file__).resolve().parents[1] / "website-design"
results = []
with sync_playwright() as p:
    browser = p.chromium.launch(
        executable_path="/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
        headless=True,
    )
    for name in ("home-draft", "home", "explore", "request", "states"):
        for label, w, h in [("desktop", 1280, 960), ("mobile", 390, 844)]:
            page = browser.new_page(
                viewport={"width": w, "height": h}, device_scale_factor=1
            )
            folder = "draft-review" if name in ("home-draft", "states") else "website"
            filename = "index" if name == "home" else name
            page.goto((root / folder / f"{filename}.html").as_uri())
            page.screenshot(
                path=str(
                    root
                    / ("draft-review" if name == "home-draft" else "website/screenshots")
                    / f"{name}-{label}.png"
                ),
                full_page=True,
            )
            results.append(
                {
                    "page": name,
                    "view": label,
                    "width": w,
                    "page_width": page.evaluate("document.documentElement.scrollWidth"),
                    "height": page.evaluate("document.documentElement.scrollHeight"),
                }
            )
            page.close()
    page = browser.new_page(viewport={"width": 390, "height": 844})
    page.goto((root / "website/explore.html").as_uri())
    for index, button in enumerate(page.locator(".enlarge-image").all()):
        button.click()
        dialog = page.locator("dialog[open]")
        assert dialog.count() == 1
        assert dialog.locator("img").get_attribute("alt")
        credit_links = dialog.locator("figcaption a")
        if credit_links.count():
            assert credit_links.first.get_attribute("target") == "_blank"
        else:
            assert "Original Seventies Sound" in dialog.locator("figcaption").inner_text()
        assert dialog.evaluate("(el) => el.getBoundingClientRect().width") <= 390
        for _ in range(5):
            page.keyboard.press("Tab")
            assert dialog.evaluate("(el) => el.contains(document.activeElement)")
        page.keyboard.press("Escape")
        assert page.locator("dialog[open]").count() == 0
        assert button.evaluate("(el) => el === document.activeElement")
    page.locator(".enlarge-image").first.click()
    page.locator("dialog .close-image").click()
    assert page.locator("dialog[open]").count() == 0
    page.close()
    print(
        "Image popups passed: all photos, credits, mobile width, keyboard focus, Escape and Close."
    )

    page = browser.new_page()
    for origin in ("index", "request", "explore"):
        page.goto((root / "website" / f"{origin}.html").as_uri())
        page.get_by_role("searchbox").fill("  aBbA  ")
        page.get_by_role("searchbox").press("Enter")
        page.wait_for_url("**/explore.html?q=*")
        assert page.locator(".artist:visible").count() == 1
        assert page.locator("#pop").is_visible()
        assert page.locator(".music-sample:visible").count() == 1
    for query, artists, tracks in [
        ("Dancing Queen", 1, 1),
        ("notarealsong", 0, 0),
        ("Kevin MacLeod", 0, 0),
        ("xyzmissing", 0, 0),
        ("   ", 7, 7),
        ("<img src=x onerror=alert(1)>", 0, 0),
    ]:
        page.get_by_role("searchbox").fill(query)
        page.get_by_role("searchbox").press("Enter")
        assert page.locator(".artist:visible").count() == artists, query
        assert page.locator(".music-sample:visible").count() == tracks, query
        assert page.locator("#search-message img").count() == 0
    page.get_by_role("link", name="Show all music", exact=True).click()
    assert page.locator(".artist:visible").count() == 7
    assert page.locator(".music-sample:visible").count() == 7
    for genre, artist_count, track_count in [
        ("pop", 1, 1),
        ("glam", 1, 1),
        ("disco", 2, 2),
        ("rock", 1, 1),
        ("punk", 1, 1),
        ("reggae", 1, 1),
        ("funk", 1, 1),
        ("all", 7, 7),
    ]:
        page.locator(f'[data-genre="{genre}"]').click()
        assert page.locator(".artist:visible").count() == artist_count
        assert page.locator(".music-sample:visible").count() == track_count
        assert (
            page.locator(f'[data-genre="{genre}"]').get_attribute("aria-pressed")
            == "true"
        )
    page.get_by_role("searchbox").fill("ABBA")
    page.get_by_role("searchbox").press("Enter")
    page.locator('[data-genre="glam"]').click()
    assert page.locator(".music-sample:visible").count() == 0
    page.locator('[data-genre="pop"]').click()
    assert page.locator(".music-sample:visible").count() == 1
    page.reload()
    assert page.locator('[data-genre="pop"]').get_attribute("aria-pressed") == "true"
    page.go_back()
    assert page.locator('[data-genre="glam"]').get_attribute("aria-pressed") == "true"
    page.get_by_role("link", name="Show all music", exact=True).click()
    assert page.locator("iframe").count() == 0
    assert page.locator(".load-video").count() == 7
    page.locator("#dancing-queen .load-video").click()
    assert page.locator(".player-notice").count() == 1
    assert (
        page.locator(".player-notice a").get_attribute("href")
        == "http://localhost:5500/website-design/website/explore.html"
    )
    page.close()
    assert all(result["width"] == result["page_width"] for result in results)
    print(
        "Search passed from all pages, including song titles, whitespace, no matches, reset and plain-text output."
    )

    page = browser.new_page()
    page.goto((root / "website/request.html").as_uri())
    page.locator("#email-request").click()
    assert page.locator("#topic").evaluate("(el) => !el.validity.valid")
    page.locator("#topic").fill("ABBA & disco?")
    page.locator("#kind").select_option(index=1)
    page.locator("#reason").fill("More songs & photos, please.")
    from urllib.parse import urlparse, parse_qs

    link = urlparse(page.locator("#email-request").get_attribute("href"))
    assert link.path == "kilekwg25@foxford.coventry.sch.uk"
    query = parse_qs(link.query)
    assert query["subject"] == ["Seventies Sound request: ABBA & disco?"]
    assert "More songs & photos, please." in query["body"][0]
    print(
        "Email fields checked. Local files show the web preview link; HTTP playback is checked separately."
    )
    page.close()
    browser.close()
(root / "draft-review/layout-checks.json").write_text(json.dumps(results, indent=2))
print(json.dumps(results, indent=2))
