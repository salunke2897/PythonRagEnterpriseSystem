import re

from ingestion.ingestion_types import ParsedPage


class AdvancedTextCleaner:
    @staticmethod
    def _normalize(text: str) -> str:
        text = re.sub(r"[ \t]+", " ", text)
        text = re.sub(r"\n{3,}", "\n\n", text)
        return text.strip()

    def remove_headers_footers(self, pages: list[ParsedPage]) -> list[ParsedPage]:
        first_lines: dict[str, int] = {}
        last_lines: dict[str, int] = {}
        total_pages = len(pages)

        for page in pages:
            lines = [ln.strip() for ln in page.text.splitlines() if ln.strip()]
            if not lines:
                continue
            first_lines[lines[0]] = first_lines.get(lines[0], 0) + 1
            last_lines[lines[-1]] = last_lines.get(lines[-1], 0) + 1

        repeated_first = {k for k, v in first_lines.items() if v >= max(2, int(total_pages * 0.5))}
        repeated_last = {k for k, v in last_lines.items() if v >= max(2, int(total_pages * 0.5))}

        cleaned_pages: list[ParsedPage] = []
        for page in pages:
            lines = [ln.rstrip() for ln in page.text.splitlines()]
            if lines and lines[0].strip() in repeated_first:
                lines = lines[1:]
            if lines and lines[-1].strip() in repeated_last:
                lines = lines[:-1]
            page.text = self._normalize("\n".join(lines))
            cleaned_pages.append(page)
        return cleaned_pages
