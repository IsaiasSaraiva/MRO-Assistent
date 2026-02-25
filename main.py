import streamlit as st
from fpdf import FPDF
import io
from processador_pdf import PDFProcessor
from vector_store import VectorStoreManager
from gerenciador_llm import LLMHandler




# --- Configurações da aplicação StreamLit ---
st.set_page_config(page_title="RAG Assistant MRO", layout="wide", page_icon="Assets/MRO.png")
st.logo("Assets/MRO.png")
st.title("MRO Assistant")
st.caption("Assistente com RAG para manutenção de aeronaves")

# --- Inicializar componentes ---
@st.cache_resource
def init_components():
    pdf_proc = PDFProcessor()
    vector_store = VectorStoreManager()
    llm = LLMHandler()
    return pdf_proc, vector_store, llm

pdf_processor, vector_store, llm_handler = init_components()

# --- Sidebar para Upload ---
with st.sidebar:
    st.header(" Upload dos manuais de manutenção!")
    
    uploaded_files = st.file_uploader(
        "Faça upload de manuais em PDFs",
        type=['pdf'],
        accept_multiple_files=True
    )
    
    if uploaded_files:
        if st.button("Processar PDFs"):
            with st.spinner("Processando os manuais..."):
                total_chunks = 0
                for uploaded_file in uploaded_files:
                    try:
                        result = pdf_processor.process_pdf(uploaded_file)
                        
                        # Adicionar ao vector store
                        success = vector_store.add_documents(result['chunks'])
                        
                        if success:
                            total_chunks += result['num_chunks']
                            st.success(f"✅ {result['file_name']}: {result['num_chunks']} chunks")
                        else:
                            st.error(f"❌ Erro ao adicionar {result['file_name']} ao banco")
                    
                    except Exception as e:
                        st.error(f"❌ Erro: {str(e)}")
                
                st.info(f"Total de chunks processados: {total_chunks}")
                
                # Forçar atualização da página para mostrar nova contagem
                st.rerun()
    
    st.divider()
    
    # Informações do banco
    doc_count = vector_store.get_collection_count()
    #st.metric("Documentos no banco", doc_count)
    
    if doc_count > 0:
        if st.button("🗑️ Limpar Banco de Dados"):
            if vector_store.delete_collection():
                st.success("Banco limpo com sucesso!")
                st.rerun()

# --- Histórico ---
if "conversas" not in st.session_state:
    st.session_state.conversas = []

# --- Modo de busca ---
use_rag = st.checkbox("🔍 Usar RAG (buscar nos documentos)", value=True)

# --- Input ---
pergunta = st.text_area("Digite sua pergunta:", height=100)

col1, col2 = st.columns([1, 5])
with col1:
    enviar = st.button("Enviar", type="primary")

if enviar and pergunta.strip():
    with st.spinner("Processando..."):
        if use_rag:
            # Buscar documentos relevantes
            docs = vector_store.similarity_search(pergunta, k=3)
            
            if docs:
                # Gerar resposta com RAG
                resposta = llm_handler.generate_rag_response(pergunta, docs)
                
                # Mostrar fontes
                fontes = "\n\n".join([
                    f"📄 Fonte {i+1}: {doc.metadata.get('source', 'Desconhecido')}\nTrecho: {doc.page_content[:150]}..."
                    for i, doc in enumerate(docs)
                ])
            else:
                resposta = "Nenhum documento  encontrado. TFaça o upload dos manuais em PDFs primeiro."
                fontes = ""
        else:
            # Resposta sem RAG
            resposta = llm_handler.generate_response(pergunta)
            fontes = ""
        
        st.session_state.conversas.append({
            "pergunta": pergunta,
            "resposta": resposta,
            "fontes": fontes,
            "usou_rag": use_rag
        })

# --- Mostrar histórico ---
for i, conv in enumerate(reversed(st.session_state.conversas)):
    with st.container():
        st.markdown(f"** Você:** {conv['pergunta']}")
        st.markdown(f"** Assistente:** {conv['resposta']}")
        
        if conv.get('usou_rag') and conv.get('fontes'):
            with st.expander("📚 Ver fontes"):
                st.text(conv['fontes'])
        
        st.divider()

# --- Download PDF ---
if st.session_state.conversas:
    if st.button("📥 Baixar Conversas em PDF"):
        pdf = FPDF()
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.add_page()
        pdf.set_font("Arial", size=10)
        
        for conv in st.session_state.conversas:
            pdf.set_font("Arial", 'B', 11)
            pdf.multi_cell(0, 8, f"Pergunta: {conv['pergunta']}")
            pdf.set_font("Arial", size=10)
            pdf.multi_cell(0, 8, f"Resposta: {conv['resposta']}")
            if conv.get('fontes'):
                pdf.multi_cell(0, 8, f"Fontes: {conv['fontes']}")
            pdf.ln(5)
        
        buffer = io.BytesIO()
        pdf.output(buffer)
        buffer.seek(0)
        
        st.download_button(
            "📄 Baixar PDF",
            data=buffer,
            file_name="conversas_rag.pdf",
            mime="application/pdf"
        )