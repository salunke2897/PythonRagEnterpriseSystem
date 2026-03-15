from dataclasses import dataclass, field
from typing import Any


@dataclass
class LayoutBlock:
    block_type: str
    text: str
    bbox: tuple[float, float, float, float] | None = None
    score: float | None = None


@dataclass
class ParsedPage:
    page_number: int
    text: str
    words: list[dict[str, Any]] = field(default_factory=list)
    layout_blocks: list[LayoutBlock] = field(default_factory=list)


@dataclass
class ParsedDocument:
    parser_used: str
    pages: list[ParsedPage]
