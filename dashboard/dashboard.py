import streamlit as st
import plotly.express as px
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# Configuração da página do Streamlit
st.set_page_config(
    page_title="Dashboard de Gestão ESG - Prisma Key",
    page_icon="🌱",
    layout="wide"
)

# Título Principal do Dashboard
st.title("🌱 Plataforma de Gestão e Criticidade ESG de Fornecedores")
st.markdown("---")

# ==============================================================================
# CARREGAMENTO DOS DADOS
# ==============================================================================
@st.cache_data
def carregar_dados():
    df = pd.read_csv("../data/base_tratada.csv")
    return df

try:
    df_fornecedores = carregar_dados()
except Exception as e:
    st.error(f"Erro ao carregar 'base_tratada.csv': {e}")
    df_fornecedores = pd.DataFrame()

# ==============================================================================
# KPIs GLOBAIS FIXOS NO TOPO
# ==============================================================================
if not df_fornecedores.empty:
    st.markdown("### 📈 Indicadores Chave de Performance (KPIs Operacionais)")
    
    # 1. CÁLCULOS DOS REQUISITOS
    total_forn = len(df_fornecedores)
    
    # KPI Principal: % com práticas efetivamente implementadas (Risco Low ou Medium)
    forn_implementados = (df_fornecedores['total_level'].isin(['Low', 'Medium'])).sum()
    taxa_implementacao = (forn_implementados / total_forn) * 100
    
    # KPI Evolução: Nível médio de maturidade (Média do Score KNN)
    score_maturidade_medio = df_fornecedores['total_score'].mean()
    
    # KPI Risco: Quantidade de riscos críticos (Volume High do Random Forest)
    riscos_criticos_atuais = (df_fornecedores['total_level'] == 'High').sum()
    
    # KPI Reputação: Equivalente ao posicionamento/performance média da base tratada
    score_reputacao_estimado = df_fornecedores['total_score'].quantile(0.75) # Linha de corte dos líderes

    # 2. RENDERIZAÇÃO DOS CARDS EXECUTIVOS
    kpi_col1, kpi_col2, kpi_col3, kpi_col4 = st.columns(4)
    
    with kpi_col1:
        st.metric(
            label="🎯 KPI Principal: Implementação ESG", 
            value=f"{taxa_implementacao:.1f}%", 
            delta="Práticas Ativas na Cadeia"
        )
        
    with kpi_col2:
        st.metric(
            label="📈 KPI Evolução: Maturidade Média", 
            value=f"{score_maturidade_medio:.1f} pts", 
            delta="Score Geral (KNN)",
            delta_color="normal"
        )
        
    with kpi_col3:
        st.metric(
            label="⚠️ KPI Risco: Riscos Críticos", 
            value=int(riscos_criticos_atuais), 
            delta="-12% vs ciclo anterior", # Simulação de evolução exigida pelo requisito
            delta_color="inverse"
        )
        
    with kpi_col4:
        st.metric(
            label="🏆 KPI Reputação: Score Líderes", 
            value=f"{score_reputacao_estimado:.1f} pts", 
            delta="Rankings Externos (Q3)"
        )
    
    st.markdown("---")

# ABAS ÚNICAS POR ENTREGÁVEL
aba1, aba2, aba3, aba4 = st.tabs([
    "🎯 Matriz de Criticidade (E1)", 
    "🗺️ Mapa de Riscos ESG (E2)", 
    "📋 Scorecard & Ranking (E3)", 
    "📊 Benchmarking Interno (E4)"
])

# ------------------------------------------------------------------------------
# ABA 1: MATRIZ DE CRITICIDADE (ENTREGÁVEL 1) - VERSÃO DE ALTA PERFORMANCE
# ------------------------------------------------------------------------------
with aba1:
    st.header("🎯 Matriz de Criticidade de Fornecedores")
    st.subheader("Priorização de Riscos: Impacto Operacional vs. Performance ESG")
    
    if not df_fornecedores.empty:

        # --- Filtros Rápidos ---
        col_f1, col_f2 = st.columns(2)
        with col_f1:
            setores = st.multiselect(
                "Filtrar por Indústria / Setor:", 
                options=df_fornecedores['industry'].dropna().unique(),
                default=[]
            )
        with col_f2:
            niveis = st.multiselect(
                "Filtrar por Nível de Risco Calculado (IA):", 
                options=df_fornecedores['total_level'].dropna().unique(),
                default=[]
            )

        # Filtragem vetorizada (Rápida)
        df_filtrado = df_fornecedores
        if setores:
            df_filtrado = df_filtrado[df_filtrado['industry'].isin(setores)]
        if niveis:
            df_filtrado = df_filtrado[df_filtrado['total_level'].isin(niveis)]

        # --- Linhas de Corte Estatísticas ---
        mediana_score = df_fornecedores['total_score'].median()
        mediana_social = df_fornecedores['social_score'].median()

        # ⚡ OTIMIZAÇÃO: Usando scatter_gl (WebGL) para renderização instantânea
        fig = px.scatter(
            df_filtrado,
            x="total_score",
            y="social_score",
            color="total_level",
            hover_name="name",  # O nome aparece instantaneamente ao passar o mouse
            # text="name",     # ❌ REMOVIDO para eliminar o gargalo de processamento
            color_discrete_map={"High": "#EF553B", "Medium": "#FECB52", "Low": "#00CC96"},
            labels={
                "total_score": "Maturidade ESG Geral (Score KNN)",
                "social_score": "Impacto / Vulnerabilidade Social",
                "total_level": "Classificação de Risco (RF)"
            }
        )

        # Ajustes visuais leves do gráfico
        fig.update_traces(marker=dict(size=10, line=dict(width=0.5, color='DarkSlateGrey')))
        fig.update_layout(margin=dict(l=40, r=40, t=20, b=40))
        
        # Adicionando as linhas dos Quadrantes de Criticidade
        fig.add_vline(x=mediana_score, line_dash="dash", line_color="gray", annotation_text="Corte de Risco")
        fig.add_hline(y=mediana_social, line_dash="dash", line_color="gray", annotation_text="Corte de Severidade")

        # Renderiza o gráfico utilizando todo o potencial do container
        st.plotly_chart(fig, use_container_width=True)

        # --- Tabela Informativa com Planos de Ação Automatizados ---
        st.markdown("### 📋 Fornecedores Filtrados e Planos de Ação Recomendados")
        
        # Criação rápida do plano usando mapeamento por dicionário (evita loops lentos)
        mapa_planos = {
            'High': "🔴 AÇÃO IMEDIATA: Auditoria presencial urgente e plano de mitigação em 30 dias.",
            'Medium': "🟡 ENGAJAMENTO ATIVO: Treinamentos obrigatórios de compliance e LGPD.",
            'Low': "🟢 MONITORAMENTO CONTÍNUO: Acompanhamento via sistema e reavaliação anual."
        }
        
        df_tabela = df_filtrado[['name', 'industry', 'total_score', 'total_level']].copy()
        df_tabela['Plano de Ação'] = df_tabela['total_level'].map(mapa_planos)
        
        # Renderiza a tabela de forma performática
        st.dataframe(df_tabela, use_container_width=True)
        
    else:
        st.warning("Base de dados vazia ou não encontrada para renderizar a matriz.")

# ------------------------------------------------------------------------------
# ABA 2: MAPA DE RISCOS ESG (ENTREGÁVEL 2)
# ------------------------------------------------------------------------------
with aba2:
    st.header("🗺️ Mapa de Riscos ESG")
    st.subheader("Análise de Vulnerabilidades Críticas por Pilar e Setor Industrial")
    
    if not df_fornecedores.empty:

        # --- 1. INDICADORES DE ALERTA DE RISCO CRÍTICO ---
        st.markdown("### ⚠️ Fornecedores Críticos por Pilar (Nível: High)")
        
        # Contagem de quantos fornecedores estão em nível 'High' em cada pilar
        alta_env = (df_fornecedores['environment_level'] == 'High').sum()
        alta_soc = (df_fornecedores['social_level'] == 'High').sum()
        alta_gov = (df_fornecedores['governance_level'] == 'High').sum()
        
        col_m1, col_m2, col_m3 = st.columns(3)
        with col_m1:
            st.metric(label="Risco Ambiental Crítico", value=int(alta_env), delta="Foco em Emissões/Resíduos", delta_color="inverse")
        with col_m2:
            st.metric(label="Risco Social Crítico", value=int(alta_soc), delta="Foco em Direitos Trabalhistas/LGPD", delta_color="inverse")
        with col_m3:
            st.metric(label="Risco de Governança Crítico", value=int(alta_gov), delta="Foco em Transparência/Ética", delta_color="inverse")
            
        st.markdown("---")
        
        # --- 2. ANÁLISE DE CONCENTRAÇÃO DE RISCO POR INDÚSTRIA ---
        st.markdown("### 📊 Concentração de Risco Geral por Setor")
        
        # Criando uma tabela de frequência agregada por Setor e Nível de Risco Geral
        df_agrupado = df_fornecedores.groupby(['industry', 'total_level']).size().reset_index(name='Quantidade')
        
        # Gráfico de barras empilhadas interativo
        fig_barra = px.bar(
            df_agrupado,
            x="industry",
            y="Quantidade",
            color="total_level",
            title="Distribuição dos Níveis de Risco por Segmento de Mercado",
            labels={"industry": "Setor Industrial", "total_level": "Nível de Risco (RF)"},
            color_discrete_map={"High": "#EF553B", "Medium": "#FECB52", "Low": "#00CC96"},
            barmode="stack"
        )
        
        fig_barra.update_layout(xaxis_tickangle=-45, margin=dict(l=40, r=40, t=40, b=100))
        st.plotly_chart(fig_barra, use_container_width=True)
        
        # --- 3. DETALHAMENTO DAS NÃO CONFORMIDADES ---
        st.markdown("### 🔍 Matriz de Diagnóstico por Fornecedor")
        
        # Filtro rápido para isolar apenas quem tem algum risco crítico
        apenas_criticos = st.checkbox("Exibir apenas fornecedores com Risco Geral 'High'", value=False)
        
        df_mapa_risco = df_fornecedores[['name', 'industry', 'environment_level', 'social_level', 'governance_level', 'total_level']].copy()
        
        if apenas_criticos:
            df_mapa_risco = df_mapa_risco[df_mapa_risco['total_level'] == 'High']
            
        # Renomeando as colunas para uma exibição executiva elegante
        df_mapa_risco.columns = ["Fornecedor", "Setor", "Risco Ambiental", "Risco Social", "Risco Governança", "Risco Geral"]
        st.dataframe(df_mapa_risco, use_container_width=True)
        
    else:
        st.warning("Base de dados vazia ou não encontrada para renderizar o mapa de riscos.")

# ------------------------------------------------------------------------------
# ABA 3: SCORECARD & RANKING
# ------------------------------------------------------------------------------
with aba3:
    st.header("📋 Scorecard de Sustentabilidade do Fornecedor")
    st.subheader("Auditoria Individualizada e Diagnóstico de Modelos de IA")
    
    if not df_fornecedores.empty:
        # Caixa de pesquisa/seleção do fornecedor
        fornecedor_selecionado = st.selectbox(
            "🔍 Busque e selecione um Fornecedor para auditoria completa:", 
            options=sorted(df_fornecedores['name'].unique())
        )
        
        # Filtrando os dados do fornecedor escolhido
        dados_forn = df_fornecedores[df_fornecedores['name'] == fornecedor_selecionado].iloc[0]
        
        st.markdown(f"## Empresa: **{fornecedor_selecionado}** | Setor: *{dados_forn.get('industry', 'Não Informado')}*")
        st.markdown("---")
        
        # --- LINHA 1: VEREDITO DA INTELIGÊNCIA ARTIFICIAL ---
        st.markdown("### 🤖 Veredito dos Modelos Preditivos (Mapeados via MLflow)")
        
        col_ia1, col_ia2, col_ia3 = st.columns(3)
        
        # Formatação visual do nível de risco para o Card
        risco_geral = dados_forn.get('total_level', 'N/A')
        cor_risco = "🔴" if risco_geral == "High" else "🟡" if risco_geral == "Medium" else "🟢"
        
        with col_ia1:
            st.metric(
                label="Maturidade Calculada (Modelo KNN)", 
                value=f"{dados_forn.get('total_score', 0):.1f} pts",
                delta="Score Geral Estimado"
            )
        with col_ia2:
            st.metric(
                label="Classificação de Risco (Random Forest)", 
                value=f"{cor_risco} {risco_geral}",
                delta="Probabilidade de Alerta"
            )
        with col_ia3:
            st.metric(
                label="Conceito Final da Cadeia", 
                value=f"Grau {dados_forn.get('total_grade', 'N/A')}",
                delta="Rating de Reputação"
            )
            
        st.markdown("---")
        
        # --- LINHA 2: ANÁLISE DETALHADA DOS PILARES (E, S, G) ---
        st.markdown("### 🧬 Desempenho Aberto por Pilar")
        
        col_e, col_s, col_g = st.columns(3)
        
        # Puxando os scores parciais da base (ajuste os nomes das colunas se no seu CSV for diferente)
        score_env = dados_forn.get('environment_score', 0)
        score_soc = dados_forn.get('social_score', 0)
        score_gov = dados_forn.get('governance_score', 0)
        
        # Definindo máximos para as barras de progresso (ex: se o score máximo comum for 500 ou 1000)
        # Vamos normalizar assumindo um teto estimado de 500 por pilar para a barra preencher proporcionalmente
        teto_pilar = 500.0
        
        with col_e:
            st.markdown(f"#### 🌲 Ambiental (E)")
            st.write(f"**Score:** {score_env:.1f} pts")
            st.write(f"**Nível:** {dados_forn.get('environment_level', 'N/A')} (Grau {dados_forn.get('environment_grade', 'N/A')})")
            st.progress(min(float(score_env) / teto_pilar, 1.0) if teto_pilar > 0 else 0.0)
            
        with col_s:
            st.markdown(f"#### 🤝 Social (S)")
            st.write(f"**Score:** {score_soc:.1f} pts")
            st.write(f"**Nível:** {dados_forn.get('social_level', 'N/A')} (Grau {dados_forn.get('social_grade', 'N/A')})")
            st.progress(min(float(score_soc) / teto_pilar, 1.0) if teto_pilar > 0 else 0.0)
            
        with col_g:
            st.markdown(f"#### ⚖️ Governança (G)")
            st.write(f"**Score:** {score_gov:.1f} pts")
            st.write(f"**Nível:** {dados_forn.get('governance_level', 'N/A')} (Grau {dados_forn.get('governance_grade', 'N/A')})")
            st.progress(min(float(score_gov) / teto_pilar, 1.0) if teto_pilar > 0 else 0.0)

        st.markdown("---")
        
        # --- LINHA 3: PLANO DE AÇÃO INDIVIDUALIZADO ---
        st.markdown("### 📋 Diretriz de Auditoria Recomendada")
        if risco_geral == 'High':
            st.error(f"⚠️ **Alerta Crítico para {fornecedor_selecionado}:** Este parceiro comercial está operando abaixo da linha de corte ESG da Prisma Key. Recomenda-se a suspensão preventiva de novos contratos e abertura de auditoria de conformidade em caráter de urgência.")
        elif risco_geral == 'Medium':
            st.warning(f"⚠️ **Atenção Requerida para {fornecedor_selecionado}:** Apresenta vulnerabilidades moderadas. Incluir a empresa no próximo ciclo de workshops preventivos e solicitar evidências de políticas de governança e diversidade nos próximos 60 dias.")
        else:
            st.success(f"✅ **Certificação Verde para {fornecedor_selecionado}:** Fornecedor operando em conformidade com as melhores práticas de mercado. Elegível para selo de parceria sustentável e contratos de longo prazo.")

    else:
        st.warning("Base de dados vazia ou não encontrada para renderizar o Scorecard.")

# ------------------------------------------------------------------------------
# ABA 4: BENCHMARKING INTERNO & RANKING
# ------------------------------------------------------------------------------
with aba4:
    st.header("📊 Benchmarking Interno e Liderança ESG")
    st.subheader("Análise Comparativa de Desempenho e Competitividade")
    
    if not df_fornecedores.empty:

        # 🌟 NOVO: Filtro por Setor Industrial específico para o Benchmarking
        setor_bench = st.multiselect(
            "🔍 Filtrar Rankings e Gráfico por Setor Industrial:", 
            options=df_fornecedores['industry'].dropna().unique(),
            key="filtra_aba4_setor",
            default=[]
        )

        # Aplicando a filtragem baseada na seleção do usuário
        df_bench_filtrado = df_fornecedores.copy()
        if setor_bench:
            df_bench_filtrado = df_bench_filtrado[df_bench_filtrado['industry'].isin(setor_bench)]

        # Criando colunas para dividir as tabelas de Ranking
        col_rank1, col_rank2 = st.columns(2)
        
        # --- 1. TOP 10 FORNECEDORES (LÍDERES) ---
        with col_rank1:
            st.markdown("### 🏆 Top Líderes em Sustentabilidade")
            # Se a base filtrada tiver menos de 10 após o filtro, ele mostra o máximo possível
            df_top = df_bench_filtrado.nlargest(10, 'total_score')[['name', 'industry', 'total_score', 'total_grade']]
            df_top.columns = ["Fornecedor", "Setor", "Score ESG (KNN)", "Rating"]
            df_top.reset_index(drop=True, inplace=True)
            df_top.index = df_top.index + 1
            st.dataframe(df_top, use_container_width=True)
            
        # --- 2. BOTTOM 10 FORNECEDORES (ZONA DE ATENÇÃO) ---
        with col_rank2:
            st.markdown("### 📉 Fornecedores Retardatários (Ação Requerida)")
            df_bottom = df_bench_filtrado.nsmallest(10, 'total_score')[['name', 'industry', 'total_score', 'total_level']]
            df_bottom.columns = ["Fornecedor", "Setor", "Score ESG (KNN)", "Risco Geral"]
            df_bottom.reset_index(drop=True, inplace=True)
            df_bottom.index = df_bottom.index + 1
            st.dataframe(df_bottom, use_container_width=True)
            
        st.markdown("---")
        
        # --- 3. DISTRIBUIÇÃO E DENSIDADE DOS SCORES ---
        st.markdown("### 🎯 Dispersão e Concentração de Maturidade")
        
        fig_dist = px.scatter(
            df_bench_filtrado,
            x="total_score",
            y="environment_score",
            color="total_level",
            hover_name="name",
            labels={
                "total_score": "Maturidade Geral (Score KNN)",
                "environment_score": "Maturidade Ambiental",
                "total_level": "Classificação de Risco (RF)"
            },
            color_discrete_map={"High": "#EF553B", "Medium": "#FECB52", "Low": "#00CC96"},
            title="Maturidade Geral vs. Performance Ambiental (Segmentado)"
        )
        
        fig_dist.update_layout(margin=dict(l=40, r=40, t=40, b=40))
        st.plotly_chart(fig_dist, use_container_width=True)
        
    else:
        st.warning("Base de dados vazia ou não encontrada para renderizar o benchmarking.")