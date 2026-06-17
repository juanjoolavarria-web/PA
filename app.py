import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Configuración de pantalla corporativa
st.set_page_config(page_title="Investment Portfolio OS", page_icon="📊", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #0d0e12; color: #f5f5f5; }
    .stMetric { background-color: #161920; padding: 20px; border-radius: 12px; border: 1px solid #272c3a; }
    .css-1r6slb0 { background-color: #161920; }
    </style>
    """, unsafe_allow_html=True)

# 2. Encabezado principal del Software
st.title("📊 Investment Portfolio OS")
st.markdown("Consolidador de Portafolio Multi-Custodio y Multi-Moneda.")

# 3. Zona de Carga Directa de Archivo (Drag & Drop)
st.sidebar.title("Control Panel")
uploaded_file = st.sidebar.file_uploader("Sube tu archivo Excel maestro aquí:", type=["xlsx"])
st.sidebar.markdown("---")

if uploaded_file is None:
    # Pantalla de bienvenida interactiva cuando no hay archivo
    st.info("👋 ¡Bienvenido! Por favor, arrastra tu archivo Excel 'Inversiones Rac-Renta4.xlsx' en el panel de la izquierda para encender el dashboard.")
    
    # Vista previa de la estructura esperada de la plataforma
    col1, col2, col3 = st.columns(3)
    col1.metric("Total AUM", "$0")
    col2.metric("Racional AUM", "$0")
    col3.metric("Renta4 AUM", "$0")
else:
    # Leer el Excel cargado dinámicamente con todas sus pestañas
    try:
        excel_data = pd.read_excel(uploaded_file, sheet_name=None)
        
        # Menu de navegación una vez que hay datos
        menu = st.sidebar.radio("Módulos", ["Consolidado (Overview)", "Trade Ledger (Transacciones)"])
        
        # --- MÓDULO: OVERVIEW ---
        if menu == "Consolidado (Overview)":
            if "Resumen" in excel_data:
                df_resumen = excel_data["Resumen"]
                
                # Selectores Corporativos de Moneda
                col_toggle, col_fx = st.columns([2, 2])
                with col_toggle:
                    moneda_base = st.radio("Moneda base del Dashboard:", ["CLP", "USD"], horizontal=True)
                with col_fx:
                    fx_rate = st.number_input("Tipo de Cambio de mercado (USD/CLP):", value=950.0, step=5.0)

                st.divider()

                # Pestañas por Custodio
                tab_total, tab_racional, tab_renta4 = st.tabs(["🌎 Portfolio Total", "📱 Racional", "🏦 Renta4"])
                
                def desplegar_tabla(df_filtrado):
                    if df_filtrado.empty:
                        st.info("No hay activos registrados para este criterio.")
                        return
                    st.dataframe(df_filtrado, use_container_width=True, hide_index=True)
                    
                    # Imprimir las columnas detectadas para programar las fórmulas exactas de rentabilidad
                    st.markdown("---")
                    st.write("🔧 **Columnas detectadas en tu hoja:**", list(df_filtrado.columns))

                with tab_total:
                    st.subheader("Visión Consolidada del Patrimonio")
                    desplegar_tabla(df_resumen)
                    
                with tab_racional:
                    st.subheader("Portafolio en Racional")
                    col_custodio = [c for c in df_resumen.columns if c.lower() in ['custodio', 'plataforma', 'broker']]
                    if col_custodio:
                        df_rac = df_resumen[df_resumen[col_custodio[0]].astype(str).str.contains("Racional", case=False, na=False)]
                        desplegar_tabla(df_rac)
                    else:
                        st.warning("Para filtrar por custodio, el Excel debe tener una columna que identifique la plataforma.")

                with tab_renta4:
                    st.subheader("Portafolio en Renta4")
                    col_custodio = [c for c in df_resumen.columns if c.lower() in ['custodio', 'plataforma', 'broker']]
                    if col_custodio:
                        df_r4 = df_resumen[df_resumen[col_custodio[0]].astype(str).str.contains("Renta", case=False, na=False)]
                        desplegar_tabla(df_r4)
                    else:
                        st.warning("Para filtrar por custodio, el Excel debe tener una columna que identifique la plataforma.")
            else:
                st.error("El archivo cargado no contiene una pestaña llamada 'Resumen'. Verifica los nombres de tus hojas.")

        # --- MÓDULO: TRADE LEDGER ---
        elif menu == "Trade Ledger (Transacciones)":
            st.title("📒 Registro General de Operaciones")
            pestanas_disponibles = [p for p in ["Compras", "Ventas", "Dividendos", "Evolución Mensual"] if p in excel_data]
            
            if pestanas_disponibles:
                tabs_ledger = st.tabs(pestanas_disponibles)
                for i, nombre_pestana in enumerate(pestanas_disponibles):
                    with tabs_ledger[i]:
                        st.subheader(f"Libro: {nombre_pestana}")
                        st.dataframe(excel_data[nombre_pestana], use_container_width=True, hide_index=True)
            else:
                st.warning("No se detectaron las pestañas clásicas de transacciones en el Excel.")
                
    except Exception as e:
        st.error(f"Error crítico al procesar el archivo Excel: {e}")
