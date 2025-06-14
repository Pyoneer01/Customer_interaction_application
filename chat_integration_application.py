import streamlit as st
import psycopg2
import pandas as pd
import os
import re
from groq import Groq
import requests
import json


api_key = os.getenv("GROQ_API_KEY")


# Check if API key is available
if not api_key:
    st.error("API key not found. Please set the GROQ_API_KEY environment variable.")
    st.stop()

# Initialize the Groq client
client = Groq(api_key=api_key)

# Your updated Groq API Key and endpoint
API_KEY = api_key
API_URL = 'https://api.groq.com/openai/v1/chat/completions'

def summarize_issue(customer_issue):
    headers = {
        'Authorization': f'Bearer {API_KEY}',
        'Content-Type': 'application/json',
    }

    data = {
        "messages": [
            {
                "role": "system",
                "content": (
                    "You are a highly skilled professional assistant. Summarize the text provided by the customer into a single, well-structured paragraph using a formal and professional tone. Focus only on the relevant and key details expressed by the customer, avoiding any unrelated or irrelevant points. Ensure the summary is clear, concise, and accurately reflects the customer's main concerns or intentions. Use third-person perspective and avoid including any first-person pronouns such as 'my' or 'I'. Do not include any introductory or concluding phrases such as 'Here is a summary.' Return only the main summarized content."
                )
            },
            {"role": "user", "content": customer_issue}
        ],
        "model": "llama3-8b-8192",
        "temperature": 0.5,
        "max_tokens": 400,
        "top_p": 1.0,
        "stop": None
    }

    try:
        response = requests.post(API_URL, json=data, headers=headers)
        if response.status_code == 200:
            response_json = response.json()
            if 'choices' in response_json and response_json['choices']:
                summary = response_json['choices'][0]['message']['content']
                return summary
            else:
                return "Error: No summary returned in response."
        else:
            return f"API Error: {response.status_code} - {response.text}"
    except Exception as e:
        return f"Error summarizing the transcript: {e}"



# Database connection setup
def get_connection():
    return psycopg2.connect(
        host="localhost",
        database="customer",
        user="postgres",
        password="meradb7"
    )

# Fetch all customers from the database
def fetch_customers():
    conn = get_connection()
    query = "SELECT * FROM customer_issues ORDER BY id"
    customers = pd.read_sql_query(query, conn)
    conn.close()
    return customers

# Add a new customer to the database and return the generated customer ID
def add_customer(first_name, last_name, email, phone):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO customer_issues (first_name, last_name, email, phone)
        VALUES (%s, %s, %s, %s) RETURNING id
        """,
        (first_name, last_name, email, phone)
    )
    customer_id = cursor.fetchone()[0]
    conn.commit()
    conn.close()
    return customer_id

# Update an existing customer
def update_customer(customer_id, first_name, last_name, email, phone, issue):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        UPDATE customer_issues
        SET first_name = %s, last_name = %s, email = %s, phone = %s, issue = %s, updated_at = NOW()
        WHERE id = %s
        """,
        (first_name, last_name, email, phone, issue, customer_id)
    )
    conn.commit()
    conn.close()
    st.rerun()

# Add an issue for a specific customer
def add_issue(customer_id, issue):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        UPDATE customer_issues
        SET issue = %s, updated_at = NOW()
        WHERE id = %s
        """,
        (issue, customer_id)
    )
    conn.commit()
    conn.close()

# Delete a customer from the database
def delete_customer(customer_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "DELETE FROM customer_issues WHERE id = %s", (customer_id,)
    )
    conn.commit()
    conn.close()
    st.rerun()  


# Retrieve the API key from environment variables


def save_chat_history(customer_id, chat_history):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        UPDATE customer_issues
        SET issue = %s, updated_at = NOW()
        WHERE id = %s
        """,
        (chat_history, customer_id)
    )
    conn.commit()
    conn.close()
    
# Groq API response
def get_groq_response(user_message):
    try:
        # Call the Groq API for a chat completion
        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": "you are a helpful assistant for an e-commerce company. Give a meaningful response within 150 tokens"},
                {"role": "user", "content": user_message},
            ],
            model="llama3-8b-8192",
            temperature=0.5,
            max_tokens=100,
            top_p=1,
            stop=None,
            stream=False,
        )
        return chat_completion.choices[0].message.content
    except Exception as e:
        return f"Error: {e}"

def chatbot_page():
    st.title("Chat with Support Bot")
    customer_id = st.session_state.get("customer_id", None)

    if not customer_id:
        st.error("No customer selected. Please add a customer first.")
        st.session_state.current_page = "new_issue"
        st.rerun()
        return

    # Initialize chat history in session state if not already set
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    # WhatsApp-like header
    st.markdown(f"### Chat with Support Bot (Customer ID: {customer_id})")
    st.markdown("---")

    # Display chat history dynamically
    chat_container = st.container()
    with chat_container:
        for message in st.session_state.chat_history:
            if message.startswith("Customer:"):
                st.markdown(
                    f"""
                    <div style='
                        width: 70%; 
                        margin-bottom: 15px; 
                        padding: 5px;
                    '>
                        👤 {message[10:]}
                    </div>
                    """, 
                    unsafe_allow_html=True
                )
            else:
                st.markdown(
                    f"""
                    <div style='
                        width: 70%; 
                        margin-left: auto; 
                        margin-bottom: 15px; 
                        padding: 5px;
                    '>
                        🤖 {message[12:]}
                    </div>
                    """, 
                    unsafe_allow_html=True
                )

    # User input for chat
    user_message = st.text_input("Describe your issue", key="user_message", placeholder="Type your message here...")

    # Send message logic
    if st.button("Send"):
        if user_message.strip():
            # Add user message to chat history
            st.session_state.chat_history.append(f"Customer: {user_message}")

            # Get bot response
            bot_response = get_groq_response(user_message)
            st.session_state.chat_history.append(f"Support Bot: {bot_response}")
            st.rerun()

    # Escalate the issue
    if st.button("Escalate Issue"):
        try:
            # Save only user messages to the database
            chat_history = [msg[10:] for msg in st.session_state.chat_history if msg.startswith("Customer:")]
            chat_history_combined = " ".join([msg[10:] for msg in st.session_state.chat_history if msg.startswith("Customer:")])
            summary = summarize_issue(chat_history_combined)
            print(summary)
            save_chat_history(
                customer_id,
                summary
            )
            st.success("Your chat history has been saved for further review.")
            del st.session_state["chat_history"]
            del st.session_state["customer_id"]
            st.session_state.current_page = "new_issue"
        except Exception as e:
            st.error(f"Error saving chat history: {e}")
    
    if st.button("🏠 Home Page"):
        st.session_state.current_page = "home"
        st.success("Navigating to 'Home' page...")
        st.rerun()  



def existing_issue_page():
    st.header("Retrieve Your Previous Issue")
    st.markdown("Enter your phone number to look up your previous issue.")

    with st.form("get_existing_issue_form"):
        phone = st.text_input("Phone", help="Enter the phone number associated with your account.")
        submitted = st.form_submit_button("Submit")

        if submitted:
            if not phone.strip():
                st.warning("Please enter a valid phone number.")
                return

            # Query to fetch the issue based on the phone number
            query = "SELECT issue FROM customer_issues WHERE phone = %s"

            # Execute the query with the parameter
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute(query, (phone,))
            result = cursor.fetchone()  # Fetch one row (or use fetchall() for multiple rows)

            # Close the connection
            cursor.close()
            conn.close()

            # Display the result
            if result:
                issue = result[0]  # Assuming the issue is the first column in the result
                st.markdown(f"#### Your previous issue was")
                st.markdown(f"#### {issue}")
            else:
                st.warning("No previous issue found for the provided phone number.")
    if st.button("🏠 Home Page"):
        st.session_state.current_page = "home"
        st.success("Navigating to 'Home' page...")
        st.rerun()

def is_valid_email(email):
    """Validate email format."""
    email_regex = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return re.match(email_regex, email)

def is_valid_phone(phone):
    """Validate phone number format (10 digits)."""
    return phone.isdigit() and len(phone) == 10


# Page switching logic
if "current_page" not in st.session_state:
    st.session_state.current_page = "home"

if st.session_state.current_page == "home":
    # Two columns for options
    st.title("Customer Interaction Management")
    st.markdown("<div style='margin-bottom: 30px;'></div>", unsafe_allow_html=True)
    st.markdown("<p style='font-size:18px;'>Welcome to the home page for the Customer Interaction Management Application! Here, you can easily raise a new issue or review existing ones by selecting the appropriate option below. Our AI-powered support system is designed to make your experience seamless—report your concern, chat with our AI assistant powered by Groq Cloud for instant guidance, or escalate unresolved matters for manual review. You can quickly access past issues using your phone number, ensuring hassle-free support whenever you need it.</p>", unsafe_allow_html=True);
    st.markdown("<div style='margin-bottom: 50px;'></div>", unsafe_allow_html=True)
    st.markdown("#### Choose an action:")
    # Create equal-sized columns
    st.markdown("<div style='margin-bottom: 30px;'></div>", unsafe_allow_html=True)

    col1, col2 = st.columns([2, 1])

    # Add buttons to each column
    with col1:
        if st.button("➕ Raise New Issue"):
            st.session_state.current_page = "new_issue"
            st.success("Navigating to 'New Issue' page...")
            st.rerun()
    with col2:
        if st.button("📂 View Existing Issues"):
            st.session_state.current_page = "existing_issue"
            st.success("Navigating to 'Existing Issues' page...")
            st.rerun()

elif st.session_state.current_page == "new_issue":

    with st.form("customer_form"):
        first_name = st.text_input("First Name")
        last_name = st.text_input("Last Name")
        email = st.text_input("Email")
        phone = st.text_input("Phone")
        submitted = st.form_submit_button("Submit")
        
        if submitted:
            # Validate input fields
            if not first_name or not last_name or not email or not phone:
                st.error("All fields are required.")
            elif not is_valid_email(email):
                st.error("Please enter a valid email address.")
            elif not is_valid_phone(phone):
                st.error("Phone number must be exactly 10 digits.")
            else:
                try:
                    # Simulate the add_customer function
                    customer_id = add_customer(first_name, last_name, email, phone)
                    st.session_state["customer_id"] = customer_id
                    st.session_state.current_page = "issue_management"  # Switch to issue management
                    st.rerun()
                except psycopg2.errors.UniqueViolation:
                    st.error("Email or Phone already exists. Please use unique values.")
                except Exception as e:
                    st.error(f"Unexpected error: {e}")

    if st.button("🏠 Home Page"):
        st.session_state.current_page = "home"
        st.success("Navigating to 'Home' page...")
        st.rerun()

elif st.session_state.current_page == "issue_management":
    chatbot_page()

elif st.session_state.current_page == "existing_issue":
    existing_issue_page()

