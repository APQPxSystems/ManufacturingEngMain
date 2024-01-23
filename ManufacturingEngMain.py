# Full systems engineering web application

# Import Libraries
import streamlit as st
import pandas as pd
import xlsxwriter
from io import BytesIO

# Streamlit Configurations
st.set_page_config(page_title="ME Dept Apps", layout="wide")

# App title and info
st.title("Manufacturing Engineering Dep't. Web App")

st.write("""This web app is a collection of Manufacturing Engineering Department's automation tools.
         This runs on streamlit's cloud server and is not connected to any database.
         Therefore, any data uploaded will not be saved or collected and will vanish everytime the app is refreshed.""") 

# Automation App Selection
automation_app = st.selectbox("Select an automation app.", ["Sub Balancing", 
                                                            "Kigyo Calculator"])

# Sub Balancing App
if automation_app == "Sub Balancing":   
    # App title
    st.title("Sub Balancing App")

    # Upload excel file
    raw_data = st.file_uploader("Upload sub balancing data", type=["xlsx"])
    st.write("--------------------------------------")

    # Read and process uploaded excel file
    if raw_data is not None:
        raw_data2 = pd.read_excel(raw_data)

        # Ordering columns
        raw_data3 = raw_data2[["SubNo", "Wi_No", "Ins_L", "Ins_R", "ConnNo_L", "ConnNo_R"]]

        # Group data by "Sub No"
        grouped_data = raw_data3.groupby("SubNo")

        # Calculate grand total
        grand_total = len(raw_data3)

        # Display tables for each "Sub No"
        for sub_no, group_data in grouped_data:
            count_wire_no = len(group_data)
            percent_of_grand_total = (count_wire_no / grand_total) * 100
            st.subheader(f"Sub No: {sub_no} - Wire Count: {count_wire_no} ({percent_of_grand_total:.2f}% of Total Insertions)")
            st.write(group_data)

        
# Kigyo Calculator
if automation_app == "Kigyo Calculator":
    # App Title and Subheader
    st.title("Kigyo Calculator")
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

    # Generating the Kigyo Output
    if price_list is not None and parts_list is not None and inventory_list is not None:
        st.subheader("Generate Kigyo Excel File")
        percent_allowance = st.slider("Slide to the desired percent of price allowance", 0, 100, 10)

        # Merge excel files
        parts_and_price = parts_list_df.merge(price_list_df, how="left")
        parts_price_inventory = parts_and_price.merge(inventory_list_df, how="left")

        # Kigyo Calculations
        kigyo_ouput = parts_price_inventory[["Parts Type", "Parts List", "Price per Piece", "Quantity", "Quantity Available"]]
        kigyo_ouput["Quantity to Purchase"] = (kigyo_ouput["Quantity"] - kigyo_ouput["Quantity Available"]).apply(lambda x: max(x, 0))
        kigyo_ouput["Purchase Cost"] = kigyo_ouput["Price per Piece"] * kigyo_ouput["Quantity to Purchase"]
        kigyo_ouput["Allowance"] = kigyo_ouput["Purchase Cost"] * (percent_allowance / 100)
        kigyo_ouput["Total Price"] = kigyo_ouput["Purchase Cost"] + kigyo_ouput["Allowance"]

        # Display Kigyo Output
        st.write("Preview of generated Kigyo")
        st.write(kigyo_ouput)

        # When the button is clicked, save the dataframe and create a download link
        if download_button:
            excel_file = download_excel(kigyo_ouput, "Kigyo_Output.xlsx")
            st.download_button(label="Download as Excel", data=excel_file, file_name="Kigyo Output.xlsx", key=download_button)

