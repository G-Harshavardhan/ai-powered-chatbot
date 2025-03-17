import pandas as pd
import sqlite3
import requests
import fitz  # PyMuPDF for PDF extraction
import streamlit as st
import json
import os
from io import BytesIO

# Initialize conversation memory
if "conversation" not in st.session_state:
    st.session_state.conversation = []

# Function to load CSV
def load_csv(file):
    try:
        df = pd.read_csv(file)
        return df
    except Exception as e:
        return f"Error loading CSV: {e}"

# Function to load Excel
def load_excel(file):
    try:
        df = pd.read_excel(file)
        return df
    except Exception as e:
        return f"Error loading Excel: {e}"

# Function to extract text from PDF
def load_pdf(file):
    try:
        doc = fitz.open(stream=file)
        text = "\n".join([page.get_text() for page in doc])
        return text[:2000]  # Limit text output
    except Exception as e:
        return f"Error extracting PDF text: {e}"

# Function to fetch data from API
def fetch_from_api(api_url):
    try:
        response = requests.get(api_url)
        if response.status_code == 200:
            return response.json()
        else:
            return f"Error fetching API: {response.status_code}"
    except Exception as e:
        return f"Error fetching API: {e}"

# Function to summarize data
def summarize_data(df):
    if isinstance(df, str):
        return df  # Return error messages directly
    
    summary = f"""
    **Summary of Data:**
    - **Total Rows:** {df.shape[0]}
    - **Total Columns:** {df.shape[1]}
    """
    
    if df.select_dtypes(include=['number']).shape[1] > 0:
        summary += "\n**Numeric Column Means:**"
        summary += "\n" + df.describe().loc['mean'].to_string()
    
    if df.select_dtypes(include=['object']).shape[1] > 0:
        for col in df.select_dtypes(include=['object']).columns:
            summary += f"\n- **Most Common {col}:** {df[col].mode()[0]}"
    
    return summary

# Streamlit UI
def main():
    st.title("AI-Powered Data Chatbot")
    
    st.markdown("""
        <style>
            .chat-box {
                max-height: 400px;
                overflow-y: auto;
                padding: 10px;
                border: 1px solid #ccc;
                border-radius: 5px;
                background-color: #f9f9f9;
            }
            .user-msg {
                color: blue;
                font-weight: bold;
            }
            .bot-msg {
                color: green;
                font-weight: bold;
            }
        </style>
    """, unsafe_allow_html=True)
    
    user_input = st.text_input("💬 Type your message:")
    file = st.file_uploader("📂 Upload a file (CSV, Excel, PDF):", type=["csv", "xlsx", "pdf"])
    api_url = st.text_input("🌍 Enter API URL (if applicable):")
    
    if st.button("Send"):
        response = "🤖 I didn't understand the request."
        
        if file is not None:
            if file.name.endswith(".csv"):
                df = load_csv(file)
                if "summarize" in user_input.lower():
                    response = summarize_data(df)
                elif "show" in user_input.lower():
                    response = st.dataframe(df.head())
                else:
                    response = "CSV uploaded successfully. Ask me what to do with it."
            elif file.name.endswith(".xlsx"):
                df = load_excel(file)
                if "summarize" in user_input.lower():
                    response = summarize_data(df)
                elif "show" in user_input.lower():
                    response = st.dataframe(df.head())
                else:
                    response = "Excel uploaded successfully. Ask me what to do with it."
            elif file.name.endswith(".pdf"):
                if "summarize" in user_input.lower() or "extract text" in user_input.lower():
                    response = load_pdf(file)
                else:
                    response = "PDF uploaded successfully. Ask me what to do with it."
        
        elif api_url:
            response = fetch_from_api(api_url)
        
        st.session_state.conversation.append(f"<div class='user-msg'>User: {user_input}</div>")
        st.session_state.conversation.append(f"<div class='bot-msg'>Bot: {response}</div>")
        
    st.markdown("<div class='chat-box'>" + "<br>".join(st.session_state.conversation) + "</div>", unsafe_allow_html=True)

if __name__ == "__main__":
    main()
