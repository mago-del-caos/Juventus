import streamlit as st
from openai import OpenAI
import streamlit.components.v1 as components
from audio_recorder_streamlit import audio_recorder

# CONFIGURACIÓN DE PÁGINA
st.set_page_config(
    page_title="🌻 Psique IJEM",
    page_icon="🌻",
    layout="centered",
    initial_sidebar_state="collapsed",
    menu_items={'Get Help': None, 'Report a bug': None, 'About': None}
)

# CSS ESENCIAL
css_psique = """
<style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    [data-testid="stDecoration"] {display: none;}
    .stApp {max-width: 100%; padding: 0;}
    .stDeployButton {display: none;}
    [data-testid="stToolbar"] {display: none;}
    [data-testid="stStatusWidget"] {display: none;}
</style>
"""
st.markdown(css_psique, unsafe_allow_html=True)

# PERSONALIDAD DE PSIQUE IJEM
SYSTEM_PROMPT = """Eres Psique IJEM, un asistente de inteligencia artificial especializado en primeros auxilios psicológicos, apoyo emocional y respaldo para adolescentes. Tu símbolo es un girasol, representando la búsqueda de la luz y la esperanza.

Tu objetivo principal es ofrecer contención emocional, escucha activa y orientación inicial a estudiantes que atraviesen momentos de crisis, estrés, ansiedad o problemas personales.

**REGLAS FUNDAMENTALES:**
1.  **Advertencia Inicial Obligatoria:** En tu primer mensaje de bienvenida, debes aclarar con total transparencia: "Hola, soy Psique IJEM. Es importante que sepas que soy un sistema de apoyo emocional y **no reemplazo a un psicólogo profesional ni a una evaluación clínica**. Mis orientaciones no tienen validez profesional médica. Si sientes que tu situación es grave o una emergencia, por favor acude con un especialista o adulto de confianza."
2.  **Tono:** Profesional pero profundamente empático, cálido y muy humano. Usa un lenguaje accesible para adolescentes.
3.  **Empatía:** Valida siempre las emociones del usuario antes de dar consejos. Nunca juzgues ni minimices lo que sienten.
4.  **Seguridad:** Si detectas indicadores de riesgo inminente (autolesiones, ideación suicida), insta amable pero firmemente a buscar ayuda profesional inmediata.

Responde de forma concisa pero cálida. Eres un compañero de apoyo en el Instituto Juventud (IJEM).
"""

# INTERFAZ PRINCIPAL
st.title("🌻 Psique IJEM")
st.caption("Primeros Auxilios Psicológicos y Apoyo Emocional")

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
    """Inyecta JavaScript para hablar. Se ejecuta al cargar el componente."""
    clean_text = text.replace("'", "\\'").replace('"', '\\"').replace("\n", " ")
    # Usamos un div contenedor para asegurar que el script se ejecute
    js_code = f"""
    <div id="audio-trigger"></div>
    <script>
        var text = "{clean_text}";
        function hablar() {{
            if ('speechSynthesis' in window) {{
                var utterance = new SpeechSynthesisUtterance(text);
                utterance.lang = 'es-MX';
                utterance.rate = 1.0;
                window.speechSynthesis.cancel(); // Detiene audios previos
                window.speechSynthesis.speak(utterance);
            }}
        }}
        // Esperamos un instante a que el navegador esté listo
        setTimeout(hablar, 100);
    </script>
    """
    components.html(js_code, height=0)

def transcribe_audio(audio_bytes):
    """Envía el audio grabado a Groq Whisper para convertirlo a texto."""
    try:
        with st.spinner("🎧 Transcribiendo..."):
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
    # Muestra mensaje del usuario
    with st.chat_message("user"):
        st.markdown(user_input)
    st.session_state.messages.append({"role": "user", "content": user_input})

    # Genera respuesta
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
            # Guardamos la respuesta en session_state para que el botón exterior pueda accederla
            st.session_state.last_response = response
        except Exception as e:
            st.error(f"⚠️ Error: {str(e)}")

# --- INTERFAZ DE USUARIO ---

# 1. Entrada de Voz (Grabación)
st.markdown("#### 🎤 Habla con Psique")
audio_bytes = audio_recorder(energy_threshold=0.5, pause_threshold=1.0, icon_size="2x")

if audio_bytes:
    texto_voz = transcribe_audio(audio_bytes)
    if texto_voz:
        st.success(f"📝 Dijiste: {texto_voz}")
        procesar_respuesta(texto_voz)

# 2. Entrada de Texto
st.markdown("---")
if prompt := st.chat_input("Escribe cómo te sientes..."):
    procesar_respuesta(prompt)

# 3. BOTÓN DE ESCUCHA (FUERA DEL FLUJO DE GENERERACIÓN)
# Este bloque se ejecuta siempre que haya una respuesta previa, permitiendo reproducirla sin regenerar.
if "last_response" in st.session_state:
    # Creamos un contenedor para el botón al final de la pantalla
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🔊 Escuchar última respuesta", use_container_width=True):
            speak_js(st.session_state.last_response)
