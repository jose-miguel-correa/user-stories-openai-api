import streamlit as st
from openai import OpenAI

api_key = st.secrets["API_KEY"]
client = OpenAI(api_key=api_key)

# Assistant ID
assistant_id = st.secrets["ASSISTANT_ID"]

# Display logo
logo_url = 'logo.gif'
st.image(logo_url, width=100)

st.title("Asistente de Historias de Usuario")

# Reset the session when the button is clicked
if st.button("Limpiar Respuestas"):
    st.session_state.clear()

# Step 1: User provides a content query
if "user_input" not in st.session_state:
    st.session_state.user_input = ""  # Initialize user input in session state

# Create a text input for user query
def submit_user_input():
    st.session_state.user_input = st.session_state.widget  # Store the input in session state
    st.session_state.widget = ""  # Clear the input field

# First text input widget
st.text_input('Escribe tu solicitud al asistente (Por ejemplo, "Crear perfil AWS EC2" o "Crear botón de login de usuario")',
              key='widget',  # Use a key to track the input
              on_change=submit_user_input)  # Call submit function when input changes

# Display the current user input
st.info(f"Solicitud ingresada: {st.session_state.user_input}")

# Initialize session state for responses if not already present
if "responses" not in st.session_state:
    st.session_state.responses = []

# Generate user story when the button is clicked
if st.button("Generar Historia de Usuario"):
    content = st.session_state.user_input  # Get the user input from session state
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
                message_content = messages[0].content[0].text.value
                st.session_state.responses.append(message_content)  # Append response
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
if "suggestion" not in st.session_state:
    st.session_state.suggestion = ""  # Initialize suggestion input in session state

# Function to handle suggestion submission
def submit_suggestion():
    st.session_state.suggestion = st.session_state.suggestion_widget  # Store the suggestion in session state
    st.session_state.suggestion_widget = ""  # Clear the suggestion input field

# Suggestion input widget
st.text_input('Sugerencia de modificación (escribe un cambio que deseas realizar en la respuesta anterior)',
              key='suggestion_widget',  # Use a key to track the suggestion input
              on_change=submit_suggestion)  # Call submit function when input changes

# Display the current suggestion input
st.info(f"Sugerencia ingresada: {st.session_state.suggestion}")

if st.button("Genera Nueva Historia de Usuario"):
    last_response = st.session_state.responses[-1] if st.session_state.responses else ""
    if not st.session_state.suggestion.strip():
        st.error("Por favor, escribe una sugerencia para modificar la respuesta anterior.")
    elif not last_response:
        st.error("No hay respuestas anteriores para modificar.")
    else:
        mod_thread = client.beta.threads.create(
            messages=[
                {
                    "role": "user",
                    "content": f"""
                        Modifica la historia de usuario manteniendo todas las modificaciones previas: {last_response}.
                        Agrega el siguiente cambio: {st.session_state.suggestion}. 
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
            mod_message_content = mod_messages[0].content[0].text.value
            st.session_state.responses.append(mod_message_content)
            st.write("Respuesta Modificada:")
            st.write(mod_message_content)
        else:
            st.error("No se pudo recuperar la respuesta modificada.")
