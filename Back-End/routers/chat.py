"""
routers/chat.py — RAG chat endpoint.
"""
import os
import io
import base64
from typing import Annotated
from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from core.security import get_current_user

router = APIRouter()


class ChatRequest(BaseModel):
    question: str


class DownloadPDFRequest(BaseModel):
    text: str
    filename: str = "relatorio_mro.pdf"


def user_collection(user_id: str) -> str:
    return f"user_{user_id.replace('-', '')}_docs"


def _eh_relatorio(texto: str) -> bool:
    palavras_chave = [
        "relatório", "serviços executados", "responsável técnico",
        "número da os", "data de início", "ordem de serviço",
        "introdução", "considerações técnicas", "conclusão",
        "formulario gerado", "formulário 015"
    ]
    return any(p in texto.lower() for p in palavras_chave)


def _sanitizar(texto: str) -> str:
    replacements = {
        "\u2013": "-", "\u2014": "--", "\u2018": "'", "\u2019": "'",
        "\u201c": '"', "\u201d": '"', "\u2022": "*", "\u2026": "...",
        "\u00b0": " graus", "\u00e9": "e", "\u00e3": "a", "\u00e7": "c",
        "\u00f5": "o", "\u00ea": "e", "\u00f3": "o", "\u00ed": "i",
        "\u00fa": "u", "\u00e2": "a", "\u00f4": "o", "\u00e0": "a",
        "\u00fc": "u", "\u00e1": "a", "\u00f1": "n",
    }
    for char, rep in replacements.items():
        texto = texto.replace(char, rep)
    return texto.encode("latin-1", errors="ignore").decode("latin-1")


def _gerar_formulario_015_pdf(dados: dict) -> io.BytesIO:
    from fpdf import FPDF
    from datetime import date

    pdf = FPDF(orientation='L', unit='mm', format='A4')
    pdf.set_auto_page_break(auto=True, margin=10)
    pdf.add_page()
    pdf.set_margins(10, 10, 10)

    nome_empresa = _sanitizar(dados.get("nome_empresa") or "")
    endereco     = _sanitizar(dados.get("endereco") or "")
    cidade_uf    = _sanitizar(dados.get("cidade_uf") or "")
    mes_ano      = _sanitizar(dados.get("mes_ano") or "")
    responsavel  = _sanitizar(dados.get("responsavel_tecnico") or "Responsavel Tecnico")
    observacoes  = _sanitizar(dados.get("observacoes") or "")
    servicos     = dados.get("servicos") or []

    page_w = 277  # A4 paisagem - margens

    # Larguras proporcionais que somam exatamente page_w
    col_w_base = [28, 20, 28, 26, 28, 20, 50, 28, 28]
    total = sum(col_w_base)
    col_w = [round(w * page_w / total) for w in col_w_base]
    col_w[-1] = page_w - sum(col_w[:-1])  # corrige arredondamento

    # ── Título ────────────────────────────────────────────────────────────────
    pdf.set_font("Arial", 'B', 11)
    pdf.cell(page_w, 8,
             "Formulario 015: Relatorio mensal de servicos executados",
             border=0, ln=True, align='C')
    pdf.ln(2)

    # ── Cabeçalho empresa ─────────────────────────────────────────────────────
    pdf.set_font("Arial", 'B', 10)
    pdf.cell(page_w, 10, nome_empresa, border=1, ln=True, align='C')
    pdf.set_font("Arial", size=9)
    pdf.cell(page_w, 6, endereco, border='LR', ln=True, align='C')
    pdf.cell(page_w, 6, cidade_uf, border='LRB', ln=True, align='C')
    pdf.ln(1)

    # ── Título da tabela ──────────────────────────────────────────────────────
    pdf.set_font("Arial", 'B', 10)
    pdf.cell(page_w, 8,
             f"Relatorio mensal de servicos executados {mes_ano}",
             border=1, ln=True, align='C')

    # ── Cabeçalho colunas em 2 linhas fixas ───────────────────────────────────
    half_h = 5  # altura de cada meia linha
    pdf.set_font("Arial", 'B', 7)

    x_start = pdf.get_x()
    y_start = pdf.get_y()

    # Linha superior do cabeçalho
    linha1 = [
        "Tipo de", "Marca", "Numero de", "Modelo",
        "Fabricante", "Numero", "Local de", "Data de", "Data de"
    ]
    for w, txt in zip(col_w, linha1):
        pdf.cell(w, half_h, txt, border='LTR', align='C')
    pdf.ln(half_h)

    # Linha inferior do cabeçalho
    pdf.set_xy(x_start, y_start + half_h)
    linha2 = [
        "Produto", "", "Serie", "",
        "", "da OS", "Execucao", "Inicio", "Fim"
    ]
    for w, txt in zip(col_w, linha2):
        pdf.cell(w, half_h, txt, border='LBR', align='C')
    pdf.ln(half_h)

    # ── Linhas de dados ───────────────────────────────────────────────────────
    pdf.set_font("Arial", size=7)
    row_h = 8

    while len(servicos) < 5:
        servicos.append({
            "tipo_produto": "", "marca": "", "numero_serie": "",
            "modelo": "", "fabricante": "", "numero_os": "",
            "local_execucao": "", "data_inicio": "", "data_fim": ""
        })

    for s in servicos:
        cells = [
            _sanitizar(s.get("tipo_produto") or ""),
            _sanitizar(s.get("marca") or ""),
            _sanitizar(s.get("numero_serie") or ""),
            _sanitizar(s.get("modelo") or ""),
            _sanitizar(s.get("fabricante") or ""),
            _sanitizar(s.get("numero_os") or ""),
            _sanitizar(s.get("local_execucao") or ""),
            _sanitizar(s.get("data_inicio") or ""),
            _sanitizar(s.get("data_fim") or ""),
        ]
        for val, w in zip(cells, col_w):
            pdf.cell(w, row_h, val, border=1, align='C')
        pdf.ln(row_h)

    # ── Observações ───────────────────────────────────────────────────────────
    pdf.ln(2)
    pdf.set_font("Arial", size=8)
    obs = observacoes if observacoes else "Nao foram executados servicos adicionais neste mes."
    pdf.cell(page_w, 7, f"Observacoes: {obs}", border=1, ln=True)

    # ── Data e assinatura ─────────────────────────────────────────────────────
    pdf.ln(4)
    pdf.set_font("Arial", size=9)
    pdf.cell(page_w, 6, f"Data: {date.today().strftime('%d/%m/%Y')}", ln=True)
    pdf.ln(8)
    assin_x = 10 + (page_w / 2) - 40
    pdf.line(assin_x, pdf.get_y(), assin_x + 80, pdf.get_y())
    pdf.ln(2)
    pdf.set_font("Arial", 'B', 9)
    pdf.cell(page_w, 6, responsavel, ln=True, align='C')

    result = pdf.output(dest="S")
    if isinstance(result, str):
        result = result.encode("latin-1")
    return io.BytesIO(result)


def _texto_para_pdf(texto: str) -> io.BytesIO:
    from fpdf import FPDF

    texto = _sanitizar(texto)
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    for line in texto.split("\n"):
        line_clean = line.replace("**", "").strip()
        if line.startswith("# "):
            pdf.set_font("Arial", 'B', 14)
            pdf.cell(0, 9, line_clean.replace("# ", ""), ln=True, align='C')
            pdf.ln(2)
        elif line.startswith("## "):
            pdf.set_font("Arial", 'B', 12)
            pdf.multi_cell(0, 8, line_clean.replace("## ", ""))
            pdf.ln(1)
        elif line.strip() == "---":
            pdf.ln(2)
            pdf.line(pdf.get_x(), pdf.get_y(), pdf.get_x() + 190, pdf.get_y())
            pdf.ln(3)
        elif line.startswith("|"):
            pdf.set_font("Arial", size=8)
            pdf.multi_cell(0, 6, line_clean)
            pdf.set_font("Arial", size=10)
        elif line.startswith("**"):
            pdf.set_font("Arial", 'B', 10)
            pdf.multi_cell(0, 7, line_clean)
            pdf.set_font("Arial", size=10)
        elif line_clean:
            pdf.set_font("Arial", size=10)
            pdf.multi_cell(0, 7, line_clean)

    result = pdf.output(dest="S")
    if isinstance(result, str):
        result = result.encode("latin-1")
    return io.BytesIO(result)


@router.post("/chat")
def chat(
    request: ChatRequest,
    current_user: Annotated[dict, Depends(get_current_user)],
):
    user_id: str = current_user["user_id"]
    collection_name = user_collection(user_id)

    from vector_store import VectorStoreManager
    from gerenciador_llm import LLMHandler

    vs = VectorStoreManager(collection_name)
    docs = vs.similarity_search(request.question, k=5)
    context = "\n\n".join([d.page_content for d in docs]) if docs else ""

    llm = LLMHandler()
    modo = llm._detectar_modo(request.question)

    # ── Formulário 015 ────────────────────────────────────────────────────────
    if modo == "formulario015":
        dados = llm.extrair_dados_formulario(request.question, context)
        buffer = _gerar_formulario_015_pdf(dados)
        pdf_b64 = base64.b64encode(buffer.getvalue()).decode()
        mes = dados.get("mes_ano", "").replace("/", "_") or "MRO"

        return {
            "answer": "Formulario 015 gerado com sucesso! Clique em **Baixar Formulario 015** para fazer o download.",
            "sources": [],
            "is_report": True,
            "formulario015": True,
            "pdf_base64": pdf_b64,
            "filename": f"formulario_015_{mes}.pdf",
        }

    # ── Fluxo RAG normal ──────────────────────────────────────────────────────
    if not docs:
        return {
            "answer": "Nenhum documento encontrado. Faca o upload dos manuais em PDF primeiro.",
            "sources": [],
            "is_report": False,
            "formulario015": False,
        }

    answer = llm.generate_rag_response(request.question, docs)
    sources = [
        {
            "filename": os.path.basename(doc.metadata.get("source", "Desconhecido")),
            "page": doc.metadata.get("page", None),
            "excerpt": doc.page_content[:200],
        }
        for doc in docs
    ]

    return {
        "answer": answer,
        "sources": sources,
        "is_report": _eh_relatorio(answer),
        "formulario015": False,
    }


@router.post("/chat/download-pdf")
def download_pdf(
    request: DownloadPDFRequest,
    current_user: Annotated[dict, Depends(get_current_user)],
):
    buffer = _texto_para_pdf(request.text)
    return StreamingResponse(
        buffer,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="{request.filename}"'
        },
    )