import sys
from pathlib import Path
from loguru import logger as _logger
from app.core.config import get_settings

_settings = None
_logger_initialized = False


def _init_logger():
    global _logger_initialized
    if _logger_initialized:
        return
    settings = get_settings()
    log_dir = Path(settings.LOG_DIR)
    log_dir.mkdir(parents=True, exist_ok=True)

    _logger.remove()
    _logger.add(
        sys.stdout,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level="INFO",
    )
    _logger.add(
        log_dir / "app.log",
        rotation="10 MB",
        retention="7 days",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        level="DEBUG",
        enqueue=True,
    )
    _logger_initialized = True


def get_logger():
    _init_logger()
    return _logger


# Compatibilidade com código existente que importa `logger` diretamente
class _LazyLogger:
    def __getattr__(self, name):
        return getattr(get_logger(), name)


logger = _LazyLogger()
__all__ = ["logger", "get_logger"]
