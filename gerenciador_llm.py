#Este arquivo é o manipulador/gerenciador da LLM. Ele é responsável por:

#Inicializar a conexão com o modelo Groq/LLaMA
#Montar as mensagens (system prompt + contexto + pergunta)
#Invocar o modelo e retornar a resposta


#importação e configuração das bibliotecas

# Importação do cliente Groq para LangChain
from langchain_groq import ChatGroq 
# Importação dos tipos de mensagem usados no prompt
from langchain_core.messages import HumanMessage, SystemMessage
# Importação do arquivo de configuração
from config import GROQ_API_KEY, GROQ_MODEL


class LLMHandler:
    def __init__(self):
        # Inicializa o modelo com as configurações definidas no config.py
        # temperature=0.1 valor ajustável para melhorar o modelo
        self.llm = ChatGroq(
            model=GROQ_MODEL,
            api_key=GROQ_API_KEY,
            temperature=0.1,
        )

    def generate_response(self, query, context="", chat_history=""):
        # Monta a lista de mensagens que será enviada ao modelo
        messages = [
            # Mensagem de sistema: define o comportamento e personalidade do assistente
            SystemMessage(content="""Você é um assistente técnico especializado em manutenção de aeronaves.
Responde de forma clara, detalhada e profissional,
baseando-se apenas nas informações fornecidas nos manuais técnicos."""),
            # Mensagem do usuário: inclui histórico, contexto dos PDFs e a pergunta
            HumanMessage(content=f"""Histórico da conversa:
{chat_history}

Contexto dos manuais técnicos (pode conter erros de OCR - interprete e corrija):
{context}

Pergunta atual:
{query}

Instruções:
- Responda de forma clara e detalhada
- Organize em passos numerados quando for procedimento
- Corrija automaticamente erros de OCR
- Use apenas informações do contexto fornecido
- Se o contexto não for suficiente, informe claramente""")
        ]
        try:
            response = self.llm.invoke(messages)
            return response.content.strip()
        except Exception as e:
            return f"Erro ao gerar resposta: {str(e)}"

    def generate_rag_response(self, query, retrieved_docs, chat_history=""):
        if not retrieved_docs:
            return self.generate_response(query, chat_history=chat_history)
        context = "\n\n".join([doc.page_content for doc in retrieved_docs])
        return self.generate_response(
            query=query,
            context=context,
            chat_history=chat_history
        )
