import streamlit as st
import google.generativeai as genai
import pyodbc
import os
from dotenv import load_dotenv
from datetime import date

# Load environment variables
load_dotenv()

# Configure Gemini API
genai.configure(api_key=os.getenv('GEMINI_API_KEY'))

# Function to classify feedback using Gemini
def classify_feedback(feedback):
    model = genai.GenerativeModel('gemini-1.5-flash')
    prompt = f"""Classify the following restaurant feedback into one of these categories: 
    Food Quality, Service(Food Service(serving and waiting time)), Ambiance, Value for Money, or Overall Experience. (or anyother category which feel makes sense)
    Only return the classification word.

    Feedback: {feedback}"""
    response = model.generate_content(prompt)
    return response.text

# Function to insert data into SQL Server
def insert_data(name, phone, rating, feedback, category):
    conn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};'
                          'SERVER=DESKTOP-KLL45AE\SQLEXPRESS;'
                          'DATABASE=ADITYADB;'
                          'Trusted_Connection=yes;')
    cursor = conn.cursor()
    today = date.today().isoformat()
    cursor.execute("""INSERT INTO RestaurantFeedback 
                      (Name, PhoneNumber, Rating, Feedback, Category, Date) 
                      VALUES (?, ?, ?, ?, ?, ?)""", 
                   name, phone, rating, feedback, category, today)
    conn.commit()
    conn.close()

# Streamlit app
def main():
    st.title("Flavor Fusion - Customer Feedback")
    
    st.write("""
    Dear Valued Guest,

    Thank you for dining at Flavor Fusion! We hope you enjoyed your experience with us.
    We would love to hear your thoughts to help us serve you better in the future.
    """)

    # Get user input
    name = st.text_input("Name (Optional):")
    phone = st.text_input("Phone Number (Optional):")
    rating = st.slider("How would you rate your overall experience?", 1, 5, 3)
    feedback = st.text_area("Please share your thoughts about your dining experience:")
    
    if st.button("Submit Feedback"):
        if feedback:
            # Classify feedback
            category = classify_feedback(feedback)
            
            # Insert data into SQL Server
            insert_data(name if name else "Anonymous", 
                        phone if phone else "Not provided", 
                        rating, feedback, category)
            
            st.success("Thank you for your valuable feedback! We appreciate your input and look forward to serving you again.")
            
            if rating <= 2:
                st.info("We're sorry to hear you didn't have the best experience. Our manager will review your feedback and we'll work on improving.")
        else:
            st.warning("Please provide some feedback before submitting.")

if __name__ == "__main__":
    main()