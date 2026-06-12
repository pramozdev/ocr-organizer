# Clipboard OCR Bridge

Ponte automatica entre o **clipboard do sistema** e a **API OCR local**.

## O que faz

1. Le uma imagem do seu clipboard (Ctrl+C em um screenshot/print)
2. Envia para a API OCR Organizer (`localhost:8000`)
3. Extrai o texto e estrutura da imagem
4. Coloca o `prompt_for_ai` de volta no clipboard
5. Voce cola no chat da IA (Ctrl+V) e ela interpreta

## Instalacao

```bash
cd backend

# Linux X11
sudo apt install xclip

# Linux Wayland
sudo apt install wl-clipboard

# Instalar dependencias Python
./venv/bin/pip install requests
```

## Uso

### Passo 1: Copie uma imagem para o clipboard
- Tira um screenshot ou copia uma imagem de qualquer lugar
- `Ctrl+C` ou `Ctrl+Shift+C`

### Passo 2: Execute a ponte
```bash
./venv/bin/python tools/clipboard_ocr.py
```

### Passo 3: Cole no chat da IA
- `Ctrl+V` nesta conversa
- A IA recebera o prompt formatado com todo o conteudo da imagem

## Opcoes

```bash
# Modo resumo (prompt mais curto)
./venv/bin/python tools/clipboard_ocr.py --mode summary

# Com contexto adicional
./venv/bin/python tools/clipboard_ocr.py --context "Prova de historia do Brasil"

# Copiar JSON bruto ao inves do prompt
./venv/bin/python tools/clipboard_ocr.py --json

# Apenas imprimir, nao copiar para clipboard
./venv/bin/python tools/clipboard_ocr.py --no-copy
```

## Exemplo de fluxo completo

```bash
# 1. Copie uma imagem de questoes (Ctrl+C no print)
# 2. Execute:
cd backend && ./venv/bin/python tools/clipboard_ocr.py

# Saida esperada:
# [INFO] Verificando clipboard...
# [INFO] Imagem capturada: /tmp/ocr_clipboard.png
# [INFO] Enviando para OCR (mode=full)...
# ============================================================
# RESULTADO OCR
# ============================================================
# # Analise Inteligente de Documento via OCR
# ... (prompt completo)
# ============================================================
# [INFO] Resultado copiado para o clipboard!
# [INFO] Cole agora no chat da IA com Ctrl+V

# 3. Cole aqui no chat (Ctrl+V)
# 4. A IA local interpreta e responde as questoes
```

## Variavel de ambiente

```bash
# Se a API rodar em outro host/porta:
export OCR_API_URL="http://localhost:8000/api/v1/ai/analyze"
```
