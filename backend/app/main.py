from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import get_settings
from app.core.exceptions import OCRException, ImageValidationException, PreprocessingException, ParsingException
from app.api.routes import router
from app.utils.logger import get_logger

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger = get_logger()
    logger.info(f"{settings.APP_NAME} v{settings.APP_VERSION} iniciado.")
    yield
    logger.info(f"{settings.APP_NAME} encerrado.")


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="API local de OCR inteligente com Tesseract e análise semântica.",
    lifespan=lifespan,
)

# CORS restrito: permite apenas localhost e origens não credenciadas não são permitidas
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost", "http://127.0.0.1", "http://localhost:3000", "http://localhost:5173"],
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

# Exception handlers globais
@app.exception_handler(ImageValidationException)
async def image_validation_handler(request: Request, exc: ImageValidationException):
    logger = get_logger()
    logger.warning(f"Validação falhou: {exc}")
    return JSONResponse(status_code=400, content={"detail": str(exc)})


@app.exception_handler(OCRException)
async def ocr_handler(request: Request, exc: OCRException):
    logger = get_logger()
    logger.error(f"Erro no OCR: {exc}")
    return JSONResponse(status_code=500, content={"detail": str(exc)})


@app.exception_handler(PreprocessingException)
async def preprocessing_handler(request: Request, exc: PreprocessingException):
    logger = get_logger()
    logger.error(f"Erro no preprocessamento: {exc}")
    return JSONResponse(status_code=500, content={"detail": str(exc)})


@app.exception_handler(ParsingException)
async def parsing_handler(request: Request, exc: ParsingException):
    logger = get_logger()
    logger.error(f"Erro no parsing: {exc}")
    return JSONResponse(status_code=500, content={"detail": str(exc)})


@app.exception_handler(Exception)
async def generic_handler(request: Request, exc: Exception):
    logger = get_logger()
    logger.error(f"Erro inesperado: {exc}")
    return JSONResponse(status_code=500, content={"detail": f"Erro interno: {exc}"})


app.include_router(router, prefix="/api/v1")
