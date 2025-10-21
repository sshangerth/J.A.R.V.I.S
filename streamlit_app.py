import streamlit as st
from openai import OpenAI

# Titel und Beschreibung
st.title("💬 Chatbot mit eigenem Assistant")
st.write(
    "Dieser Chatbot verwendet deinen eigenen Assistant aus der OpenAI Assistants API."
)

# API-Key Eingabe
openai_api_key = st.text_input("OpenAI API Key", type="password")
if not openai_api_key:
    st.info("Bitte gib deinen OpenAI API Key ein, um fortzufahren.", icon="🗝️")
else:
    client = OpenAI(api_key=openai_api_key)

    # Assistant-ID (deine eigene)
    ASSISTANT_ID = "asst_u3LOqVkIQNe0KjxToHj8tKoG"

    # Thread-Objekt im Session-State speichern (damit der Chat erhalten bleibt)
    if "thread_id" not in st.session_state:
        thread = client.beta.threads.create()
        st.session_state.thread_id = thread.id

    # Chat-Verlauf anzeigen
    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Chat-Eingabe
    if prompt := st.chat_input("Schreib etwas..."):
        # Nutzer-Nachricht anzeigen und speichern
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Nutzer-Nachricht an Thread anhängen
        client.beta.threads.messages.create(
            thread_id=st.session_state.thread_id,
            role="user",
            content=prompt,
        )

        # Assistant-Run starten
        run = client.beta.threads.runs.create(
            thread_id=st.session_state.thread_id,
            assistant_id=ASSISTANT_ID,
        )

        # Warten bis Run fertig ist
        with st.chat_message("assistant"):
            with st.spinner("Denke nach..."):
                while True:
                    run_status = client.beta.threads.runs.retrieve(
                        thread_id=st.session_state.thread_id,
                        run_id=run.id,
                    )
                    if run_status.status == "completed":
                        break
                    elif run_status.status in ["failed", "cancelled"]:
                        st.error(f"Run status: {run_status.status}")
                        break

                # Antworten des Assistants abrufen
                messages = client.beta.threads.messages.list(
                    thread_id=st.session_state.thread_id
                )

                # Letzte Antwort finden (vom Assistant)
                last_msg = next(
                    (m for m in messages.data if m.role == "assistant"), None
                )
                if last_msg:
                    response = last_msg.content[0].text.value
                    st.markdown(response)
                    st.session_state.messages.append({"role": "assistant", "content": response})
