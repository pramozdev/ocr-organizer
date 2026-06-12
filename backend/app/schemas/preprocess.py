from pydantic import BaseModel


class PreprocessOptions(BaseModel):
    grayscale: bool = True
    threshold: bool = False
    denoise: bool = True
    sharpen: bool = True
    resize: bool = True
    deskew: bool = True
