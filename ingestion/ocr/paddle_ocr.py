import io
import logging

import fitz
import numpy as np

logger = logging.getLogger(__name__)


class PaddleOCRExtractor:
    def __init__(self, lang: str = "en") -> None:
        self.lang = lang
        self._ocr = None

    def _get_ocr(self):
        if self._ocr is not None:
            return self._ocr
        try:
            from paddleocr import PaddleOCR  # type: ignore

            self._ocr = PaddleOCR(use_angle_cls=True, lang=self.lang, show_log=False)
            return self._ocr
        except Exception:
            logger.exception("paddle_ocr_initialization_failed")
            return None

    @staticmethod
    def _preprocess(image_bgr: np.ndarray) -> np.ndarray:
        import cv2

        gray = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2GRAY)
        denoised = cv2.GaussianBlur(gray, (3, 3), 0)
        return cv2.adaptiveThreshold(denoised, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 31, 3)

    def extract(self, file_path: str) -> dict[int, dict]:
        ocr_engine = self._get_ocr()
        if ocr_engine is None:
            return {}

        output: dict[int, dict] = {}
        with fitz.open(file_path) as doc:
            for page_number, page in enumerate(doc, start=1):
                pix = page.get_pixmap(dpi=220)
                image = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width, pix.n)
                if pix.n == 4:
                    image = image[:, :, :3]
                preprocessed = self._preprocess(image)

                result = ocr_engine.ocr(preprocessed, cls=True)
                lines = result[0] if result else []
                texts: list[str] = []
                boxes: list[list[list[float]]] = []
                for line in lines:
                    if not line or len(line) < 2:
                        continue
                    boxes.append(line[0])
                    texts.append((line[1] or [""])[0])

                output[page_number] = {"text": "\n".join(texts), "boxes": boxes}

        return output
