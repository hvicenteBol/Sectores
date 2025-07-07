import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import matplotlib.pyplot as plt

# --- Configuración de página y estilo ---
st.set_page_config(page_title="Visualizador por Sectores", layout="wide")

st.markdown("""
<style>
.main-header {
    font-size: 3rem;
    font-weight: 700;
    text-align: center;
    background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 0.5rem;
}
.stButton > button {
    background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
    color: white;
    border: none;
    border-radius: 10px;
    padding: 0.5rem 1rem;
    font-weight: 600;
}
</style>
""", unsafe_allow_html=True)

st.markdown('<h1 class="main-header">Visualizador por sectores</h1>', unsafe_allow_html=True)

# --- Diccionario de ETFs por sector ---
SECTORAL_ETFS = {
    'Energy': 'XLE',
    'Materials': 'XLB',
    'Industrials': 'XLI',
    'Consumer Discretionary': 'XLY',
    'Consumer Staples': 'XLP',
    'Healthcare': 'XLV',
    'Financials': 'XLF',
    'Information Technology': 'SMH',
    'Communication Services': 'XLC',
    'Utilities': 'XLU',
    'Real Estate': 'IYR'
}

# --- Panel lateral de filtros ---
st.sidebar.markdown("## ⚙️ Filtros de Análisis")
selected_sectors = st.sidebar.multiselect("Sectores", list(SECTORAL_ETFS.keys()), default=["Information Technology", "Healthcare"])
year_range = st.sidebar.slider("Rango de Años", 2000, 2025, (2010, 2020))
start_date = f"{year_range[0]}-01-01"
end_date = f"{year_range[1]}-12-31"

show = st.sidebar.button("📈 Mostrar análisis")

# --- Función de análisis ---
@st.cache_data
def analyze_sectoral_etfs(selected_sectors, start, end):
    results = {}
    for sector in selected_sectors:
        ticker = SECTORAL_ETFS[sector]
        try:
            data = yf.download(ticker, start=start, end=end, progress=False, auto_adjust=True)[['Open', 'Close']]
            if data.empty:
                continue

            overnight_return = (data['Open'] / data['Close'].shift(1)) - 1.0
            intraday_return = (data['Close'] / data['Open']) - 1.0
            close_to_close_return = (data['Close'] / data['Close'].shift(1)) - 1.0

            results[sector] = {
                'overnight': (1 + overnight_return).cumprod().fillna(1),
                'intraday': (1 + intraday_return).cumprod().fillna(1),
                'close_to_close': (1 + close_to_close_return).cumprod().fillna(1)
            }
        except Exception as e:
            st.warning(f"⚠️ Error en {sector} ({ticker}): {e}")
    return results

# --- Visualización principal ---
if show:
    st.markdown("### 📉 Rentabilidades Acumuladas por Sector")

    results = analyze_sectoral_etfs(selected_sectors, start_date, end_date)
    if results:
        tabs = st.tabs(["🌙 Overnight", "📅 Close-to-Close", "☀️ Intraday"])
        categories = ["overnight", "close_to_close", "intraday"]
        titles = ["Retorno Acumulado Overnight", "Retorno Acumulado Close-to-Close", "Retorno Acumulado Intraday"]

        for i in range(3):
            with tabs[i]:
                
                fig, axs = plt.subplots(1, 1, figsize=(12, 10), sharex=True)

                for sector, data in results.items():
                    axs.plot(data[categories[i]], label=sector)

                axs.set_title(f"📈{titles[i]}")

      
                axs.set_yscale('log')
                axs.legend()
                axs.grid(True)

            
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.error("No se encontraron datos para los sectores seleccionados.")
