import random
import streamlit as st
import hashlib
import smtplib
import datetime
from pymongo import MongoClient
from PyPDF2 import PdfReader
import tempfile
import pyqrcode
from streamlit_lottie import st_lottie
import json
import requests
import base64
import pandas as pd
import plotly.express as px

# MongoDB Setup
client = MongoClient("mongodb://localhost:27017/")
db = client["record_writing_app"]
users_collection = db["users"]
records_collection = db["records"]

# Email Configuration for OTP
EMAIL_ADDRESS = "noteworthynotes24@gmail.com"
EMAIL_PASSWORD = "bnkm atmy ooup dmke"

# Lottie Animations
def load_lottie_url(url):
    response = requests.get(url)
    if response.status_code != 200:
        return None
    return response.json()

lottie_upload = load_lottie_url("https://assets10.lottiefiles.com/packages/lf20_5tkzkblw.json")
lottie_chatbot = load_lottie_url("https://assets10.lottiefiles.com/packages/lf20_vnikrcia.json")
lottie_payment = load_lottie_url("https://assets10.lottiefiles.com/packages/lf20_5tkzkblw.json")

# SIMRAN Chatbot Responses
responses = {
    "greeting": [
        "Hello! How can I assist you today?",
        "Hi there! What can I help you with?",
        "Hey! How are you doing today?",
        "Hi! I'm here to help. What's on your mind?",
        "Hey! How can I be of service?"
    ],
    "task_submission": [
        "You can submit a task by uploading your PDF document, choosing the font, and providing task details.",
        "To submit a task, please upload your document and select the appropriate options.",
        "Just upload your PDF and let me know the task type, font, and priority, and I'll handle the rest."
    ],
    "order_status": [
        "You can view the status of your order in the 'Your Orders' section.",
        "To check your order status, go to your dashboard and look for the order details.",
        "Order status can be found under 'Your Orders'. You'll see if it's pending or completed."
    ],
    "pricing": [
        "The price is calculated based on the number of pages, font choice, and priority. You can see the total cost after uploading the PDF.",
        "The cost depends on the number of pages and the font choice. After you upload a document, the price will be displayed.",
        "Pricing is dynamic based on the task and font options selected. Upload your document to calculate the cost."
    ],
    "default": [
        "I'm sorry, I didn't quite understand that. Could you please rephrase your question?",
        "Could you clarify your request? I didn't catch that.",
        "I'm still learning! Can you provide more details so I can assist you better?",
        "I'm not sure about that, but I'll try to assist you. Could you rephrase?"
    ]
}

# Function to generate a response based on user input
def get_chatbot_response(user_input):
    user_input = user_input.lower()

    # Simple keyword-based matching
    if any(keyword in user_input for keyword in ["hello", "hi", "hey"]):
        return random.choice(responses["greeting"])
    elif any(keyword in user_input for keyword in ["submit", "task", "upload"]):
        return random.choice(responses["task_submission"])
    elif any(keyword in user_input for keyword in ["status", "order", "check"]):
        return random.choice(responses["order_status"])
    elif any(keyword in user_input for keyword in ["price", "cost", "pricing"]):
        return random.choice(responses["pricing"])
    else:
        return random.choice(responses["default"])

# Helper Functions
def generate_upi_qr_code(upi_id, amount):
    qr_data = f"upi://pay?pa={upi_id}&am={amount}&cu=INR"
    qr_code = pyqrcode.create(qr_data)
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
    qr_code.png(temp_file.name, scale=8)
    return temp_file.name

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def send_otp(email):
    otp = random.randint(100000, 999999)
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        message = f"Subject: Your OTP Code\n\nYour OTP code is: {otp}"
        server.sendmail(EMAIL_ADDRESS, email, message)
    return otp

def get_pdf_page_count(file):
    try:
        reader = PdfReader(file)
        return len(reader.pages)
    except Exception as e:
        st.error(f"Error reading PDF: {e}")
        return 0

def authenticate_user(username, password):
    hashed_password = hash_password(password)
    user = users_collection.find_one({"username": username, "password": hashed_password})
    return user

def calculate_total_cost(num_pages, font_choice, priority):
    font_price_map = {
        "Font_1": 6.0,
        "Font_2": 5.0,
        "Font_3": 7.0
    }
    base_price = font_price_map.get(font_choice, 5.0)
    priority_multiplier = {
        "Low": 1.0,
        "Medium": 1.2,
        "High": 1.5
    }
    price_per_page = base_price * priority_multiplier.get(priority, 1.0)
    total_cost = price_per_page * num_pages
    return total_cost

# SIMRAN Chatbot Integration
def simran_chatbot():
    st.header("🤖 SIMRAN - Your AI Assistant")
    st.write("Hi! I'm SIMRAN, your AI assistant. How can I help you today?")

    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display chat history
    for message in st.session_state.messages:
        if message["role"] == "user":
            st.write(f"**You:** {message['content']}")
        else:
            st.write(f"**SIMRAN:** {message['content']}")

    # User input
    user_input = st.text_input("Ask SIMRAN anything:", key="user_input")

    if user_input:
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": user_input})

        # Get SIMRAN's response
        simran_response = get_chatbot_response(user_input)

        # Add SIMRAN's response to chat history
        st.session_state.messages.append({"role": "simran", "content": simran_response})

        # Display SIMRAN's response
        st.write(f"**SIMRAN:** {simran_response}")

# Streamlit App
def main():
    st.set_page_config(page_title="Record Writing App", page_icon="📜", layout="wide")

    # Custom CSS for enhanced UI
    st.markdown("""
        <style>
        .stButton button {
            background-color: #4CAF50;
            color: white;
            border-radius: 5px;
            padding: 10px 24px;
            font-size: 16px;
        }
        .stTextInput input {
            border-radius: 5px;
            padding: 10px;
        }
        .stSelectbox select {
            border-radius: 5px;
            padding: 10px;
        }
        .stFileUploader button {
            border-radius: 5px;
            padding: 10px;
        }
        .version {
            position: absolute;
            top: 10px;
            right: 10px;
            font-size: 14px;
            color: gray;
        }
        </style>
    """, unsafe_allow_html=True)

    # Display version number
    st.markdown('<div class="version">Version 1.0.1</div>', unsafe_allow_html=True)

    if "username" in st.session_state:
        user_dashboard(st.session_state["username"])
    else:
        page = st.sidebar.radio("📄 Navigate", ["Login", "Register"])

        if page == "Login":
            st.title("🔒 Login")
            username = st.text_input("👤 Username:")
            password = st.text_input("🔑 Password:", type="password")

            if st.button("🔓 Login"):
                user = authenticate_user(username, password)
                if user:
                    st.session_state["username"] = username
                    st.success("✅ Login Successful!")
                    st.balloons()
                else:
                    st.error("❌ Invalid username or password.")

        elif page == "Register":
            st.title("🔑 Register")
            username = st.text_input("👤 Username:")
            password = st.text_input("🔒 Password:", type="password")
            email = st.text_input("📧 Email:")

            if st.button("🎉 Register"):
                if users_collection.find_one({"username": username}):
                    st.error("❌ Username already exists.")
                else:
                    hashed_password = hash_password(password)
                    users_collection.insert_one({"username": username, "password": hashed_password, "email": email})
                    otp = send_otp(email)
                    st.session_state["otp"] = otp
                    st.session_state["username"] = username
                    st.session_state["password"] = password
                    st.success("✅ OTP sent to your email.")
                    otp_input = st.text_input("🔢 Enter OTP:")
                    if st.button("🔓 Verify OTP"):
                        if str(st.session_state["otp"]) == otp_input:
                            st.success("🎉 Registration Successful!")
                            st.balloons()
                        else:
                            st.error("❌ Invalid OTP. Please try again.")

def user_dashboard(username):
    st.title(f"👋 Welcome {username}!")

    # Tabs for navigation
    tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8, = st.tabs([
        "📤 Submit Task", 
        "📜 Your Orders", 
        "🤖 Chatbot", 
        "⚙️ Settings", 
        "⭐ Rate Your Order", 
        "🎁 Seasonal Offers", 
        "📦 Bulk Order Discounts", 
        "📊 Spending Analytics"
    ])

    # Submit Task Tab
    with tab1:
        st.header("📤 Submit a Task")
        st_lottie(lottie_upload, height=200, key="upload_animation")
        uploaded_file = st.file_uploader("📄 Upload your PDF", type="pdf")
        num_pages = 0

        if uploaded_file is not None:
            # PDF Preview Section
            st.subheader("PDF Preview")
            
            # Show PDF in browser
            base64_pdf = base64.b64encode(uploaded_file.read()).decode('utf-8')
            pdf_display = f"""
                <iframe src="data:application/pdf;base64,{base64_pdf}" 
                        width="100%" 
                        height="800" 
                        style="border:1px solid #EEEEEE;
                               border-radius: 10px;
                               margin-bottom: 20px;">
                </iframe>
            """
            st.markdown(pdf_display, unsafe_allow_html=True)
            
            # Reset file pointer for processing
            uploaded_file.seek(0)

            # Existing processing code
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
                temp_file.write(uploaded_file.read())
                temp_file_path = temp_file.name
                st.success("📃 PDF uploaded successfully!")

            try:
                num_pages = get_pdf_page_count(temp_file_path)
                st.write(f"📑 Number of Pages: {num_pages}")
            except Exception as e:
                st.error(f"Error processing the PDF: {e}")

            task_type = st.selectbox("🗂️ Task Type:", ["Record", "Notes", "Assignment"])

            # Font recommendation based on task type
            if task_type == "Record":
                recommended_fonts = ["Font_1", "Font_2", "Font_3", "Font_11"]
            elif task_type == "Notes":
                recommended_fonts = ["Font_4", "Font_5", "Font_6", "Font_7"]
            else: # Assignment
                recommended_fonts = ["Font_8", "Font_9", "Font_10"]

            font_choice = st.selectbox("🖋️ Select Font:", recommended_fonts)
            st.image(f"C:/Users/tilak/OneDrive/Desktop/{font_choice}.png", caption="Font Preview", use_container_width=True)

            pickup_location = st.text_input("📍 Pick-Up Location:")
            drop_location = st.text_input("📍 Drop-Off Location:")
            priority = st.radio("⚡ Priority:", ["Low", "Medium", "High"])
            deadline = st.date_input("⏰ Set Deadline:", min_value=datetime.date.today())

            if num_pages > 0:
                total_cost = calculate_total_cost(num_pages, font_choice, priority)
                st.write(f"💰 Total Cost: ₹{total_cost:.2f}")
            else:
                total_cost = 0.0

            if st.button("🚀 Submit Task"):
                if num_pages > 0:
                    record = {
                        "username": username,
                        "pdf_path": temp_file_path,
                        "num_pages": num_pages,
                        "font": font_choice,
                        "total_cost": total_cost,
                        "pickup_location": pickup_location,
                        "dropoff_location": drop_location,
                        "task_type": task_type,
                        "priority": priority,
                        "deadline": str(deadline),
                        "status": "pending"
                    }
                    records_collection.insert_one(record)
                    st.success("Task Submitted Successfully! 🎉")
                    st.balloons()
                    st.info("🎓 While your task is being processed, check out these amazing YouTube channels to learn coding!")
                    st.markdown(
                        """
                        - [Apna College](https://www.youtube.com/@ApnaCollegeOfficial)
                        - [CodeWithHarry](https://www.youtube.com/c/CodeWithHarry)
                        - [freeCodeCamp.org](https://www.youtube.com/@freecodecamp)
                        - [Kunal Kushwaha](https://www.youtube.com/@KunalKushwaha)
                        """
                    )           
                else:
                    st.error("Please upload a PDF file to proceed.")

    # Your Orders Tab
    with tab2:
        st.header("📜 Your Orders")
        st.write("✨ Kindly send the screenshot of the payment on WhatsApp to 📲 9182330751. Thank you! 😊")
        orders = records_collection.find({"username": username})

        for order in orders:
            order_id = str(order["_id"])
            st.subheader(f"📝 Order ID: {order_id}")
            st.write(f"Font: {order['font']} | Status: {order['status']} | Total Cost: ₹{order['total_cost']:.2f}")
            st.write(f"Task Type: {order['task_type']} | Deadline: {order['deadline']}")

            # Pay Now button to generate QR code for payment
            with st.form(key=f"pay_form_{order_id}"):
                if st.form_submit_button(f"Pay Now for Order {order_id}"):
                    qr_code_path = generate_upi_qr_code("9182330751@ybl", order["total_cost"])
                    st.image(qr_code_path, caption="Scan this UPI QR Code to make payment")
                    st.success(f"Payment Amount: ₹{order['total_cost']:.2f}")
                    st_lottie(lottie_payment, height=200, key="payment_animation")

    # Chatbot Tab
    with tab3:
        simran_chatbot()  # SIMRAN Chatbot Integration

    # Settings Tab
    with tab4:
        st.header("⚙️ Settings")
        st.subheader("🔑 Change Password")
        current_password = st.text_input("Current Password:", type="password")
        new_password = st.text_input("New Password:", type="password")
        confirm_new_password = st.text_input("Confirm New Password:", type="password")
        otp_input = st.text_input("Enter OTP sent to your email:", type="password")

        if st.button("Send OTP"):
            user = authenticate_user(username, current_password)
            if user:
                otp = send_otp(user["email"])
                st.session_state["otp"] = otp
                st.success("OTP sent to your registered email.")
            else:
                st.error("Current password is incorrect. Please try again.")

        if st.button("Update Password"):
            if otp_input == str(st.session_state.get("otp", "")):
                if new_password == confirm_new_password:
                    hashed_new_password = hash_password(new_password)
                    users_collection.update_one({"username": username}, {"$set": {"password": hashed_new_password}})
                    st.success("Password updated successfully.")
                else:
                    st.error("New passwords do not match. Please try again.")
            else:
                st.error("Incorrect OTP. Please try again.")

    # Rate Your Order Tab
    with tab5:
        st.header("⭐ Rate Your Order")
        user_orders = list(records_collection.find({"username": username}))
        if user_orders:
            order_options = {order["_id"]: f"Order {order['_id']} - Status: {order['status']}" for order in user_orders}
            selected_order = st.selectbox("Select an order to rate:", options=list(order_options.keys()), format_func=lambda x: order_options[x])
            
            if selected_order:
                selected_order_data = records_collection.find_one({"_id": selected_order})
                st.write(f"**Status:** {selected_order_data['status']}")
                
                if selected_order_data["status"].lower() == "completed":
                    rating = st.slider("Rate this order:", 1, 5, 3)
                    if st.button("Submit Rating"):
                        records_collection.update_one({"_id": selected_order}, {"$set": {"rating": rating}})
                        st.success("✅ Rating submitted successfully!")
                        st.success("🎉 Thank you for using our services!")
                        st.snow()
                else:
                    st.warning("⚠️ You can only rate completed orders.")
        else:
            st.info("ℹ️ No orders found.")

    # Seasonal Offers Tab
    with tab6:
        st.header("🎁 Seasonal Offers")
        st.write("Check out our special offers during exam periods!")

    # Bulk Order Discounts Tab
    with tab7:
        st.header("📦 Bulk Order Discounts")
        st.write("Get discounts on bulk orders!")
        # Add your bulk order discounts logic here

    # Spending Analytics Tab
    with tab8:
        st.header("📊 Spending Analytics")
        st.write("Analyze your spending patterns and get insights.")
        st.write("It's under development!")
        st.write("Check back soon for updates.")
        # Add your spending analytics logic here

if __name__ == "__main__":
    main()