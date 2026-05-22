import streamlit as st
import pandas as pd
import plotly.express as px

st.title("Pagamentos")

df = pd.read_excel("Pagamentos_atualizado.xlsx")

# converter decimal brasileiro corretamente
df["Valor Restante"] = pd.to_numeric(
    df["Valor Restante"].astype(str).str.replace(",", "."),
    errors="coerce"
)

# KPI
valor_restante_total = df["Valor Restante"].sum()

st.metric(
    label="Valor Restante Total",
    value=f"R$ {valor_restante_total:,.2f}"
)

# Pizza
status_counts = df["Pagamento"].value_counts()

fig = px.pie(
    values=status_counts.values,
    names=status_counts.index,
    title="Proporção de Pagamentos"
)

st.plotly_chart(fig, use_container_width=True)