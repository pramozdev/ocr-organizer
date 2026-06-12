from pydantic import BaseModel
from typing import List, Dict, Any, Optional


class ContentBlock(BaseModel):
    type: str
    text: str
    bbox: Optional[List[List[float]]] = None
    confidence: Optional[float] = None


class DeepAnalysisResult(BaseModel):
    document_type: str
    structure: Dict[str, Any]
    reading_order: List[int]
    content_blocks: List[ContentBlock]
