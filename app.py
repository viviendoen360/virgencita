import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import urllib.parse
import os

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Custodia de la Virgen", page_icon="🙏", layout="centered")

# --- ESTILOS VISUALES ---
st.markdown("""
    <style>
    .stButton>button { width: 100%; border-radius: 12px; height: 3em; background-color: #25D366; color: white; font-weight: bold; border: none; }
    .stButton>button:hover { background-color: #128C7E; color: white; }
    .card { background-color: #f0f2f6; padding: 20px; border-radius: 10px; margin-bottom: 20px; text-align: center; color: #31333F !important; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
    .card h3, .card h4, .card p, .card small { color: #31333F !important; }
    
    /* Estilo para el Salmo del Día */
    .salmo-container {
        background-color: #fff9e6;
        padding: 25px;
        border-left: 5px solid #ffcc00;
        border-radius: 10px;
        margin-bottom: 25px;
        font-style: italic;
        text-align: center;
        box-shadow: 2px 2px 10px rgba(0,0,0,0.05);
        color: #5d4037 !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- LISTA DE SALMOS (Puedes ir agregando más hasta llegar a 365) ---
SALMOS_365 = [
    "“El Señor es mi pastor, nada me falta.” (Salmo 23:1)",
    "“Tu palabra es una lámpara a mis pies y una luz en mi camino.” (Salmo 119:105)",
    "“Pongan sus preocupaciones en las manos de Dios, pues él tiene cuidado de ustedes.” (1 Pedro 5:7)",
    "“El Señor es mi luz y mi salvación; ¿a quién temeré?” (Salmo 27:1)",
    "“Dios es nuestro amparo y nuestra fortaleza, nuestro pronto auxilio en las tribulaciones.” (Salmo 46:1)",
    "“Encomienda al Señor tu camino, confía en él, y él actuará.” (Salmo 37:5)",
    "“Todo lo puedo en Cristo que me fortalece.” (Filipenses 4:13)",
    "“Este es el día que hizo el Señor; nos gozaremos y alegraremos en él.” (Salmo 118:24)",
    "“El Señor guardará tu salida y tu entrada desde ahora y para siempre.” (Salmo 121:8)",
    "“Alma mía, en Dios solamente reposa, porque de él viene mi esperanza.” (Salmo 62:5)",
    "“Mi socorro viene del Señor, que hizo los cielos y la tierra.” (Salmo 121:2)",
    "“El corazón alegre hermosea el rostro.” (Proverbios 15:13)",
    "“Jehová es la fortaleza de mi vida; ¿de quién he de atemorizarme?” (Salmo 27:1)",
    "“Los que siembran con lágrimas, con regocijo segarán.” (Salmo 126:5)",
    "“Sean fuertes y valientes, no teman ni se asusten, porque el Señor va con ustedes.” (Deuteronomio 31:6)",
    "“En paz me acostaré, y asimismo dormiré; porque solo tú, Señor, me haces vivir confiado.” (Salmo 4:8)",
    "“Bendeciré al Señor en todo tiempo; su alabanza estará siempre en mi boca.” (Salmo 34:1)",
    "“Crea en mí, oh Dios, un corazón limpio, y renueva un espíritu recto dentro de mí.” (Salmo 51:10)",
    "“La alegría del Señor es nuestra fortaleza.” (Nehemías 8:10)",
    "“El Señor es bueno con todos, y su ternura abraza a todas sus criaturas.” (Salmo 145:9)"
]

# --- FUNCIONES ---
def obtener_salmo_dia():
    # Obtiene el día del año (1 al 365 o 366 si es bisiesto)
    dia_del_año = datetime.now().timetuple().tm_yday
    
    # El operador % asegura que si tienes menos de 365 salmos, vuelva a empezar la lista sin dar error
    indice_salmo = (dia_del_año - 1) % len(SALMOS_365)
    return SALMOS_365[indice_salmo]

def limpiar_telefono(telefono):
    s_tel = "".join(filter(str.isdigit, str(telefono)))
    if s_tel.startswith("09"): s_tel = "593" + s_tel[1:]
    elif s_tel.startswith("9"): s_tel = "593" + s_tel
    return s_tel

def generar_link_wa(telefono, mensaje):
    msg_encoded = urllib.parse.quote(mensaje)
    return f"https://wa.me/{limpiar_telefono(telefono)}?text={msg_encoded}"

def generar_link_calendar(fecha_obj, nombre_entrega):
    f_inicio = fecha_obj.strftime('%Y%m%d')
    f_fin = (fecha_obj + timedelta(days=1)).strftime('%Y%m%d')
    titulo = "🙏 Recibir Virgen María"
    descripcion = f"Recibir la imagen de manos de {nombre_entrega}. \n\n“Madre, en tus manos ponemos nuestro trabajo y nuestras familias. Amén.”"
    params = {'action': 'TEMPLATE', 'text': titulo, 'details': descripcion, 'dates': f"{f_inicio}/{f_fin}"}
    return f"https://www.google.com/calendar/render?{urllib.parse.urlencode(params)}"

def cargar_datos_demo():
    """Genera datos de prueba para la previsualización en Canvas"""
    hoy = datetime.now().date()
    datos = {
        'Fecha': [hoy - timedelta(days=1), hoy, hoy + timedelta(days=1), hoy + timedelta(days=2)],
        'Nombre': ['Juan Pérez', 'María Gómez', 'Carlos López', 'Ana Torres'],
        'Telefono': ['0987654321', '0991234567', '0981112233', '0999888777'],
        'Departamento': ['Contabilidad', 'Recursos Humanos', 'Auditoría', 'Legal']
    }
    df = pd.DataFrame(datos)
    return df

# --- INTERFAZ PRINCIPAL ---
st.title("🙏 Camino de la Virgen")

# --- SECCIÓN: SALMO DEL DÍA ---
salmo_hoy = obtener_salmo_dia()
st.markdown(f"""
    <div class="salmo-container">
        <p style="font-size: 1.2em; margin-bottom: 5px;">📖 <b>Palabra de Vida para hoy</b></p>
        <p style="font-size: 1.1em; color: #5d4037;">{salmo_hoy}</p>
    </div>
    """, unsafe_allow_html=True)

# Usamos datos de demo para que funcione aquí en la previsualización
df = cargar_datos_demo()

if df is not None:
    # A. CONSULTA POR FECHA
    st.markdown("### 📅 Consulta por fecha")
    fecha_actual = datetime.now().date()
    fecha_sel = st.date_input("Ver quién recibe el día:", value=fecha_actual, format="DD/MM/YYYY")
    
    fila = df[df['Fecha'] == fecha_sel]
    
    if not fila.empty:
        idx = fila.index[0]
        p_recibe = df.iloc[idx]
        if idx > 0:
            p_entrega = df.iloc[idx - 1]
            st.info(f"📍 **{fecha_sel.strftime('%d/%m/%Y')}** - Cambio de custodia.")
            
            c1, c2 = st.columns(2)
            with c1: st.markdown(f"<div class='card'><h3>Entrega</h3><h4>{p_entrega['Nombre']}</h4><small>{p_entrega['Departamento']}</small></div>", unsafe_allow_html=True)
            with c2: st.markdown(f"<div class='card'><h3>Recibe</h3><h4>{p_recibe['Nombre']}</h4><small>{p_recibe['Departamento']}</small></div>", unsafe_allow_html=True)
            
            # Botones WA
            oracion = "“Madre, en tus manos ponemos nuestro trabajo y nuestras familias. Amén.”"
            txt_dia = "hoy" if fecha_sel == fecha_actual else f"el {fecha_sel.strftime('%d/%m')}"
            msg_e = f"Hola {p_entrega['Nombre']}, {txt_dia} entregas la Virgen a {p_recibe['Nombre']}. \n\n{oracion}"
            msg_r = f"Hola {p_recibe['Nombre']}, {txt_dia} recibes la Virgen de {p_entrega['Nombre']}. \n\n{oracion}"
            
            col_b1, col_b2 = st.columns(2)
            with col_b1: st.link_button(f"📲 Avisar a {p_entrega['Nombre']}", generar_link_wa(p_entrega['Telefono'], msg_e))
            with col_b2: st.link_button(f"📩 Avisar a {p_recibe['Nombre']}", generar_link_wa(p_recibe['Telefono'], msg_r))
        else:
            st.info(f"Recibe: **{p_recibe['Nombre']}** (Primer día de la lista, {fecha_sel.strftime('%d/%m/%Y')})")
    else:
        st.warning("No hay entregas programadas para esta fecha en los datos de prueba.")

    # B. BUSCADOR
    st.markdown("---")
    st.header("🔍 Busca tu nombre")
    lista = sorted(df['Nombre'].unique())
    nombre = st.selectbox("Selecciona tu nombre:", [""] + lista)
    
    if nombre:
        turnos = df[df['Nombre'] == nombre]
        for i, r in turnos.iterrows():
            f_t = r['Fecha']
            n_e = df.iloc[i-1]['Nombre'] if i > 0 else "Inicio"
            st.write(f"🗓️ **{f_t.strftime('%d/%m/%Y')}** (Entrega: {n_e})")
            st.link_button("📅 Agendar en Google", generar_link_calendar(f_t, n_e))
