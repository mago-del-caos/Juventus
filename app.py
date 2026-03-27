import streamlit as st
from openai import OpenAI
import streamlit.components.v1 as components
from audio_recorder_streamlit import audio_recorder
import base64

# CONFIGURACIÓN DE PÁGINA
st.set_page_config(
    page_title="🦅Juventus🦅",
    page_icon="🦅",
    layout="centered",
    initial_sidebar_state="collapsed",
    menu_items={'Get Help': None, 'Report a bug': None, 'About': None}
)

# CSS ESENCIAL
css_juventus = """
<style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    [data-testid="stDecoration"] {display: none;}
    .stApp {max-width: 100%; padding: 0;}
    .stDeployButton {display: none;}
    [data-testid="stToolbar"] {display: none;}
    [data-testid="stStatusWidget"] {display: none;}
    /* Estilo para el botón de grabación */
    button[kind="header"] {display: none;}
</style>
"""
st.markdown(css_juventus, unsafe_allow_html=True)

# PERSONALIDAD DE JUVENTUS
SYSTEM_PROMPT = """Eres Juventus, una IA de apoyo inspirada en el Instituto Juventud del Estado de México, A.C. (IJEM), institución fundada y dirigida por Misioneros Josefinos con más de 50 años de trayectoria.
[Tu prompt completo aquí...]""" # Acorta el prompt si es muy largo para este ejemplo

# INTERFAZ PRINCIPAL
st.title("🦅 Juventus • Asistente Josefino 🦅")
st.caption("Hacer siempre y en todo lo mejor")

# CONEXIÓN CON GROQ
try:
    client = OpenAI(
        base_url="https://api.groq.com/openai/v1",
        api_key=st.secrets["groq"]["api_key"]
    )
except Exception:
    st.error("❌ Error de configuración: Revisa los 'Secrets' en Streamlit Cloud.")
    st.stop()

# --- FUNCIONES DE AUDIO WEB ---

def speak_js(text):
    """Usa JavaScript para que el navegador hable (Text-to-Speech)."""
    clean_text = text.replace("'", "\\'").replace('"', '\\"').replace("\n", " ")
    js_code = f"""
    <script>
        if ('speechSynthesis' in window) {{
            var utterance = new SpeechSynthesisUtterance("{clean_text}");
            utterance.lang = 'es-MX';
            utterance.rate = 1.0;
            window.speechSynthesis.cancel();
            window.speechSynthesis.speak(utterance);
        }}
    </script>
    """
    components.html(js_code, height=0)

def transcribe_audio(audio_bytes):
    """Envía el audio grabado a Groq Whisper para convertirlo a texto."""
    try:
        with st.spinner("🎧 Transcribiendo..."):
            # Groq requiere que el archivo tenga un nombre
            transcript = client.audio.transcriptions.create(
                file=("input.wav", audio_bytes),
                model="whisper-large-v3",
                language="es",
                response_format="text"
            )
            return transcript
    except Exception as e:
        st.error(f"Error en transcripción: {e}")
        return None

# HISTORIAL DE CHAT
if "messages" not in st.session_state:
    st.session_state.messages = []

# Mostrar historial
for message in st.session_state.messages:
    if message["role"] != "system":
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

# FUNCIÓN PARA PROCESAR RESPUESTA
def procesar_respuesta(user_input):
    with st.chat_message("user"):
        st.markdown(user_input)
    st.session_state.messages.append({"role": "user", "content": user_input})

    with st.chat_message("assistant"):
        try:
            mensajes_api = [{"role": "system", "content": SYSTEM_PROMPT}] + st.session_state.messages
            stream = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=mensajes_api,
                stream=True,
            )
            response = st.write_stream(stream)
            st.session_state.messages.append({"role": "assistant", "content": response})
            speak_js(response) # HABLAR
        except Exception as e:
            st.error(f"⚠️ Error: {str(e)}")

# --- INTERFAZ DE USUARIO ---

# 1. Entrada de Voz (Grabación)
st.markdown("#### 🎤 Habla con Juventus")
audio_bytes = audio_recorder(energy_threshold=0.5, pause_threshold=1.0, icon_size="2x")

if audio_bytes:
    # El usuario grabó algo, lo transcribimos
    texto_voz = transcribe_audio(audio_bytes)
    if texto_voz:
        st.success(f"📝 Dijiste: {texto_voz}")
        procesar_respuesta(texto_voz)

# 2. Entrada de Texto
st.markdown("---")
if prompt := st.chat_input("O escribe tu pregunta aquí..."):
    procesar_respuesta(prompt)
