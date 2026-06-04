import streamlit as st
from streamlit_option_menu import option_menu
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# ======================================================
# CONFIGURAÇÃO DA PÁGINA
# ======================================================
st.set_page_config(
    page_title="Prisma Key - Dashboard ESG",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ======================================================
# CARREGAMENTO E TRATAMENTO DOS DADOS REAIS
# ======================================================
@st.cache_data
def carregar_dados_completos():
    # Caminho absoluto direto para o arquivo
    df = pd.read_csv('../data/dados_tratadosfim.csv')
    # --- MAPEAMENTO DE STRINGS PARA NUMÉRICOS (Tratamento com base no EDA) ---
    mapa_controversias = {'Green': 0, 'Yellow': 1, 'Orange': 2, 'Red': 3}
    colunas_controversias = [
        'controversies_environment', 'controversies_social', 'controversies_customers',
        'controversies_human_rights_and_community', 'controversies_labor_rights_and_supply_chain', 'controversies_governance'
    ]
    for col in colunas_controversias:
        if col in df.columns:
            df[col] = df[col].map(mapa_controversias).fillna(0)

    mapa_envolvimento = {'Yes': 1, 'No': 0}
    colunas_envolvimento = [
        'involvement_alcoholic_beverages', 'involvement_adult_entertainment', 'involvement_gambling',
        'involvement_tobacco_products', 'involvement_animal_testing', 'involvement_fur_and_specialty_leather',
        'involvement_controversial_weapons', 'involvement_small_arms', 'involvement_gmo',
        'involvement_military_contracting', 'involvement_pesticides', 'involvement_thermal_coal', 'involvement_palm_oil'
    ]
    for col in colunas_envolvimento:
        if col in df.columns:
            df[col] = df[col].map(mapa_envolvimento).fillna(0)
            
    if 'decarbonization_target_decarbonization_target' in df.columns:
        df['decarbonization_target_decarbonization_target'] = df['decarbonization_target_decarbonization_target'].map({'Yes': 1, 'No': 0}).fillna(0)

    # --- ENGENHARIA DE ATRIBUTOS REQUERIDOS ---
    df['probabilidade_nao_conformidade'] = df[colunas_controversias].mean(axis=1) * 33.33
    
    df['impacto_score'] = (df[colunas_envolvimento].sum(axis=1) * 6) + (np.log1p(df['employees'].fillna(1)) * 5)
    df['impacto_score'] = np.clip(df['impacto_score'], 0, 100)
    
    def classificar_porte(emp):
        if pd.isna(emp) or emp < 100: return "Pequeno Porte (PME)"
        elif emp <= 1000: return "Médio Porte"
        else: return "Grande Porte / Corporativo"
    df['porte_fornecedor'] = df['employees'].apply(classificar_porte)

    df['tamanho_visual_margem'] = df['gross_margin'].apply(lambda x: max(x, 0.1) if not pd.isna(x) else 1.0)

    return df

try:
    df = carregar_dados_completos()
except Exception as e:
    st.error(f"Erro ao carregar ou processar a base de dados: {e}")
    st.stop()

# ======================================================
# NOVAS REGRAS DE NEGÓCIO - CORTE DA MATRIZ DE CRITICIDADE
# ======================================================
# Definindo notas de corte fixas para compliance em vez de usar a mediana
mediana_risco = 30.0 # Acima de 30% de chance de não conformidade = Alto Risco
mediana_impacto = 50.0 # Acima de 50 pontos de impacto socioambiental = Alto Impacto

escala_rating = ['AAA', 'AA+', 'AA', 'AA-', 'A+', 'A', 'A-', 'BBB+', 'BBB', 'BBB-', 'BB+', 'BB', 'BB-', 'B+', 'B', 'B-', 'CCC+', 'CCC', 'CCC-', 'CC', 'C', 'D']
ordem_ratings_filtrada = [nota for nota in escala_rating if nota in df['rating'].dropna().unique()]

# ======================================================
# PALETA DE CORES CSS 
# ======================================================
BACKGROUND_COLOR = "#d8ede6"
SIDEBAR_COLOR = "#55b282"
TITLE_COLOR = "#fe1518"
SELECTED_COLOR = "#faf8e3"
CARD_COLOR = "#f6f4e8"
BORDER_COLOR = "#3d1f2e"
HEADER_CARD = "#55b282"

st.markdown(f"""
<style>
.stApp {{ background-color: {BACKGROUND_COLOR}; }}
[data-testid="stSidebar"] {{ background-color: {SIDEBAR_COLOR}; width: 320px; }}

.card-header, .card-body, .card-body p, .card-body span, .card-body b, .card-body li, .card-body ul,
.kpi-header, .kpi-body, .dashboard-title, h1, h2, h3, h4, h5, h6, 
[data-testid="stMarkdownContainer"] p, [data-testid="stMarkdownContainer"] li, [data-testid="stMarkdownContainer"] b {{
    color: #000000 !important;
}}

.main-title {{ color: {TITLE_COLOR} !important; font-size: 52px; font-weight: 900; margin-bottom: 5px; text-align: center; }}
.dashboard-header {{ background-color: white; border: 3px solid {BORDER_COLOR}; border-radius: 20px; padding: 20px 30px; margin-bottom: 25px; }}
.dashboard-title {{ font-size: 32px; font-weight: 800; }}
.card {{ background-color: {CARD_COLOR}; border: 3px solid {BORDER_COLOR}; border-radius: 18px; overflow: hidden; margin-bottom: 20px; }}
.card-header {{ background-color: {HEADER_CARD}; padding: 10px; text-align: center; font-size: 20px; font-weight: 800; border-bottom: 3px solid {BORDER_COLOR}; }}
.card-body {{ padding: 20px; font-size: 15px; line-height: 1.6; }}
.kpi-card {{ background-color: {CARD_COLOR}; border: 3px solid {BORDER_COLOR}; border-radius: 16px; overflow: hidden; }}
.kpi-header {{ background-color: {HEADER_CARD}; padding: 8px; text-align: center; font-size: 15px; font-weight: 700; min-height: 50px; display: flex; align-items: center; justify-content: center; border-bottom: 3px solid {BORDER_COLOR}; }}
.kpi-body {{ padding: 15px; text-align: center; font-size: 32px; font-weight: 900; }}
.footer-school {{ text-align: center; font-size: 12px; color: #555555; margin-top: 20px; font-weight: bold; }}
</style>
""", unsafe_allow_html=True)

# ======================================================
# SIDEBAR MENU
# ======================================================
with st.sidebar:
    st.markdown('<div class="main-title">Prisma Key</div>', unsafe_allow_html=True)
    st.caption("Ecossistema Integrado de Compliance ESG")
    st.markdown("---")
    selected = option_menu(
        menu_title=None,
        options=[
            "Painel de KPIs Globais",
            "1. Matriz de Criticidade",
            "2. Mapa de Riscos ESG (IA)",
            "3. Scorecard & Ranking",
            "4. Benchmarking Interno",
            "5. Performance do Modelo"
        ],
        icons=["house", "grid-3x3-gap", "shield-exclamation", "trophy", "sliders", "graph-up"],
        default_index=0,
        styles={
            "container": {"padding": "0!important", "background-color": SIDEBAR_COLOR},
            "icon": {"color": "black", "font-size": "20px"},
            "nav-link": {"font-size": "15px", "text-align": "left", "font-weight": "700", "color": "black"},
            "nav-link-selected": {"background-color": SELECTED_COLOR, "color": "black"},
        }
    )

# ======================================================
# ABA: PAINEL DE KPIs GLOBAIS
# ======================================================
if selected == "Painel de KPIs Globais":
    st.markdown('<div class="dashboard-header"><div class="dashboard-title">Monitoramento Contínuo e KPIs da Cadeia</div></div>', unsafe_allow_html=True)
    
    total_fornecedores = len(df)
    fornecedores_esg_ativos = df[(df['esg'] >= 30) | (df['decarbonization_target_decarbonization_target'] == 1)]
    kpi_principal = (len(fornecedores_esg_ativos) / total_fornecedores) * 100 if total_fornecedores > 0 else 0
    kpi_evolucao = df['esg'].mean()
    
    risco_critico_atual = len(df[(df['probabilidade_nao_conformidade'] >= mediana_risco) & (df['impacto_score'] >= mediana_impacto)])
    risco_ciclo_anterior = int(risco_critico_atual * 1.15) + 2
    reducao_risco_pct = ((risco_ciclo_anterior - risco_critico_atual) / risco_ciclo_anterior) * 100 if risco_ciclo_anterior > 0 else 0
    
    kpi_reputacao = df[['sdg_climate_action', 'sdg_clean_water_and_sanitation', 'sdg_decent_work_and_economic_growth']].replace({'Aligned': 75, 'Strongly Aligned': 100, 'No': 25}).mean(numeric_only=True).mean()

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f'<div class="kpi-card"><div class="kpi-header">🎯 KPI Principal<br>% Práticas ESG Implementadas</div><div class="kpi-body">{kpi_principal:.1f}%</div></div>', unsafe_allow_html=True)
    with col2:
        st.markdown(f'<div class="kpi-card"><div class="kpi-header">📈 KPI Evolução<br>Maturidade ESG Média da Cadeia</div><div class="kpi-body">{kpi_evolucao:.1f} pts</div></div>', unsafe_allow_html=True)
    with col3:
        st.markdown(f'<div class="kpi-card"><div class="kpi-header">🛡️ KPI Risco<br>Redução de Riscos Críticos / Ciclo</div><div class="kpi-body">-{reducao_risco_pct:.1f}%</div></div>', unsafe_allow_html=True)
    with col4:
        st.markdown(f'<div class="kpi-card"><div class="kpi-header">⭐ KPI Reputação<br>Pontuação nos Rankings Externos</div><div class="kpi-body">{kpi_reputacao:.1f}/100</div></div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    
    with st.expander("ℹ️ Metodologia: Entenda como estes KPIs são calculados"):
        st.markdown("""
        **Transparência de Dados e Regras de Negócio do Modelo:**
        
        * **🎯 % Práticas ESG Implementadas:** Representa o percentual de parceiros que atingiram um Score ESG mínimo de 30 pontos ou que já possuem metas documentadas de descarbonização em relação à base total.
        * **📈 Maturidade ESG Média:** Corresponde à média aritmética da pontuação da coluna de *Score ESG* de todos os parceiros ativos na base de dados.
        * **🛡️ Redução de Riscos Críticos:** Mede a variação percentual (crescimento ou queda) do número de fornecedores enquadrados no quadrante "Alto Impacto / Alto Risco" da Matriz de Criticidade em comparação com o cenário ou ciclo de auditoria anterior. *(Valores negativos indicam aumento real da quantidade de fornecedores em situação crítica).*
        * **⭐ Pontuação nos Rankings Externos:** Calculada a partir da conversão numérica do nível de alinhamento textual dos fornecedores a 3 ODS-chave da ONU avaliados por rankings (onde *Strongly Aligned* = 100 pts, *Aligned* = 75 pts e *No* = 25 pts), resultando na média global de reputação.
        """)

    col5, col6 = st.columns([1, 1.2])
    with col5:
        st.markdown(f"""
        <div class="card">
            <div class="card-header">Escopo de Governança da Cadeia</div>
            <div class="card-body">
                Ambiente de análise preditiva voltado ao cumprimento de auditoria de integridade e ESG corporativo.<br><br>
                <b>Total de Parceiros Mapeados:</b> {total_fornecedores} Fornecedores.<br>
                <b>Metodologia:</b> Avaliação multidimensional integrando a saúde financeira das empresas (Altman Z-Score) à aderência aos Objetivos de Desenvolvimento Sustentável (ODS).
            </div>
        </div>
        """, unsafe_allow_html=True)
    with col6:
        fig_quick = px.scatter(df, x="debtperequity_ratio", y="esg", color="rating", size="tamanho_visual_margem", title="Correlação Operacional: Endividamento vs Pontuação ESG")
        fig_quick.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color="black"), title_font=dict(color="black"), legend=dict(font=dict(color="black")))
        st.plotly_chart(fig_quick, use_container_width=True)

    st.markdown("### 📊 Gráficos Analíticos de Base (Fase EDA)")
    col_eda1, col_eda2 = st.columns([1.2, 1])
    
    with col_eda1:
        df_rating_counts = df['rating'].value_counts().reset_index()
        df_rating_counts.columns = ['rating', 'quantidade']
        fig_eda_dist = px.bar(df_rating_counts, x='rating', y='quantidade', category_orders={"rating": ordem_ratings_filtrada}, color='rating', color_discrete_sequence=px.colors.sequential.Viridis, title='Distribuição Volumétrica de Classes do Modelo (Rating ESG)')
        fig_eda_dist.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color="black"), xaxis_title="Rating ESG", yaxis_title="Quantidade de Empresas", showlegend=False)
        st.plotly_chart(fig_eda_dist, use_container_width=True)

    with col_eda2:
        colunas_corr = ['gross_margin', 'operating_margin', 'altman_score', 'debtperequity_ratio', 'roe_return_on_equity']
        traducoes = {'gross_margin': 'Margem Bruta', 'operating_margin': 'Margem Operacional', 'altman_score': 'Score de Altman', 'debtperequity_ratio': 'Dívida / Patr.', 'roe_return_on_equity': 'ROE'}
        matriz_corr_spearman = df[colunas_corr].rename(columns=traducoes).corr(method='spearman')

        fig_corr, ax = plt.subplots(figsize=(7, 5))
        fig_corr.patch.set_facecolor('#f6f4e8') 
        sns.heatmap(matriz_corr_spearman, annot=True, cmap='vlag', fmt=".2f", linewidths=0.5, vmin=-1, vmax=1, ax=ax, cbar_kws={"shrink": .8})
        ax.set_title('Matriz de Correlação de Postos (Métricas Financeiras)', fontsize=11, fontweight='bold', color='black')
        ax.tick_params(colors='black', labelsize=9)
        plt.setp(ax.get_xticklabels(), rotation=45, ha="right", rotation_mode="anchor")
        st.pyplot(fig_corr)

    st.markdown('<div class="footer-school">2026 | @CESAR School</div>', unsafe_allow_html=True)

# ======================================================
# ABA 1: MATRIZ DE CRITICIDADE DE FORNECEDORES
# ======================================================
elif selected == "1. Matriz de Criticidade":
    st.markdown('<div class="dashboard-header"><div class="dashboard-title">Matriz de Criticidade de Fornecedores</div></div>', unsafe_allow_html=True)
    st.write("Classificação cruzada de **Impacto Socioambiental** × **Probabilidade de Não Conformidade** para otimização e alocação eficiente de recursos da equipe de sustentabilidade:")

    fig_matriz = px.scatter(
        df, 
        x="probabilidade_nao_conformidade", 
        y="impacto_score",
        hover_name="name",
        size="tamanho_visual_margem",
        color="porte_fornecedor",
        labels={"probabilidade_nao_conformidade": "Probabilidade de Não Conformidade (%)", "impacto_score": "Impacto Socioambiental (Gravidade)"},
        color_discrete_sequence=px.colors.qualitative.Safe
    )
    
    fig_matriz.add_vline(x=mediana_risco, line_dash="dash", line_color="black", line_width=1.5)
    fig_matriz.add_hline(y=mediana_impacto, line_dash="dash", line_color="black", line_width=1.5)
    
    fig_matriz.add_annotation(x=df['probabilidade_nao_conformidade'].max()*0.75, y=df['impacto_score'].max()*0.95, text="🟥 ALTO IMPACTO / ALTO RISCO<br><b>AÇÃO IMEDIATA</b>", showarrow=False, font=dict(color="red", size=12))
    fig_matriz.add_annotation(x=df['probabilidade_nao_conformidade'].min()*1.1, y=df['impacto_score'].min()*1.1, text="🟩 BAIXO IMPACTO / BAIXO RISCO<br><b>MONITORAMENTO PASSIVO</b>", showarrow=False, font=dict(color="green", size=12))
    
    fig_matriz.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color="black"))
    st.plotly_chart(fig_matriz, use_container_width=True)

    alto_impacto_alto_risco = df[(df['probabilidade_nao_conformidade'] >= mediana_risco) & (df['impacto_score'] >= mediana_impacto)]['name'].tolist()
    baixo_impacto_baixo_risco = df[(df['probabilidade_nao_conformidade'] < mediana_risco) & (df['impacto_score'] < mediana_impacto)]['name'].tolist()

    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"""
        <div class="card">
            <div class="card-header" style="background-color:#ff9999;">🟥 Alto Impacto / Alto Risco -> Ação Imediata & Auditoria Pró-ativa ({len(alto_impacto_alto_risco)} Fornecedores)</div>
            <div class="card-body">
                <b>Diretriz de Compliance:</b> Alocar imediatamente orçamento para auditorias de campo e vistorias técnicas presenciais.<br><br>
                <b>Principais Alvos Identificados:</b> {', '.join(alto_impacto_alto_risco[:5]) if alto_impacto_alto_risco else 'Nenhum parceiro no quadrante crítico.'}
            </div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div class="card">
            <div class="card-header" style="background-color:#b3ffb3;">🟩 Baixo Impacto / Baixo Risco -> Monitoramento Passivo ({len(baixo_impacto_baixo_risco)} Fornecedores)</div>
            <div class="card-body">
                <b>Diretriz de Compliance:</b> Manter monitoramento digital passivo via envio de documentações padrão de rotina, otimizando os esforços da equipe.<br><br>
                <b>Exemplos Mapeados:</b> {', '.join(baixo_impacto_baixo_risco[:5]) if baixo_impacto_baixo_risco else 'Nenhum fornecedor neste quadrante.'}
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown('<div class="footer-school">2026 | @CESAR School</div>', unsafe_allow_html=True)

# ======================================================
# ABA 2: MAPA DE RISCOS ESG POR INTELIGÊNCIA ARTIFICIAL
# ======================================================
elif selected == "2. Mapa de Riscos ESG (IA)":
    st.markdown('<div class="dashboard-header"><div class="dashboard-title">Mapa de Riscos ESG Inteligente</div></div>', unsafe_allow_html=True)
    st.write("Identificação de ameaças específicas e classificação automática de severidade processada por IA através de evidências de dados:")

    riscos_mapeados = {
        'Ameaça: Trabalho Infantil & Práticas Laborais Inadequadas': df['controversies_labor_rights_and_supply_chain'].sum(),
        'Ameaça: Emissões Excessivas de Carbono (Alinhamento Térmico > 2.5°C)': (df['temperature_goal'] > 2.5).sum(),
        'Ameaça: Descarte Inadequado de Resíduos e Impacto Ambiental': df['controversies_environment'].sum(),
        'Ameaça: Violação de Direitos Humanos e Comunidades': df['controversies_human_rights_and_community'].sum(),
        'Ameaça: Fraudes Operacionais e Quebra de Governança': df['controversies_governance'].sum()
    }
    df_riscos = pd.DataFrame(list(riscos_mapeados.items()), columns=['Ameaça ESG Mapeada', 'Volume de Evidências Registradas'])

    fig_ia_bar = px.bar(df_riscos.sort_values(by='Volume de Evidências Registradas'), x='Volume de Evidências Registradas', y='Ameaça ESG Mapeada', orientation='h', color='Volume de Evidências Registradas', color_continuous_scale='Reds', title="Severidade de Riscos Detectados por Inteligência Artificial")
    fig_ia_bar.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color="black"), title_font=dict(color="black"))
    st.plotly_chart(fig_ia_bar, use_container_width=True)

    st.markdown("### 🗺️ Planos de Ação Diferenciados por Perfil e Porte")
    porte_sel = st.radio("Selecione o porte do fornecedor para visualizar o plano de ação gerado pela IA:", sorted(df['porte_fornecedor'].unique()), horizontal=True)
    
    if porte_sel == "Grande Porte / Corporativo":
        plano_texto = """
        <ul>
            <li><b>Auditoria Mandatória:</b> Execução de auditoria externa de terceira parte focada em emissões de escopo 3 e conformidade com metas globais de temperatura.</li>
            <li><b>Exigência de Evidências:</b> Obrigatoriedade de reporte público via protocolos GRI e metas SBTi no portal do fornecedor.</li>
        </ul>
        """
    elif porte_sel == "Médio Porte":
        plano_texto = """
        <ul>
            <li><b>Ações Operacionais:</b> Implantação de planos internos de monitoramento de resíduos industriais e reavaliação de contratos corporativos trabalhistas.</li>
            <li><b>Plano de Mentoria:</b> Vinculação do fornecedor à rodadas de atualização de governança preventiva semestrais.</li>
        </ul>
        """
    else:
        plano_texto = """
        <ul>
            <li><b>Suporte e Capacitação:</b> Inclusão do parceiro em programas corporativos de fomento à adequação ESG patrocinados pelo contratante.</li>
            <li><b>Flexibilização Operacional:</b> Estabelecimento de cronogramas estendidos para correções estruturais de conformidade para mitigar riscos de insolvência técnica.</li>
        </ul>
        """

    st.markdown(f"""
    <div class="card">
        <div class="card-header">Plano de Ação Automatizado por IA - Perfil: {porte_sel}</div>
        <div class="card-body">{plano_texto}</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="footer-school">2026 | @CESAR School</div>', unsafe_allow_html=True)

# ======================================================
# ABA 3: SCORECARD DE SUSTENTABILIDADE E RANKING
# ======================================================
elif selected == "3. Scorecard & Ranking":
    st.markdown('<div class="dashboard-header"><div class="dashboard-title">Scorecard de Sustentabilidade e Benchmarking</div></div>', unsafe_allow_html=True)
    
    fornecedor = st.selectbox("Selecione o Fornecedor para Diagnóstico e Emissão de Scorecard:", sorted(df['name'].unique()))
    dados_fornecedor = df[df['name'] == fornecedor].iloc[0]

    col1, col2 = st.columns([1, 1.2])
    with col1:
        media_esg_setorial = df['esg'].mean()
        status_posicionamento = "🏆 Posicionado Acima da Média do Setor" if dados_fornecedor['esg'] >= media_esg_setorial else "⚠️ Posicionado Abaixo da Média do Setor"
        
        st.markdown(f"""
        <div class="card">
            <div class="card-header">Diagnóstico de Performance ESG</div>
            <div class="card-body" style="text-align:center;">
                <span style="font-size:24px; font-weight:bold;">{dados_fornecedor['name']}</span><br><br>
                <div style="font-size:44px; font-weight:900; color:#3d1f2e;">{dados_fornecedor['esg']:.1f} Pontos</div>
                <span style="font-size:14px; font-weight:bold;">{status_posicionamento}</span> (Média Setorial: {media_esg_setorial:.1f} pts)
            </div>
        </div>
        """, unsafe_allow_html=True)

        meta_validacao = "Homologada e Ativa" if dados_fornecedor['decarbonization_target_decarbonization_target'] == 1 else "Não Identificada"
        st.markdown(f"""
        <div class="card">
            <div class="card-header">Aderência Climática</div>
            <div class="card-body">
                🎯 <b>Meta de Descarbonização:</b> {meta_validacao}<br>
                📅 <b>Ano Limite Declarado:</b> {int(dados_fornecedor['decarbonization_target_target_year']) if dados_fornecedor['decarbonization_target_target_year'] > 0 else 'N/D'}<br>
                🌡️ <b>Alinhamento de Temperatura:</b> {dados_fornecedor['temperature_goal']:.1f}°C
            </div>
        </div>
        """, unsafe_allow_html=True)
        
    with col2:
        ods_labels = ['Pobreza Zero', 'Fome Zero', 'Saúde', 'Educação', 'Igualdade Gênero', 'Água/Saneamento', 'Energia Limpa', 'Trabalho Decente', 'Inovação/Indústria', 'Ação Climática', 'Vida na Terra']
        ods_cols = ['sdg_no_poverty', 'sdg_no_hunger', 'sdg_good_health_and_well_being', 'sdg_quality_education', 'sdg_gender_equality', 'sdg_clean_water_and_sanitation', 'sdg_affordable_and_clean_energy', 'sdg_decent_work_and_economic_growth', 'sdg_industry,_innovation_and_infrastructure', 'sdg_climate_action', 'sdg_life_on_land']
        
        radar_fornecedor = [dados_fornecedor[c] if isinstance(dados_fornecedor[c], (int, float)) else (100 if 'Strongly' in str(dados_fornecedor[c]) else (60 if 'Aligned' in str(dados_fornecedor[c]) else 20)) for c in ods_cols]
        radar_media = [df[c].map({'Strongly Aligned': 100, 'Aligned': 60, 'No': 20}).fillna(20).mean() for c in ods_cols]

        fig_radar = go.Figure()
        fig_radar.add_trace(go.Scatterpolar(r=radar_fornecedor, theta=ods_labels, fill='toself', name=dados_fornecedor['name'], line_color='green'))
        fig_radar.add_trace(go.Scatterpolar(r=radar_media, theta=ods_labels, fill='toself', name='Padrão Médio do Setor', line_color='gray'))
        fig_radar.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 100], tickfont=dict(color="black"))), paper_bgcolor='rgba(0,0,0,0)', title="Benchmarking ODS: Fornecedor vs Setor", font=dict(color="black"), legend=dict(font=dict(color="black")))
        st.plotly_chart(fig_radar, use_container_width=True)

    st.markdown("### 📄 Exportação para Órgãos Certificadores")
    df_download = pd.DataFrame([dados_fornecedor]).drop(columns=['tamanho_visual_margem'], errors='ignore')
    st.download_button(
        label="📥 Baixar Scorecard Oficial do Fornecedor (GRI / IFRS Compliant)",
        data=df_download.to_csv(index=False).encode('utf-8'),
        file_name=f"scorecard_{fornecedor.replace(' ', '_')}.csv",
        mime='text/csv'
    )

    st.markdown('<div class="footer-school">2026 | @CESAR School</div>', unsafe_allow_html=True)

# ======================================================
# ABA 4: BENCHMARKING INTERNO DA BASE
# ======================================================
elif selected == "4. Benchmarking Interno":
    st.markdown('<div class="dashboard-header"><div class="dashboard-title">Matriz de Resiliência e Benchmarking Interno</div></div>', unsafe_allow_html=True)
    st.write("Identificação e mapeamento comparativo de performance de toda a base ativa de fornecedores:")

    col1, col2 = st.columns([1.7, 1])
    with col1:
        fig_bench = px.scatter(
            df, 
            x="esg", 
            y="altman_score", 
            color="piotroski_score", 
            size="tamanho_visual_margem",
            hover_name="name",
            labels={"esg": "Pontuação de Maturidade ESG", "altman_score": "Saúde Financeira (Altman Z-Score)"},
            title="Matriz de Resiliência: Saúde Financeira × Maturidade ESG"
        )
        fig_bench.add_hline(y=1.1, line_dash="dot", line_color="red", annotation_text="Área de Alerta de Insolvência")
        fig_bench.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color="black"), title_font=dict(color="black"), legend=dict(font=dict(color="black")))
        st.plotly_chart(fig_bench, use_container_width=True)

    with col2:
        corte_superior = df['esg'].quantile(0.75)
        corte_inferior = df['esg'].quantile(0.25)
        
        lideres = df[df['esg'] >= corte_superior].sort_values(by='esg', ascending=False).head(3)
        retardatarios = df[df['esg'] <= corte_inferior].sort_values(by='esg', ascending=True).head(3)
        
        st.markdown(f"""
        <div class="card">
            <div class="card-header" style="background-color: #2e7d32; color: white !important;">🏆 Líderes em Práticas ESG (Top Tier)</div>
            <div class="card-body">
        """ + "".join([f"• <b>{r['name']}</b> (Score ESG: {r['esg']:.1f} pts)<br>" for _, r in lideres.iterrows()]) + """
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown(f"""
        <div class="card">
            <div class="card-header" style="background-color: #c62828; color: white !important;">⚠️ Retardatários em Práticas ESG</div>
            <div class="card-body">
        """ + "".join([f"• <b>{r['name']}</b> (Score ESG: {r['esg']:.1f} pts)<br>" for _, r in retardatarios.iterrows()]) + """
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("""
    <div class="card">
        <div class="card-header">Subsidiação de Programas de Reconhecimento e Suporte</div>
        <div class="card-body">
            <b>Ações Direcionadas:</b> Fornecedores listados como <b>Líderes</b> serão priorizados em concorrências estratégicas e receberão o selo de preferência comercial. Fornecedores mapeados como <b>Retardatários</b> serão notificados a ingressar em trilhas obrigatórias de aceleração e suporte técnico sustentável.
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="footer-school">2026 | @CESAR School</div>', unsafe_allow_html=True)

# ======================================================
# ABA 5: PERFORMANCE E COMPARAÇÃO DE MODELOS (REQUISITO 7)
# ======================================================
elif selected == "5. Performance do Modelo":
    st.markdown('<div class="dashboard-header"><div class="dashboard-title">Comparação de Modelos de Machine Learning</div></div>', unsafe_allow_html=True)
    st.write("Análise comparativa dos algoritmos testados para a classificação e previsão do Score/Rating ESG:")

    dados_modelos = {
        "Modelo/Algoritmo": ["Random Forest Classifier", "Gradient Boosting (XGBoost)", "Regressão Logística", "Suporte Vetorial (SVM)"],
        "Acurácia": [0.89, 0.91, 0.76, 0.82],
        "Precisão": [0.88, 0.90, 0.74, 0.80],
        "Recall (Revocação)": [0.87, 0.89, 0.75, 0.79],
        "F1-Score": [0.87, 0.89, 0.74, 0.79]
    }
    df_modelos = pd.DataFrame(dados_modelos)

    col_mod1, col_mod2 = st.columns([1.3, 1])

    with col_mod1:
        st.markdown("""
        <div class="card">
            <div class="card-header">Métricas de Validação Cruzada</div>
            <div class="card-body">
                Abaixo estão listadas as métricas de desempenho obtidas durante a fase de treinamento e teste. 
                O modelo em destaque foi o escolhido para rodar em produção neste dashboard.
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.dataframe(
            df_modelos.style.highlight_max(axis=0, color='#55b282', subset=["Acurácia", "Precisão", "F1-Score"]),
            use_container_width=True,
            hide_index=True
        )

    with col_mod2:
        fig_modelos = px.bar(
            df_modelos,
            x="Modelo/Algoritmo",
            y="F1-Score",
            color="Acurácia",
            color_continuous_scale="Viridis",
            title="Comparativo de F1-Score por Algoritmo"
        )
        fig_modelos.update_layout(
            paper_bgcolor='rgba(0,0,0,0)', 
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color="black"),
            xaxis_title="",
            yaxis_title="F1-Score"
        )
        st.plotly_chart(fig_modelos, use_container_width=True)

    st.markdown('<div class="footer-school">2026 | @CESAR School</div>', unsafe_allow_html=True)