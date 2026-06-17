import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Configuración del software
st.set_page_config(
    page_title="Investment Portfolio OS",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. Base de datos de prueba (Mock Data)
# Puedes modificar estos datos directamente o luego conectarlo a un Excel
@st.cache_data
def cargar_datos():
    data = {
        "Activo": ["Fondo KKR Américas", "Oaktree Private Debt", "Stonepeak Infra", "SaaS Portfolio (nCino/Globant)", "Liquidez Banco"],
        "Clase": ["Private Equity", "Private Credit", "Infrastructure", "Public Equity", "Caja (CLP)"],
        "Moneda": ["USD", "USD", "USD", "USD", "CLP"],
        "Costo Base": [100000, 80000, 100000, 40000, 15000],
        "NAV Actual": [145000, 88000, 115000, 48000, 15000]
    }
    df = pd.DataFrame(data)
    df["P&L LTM"] = df["NAV Actual"] - df["Costo Base"]
    df["MOIC"] = df["NAV Actual"] / df["Costo Base"]
    return df

df = cargar_datos()

# 3. Menú Lateral
st.sidebar.title("Menú Principal")
st.sidebar.markdown("---")
opcion = st.sidebar.radio("Módulos", ["Overview (Dashboard)", "Posiciones y NAV", "Data Room (Subir Cartolas)"])

# 4. Vistas del Software
if opcion == "Overview (Dashboard)":
    st.title("Consolidado del Portafolio")
    st.markdown("Visión macro y Asset Allocation al cierre del trimestre.")
    
    total_nav = df["NAV Actual"].sum()
    total_costo = df["Costo Base"].sum()
    total_pl = total_nav - total_costo
    
    # KPIs Corporativos
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total AUM (USD)", f"${total_nav:,.0f}")
    col2.metric("Total P&L", f"${total_pl:,.0f}", f"{(total_pl/total_costo)*100:.1f}%")
    col3.metric("Blended MOIC", f"{(total_nav/total_costo):.2f}x")
    col4.metric("Posiciones Activas", len(df))
    
    st.divider()
    
    # Gráficos
    col_grafico1, col_grafico2 = st.columns(2)
    
    with col_grafico1:
        st.subheader("Asset Allocation")
        fig_pie = px.pie(df, values='NAV Actual', names='Clase', hole=0.4)
        fig_pie.update_layout(margin=dict(t=0, b=0, l=0, r=0))
        st.plotly_chart(fig_pie, use_container_width=True)
        
    with col_grafico2:
        st.subheader("Exposición por Activo")
        fig_bar = px.bar(df, x='Activo', y='NAV Actual', color='Clase')
        fig_bar.update_layout(margin=dict(t=0, b=0, l=0, r=0))
        st.plotly_chart(fig_bar, use_container_width=True)

elif opcion == "Posiciones y NAV":
    st.title("Detalle de Posiciones")
    st.markdown("Seguimiento línea por línea.")
    
    # Mostrar tabla con formato
    st.dataframe(
        df,
        column_config={
            "Costo Base": st.column_config.NumberColumn(format="$ %d"),
            "NAV Actual": st.column_config.NumberColumn(format="$ %d"),
            "P&L LTM": st.column_config.NumberColumn(format="$ %d"),
            "MOIC": st.column_config.NumberColumn(format="%.2f x")
        },
        hide_index=True,
        use_container_width=True
    )

elif opcion == "Data Room (Subir Cartolas)":
    st.title("Procesamiento de Cartolas")
    st.markdown("Módulo en construcción para parsing de PDFs (Upload Inicial: 31/12/2025).")
    uploaded_file = st.file_uploader("Arrastra tu PDF bancario o de corredora aquí", type="pdf")
    
    if uploaded_file is not None:
        st.success(f"Archivo '{uploaded_file.name}' cargado exitosamente. Listo para extracción OCR.")