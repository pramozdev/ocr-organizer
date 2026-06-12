#!/usr/bin/env python3
"""
Ponte Clipboard <-> OCR API

Le uma imagem do clipboard do sistema, envia para a API OCR local
e coloca o resultado (prompt_for_ai) de volta no clipboard.

Requisitos Linux:
    - X11: sudo apt install xclip
    - Wayland: sudo apt install wl-clipboard

Uso:
    python tools/clipboard_ocr.py
    # ou
    ./tools/clipboard_ocr.py --mode summary --context "Quiz de historia"
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
    wayland = os.environ.get("WAYLAND_DISPLAY")
    x11 = os.environ.get("DISPLAY")
    if wayland:
        return "wayland"
    if x11:
        return "x11"
    return "unknown"


IMAGE_MIME_TYPES = [
    "image/png",
    "image/jpeg",
    "image/jpg",
    "image/webp",
    "image/bmp",
    "image/x-portable-pixmap",
]


def get_image_from_clipboard() -> Path | None:
    """Tenta extrair uma imagem do clipboard testando varios formatos MIME."""
    session = detect_desktop_session()
    temp_path = TEMP_DIR / "ocr_clipboard.png"

    if session == "x11":
        for mime in IMAGE_MIME_TYPES:
            try:
                result = subprocess.run(
                    ["xclip", "-selection", "clipboard", "-t", mime, "-o"],
                    capture_output=True,
                )
                if result.returncode == 0 and len(result.stdout) > 100:
                    temp_path.write_bytes(result.stdout)
                    print(f"[INFO] Formato detectado no clipboard: {mime}")
                    return temp_path
            except FileNotFoundError:
                print("[ERRO] xclip nao encontrado. Instale: sudo apt install xclip")
                return None

    elif session == "wayland":
        for mime in IMAGE_MIME_TYPES:
            try:
                result = subprocess.run(
                    ["wl-paste", "--type", mime],
                    capture_output=True,
                )
                if result.returncode == 0 and len(result.stdout) > 100:
                    temp_path.write_bytes(result.stdout)
                    print(f"[INFO] Formato detectado no clipboard: {mime}")
                    return temp_path
            except FileNotFoundError:
                print("[ERRO] wl-clipboard nao encontrado. Instale: sudo apt install wl-clipboard")
                return None

    else:
        print("[ERRO] Sessao de desktop nao detectada (X11/Wayland).")
        return None

    return None


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
    parser = argparse.ArgumentParser(description="Clipboard OCR Bridge")
    parser.add_argument("--mode", choices=["full", "summary"], default="full")
    parser.add_argument("--context", default=None, help="Contexto adicional")
    parser.add_argument("--json", action="store_true", help="Copia JSON bruto ao inves do prompt")
    parser.add_argument("--no-copy", action="store_true", help="Nao copia para clipboard, apenas imprime")
    args = parser.parse_args()

    print("[INFO] Verificando clipboard...")
    img_path = get_image_from_clipboard()
    if not img_path:
        print("[ERRO] Nenhuma imagem encontrada no clipboard.")
        print("[DICA] Copie uma imagem (Ctrl+C em um print/screenshot) e execute novamente.")
        return 1

    print(f"[INFO] Imagem capturada: {img_path}")
    print(f"[INFO] Enviando para OCR (mode={args.mode})...")

    try:
        result = send_to_ocr(img_path, mode=args.mode, context=args.context)
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
