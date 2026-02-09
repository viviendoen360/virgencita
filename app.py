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

# --- ESTILOS VISUALES ---
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
    
    /* ESTILO DE TARJETAS (Fixed para Dark Mode) */
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

    /* Botón de Calendario (Azul) */
    .calendar-btn {
        background-color: #4285F4 !important;
    }
    </style>
    "