from typing import Optional
from app.schemas.response import AnalyzeResponse, DeepAnalyzeResponse
from app.ai_local.prompt_builder import build_analysis_prompt, build_summary_prompt
from app.utils.logger import get_logger


def interpret_ocr_result(
    response: AnalyzeResponse | DeepAnalyzeResponse,
    mode: str = "full",
    context: Optional[str] = None,
) -> str:
    """Gera um prompt otimizado para IA local interpretar o resultado OCR.

    Args:
        response: Resultado da analise OCR (padrao ou profunda).
        mode: Modo de interpretacao - 'full' (analise completa) ou 'summary' (resumo rapido).
        context: Contexto adicional fornecido pelo usuario.

    Returns:
        String contendo o prompt formatado para a IA local.
    """
    logger = get_logger()
    logger.info(f"Gerando prompt para IA local (mode={mode})")

    if mode == "summary":
        return build_summary_prompt(response)

    return build_analysis_prompt(response, context=context)
