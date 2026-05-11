import streamlit as st
import streamlit_authenticator as stauth
import plotly.graph_objects as go
import pandas as pd

st.set_page_config(layout="wide")

# =========================
# LOGIN
# =========================

credentials = {
    "usernames": {
        "legalerbe": {
            "name": "legalerbe",
            "password": "Erbe@3009"
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
name = st.session_state.get("name")
username = st.session_state.get("username")

# =========================
# CONTROLE DE ACESSO
# =========================

if authentication_status == False:
    st.error("Usuário ou senha incorretos")

elif authentication_status == None:
    st.warning("Digite seu usuário e senha")

elif authentication_status:

    authenticator.logout("Sair", "sidebar")

    # =========================
    # ESTILO
    # =========================
    st.markdown("""
    <style>
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        padding-left: 3rem;
        padding-right: 3rem;
    }
    </style>
    """, unsafe_allow_html=True)

    # =========================
    # CORES
    # =========================
    COLORS = {
        "blue_dark": "#0B3C5D",
        "blue_light": "#BFD7EA",
        "blue_medium": "#328CC1",
        "gray": "#A9A9A9",
        "green": "#5CB85C",
        "red": "#D9534F",
        "magenta": "#C2185B"
    }

    labels_macro = ["FAR", "Cível", "Property Tax", "Labor", "Tax"]

    pagina = st.sidebar.radio("Navegação", [
        "Overview",
        "Claims por Ano",
        "New Claims",
        "Resolved"
    ])

    # =========================
    # FUNÇÃO DONUT
    # =========================
    def donut(values, title, total):
        fig = go.Figure(data=[go.Pie(
            labels=labels_macro,
            values=values,
            hole=0.7,
            marker_colors=[
                COLORS["blue_dark"],
                COLORS["blue_medium"],
                COLORS["magenta"],
                COLORS["gray"],
                COLORS["blue_light"]
            ],
            textinfo='percent',
            texttemplate='%{percent:.2%}'
        )])

        fig.update_layout(
            title=dict(text=title, x=0.5),
            annotations=[dict(text=f"<b>{total}</b>", x=0.5, y=0.5, showarrow=False)],
            legend=dict(orientation="h", y=-0.2, x=0.5, xanchor="center"),
            plot_bgcolor="white"
        )

        return fig

    # =========================
    # FUNÇÃO LABEL
    # =========================
    def add_labels(fig, x_vals, y_vals, color):

        texts = []

        for i in range(len(y_vals)):

            if y_vals[i] >= 11:
                texts.append(str(y_vals[i]))

            else:
                texts.append("")

                if y_vals[i] > 0:

                    fig.add_annotation(
                        x=x_vals[i],
                        y=y_vals[i],
                        text=str(y_vals[i]),
                        showarrow=False,
                        xshift=-25,
                        font=dict(color=color, size=11)
                    )

        return texts

    # =========================
    # PAGE 1 — OVERVIEW
    # =========================
    if pagina == "Overview":

        df = pd.read_excel("BASE_UNIFICADA.xlsx")
        df = df.drop_duplicates(subset="Pasta")
        df_assu = pd.read_excel("assumptions_26_slides.xlsx")
        values = [
            (df_assu.iloc[2,1]/1000000).round(2),
            (-df_assu.iloc[3,1]/1000000).round(2),
            (-df_assu.iloc[4,1]/1000000).round(2),
            (df_assu.iloc[5,1]/1000000).round(2),
            (df_assu.iloc[6,1]/1000000).round(2),
            (df_assu.iloc[7,1]/1000000).round(2),
            (df_assu.iloc[8,1]/1000000).round(2)
        ]
        st.title("Erbe Update")

        claims_macro = df.groupby("Macro Assunto").size()

        # TOTAL LOSS vindo da outra tabela
        total_loss = (df_assu.iloc[8,1] / 1000000).round(2)

        total_claims = len(df)

        # -----------------------------
        # proporção fixa por macro assunto
        # (exemplo - ajuste para o seu caso)
        # -----------------------------

        proporcao_macro = {
            "FAR": 0.09,
            "Cível": 0.77,
            "IPTU Customer": 0.01,
            "Tax": 0.11,
            "Labor": 0.02
        }

        # gera os valores proporcionais
        loss_macro_prop = pd.Series(proporcao_macro) * total_loss

        # garante ordem igual ao gráfico
        loss_macro_prop = loss_macro_prop.reindex(labels_macro, fill_value=0)

        col1, col2 = st.columns(2)

        with col1:

            st.plotly_chart(
                donut(
                    claims_macro.reindex(labels_macro, fill_value=0).values,
                    "Total Claims",
                    total_claims
                ),
                use_container_width=True
            )

        with col2:

            st.plotly_chart(
            donut(
            loss_macro_prop.values,
            "Expected Loss",
            total_loss
        ),
        use_container_width=True
    )

        st.markdown("<br>", unsafe_allow_html=True)

        df_assu = pd.read_excel("assumptions_26_slides.xlsx")

        values = [
            (df_assu.iloc[2,1]/1000000).round(2),
            (-df_assu.iloc[3,1]/1000000).round(2),
            (-df_assu.iloc[4,1]/1000000).round(2),
            (df_assu.iloc[5,1]/1000000).round(2),
            (df_assu.iloc[6,1]/1000000).round(2),
            (df_assu.iloc[7,1]/1000000).round(2),
            (df_assu.iloc[8,1]/1000000).round(2)
        ]

        fig = go.Figure()

        fig.add_trace(go.Bar(
            x=["Dez25","Resolved","Savings","Revised","Subtotal","New","Total"],
            y=values,
            marker_color=[
                COLORS["gray"], COLORS["red"], COLORS["green"],
                COLORS["blue_medium"], COLORS["gray"],
                COLORS["magenta"], COLORS["blue_dark"]
            ],
            text=values,
            textposition="outside"
        ))

        fig.update_layout(plot_bgcolor="white", height=350)

        st.plotly_chart(fig, use_container_width=True)

        col3, col4 = st.columns([2,1])

        with col3:
            valor1 = ((df_assu.iloc[2,1]/1000000).round(2))
            valor3 = ((df["Valor Pedido Objeto Corrigido"].sum()/1000000).round(2))
            vals = [valor1, (valor3 - valor1).round(2), valor3]

            fig2 = go.Figure()

            fig2.add_trace(go.Bar(
                x=["Total","Carrying","Updated"],
                y=vals,
                marker_color=[COLORS["gray"], COLORS["blue_medium"], COLORS["green"]],
                text=vals,
                textposition="outside"
            ))

            fig2.update_layout(plot_bgcolor="white", height=300)

            st.plotly_chart(fig2, use_container_width=True)

        with col4:

            st.table(pd.DataFrame({
                "Subject":["Civil","Tax","Labor","Construction"],
                "Rate":["TJ+1%","Selic","TST+1%","INCC"],
                "12M":["16.8%","14.5%","16.8%","5.8%"]
            }))

    # =========================
    # PAGE 2 — CLAIMS
    # =========================
    elif pagina == "Claims por Ano":

        st.title("New Claims Filled per Year")

        df = pd.read_excel("RELATORIO_FILTRADO.xlsx")

        df = df.drop_duplicates(subset="Pasta")

        df["Data de cadastro"] = pd.to_datetime(df["Data de cadastro"], dayfirst=True, errors="coerce")
        df["Data de Encerramento"] = pd.to_datetime(df["Data de Encerramento"], dayfirst=True, errors="coerce")

        ativos_2026 = df[
            (df["Data de cadastro"].dt.year == 2026) &
            (df["Status"] == "ATIVOS")
        ].shape[0]

        encerrados_2026 = df[
            (df["Data de cadastro"].dt.year == 2026) &
            (df["Data de Encerramento"].dt.year == 2026)
        ].shape[0]

        anos = ["2012","2013","2014","2015","2016","2017","2018","2019","2020","2021","2022","2023","2024","2025","2026"]

        ativos = [80,34,92,159,261,200,630,261,641,1739,523,339,305,452,ativos_2026]

        encerrados = [7952,5966,7590,7987,7314,4810,2782,1873,1078,2475,638,483,236,74,encerrados_2026]

        df_bp = pd.read_excel("POS_BP.xlsx")

        df_bp["Data de cadastro"] = pd.to_datetime(df_bp["Data de cadastro"], dayfirst=True, errors="coerce")

        

        total_risk_2026 = df_bp["Valor Pedido Atualizado"].sum()
        expected_loss_2026 = df_bp["Valor Pedido.1"].sum()
        total_risk_2026 = (total_risk_2026/1000000).round(2)
        expected_loss_2026 = (expected_loss_2026/1000000).round(2)

        st.table(pd.DataFrame({
            "Métrica":["Total Risk","Expected Loss"],
            "≤2012":[144.2,33.3],"2013":[47.7,7],"2014":[24.2,16.6],"2015":[87.4,31.9],
            "2016":[199.2,69.6],"2017":[194.4,65.9],"2018":[190.9,94.6],"2019":[87.8,40.8],
            "2020":[226,93.2],"2021":[191.6,59.7],"2022":[211.3,20.8],"2023":[136.3,50.6],
            "2024":[46.6,18.3],"2025":[55.3,28.7],
            "2026":[total_risk_2026,expected_loss_2026]
        }))

        fig = go.Figure()

        text_resolved = add_labels(fig, anos, encerrados, COLORS["blue_light"])
        text_active = add_labels(fig, anos, ativos, COLORS["blue_dark"])

        fig.add_trace(go.Bar(
            x=anos, y=encerrados,
            name="Resolved",
            marker_color=COLORS["blue_light"],
            text=text_resolved,
            textposition="inside"
        ))

        fig.add_trace(go.Bar(
            x=anos, y=ativos,
            name="Active",
            marker_color=COLORS["blue_dark"],
            text=text_active,
            textposition="inside"
        ))

        totals = [a+b for a,b in zip(ativos,encerrados)]

        for i in range(len(anos)):

            fig.add_annotation(
                x=anos[i],
                y=totals[i]*1.05,
                text=str(totals[i]),
                showarrow=False
            )

        fig.update_layout(barmode="stack", plot_bgcolor="white", height=450)

        st.plotly_chart(fig, use_container_width=True)

    # =========================
    # PAGE 3 — NEW CLAIMS
    # =========================
    elif pagina == "New Claims":
        df_bp = pd.read_excel("POS_BP.xlsx")
        df_bp["Data de cadastro"] = pd.to_datetime(df_bp["Data de cadastro"], dayfirst=True, errors="coerce")
        
        st.title("New Claims")
        acumulado_new_claims = df_bp["Valor Pedido.1"].sum()
        acumulado_new_claims = (acumulado_new_claims/1000000).round(2)
        values = [54.4,9.2,acumulado_new_claims]  # ALTERE AQUI O VALOR DO MEIO

        fig = go.Figure()

        fig.add_trace(go.Bar(
            x=["Budget","Forecast","Actual"],
            y=values,
            marker_color=[COLORS["magenta"], COLORS["blue_medium"], COLORS["blue_light"]],
            text=values,
            textposition="outside"
        ))

        perc = (values[2]/values[1] - 1)*100

        # índices das barras
        # índices das barras
        x0 = 1  # Forecast
        x1 = 2  # Actual

        y0 = values[1]
        y1 = values[2]

        # linha inclinada
        fig.add_shape(
            type="line",
            x0=x0,
            y0=y0,
            x1=x1,
            y1=y1,
            line=dict(color="black", width=2, dash="dot")
        )

        

        # texto
        fig.add_annotation(
            x=(x0 + x1)/2,
            y=(y0 + y1)/2,
            text=f"{perc:.2f}%",
            showarrow=False,
            yshift=10
        )

        st.plotly_chart(fig, use_container_width=True)

        # ===== TRATAMENTO NOVO =====
        # trata NaN e vazios corretamente
        df_bp["Macro Assunto"] = df_bp["Macro Assunto"].where(
            df_bp["Macro Assunto"].notna(), "Demais"
            )

        df_bp["Macro Assunto"] = df_bp["Macro Assunto"].astype(str).str.strip()

        df_bp["Macro Assunto"] = df_bp["Macro Assunto"].replace(
            ["", "nan", "None"], "Demais")

        # inclui "Demais"
        tipos = ["Cível","Property Tax","Labor","Delay","FAR","Construction","Tax","Demais","Total"]

        total_risk = df_bp.groupby("Macro Assunto")["Valor Pedido Atualizado"].sum()
        expected_loss = df_bp.groupby("Macro Assunto")["Valor Pedido.1"].sum()
        quantidade = df_bp.groupby("Macro Assunto").size()

        total_risk = (total_risk/1000000).round(2)
        expected_loss = (expected_loss/1000000).round(2)

        total_risk_vals = total_risk.reindex(tipos[:-1], fill_value=0).tolist()
        expected_loss_vals = expected_loss.reindex(tipos[:-1], fill_value=0).tolist()
        quantidade_vals = quantidade.reindex(tipos[:-1], fill_value=0).tolist()

        total_risk_vals.append(sum(total_risk_vals))
        expected_loss_vals.append(sum(expected_loss_vals))
        quantidade_vals.append(sum(quantidade_vals))

        st.table(pd.DataFrame({
            "Tipo": tipos,
            "Total Risk": total_risk_vals,
            "Expected Loss": expected_loss_vals
        }))

        fig2 = go.Figure()

        fig2.add_trace(go.Bar(
            x=tipos,
            y=quantidade_vals,
            marker_color=COLORS["blue_dark"],
            text=quantidade_vals,
            textposition="outside"
        ))

        st.plotly_chart(fig2, use_container_width=True)

    # =========================
    # PAGE 4 — RESOLVED
    # =========================
    # =========================
    elif pagina == "Resolved":

        st.title("Finally Resolved Claims")

        tipos = ["Cível","Property Tax","Labor","Delay","FAR","Construction","Tax"]
        tipos_total = tipos + ["Total"]

        # =========================
        # CARREGAR BASE
        # =========================
        df_set = pd.read_excel("SETTLED_ACUMULADO.xlsx")

        # =========================
        # REMOVER DUPLICADOS
        # =========================
        df_set = (
            df_set
            .sort_values("Soma_Valor_Lancamento", ascending=False)
            .drop_duplicates(subset="Pasta")
        )

        # =========================
        # TABELA
        # =========================
        total_risk = df_set.groupby("Macro Assunto")["Valor Pedido Atualizado"].sum()
        expected_loss = df_set.groupby("Macro Assunto")["Valor Pedido Objeto Corrigido"].sum()
        disbursement = df_set.groupby("Macro Assunto")["Soma_Valor_Lancamento"].sum()
        total_risk = (total_risk/1000000).round(2)
        expected_loss = (expected_loss/1000000).round(2)
        disbursement = (disbursement/1000000).round(2)
        tabela = pd.DataFrame({
            "Métrica": ["Total Risk","Expected Loss","Disbursement"]
        })

        for tipo in tipos:
            tabela[tipo] = [
                total_risk.get(tipo,0),
                expected_loss.get(tipo,0),
                disbursement.get(tipo,0)
            ]

        # adicionar TOTAL na tabela
        tabela["Total"] = tabela[tipos].sum(axis=1)

        st.table(tabela)

        # =========================
        # GRÁFICO
        # =========================

        contagem = (
            df_set
            .groupby(["Macro Assunto","Macro encerramento"])
            .size()
            .unstack(fill_value=0)
        )

        settlement = contagem.get("Settled", pd.Series(0,index=tipos)).reindex(tipos, fill_value=0)
        lost = contagem.get("Lost", pd.Series(0,index=tipos)).reindex(tipos, fill_value=0)
        won = contagem.get("Won", pd.Series(0,index=tipos)).reindex(tipos, fill_value=0)

        # adicionar TOTAL ao gráfico
        settlement = settlement.tolist() + [settlement.sum()]
        lost = lost.tolist() + [lost.sum()]
        won = won.tolist() + [won.sum()]

        fig = go.Figure()

        fig.add_trace(go.Bar(
            x=tipos_total,
            y=settlement,
            name="Settlement",
            marker_color=COLORS["red"]
        ))

        fig.add_trace(go.Bar(
            x=tipos_total,
            y=lost,
            name="Lost",
            marker_color=COLORS["blue_dark"]
        ))

        fig.add_trace(go.Bar(
            x=tipos_total,
            y=won,
            name="Won",
            marker_color=COLORS["blue_light"]
        ))

        totals = [s+l+w for s,l,w in zip(settlement,lost,won)]

        for i in range(len(tipos_total)):

            fig.add_annotation(
                x=tipos_total[i],
                y=totals[i]*1.08,
                text=str(int(totals[i])),
                showarrow=False
            )

        fig.update_layout(
            barmode="stack",
            plot_bgcolor="white",
            height=450
        )

        st.plotly_chart(fig, use_container_width=True)