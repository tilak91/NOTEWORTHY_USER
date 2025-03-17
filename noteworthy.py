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
import os

# MongoDB Setup

CONNECTION_STRING = "mongodb+srv://NOTEWORTHY:Tilak$2004@noteworthy.fmh8b.mongodb.net/?retryWrites=true&w=majority&appName=NOTEWORTHY"

# Connect to MongoDB Atlas
client = MongoClient(CONNECTION_STRING)

db = client["record_writing_app"]
users_collection = db["users"]
records_collection = db["records"]



# Email Configuration for OTP
EMAIL_ADDRESS = "noteworthynotes24@gmail.com"
EMAIL_PASSWORD = "bnkm atmy ooup dmke"

# Lottie Animations
def load_lottie_url(url):
