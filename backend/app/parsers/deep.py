import re
from typing import List, Dict, Any
from app.schemas.ocr import OCRResult
from app.schemas.deep import DeepAnalysisResult, ContentBlock
from app.utils.logger import get_logger
from app.parsers.semantic import (
    is_question, is_alternative, is_cta, is_title, is_answer, is_list_item
)

# Regex mais precisas para evitar falsos positivos
_EMAIL_RE = re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")
_URL_RE = re.compile(r"^https?://[^\s]+$|^www\.[^\s]+$", re.IGNORECASE)
_PHONE_RE = re.compile(
    r"^(?:\+?55\s?)?(?:\(?\d{2}\)?\s?)?(?:9\d{4}|\d{4})[-.\s]?\d{4}$"
)


def classify_document_type(ocr_result: OCRResult, blocks: List[ContentBlock]) -> str:
    full_text_lower = ocr_result.text.lower()
    has_questions = sum(1 for b in blocks if b.type == "question")
    has_alternatives = sum(1 for b in blocks if b.type == "alternative")
    has_answers = sum(1 for b in blocks if b.type == "answer")
    has_ctas = sum(1 for b in blocks if b.type == "cta")
    has_titles = sum(1 for b in blocks if b.type == "title")
    has_links = sum(1 for b in blocks if b.type == "link")
    has_lists = sum(1 for b in blocks if b.type == "list_item")

    whatsapp_keywords = ["whatsapp", "wa.me", "encaminhada", "mensagem", "conversa"]
    telegram_keywords = ["telegram", "t.me", "mensagem", "encaminhada"]

    if any(k in full_text_lower for k in whatsapp_keywords):
        return "Conversa WhatsApp"
    if any(k in full_text_lower for k in telegram_keywords):
        return "Conversa Telegram"

    if has_questions > 0 and has_alternatives > 0:
        if has_answers > 0 or has_questions >= 3:
            return "Prova"
        return "Quiz"

    if has_questions > 0 and has_alternatives == 0:
        return "Questionário"

    if has_ctas > 1 and has_links > 0:
        return "Landing Page"

    if has_ctas > 0 and has_titles > 0:
        return "Página de vendas"

    if "@" in ocr_result.text and has_titles > 0:
        return "Formulário"

    if has_titles > 1 and has_questions == 0 and has_alternatives == 0:
        return "Artigo"

    if has_titles > 0 and has_lists > 0:
        return "Página de curso"

    return "Documento"


def build_structure(blocks: List[ContentBlock]) -> Dict[str, Any]:
    structure: Dict[str, Any] = {}
    current_section: str = "intro"
    section_idx = 0

    for block in blocks:
        if block.type == "title":
            section_idx += 1
            current_section = f"section_{section_idx}"
            structure[current_section] = {
                "title": block.text,
                "items": [],
            }
        else:
            if current_section not in structure:
                structure[current_section] = {"title": None, "items": []}
            structure[current_section]["items"].append({
                "type": block.type,
                "text": block.text,
            })

    return structure


def _compute_reading_order(blocks: List[ContentBlock]) -> List[int]:
    """Ordena blocos por posição Y (top) e depois X (left) para reading order real."""
    indexed = []
    for i, block in enumerate(blocks):
        if block.bbox and len(block.bbox) > 0:
            top = block.bbox[0][1]
            left = block.bbox[0][0]
        else:
            top = i * 1000  # fallback para preservar ordem original
            left = 0
        indexed.append((top, left, i))
    indexed.sort(key=lambda t: (t[0], t[1]))
    return [idx for _, _, idx in indexed]


def parse_deep(ocr_result: OCRResult) -> DeepAnalysisResult:
    logger = get_logger()
    blocks: List[ContentBlock] = []

    for idx, block in enumerate(ocr_result.blocks):
        text = block.text.strip()
        if not text:
            continue
        btype = "paragraph"

        if is_question(text):
            btype = "question"
        elif is_alternative(text):
            btype = "alternative"
        elif is_answer(text):
            btype = "answer"
        elif is_cta(text):
            btype = "cta"
        elif is_title(text, len(ocr_result.blocks), idx):
            btype = "title"
        elif is_list_item(text):
            btype = "list_item"
        elif _URL_RE.match(text):
            btype = "link"
        elif _EMAIL_RE.match(text):
            btype = "email"
        elif _PHONE_RE.match(text):
            btype = "phone"

        blocks.append(
            ContentBlock(
                type=btype,
                text=text,
                bbox=block.coordinates,
                confidence=block.confidence,
            )
        )

    doc_type = classify_document_type(ocr_result, blocks)
    structure = build_structure(blocks)
    reading_order = _compute_reading_order(blocks)

    logger.info(f"Análise profunda concluída: tipo={doc_type}, blocos={len(blocks)}")

    return DeepAnalysisResult(
        document_type=doc_type,
        structure=structure,
        reading_order=reading_order,
        content_blocks=blocks,
    )
