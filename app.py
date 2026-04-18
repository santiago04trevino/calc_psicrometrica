import streamlit as st
import math

# ==========================================
# 1. CONFIGURACIÓN DE LA INTERFAZ (UI)
# ==========================================
st.set_page_config(
    page_title="Calculadora Psicrometría",
    page_icon="💧",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inyección de CSS avanzado (Animaciones, Gradientes y Tarjetas)
st.markdown("""
    <style>
    /* Animación de entrada Fade In */
    @keyframes fadeIn {
        0% { opacity: 0; transform: translateY(20px); }
        100% { opacity: 1; transform: translateY(0); }
    }
    
    .main .block-container {
        animation: fadeIn 0.8s ease-out;
    }

    /* Título general (Blanco) */
    .titulo-blanco {
        font-size: 2.5rem;
        font-weight: 800;
        margin-bottom: 0px;
        padding-bottom: 0px;
        color: #f8fafc; /* Color blanco */
    }

    /* Clase específica solo para el gradiente */
    .texto-gradiente {
        background: linear-gradient(90deg, #a855f7, #6366f1);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
   
    /* Subtítulo descriptivo */
    .subtitle {
        color: #94a3b8;
        font-size: 1.2rem;
        margin-bottom: 2rem;
    }

    /* Tarjetas de Métricas (Estilo SaaS) */
    div[data-testid="stMetric"] {
        background-color: #111827;
        border: 1px solid #1f2937;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
        transition: all 0.3s ease;
    }
    
    div[data-testid="stMetric"]:hover {
        transform: translateY(-5px);
        border-color: #6366f1;
        box-shadow: 0 10px 15px -3px rgba(99, 102, 241, 0.2);
    }

    /* Etiquetas de las métricas */
    div[data-testid="stMetricLabel"] > div > div > p {
        color: #94a3b8;
        font-weight: 600;
        font-size: 1.1rem;
    }

    /* Valores principales de las métricas */
    div[data-testid="stMetricValue"] > div {
        color: #f8fafc;
        font-weight: 700;
    }

    /* Estilo del slider para que tenga gradiente en la barra de progreso */
    div[data-baseweb="slider"] > div > div > div:nth-child(1) {
        background: linear-gradient(90deg, #a855f7, #6366f1) !important;
    }
    </style>
    """, unsafe_allow_html=True)

# Título visualmente atractivo con HTML
st.markdown('<h1 class="titulo-blanco">Calculadora de agua contenida en el aire - <span class="texto-gradiente">Psicrometría</span></h1>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Análisis termodinámico avanzado para el cálculo de agua suspendida en espacios cerrados.</p>', unsafe_allow_html=True)
st.markdown("---")

# ==========================================
# 2. BARRA LATERAL (INPUTS DEL USUARIO)
# ==========================================
st.sidebar.markdown('<h2 style="color: white;">⚙️ Parámetros del Entorno</h2>', unsafe_allow_html=True)

altitud = st.sidebar.number_input("Altitud de la ciudad (msnm)", min_value=0, max_value=5000, value=2135, step=50)

# Ecuación Barométrica Estándar
presion_local_kpa = 101.325 * math.pow((1 - 2.25577e-5 * altitud), 5.2559)

factores_conversion = {
    "kPa": 1.0, "atm": 101.325, "bar": 100.0, 
    "psi": 6.89476, "mmHg": 0.133322, "hPa": 0.1, "Pa": 0.001
}

unidad_presion = st.sidebar.selectbox("Unidad de Presión", list(factores_conversion.keys()))
default_pres_local = presion_local_kpa / factores_conversion[unidad_presion]

presion_input = st.sidebar.number_input(
    f"Presión Atmosférica ({unidad_presion})", 
    value=float(default_pres_local), 
    step=0.1
)

presion_kpa_calculo = presion_input * factores_conversion[unidad_presion]

temperatura = st.sidebar.slider("Temperatura Bulbo Seco (°C)", min_value=-10.0, max_value=50.0, value=22.0, step=0.5)
humedad_relativa = st.sidebar.slider("Humedad Relativa (%)", min_value=1.0, max_value=100.0, value=50.0, step=1.0)

st.sidebar.markdown("---")
st.sidebar.markdown('<h2 style="color: white;">📐 Dimensiones</h2>', unsafe_allow_html=True)
volumen_salon = st.sidebar.number_input("Volumen del cuarto/salón (m³)", min_value=1.0, max_value=10000.0, value=150.0, step=10.0)

# ==========================================
# 3. MOTOR MATEMÁTICO (CÁLCULOS)
# ==========================================
def calcular_agua_en_aire(T, RH, P_atm, V):
    Pws = 0.61078 * math.exp((17.27 * T) / (T + 237.3))
    Pw = Pws * (RH / 100.0)
    omega = 0.621945 * (Pw / (P_atm - Pw))
    T_kelvin = T + 273.15
    v = (0.28704 * T_kelvin) / (P_atm - Pw)
    
    masa_aire_seco = V / v            
    volumen_aire_seco = masa_aire_seco * v  
    masa_agua_kg = masa_aire_seco * omega  
    litros_agua = masa_agua_kg  
    
    return masa_aire_seco, volumen_aire_seco, masa_agua_kg, omega, v, Pw, litros_agua

m_a, v_a, m_w, hum_abs, vol_esp, pres_vap, litros = calcular_agua_en_aire(temperatura, humedad_relativa, presion_kpa_calculo, volumen_salon)

# ==========================================
# 4. DESPLIEGUE DE RESULTADOS (OUTPUTS)
# ==========================================
st.markdown('<h3 style="color: white; margin-top: 20px;">Resultados del Análisis Termodinámico</h3>', unsafe_allow_html=True)

col1, col2 = st.columns(2)
col3, col4 = st.columns(2)

with col1:
    st.metric(label="💧 Masa de Agua Suspendida", value=f"{m_w:.2f} kg", delta=f"Equivalente a {litros:.2f} Litros", delta_color="off")
with col2:
    st.metric(label="🌬️ Masa de Aire Seco", value=f"{m_a:.1f} kg", delta=f"Volumen ocupado: {v_a:.1f} m³", delta_color="off")
with col3:
    st.metric(label="📈 Humedad Absoluta", value=f"{(hum_abs*1000):.1f} g/kg", delta=f"Presión de vapor: {pres_vap:.2f} kPa", delta_color="off")
with col4:
    st.metric(label="📦 Volumen Específico", value=f"{vol_esp:.3f} m³/kg", delta=f"Presión operativa: {presion_kpa_calculo:.2f} kPa", delta_color="off")
