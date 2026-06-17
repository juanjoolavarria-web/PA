import streamlit as st
import pandas as pd
import plotly.express as px
import pdfplumber

# 1. Configuración de pantalla corporativa (Dark Mode)
st.set_page_config(
    page_title="Investment Portfolio OS", 
    page_icon="📊", 
    layout="wide"
)

# Estilos visuales de nivel SaaS institucional
st.markdown("""
    <style>
    .main { background-color: #0d0e12; color: #f5f5f5; }
    .stMetric { background-color: #161920; padding: 20px; border-radius: 12px; border: 1px solid #272c3a; }
    .css-1r6slb0 { background-color: #161920; }
    </style>
    """, unsafe_allow_html=True)

# 2. Inicializar base de datos temporal en memoria
if "portfolio_data" not in st.session_state:
    st.session_state.portfolio_data = pd.DataFrame(columns=["Activo", "Clase", "Moneda", "Monto/NAV", "Fecha"])

# 3. Menú Lateral de Navegación
st.sidebar.title("Wealth OS v1.0")
st.sidebar.markdown("---")
menu = st.sidebar.radio("Módulos", ["Overview / Dashboard", "Data Room (Subir Cartolas)"])

# --- MÓDULO: DATA ROOM (SUBIR ARCHIVOS) ---
if menu == "Data Room (Subir Cartolas)":
    st.title("🗂️ Centro de Procesamiento de Documentos")
    
    st.markdown("""Sube tus cartolas en formato PDF (Base 31/12/2025 o Mensuales). El sistema extraerá la información financieramente relevante.""")
    
    tipo_cartola = st.selectbox("Tipo de Cartola", ["Línea Base (31/12/2025)", "Evolución Mensual (2026)"])
    
    uploaded_file = st.file_uploader("Arrastra aquí tu cartola en PDF", type="pdf")
    
    if uploaded_file is not None:
        st.info("Procesando archivo... Extrayendo capas de texto.")
        
        # Leer el PDF de forma gratuita con pdfplumber
        texto_completo = ""
        with pdfplumber.open(uploaded_file) as pdf:
            for pagina in pdf.pages:
                texto_completo += pagina.extract_text() or ""
        
        st.success("¡Texto extraído con éxito!")
        
        # Cuadro estilo consola de software con el texto reconocido
        st.subheader("Vista Previa del Reconocimiento de Datos")
        st.text_area("Texto crudo detectado en el documento:", value=texto_completo, height=250)
        
        st.markdown("---")
        st.subheader("Configuración del Parser Automático")
        
        st.markdown("""Cada institución (LarrainVial, Compass, Banchile, BTG, etc.) ordena los datos de forma distinta. Para crear tu regla de reconocimiento a medida, dime qué datos ves arriba:""")
        
        # Mapeo manual inicial para calibrar el algoritmo
        nombre_detectado = st.text_input("¿Qué nombre de activo o fondo detectas en el texto?")
        monto_detectado = st.number_input("¿Qué monto o saldo final aparece para ese activo?", min_value=0.0, step=1000.0)
        
        if st.button("Validar e Inyectar al Portafolio"):
            nueva_fila = {
                "Activo": nombre_detectado if nombre_detectado else "Activo Detectado",
                "Clase": "Por Clasificar",
                "Moneda": "USD" if "USD" in texto_completo or "US$" in texto_completo else "CLP",
                "Monto/NAV": monto_detectado,
                "Fecha": "31/12/2025" if tipo_cartola == "Línea Base (31/12/2025)" else "Mensual"
            }
            # Agregar la fila a nuestra base de datos en memoria
            st.session_state.portfolio_data = pd.concat([st.session_state.portfolio_data, pd.DataFrame([nueva_fila])], ignore_index=True)
            st.success("Posición guardada temporalmente. Ya puedes revisarla en el módulo Overview.")

# --- MÓDULO: OVERVIEW / DASHBOARD ---
elif menu == "Overview / Dashboard":
    st.title("📊 Consolidado General del Portafolio")
    
    df_actual = st.session_state.portfolio_data
    
    if df_actual.empty:
        st.warning("El portafolio está vacío. Ve al 'Data Room' para subir tu primera cartola al 31/12/2025.")
        
        # KPIs en cero por defecto
        col1, col2 = st.columns(2)
        col1.metric("Total Patrimonio (AUM)", "$0")
        col2.metric("Activos Registrados", "0")
    else:
        total_aum = df_actual["Monto/NAV"].sum()
        
        # KPIs con data real extraída
        col1, col2 = st.columns(2)
        col1.metric("Total Patrimonio (AUM)", f"${total_aum:,.0f}")
        col2.metric("Activos Registrados", len(df_actual))
        
        st.divider()
        st.subheader("Posiciones Consolidadas")
        st.dataframe(df_actual, use_container_width=True, hide_index=True)
        
        # Gráfico dinámico automatizado
        fig = px.bar(df_actual, x="Activo", y="Monto/NAV", title="Distribución por Activo", color="Moneda", template="plotly_dark")
        st.plotly_chart(fig, use_container_width=True)
