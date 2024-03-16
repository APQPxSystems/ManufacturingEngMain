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
    automation_app = "Sub Balancing"

    # Sub Balancing App
    if automation_app == "Sub Balancing":   
        st.title("Sub Balancing App")
        st.write("""How to use: Upload an excel file of sub data.
                Make sure that the extension is in XLSX. If not, open the file first and save as XLSX.
                Make sure that the columns SubNo, Wi_No, Ins_L, Ins_R, ConnNo_L, ConnNo_R are present to avoid errors.
                """)
        
        # Upload excel file
        raw_data = st.file_uploader("Upload sub balancing data", type=["xlsx"])
        st.write("--------------------------------------")
        
        # Read and process uploaded excel file
        if raw_data is not None:
            raw_data2 = pd.read_excel(raw_data)
        
            # Ordering columns
            raw_data3 = raw_data2[["SubNo", "Wi_No", "Ins_L", "Ins_R", "ConnNo_L", "ConnNo_R", "ApplCD"]]
            
            # Input Product
            product = st.text_input("Input Product (from ApplCD)")
            st.write("______________________________________________________________")
            
            st.subheader(f"Applicable Insertions on Product '{product}'")
            
            # Filter Applicability by Product
            raw_data3 = raw_data3[raw_data3["ApplCD"].str.contains(product)]
        
            # Group data by "Sub No"
            grouped_data = raw_data3.groupby("SubNo")
        
            # Calculate grand total
            grand_total = len(raw_data3)
        
            # Create a BytesIO object to store the Excel file
            excel_buffer_all = BytesIO()
        
            # Use pandas to_excel method to write all grouped_data to the BytesIO object
            with pd.ExcelWriter(excel_buffer_all, engine='openpyxl') as writer_all:
                for sub_no, group_data in grouped_data:
                    # Write each group_data to a separate sheet in the Excel file
                    group_data.to_excel(writer_all, sheet_name=f"SubNo_{sub_no}", index=False)
        
            # Add a download button for the entire Excel file
            download_all_button = st.button("Download All Generated Data")
            if download_all_button:
                # Set the cursor to the beginning of the BytesIO object
                excel_buffer_all.seek(0)
        
                # Add a download link for the entire Excel file
                st.download_button(
                    label="Download All Generated Data as Excel File",
                    data=excel_buffer_all,
                    file_name="All_Grouped_Data.xlsx",
                    key="download_button_all"
                )
        
            # Display tables for each "Sub No"
            for sub_no, group_data in grouped_data:
                count_wire_no = len(group_data)
                percent_of_grand_total = (count_wire_no / grand_total) * 100
                st.subheader(f"Sub No: {sub_no} - Wire Count: {count_wire_no} ({percent_of_grand_total:.2f}% of Total Insertions)")
                st.write(group_data)

    st.write("______________________________________________________")  


with open('MPPDSubBalancing/style.css') as f:
    css = f.read()

st.markdown(f'<style>{css}</style>', unsafe_allow_html=True)
  

