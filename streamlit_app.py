import time
import streamlit as st
from openai import OpenAI

# Titel und Beschreibung
st.title("💬 Chatbot (eigener Assistant)")
st.write(
    "Dieser Chatbot verwendet deinen eigenen Assistant aus der OpenAI Assistants API."
)

# API-Key Eingabe
openai_api_key = st.text_input("OpenAI API Key", type="password")

if not openai_api_key:
    st.info("Bitte gib deinen OpenAI API Key ein, um fortzufahren.", icon="🗝️")
else:
    # OpenAI Client
    client = OpenAI(api_key=openai_api_key)

    # Deine Assistant-ID
    ASSISTANT_ID = "asst_u3LOqVkIQNe0KjxToHj8tKoG"

    # Thread speichern (damit Verlauf bleibt)
    if "thread_id" not in st.session_state:
        thread = client.beta.threads.create()
        st.session_state.thread_id = thread.id

    # Bisherige Nachrichten anzeigen
    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Eingabe
    if prompt := st.chat_input("Was möchtest du fragen?"):
        # Nachricht speichern & anzeigen
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Nachricht in Thread einfügen
        client.beta.threads.messages.create(
            thread_id=st.session_state.thread_id,
            role="user",
            content=prompt,
        )

        # Run starten
        run = client.beta.threads.runs.create(
            thread_id=st.session_state.thread_id,
            assistant_id=ASSISTANT_ID,
        )

        # Auf Antwort warten
        with st.chat_message("assistant"):
            with st.spinner("Denke nach..."):
                while True:
                    run_status = client.beta.threads.runs.retrieve(
                        thread_id=st.session_state.thread_id,
                        run_id=run.id,
                    )
                    if run_status.status == "completed":
                        break
                    if run_status.status in ["failed", "cancelled", "expired"]:
                        st.error(f"Run status: {run_status.status}")
                        st.stop()
                    time.sleep(0.5)

                # Antwort abrufen
                messages = client.beta.threads.messages.list(
                    thread_id=st.session_state.thread_id
                )
                last_msg = next((m for m in messages.data if m.role == "assistant"), None)

                if last_msg and last_msg.content:
                    response = last_msg.content[0].text.value
                else:
                    response = "(keine Antwort erhalten)"

                st.markdown(response)
                st.session_state.messages.append(
                    {"role": "assistant", "content": response}
                )
