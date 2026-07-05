import trafilatura


def get_page_text(url: str) -> str:

    try:

        downloaded = trafilatura.fetch_url(url)

        if not downloaded:
            return ""

        text = trafilatura.extract(downloaded)

        return text or ""

    except Exception as e:

        print("Crawler Error:", e)

        return ""