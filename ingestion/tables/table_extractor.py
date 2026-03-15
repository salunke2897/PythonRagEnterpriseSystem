import logging

logger = logging.getLogger(__name__)


class TableExtractor:
    @staticmethod
    def _to_markdown(rows: list[list[str]]) -> str:
        if not rows:
            return ""
        max_cols = max(len(r) for r in rows)
        normalized = [r + [""] * (max_cols - len(r)) for r in rows]
        header = normalized[0]
        body = normalized[1:] if len(normalized) > 1 else []
        md_header = "| " + " | ".join(header) + " |"
        md_sep = "| " + " | ".join(["---"] * len(header)) + " |"
        md_body = ["| " + " | ".join(r) + " |" for r in body]
        return "\n".join([md_header, md_sep, *md_body])

    def extract_markdown_tables(self, file_path: str) -> dict[int, list[str]]:
        output: dict[int, list[str]] = {}

        try:
            import camelot  # type: ignore

            tables = camelot.read_pdf(file_path, pages="all", flavor="stream")
            for table in tables:
                page = int(table.page or 1)
                df = table.df.fillna("")
                if df.empty:
                    continue
                rows = [list(map(str, row)) for row in df.values.tolist()]
                markdown = self._to_markdown(rows)
                if markdown:
                    output.setdefault(page, []).append(markdown)
        except Exception:
            logger.info("table_extraction_skipped")

        if output:
            return output

        try:
            import pdfplumber

            with pdfplumber.open(file_path) as pdf:
                for page_number, page in enumerate(pdf.pages, start=1):
                    extracted = page.extract_tables() or []
                    for table in extracted:
                        rows = [[(cell or "").strip() for cell in row] for row in table if row]
                        markdown = self._to_markdown(rows)
                        if markdown:
                            output.setdefault(page_number, []).append(markdown)
        except Exception:
            logger.info("pdfplumber_table_fallback_skipped")

        return output
