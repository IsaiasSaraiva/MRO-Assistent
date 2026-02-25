# MRO-Assistent

Ferramenta de assistente de manutenção para documentos técnicos, utilizando **RAG (Retrieval-Augmented Generation)** com interface via **Streamlit**.

---

## Requisitos

- Python 3.12.2 
- Git  
- Chave de API `GROQ_API_KEY` (necessária para acesso ao serviço de embeddings/retrieval)

---

## Configuração Inicial

### 1. Clonar o repositório

```bash
git clone https://github.com/IsaiasSaraiva/MRO-Assistent.git
cd MRO-Assistent
```

### 2. Criar o arquivo .env

```bash
nano .env
```

e inserir a chave API KEY gerada no Groq
GROQ_API_KEY=INSERIR_SUA_CHAVE_AQUI

### 3. Criar e ativar o ambiente virtual
Linux/Mac

```bash
python -m venv venv
source venv/bin/activate
```

Windows (PowerShell):

```bash
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### 4. Instalar as dependências

```bash
pip install -r requirements.txt
```

### 5. Executar a aplicação

```bash
streamlit run main.py
```
