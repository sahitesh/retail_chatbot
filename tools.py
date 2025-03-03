from langchain_core.tools import tool
import pandas as pd

with open("data/policy_document.txt", "r") as f:
    policy_document = f.read()

details_json = pd.read_csv("data/customers.csv").set_index('customer_id').T.to_dict()
transaction_json = pd.read_csv("data/transactions.csv").set_index('customer_id').T.to_dict()

@tool
def customer_details(customer_id):
    """fetch customer details like name, email, phone number, age, and address."""
    return details_json[customer_id]

@tool
def all_transaction_details(customer_id):
    """fetch all transaction details of a customer like transaction id, date, time, amount, and status."""
    return transaction_json[customer_id]

@tool
def general_inquiry() -> int:
    """Returns a static message for general inquiries."""
    return "Query falls out of scope for the chatbot's intended use. Please contact our customer support team for further assistance."

@tool
def policy_documents() -> int:
    """fetches the relevant policy documents regarding return policy, refund policy, warranty policy and shipping policy."""
    return policy_document

