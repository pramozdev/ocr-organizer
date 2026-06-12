from typing import Dict, Any, Optional
from app.schemas.response import AnalyzeResponse, DeepAnalyzeResponse
from app.utils.logger import get_logger


def build_analysis_prompt(
    response: AnalyzeResponse | DeepAnalyzeResponse,
    context: Optional[str] = None,
) -> str:
    """Constroi um prompt otimizado para IA local interpretar o resultado OCR."""

    content = response.content
    # Preserva quebras de linha do OCR no bloco de código
    ocr_text = response.ocr.text
    lines = [
        "# Analise Inteligente de Documento via OCR",
        "",
        f"**Arquivo:** {response.filename}",
        f"**Confianca OCR:** {response.ocr.confidence:.0%}",
        "",
        "## Texto Completo Extraido",
        "```",
        ocr_text,
        "```",
        "",
        "## Elementos Estruturais Detectados",
    ]

    if content.titles:
        lines.extend(["", "### Titulos", *[f"- {t}" for t in content.titles]])
    if content.questions:
        lines.extend(["", "### Perguntas", *[f"- {q}" for q in content.questions]])
    if content.alternatives:
        lines.extend(["", "### Alternativas", *[f"- {a}" for a in content.alternatives]])
    if content.answers:
        lines.extend(["", "### Respostas", *[f"- {a}" for a in content.answers]])
    if content.lists:
        lines.extend(["", "### Listas", *[f"- {l}" for l in content.lists]])
    if content.links:
        lines.extend(["", "### Links", *[f"- {l}" for l in content.links]])
    if content.emails:
        lines.extend(["", "### Emails", *[f"- {e}" for e in content.emails]])
    if content.phones:
        lines.extend(["", "### Telefones", *[f"- {p}" for p in content.phones]])
    if content.ctas:
        lines.extend(["", "### Chamadas para Acao (CTA)", *[f"- {c}" for c in content.ctas]])

    lines.extend(["", "## Blocos OCR (com coordenadas e confianca)"])
    for i, block in enumerate(response.ocr.blocks, 1):
        lines.append(f"{i}. `{block.text}` (conf: {block.confidence:.2f})")

    if isinstance(response, DeepAnalyzeResponse) and response.deep:
        deep = response.deep
        lines.extend([
            "",
            "## Analise Profunda",
            f"**Tipo de Documento:** {deep.document_type}",
            "",
            "### Ordem de Leitura",
            *[f"{idx+1}. Bloco {bid}" for idx, bid in enumerate(deep.reading_order)],
            "",
            "### Blocos de Conteudo",
        ])
        for block in deep.content_blocks:
            lines.append(f"- **[{block.type.upper()}]** {block.text}")

    lines.extend([
        "",
        "---",
        "## Instrucoes para IA Local",
        "Voce esta recebendo o resultado de um OCR de alta precisao.",
        "Analise o conteudo e forneca:",
        "1. Um resumo contextual do documento",
        "2. Identificacao do publico-alvo (se aplicavel)",
        "3. Insights sobre a intencao (educacional, comercial, conversacional, etc.)",
        "4. Sugestoes de organizacao ou proximos passos",
        "5. Se houver perguntas/alternativas, estruture-as de forma clara",
        "6. Destaque qualquer informacao sensivel (dados pessoais, contatos)",
    ])

    if context:
        lines.extend(["", f"## Contexto Adicional do Usuario\n{context}"])

    lines.append("")
    return "\n".join(lines)


def build_summary_prompt(response: AnalyzeResponse | DeepAnalyzeResponse) -> str:
    """Prompt focado em resumo rapido para IA local."""
    return (
        f"Resuma o seguinte documento extraido por OCR:\n\n"
        f"**Arquivo:** {response.filename}\n"
        f"**Texto:**\n```\n{response.ocr.text}\n```\n\n"
        f"Forneca um resumo de ate 5 linhas."
    )
