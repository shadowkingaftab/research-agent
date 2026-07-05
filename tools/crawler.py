from playwright.sync_api import sync_playwright
import trafilatura

def get_page_text(url):
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()

            page.goto(url, timeout=60000)

            html = page.content()

            browser.close()

        text = trafilatura.extract(html)

        return text if text else ""

    except Exception as e:
        return f"ERROR: {e}"