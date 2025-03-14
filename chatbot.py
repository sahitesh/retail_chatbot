import streamlit as st
import pandas as pd
from mistralai import Mistral
import json
import os
import random
from langchain_mistralai import ChatMistralAI
from langchain_core.prompts import ChatPromptTemplate
from tools import customer_details, all_transaction_details, general_inquiry, policy_documents, get_most_recent_transaction
from langchain_core.utils.function_calling import convert_to_openai_tool
from typing import Annotated
from typing_extensions import TypedDict

from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from system_prompts import ROUTER_SYSTEM_PROMPT, ANSWER_GENERATOR_PROMPT


# configure the Phoenix tracer
from phoenix.otel import register
tracer_provider = register(
  project_name="Askit",  # Default is 'default'
  auto_instrument=True  # Auto-instrument your app based on installed dependencies
)



# Load transactions from CSV
transactions = pd.read_csv('data/transactions.csv')

# Set up customer ID
customer_id = "CUST0{:02d}".format(random.randint(1, 20))

# Load API key from secrets
secrets = json.load(open("secrets.json"))
os.environ["MISTRAL_API_KEY"] = secrets["mistral_api_key"]

# Set up Mistral LLM
llm = ChatMistralAI(
    model="mistral-large-latest",
    temperature=0,
    max_retries=2,
    max_tokens=150,
    top_p=1,
    frequency_penalty=0,
    presence_penalty=0,
)

# Define chatbot state
class State(TypedDict):
    customer_id: str
    messages: Annotated[list, add_messages]

router_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", ROUTER_SYSTEM_PROMPT),
        ("placeholder", "{msgs}"),
    ]
)

answer_generator_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", ANSWER_GENERATOR_PROMPT),
        ("user", "{text}"),
    ]
)

router_llm = router_prompt | llm
answer_generator = answer_generator_prompt | llm

# Define router function
def router(state: State):
    return {"messages": [router_llm.invoke({"msgs": state["messages"]})]}

# Define answer generation function
def generate_answer(state: State):
    call_tool = state['messages'][-1].content
    response = ''
    if call_tool == 'customer_details':
        response = customer_details(state['customer_id'])
    elif call_tool == 'all_transaction_details':
        response = all_transaction_details(state['customer_id'])
    elif call_tool == 'general_inquiry':
        response = general_inquiry(state['customer_id'])
    elif call_tool == 'policy_documents':
        response = policy_documents(state['customer_id'])
    elif call_tool == 'get_most_recent_transaction':
        response = get_most_recent_transaction(state['customer_id'])
    return {
        "messages": [answer_generator.invoke({
            "text": state["messages"][-2].content,
            "additional_information": response
        })]
    }

# Build chatbot graph
graph_builder = StateGraph(State)
graph_builder.add_node("router", router)
graph_builder.add_node("generate_answer", generate_answer)
graph_builder.add_edge(START, "router")
graph_builder.add_edge("router", "generate_answer")
graph_builder.add_edge("generate_answer", END)
graph = graph_builder.compile()

def graph_output(user_query, customer_id):
    events = graph.stream({
        "messages": [{"role": "user", "content": user_query}],
        "customer_id": customer_id
    })
    list_events = [x for x in events]
    return list_events[-1]['generate_answer']['messages'][-1].content

# Streamlit UI setup
st.title("💬 AskIt")
st.caption("🌟 Meet AskIt – Your intelligent customer support assistant! 🚀")

# Initialize session state for messages
if "messages" not in st.session_state:
    st.session_state["messages"] = [{"role": "assistant", "content": f"How can I help you, {customer_details(customer_id)['name']}?"}]

# Display previous messages
for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

# Handle user input
if user_query := st.chat_input():
    st.session_state.messages.append({"role": "user", "content": user_query})
    st.chat_message("user").write(user_query)
    msg = graph_output(user_query, customer_id)
    st.session_state.messages.append({"role": "assistant", "content": msg})
    st.chat_message("assistant").write(msg)
