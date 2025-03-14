# retail_chatbot

## Instructions to run

1. clone the repository
2. create a virtualenv in the repo. (virtualenv .venv)
3. source .venv/bin/activate
4. pip install -r requirements.txt
5. Start Phoenix for Tracing 
    phoenix serve  
6. Run the Chatbot
    streamlit run chatbot.py  
    



## Objective

### Retail customer support chatbot

1. Answer questions on policies - return, refund, warranty etc
2. Answer questions on subscription programs - bronze, gold, platinum
3. Answer questions on order history, order tracking, etc

### Data collection

1. Mock the customer profile, transaction data with their subscription status with points
2. Create some policy documents to answer policy related questions
3. Create documents for subscription programs
