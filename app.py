import streamlit as st
from openai import OpenAI

# CONFIGURACIÓN DE LA PÁGINA
st.set_page_config(page_title="Mi IA Personal", page_icon="🤖")

# TÍTULO
st.title("🤖 Mi Asistente Personal")

# --- AQUÍ PERSONALIZAS TU IA ---
PERSONALIDAD = """
Eres 'Alex', un asistente experto en productividad y organización.
Tu tono es motivador, breve y usas emojis.
Si te preguntan algo que no sabes, admite que no lo sabes.
"""
# -------------------------------

# BARRA LATERAL PARA CONFIGURACIÓN (OCULTAR API KEY)
with st.sidebar:
    st.header("Configuración")
    api_key = st.text_input("Tu API Key", type="password")
    st.markdown("---")
    st.write("Hecho con ❤️ desde el móvil")

# INICIALIZAR HISTORIAL DE CHAT
if "messages" not in st.session_state:
    st.session_state.messages = []
    # Añadir la personalidad al inicio
    st.session_state.messages.append({"role": "system", "content": PERSONALIDAD})

# MOSTRAR MENSAJES ANTERIORES
for message in st.session_state.messages:
    if message["role"] != "system": # No mostrar el prompt del sistema
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

# PROCESAR MENSAJE DEL USUARIO
if prompt := st.chat_input("Escribe aquí..."):
    if not api_key:
        st.info("Por favor añade tu API Key en la barra lateral para empezar.")
        st.stop()

    # Mostrar mensaje del usuario
    with st.chat_message("user"):
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    # GENERAR RESPUESTA DE LA IA
    with st.chat_message("assistant"):
        client = OpenAI(
            base_url="https://api.groq.com/openai/v1", # Usando Groq
            api_key=api_key
        )
        stream = client.chat.completions.create(
            model="llama3-8b-8192", # Modelo rápido
            messages=st.session_state.messages,
            stream=True,
        )
        response = st.write_stream(stream)
    
    st.session_state.messages.append({"role": "assistant", "content": response})
