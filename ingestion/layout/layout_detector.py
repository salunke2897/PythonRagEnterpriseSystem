import logging

from ingestion.ingestion_types import LayoutBlock

logger = logging.getLogger(__name__)


class LayoutDetector:
    """Detect high-level layout blocks. Uses layoutparser when available."""

    def __init__(self) -> None:
        self._model = None

    def _get_model(self):
        if self._model is not None:
            return self._model
        try:
            import layoutparser as lp  # type: ignore

            self._model = lp.Detectron2LayoutModel(
                config_path="lp://PubLayNet/faster_rcnn_R_50_FPN_3x/config",
                label_map={0: "text", 1: "title", 2: "list", 3: "table", 4: "figure"},
            )
            return self._model
        except Exception:
            logger.info("layoutparser_model_unavailable_using_heuristic")
            return None

    def detect_from_text(self, page_text: str) -> list[LayoutBlock]:
        blocks: list[LayoutBlock] = []
        paragraphs = [p.strip() for p in page_text.split("\n\n") if p.strip()]
        for para in paragraphs:
            block_type = "title" if para.istitle() and len(para.split()) <= 12 else "paragraph"
            blocks.append(LayoutBlock(block_type=block_type, text=para))
        return blocks
