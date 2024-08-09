import streamlit as st
from backend import create_agent, create_retriever, create_prompt, DocType

st.title("Agent Management System")

# Initialize session state for storing agents and info
if 'agents' not in st.session_state:
    st.session_state.agents = []

if 'info' not in st.session_state:
    class Bruh:
        agents = []
        built = False
        output = ""
        input_text = ""

    st.session_state.info = Bruh()

# Function to add a new agent
def add_agent():
    st.session_state.agents.append({
        'name': '',
        'prompt': '',
        'RAG_link': '',
        'RAG_name': '',
        'RAG_prompt': '',
    })

# Function to remove an agent
def remove_agent(index):
    st.session_state.agents.pop(index)

# Section to add/remove agents
st.header("Agents")

# Add new agent button
if st.button("Add Agent"):
    add_agent()

# Display current agents
for i, agent in enumerate(st.session_state.agents):
    st.subheader(f"Agent {i + 1}")
    agent['name'] = st.text_input(f"Name {i + 1}", value=agent['name'], key=f"name_{i}")
    agent['prompt'] = st.text_area(f"String Prompt {i + 1}", value=agent['prompt'], key=f"prompt_{i}")
    agent['RAG_link'] = st.text_input(f"RAG {i + 1}", value=agent['RAG_link'], key=f"RAG_link_{i}")
    agent['RAG_name'] = st.text_input(f"RAG name {i + 1}", value=agent['RAG_name'], key=f"RAG_name_{i}")
    agent['RAG_prompt'] = st.text_area(f"RAG Explanation {i + 1}", value=agent['RAG_prompt'], key=f"RAG_prompt_{i}")

    # Remove agent button
    if st.button(f"Remove Agent {i + 1}", key=f"remove_{i}"):
        remove_agent(i)
        st.experimental_rerun()

# Another text field section
st.header("Input")
input_text = st.text_area("Enter input here")

info = st.session_state.info

if st.button("Build"):
    info.agents.clear()
    info.agents = [create_agent(
        name=agent["name"],
        prompt=create_prompt(agent["prompt"]),
        RAG=create_retriever(
            path=agent["RAG_link"],
            type=DocType.WEB,
            name=agent["RAG_name"],
            description_prompt=agent["RAG_prompt"]
        )
    ) for agent in st.session_state.agents]
    info.built = True
    info.output = ""  # Reset output when rebuilding
    info.input_text = input_text
    st.session_state.info = info  # Update session state

def process():
    for i, agent in enumerate(info.agents):
        print(info.input_text)
        curr_output = f"{st.session_state.agents[i]['name']} : {agent.invoke({'input': info.input_text}, {'configurable': {'session_id': '1'}}).get('output', info.input_text)}"
        info.output += curr_output + "\n"  # Add a newline for better readability
        info.input_text = info.output
    return info.input_text, info.output

if info.built and st.button("Iterate"):
    process()
    st.write(info.input_text)


# Display stored agents and notes for debugging purposes
# st.write("Current Agents:", st.session_state.agents)
# st.write("Additional Notes:", input)
