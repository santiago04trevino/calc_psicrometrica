import streamlit as st
import math

# ==========================================
# 1. CONFIGURACIÓN DE LA INTERFAZ (UI)
# ==========================================
st.set_page_config(
    page_title="Calculadora Psicrométrica HVAC",
    page_icon="💧",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilo CSS personalizado para darle un toque más moderno
st.markdown("""
    <style>
    .main {background-color: #f8f9fa;}
    h1 {color: #1f77b4;}
    .stMetric {background-color: white; padding: 15px; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);}
    </style>
    """, unsafe_allow_html=True)

# Título y descripción
st.title("💧 Calculadora de Agua Contenida en el Aire (Psicrometría)")
st.markdown("---")
st.markdown("""
Esta aplicación calcula la masa y el volumen equivalente de agua en estado de vapor contenida en un espacio cerrado. 
Utiliza correlaciones termodinámicas estándar de ASHRAE. Diseñado para ingeniería de servicios auxiliares y climatización.
""")

# ==========================================
# 2. BARRA LATERAL (INPUTS DEL USUARIO)
# ==========================================
st.sidebar.header("⚙️ Parámetros del Entorno")

# Usamos Puebla como valores por defecto (Altitud ~2135 m, T=22°C, RH=50%)
altitud = st.sidebar.number_input("Altitud de la ciudad (msnm)", min_value=0, max_value=5000, value=2135, step=50, help="Puebla está a aprox. 2135 msnm")

# Cálculo automático de presión local (Ecuación Barométrica Estándar)
# P = 101.325 * (1 - 2.25577e-5 * Altitud)^5.2559
presion_local_kpa = 101.325 * math.pow((1 - 2.25577e-5 * altitud), 5.2559)

presion_input = st.sidebar.number_input("Presión Atmosférica (kPa)", min_value=50.0, max_value=110.0, value=float(presion_local_kpa), step=0.1, help="Calculada automáticamente por la altitud, pero modificable.")
temperatura = st.sidebar.slider("Temperatura Bulbo Seco (°C)", min_value=-10.0, max_value=50.0, value=22.0, step=0.5)
humedad_relativa = st.sidebar.slider("Humedad Relativa (%)", min_value=1.0, max_value=100.0, value=50.0, step=1.0)

st.sidebar.markdown("---")
st.sidebar.header("📐 Dimensiones del Espacio")
volumen_salon = st.sidebar.number_input("Volumen del cuarto/salón (m³)", min_value=1.0, max_value=10000.0, value=150.0, step=10.0, help="Ejemplo: Un salón de 10m x 5m x 3m = 150 m³")


# ==========================================
# 3. MOTOR MATEMÁTICO (CÁLCULOS)
# ==========================================
def calcular_agua_en_aire(T, RH, P_atm, V):
    # A. Presión de saturación de vapor de agua (Ecuación de Magnus-Tetens, Pws en kPa)
    # Valida para agua líquida (0°C a 200°C)
    Pws = 0.61078 * math.exp((17.27 * T) / (T + 237.3))
    
    # B. Presión parcial del vapor de agua (Pw en kPa)
    Pw = Pws * (RH / 100.0)
    
    # C. Relación de Humedad (Humedad Absoluta, omega en kg agua / kg aire seco)
    omega = 0.621945 * (Pw / (P_atm - Pw))
    
    # D. Volumen Específico del aire húmedo (v en m³/kg aire seco)
    # Ra (Constante aire seco) = 0.28704 kJ/kg.K
    T_kelvin = T + 273.15
    v = (0.28704 * T_kelvin) / (P_atm - Pw)
    
    # E. Cálculo de Masas
    masa_aire_seco = V / v            # kg de aire seco
    masa_agua_kg = masa_aire_seco * omega  # kg de agua
    
    # F. Conversión a Litros (1 kg de agua líquida ~ 1 Litro)
    litros_agua = masa_agua_kg
    
    return masa_aire_seco, omega, v, Pw, litros_agua

# Ejecutar el cálculo
m_a, hum_abs, vol_esp, pres_vap, litros = calcular_agua_en_aire(temperatura, humedad_relativa, presion_input, volumen_salon)

# ==========================================
# 4. DESPLIEGUE DE RESULTADOS (OUTPUTS)
# ==========================================
st.subheader("📊 Resultados del Análisis")

# Columnas para métricas principales
col1, col2, col3 = st.columns(3)

with col1:
    st.metric(label="💧 Agua Total en el Aire", value=f"{litros:.2f} Litros", delta="Condensado equivalente")
with col2:
    st.metric(label="🌬️ Masa de Aire Seco", value=f"{m_a:.1f} kg", delta=f"Volumen esp: {vol_esp:.3f} m³/kg", delta_color="off")
with col3:
    st.metric(label="📈 Humedad Absoluta", value=f"{(hum_abs*1000):.1f} g/kg", delta=f"Presión vapor: {pres_vap:.2f} kPa", delta_color="off")

st.markdown("---")

# Explicación de ingeniería para el usuario
st.info(f"**Análisis de Ingeniería:** En un espacio de **{volumen_salon} m³** en las condiciones ingresadas ({temperatura}°C y {humedad_relativa}% HR a {presion_input:.1f} kPa), el aire contiene **{litros:.2f} litros** de agua en forma de vapor. Si un equipo de aire acondicionado enfriara este aire por debajo de su punto de rocío, esta es la cantidad máxima de condensado que el equipo drenaría al deshumidificar el salón por completo.")
