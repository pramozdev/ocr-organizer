#!/usr/bin/env python3
"""
Captura screenshot da tela e envia para OCR API.

Nao depende de clipboard. Captura diretamente via ImageMagick (import).

Uso:
    python tools/ocr_screenshot.py
    # Clique e arraste para selecionar a area da tela
    # O resultado sera copiado para o clipboard

Opcoes:
    python tools/ocr_screenshot.py --mode summary
    python tools/ocr_screenshot.py --context "Quiz de Python"
    python tools/ocr_screenshot.py --fullscreen  # captura tela inteira
"""

import argparse
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

import requests

API_URL = os.getenv("OCR_API_URL", "http://localhost:8000/api/v1/ai/analyze")
TEMP_DIR = Path(tempfile.gettempdir())


def detect_desktop_session() -> str:
    """Detecta se eh X11 ou Wayland."""
    if os.environ.get("WAYLAND_DISPLAY"):
        return "wayland"
    if os.environ.get("DISPLAY"):
        return "x11"
    return "unknown"


def capture_screenshot_area(output_path: Path) -> bool:
    """Captura uma area da tela via ImageMagick import."""
    try:
        # import -window root -crop ... eh complicado; usamos o modo interativo
        # O import do ImageMagick abre um cursor de cruz para selecionar area
        print("[INFO] Clique e arraste para selecionar a area da tela...")
        result = subprocess.run(
            ["import", str(output_path)],
            capture_output=True,
            text=True,
        )
        if result.returncode == 0 and output_path.exists() and output_path.stat().st_size > 0:
            return True
        print(f"[ERRO] import falhou: {result.stderr}")
        return False
    except FileNotFoundError:
        print("[ERRO] ImageMagick 'import' nao encontrado.")
        return False


def capture_screenshot_fullscreen(output_path: Path) -> bool:
    """Captura a tela inteira."""
    try:
        result = subprocess.run(
            ["import", "-window", "root", str(output_path)],
            capture_output=True,
            text=True,
        )
        if result.returncode == 0 and output_path.exists() and output_path.stat().st_size > 0:
            return True
        print(f"[ERRO] import falhou: {result.stderr}")
        return False
    except FileNotFoundError:
        print("[ERRO] ImageMagick 'import' nao encontrado.")
        return False


def send_to_ocr(image_path: Path, mode: str = "full", context: str | None = None) -> dict:
    """Envia a imagem para a API OCR local."""
    files = {"file": open(image_path, "rb")}
    data = {"mode": mode}
    if context:
        data["context"] = context

    response = requests.post(API_URL, files=files, data=data, timeout=60)
    response.raise_for_status()
    return response.json()


def copy_text_to_clipboard(text: str) -> bool:
    """Copia texto para o clipboard."""
    session = detect_desktop_session()

    if session == "x11":
        try:
            proc = subprocess.Popen(
                ["xclip", "-selection", "clipboard"],
                stdin=subprocess.PIPE,
            )
            proc.communicate(text.encode("utf-8"))
            return proc.returncode == 0
        except FileNotFoundError:
            return False

    elif session == "wayland":
        try:
            proc = subprocess.Popen(
                ["wl-copy"],
                stdin=subprocess.PIPE,
            )
            proc.communicate(text.encode("utf-8"))
            return proc.returncode == 0
        except FileNotFoundError:
            return False

    return False


def main() -> int:
    parser = argparse.ArgumentParser(description="OCR Screenshot Bridge")
    parser.add_argument("--mode", choices=["full", "summary"], default="full")
    parser.add_argument("--context", default=None, help="Contexto adicional")
    parser.add_argument("--json", action="store_true", help="Copia JSON bruto ao inves do prompt")
    parser.add_argument("--no-copy", action="store_true", help="Nao copia para clipboard, apenas imprime")
    parser.add_argument("--fullscreen", action="store_true", help="Captura tela inteira (nao interativo)")
    args = parser.parse_args()

    temp_path = TEMP_DIR / "ocr_screenshot.png"

    if args.fullscreen:
        print("[INFO] Capturando tela inteira...")
        if not capture_screenshot_fullscreen(temp_path):
            return 1
    else:
        print("[INFO] Captura de area da tela...")
        if not capture_screenshot_area(temp_path):
            return 1

    print(f"[INFO] Screenshot salvo: {temp_path}")
    print(f"[INFO] Enviando para OCR (mode={args.mode})...")

    try:
        result = send_to_ocr(temp_path, mode=args.mode, context=args.context)
    except requests.exceptions.ConnectionError:
        print(f"[ERRO] Nao foi possivel conectar a API em {API_URL}")
        print("[DICA] Certifique-se de que o servidor esta rodando:")
        print("       uvicorn app.main:app --reload")
        return 1
    except Exception as e:
        print(f"[ERRO] Falha no OCR: {e}")
        return 1

    if not result.get("success"):
        print(f"[ERRO] API retornou erro: {result}")
        return 1

    if args.json:
        output = json.dumps(result, indent=2, ensure_ascii=False)
    else:
        output = result.get("prompt_for_ai", "")
        if not output:
            print("[AVISO] prompt_for_ai vazio. Usando texto bruto do OCR.")
            output = result.get("ocr_result", {}).get("ocr", {}).get("text", "")

    print("\n" + "=" * 60)
    print("RESULTADO OCR")
    print("=" * 60)
    print(output)
    print("=" * 60)

    if not args.no_copy:
        if copy_text_to_clipboard(output):
            print("\n[INFO] Resultado copiado para o clipboard!")
            print("[INFO] Cole agora no chat da IA com Ctrl+V")
        else:
            print("\n[AVISO] Nao foi possivel copiar para o clipboard.")
            print("[DICA] Selecione e copie o texto acima manualmente.")

    return 0


if __name__ == "__main__":
    sys.exit(main())
