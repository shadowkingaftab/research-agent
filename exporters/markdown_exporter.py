from exporters.base import Exporter


class MarkdownExporter(Exporter):

    def export(self, title, report):

        filename = self.safe_filename(title) + ".md"

        path = self.output_dir / filename

        with open(path, "w", encoding="utf-8") as f:
            f.write(report)

        return path