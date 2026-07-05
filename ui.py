import streamlit as st
agent = ResearchAgent()
from core.research_agent import ResearchAgent

st.set_page_config(
    page_title="Research Agent",
    page_icon="🔎",
    layout="wide"
)

st.title("🔎 Research Agent")

# Store conversation history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display previous messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
prompt = st.chat_input("Ask me anything...")

if prompt:
    # Display user message
    st.session_state.messages.append(
        {"role": "user", "content": prompt}
    )

    with st.chat_message("user"):
        st.markdown(prompt)

    # Generate response
    with st.chat_message("assistant"):

        status = st.empty()
        status.info("🔍 Searching the web...")

        try:
            response = agent.run(prompt)

            status.success("✅ Research complete.")
            st.markdown(response)

        except Exception as e:
            response = f"Error:\n\n{e}"
            status.error("❌ Research failed.")
            st.code(str(e))

    # Save assistant response
    st.session_state.messages.append(
        {"role": "assistant", "content": response}
    )