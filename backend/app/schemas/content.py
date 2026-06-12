from pydantic import BaseModel
from typing import List


class ContentExtraction(BaseModel):
    titles: List[str] = []
    questions: List[str] = []
    alternatives: List[str] = []
    answers: List[str] = []
    lists: List[str] = []
    links: List[str] = []
    emails: List[str] = []
    phones: List[str] = []
    ctas: List[str] = []
