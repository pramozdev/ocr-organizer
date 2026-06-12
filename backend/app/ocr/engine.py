import numpy as np
import cv2
import pytesseract
from PIL import Image
from app.core.config import get_settings
from app.core.exceptions import OCRException
from app.schemas.ocr import OCRResult, OCRBlock
from app.utils.logger import get_logger


def _convert_to_pil(image: np.ndarray) -> Image.Image:
    if len(image.shape) == 2:
        return Image.fromarray(image)
    return Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))


def _group_words_into_lines(data: dict) -> list[dict]:
    """Agrupa palavras do Tesseract por block_num + line_num para preservar estrutura."""
    n_boxes = len(data["text"])
    lines_dict: dict[tuple[int, int], list[dict]] = {}

    for i in range(n_boxes):
        text = data["text"][i].strip()
        conf = int(data["conf"][i])
        if not text or conf < 0:
            continue
        block_num = data["block_num"][i]
        line_num = data["line_num"][i]
        key = (block_num, line_num)

        if key not in lines_dict:
            lines_dict[key] = []
        lines_dict[key].append({
            "text": text,
            "conf": conf,
            "left": data["left"][i],
            "top": data["top"][i],
            "width": data["width"][i],
            "height": data["height"][i],
        })

    # Ordenar linhas por posição vertical (top) e depois horizontal (left da primeira palavra)
    sorted_keys = sorted(lines_dict.keys(), key=lambda k: (lines_dict[k][0]["top"], lines_dict[k][0]["left"]))
    return [lines_dict[k] for k in sorted_keys]


def _build_line_block(words: list[dict]) -> tuple[OCRBlock, float]:
    """Constroi um OCRBlock a partir de uma linha de palavras."""
    full_line_text = " ".join(w["text"] for w in words)
    min_x = min(w["left"] for w in words)
    min_y = min(w["top"] for w in words)
    max_x = max(w["left"] + w["width"] for w in words)
    max_y = max(w["top"] + w["height"] for w in words)
    avg_conf = sum(w["conf"] for w in words) / len(words)

    coordinates = [
        [float(min_x), float(min_y)],
        [float(max_x), float(min_y)],
        [float(max_x), float(max_y)],
        [float(min_x), float(max_y)],
    ]

    block = OCRBlock(
        text=full_line_text,
        confidence=round(avg_conf / 100.0, 4),
        coordinates=coordinates,
    )
    return block, avg_conf / 100.0


def run_ocr(image: np.ndarray) -> OCRResult:
    logger = get_logger()
    settings = get_settings()
    try:
        pil_image = _convert_to_pil(image)

        data = pytesseract.image_to_data(
            pil_image,
            lang=settings.OCR_LANG,
            output_type=pytesseract.Output.DICT,
        )

        lines = _group_words_into_lines(data)
        blocks: list[OCRBlock] = []
        line_texts: list[str] = []
        total_confidence = 0.0
        count = 0

        for words in lines:
            block, norm_conf = _build_line_block(words)
            blocks.append(block)
            line_texts.append(block.text)
            total_confidence += norm_conf
            count += 1

        avg_confidence = total_confidence / count if count > 0 else 0.0
        full_text = "\n".join(line_texts)

        return OCRResult(
            text=full_text,
            confidence=round(avg_confidence, 4),
            blocks=blocks,
        )
    except Exception as e:
        logger.error(f"Erro no OCR: {e}")
        raise OCRException(f"Falha no OCR: {e}") from e
