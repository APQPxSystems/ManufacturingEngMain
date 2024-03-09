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
    user_role = st.selectbox("Select your department.", ["Manufacturing Engineering",
                                                        "Production",
                                                        "Production Engineering",
                                                        "Quality Assurance"])
with credential_col2:
    app_key = st.text_input("Enter department key.", type="password")

# Automation App Selection
if user_role == "Manufacturing Engineering" and app_key == "MESE24":
    automation_app = "PDCA Summary Viewer"

# PDCA Summary Viewer
    if automation_app == "PDCA Summary Viewer":
        # App Title and Description
        st.title("PDCA Summary Viewer")
    
        # Read Excel File
        pdca_file = pd.read_excel("PDCA/PDCA.xlsx")
    
        # Altair Bar Chart - All Models and per Department
        general_df_open = pd.DataFrame(pdca_file[pdca_file["Status"]=="Open"])
        general_chart = alt.Chart(general_df_open).mark_bar().encode(
            x=alt.X('Model:N', title='Model'),
            y=alt.Y('count():Q', title='Count'),
            color='Department:N'
        ).properties(
            title='Stacked Count of Open items for each Model by Department'
        )
        st.altair_chart(general_chart, use_container_width=True)
        st.write("--------------------------------------------------------")
    
        # Columns for Filters in Model and Status
        
        st.write("""Select car maker, car model, status, and department/ section.""")
        model_col, status_col = st.columns([1,1])
    
        with model_col:
            car_model = st.selectbox("Select Car Model:", pdca_file["Model"].unique())
    
        with status_col:
            status = st.selectbox("Select Status:", pdca_file["Status"].unique())
    
        # Filter the DataFrame based on selected Model and Status
        filtered_data = pdca_file[(pdca_file['Model'] == car_model) & (pdca_file['Status'] == status)]
    
        # Altair Bar Chart - Specific Model per Department
        chart_df = pd.DataFrame(filtered_data)
        grouped_data = chart_df.groupby(["Department", "Status"]).size().reset_index(name="Count")
        chart_bar = alt.Chart(grouped_data).mark_bar().encode(
            x="Department",
            y="Count",
            color="Status"
        )
        st.altair_chart(chart_bar, use_container_width=True)
        st.write("------------------------------------------")
        
        # Filter in Department
        department_section = st.selectbox("Choose Department/ Section:", pdca_file["Department"].unique())
    
        # Filter and Drop Filtered Columns
        filtered_items = pdca_file.loc[(pdca_file["Model"]==car_model) 
                                    & (pdca_file["Status"]==status) 
                                    & (pdca_file["Department"]==department_section)]
    
        final_pdca = filtered_items.drop(["Car Maker", "Model", "Status", "Department"], axis=1)
    
        # Variable Type Conversion and Fill None
        final_pdca["Product"] = final_pdca["Product"].astype(str)
        final_pdca.fillna("", inplace=True)
    
        # Display Dataframe
        st.title(f"{department_section} {status} Items - {car_model}")
        total_items = len(final_pdca["Items"])
        st.subheader(f"{total_items} {status} Items in Total.")
        st.dataframe(final_pdca)
    
        # Download Button
        @st.cache_data
        def convert_df(df):
            return df.to_csv().encode('utf-8')
        
        csv = convert_df(final_pdca)
    
        st.download_button(
            label="Download PDCA",
            data=csv,
            file_name= f"{department_section} PDCA {status} items - {car_model}.csv",
            mime="text/csv")

st.write("______________________________________________________")  


with open('style.css') as f:
    css = f.read()

st.markdown(f'<style>{css}</style>', unsafe_allow_html=True)
