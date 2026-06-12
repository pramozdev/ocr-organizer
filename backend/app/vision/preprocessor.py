import cv2
import numpy as np
from app.schemas.preprocess import PreprocessOptions
from app.core.config import get_settings
from app.core.exceptions import PreprocessingException
from app.utils.logger import get_logger


def grayscale(image: np.ndarray) -> np.ndarray:
    if len(image.shape) == 3:
        return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    return image


def denoise(image: np.ndarray) -> np.ndarray:
    return cv2.fastNlMeansDenoising(image, None, 10, 7, 21)


def sharpen(image: np.ndarray) -> np.ndarray:
    kernel = np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]])
    return cv2.filter2D(image, -1, kernel)


def resize(image: np.ndarray, max_dim: int | None = None) -> np.ndarray:
    if max_dim is None:
        max_dim = get_settings().PREPROCESS_MAX_DIM or 2000
    h, w = image.shape[:2]
    if max(h, w) > max_dim:
        scale = max_dim / max(h, w)
        new_w = int(w * scale)
        new_h = int(h * scale)
        return cv2.resize(image, (new_w, new_h), interpolation=cv2.INTER_AREA)
    return image


def threshold(image: np.ndarray) -> np.ndarray:
    if len(image.shape) == 3:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    else:
        gray = image
    return cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]


def deskew(image: np.ndarray) -> np.ndarray:
    if len(image.shape) == 3:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    else:
        gray = image.copy()

    coords = np.column_stack(np.where(gray > 0))
    if len(coords) == 0:
        return image

    angle = cv2.minAreaRect(coords)[-1]
    if angle < -45:
        angle = -(90 + angle)
    else:
        angle = -angle

    if abs(angle) < 0.5:
        return image

    (h, w) = image.shape[:2]
    center = (w // 2, h // 2)
    M = cv2.getRotationMatrix2D(center, angle, 1.0)
    rotated = cv2.warpAffine(image, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
    return rotated


def preprocess_image(image: np.ndarray, options: PreprocessOptions) -> np.ndarray:
    logger = get_logger()
    try:
        # Ordenação ideal: deskew primeiro para não distorcer após resize
        if options.deskew:
            image = deskew(image)
            logger.debug("Preprocess: deskew applied")
        if options.resize:
            image = resize(image)
            logger.debug("Preprocess: resize applied")
        if options.grayscale:
            image = grayscale(image)
            logger.debug("Preprocess: grayscale applied")
        if options.denoise:
            image = denoise(image)
            logger.debug("Preprocess: denoise applied")
        if options.sharpen:
            image = sharpen(image)
            logger.debug("Preprocess: sharpen applied")
        if options.threshold:
            image = threshold(image)
            logger.debug("Preprocess: threshold applied")
        return image
    except Exception as e:
        logger.error(f"Erro no preprocessamento: {e}")
        raise PreprocessingException(f"Falha no preprocessamento: {e}") from e
