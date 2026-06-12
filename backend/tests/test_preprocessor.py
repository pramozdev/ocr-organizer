import numpy as np
import cv2
from app.vision.preprocessor import (
    grayscale, denoise, sharpen, resize, threshold, deskew, preprocess_image
)
from app.schemas.preprocess import PreprocessOptions


def create_test_image(mode: str = "color") -> np.ndarray:
    if mode == "color":
        return np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
    return np.random.randint(0, 255, (100, 100), dtype=np.uint8)


def test_grayscale():
    img = create_test_image("color")
    gray = grayscale(img)
    assert len(gray.shape) == 2


def test_denoise():
    img = create_test_image("gray")
    denoised = denoise(img)
    assert denoised.shape == img.shape


def test_sharpen():
    img = create_test_image("color")
    sharp = sharpen(img)
    assert sharp.shape == img.shape


def test_resize():
    img = np.random.randint(0, 255, (3000, 3000, 3), dtype=np.uint8)
    resized = resize(img, max_dim=2000)
    assert max(resized.shape[:2]) <= 2000


def test_threshold():
    img = create_test_image("gray")
    thresh = threshold(img)
    assert len(thresh.shape) == 2
    assert set(np.unique(thresh)).issubset({0, 255})


def test_deskew():
    img = create_test_image("gray")
    deskewed = deskew(img)
    assert deskewed.shape == img.shape


def test_preprocess_image():
    img = create_test_image("color")
    options = PreprocessOptions(
        grayscale=True, threshold=False, denoise=True, sharpen=True, resize=True, deskew=True
    )
    processed = preprocess_image(img, options)
    assert processed is not None
    assert len(processed.shape) == 2  # grayscale result
