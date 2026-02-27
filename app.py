import streamlit as st
from openai import OpenAI

# CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="Mi IA Personal", page_icon="🤖")

# --- CONFIGURACIÓN DE PERSONALIDAD ---
SYSTEM_PROMPT = """
Eres un asistente útil y amigable. Responde de forma concisa.
"""
# -------------------------------------

st.title("🤖 Mi IA Personal")

# Inicializar cliente de OpenAI (conectado a Groq)
try:
    client = OpenAI(
        base_url="https://api.groq.com/openai/v1",
        api_key=st.secrets["groq"]["api_key"]
    )
except Exception as e:
    st.error("❌ Error de configuración: Revisa los 'Secrets' en Streamlit Cloud.")
    st.stop()

# Inicializar historial de chat
if "messages" not in st.session_state:
    st.session_state.messages = []
    # Reiniciar historial limpio sin mensaje de sistema incrustado
    st.session_state.messages = [] 

# Mostrar mensajes anteriores
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Procesar mensaje del usuario
if prompt := st.chat_input("Escribe aquí..."):
    # 1. Mostrar mensaje usuario
    with st.chat_message("user"):
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    # 2. Generar respuesta
    with st.chat_message("assistant"):
        try:
            # Construimos los mensajes para la API (System + Historial)
            mensajes_api = [{"role": "system", "content": SYSTEM_PROMPT}] + st.session_state.messages
            
            stream = client.chat.completions.create(
                model="llama3-8b-8192",
                messages=mensajes_api,
                stream=True,
            )
            response = st.write_stream(stream)
            
            # 3. Guardar respuesta en historial
            st.session_state.messages.append({"role": "assistant", "content": response})
            
        except Exception as e:
            st.error(f"⚠️ Error en la IA: {str(e)}")
            # En caso de error, limpiamos el último mensaje del usuario para evitar bucles
            st.session_state.messages.pop() 