import streamlit as st
from openai import OpenAI


# Display logo
logo_url = 'logo3.jpg'
st.image(logo_url, width=100)

api_key = st.secrets["API_KEY"]
client = OpenAI(api_key=api_key)

# Assistant ID
assistant_id = st.secrets["ASSISTANT_ID"]

# Reset the session when the button is clicked
if st.button("Limpiar Respuestas"):
    st.session_state.clear()
    st.session_state.user_input = ""

st.title("Asistente de Historias de Usuario")

# Step 1: User provides a content query
content = st.text_input('Escribe tu solicitud al asistente (Por ejemplo, "Crear perfil AWS EC2" o "Crear botón de login de usuario")')

# Initialize session state for responses if not already present
if "responses" not in st.session_state:
    st.session_state.responses = []

# Step 2: Generate a user story when the button is clicked
if st.button("Generar Historia de Usuario"):
    if content.strip() == "":
        st.error("Por favor, escribe el texto que necesitas.")
    else:
        # Create a thread with the user's query
        thread = client.beta.threads.create(
            messages=[
                {
                    "role": "user",
                    "content": content,
                }
            ]
        )

        # Run until it's in a terminal state
        run = client.beta.threads.runs.create_and_poll(
            thread_id=thread.id, assistant_id=assistant_id
        )

        # Retrieve the response messages
        messages = list(client.beta.threads.messages.list(thread_id=thread.id, run_id=run.id))

        # Extract the response and append to session state
        if messages:
            try:
                message_content = messages[0].content[0].text
                st.session_state.responses.append(message_content.value)
            except IndexError:
                st.error("No content found in the first message. Please verify the response structure.")
        else:
            st.error("No messages were retrieved. Please check the query or the assistant's configuration.")

# Display all responses generated so far
if st.session_state.responses:
    st.write("Respuestas del Asistente:")
    for response in st.session_state.responses:
        st.write(response)

# Step 3: Allow user to suggest modifications
suggestion = st.text_input('Sugerencia de modificación (escribe un cambio que deseas realizar en la respuesta anterior)')

if st.button("Genera Nueva Historia de Usuario"):
    if not suggestion.strip():
        st.error("Por favor, escribe una sugerencia para modificar la respuesta anterior.")
    elif not st.session_state.responses:
        st.error("No hay respuestas anteriores para modificar.")
    else:
        last_response = st.session_state.responses[-1]
        mod_thread = client.beta.threads.create(
            messages=[
                {
                    "role": "user",
                    "content": f"""
                        Modifica la historia de usuario manteniendo todas las modificaciones previas: {last_response}.
                        Agrega el siguiente cambio: {suggestion}. 
                        No elimines ningún escenario previamente agregado, a menos que te lo indique explícitamente.
                    """,
                }
            ]
        )

        # Run and poll
        mod_run = client.beta.threads.runs.create_and_poll(
            thread_id=mod_thread.id, assistant_id=assistant_id
        )

        # Retrieve the modified response
        mod_messages = list(client.beta.threads.messages.list(thread_id=mod_thread.id, run_id=mod_run.id))

        # Display the modified response and append to session state
        if mod_messages:
            mod_message_content = mod_messages[0].content[0].text
            st.session_state.responses.append(mod_message_content.value)
            st.write("Respuesta Modificada:")
            st.write(mod_message_content.value)
        else:
            st.error("No se pudo recuperar la respuesta modificada.")
