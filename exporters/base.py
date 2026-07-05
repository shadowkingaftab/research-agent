from pathlib import Path


class Exporter:

    def __init__(self):

        self.output_dir = Path("exports")
        self.output_dir.mkdir(exist_ok=True)

    def safe_filename(self, text):

        text = text.lower()

        for c in '<>:"/\\|?*':
            text = text.replace(c, "_")

        text = text.replace(" ", "_")

        return text[:80]