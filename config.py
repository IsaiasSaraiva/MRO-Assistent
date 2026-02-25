
# O Arquivo config.py, contém as informações gerais da plataforma, neste arquivo contém as configurações da LLM, banco dados vetorial
# e configuração da orquestração 


import os
from dotenv import load_dotenv

# Carrega variáveis do arquivo .env
load_dotenv() 

# Diretório base onde este arquivo está localizado
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Pasta onde o banco vetorial ChromaDB será armazenado
CHROMA_DB_PATH = os.path.join(BASE_DIR, "chroma_db")

# Pasta onde os PDFs dos manuais enviados pelo usuário ficam salvos
UPLOAD_DIR = os.path.join(BASE_DIR, "uploaded_pdfs")

# Criar diretórios se não existirem
os.makedirs(CHROMA_DB_PATH, exist_ok=True)
os.makedirs(UPLOAD_DIR, exist_ok=True)

# ── Groq (LLM) ────────────────────────────────────────────────────────────────
# Chave de API lida do .env
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Modelo usado para geração de respostas (LLaMA 3.1 8B, rápido e leve)
GROQ_MODEL = "llama-3.1-8b-instant"


# ── Text Splitting ────────────────────────────────────────────────────────────
# Configurações de Text Splitting
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200

# ── Embeddings ────────────────────────────────────────────────────────────────
# Configurações de Embeddings
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

# Nome da coleção (equivalente a uma "tabela") dentro do banco vetorial
COLLECTION_NAME = "mro_documents"
