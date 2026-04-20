from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage
from config import GROQ_API_KEY, GROQ_MODEL
import json


class LLMHandler:
    def __init__(self):
        self.llm = ChatGroq(
            model=GROQ_MODEL,
            api_key=GROQ_API_KEY,
            temperature=0.1,
        )

    def _detectar_modo(self, query: str) -> str:
        query_lower = query.lower()

        palavras_formulario015 = [
            "formulário 015", "formulario 015", "form 015",
            "formulário 15", "formulario 15", "form 15",
            "relatório 015", "relatorio 015", "formulario anac",
            "formulário anac"
        ]
        palavras_relatorio = [
            "gere um relatório", "gerar relatório", "crie um relatório",
            "relatório mensal", "relatório de serviços", "gere o relatório",
            "fazer relatório", "montar relatório", "gere relatório",
            "cria um relatório", "elabore um relatório", "elaborar relatório",
            "gerar report", "gere report"
        ]
        palavras_resumo = [
            "resumo", "resuma", "resume", "sintetize", "síntese",
            "principais pontos", "pontos principais", "o que fala",
            "do que se trata", "sobre o que é", "me explique o documento",
            "explique o manual", "explique esse pdf"
        ]
        palavras_analise = [
            "analise", "análise", "compare", "comparação", "liste",
            "quais são", "quais os", "me dê uma lista", "extraia",
            "identifique", "encontre", "busque"
        ]

        # Formulário 015 tem prioridade sobre relatório genérico
        if any(p in query_lower for p in palavras_formulario015):
            return "formulario015"
        elif any(p in query_lower for p in palavras_relatorio):
            return "relatorio"
        elif any(p in query_lower for p in palavras_resumo):
            return "resumo"
        elif any(p in query_lower for p in palavras_analise):
            return "analise"
        else:
            return "assistente"

    def extrair_dados_formulario(self, query: str, context: str = "") -> dict:
        """
        Usa a LLM para extrair os dados do formulário 015 da mensagem
        do usuário e/ou do contexto RAG dos documentos anexados.
        Retorna um dict com os campos do formulário.
        """
        messages = [
            SystemMessage(content="""Você é um extrator de dados para o Formulário 015 da ANAC.
Extraia os dados do texto do usuário E do contexto dos documentos anexados.
NUNCA invente dados não fornecidos — use string vazia "" para campos ausentes.
Retorne SOMENTE o JSON válido, sem texto adicional, sem markdown, sem explicações."""),

            HumanMessage(content=f"""
Extraia os dados e retorne JSON com exatamente esta estrutura:

{{
  "nome_empresa": "",
  "endereco": "",
  "cidade_uf": "",
  "mes_ano": "",
  "responsavel_tecnico": "",
  "servicos": [
    {{
      "tipo_produto": "",
      "marca": "",
      "numero_serie": "",
      "modelo": "",
      "fabricante": "",
      "numero_os": "",
      "local_execucao": "",
      "data_inicio": "",
      "data_fim": ""
    }}
  ],
  "observacoes": ""
}}

Contexto extraído dos documentos anexados:
{context}

Mensagem do usuário:
{query}

Regras:
- Priorize os dados do contexto dos documentos
- Complemente com os dados da mensagem do usuário
- tipo_produto: apenas AERONAVE, MOTOR, HELICE, RADIO, INSTRUMENTO, ACESSORIO ou SERVICO ESPECIALIZADO
- marca: preencher somente se tipo_produto for AERONAVE
- data_fim: vazio se serviço ainda não concluído
- Pode haver múltiplos serviços no array
- Retorne SOMENTE o JSON, sem nenhum texto antes ou depois
""")
        ]

        try:
            response = self.llm.invoke(messages)
            texto = response.content.strip()
            texto = texto.replace("```json", "").replace("```", "").strip()
            return json.loads(texto)
        except Exception:
            return {
                "nome_empresa": "",
                "endereco": "",
                "cidade_uf": "",
                "mes_ano": "",
                "responsavel_tecnico": "",
                "servicos": [{
                    "tipo_produto": "", "marca": "", "numero_serie": "",
                    "modelo": "", "fabricante": "", "numero_os": "",
                    "local_execucao": "", "data_inicio": "", "data_fim": ""
                }],
                "observacoes": ""
            }

    def generate_response(self, query, context="", chat_history=""):

        modo = self._detectar_modo(query)

        if modo == "relatorio":
            system_content = """Você é um assistente técnico especializado em manutenção de aeronaves (MRO)
e gerador de relatórios técnicos profissionais no padrão ANAC/SIGRAC com formatação ABNT.

FORMATAÇÃO OBRIGATÓRIA:
- Use # para título principal (será centralizado automaticamente)
- Use ## para seções numeradas
- Use tabelas markdown SEM negrito dentro das células (NUNCA use ** dentro de | |)
- Use **negrito** apenas em textos fora das tabelas
- Separe todas as seções com ---

DADOS DA EMPRESA E RESPONSÁVEL:
- Use APENAS os dados que o usuário informou na mensagem
- Se não informou nome da empresa, use [Nome da Empresa]
- Se não informou responsável técnico, use [Responsável Técnico]
- NUNCA invente ou assuma dados não fornecidos

ESTRUTURA OBRIGATÓRIA (padrão ABNT/ANAC):

# Título Oficial do Relatório
## 1. Introdução
## 2. Identificação
## 3. Serviços Executados
## 4. Considerações Técnicas
## 5. Observações
## 6. Conclusão
## 7. Responsável Técnico

PROIBIDO:
- NUNCA use ** dentro de células de tabela
- NUNCA invente dados da empresa ou responsável
- NÃO mencionar SIGRAC, Santos Dumont ou links externos"""

        elif modo == "resumo":
            system_content = """Você é um assistente especializado em análise de documentos técnicos.
Estruture o resumo em seções: Sobre o Documento, Principais Tópicos, Informações-Chave, Conclusão.
Use **negrito** para termos importantes e listas quando apropriado.
Adapte ao tipo de documento (manual técnico, relatório, norma, etc.)"""

        elif modo == "analise":
            system_content = """Você é um assistente especializado em análise técnica de documentos.
Seja preciso e detalhado. Use listas e tabelas quando facilitar a leitura.
Use **negrito** para destacar informações críticas.
Adapte ao contexto do documento (aeronáutico, industrial, mecânico, etc.)"""

        elif modo == "formulario015":
            system_content = """Você é um assistente técnico MRO.
O formulário 015 da ANAC está sendo gerado automaticamente com os dados fornecidos.
Responda de forma curta e profissional confirmando a geração."""

        else:
            system_content = """Você é um assistente técnico inteligente especializado em:
- Manutenção de aeronaves (MRO)
- Análise de documentos técnicos de qualquer tipo
- Resposta a perguntas sobre manuais, relatórios e documentação técnica
- Geração de relatórios profissionais

Responda de forma clara, detalhada e profissional.
Use as informações dos documentos fornecidos e seu conhecimento técnico.
Se o documento for de outra área (não aeronáutica), adapte sua resposta ao contexto."""

        messages = [
            SystemMessage(content=system_content),
            HumanMessage(content=f"""Histórico da conversa:
{chat_history}

Contexto extraído dos documentos (corrija erros de OCR automaticamente):
{context}

Solicitação do usuário:
{query}

Instruções:
- Use as informações do contexto E do conhecimento técnico disponível
- Corrija erros de OCR automaticamente
- Adapte a linguagem ao tipo de documento
- Quando gerar relatórios: NUNCA use ** dentro de células de tabela
- NUNCA invente dados da empresa ou do responsável técnico
- Seja profissional e preciso""")
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

    def generate_report(self, retrieved_docs, mes_ano: str, empresa: dict) -> str:
        context = "\n\n".join([doc.page_content for doc in retrieved_docs]) if retrieved_docs else ""

        nome = empresa.get('nome') or '[Nome da Empresa]'
        endereco = empresa.get('endereco') or '[Endereço]'
        cidade_uf = empresa.get('cidade_uf') or '[Cidade/UF]'
        responsavel = empresa.get('responsavel') or '[Responsável Técnico]'

        messages = [
            SystemMessage(content="""Você é um sistema especializado em gerar relatórios técnicos
de manutenção aeronáutica no padrão ANAC/SIGRAC com formatação ABNT.
Saída APENAS o relatório em markdown profissional.
NUNCA invente dados da empresa ou do responsável técnico.
NUNCA use ** dentro de células de tabela.
NUNCA adicione instruções sobre SIGRAC, links externos ou passos para o usuário."""),

            HumanMessage(content=f"""
Gere o Relatório Mensal de Serviços Executados com base nos dados abaixo.

=== INFORMAÇÕES DA EMPRESA ===
Nome: {nome}
Endereço: {endereco}
Cidade/UF: {cidade_uf}
Responsável Técnico: {responsavel}

=== MÊS/ANO ===
{mes_ano}

=== DADOS DOS DOCUMENTOS ===
{context}

Estrutura obrigatória:
# Título | ## 1. Introdução | ## 2. Identificação (tabela) |
## 3. Serviços Executados (tabela) | ## 4. Considerações Técnicas |
## 5. Observações | ## 6. Conclusão | ## 7. Responsável Técnico

Regras:
- NUNCA use ** dentro de células de tabela
- Tipo de Produto: AERONAVE, MOTOR, HELICE, RADIO, INSTRUMENTO, ACESSORIO ou SERVICO ESPECIALIZADO
- Marca: somente se AERONAVE
- Local: sigla ICAO ou cidade
- Data de Fim em branco se em aberto
""")
        ]

        try:
            response = self.llm.invoke(messages)
            return response.content.strip()
        except Exception as e:
            return f"Erro ao gerar relatório: {str(e)}"