import streamlit as st
from importlib import import_module

# Mapping of script names to their file names
AGENT_SCRIPTS = {
    "Lang Agent - [GMAIL - Make Game - Add - Wiki]": "lang",
    "Lang React - [Make game - Add - Wiki]": "lang_react",
    "Lang No Gmail (True Agent) - [Make-game - Add - Wiki]": "lang_no_gmail",
}

st.title("Unified Agent Chat UI")

# Sidebar for selecting an agent script
selected_script = st.sidebar.selectbox("Select Agent Script", list(AGENT_SCRIPTS.keys()))

# Import the selected module dynamically
script_module = __import__(AGENT_SCRIPTS[selected_script])

# Initialize chat history if not already initialized
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

# Input box for the user
if prompt := st.chat_input(f"Ask something to {selected_script}"):
    # Display user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

    # Call the agent's response function
    if hasattr(script_module, 'chat'):
        response = script_module.chat(prompt)
    else:
        response = "Selected script does not have a chat function."

    # Display agent response
    st.session_state.messages.append({"role": "assistant", "content": response})
    with st.chat_message("assistant"):
        st.write(response)
