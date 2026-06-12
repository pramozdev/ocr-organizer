# OCR Organizer

Aplicação local em Python para análise inteligente de imagens contendo texto.

## Requisitos de Sistema

- Python 3.12+
- Tesseract OCR + dados em português:
  ```bash
  sudo apt install tesseract-ocr tesseract-ocr-por
  ```
- (Opcional para clipboard tools) Linux: `xclip` (X11) ou `wl-clipboard` (Wayland)
- (Opcional para screenshot tool) ImageMagick: `sudo apt install imagemagick`

## Instalação

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

## Execução

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Acesse a documentação interativa em: http://localhost:8000/docs

## Endpoints

### OCR Basico
- `GET /api/v1/health` — Health check
- `POST /api/v1/analyze` — Analise OCR + parsing semantico
- `POST /api/v1/analyze/deep` — Analise profunda (tipo de documento, estrutura, ordem de leitura, blocos de conteudo)

### Integracao com IA Local
- `POST /api/v1/ai/analyze` — OCR completo + **prompt formatado** para IA local interpretar
  - Parametros: `file`, `mode=full|summary`, `context` (opcional), plus opcoes de preprocessamento
  - Retorna: `ocr_result` (JSON) + `prompt_for_ai` (string pronta para enviar a IA)
- `POST /api/v1/ai/summary` — OCR + **prompt de resumo rapido** para IA local

## Uso com IA Local (Voce / IDE)

O sistema gera automaticamente prompts otimizados a partir do JSON OCR. Fluxo:

1. Envie uma imagem para `POST /api/v1/ai/analyze`
2. Receba o JSON com `prompt_for_ai`
3. Cole o prompt no chat da IA local (esta conversa) para interpretacao inteligente

### CLI para Gerar Prompts Localmente

```bash
./venv/bin/python cli_analyze.py imagem.png
./venv/bin/python cli_analyze.py imagem.png --mode summary
./venv/bin/python cli_analyze.py imagem.png --context "Pagina de curso de Python"
```

O CLI imprime o prompt formatado + o JSON bruto do OCR.

### Tools de Captura Rapida

```bash
# Captura de area da tela (clique e arraste)
./venv/bin/python tools/ocr_screenshot.py

# Captura tela inteira
./venv/bin/python tools/ocr_screenshot.py --fullscreen

# Clipboard OCR (imagem ja no clipboard do sistema)
./venv/bin/python tools/clipboard_ocr.py
```

## Variaveis de Ambiente (.env)

```bash
HOST=0.0.0.0
PORT=8000
MAX_FILE_SIZE_MB=20
OCR_LANG=por
PREPROCESS_MAX_DIM=2000
```

## Testes

```bash
pytest
```

## Estrutura

```
app/
├── api/          # Rotas FastAPI
├── ai_local/     # Ponte OCR -> IA Local (prompt builder, interpreter)
├── core/         # Config, excecoes, lifespan, exception handlers
├── ocr/          # Engine Tesseract (pytesseract)
├── vision/       # Pre-processamento de imagens
├── parsers/      # Parsers semanticos e profundos
├── schemas/      # Modelos Pydantic
├── services/     # Orquestracao de analise (async com thread pool)
├── utils/        # Validacao, logging
└── main.py       # Entrypoint
```

## Extensibilidade para IA Local

A arquitetura separa claramente **extracao** (OCR + parsers) de **interpretacao** (IA local).

- O modulo `ai_local/` formata o JSON OCR em prompts otimizados
- Endpoints `/api/v1/ai/*` retornam tanto o JSON bruto quanto o `prompt_for_ai`
- A IA local (voce) recebe o prompt pronto, sem necessidade de parsing manual de JSON
