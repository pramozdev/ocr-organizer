from app.ai_local.prompt_builder import build_analysis_prompt, build_summary_prompt
from app.ai_local.interpreter import interpret_ocr_result
from app.schemas.ocr import OCRResult, OCRBlock
from app.schemas.content import ContentExtraction
from app.schemas.response import AnalyzeResponse


def make_sample_response() -> AnalyzeResponse:
    return AnalyzeResponse(
        success=True,
        filename="teste.png",
        ocr=OCRResult(
            text="Titulo do Documento\nQual a capital do Brasil?\nA) Sao Paulo\nB) Brasilia\nClique aqui para saber mais\ncontato@email.com\nhttps://site.com\n(11) 98765-4321",
            confidence=0.96,
            blocks=[
                OCRBlock(text="Titulo do Documento", confidence=0.99, coordinates=[[0,0],[1,0],[1,1],[0,1]]),
                OCRBlock(text="Qual a capital do Brasil?", confidence=0.98, coordinates=[]),
                OCRBlock(text="A) Sao Paulo", confidence=0.97, coordinates=[]),
                OCRBlock(text="B) Brasilia", confidence=0.97, coordinates=[]),
                OCRBlock(text="Clique aqui para saber mais", confidence=0.95, coordinates=[]),
                OCRBlock(text="contato@email.com", confidence=0.99, coordinates=[]),
                OCRBlock(text="https://site.com", confidence=0.99, coordinates=[]),
                OCRBlock(text="(11) 98765-4321", confidence=0.98, coordinates=[]),
            ]
        ),
        content=ContentExtraction(
            titles=["Titulo do Documento"],
            questions=["Qual a capital do Brasil?"],
            alternatives=["A) Sao Paulo", "B) Brasilia"],
            answers=[],
            lists=[],
            links=["https://site.com"],
            emails=["contato@email.com"],
            phones=["(11) 98765-4321"],
            ctas=["Clique aqui para saber mais"],
        )
    )


def test_build_analysis_prompt():
    response = make_sample_response()
    prompt = build_analysis_prompt(response)
    assert "Titulo do Documento" in prompt
    assert "Qual a capital do Brasil?" in prompt
    assert "A) Sao Paulo" in prompt
    assert "Clique aqui para saber mais" in prompt
    assert "contato@email.com" in prompt
    assert "https://site.com" in prompt
    assert "(11) 98765-4321" in prompt
    assert "## Instrucoes para IA Local" in prompt


def test_build_analysis_prompt_with_context():
    response = make_sample_response()
    prompt = build_analysis_prompt(response, context="Pagina de quiz")
    assert "Pagina de quiz" in prompt
    assert "## Contexto Adicional do Usuario" in prompt


def test_build_summary_prompt():
    response = make_sample_response()
    prompt = build_summary_prompt(response)
    assert "Resuma" in prompt
    assert "teste.png" in prompt
    assert "Titulo do Documento" in prompt


def test_interpret_ocr_result_full():
    response = make_sample_response()
    prompt = interpret_ocr_result(response, mode="full")
    assert "Instrucoes para IA Local" in prompt


def test_interpret_ocr_result_summary():
    response = make_sample_response()
    prompt = interpret_ocr_result(response, mode="summary")
    assert "Resuma" in prompt
