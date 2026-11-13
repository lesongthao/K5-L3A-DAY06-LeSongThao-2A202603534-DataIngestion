"""Optional real-browser smoke test; uses an existing Edge/Chromium installation."""
from pathlib import Path
import sys
import threading

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from demo.server import DemoServer, DemoState


def main():
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        raise SystemExit("Optional UI test needs playwright; HTTP tests do not.")
    server = DemoServer(("127.0.0.1", 0), DemoState())
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        with sync_playwright() as p:
            candidates = [Path(p.chromium.executable_path),
                          Path("C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe"),
                          Path("C:/Program Files/Microsoft/Edge/Application/msedge.exe")]
            browser_path = next((path for path in candidates if path.is_file()), None)
            if not browser_path:
                raise SystemExit("No existing browser available; install one separately to run optional UI QA.")
            browser = p.chromium.launch(executable_path=str(browser_path), headless=True)
            page = browser.new_page(viewport={"width": 1440, "height": 1000}, device_scale_factor=1)
            errors = []
            page.on("pageerror", lambda error: errors.append(str(error)))
            page.goto(f"http://127.0.0.1:{server.server_address[1]}")
            page.wait_for_function("document.body.classList.contains('ready')")
            assert page.locator(".strategy-card").count() == 3
            assert page.locator("#questionSelect").input_value() == "q08"
            page.select_option("#questionSelect", "q20")
            assert page.locator(".strategy-b mark").count() >= 2
            page.click('[data-split="test"]')
            assert page.locator("#questionSelect option").count() == 5
            page.fill("#questionFilter", "no-match-987654")
            assert page.locator("#questionSelect").is_disabled()
            page.fill("#questionFilter", "")
            page.click('[data-strategy="a"]')
            assert page.locator(".strategy-card").count() == 1
            page.click('[data-view="overview"]')
            page.click('[data-metric-split="test"]')
            assert page.locator("#metricsBody tr").count() == 3
            assert page.locator("#metricsBody").inner_text().count("5/5") >= 4
            page.click('[data-view="audit"]')
            assert page.locator("#coherenceSamples>details").count() == 10
            assert page.locator("#groundingSamples>details").count() == 5
            with page.expect_download() as download:
                page.click("#exportAudit")
            assert download.value.suggested_filename == "day06-audit-labels.json"
            page.click('[data-view="explorer"]')
            page.click("#liveTab")
            assert page.locator("#liveSubmit").is_disabled()
            page.click("#recordedTab")
            page.click('[data-split="all"]')
            page.click('[data-strategy="all"]')
            page.select_option("#questionSelect", "q08")
            # Source text must remain text, even if a future corpus contains HTML.
            safe = page.evaluate("""() => {
                const n = highlight('<img src=x onerror=alert(1)>', []);
                return n.querySelectorAll('img,script').length === 0 && n.textContent.includes('<img');
            }""")
            assert safe
            (ROOT / "assets").mkdir(exist_ok=True)
            page.evaluate("scrollTo(0, 0); document.activeElement.blur()")
            page.screenshot(path=str(ROOT / "assets/demo-desktop.png"), full_page=True)
            page.set_viewport_size({"width": 390, "height": 844})
            page.evaluate("scrollTo(0, 0); document.activeElement.blur()")
            assert page.evaluate("document.documentElement.scrollWidth <= innerWidth")
            page.screenshot(path=str(ROOT / "assets/demo-mobile.png"), full_page=True)
            assert not errors, errors
            browser.close()
            print("PASS: desktop/mobile UI, split/search, strategy compare, overview, audit export, disabled live and safe text rendering")
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)


if __name__ == "__main__":
    main()
