import re
from typing import List
from app.schemas.ocr import OCRResult
from app.schemas.content import ContentExtraction
from app.utils.logger import get_logger

QUESTION_PATTERNS = [
    re.compile(r"^\s*(?:\d+\.)?\s*(?:Qual|Quais|Como|Quando|Onde|Quem|Por\s*que|Porque|Porquê|Porquê|O\s*que|Oque|oq)\b", re.IGNORECASE),
    re.compile(r"^\s*(?:\d+\.)?\s*.*\?\s*$"),
]

ALTERNATIVE_PATTERNS = [
    re.compile(r"^\s*(?:[A-Da-d])\s*[\.\)\-:]\s+"),
    re.compile(r"^\s*(?:\d+)\s*[\.\)\-:]\s+"),
]

CTA_KEYWORDS = [
    "clique aqui", "comprar agora", "inscreva-se", "inscrever-se",
    "saiba mais", "acessar", "entrar", "começar agora", "comece agora",
    "quero agora", "assinar", "cadastrar", "baixar agora", "garantir",
    "quero participar", "fazer parte", "quero aprender", "mais informações",
]

LINK_PATTERN = re.compile(r"https?://[^\s]+|www\.[^\s]+", re.IGNORECASE)
EMAIL_PATTERN = re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}")
PHONE_PATTERN_BR = re.compile(
    r"(?:\+?55\s?)?(?:\(?\d{2}\)?\s?)?(?:9\d{4}|\d{4})[-.\s]?\d{4}",
    re.IGNORECASE,
)
PHONE_PATTERN_INTL = re.compile(r"\+\d{1,3}[\s\-]?\(?\d{1,4}\)?[\s\-]?\d{1,4}[\s\-]?\d{1,9}")

TITLE_PATTERNS = [
    re.compile(r"^\s*(?:[A-Z][A-Z\s]{2,})\s*$"),
    re.compile(r"^\s*(?:\d+\.)?\s*(?:[A-Z][a-z]+(?:\s+[A-Z][a-z]+){0,5})\s*$"),
]

ANSWER_PATTERNS = [
    re.compile(r"^\s*(?:Resposta|Answer|R:\s*|A:\s*|Resposta correta)\s*:?\s*", re.IGNORECASE),
]

LIST_PATTERNS = [
    re.compile(r"^\s*(?:[\-\*•◦▸▹→⇒])\s+"),
    re.compile(r"^\s*(?:\d+\.)\s+"),
]


def is_question(text: str) -> bool:
    return any(p.search(text) for p in QUESTION_PATTERNS)


def is_alternative(text: str) -> bool:
    return any(p.search(text) for p in ALTERNATIVE_PATTERNS)


def is_cta(text: str) -> bool:
    lower = text.lower()
    return any(kw in lower for kw in CTA_KEYWORDS)


def is_title(text: str, block_count: int, index: int) -> bool:
    stripped = text.strip()
    # Só considera os primeiros blocos como título se parecerem com título (maiusculas ou curtos significativos)
    if index < min(2, block_count):
        if 5 < len(stripped) < 80 and stripped[-1] not in "?.!":
            # Precisa ter algum sinal de título: todas maiúsculas, ou começar com maiúscula sem ponto final
            if stripped.isupper():
                return True
            if stripped[0].isupper() and stripped[-1] not in ".":
                return True
    for p in TITLE_PATTERNS:
        if p.search(text):
            return True
    return False


def is_answer(text: str) -> bool:
    return any(p.search(text) for p in ANSWER_PATTERNS)


def is_list_item(text: str) -> bool:
    return any(p.search(text) for p in LIST_PATTERNS)


def extract_links(text: str) -> List[str]:
    return LINK_PATTERN.findall(text)


def extract_emails(text: str) -> List[str]:
    return EMAIL_PATTERN.findall(text)


def extract_phones(text: str) -> List[str]:
    found = PHONE_PATTERN_BR.findall(text)
    found += PHONE_PATTERN_INTL.findall(text)
    return list(dict.fromkeys(found))


def parse_semantic(ocr_result: OCRResult) -> ContentExtraction:
    content = ContentExtraction()
    blocks = ocr_result.blocks
    block_count = len(blocks)

    for idx, block in enumerate(blocks):
        text = block.text
        if not text or not text.strip():
            continue

        content.links.extend(extract_links(text))
        content.emails.extend(extract_emails(text))
        content.phones.extend(extract_phones(text))

        if is_question(text):
            content.questions.append(text.strip())
        elif is_alternative(text):
            content.alternatives.append(text.strip())
        elif is_answer(text):
            content.answers.append(text.strip())
        elif is_cta(text):
            content.ctas.append(text.strip())
        elif is_list_item(text):
            content.lists.append(text.strip())
        elif is_title(text, block_count, idx):
            content.titles.append(text.strip())

    content.links = list(dict.fromkeys(content.links))
    content.emails = list(dict.fromkeys(content.emails))
    content.phones = list(dict.fromkeys(content.phones))
    content.questions = list(dict.fromkeys(content.questions))
    content.alternatives = list(dict.fromkeys(content.alternatives))
    content.answers = list(dict.fromkeys(content.answers))
    content.ctas = list(dict.fromkeys(content.ctas))
    content.lists = list(dict.fromkeys(content.lists))
    content.titles = list(dict.fromkeys(content.titles))

    get_logger().info(f"Parsing semântico concluído: {len(content.questions)} perguntas, {len(content.alternatives)} alternativas, {len(content.titles)} títulos")
    return content
