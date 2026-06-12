from pydantic import BaseModel
from typing import Optional
from app.schemas.response import AnalyzeResponse, DeepAnalyzeResponse


class AIInterpretResponse(BaseModel):
    success: bool = True
    filename: str
    ocr_result: AnalyzeResponse | DeepAnalyzeResponse
    prompt_for_ai: str
    mode: str
    context: Optional[str] = None
