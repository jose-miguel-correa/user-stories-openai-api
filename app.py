import streamlit as st
from openai import OpenAI
import os
from dotenv import load_dotenv

class UserStoryAssistant:
    def __init__(self):
        # Load environment variables
        load_dotenv()
        self.api_key = os.getenv("openai_api_key")
        self.client = OpenAI(api_key=self.api_key)
        self.assistant_id = "asst_X0m1o5VijT4CglzNxpe5jwfN"

        # Initialize session state for responses if not already present
        if "responses" not in st.session_state:
            st.session_state.responses = []

        # Display logo
        self.display_logo()

    def display_logo(self):
        logo_url = 'logo3.jpg'
        st.image(logo_url, width=200)

    def clear_responses(self):
        if st.button("Limpiar Respuestas"):
            st.session_state.clear()

    def user_input(self):
        self.content = st.text_input('Escribe tu solicitud al asistente (Por ejemplo, "Crear perfil AWS EC2" o "Crear botón de login de usuario")')

    def generate_user_story(self):
        if st.button("Generar Historia de Usuario"):
            if self.content.strip() == "":
                st.error("Por favor, escribe el texto que necesitas.")
            else:
                try:
                    thread = self.client.beta.threads.create(
                        messages=[
                            {
                                "role": "user",
                                "content": self.content,
                            }
                        ]
                    )

                    run = self.client.beta.threads.runs.create_and_poll(
                        thread_id=thread.id, assistant_id=self.assistant_id
                    )

                    messages = list(self.client.beta.threads.messages.list(thread_id=thread.id, run_id=run.id))

                    if messages:
                        try:
                            message_content = messages[0].content[0].text
                            st.session_state.responses.append(message_content.value)
                        except IndexError:
                            st.error("No content found in the first message. Please verify the response structure.")
                    else:
                        st.error("No messages were retrieved. Please check the query or the assistant's configuration.")
                except Exception as e:
                    st.error(f"An error occurred: {str(e)}")


    def display_responses(self):
        if st.session_state.responses:
            st.write("Respuestas del Asistente:")
            for response in st.session_state.responses:
                st.write(response)

    def suggest_modification(self):
        suggestion = st.text_input('Sugerencia de modificación (escribe un cambio que deseas realizar en la respuesta anterior)')
        if st.button("Genera Nueva Historia de Usuario"):
            if not suggestion.strip():
                st.error("Por favor, escribe una sugerencia para modificar la respuesta anterior.")
            elif not st.session_state.responses:
                st.error("No hay respuestas anteriores para modificar.")
            else:
                last_response = st.session_state.responses[-1]
                mod_thread = self.client.beta.threads.create(
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

                mod_run = self.client.beta.threads.runs.create_and_poll(
                    thread_id=mod_thread.id, assistant_id=self.assistant_id
                )

                mod_messages = list(self.client.beta.threads.messages.list(thread_id=mod_thread.id, run_id=mod_run.id))

                if mod_messages:
                    mod_message_content = mod_messages[0].content[0].text
                    st.session_state.responses.append(mod_message_content.value)
                    st.write("Respuesta Modificada:")
                    st.write(mod_message_content.value)
                else:
                    st.error("No se pudo recuperar la respuesta modificada.")

# Main function to run the app
def main():
    assistant = UserStoryAssistant()
    assistant.clear_responses()
    assistant.user_input()
    assistant.generate_user_story()
    assistant.display_responses()
    assistant.suggest_modification()

if __name__ == "__main__":
    main()
