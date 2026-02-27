import streamlit as st
from openai import OpenAI

# =============================================================================
# CONFIGURACIÓN PWA Y MÓVIL - OPTIMIZADO PARA "AÑADIR A INICIO"
# =============================================================================
st.set_page_config(
    page_title="Juventus 🦅",
    page_icon="🦅",
    layout="centered",
    initial_sidebar_state="collapsed",
    menu_items={
        'Get Help': None,
        'Report a bug': None,
        'About': None
    }
)

# CSS para ocultar elementos de Streamlit y dar apariencia de app nativa
st.markdown("""
    <style>
        /* Ocultar elementos innecesarios */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        [data-testid="stDecoration"] {display: none;}
        [data-testid="stSidebar"] {display: none;}
        
        /* Optimizar para móvil */
        .stApp {max-width: 100%; padding: 0;}
        .stChatMessage {padding: 0.5rem 0;}
        .stChatInputContainer {padding-bottom: 1rem;}
        
        /* Estilo visual Juventus - colores josefinos */
        .stTitle {color: #1a365d; font-weight: bold;}
        .stChatMessage-user {background-color: #e6f3ff;}
        .stChatMessage-assistant {background-color: