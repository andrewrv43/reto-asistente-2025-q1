import streamlit as st
import requests

# URL del servicio Flask
API_URL = "http://orchestate-service:5001/orchestrator"

st.title("💬 ChatGPT en Streamlit con Archivos y Markdown")

# Inicializar historial de mensajes
if "messages" not in st.session_state:
    st.session_state.messages = []

# Mostrar mensajes anteriores
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"], unsafe_allow_html=True)

# Crear un contenedor más visual para la entrada de usuario
with st.container():
    st.subheader("📩 Enviar un mensaje o subir un archivo")

    # Entrada del usuario
    user_input = st.text_area("✏️ Escribe tu mensaje:", key="user_input", height=100)

    # Subir archivo (opcional) con mejor presentación
    uploaded_file = st.file_uploader(
        "📂 Adjuntar documento (Opcional)", type=["pdf", "txt", "docx"]
    )

    # Mostrar nombre del archivo con un diseño atractivo si se ha subido algo
    if uploaded_file:
        st.success(f"✅ Archivo seleccionado: **{uploaded_file.name}**")

# Botón de envío solo habilitado si hay texto o archivo
send_button = st.button("🚀 Enviar", disabled=not (user_input or uploaded_file))

# Procesamiento del envío
if send_button:
    # Agregar mensaje del usuario con referencia al archivo si existe
    user_message = f"📤 **{user_input}**" if user_input else ""

    if uploaded_file:
        file_info = f"\n📎 **Archivo adjunto:** `{uploaded_file.name}`"
        user_message += file_info  # Agregar info del archivo al mensaje

    st.session_state.messages.append({"role": "user", "content": user_message})

    with st.chat_message("user"):
        st.markdown(user_message)

    # Preparar datos para enviar
    data = {"query": user_input}
    files = {"file": (uploaded_file.name, uploaded_file.getvalue())} if uploaded_file else None

    try:
        # Hacer la solicitud POST con multipart/form-data
        response = requests.post(API_URL, data=data, files=files)

        if response.status_code == 200:
            respuesta = "Vuelva a intentarlo por favor."

            res_json = response.json()
            print(res_json)
            if uploaded_file:
                res_json = res_json.get("response", {})
                if not isinstance(res_json, str):
                    entrada = res_json.get("entradas", None)
                    gastos = res_json.get("gastos", None)
                    visitas = res_json.get("visitas", None)
                    filename = res_json.get("filename", None)

                    if entrada is not None:
                        respuesta = f"""
🎯 **Resumen de Datos**
- 📉 **Gastos principales:** 
\n
{gastos}
\n
- 💰 **Ingresos principales:** 
\n
{entrada}
\n
- 👀 **Visitas destacadas:** 
\n
{visitas}
\n
- 📄 **Resumen:** `{filename}`
"""
                else:
                    respuesta = "Vuelva a intentar por favor"
            else:
                if not isinstance(res_json, str):
                    respuesta = res_json.get("response", None)
                    if respuesta:
                        if isinstance(respuesta, str):
                            respuesta=respuesta
                        else:    
                            respuesta =respuesta.get("response",None)
                    if respuesta is None:
                        respuesta = "No se pudo determinar la herramienta adecuada para la consulta."
                else:
                    respuesta = "Vuelva a intentar por favor"
            chat_response = respuesta
            #write chat_response into a text file
            with open("chat_response.txt", "w") as f:
                f.write(chat_response)
        else:
            chat_response = f"❌ **Error {response.status_code}:** {response.text}"

    except requests.exceptions.RequestException as e:
        chat_response = f"⚠️ **Error de conexión:** {e}"
    
    # Mostrar respuesta del asistente con Markdown bien formateado
    with st.chat_message("assistant"):
        print(chat_response)
        st.markdown(chat_response, unsafe_allow_html=True)
    # Guardar en el historial
    st.session_state.messages.append({"role": "assistant", "content": chat_response})

    # Resetear el archivo subido en la UI después del envío
    uploaded_file = None
