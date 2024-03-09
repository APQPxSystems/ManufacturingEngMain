# Import Libraries
# import hmac
import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
from datetime import datetime, timedelta, date
from io import BytesIO

# Streamlit Configurations
st.set_page_config(page_title="ME Dept Apps", layout="wide")
hide_st_style = """
                <style>
                #MainMenu {visibility:hidden;}
                footer {visibility:hidden;}
                header {visibility:hidden;}
                </style>
                """
st.markdown(hide_st_style, unsafe_allow_html=True)

# Remove top white space
st.markdown("""
        <style>
               .block-container {
                    padding-top: 0rem;
                    padding-bottom: 0rem;
                    padding-left: 1rem;
                    padding-right: 1rem;
                }
        </style>
        """, unsafe_allow_html=True)

# App title and info
st.markdown("<p class='app_sub_title'>MANUFACTURING ENGINEERING DEPARTMENT | SYSTEMS ENGINEERING</p>", unsafe_allow_html=True)
# Tagline
st.markdown("<p class='tagline'>Mitigating Encumbrances; Moving towards Excellence</p>", unsafe_allow_html=True)
st.markdown("<p class='app_title'>MANUFACTURING ENGINEERING WEB APP</p>", unsafe_allow_html=True)     
st.markdown("""<p class='app_info'>This web app is a collection of Manufacturing Engineering Department's automation tools.
          This runs on streamlit's cloud server and is not connected to any database.
          Therefore, any data uploaded will not be saved or collected and will vanish everytime the app is refreshed.</p>""", unsafe_allow_html=True)

# User Roles
credential_col1, credential_col2 = st.columns([2,1])
with credential_col1:
    user_role = st.selectbox("Select your department.", ["Manufacturing Engineering"])
with credential_col2:
    app_key = st.text_input("Enter department key.", type="password")

# Automation App Selection
if user_role == "Manufacturing Engineering" and app_key == "MESE24":
    automation_app = "FMEA and QCP Matrix Date Calculator"


    # FMEA and QCP Matrix Date Calculator
    if automation_app == "FMEA and QCP Matrix Date Calculator":
    
        # App Title and Description
        st.title("FMEA and QCP Matrix Date Calculator")
        st.write("""How to use: Select the type of matrix to be created.
                The required timing will be displayed.
                Look for the date of the indicated timing on the event schedule and input on the space provided.
                The necessary DATE MADE, EFFECTIVITY DATE, and KEY DATE will be automatically generated.""")
        st.write("--------------------------------------------")
    
        # Matrix Type Selection
        matrix_type = st.selectbox("Selec matrix type", ["Pre-Launch", "Mass Pro"])
    
        # Required Timing
        if matrix_type == "Pre-Launch":
            st.subheader("! Use Assy date of first event")
        else:
            st.subheader("! Use Assy date of EV/RT")
        st.write("--------------------------------------------")
    
        # Date Input
        date_input = st.date_input("Input the date based on event schedule.", value="today")
    
        # Date Function
        def subtract_weekdays(start_date, days_to_subtract):
            current_date = start_date
            while days_to_subtract > 0:
                current_date -= timedelta(days=1)
                # Check if the current day is a weekend (Saturday or Sunday)
                if current_date.weekday() < 5:
                    days_to_subtract -= 1
            return current_date
    
        # FMEA and QCP columns
        FMEAcol, QCPcol = st.columns([1,1])
    
        with FMEAcol:
            st.subheader("FMEA Matrix")
            start_date = date_input
    
            # Date Made
            if matrix_type == "Pre-Launch":
                result_date = subtract_weekdays(start_date, 9)
                st.subheader(f"Date Made: {result_date.strftime('%Y-%m-%d')}")
            else:
                result_date = subtract_weekdays(start_date, 12)
                st.subheader(f"Date Made: {result_date.strftime('%Y-%m-%d')}")
    
            # Key Date
            result_date = subtract_weekdays(start_date, 6)
            st.subheader(f"Key Date: {result_date.strftime('%Y-%m-%d')}")
    
            # Effectivity Date
            if matrix_type == "Pre-Launch":
                result_date = subtract_weekdays(start_date, 6)
                st.subheader(f"Effectivity Date: {result_date.strftime('%Y-%m-%d')}")
            else:
                result_date = subtract_weekdays(start_date, 9)
                st.subheader(f"Effectivity Date: {result_date.strftime('%Y-%m-%d')}")
    
        with QCPcol:
            st.subheader("QCP Matrix")
            start_date = date_input
    
            # Date Made
            result_date = subtract_weekdays(start_date, 6)
            st.subheader(f"Date Made: {result_date.strftime('%Y-%m-%d')}")
    
            # Key Date
            result_date = subtract_weekdays(start_date, 3)
            st.subheader(f"Key Date: {result_date.strftime('%Y-%m-%d')}")
    
            # Effectivity Date
            result_date = subtract_weekdays(start_date, 3)
            st.subheader(f"Effectivty Date: {result_date.strftime('%Y-%m-%d')}")


st.write("______________________________________________________")  


with open('style.css') as f:
    css = f.read()

st.markdown(f'<style>{css}</style>', unsafe_allow_html=True)
