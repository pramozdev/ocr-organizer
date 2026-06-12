from typing import Optional
from fastapi import APIRouter, UploadFile, File, Form
from app.schemas.preprocess import PreprocessOptions
from app.schemas.response import AnalyzeResponse, DeepAnalyzeResponse
from app.schemas.ai_local import AIInterpretResponse
from app.services.analyzer import analyze_image
from app.ai_local.interpreter import interpret_ocr_result
from app.utils.logger import get_logger

router = APIRouter()
logger = get_logger()


def _build_preprocess_options(
    grayscale: bool = True,
    threshold: bool = False,
    denoise: bool = True,
    sharpen: bool = True,
    resize: bool = True,
    deskew: bool = True,
) -> PreprocessOptions:
    return PreprocessOptions(
        grayscale=grayscale,
        threshold=threshold,
        denoise=denoise,
        sharpen=sharpen,
        resize=resize,
        deskew=deskew,
    )


@router.get("/health", response_model=dict)
async def health_check() -> dict:
    return {"status": "ok"}


@router.post("/analyze", response_model=AnalyzeResponse)
async def analyze(
    file: UploadFile = File(...),
    grayscale: bool = Form(True),
    threshold: bool = Form(False),
    denoise: bool = Form(True),
    sharpen: bool = Form(True),
    resize: bool = Form(True),
    deskew: bool = Form(True),
) -> AnalyzeResponse:
    options = _build_preprocess_options(grayscale, threshold, denoise, sharpen, resize, deskew)
    return await analyze_image(file, options=options, deep=False)


@router.post("/analyze/deep", response_model=DeepAnalyzeResponse)
async def analyze_deep(
    file: UploadFile = File(...),
    grayscale: bool = Form(True),
    threshold: bool = Form(False),
    denoise: bool = Form(True),
    sharpen: bool = Form(True),
    resize: bool = Form(True),
    deskew: bool = Form(True),
) -> DeepAnalyzeResponse:
    options = _build_preprocess_options(grayscale, threshold, denoise, sharpen, resize, deskew)
    return await analyze_image(file, options=options, deep=True)


@router.post("/ai/analyze", response_model=AIInterpretResponse)
async def ai_analyze(
    file: UploadFile = File(...),
    mode: str = Form("full"),
    context: Optional[str] = Form(None),
    grayscale: bool = Form(True),
    threshold: bool = Form(False),
    denoise: bool = Form(True),
    sharpen: bool = Form(True),
    resize: bool = Form(True),
    deskew: bool = Form(True),
) -> AIInterpretResponse:
    """Faz OCR e retorna o resultado + um prompt formatado para IA local interpretar."""
    options = _build_preprocess_options(grayscale, threshold, denoise, sharpen, resize, deskew)
    result = await analyze_image(file, options=options, deep=True)
    prompt = interpret_ocr_result(result, mode=mode, context=context)
    return AIInterpretResponse(
        success=True,
        filename=result.filename,
        ocr_result=result,
        prompt_for_ai=prompt,
        mode=mode,
        context=context,
    )


@router.post("/ai/summary", response_model=AIInterpretResponse)
async def ai_summary(
    file: UploadFile = File(...),
    context: Optional[str] = Form(None),
    grayscale: bool = Form(True),
    threshold: bool = Form(False),
    denoise: bool = Form(True),
    sharpen: bool = Form(True),
    resize: bool = Form(True),
    deskew: bool = Form(True),
) -> AIInterpretResponse:
    """Faz OCR e retorna um prompt de resumo para IA local."""
    options = _build_preprocess_options(grayscale, threshold, denoise, sharpen, resize, deskew)
    result = await analyze_image(file, options=options, deep=False)
    prompt = interpret_ocr_result(result, mode="summary", context=context)
    return AIInterpretResponse(
        success=True,
        filename=result.filename,
        ocr_result=result,
        prompt_for_ai=prompt,
        mode="summary",
        context=context,
    )
