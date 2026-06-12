from pydantic import BaseModel
from typing import Optional
from app.schemas.ocr import OCRResult
from app.schemas.content import ContentExtraction
from app.schemas.deep import DeepAnalysisResult


class AnalyzeResponse(BaseModel):
    success: bool = True
    filename: str
    ocr: OCRResult
    content: ContentExtraction


class DeepAnalyzeResponse(BaseModel):
    success: bool = True
    filename: str
    ocr: OCRResult
    content: ContentExtraction
    deep: Optional[DeepAnalysisResult] = None
