# Full systems engineering web application

# Import Libraries
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from io import BytesIO

# Streamlit Configurations
st.set_page_config(page_title="ME Dept Apps", layout="wide")

# App title and info
st.title("Manufacturing Engineering Dep't. Web App")

st.write("""This web app is a collection of Manufacturing Engineering Department's automation tools.
         This runs on streamlit's cloud server and is not connected to any database.
         Therefore, any data uploaded will not be saved or collected and will vanish everytime the app is refreshed.""") 
st.write("--------------------------------------------------------")

# Automation App Selection
automation_app = st.selectbox("Select an automation app.", ["Sub Balancing", 
                                                            "Kigyo Generator",
                                                            "FMEA and QCP Matrix Date Calculator",
                                                           "PDCA Viewer"])
st.write("--------------------------------------------------------")

# Sub Balancing App
if automation_app == "Sub Balancing":   
    # App title
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

        # Add a download button for all grouped data
            st.write("------------------------------")
        download_all_button = st.button("Download Generated Data")
        if download_all_button:
            # Create a BytesIO object to store the Excel file
            excel_buffer_all = BytesIO()

            # Use pandas to_excel method to write the raw_data3 to the BytesIO object
            with pd.ExcelWriter(excel_buffer_all, engine='xlsxwriter') as writer_all:
                for sub_no, group_data in grouped_data:
                    group_data.to_excel(writer_all, sheet_name=f"SubNo_{sub_no}", index=False)

            # Set the cursor to the beginning of the BytesIO object
            excel_buffer_all.seek(0)

            # Add a download link for the Excel file
            st.download_button(
                label="Download All Generated Data as Excel File",
                data=excel_buffer_all,
                file_name="All_Grouped_Data.xlsx",
                key="download_button_all"
            )

# Kigyo Calculator
if automation_app == "Kigyo Generator":
    # App Title and Subheader
    st.title("Kigyo Generator")
    st.write("""How to use: Upload required excel files.
             Drag the allowance slider to your desired price allowance in %.
             The Kigyo output will automatically generated
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
        kigyo_ouput.set_index("Parts List", inplace=True)
        st.write("--------------------------------------------------------")

        # Display Kigyo Output
        st.subheader("Preview of generated Kigyo")
        st.write(kigyo_ouput)

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
    # Generating the Updated Inventory minus the Used Parts
    if price_list is not None and parts_list is not None and inventory_list is not None:
        st.subheader("Updated Inventory List")
        inventory_update = inventory_list_df.merge(parts_list_df, how="left")
        inventory_update["Quantity"] = inventory_update["Quantity"].fillna(0)
        inventory_update["New Quantity Available"] = (inventory_update["Quantity Available"] - inventory_update["Quantity"]).apply(lambda x: max(x, 0))
        inventory_final = inventory_update[["Parts List", "New Quantity Available"]]
        inventory_final_pd = pd.DataFrame(inventory_final)
        inventory_final_pd.rename(columns={"New Quantity Available":"Quantity Available"}, inplace=True)
        inventory_final_pd.set_index("Parts List", inplace=True)

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

# PDCA Viewer
if automation_app == "PDCA Viewer":
         st.title("PDCA Summary")

         pdca_file = pd.read_excel("Sub Balancing Sample.csv")

         st.write(pdca_file)
