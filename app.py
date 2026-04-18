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

# Estilo CSS personalizado 
st.markdown("""
    <style>
    .main {background-color: #f8f9fa;}
    h1 {color: #1f77b4;}
    .stMetric {background-color: white; padding: 15px; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);}
    </style>
    """, unsafe_allow_html=True)

st.title("💧 Calculadora de Agua Contenida en el Aire (Psicrometría)")
st.markdown("---")
st.markdown("""
Esta aplicación calcula la masa de agua en estado de vapor contenida en un espacio cerrado. 
Utiliza correlaciones termodinámicas estándar de ASHRAE e integra conversión dinámica de unidades de presión.
""")

# ==========================================
# 2. BARRA LATERAL (INPUTS DEL USUARIO)
# ==========================================
st.sidebar.header("⚙️ Parámetros del Entorno")

altitud = st.sidebar.number_input("Altitud de la ciudad (msnm)", min_value=0, max_value=5000, value=2135, step=50, help="Ejemplo: 2135 msnm")

# Cálculo automático de presión local (Ecuación Barométrica Estándar en kPa)
presion_local_kpa = 101.325 * math.pow((1 - 2.25577e-5 * altitud), 5.2559)

# Diccionario de factores de conversión a kPa
factores_conversion = {
    "kPa": 1.0,
    "atm": 101.325,
    "bar": 100.0,
    "psi": 6.89476,
    "mmHg": 0.133322,
    "hPa": 0.1,
    "Pa": 0.001
}

# Selector de unidades de presión
unidad_presion = st.sidebar.selectbox("Unidad de Presión", list(factores_conversion.keys()))

# Conversión del valor calculado por altitud a la unidad seleccionada por el usuario
default_pres_local = presion_local_kpa / factores_conversion[unidad_presion]

presion_input = st.sidebar.number_input(
    f"Presión Atmosférica ({unidad_presion})", 
    value=float(default_pres_local), 
    step=0.1, 
    help="El valor se estima por la altitud, pero puede ingresarse de forma manual."
)

# Conversión interna y silenciosa a kPa para ser procesada por el motor matemático
presion_kpa_calculo = presion_input * factores_conversion[unidad_presion]

temperatura = st.sidebar.slider("Temperatura Bulbo Seco (°C)", min_value=-10.0, max_value=50.0, value=22.0, step=0.5)
humedad_relativa = st.sidebar.slider("Humedad Relativa (%)", min_value=1.0, max_value=100.0, value=50.0, step=1.0)

st.sidebar.markdown("---")
st.sidebar.header("📐 Dimensiones del Espacio")
volumen_salon = st.sidebar.number_input("Volumen del cuarto/salón (m³)", min_value=1.0, max_value=10000.0, value=150.0, step=10.0)

# ==========================================
# 3. MOTOR MATEMÁTICO (CÁLCULOS)
# ==========================================
def calcular_agua_en_aire(T, RH, P_atm, V):
    # Ecuación de Magnus-Tetens para presión de saturación
    Pws = 0.61078 * math.exp((17.27 * T) / (T + 237.3))
    Pw = Pws * (RH / 100.0)
    
    # Humedad Absoluta (omega)
    omega = 0.621945 * (Pw / (P_atm - Pw))
    
    # Volumen Específico
    T_kelvin = T + 273.15
    v = (0.28704 * T_kelvin) / (P_atm - Pw)
    
    # Desglose de masas
    masa_aire_seco = V / v            
    masa_agua_kg = masa_aire_seco * omega  
    litros_agua = masa_agua_kg  # 1 kg de agua líquida ~ 1 Litro
    
    return masa_aire_seco, masa_agua_kg, omega, v, Pw, litros_agua

# Ejecución de la función
m_a, m_w, hum_abs, vol_esp, pres_vap, litros = calcular_agua_en_aire(temperatura, humedad_relativa, presion_kpa_calculo, volumen_salon)

# ==========================================
# 4. DESPLIEGUE DE RESULTADOS (OUTPUTS)
# ==========================================
st.subheader("📊 Resultados del Análisis Termodinámico")

# Cuadrícula 2x2 para mejor visualización
col1, col2 = st.columns(2)
col3, col4 = st.columns(2)

with col1:
    st.metric(label="💧 Masa de Agua Suspendida", value=f"{m_w:.2f} kg", delta=f"Equivalente a {litros:.2f} Litros", delta_color="off")
with col2:
    st.metric(label="🌬️ Masa de Aire Seco", value=f"{m_a:.1f} kg", delta="Fluido portador", delta_color="off")
with col3:
    st.metric(label="📈 Humedad Absoluta", value=f"{(hum_abs*1000):.1f} g/kg", delta=f"Presión de vapor: {pres_vap:.2f} kPa", delta_color="off")
with col4:
    st.metric(label="📦 Volumen Específico", value=f"{vol_esp:.3f} m³/kg", delta=f"Presión operativa: {presion_kpa_calculo:.2f} kPa", delta_color="off")

st.markdown("---")

# Resumen técnico
st.info(f"**Análisis Técnico:** En un volumen de control de **{volumen_salon} m³** sometido a las condiciones de {temperatura}°C, {humedad_relativa}% HR y una presión atmosférica calculada de **{presion_kpa_calculo:.2f} kPa**, el sistema contiene exactamente **{m_w:.2f} kg de agua** disuelta en **{m_a:.1f} kg de aire seco**.")
