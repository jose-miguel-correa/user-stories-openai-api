import streamlit as st
from openai import OpenAI
from parse_text import textProcess
import requests
from requests.auth import HTTPBasicAuth
import json

# Jira API endpoint to create an issue (task)
url = st.secrets['URL']
#url = "https://siigroup-josecorrea.atlassian.net/rest/api/2/issue"
email = st.secrets['EMAIL']
jira_api = st.secrets['JIRA_API']
# Authentication
#auth = HTTPBasicAuth("jose.correa@siigroup.cl", "ATATT3xFfGF0keQkAPtE-S_bF6JiFh9E_S6p6DqM00ZjprNlGyiGsZPHJ5U0aa-luG1Fywsj0e4rPM8zW3lIvAh92ExT0KnACPgG0rXu7F7Kgaas036VxYnXKLPnXzURdp1HVjnbpVaoa03o9YO_tUk9aVopeFuwBK6hD0rayOcmvpx-GmlY11M=A1254279")  # Replace with your API token
auth = HTTPBasicAuth(email, jira_api)

# Headers
headers = {
    "Accept": "application/json",
    "Content-Type": "application/json"
}

api_key = st.secrets["API_KEY"]
#api_key = "sk-B61TXWnjCOjXr9ibIm_76-_IHMkTsbhjXNFFBEUVPGT3BlbkFJk8r_k98Nk2B77q38kpzs-gQkcc8fJFrUcvMM-pUjAA"
client = OpenAI(api_key=api_key)


# Assistant ID
assistant_id = st.secrets["ASSISTANT_ID"]
#assistant_id = "asst_X0m1o5VijT4CglzNxpe5jwfN"

# Display logo
logo_url = 'logo.gif'
st.image(logo_url, width=100)

st.title("Asistente de Historias de Usuario")

# Reset the session when the button is clicked
if st.button("Limpiar Entorno"):
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

# Ensure that the session_state has a responses entry
if 'responses' not in st.session_state:
    st.session_state.responses = []

# Ensure mod_message_content is in session state
if 'mod_message_content' not in st.session_state:
    st.session_state.mod_message_content = None

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

        # Display the modified response and store it in session state
        if mod_messages:
            st.session_state.mod_message_content = mod_messages[0].content[0].text.value
            st.session_state.responses.append(st.session_state.mod_message_content)
            st.write("Respuesta Modificada:")
            st.write(st.session_state.mod_message_content)            
        else:
            st.error("No se pudo recuperar la respuesta modificada.")

if st.session_state.mod_message_content:
    if st.button("Enviar a Jira"):
        texto = st.session_state.mod_message_content  # Directly assign the content
        #print(st.session_state.mod_message_content)
        get_text_splitted = textProcess()
        caracteristica, contexto, scenarios = get_text_splitted.parse_input(texto)
        # Main task payload (the "Característica" in Gherkin)
        task_payload = json.dumps({
            "fields": {
                "project": {
                    "key": "US2"  # Your project key
                },
                "summary": caracteristica,  # Main task (User Story)
                "description": contexto,  # Gherkin's context
                "issuetype": {
                    "name": "Story"  # Issue type: Task for the user story
                }
            }
        })

        # Create the main task (user story)
        task_response = requests.request(
            "POST",
            url,
            headers=headers,
            auth=auth,
            data=task_payload
        )

        # Print the response for the main task
        print(f"Status Code: {task_response.status_code}")
        main_task_data = task_response.json()
        print(main_task_data)

        task_key = main_task_data["key"]  # Example: US2-123

        subtask_payloads = get_text_splitted.generate_subtask_payloads(scenarios, task_key)

        # Get the task key to create subtasks under it

        # Jira API endpoint to create subtasks
        subtask_url = "https://siigroup-josecorrea.atlassian.net/rest/api/2/issue"

        # Loop through each subtask and create them in Jira
        for subtask_payload in subtask_payloads:
            subtask_response = requests.request(
                "POST",
                subtask_url,
                headers=headers,
                auth=auth,
                data=json.dumps(subtask_payload)
            )
            print(f"Status Code: {subtask_response.status_code}")
            print(subtask_response.json())
    
        st.succes("Historia de Usuario creada em Jira")
