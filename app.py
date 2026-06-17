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
    st.markdown("Sube tus cartolas en formato PDF (Base 31/12/2025 o Mensuales). El sistema extraerá la información financieramente relevante.")
    
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
        st.markdown("Cada institución (LarrainVial, Compass, Banchile, BTG
