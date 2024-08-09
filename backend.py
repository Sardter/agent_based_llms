from enum import Enum

from langchain_community.vectorstores import Chroma
from langchain_cohere import CohereEmbeddings
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.document_loaders import WebBaseLoader, UnstructuredPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.tools.retriever import create_retriever_tool
from langchain.tools import Tool
from langchain_core.prompts import PromptTemplate
from langchain.agents import AgentExecutor
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain.agents import create_tool_calling_agent
from langchain import hub
from langchain.prompts.chat import SystemMessagePromptTemplate

embedings = CohereEmbeddings()

class DocType(Enum):
    PDF = 0
    WEB = 1

def create_retriever(path: str, type: DocType, name: str, description_prompt: str):
    match type:
        case DocType.PDF:
            loader = UnstructuredPDFLoader(path)
        case DocType.WEB:
            loader = WebBaseLoader(path)
        case _:
            raise Exception(f"Type not implemented: {type}")
    docs = loader.load()
    documents = RecursiveCharacterTextSplitter(
        chunk_size=1000, chunk_overlap=200
    ).split_documents(docs)
    db = Chroma.from_documents(documents, embedings).as_retriever()
    return create_retriever_tool(
        db,
        name,
        description_prompt,
    )
    
def create_agent(name: str, prompt: PromptTemplate, RAG: Tool | None):
    tools = [RAG] if RAG is not None else []
    llm = ChatGoogleGenerativeAI(model="gemini-1.5-pro-latest")
    message_history = ChatMessageHistory()
    agent = create_tool_calling_agent(llm.bind_tools(tools), tools, prompt)
    agent.name = name
    agent_executor = AgentExecutor(name=name, agent=agent, tools=tools, verbose=True)
    return RunnableWithMessageHistory(
        agent_executor,
        # This is needed because in most real world scenarios, a session id is needed
        # It isn't really used here because we are using a simple in memory ChatMessageHistory
        lambda session_id: message_history,
        input_messages_key="input",
        history_messages_key="chat_history",
    )
    
def process(input: str, agents: list[RunnableWithMessageHistory]):
    output = ""
    for agent in agents:
        print("here")
        curr_output =  f"{agent.name} :{agent.invoke({'input': input}, {'configurable': {'session_id': '1'}}).get('output', input)}"
        print(curr_output)
        output += curr_output
        input = output
    return input, output


def create_prompt(s: str) -> PromptTemplate:
    prompt = hub.pull("hwchase17/openai-functions-agent")
    prompt.messages[0] = SystemMessagePromptTemplate.from_template(s)
    return prompt