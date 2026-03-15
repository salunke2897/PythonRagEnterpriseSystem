import logging

logger = logging.getLogger(__name__)


class TableExtractor:
    def extract_markdown_tables(self, file_path: str) -> dict[int, list[str]]:
        try:
            import camelot  # type: ignore

            tables = camelot.read_pdf(file_path, pages="all", flavor="stream")
        except Exception:
            logger.info("table_extraction_skipped")
            return {}

        output: dict[int, list[str]] = {}
        for table in tables:
            page = int(table.page or 1)
            df = table.df.fillna("")
            if df.empty:
                continue
            header = "| " + " | ".join(df.iloc[0].tolist()) + " |"
            sep = "| " + " | ".join(["---"] * len(df.columns)) + " |"
            body = ["| " + " | ".join(row.tolist()) + " |" for _, row in df.iloc[1:].iterrows()]
            markdown = "\n".join([header, sep, *body])
            output.setdefault(page, []).append(markdown)
        return output
