# 🌎 Prisma Key: Sistema Inteligente de Classificação de Risco ESG

## Integrantes
* **Angelita Dias** - [angelita-cesar]
* **Guaraci Rios** - [gbr2]
* **Mikael Mulatinho** - [mmulatinho]

---

## Informações Acadêmicas
* **Instituição:** CESAR School
* **Disciplina:** Machine Learning I & Projeto 3
* **Período:** 2026.1
* **Professores:** João Tinôco e Diego Bezerra
---

##  Sobre a Solução
O Prisma Key é uma solução orientada a dados desenvolvida para o monitoramento preditivo de riscos ESG. Integrando engenharia de dados e modelos supervisionados de Machine Learning, a ferramenta substitui processos manuais de auditoria, classificando com precisão a probabilidade de não conformidade de cada fornecedor e facilitando a geração de planos de ação.

[Google Sites - Projeto Prisma Key](https://sites.google.com/cesar.school/slaesg/home)

---

## Instruções de Compilação e Execução

**Pré-requisitos:** Python 3.9+ instalado.

1. **Clone o repositório:**
   ```bash
   git clone https://github.com/seu-usuario/prisma-key.git
   cd prisma-key
   ```

2. **Crie e ative um ambiente virtual:**
   ```bash
   python -m venv venv
   # No Windows:
   venv\Scripts\activate
   # No Linux/Mac:
   source venv/bin/activate
   ```

3. **Instale as dependências:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Execute o Dashboard (Streamlit):**
   ```bash
   streamlit run app/main.py
   ```

### 2. Execução via Docker

**Pré-requisitos:** Docker instalado.

1. **Construa a imagem:**
   ```bash
   docker build -t prisma-key .
   ```

2. **Execute o container:**
   ```bash
   docker run -p 8501:8501 prisma-key
   ```
   *Após a execução, acesse `http://localhost:8501` no seu navegador.*


## 🛠️ Estrutura do Repositório

```text
├── data/           # Amostras da base de dados de fornecedores
├── notebooks/      # Análise Exploratória (EDA) e prototipagem de modelos
├── src/            # Scripts modulares de pré-processamento e treinamento
├── app/            # Código da aplicação (Dashboard Streamlit)
├── mlruns/         # Rastreamento de experimentos e métricas (MLflow)
├── Dockerfile      # Configuração para containerização da solução
├── requirements.txt # Dependências do projeto
└── README.md       # Documentação principal
