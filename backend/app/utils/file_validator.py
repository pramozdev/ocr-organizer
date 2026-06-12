import os
import io
from functools import lru_cache
from PIL import Image
from app.core.config import get_settings
from app.core.exceptions import ImageValidationException


@lru_cache
def _get_validation_constants():
    settings = get_settings()
    max_bytes = settings.MAX_FILE_SIZE_MB * 1024 * 1024
    allowed_exts = settings.ALLOWED_EXTENSIONS
    return max_bytes, allowed_exts, settings.MAX_FILE_SIZE_MB


def validate_image_file(filename: str, file_size: int) -> None:
    max_bytes, allowed_exts, max_mb = _get_validation_constants()
    if file_size > max_bytes:
        raise ImageValidationException(
            f"Arquivo muito grande: {file_size} bytes. Limite: {max_bytes} bytes ({max_mb} MB)"
        )

    ext = os.path.splitext(filename)[1].lower().lstrip(".")
    if ext not in allowed_exts:
        raise ImageValidationException(
            f"Extensão não permitida: .{ext}. Permitidas: {', '.join(allowed_exts)}"
        )


def validate_image_bytes(content: bytes, filename: str) -> None:
    try:
        img = Image.open(io.BytesIO(content))
        img_type = img.format.lower() if img.format else None
    except Exception:
        raise ImageValidationException("Arquivo não é uma imagem válida.")

    allowed_types = {"png", "jpeg", "gif", "webp", "jpg"}
    if img_type not in allowed_types:
        raise ImageValidationException(
            f"Formato de imagem não suportado: {img_type}. Suportados: {', '.join(sorted(allowed_types))}"
        )
