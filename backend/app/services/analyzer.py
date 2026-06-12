import asyncio
import io
import cv2
import numpy as np
from PIL import Image
from fastapi import UploadFile
from app.schemas.preprocess import PreprocessOptions
from app.schemas.response import AnalyzeResponse, DeepAnalyzeResponse
from app.vision.preprocessor import preprocess_image
from app.ocr.engine import run_ocr
from app.parsers.semantic import parse_semantic
from app.parsers.deep import parse_deep
from app.utils.file_validator import validate_image_file, validate_image_bytes
from app.utils.logger import get_logger


def _bytes_to_cv_image(content: bytes) -> np.ndarray:
    """Converte bytes de imagem para array OpenCV."""
    image = Image.open(io.BytesIO(content))
    if image.mode in ("RGBA", "P"):
        image = image.convert("RGB")
    return cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)


async def _run_in_executor(func, *args):
    """Executa função síncrona em thread pool para não bloquear o event loop."""
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, func, *args)


async def analyze_image(
    file: UploadFile | bytes,
    options: PreprocessOptions = PreprocessOptions(),
    deep: bool = False,
    filename: str | None = None,
) -> AnalyzeResponse | DeepAnalyzeResponse:
    logger = get_logger()

    if hasattr(file, "filename"):
        # UploadFile / qualquer objeto file-like com metadata
        upload = file  # type: ignore
        fname = upload.filename or filename or "unknown"
        content = await upload.read()
    else:
        fname = filename or "unknown"
        content = file  # type: ignore

    validate_image_file(fname, len(content))
    validate_image_bytes(content, fname)

    logger.info(f"Analisando imagem: {fname} ({len(content)} bytes)")

    # Conversão síncrona (rápida, mas ainda assim em executor)
    cv_image = await _run_in_executor(_bytes_to_cv_image, content)

    # Preprocessamento e OCR em thread pool
    processed = await _run_in_executor(preprocess_image, cv_image, options)
    ocr_result = await _run_in_executor(run_ocr, processed)

    # Parsers são CPU-bound leves, mas ainda assim executamos em executor
    content_extraction = await _run_in_executor(parse_semantic, ocr_result)

    if deep:
        deep_result = await _run_in_executor(parse_deep, ocr_result)
        return DeepAnalyzeResponse(
            success=True,
            filename=fname,
            ocr=ocr_result,
            content=content_extraction,
            deep=deep_result,
        )

    return AnalyzeResponse(
        success=True,
        filename=fname,
        ocr=ocr_result,
        content=content_extraction,
    )
