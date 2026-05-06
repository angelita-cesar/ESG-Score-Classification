# Prisma Key: Sistema Inteligente de Classificação de Risco ESG

## Integrantes
* **Angelita Dias** - [angelita-cesar]
* **Guaraci Rios** - []
* **Mikael Mulatinho** - []

---

## Informações Acadêmicas
* **Instituição:** CESAR School
* **Disciplina:** Machine Learning I & Projeto 3
* **Período:** 2026.1
* **Professores:** João Tinôco e Diego Bezerra
---

## 🚀 Sobre a Solução (SIDD-ESG)
O **Prisma Key** é uma ferramenta avançada de análise de conformidade e risco para fornecedores, baseada em pilares Ambientais, Sociais e de Governança. O sistema vai além do simples preenchimento de formulários, utilizando Machine Learning para combater o greenwashing e identificar riscos ocultos.

### Diferenciais Técnicos:
* **NLP Forense:** Análise de densidade semântica para validar se as explicações dos fornecedores possuem evidências reais ou são apenas textos genéricos.
* **Modelo Híbrido:**
    * **Árvore de Decisão:** Implementação de regras críticas de negócio (Sanções, Compliance, Inconsistências).
    * **KNN (K-Nearest Neighbors):** Utilizado para **Benchmarking Interno** e detecção de *outliers*. Se um fornecedor apresenta scores distantes dos seus pares de setor/porte, o sistema gera um alerta de auditoria.
* **Materialidade Dinâmica:** Pesos automáticos baseados no setor (ex: Setor industrial foca mais no pilar Ambiental; Setor de tecnologia foca mais no pilar Social).

---

## 🛠️ Estrutura do Repositório
A organização do projeto segue as melhores práticas de MLOps:

```text
├── data/           # Amostras da base de dados de fornecedores
├── notebooks/      # Análise Exploratória (EDA) e prototipagem de modelos
├── src/            # Scripts modulares de pré-processamento e treinamento
├── app/            # Código da aplicação (Dashboard Streamlit)
├── mlruns/         # Rastreamento de experimentos e métricas (MLflow)
├── Dockerfile      # Configuração para containerização da solução
├── requirements.txt # Dependências do projeto
└── README.md       # Documentação principal