#!/usr/bin/env python3
"""CLI para analisar imagens via OCR e gerar prompts para IA local.

Uso:
    python cli_analyze.py imagem.png
    python cli_analyze.py imagem.png --mode summary
    python cli_analyze.py imagem.png --context "Contexto adicional"
"""

import argparse
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from app.schemas.preprocess import PreprocessOptions
from app.services.analyzer import analyze_image
from app.ai_local.interpreter import interpret_ocr_result
from app.utils.logger import get_logger


async def main() -> int:
    logger = get_logger()
    parser = argparse.ArgumentParser(
        description="OCR Organizer CLI - Analise imagens e gere prompts para IA local"
    )
    parser.add_argument("image", help="Caminho para a imagem a ser analisada")
    parser.add_argument(
        "--mode",
        choices=["full", "summary"],
        default="full",
        help="Modo de interpretacao: full (analise completa) ou summary (resumo rapido)",
    )
    parser.add_argument(
        "--context",
        default=None,
        help="Contexto adicional para a IA local",
    )
    parser.add_argument(
        "--no-grayscale",
        action="store_true",
        help="Desativa conversao para escala de cinza",
    )
    parser.add_argument(
        "--threshold",
        action="store_true",
        help="Ativa thresholding",
    )
    parser.add_argument(
        "--no-denoise",
        action="store_true",
        help="Desativa denoising",
    )
    parser.add_argument(
        "--no-sharpen",
        action="store_true",
        help="Desativa sharpening",
    )
    parser.add_argument(
        "--no-resize",
        action="store_true",
        help="Desativa resize",
    )
    parser.add_argument(
        "--no-deskew",
        action="store_true",
        help="Desativa deskew",
    )

    args = parser.parse_args()

    image_path = Path(args.image)
    if not image_path.exists():
        logger.error(f"Arquivo nao encontrado: {image_path}")
        return 1

    content = image_path.read_bytes()

    options = PreprocessOptions(
        grayscale=not args.no_grayscale,
        threshold=args.threshold,
        denoise=not args.no_denoise,
        sharpen=not args.no_sharpen,
        resize=not args.no_resize,
        deskew=not args.no_deskew,
    )

    logger.info(f"Analisando: {image_path.name} (mode={args.mode})")

    deep = args.mode == "full"
    result = await analyze_image(content, options=options, deep=deep, filename=image_path.name)
    prompt = interpret_ocr_result(result, mode=args.mode, context=args.context)

    print("=" * 60)
    print("PROMPT PARA IA LOCAL")
    print("=" * 60)
    print()
    print(prompt)
    print()
    print("=" * 60)
    print("JSON BRUTO DO OCR (para referencia)")
    print("=" * 60)
    import json
    print(result.model_dump_json(indent=2))

    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
