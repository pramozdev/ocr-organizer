from app.parsers.semantic import (
    is_question, is_alternative, is_cta, is_title, is_answer, is_list_item,
    extract_links, extract_emails, extract_phones, parse_semantic
)
from app.schemas.ocr import OCRResult, OCRBlock


def test_is_question():
    assert is_question("Qual é a capital do Brasil?")
    assert is_question("Como funciona o sistema?")
    assert is_question("O que é Python?")
    assert not is_question("A capital é Brasília.")


def test_is_alternative():
    assert is_alternative("A) São Paulo")
    assert is_alternative("b) Rio de Janeiro")
    assert is_alternative("1) Alternativa um")
    assert not is_alternative("Texto qualquer")


def test_is_cta():
    assert is_cta("Clique aqui para saber mais")
    assert is_cta("Comprar agora")
    assert not is_cta("Texto informativo")


def test_is_title():
    assert is_title("TÍTULO IMPORTANTE", 5, 0)
    assert not is_title("Texto comum no meio", 10, 5)


def test_is_answer():
    assert is_answer("Resposta: Brasília")
    assert is_answer("A: São Paulo")
    assert not is_answer("Pergunta: Qual a capital?")


def test_is_list_item():
    assert is_list_item("- Item 1")
    assert is_list_item("* Item 2")
    assert is_list_item("1. Item numerado")
    assert not is_list_item("Texto normal")


def test_extract_links():
    assert extract_links("Visite https://example.com") == ["https://example.com"]
    assert extract_links("Site: www.test.com.br") == ["www.test.com.br"]


def test_extract_emails():
    assert extract_emails("Contato: email@test.com") == ["email@test.com"]


def test_extract_phones():
    assert len(extract_phones("Ligue: (11) 98765-4321")) > 0
    assert len(extract_phones("Tel: +55 11 98765-4321")) > 0


def test_parse_semantic():
    ocr = OCRResult(
        text="Título\nQual a capital?\nA) São Paulo\nB) Brasília\nClique aqui\nemail@test.com\nhttps://site.com\n(11) 98765-4321\n- Lista 1",
        confidence=0.95,
        blocks=[
            OCRBlock(text="Título", confidence=0.99, coordinates=[[0,0],[1,0],[1,1],[0,1]]),
            OCRBlock(text="Qual a capital?", confidence=0.98, coordinates=[]),
            OCRBlock(text="A) São Paulo", confidence=0.97, coordinates=[]),
            OCRBlock(text="B) Brasília", confidence=0.97, coordinates=[]),
            OCRBlock(text="Clique aqui", confidence=0.96, coordinates=[]),
            OCRBlock(text="email@test.com", confidence=0.99, coordinates=[]),
            OCRBlock(text="https://site.com", confidence=0.99, coordinates=[]),
            OCRBlock(text="(11) 98765-4321", confidence=0.98, coordinates=[]),
            OCRBlock(text="- Lista 1", confidence=0.95, coordinates=[]),
        ]
    )
    content = parse_semantic(ocr)
    assert "Título" in content.titles
    assert "Qual a capital?" in content.questions
    assert "A) São Paulo" in content.alternatives
    assert "Clique aqui" in content.ctas
    assert "email@test.com" in content.emails
    assert "https://site.com" in content.links
    assert "(11) 98765-4321" in content.phones
    assert "- Lista 1" in content.lists
