# 💬 Customer Interaction Application

![Screenshot 2025-05-20 214857](https://github.com/user-attachments/assets/ea22a333-fa49-43c1-b2c2-b7e64a8152ee)


An AI-powered customer support application that allows users to:
- Raise product-related issues
- Chat with an AI assistant (Groq Cloud API)
- Escalate unresolved issues for manual review
- Retrieve existing issues using the customer’s phone number

---

## 🚀 Features

- 🤖 AI chatbot integration via **Groq Cloud API**
- 🗃️ PostgreSQL-based issue storage
- 🧑‍💻 Escalation handling for unresolved cases
- 🧾 Phone number-based issue lookup
- 📺 Streamlit-based frontend UI

---

## 🧰 Requirements

- Python ≥ 3.8  
- PostgreSQL ≥ 12  
- Groq Cloud API account  
- pgAdmin or psql terminal  
- Python Libraries: `streamlit`, `psycopg2-binary`, `requests`, `python-dotenv` (optional)

---

## 🔐 API Key Setup

### Step 1: Create Groq API Key  
1. Go to [https://console.groq.com](https://console.groq.com)  
2. Register or log in  
3. Navigate to “API Keys”  
4. Click **“Create API Key”**  
5. Copy the generated key

### Step 2: Export the API Key in Bash  
```bash
export GROQ_API_KEY="your_groq_api_key_here"
```

For Windows CMD:
```cmd
set GROQ_API_KEY=your_groq_api_key_here
```

Optional: Store in a `.env` file and load using `dotenv`.

---

## 🐘 PostgreSQL Setup

### Step 3: Create "customer" Database and Table using pgAdmin or psql  
#### Create Database:
```sql
CREATE DATABASE customer;
```

#### Create Table:
```sql
CREATE TABLE customer_issues (
    id SERIAL PRIMARY KEY,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    email VARCHAR(100),
    phone CHAR(10),
    issue TEXT
);
```

---

## 📦 Installation and Setup

### Step 4: Clone and Set Up Project
```bash
git clone https://github.com/Pyoneer01/Customer_interaction_application.git
cd Customer_interaction_application
```


## ▶️ Run the Streamlit Application
```bash
streamlit run chat_integration_application.py
```

It will open in your browser at:  
`http://localhost:8501`

---

## ✅ Future Improvements

- [ ] Add login/authentication
- [ ] Admin dashboard for escalated issue review
- [ ] Notification system via email/SMS

---
