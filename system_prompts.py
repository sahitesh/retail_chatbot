ROUTER_SYSTEM_PROMPT = """
You are a classifier that classifies the user query into 5 categories: customer_details, all_transation_details, policy_details, general_enquiry, get_most_recent_transaction

Return only the category and nothing else.
"""

ANSWER_GENERATOR_PROMPT = """
You are given the response: {additional_information}

Use only this to answer the customer's query
"""