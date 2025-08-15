from datetime import date, timedelta
import pandas as pd
import plotly.express as px
import streamlit as st
from db import run_query

# ========= Helpers / labels =========
def fmt_brl(v: float) -> str:
    return f"R$ {v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

def fmt_int(n: int) -> str:
    return f"{int(n):,}".replace(",", ".")

# Mapeamento PT-BR para eixos/legendas dos gráficos
LABELS_PT = {
    "OrderDate": "Data do pedido",
    "YearMonth": "Ano-Mês",
    "Category": "Categoria",
    "Region": "Região",
    "ProductName": "Produto",
    "ProductID": "ID do produto",
    "SalesOrderID": "ID do pedido",
    "Quantity": "Quantidade",
    "LineAmount": "Valor",
    "TotalDue": "Total faturado",
    "Orders": "Pedidos",
}

# Mapeamento para renomear as colunas na TABELA (exibição)
PT_COLS = {
    "Category": "Categoria",
    "LineAmount": "Valor",
    "OrderDate": "Data do pedido",
    "ProductID": "ID do produto",
    "ProductName": "Produto",
    "Quantity": "Quantidade",
    "Region": "Região",
    "SalesOrderID": "ID do pedido",
    "TotalDue": "Total faturado",
    "YearMonth": "Ano-Mês",
}

# ========= Config geral =========
st.set_page_config(
    page_title="Painel de Vendas",
    layout="wide",
    initial_sidebar_state="collapsed",  # inicia com a barra lateral colapsada
)
BOX_HEIGHT = 420  # altura padrão em caixas

if "show_sidebar" not in st.session_state:
    st.session_state.show_sidebar = False  # sidebar fechada

def _toggle_sidebar():
    st.session_state.show_sidebar = not st.session_state.show_sidebar

# Botão para abrir/fechar filtros
top_left, _, _ = st.columns([1, 6, 1])
with top_left:
    st.button("☰ Filtros", on_click=_toggle_sidebar, use_container_width=True)

# CSS para controlar a sidebar via estado
st.markdown(
    f"""
    <style>
      [data-testid="stSidebar"] {{
        display: {'block' if st.session_state.show_sidebar else 'none'};
      }}
      [data-testid="collapsedControl"] {{ display: none; }}
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("📊 Painel de Vendas – AdventureWorks")

# ========= Intervalo de datas disponível no BD =========
@st.cache_data(ttl=600)
def get_available_date_range():
    sql = """
        SELECT
          CAST(MIN(h.OrderDate) AS date) AS MinDate,
          CAST(MAX(h.OrderDate) AS date) AS MaxDate
        FROM Sales.SalesOrderHeader h;
    """
    rows = run_query(sql, {})
    if not rows:
        # fallback seguro
        return date(2011, 1, 1), date(2014, 12, 31)
    mind = pd.to_datetime(rows[0]["MinDate"]).date()
    maxd = pd.to_datetime(rows[0]["MaxDate"]).date()
    return mind, maxd

# ========= Filtros (opções do BD) =========
@st.cache_data(ttl=600)
def get_filter_options():
    q_cat = """
    SELECT DISTINCT pc.Name AS Category
    FROM Sales.SalesOrderDetail d
    JOIN Production.Product p ON p.ProductID = d.ProductID
    LEFT JOIN Production.ProductSubcategory psc ON psc.ProductSubcategoryID = p.ProductSubcategoryID
    LEFT JOIN Production.ProductCategory pc ON pc.ProductCategoryID = psc.ProductCategoryID
    WHERE pc.Name IS NOT NULL;
    """
    q_reg = """
    SELECT DISTINCT sp.Name AS Region
    FROM Sales.SalesOrderHeader h
    LEFT JOIN Person.Address a ON a.AddressID = h.ShipToAddressID
    LEFT JOIN Person.StateProvince sp ON sp.StateProvinceID = a.StateProvinceID
    WHERE sp.Name IS NOT NULL;
    """
    cats = [r["Category"] for r in run_query(q_cat, {})]
    regs = [r["Region"] for r in run_query(q_reg, {})]
    return sorted(cats), sorted(regs)

# ========= Sidebar =========
with st.sidebar:
    st.header("Filtros")

    # Limites de data vindos do banco
    min_date, max_date = get_available_date_range()

    start_date = st.date_input(
        "Data inicial",
        value=min_date,
        min_value=min_date,
        max_value=max_date,
    )
    end_date_inclusive = st.date_input(
        "Data final (incl.)",
        value=max_date,
        min_value=min_date,
        max_value=max_date,
    )

    st.subheader("Dimensões")
    categories_opts, regions_opts = get_filter_options()
    sel_categories = st.multiselect("Categorias", options=categories_opts, placeholder="Selecione categorias")
    sel_regions   = st.multiselect("Regiões (ShipTo)", options=regions_opts, placeholder="Selecione regiões")

# Para queries.sql (se necessário)
categories_csv = ",".join(sel_categories)
regions_csv    = ",".join(sel_regions)

# Intervalo half-open [start, end)
end_exclusive_date = end_date_inclusive + timedelta(days=1)
start_str         = start_date.isoformat()
end_exclusive_str = end_exclusive_date.isoformat()

# ========= Carga principal (SQL + Pandas) =========
MIN_AMOUNT = 0.0

@st.cache_data(ttl=300)
def load_sales(_start_str: str, _end_exclusive_str: str,
               _min_amount: float, _categories_csv: str, _regions_csv: str):
    with open("queries.sql", "r", encoding="utf-8") as f:
        sql = f.read()
    rows = run_query(sql, {
        "start_date": _start_str,
        "end_date": _end_exclusive_str,
        "min_amount": float(_min_amount),
        "categories_csv": _categories_csv.strip(),
        "regions_csv": _regions_csv.strip(),
    })
    df = pd.DataFrame(rows)
    if df.empty:
        return df
    df["OrderDate"] = pd.to_datetime(df["OrderDate"])
    df["YearMonth"] = df["OrderDate"].dt.to_period("M").dt.to_timestamp()
    return df

with st.spinner("Carregando dados..."):
    df = load_sales(start_str, end_exclusive_str, MIN_AMOUNT, categories_csv, regions_csv)

# ========= Aplica filtros =========
if df is None or df.empty:
    st.info("Nenhum dado para os filtros selecionados. Ajuste o período (2011–2014) ou as dimensões.")
    st.stop()

start_ts = pd.to_datetime(start_str)
end_ts   = pd.to_datetime(end_exclusive_str)
df = df[(df["OrderDate"] >= start_ts) & (df["OrderDate"] < end_ts)]
if sel_categories:
    df = df[df["Category"].isin(sel_categories)]
if sel_regions:
    df = df[df["Region"].isin(sel_regions)]

if df.empty:
    st.info("Nenhum dado para os filtros selecionados. Ajuste o período e as dimensões.")
    st.stop()

# ========= KPIs (em caixas) =========
orders_count = int(df["SalesOrderID"].nunique())
if "Quantity" in df.columns:
    units_total = int(df["Quantity"].sum())
elif "Units" in df.columns:
    units_total = int(df["Units"].sum())
elif "OrderQty" in df.columns:
    units_total = int(df["OrderQty"].sum())
else:
    units_total = 0
total_line_amount = float(df["LineAmount"].sum())

c1, c2, c3 = st.columns(3)
with c1:
    with st.container(border=True):
        st.metric("🛒 Pedidos (qtde)", fmt_int(orders_count))
with c2:
    with st.container(border=True):
        st.metric("📦 Unidades vendidas", fmt_int(units_total))
with c3:
    with st.container(border=True):
        st.metric("💰 Receita (itens)", fmt_brl(total_line_amount))

st.divider()

# =========================
# CAIXA 1 — Visão geral (ABERTA)
# =========================
with st.expander("Visão geral (receita por dia e por produto)", expanded=True):
    cA, cB = st.columns(2, gap="medium")

    # Esquerda: receita por dia
    with cA:
        ts = df.groupby("OrderDate", as_index=False)["LineAmount"].sum()
        fig_ts = px.line(
            ts, x="OrderDate", y="LineAmount",
            title="Receita por dia", labels=LABELS_PT
        )
        fig_ts.update_yaxes(tickprefix="R$ ", separatethousands=True)
        fig_ts.update_xaxes(dtick="M2", tickformat="%b %Y")
        fig_ts.update_layout(height=BOX_HEIGHT, margin=dict(l=40, r=10, t=48, b=40))
        with st.container(border=True):
            st.plotly_chart(fig_ts, use_container_width=True)

    # Direita: receita por produto (horizontal com scroll)
    with cB:
        prod_rev = (
            df.groupby("ProductName", as_index=False)["LineAmount"]
              .sum().sort_values("LineAmount", ascending=False)
        )
        def _short(s, n=40): return s if len(s) <= n else s[: n-1] + "…"
        prod_rev["ProductName"] = prod_rev["ProductName"].apply(_short)

        fig_prod = px.bar(
            prod_rev, y="ProductName", x="LineAmount",
            orientation="h", title="Receita por produto", labels=LABELS_PT
        )
        fig_prod.update_xaxes(tickprefix="R$ ", separatethousands=True)
        fig_prod.update_layout(
            yaxis={"categoryorder": "total ascending"},
            height=max(800, 24 * len(prod_rev)),
            margin=dict(l=220, r=8, t=48, b=32),
        )
        with st.container(border=True):
            try:
                with st.container(height=BOX_HEIGHT, border=False):
                    st.plotly_chart(fig_prod, use_container_width=True)
            except TypeError:
                st.markdown(
                    f"<div style='height:{BOX_HEIGHT}px; overflow-y:auto; padding-right:8px;'>",
                    unsafe_allow_html=True,
                )
                st.plotly_chart(fig_prod, use_container_width=True)
                st.markdown("</div>", unsafe_allow_html=True)

# =========================
# CAIXA 2 — Número de vendas (FECHADA)
# =========================
with st.expander("Número de vendas (pedidos)", expanded=False):
    c1, c2 = st.columns(2, gap="medium")

    with c1:
        orders_ts = (
            df.groupby("OrderDate")["SalesOrderID"].nunique()
              .reset_index(name="Orders")
        )
        fig_ts_orders = px.line(
            orders_ts, x="OrderDate", y="Orders",
            title="Nº de vendas por dia", labels=LABELS_PT
        )
        fig_ts_orders.update_yaxes(tickformat=",d")
        fig_ts_orders.update_xaxes(dtick="M2", tickformat="%b %Y")
        fig_ts_orders.update_layout(height=BOX_HEIGHT)
        with st.container(border=True):
            st.plotly_chart(fig_ts_orders, use_container_width=True)

    with c2:
        cat_orders = (
            df.groupby("Category")["SalesOrderID"].nunique()
              .reset_index(name="Orders").sort_values("Orders", ascending=False)
        )
        fig_cat_orders = px.bar(
            cat_orders, x="Category", y="Orders",
            title="Vendas por categoria (nº de pedidos)", labels=LABELS_PT
        )
        fig_cat_orders.update_yaxes(tickformat=",d")
        fig_cat_orders.update_layout(height=BOX_HEIGHT)
        with st.container(border=True):
            st.plotly_chart(fig_cat_orders, use_container_width=True)

# =========================
# CAIXA 3 — Análises adicionais (FECHADA)
# =========================
with st.expander("Análises adicionais (regiões, mês e detalhe)", expanded=False):
    c3, c4 = st.columns(2, gap="medium")
    with c3:
        reg = (
            df.groupby("Region", as_index=False)["LineAmount"]
              .sum().sort_values("LineAmount", ascending=False)
        )
        fig_reg = px.bar(
            reg, y="Region", x="LineAmount", orientation="h",
            title="Receita por região (ShipTo)", labels=LABELS_PT
        )
        fig_reg.update_xaxes(tickprefix="R$ ", separatethousands=True)
        fig_reg.update_layout(yaxis={'categoryorder': 'total ascending'}, height=BOX_HEIGHT)
        with st.container(border=True):
            st.plotly_chart(fig_reg, use_container_width=True)

    with c4:
        month = df.groupby("YearMonth", as_index=False)["LineAmount"].sum()
        fig_month = px.area(
            month, x="YearMonth", y="LineAmount",
            title="Receita por mês", labels=LABELS_PT
        )
        fig_month.update_yaxes(tickprefix="R$ ", separatethousands=True)
        fig_month.update_xaxes(dtick="M2", tickformat="%b %Y")
        fig_month.update_layout(height=BOX_HEIGHT)
        with st.container(border=True):
            st.plotly_chart(fig_month, use_container_width=True)

    st.subheader("Detalhe (linhas filtradas)")
    # tabela com colunas traduzidas
    df_display = df.rename(columns=PT_COLS)
    st.dataframe(
        df_display.sort_values(["Data do pedido", "Valor"], ascending=[True, False]),
        use_container_width=True,
        height=380,
    )
