import streamlit as st
from openai import OpenAI


# Conversation buffer helper (keep last 2 Q&A pairs)
def keep_last_n_messages(messages, n=2):
    system_msgs = [m for m in messages if m["role"] == "assistant" and "What question can I help with?" in m["content"]]
    other_msgs = [m for m in messages if m not in system_msgs]
    return system_msgs + other_msgs[-2 * n:]


def app():
    # Title
    st.title("📄 LAB 3 – Chatbot")

    # Load API key
    api_key = st.secrets["openai"]["api_key"]

    # Model selection
    openAI_model = st.sidebar.selectbox("Select Model", ("mini", "regular"))
    model_to_use = "gpt-4o-mini" if openAI_model == "mini" else "gpt-4o"

    # Create OpenAI client
    if "client" not in st.session_state:
        st.session_state.client = OpenAI(api_key=api_key)

    client = st.session_state.client

    # Init session state
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "assistant", "content": "What question can I help with?"}
        ]
    if "awaiting_more_info" not in st.session_state:
        st.session_state.awaiting_more_info = False

    # Show past messages
    for msg in st.session_state.messages:
        st.chat_message(msg["role"]).write(msg["content"])

    # Chat loop
    if prompt := st.chat_input("Type here..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Case 1: User is in "more info" loop
        if st.session_state.awaiting_more_info:
            if prompt.strip().lower() in ["yes", "y", "sure", "ok"]:
                messages_for_llm = keep_last_n_messages(
                    st.session_state.messages
                    + [{"role": "assistant", "content": "Give a longer, more detailed explanation that a 10-year-old can understand."}],
                    n=2,
                )
                completion = client.chat.completions.create(
                    model=model_to_use,
                    messages=messages_for_llm
                )
                response = completion.choices[0].message.content

                with st.chat_message("assistant"):
                    st.write(response)
                st.session_state.messages.append({"role": "assistant", "content": response})

                # Ask again
                followup = "DO YOU WANT MORE INFO"
                with st.chat_message("assistant"):
                    st.write(followup)
                st.session_state.messages.append({"role": "assistant", "content": followup})

            elif prompt.strip().lower() in ["no", "n", "nope"]:
                reset_msg = "What question can I help with?"
                with st.chat_message("assistant"):
                    st.write(reset_msg)
                st.session_state.messages.append({"role": "assistant", "content": reset_msg})
                st.session_state.awaiting_more_info = False

        # Case 2: Normal Q&A
        else:
            messages_for_llm = keep_last_n_messages(
                st.session_state.messages
                + [{"role": "assistant", "content": "Answer the user's question so that a 10-year-old can understand."}],
                n=2,
            )

            completion = client.chat.completions.create(
                model=model_to_use,
                messages=messages_for_llm
            )
            response = completion.choices[0].message.content

            with st.chat_message("assistant"):
                st.write(response)
            st.session_state.messages.append({"role": "assistant", "content": response})

            # Always enter info loop
            followup = "DO YOU WANT MORE INFO"
            with st.chat_message("assistant"):
                st.write(followup)
            st.session_state.messages.append({"role": "assistant", "content": followup})
            st.session_state.awaiting_more_info = True
