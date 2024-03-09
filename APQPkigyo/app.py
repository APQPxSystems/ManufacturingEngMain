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
    automation_app = st.selectbox("Select an automation app.", [
                                                                "Kigyo Generator (with Inventory Data)",
                                                                "Kigyo Generator (without Inventory Data)"])

    # Kigyo Calculator -- with Inventory Data
    if automation_app == "Kigyo Generator (with Inventory Data)":
        # App Title and Subheader
        st.title("Kigyo Generator")
        st.write("""How to use: Upload required excel files.
                 Drag the allowance slider to your desired price allowance in %.
                 The Kigyo output will be automatically generated
                 """)
        st.subheader("Upload the required excel files")
    
        # Upload necessary excel files and preview uploaded data
        kigyo_col1, kigyo_col2, kigyo_col3 = st.columns([1,1,1])
        
        with kigyo_col1:
            price_list = st.file_uploader("Upload excel file of updated price list of parts", type=["xlsx"])
            if price_list is not None:
                st.write("Preview of Updated Price List:")
                price_list_df = pd.read_excel(price_list)
                st.write(price_list_df)
    
        with kigyo_col2:
            parts_list = st.file_uploader("Upload excel file of parts list", type=["xlsx"])
            if parts_list is not None:
                st.write("Preview of Parts List:")
                parts_list_df = pd.read_excel(parts_list)
                st.write(parts_list_df)
    
        with kigyo_col3:
            inventory_list = st.file_uploader("Upload excel file of updated inventory list", type=["xlsx"])
            if inventory_list is not None:
                st.write("Preview of Updated Inventory List:")
                inventory_list_df = pd.read_excel(inventory_list)
                st.write(inventory_list_df)
        st.write("--------------------------------------------------------")
    
        # Generating the Kigyo Output
        if price_list is not None and parts_list is not None and inventory_list is not None:
            st.subheader("Generate Kigyo Excel File")
            percent_allowance = st.slider("Slide to the desired percent of price allowance", 0, 100, 10)
    
            # Merge excel files
            parts_and_price = parts_list_df.merge(price_list_df, how="left")
            parts_price_inventory = parts_and_price.merge(inventory_list_df, how="left")
    
            # Kigyo Calculations
            kigyo_ouput = parts_price_inventory[["Department", "Process", "Category Name", "Parts List", "Model No.", "Price per Piece", "Quantity", "Quantity Available"]]
            kigyo_ouput["Quantity to Purchase"] = (kigyo_ouput["Quantity"] - kigyo_ouput["Quantity Available"]).apply(lambda x: max(x, 0))
            kigyo_ouput["Purchase Cost"] = kigyo_ouput["Price per Piece"] * kigyo_ouput["Quantity to Purchase"]
            kigyo_ouput["Allowance"] = kigyo_ouput["Purchase Cost"] * (percent_allowance / 100)
            kigyo_ouput["Total Price"] = kigyo_ouput["Purchase Cost"] + kigyo_ouput["Allowance"]
            kigyo_ouput["Used Inventory"] = kigyo_ouput["Quantity"] - kigyo_ouput["Quantity to Purchase"]
            kigyo_ouput["Savings from Inventory"] = kigyo_ouput["Price per Piece"] * kigyo_ouput["Used Inventory"]
    
        # Generating the Updated Inventory minus the Used Parts
            inventory_update = inventory_list_df.merge(parts_list_df, how="left")
            inventory_update["Quantity"] = inventory_update["Quantity"].fillna(0)
            inventory_update["New Quantity Available"] = (inventory_update["Quantity Available"] - inventory_update["Quantity"]).apply(lambda x: max(x, 0))
            inventory_final = inventory_update[["Parts List", "New Quantity Available"]]
            inventory_final_pd = pd.DataFrame(inventory_final)
            inventory_final_pd.rename(columns={"New Quantity Available":"Quantity Available"}, inplace=True)
            inventory_final_pd.set_index("Parts List", inplace=True)
            st.write("--------------------------------------------------------")
    
            # Display Kigyo Output
            st.subheader("Preview of generated Kigyo")
            st.write(kigyo_ouput)
            st.write("Total Purchase Cost: " + str(kigyo_ouput["Purchase Cost"].sum()))
            st.write("Total Allowance Cost: " + str(kigyo_ouput["Allowance"].sum()))
            st.write("Total Price (Cost + Allowance): " + str(kigyo_ouput["Total Price"].sum()))
            st.write("Total saved from inventory: " + str(kigyo_ouput["Savings from Inventory"].sum()))
    
            # Download Excel File
            @st.cache_data
            def convert_kigyo(kigyo):
                return kigyo.to_csv().encode("utf-8")
            
            generated_kigyo = convert_kigyo(kigyo_ouput)
    
            st.download_button(
                label="Download Kigyo as CSV",
                data=generated_kigyo,
                file_name="Generated Kigyo.csv",
                mime="text/csv"
            )
            st.write("--------------------------------------------------------")
    
            # Display Generated Inventory Update
            st.subheader("Updated Inventory List")
            st.write(inventory_final_pd)
    
            # Download Inventory Excel File
            @st.cache_data
            def convert_kigyo(inventory):
                return inventory.to_csv().encode("utf-8")
            
            generated_inventory = convert_kigyo(inventory_final_pd)
    
            st.download_button(
                label="Download Inventory as CSV",
                data=generated_inventory,
                file_name="Updated Inventory.csv",
                mime="text/csv"
            )
    
            st.write("--------------------------------------------------------")
    
        # Generating the Table of Sub Kigyo No.
            
            st.subheader("Generating Sub Kigyo No. Output")
            kigyo_sub_col1, kigyo_sub_col2, kigyo_sub_col3, kigyo_sub_col4 = st.columns([1.5,0.1,4,1.5])
            
            with kigyo_sub_col1:
                # Assigning Kigyo Sub No. for each process
                st.subheader("Sub Kigyo No.")
                # Generating all unique processes
                kigyo_output_copy = kigyo_ouput.copy()
    
                unique_process = kigyo_output_copy["Process"].unique()
    
                for process in unique_process:
                    # Get the selected Sub Kigyo No. for the current category
                    selected_sub_kigyo = st.selectbox(f"Select Sub Kigyo No. for {process}",
                                                    ("900", "901", "001", "002", "003", "004", "005",
                                                    "006", "007", "008", "009", "010"), key=process)
                    
                    # Add a new column "Sub Kigyo No." and set the selected value for the current category
                    kigyo_output_copy.loc[kigyo_output_copy["Process"] == process, "Sub Kigyo No."] = selected_sub_kigyo
    
                # Now, kigyo_output_copy DataFrame contains the new column "Sub Kigyo No."
                    
            with kigyo_sub_col3:
                # Create final Sub Kigyo Output
                sub_kigyo_output = kigyo_output_copy[["Process", "Category Name", "Sub Kigyo No."]]
    
                # Renaming and adding some columns
                sub_kigyo_output["Item Name"] = kigyo_output_copy["Parts List"]
                sub_kigyo_output["Quantity"] = kigyo_output_copy["Quantity to Purchase"]
                sub_kigyo_output["Average Price per Unit"] = kigyo_output_copy["Price per Piece"]
                sub_kigyo_output["Price"] = sub_kigyo_output["Quantity"] * sub_kigyo_output["Average Price per Unit"]
                
                # Dropping rows with zero value in Quantity column
                sub_kigyo_output = sub_kigyo_output[sub_kigyo_output["Quantity"] != 0]
    
                # Rearranging Columns
                sub_kigyo_output = sub_kigyo_output[["Process", "Category Name", "Item Name", "Average Price per Unit",
                                                    "Sub Kigyo No.", "Quantity", "Price"]]
            
                # Display Sub Kigyo Output
                st.subheader("Sub Kigyo No. Output")
                st.write(sub_kigyo_output)
    
            with kigyo_sub_col4:        
                # Get sum of price per unique values of Sub Kigyo No.
                st.subheader("Subtotals")
                sub_kigyo_totals = kigyo_output_copy.groupby("Sub Kigyo No.")["Total Price"].sum()
                sub_kigyo_totals = pd.DataFrame(sub_kigyo_totals)
                sub_kigyo_totals = sub_kigyo_totals[sub_kigyo_totals["Total Price"] != 0]
                st.write(sub_kigyo_totals)
    
    # Kigyo Calculator -- without Inventory Data
    if automation_app == "Kigyo Generator (without Inventory Data)":
        # App Title and Subheader
        st.title("Kigyo Generator")
        st.write("""How to use: Upload required excel files.
                Drag the allowance slider to your desired price allowance in %.
                The Kigyo output will be automatically generated
                """)
        st.subheader("Upload the required excel files")
    
        # Upload necessary excel files and preview uploaded data
        kigyo_col1, kigyo_col2 = st.columns([1,1])
        
        with kigyo_col1:
            price_list = st.file_uploader("Upload excel file of updated price list of parts", type=["xlsx"])
            if price_list is not None:
                st.write("Preview of Updated Price List:")
                price_list_df = pd.read_excel(price_list)
                st.write(price_list_df)
    
        with kigyo_col2:
            parts_list = st.file_uploader("Upload excel file of parts list", type=["xlsx"])
            if parts_list is not None:
                st.write("Preview of Parts List:")
                parts_list_df = pd.read_excel(parts_list)
                st.write(parts_list_df)
    
        st.write("--------------------------------------------------------")
    
        # Generating the Kigyo Output
        if price_list is not None and parts_list is not None:
            st.subheader("Generate Kigyo Excel File")
            percent_allowance = st.slider("Slide to the desired percent of price allowance", 0, 100, 10)
    
            # Merge excel files
            parts_and_price = parts_list_df.merge(price_list_df, how="left")
    
            # Kigyo Calculations
            kigyo_ouput = parts_and_price[["Department", "Process", "Category Name", "Parts List", "Model No.", "Price per Piece", "Quantity"]]
            kigyo_ouput["Quantity to Purchase"] = (kigyo_ouput["Quantity"])
            kigyo_ouput["Purchase Cost"] = kigyo_ouput["Price per Piece"] * kigyo_ouput["Quantity to Purchase"]
            kigyo_ouput["Allowance"] = kigyo_ouput["Purchase Cost"] * (percent_allowance / 100)
            kigyo_ouput["Total Price"] = kigyo_ouput["Purchase Cost"] + kigyo_ouput["Allowance"]
            st.write("--------------------------------------------------------")
    
            # Display Kigyo Output
            st.subheader("Preview of generated Kigyo")
            st.write(kigyo_ouput)
            st.write("Total Purchase Cost: " + str(kigyo_ouput["Purchase Cost"].sum()))
            st.write("Total Allowance Cost: " + str(kigyo_ouput["Allowance"].sum()))
            st.write("Total Price (Cost + Allowance): " + str(kigyo_ouput["Total Price"].sum()))
    
            # Download Excel File
            @st.cache_data
            def convert_kigyo(kigyo):
                return kigyo.to_csv().encode("utf-8")
            
            generated_kigyo = convert_kigyo(kigyo_ouput)
    
            st.download_button(
                label="Download Kigyo as CSV",
                data=generated_kigyo,
                file_name="Generated Kigyo.csv",
                mime="text/csv"
            )
            st.write("--------------------------------------------------------")
    
        # Generating the Table of Sub Kigyo No.
            
            st.subheader("Generating Sub Kigyo No. Output")
            kigyo_sub_col1, kigyo_sub_col2, kigyo_sub_col3, kigyo_sub_col4 = st.columns([1.5,0.1,4,1.5])
            
            with kigyo_sub_col1:
                # Assigning Kigyo Sub No. for each process
                st.subheader("Sub Kigyo No.")
                # Generating all unique processes
                kigyo_output_copy = kigyo_ouput.copy()
    
                unique_process = kigyo_output_copy["Process"].unique()
    
                for process in unique_process:
                    # Get the selected Sub Kigyo No. for the current category
                    selected_sub_kigyo = st.selectbox(f"Select Sub Kigyo No. for {process}",
                                                    ("900", "901", "001", "002", "003", "004", "005",
                                                    "006", "007", "008", "009", "010"), key=process)
                    
                    # Add a new column "Sub Kigyo No." and set the selected value for the current category
                    kigyo_output_copy.loc[kigyo_output_copy["Process"] == process, "Sub Kigyo No."] = selected_sub_kigyo
    
                # Now, kigyo_output_copy DataFrame contains the new column "Sub Kigyo No."
                    
            with kigyo_sub_col3:
                # Create final Sub Kigyo Output
                sub_kigyo_output = kigyo_output_copy[["Process", "Category Name", "Sub Kigyo No."]]
    
                # Renaming and adding some columns
                sub_kigyo_output["Item Name"] = kigyo_output_copy["Parts List"]
                sub_kigyo_output["Quantity"] = kigyo_output_copy["Quantity to Purchase"]
                sub_kigyo_output["Average Price per Unit"] = kigyo_output_copy["Price per Piece"]
                sub_kigyo_output["Price"] = sub_kigyo_output["Quantity"] * sub_kigyo_output["Average Price per Unit"]
                
                # Dropping rows with zero value in Quantity column
                sub_kigyo_output = sub_kigyo_output[sub_kigyo_output["Quantity"] != 0]
    
                # Rearranging Columns
                sub_kigyo_output = sub_kigyo_output[["Process", "Category Name", "Item Name", "Average Price per Unit",
                                                    "Sub Kigyo No.", "Quantity", "Price"]]
            
                # Display Sub Kigyo Output
                st.subheader("Sub Kigyo No. Output")
                st.write(sub_kigyo_output)
    
            with kigyo_sub_col4:        
                # Get sum of price per unique values of Sub Kigyo No.
                st.subheader("Subtotals")
                sub_kigyo_totals = kigyo_output_copy.groupby("Sub Kigyo No.")["Total Price"].sum()
                sub_kigyo_totals = pd.DataFrame(sub_kigyo_totals)
                sub_kigyo_totals = sub_kigyo_totals[sub_kigyo_totals["Total Price"] != 0]
                st.write(sub_kigyo_totals)

st.write("______________________________________________________________")

with open('style.css') as f:
    css = f.read()

st.markdown(f'<style>{css}</style>', unsafe_allow_html=True)

  
