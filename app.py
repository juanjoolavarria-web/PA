import streamlit as st
import pandas as pd

# 1. Configuración Institucional
st.set_page_config(page_title="Investment Portfolio OS", page_icon="📊", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #0d0e12; color: #f5f5f5; }
    .stMetric { background-color: #161920; padding: 20px; border-radius: 12px; border: 1px solid #272c3a; }
    .css-1r6slb0 { background-color: #161920; }
    </style>
    """, unsafe_allow_html=True)

st.title("📊 Investment Portfolio OS")
st.markdown("Consolidador Transaccional y Cálculo Dinámico de Posiciones.")

# 2. Panel de Carga Directa
st.sidebar.title("Control Panel")
uploaded_file = st.sidebar.file_uploader("Sube tu archivo Excel maestro (Solo Compras, Ventas, Divs):", type=["xlsx"])
st.sidebar.markdown("---")

if uploaded_file is None:
    st.info("👋 Por favor, arrastra tu archivo Excel transaccional en el panel de la izquierda.")
else:
    try:
        excel_data = pd.read_excel(uploaded_file, sheet_name=None)
        
        # Validación de pestañas requeridas
        if "Compras" not in excel_data or "Ventas" not in excel_data:
            st.error("El Excel debe contener exactamente las pestañas llamadas 'Compras' y 'Ventas'.")
        else:
            df_compras = excel_data["Compras"]
            df_ventas = excel_data["Ventas"]
            
            # --- MOTOR DE CONSOLIDACIÓN (NETTING DE POSICIONES) ---
            # Nota: Este bloque intenta encontrar columnas genéricas. 
            # Los nombres de columnas deben ajustarse a la realidad de tu Excel.
            
            # Buscar el nombre de la columna que tiene el Ticker/Activo
            col_activo_compra = [c for c in df_compras.columns if c.lower() in ['símbolo', 'ticker', 'activo', 'instrumento']][0]
            col_cant_compra = [c for c in df_compras.columns if c.lower() in ['cantidad', 'acciones', 'títulos']][0]
            
            col_activo_venta = [c for c in df_ventas.columns if c.lower() in ['símbolo', 'ticker', 'activo', 'instrumento']][0]
            col_cant_venta = [c for c in df_ventas.columns if c.lower() in ['cantidad', 'acciones', 'títulos']][0]

            # Sumar total comprado por activo
            compras_agrupadas = df_compras.groupby(col_activo_compra)[col_cant_compra].sum().reset_index()
            compras_agrupadas.rename(columns={col_activo_compra: 'Activo', col_cant_compra: 'Total_Comprado'}, inplace=True)
            
            # Sumar total vendido por activo
            ventas_agrupadas = df_ventas.groupby(col_activo_venta)[col_cant_venta].sum().reset_index()
            ventas_agrupadas.rename(columns={col_activo_venta: 'Activo', col_cant_venta: 'Total_Vendido'}, inplace=True)
            
            # Cruzar datos (Merge) para obtener el neto
            df_posiciones = pd.merge(compras_agrupadas, ventas_agrupadas, on='Activo', how='left')
            df_posiciones['Total_Vendido'].fillna(0, inplace=True) # Llenar con 0 si no hay ventas
            
            # CÁLCULO ESTRELLA: Posición Viva Exacta
            df_posiciones['Acciones_Activas'] = df_posiciones['Total_Comprado'] - df_posiciones['Total_Vendido']
            
            # Filtrar activos que ya se vendieron por completo (Posición 0)
            df_posiciones_vivas = df_posiciones[df_posiciones['Acciones_Activas'] > 0]

            # --- RENDERIZADO DEL DASHBOARD ---
            menu = st.sidebar.radio("Módulos", ["Posiciones Activas (Overview)", "Trade Ledger (Transacciones)"])
            
            if menu == "Posiciones Activas (Overview)":
                st.subheader("Resumen Dinámico del Portafolio")
                st.markdown("Tabla generada automáticamente calculando Compras - Ventas.")
                
                # Desplegar la tabla consolidada
                st.dataframe(df_posiciones_vivas, use_container_width=True, hide_index=True)
                
            elif menu == "Trade Ledger (Transacciones)":
                st.subheader("Libros Auxiliares")
                tabs_ledger = st.tabs(["Compras", "Ventas", "Dividendos"])
                with tabs_ledger[0]: st.dataframe(df_compras, use_container_width=True)
                with tabs_ledger[1]: st.dataframe(df_ventas, use_container_width=True)
                if "Dividendos" in excel_data:
                    with tabs_ledger[2]: st.dataframe(excel_data["Dividendos"], use_container_width=True)

    except Exception as e:
        st.error(f"Error al procesar los datos: Revisa que los nombres de las columnas coincidan. Detalle técnico: {e}")
