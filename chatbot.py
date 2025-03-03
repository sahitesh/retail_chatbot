# from openai import OpenAI
import streamlit as st
from mistralai import Mistral
import requests
import json
from langchain_mistralai import ChatMistralAI
from langchain_core.prompts import ChatPromptTemplate
from tools import customer_details, all_transaction_details, general_inquiry, policy_documents
from system_prompts import SYSTEM_PROMPT_TEMPLATE
import os
import random

customer_id = "CUST0{:02d}".format(random.randint(1, 20))

llm = ChatMistralAI(
    model="mistral-large-latest",
    temperature=0,
    max_retries=2,
    max_tokens=150,
    top_p=1,
    frequency_penalty=0,
    presence_penalty=0,
)

secrets = json.load(open("secrets.json"))
os.environ["MISTRAL_API_KEY"] = secrets["mistral_api_key"]

tools = [customer_details, all_transaction_details, general_inquiry, policy_documents]

prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            SYSTEM_PROMPT_TEMPLATE,
        ),
        ("placeholder", "{msgs}"),
    ]
)

prompt.format(customer_id=customer_id)
llm_with_tools = llm.bind_tools(tools)

llm_with_tools = prompt | llm


st.title("💬 Chatbot")
st.caption("🚀 A Streamlit chatbot powered by Mistral")
if "messages" not in st.session_state:
    st.session_state["messages"] = [{"role": "assistant", "content": f"How can I help you, {customer_details(customer_id)["name"]}?"}]

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

if prompt := st.chat_input():
    
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)
    response = llm_with_tools.invoke({"customer_id":customer_id, "msgs":st.session_state.messages})
    msg = response.content
    st.session_state.messages.append({"role": "assistant", "content": msg})
    st.chat_message("assistant").write(msg)