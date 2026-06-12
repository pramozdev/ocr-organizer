from pydantic import BaseModel, Field
from typing import List, Optional


class OCRBlock(BaseModel):
    text: str
    confidence: float = Field(ge=0.0, le=1.0)
    coordinates: List[List[float]]


class OCRResult(BaseModel):
    text: str
    confidence: float = Field(ge=0.0, le=1.0)
    blocks: List[OCRBlock]
