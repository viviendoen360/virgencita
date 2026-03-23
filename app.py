import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import urllib.parse
import os

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(
    page_title="Custodia de la Virgen",
    page_icon="🙏",
    layout="centered"
)

# --- ESTILOS VISUALES (Dark Mode Friendly) ---
st.markdown("""
    <style>
    /* Botones estilo WhatsApp */
    .stButton>button {
        width: 100%;
        border-radius: 12px;
        height: 3em;
        background-color: #25D366; 
        color: white;
        font-weight: bold;
        border: none;
    }
    .stButton>button:hover {
        background-color: #128C7E;
        color: white;
    }
    
    /* ESTILO DE TARJETAS */
    .card {
        background-color: #f0f2f6; 
        padding: 20px;
        border-radius: 10px;
        margin-bottom: 20px;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        color: #31333F !important; 
    }
    .card h3, .card h4, .card p, .card small {
        color: #31333F !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- CONSTANTES ---
ORACION = "“Madre, en tus manos ponemos nuestro trabajo y nuestras familias. Amén.”"
ARCHIVO_DEFAULT = "lista.xlsx"

# --- FUNCIONES ---
def limpiar_telefono(telefono):
    s_tel = str(telefono)
    s_tel = "".join(filter(str.isdigit, s_tel))
    if s_tel.startswith("09"):
        return "593" + s_tel[1:]
    elif s_tel.startswith("9"):
         return "593" + s_tel
    return s_tel

def generar_link_wa(telefono, mensaje):
    tel_clean = limpiar_telefono(telefono)
    msg_encoded = urllib.parse.quote(mensaje)
    return f"https://wa.me/{tel_clean}?text={msg_encoded}"

def generar_link_calendar(fecha_obj, nombre_entrega):
    f_inicio = fecha_obj.strftime('%Y%m%d')
    f_fin = (fecha_obj + timedelta(days=1)).strftime('%Y%m%d')
    
    titulo = "🙏 Recibir Virgen María"
    descripcion = f"Recibir la imagen de manos de {nombre_entrega}. \n\n{ORACION}"
    
    params = {
        'action': 'TEMPLATE',
        'text': titulo,
        'details': descripcion,
        'dates': f"{f_inicio}/{f_fin}"
    }
    return f"https://www.google.com/calendar/render?{urllib.parse.urlencode(params)}"

def cargar_datos(archivo):
    try:
        df = pd.read_excel(archivo, engine='openpyxl')
        df.columns = [c.strip().capitalize() for c in df.columns]
        if 'Fecha' in df.columns:
            df['Fecha'] = pd.to_datetime(df['Fecha']).dt.date
        return df
    except Exception as e:
        st.error(f"Error leyendo el archivo: {e}")
        return None

# --- INTERFAZ PRINCIPAL ---
st.title("🙏 Camino de la Virgen")

# Carga directa desde GitHub
df = None
if os.path.exists(ARCHIVO_DEFAULT):
    df = cargar_datos(ARCHIVO_DEFAULT)

# --- LÓGICA DEL PROGRAMA ---
if df is not None:
    # A. SECCIÓN DE FECHA INTERACTIVA
    st.markdown("### 📅 Consulta por fecha")
    
    # El calendario por defecto muestra el día de hoy
    fecha_actual = datetime.now().date()
    fecha_seleccionada = st.date_input("Selecciona un día para ver a quién le corresponde:", value=fecha_actual, format="DD/MM/YYYY")
    
    # Filtramos la base de datos según la fecha que elija el usuario
    fila_fecha = df[df['Fecha'] == fecha_seleccionada]
    
    if not fila_fecha.empty:
        idx_fecha = fila_fecha.index[0]
        p_recibe = df.iloc[idx_fecha]
        
        if idx_fecha > 0:
            p_entrega = df.iloc[idx_fecha - 1]
            
            # Ajuste de texto según si es hoy u otro día
            if fecha_seleccionada == fecha_actual:
                st.info(f"**HOY ({fecha_seleccionada.strftime('%d/%m/%Y')})** - Hay cambio de custodia.")
                texto_dia = "hoy"
            else:
                st.info(f"**{fecha_seleccionada.strftime('%d/%m/%Y')}** - Custodia programada para este día.")
                texto_dia = f"el {fecha_seleccionada.strftime('%d/%m/%Y')}"
            
            col1, col2 = st.columns(2)
            with col1:
                st.markdown(f"""
                <div class="card">
                    <div style='font-size:2em;'>📤</div>
                    <h3>Entrega</h3>
                    <h4>{p_entrega['Nombre']}</h4>
                    <small>{p_entrega['Departamento']}</small>
                </div>
                """, unsafe_allow_html=True)

            with col2:
                st.markdown(f"""
                <div class="card">
                    <div style='font-size:2em;'>📥</div>
                    <h3>Recibe</h3>
                    <h4>{p_recibe['Nombre']}</h4>
                    <small>{p_recibe['Departamento']}</small>
                </div>
                """, unsafe_allow_html=True)
            
            # Botones WA adaptados a la fecha elegida
            msg_e = f"👋 Hola *{p_entrega['Nombre']}*, {texto_dia} entregas la imagen de la Virgen a *{p_recibe['Nombre']}* ({p_recibe['Departamento']}).\n\n{ORACION}"
            msg_r = f"👋 Hola *{p_recibe['Nombre']}*, {texto_dia} recibes la visita de la Virgen de manos de *{p_entrega['Nombre']}*.\n\n{ORACION}"
            
            c1, c2 = st.columns(2)
            with c1:
                st.link_button(f"📲 Avisar a {p_entrega['Nombre']}", generar_link_wa(p_entrega['Telefono'], msg_e))
            with c2:
                st.link_button(f"📩 Avisar a {p_recibe['Nombre']}", generar_link_wa(p_recibe['Telefono'], msg_r))
        else:
            st.info(f"Recibe: **{p_recibe['Nombre']}** (Primer día de la lista, {fecha_seleccionada.strftime('%d/%m/%Y')})")
    else:
        if fecha_seleccionada == fecha_actual:
            st.warning(f"Hoy ({fecha_seleccionada.strftime('%d/%m/%Y')}) no hay entregas programadas.")
        else:
            st.warning(f"El {fecha_seleccionada.strftime('%d/%m/%Y')} no hay entregas programadas en la lista.")

    # B. BUSCADOR POR NOMBRE
    st.markdown("---")
    st.header("🔍 Busca por tu nombre")
    
    lista_nombres = sorted(df['Nombre'].unique())
    nombre_seleccionado = st.selectbox("Selecciona tu nombre para ver tus fechas:", lista_nombres)

    if nombre_seleccionado:
        mis_turnos = df[df['Nombre'] == nombre_seleccionado]
        
        if not mis_turnos.empty:
            st.success(f"Hola **{nombre_seleccionado}**, te toca recibir la imagen en estas fechas:")
            
            for idx, row in mis_turnos.iterrows():
                fecha_turno = row['Fecha']
                
                nombre_entrega = "un compañero"
                if idx > 0:
                    nombre_entrega = df.iloc[idx - 1]['Nombre']
                
                link_cal = generar_link_calendar(fecha_turno, nombre_entrega)
                
                col_a, col_b = st.columns([2, 2])
                with col_a:
                    st.markdown(f"🗓️ **{fecha_turno.strftime('%d/%m/%Y')}**")
                    st.caption(f"Recibes de: {nombre_entrega}")
                with col_b:
                    st.link_button("📅 Agendar en Google", link_cal)
                st.markdown("---")
        else:
            st.info("No tienes fechas asignadas en la lista actual.")

else:
    st.error("⚠️ No se encontró la base de datos.")
    st.info("Por favor, sube el archivo 'lista.xlsx' al repositorio de GitHub.")
