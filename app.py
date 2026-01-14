import streamlit as st
from langchain_core.messages import HumanMessage, AIMessage
from research_assistant.graph.workflow import create_graph
import uuid

# Page Config
st.set_page_config(page_title="Agentic Research Assistant", layout="wide")
st.title("🕵️‍♂️ Multi-Agent Research Assistant")

# Initialize Session State
if "thread_id" not in st.session_state:
    st.session_state.thread_id = str(uuid.uuid4())

if "messages" not in st.session_state:
    st.session_state.messages = []

# Initialize Graph
if "graph" not in st.session_state:
    st.session_state.graph = create_graph()

# Sidebar
with st.sidebar:
    st.header("System Status")
    st.markdown("Agents Active:")
    st.markdown("- ✅ Clarity Agent")
    st.markdown("- ✅ Research Agent")
    st.markdown("- ✅ Validator Agent")
    st.markdown("- ✅ Synthesis Agent")
    if st.button("Clear Chat"):
        st.session_state.messages = []
        st.session_state.thread_id = str(uuid.uuid4())
        st.rerun()

# Display Chat History
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Chat Input
if prompt := st.chat_input("Ask about a company (e.g., 'Tell me about Apple')"):
    # Add user message to history
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Prepare configuration for graph run
    config = {"configurable": {"thread_id": st.session_state.thread_id}, "recursion_limit": 50}

    # Run the graph
    with st.spinner("Agents are working..."):
        # Pass the full chat history to the graph
        from langchain_core.messages import HumanMessage, AIMessage
        inputs = {"messages": [
            HumanMessage(content=msg["content"]) if msg["role"] == "user" else AIMessage(content=msg["content"])
            for msg in st.session_state.messages
        ]}

        final_state = None
        try:
            result = st.session_state.graph.invoke(inputs, config=config)
            final_state = result

            if final_state["clarity_status"] == "needs_clarification":
                response_content = "I'm not sure which company you're referring to. Could you please specify the company name?"
                st.session_state.messages.append({"role": "assistant", "content": response_content})
                with st.chat_message("assistant"):
                    st.markdown(response_content)

            elif "summary" in final_state:
                response_content = final_state["summary"]
                st.session_state.messages.append({"role": "assistant", "content": response_content})
                with st.chat_message("assistant"):
                    st.markdown(response_content)

            else:
                response_content = "Process completed but no summary generated."
                st.session_state.messages.append({"role": "assistant", "content": response_content})
                with st.chat_message("assistant"):
                    st.markdown(response_content)

        except Exception as e:
            st.error(f"An error occurred: {e}")

# Debugging State View (Optional)
with st.expander("View Agent State"):
    if "graph" in st.session_state:
        try:
            current_state = st.session_state.graph.get_state({"configurable": {"thread_id": st.session_state.thread_id}})
            st.write(current_state.values)
        except:
            st.write("No active state.")
