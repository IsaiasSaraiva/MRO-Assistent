### MRO-Assistent
#### Repositório referente a Capacitação e Residência Tecnológica em Tecnologias Aeroespaciais Avançadas com o Instituto de Hardware HBR

<img src="https://hardware.org.br/capacitacao/aero/images/item/item9.webp" alt="Imagem de Exemplo da Fuselagem" width="300"/>

A Capacitação e Residência Tecnológica em Tecnologias Aeroespaciais Avançadas destaca os temas de inteligência artificial, segurança cibernética para aviação e biotecnologia para a área aeroespacial e tem duração de 10 meses. Participarão da Capacitação Básica, durante os três primeiros meses, 120 ingressantes, 40 para cada disciplina. Desses, 30 alunos participarão da fase de Capacitação Avançada de quatro meses, seguida da Residência Tecnológica de três meses em instituições parceiras.

O principal objetivo da Residência Tecnológica em Tecnologias Aeroespaciais Avançadas é a capacitação de profissionais para a área aeroespacial brasileira, principalmente a do Estado de São Paulo, tendo como principal diferencial a relevância dos temas propostos para o setor e a qualidade da capacitação oferecida.

#### O MRO Assistant é uma ferramenta para auxílio de manutenção de aeronaves e na geração de relatórios da ANAC.

---

## 🚀 Como Executar

### Pré-requisitos

- [Docker](https://docs.docker.com/get-docker/) instalado
- [Docker Compose v2](https://docs.docker.com/compose/install/) instalado
- Chave de API da [Groq](https://console.groq.com/)

---

### 1. Clone o repositório

```bash
git clone https://github.com/IsaiasSaraiva/MRO-Assistent.git
cd MRO-Assistent
```

### 2. Configure as variáveis de ambiente

Crie um arquivo `.env` na raiz do projeto:

```bash
cp .env.example .env
```

Edite o `.env` e preencha sua chave da Groq:

```env
GROQ_API_KEY=sua_chave_aqui
```

### 3. Suba os containers

```bash
docker-compose up --build -d
```

> O primeiro build pode levar alguns minutos pois baixa as dependências e o modelo de embeddings.

### 4. Acesse a aplicação

| Serviço | URL |
|---|---|
| Front-end (Interface) | http://localhost:3000 |
| Back-end (API) | http://localhost:8000 |
| Documentação da API | http://localhost:8000/docs |

### 5. Crie seu usuário

Acesse http://localhost:3000, clique em **Cadastre-se** e crie sua conta.

---

## 🛑 Como Parar

```bash
docker-compose down
```


---

## ⚙️ Executar sem Docker (desenvolvimento)

### Back-end

```bash
cd Back-End
python -m venv venv
source venv/bin/activate  # Linux/Mac
pip install -r requirements.txt
uvicorn api:app --port 8000 --reload
```

### Front-end

```bash
cd Front-End
npm install --legacy-peer-deps
npm run dev
```

Acesse http://localhost:3000

---

## 👥 Equipe

- Isaias Abner Lima Saraiva
- Raphael Magalhães Coelho
- Fábio José Justos dos Santos
- André de Souza Tarallo
- Marcos Davi de Souza Castro
