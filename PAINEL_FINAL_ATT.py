import streamlit as st
import pandas as pd
import plotly.express as px
import os
import streamlit_authenticator as stauth

# ===============================
# CONFIG
# ===============================
st.set_page_config(page_title="Report Mensal Erbe - Jurídico", layout="wide")

# =========================
# LOGIN
# =========================
credentials = {
    "usernames": {
        "legalerbe": {
            "name": "legalerbe",
            "password": "Erbe@17007"
        }
    }
}

authenticator = stauth.Authenticate(
    credentials,
    "meu_app",
    "abc123",
    cookie_expiry_days=1
)

authenticator.login()
authentication_status = st.session_state.get("authentication_status")

# =========================
# CONTROLE DE ACESSO
# =========================
if authentication_status == False:
    st.error("Usuário ou senha incorretos")

elif authentication_status == None:
    st.warning("Digite seu usuário e senha")

elif authentication_status:

    authenticator.logout("Sair", "sidebar")
    st.title("Dashboard de Processos")

    # ===============================
    # LOADS
    # ===============================
    @st.cache_data
    def load_base():
        df = pd.read_excel("BASE_UNIFICADA.xlsx")
        df.columns = df.columns.str.strip()
        return df

    @st.cache_data
    def load_relatorio():
        df = pd.read_excel("RELATORIO_FILTRADO.xlsx")
        df.columns = df.columns.str.strip()
        return df

    @st.cache_data
    def load_entradas():
        df = pd.read_excel("ENTRADAS.xlsx")
        df.columns = df.columns.str.strip().str.lower()
        return df

    @st.cache_data
    def load_settled():
        df = pd.read_excel("SETTLED_MENSAL.xlsx")
        df.columns = df.columns.str.strip().str.lower()
        return df

    df_base = load_base()
    df = load_relatorio()
    df_entradas = load_entradas()
    df_settled = load_settled()

    # ===============================
    # TRATAMENTO
    # ===============================
    df_base = df_base.drop_duplicates(subset="Pasta")

    df_entradas["data de cadastro"] = pd.to_datetime(
        df_entradas["data de cadastro"], errors="coerce"
    )

    for c in ["Data de cadastro", "Data de Encerramento"]:
        if c in df.columns:
            df[c] = pd.to_datetime(df[c], errors="coerce")

    # ===============================
    # SELEÇÃO DO MÊS DE FECHAMENTO (MANUAL)
    # ===============================
    st.sidebar.header("Configurações de Fechamento")
    
    lista_meses = [
        "Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
        "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"
    ]
    
    mes_nome = st.sidebar.selectbox("Selecione o mês de referência", lista_meses, index=2) # Index 2 = Março
    ano_ref = st.sidebar.number_input("Ano", min_value=2020, max_value=2030, value=2026)

    # Converter o nome do mês em número (Janeiro = 1, etc)
    mes_numero = lista_meses.index(mes_nome) + 1

    # Definir a data de "fim" (25 do mês selecionado)
    fim = pd.Timestamp(year=ano_ref, month=mes_numero, day=25)

    # Definir a data de "início" (26 do mês anterior)
    mes_anterior_dt = fim - pd.DateOffset(months=1)
    ini = pd.Timestamp(year=mes_anterior_dt.year, month=mes_anterior_dt.month, day=26)

    # Nome que será usado nos títulos (Ex: Março/26)
    mes_fechamento_nome = f"{mes_nome}/{str(ano_ref)[2:]}"

    st.sidebar.success(f"Período ativo: {ini.date()} a {fim.date()}")

    # ===============================
    # 1. IDENTIFICAÇÃO DINÂMICA DE COLUNAS (PARA EVITAR KEYERROR)
    # ===============================

    # Localiza a coluna de "Baixado Antes" independente de maiúsculas/minúsculas ou espaços
    col_baixado = [c for c in df_settled.columns if c.strip().upper() == "FOI BAIXADO ANTES"]
    col_status = [c for c in df_settled.columns if c.strip().upper() == "STATUS"]

    if not col_baixado or not col_status:
        st.error(f"Colunas não encontradas! Colunas disponíveis: {list(df_settled.columns)}")
        st.stop()

    nome_col_baixado = col_baixado[0]
    nome_col_status = col_status[0]

    # ===============================
    # 2. KPIs E CÁLCULOS
    # ===============================
    ativos = len(df_base)

    entradas_mes = len(df_entradas[
        (df_entradas["data de cadastro"] >= ini) & 
        (df_entradas["data de cadastro"] <= fim)
    ])

    # Criamos cópias temporárias normalizadas para os filtros
    status_series = df_settled[nome_col_status].astype(str).str.upper().str.strip()
    baixado_series = df_settled[nome_col_baixado].astype(str).str.upper().str.strip()

    # Filtramos quem encerrou no período
    mask_encerrados = (status_series == "ENCERRADOS")
    encerrados_mes = len(df_settled[mask_encerrados])

    # Interseção: Status ENCERRADOS e baixado_norm == SIM
    intersecao = len(df_settled[mask_encerrados & (baixado_series == "SIM")])

    # Quem encerrou sem nunca ter passado por baixa
    encerrados_diretos = encerrados_mes - intersecao

    # Baixas que ainda estão pendentes
    baixa_mes = len(df_settled[status_series == "BAIXA PROVISÓRIA"])

    # Cálculo do estoque inicial
    saidas_estoque_ativos = baixa_mes + encerrados_diretos
    ativos_mes_anterior = ativos - entradas_mes + saidas_estoque_ativos

    # ===============================
    # CÁLCULOS (Mantenha estes)
    # ===============================
    # ... (Seu código de ativos, entradas_mes, baixa_mes, encerrados_mes e intersecao)

    # Função de formatação segura
    def fmt_saida(valor):
        try:
            v = int(valor)
            return f"({v})" if v > 0 else ""
        except:
            return ""

    # ===============================
    # MONTAGEM DA TABELA (RECONCILIAÇÃO FINAL)
    # ===============================

    # Criamos os dados linha por linha para garantir a ordem exata da sua ilustração
    # No bloco de MONTAGEM DA TABELA:
    dados = [
        ["Ativos", int(ativos_mes_anterior), int(entradas_mes), fmt_saida(baixa_mes), fmt_saida(encerrados_mes), int(ativos)],
        ["Baixa Provisória", "", "", int(baixa_mes), fmt_saida(intersecao), int(baixa_mes - intersecao)],
        ["Encerrados", "", "", int(intersecao), int(encerrados_mes), int(intersecao + encerrados_mes)] # Exemplo dinâmico
    ]

    tabela = pd.DataFrame(dados, columns=["", "Mês anterior", "Novos", "Baixa provisória", "Encerrados", "Mês atual"])

    # Remove qualquer '0' que tenha sobrado para limpar o visual
    tabela = tabela.replace(0, "").replace("0", "")

    st.subheader(f"Movimentação - {fim.strftime('%b/%y')}")
    st.dataframe(tabela, use_container_width=True)

    # ===============================
    # GRÁFICO 1
    # ===============================
    st.subheader("Entradas por Macro Assunto")

    graf1 = (
        df_entradas
        .groupby("macro assunto")
        .size()
        .reset_index(name="quantidade")
        .sort_values(by="quantidade", ascending=False)
    )

    st.plotly_chart(
        px.bar(graf1, x="macro assunto", y="quantidade"),
        use_container_width=True
    )

    # ===============================
    # GRÁFICO 2
    # ===============================
    st.subheader("Encerrados vs Baixa Provisória")

    graf2 = (
        df_settled
        .groupby(["status", "macro encerramento"])
        .size()
        .reset_index(name="quantidade")
    )

    st.plotly_chart(
        px.bar(
            graf2,
            x="status",
            y="quantidade",
            color="macro encerramento",
            barmode="stack"
        ),
        use_container_width=True
    )

    # ===============================

    # GRÁFICO 3

    # ===============================

    st.subheader("Entradas vs Encerrados (2026)")



    # REMOVE DUPLICIDADE (CRÍTICO)

    df_grafico = df.sort_values("Data Cálculo", ascending=False)

    df_grafico = df_grafico.drop_duplicates(subset="Pasta", keep="first")



    # Entradas

    entradas_2026 = (

        df_grafico[df_grafico["Data de cadastro"].dt.year == 2026]

        .dropna(subset=["Data de cadastro"])

        .groupby(pd.Grouper(key="Data de cadastro", freq="MS"))

        .size()

        .reset_index(name="Entradas")

        .rename(columns={"Data de cadastro": "Data"})

    )



    # Encerrados

    encerrados_2026 = (

        df_grafico[df_grafico["Data de Encerramento"].dt.year == 2026]

        .dropna(subset=["Data de Encerramento"])

        .groupby(pd.Grouper(key="Data de Encerramento", freq="MS"))

        .size()

        .reset_index(name="Encerrados")

        .rename(columns={"Data de Encerramento": "Data"})

    )



    # Merge

    graf3 = pd.merge(entradas_2026, encerrados_2026, on="Data", how="outer")



    graf3["Entradas"] = graf3["Entradas"].fillna(0)

    graf3["Encerrados"] = graf3["Encerrados"].fillna(0)



    # Meses completos

    meses_2026 = pd.date_range("2026-01-01", "2026-12-31", freq="MS")



    graf3 = (

        graf3

        .set_index("Data")

        .reindex(meses_2026, fill_value=0)

        .reset_index()

        .rename(columns={"index": "Data"})

    )



    st.plotly_chart(

        px.line(graf3, x="Data", y=["Entradas", "Encerrados"], markers=True),

        use_container_width=True

    )
    # ===============================
    # ASSUMPTIONS
    # ===============================
    st.divider()
    st.subheader("Assumptions")

    if os.path.exists("assumptions_26_slides.xlsx"):

        assumptions = pd.read_excel("assumptions_26_slides.xlsx")
        assumptions.columns = assumptions.columns.astype(str).str.strip().str.lower()

        for col in ["calculo", "fixo", "soma"]:
            if col in assumptions.columns:
                assumptions[col] = pd.to_numeric(assumptions[col], errors="coerce")
                assumptions[col] = assumptions[col].apply(
                    lambda v: f"R$ {v/1000000:.2f}M" if pd.notnull(v) else ""
                )

        st.dataframe(assumptions, use_container_width=True)

    else:
        st.info("Arquivo assumptions_26_slides.xlsx não encontrado.")