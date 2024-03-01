# Full systems engineering web application
# Systems Engineering Section - Manufacturing Engineering Department
# Kent Katigbak - Staff

# Import Libraries
# import hmac
import streamlit as st
import pandas as pd
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
st.markdown("<p class='app_sub_title'>ME DEPARTMENT | SYSTEMS ENGINEERING</p>", unsafe_allow_html=True)
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

# def check_password():
#     """Returns `True` if the user had the correct password."""

#     def password_entered():
#         """Checks whether a password entered by the user is correct."""
#         if hmac.compare_digest(st.session_state["password"], st.secrets["password"]):
#             st.session_state["password_correct"] = True
#             del st.session_state["password"]  # Don't store the password.
#         else:
#             st.session_state["password_correct"] = False

#     # Return True if the password is validated.
#     if st.session_state.get("password_correct", False):
#         return True

#     # Show input for password.
#     st.text_input(
#         "ENTER PASSWORD TO OPEN THE WEB APP", type="password", on_change=password_entered, key="password"
#     )
#     if "password_correct" in st.session_state:
#         st.error("Password incorrect")
#     return False


# if not check_password():
#     st.stop()  # Do not continue if check_password is not True.
#-------------------------------------------------------------------------------------------

# Automation App Selection
if user_role == "Manufacturing Engineering" and app_key == "MESE24":
    automation_app = st.selectbox("Select an automation app.", ["Home",
                                                                "PDCA Summary Viewer",
                                                                "FMEA PDCA Viewer",
                                                                "Sub Balancing", 
                                                                "Kigyo Generator",
                                                                "FMEA and QCP Matrix Date Calculator",
                                                               "Merge Master Sample Automation"])
elif user_role == "Production" and app_key == "SE24":
    automation_app = st.selectbox("Select an automation app.", ["Home",
                                                                "PDCA Summary Viewer",
                                                                "FMEA PDCA Viewer"])
elif user_role == "Production Engineering" and app_key == "SE24":
    automation_app = st.selectbox("Select an automation app.", ["Home",
                                                                "PDCA Summary Viewer",
                                                                "FMEA PDCA Viewer"])
elif user_role == "Quality Assurance" and app_key == "SE24":
    automation_app = st.selectbox("Select an automation app.", ["Home",
                                                                "PDCA Summary Viewer",
                                                                "FMEA PDCA Viewer"])
else:
    st.subheader("Department/ Department Key Required")
    st.write("Please enter the department key that matches with your chosen department.")
    automation_app = ""

st.write("--------------------------------------------------------")

# Home
if automation_app == "Home":
    st.write("")
  
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
      raw_data3 = raw_data2[["SubNo", "Wi_No", "Ins_L", "Ins_R", "ConnNo_L", "ConnNo_R"]]
  
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
          st.write("------------------------------")

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

#FMEA PDCA Viewer
if automation_app == "FMEA PDCA Viewer":
    # Landing Page
    st.title("FMEA PDCA Viewer")

    # Read FMEA PDCA Excel File
    fmea_pdca = pd.read_csv("FMEA/FMEA_PDCA.csv", encoding="ISO-8859-1")
    
    # Drop Unnecessary Columns
    fmea_pdca = fmea_pdca[["Car Maker", "Car Model", "Line", "Findings",
                            "Items to Check/Action", "Department",
                            "Person in Charge", "Status", "Target Date"]]
        
    # Convert Line Column to String
    fmea_pdca["Line"] = fmea_pdca["Line"].astype(str)
        
    # Convert Target Date to Datetime
    fmea_pdca["Target Date"] = pd.to_datetime(fmea_pdca["Target Date"], errors="coerce")
    
    department_options = list(fmea_pdca["Department"].unique())
    
    department_selection_container = st.container(border=True)
    with department_selection_container:
        department = st.selectbox("Please select your department:", department_options)
    
    first_part_container = st.container(border=True)
    with first_part_container:
        if department != "___________________________":
            # First Part -- General
            st.title(f"Here's the FMEA Dashboard for {department}")
            
            department_fmea_pdca = fmea_pdca[fmea_pdca["Department"].isin([department])]
            
            # First Chart --- Open and Close Items per Car Maker
            open_count = len(department_fmea_pdca[department_fmea_pdca["Status"]== "OPEN"])
            st.subheader(f"You have {open_count} OPEN items in total!")
            first_chart = alt.Chart(department_fmea_pdca).mark_bar().encode(
                x=alt.X('Car Maker:N', title='Car Maker'),
                y=alt.Y('count():Q', title='Count'),
                color='Status:N'
            ).properties(
                title = f"{department} Status of Items per Car Maker"
            )
            st.altair_chart(first_chart, use_container_width=True)
        
    car_maker_container = st.container(border=True)
    with car_maker_container:
        # Second Part -- Filter by Car Maker
        car_maker = st.selectbox("Select a car maker:", department_fmea_pdca["Car Maker"].unique())
        
        # Filter by Car Maker
        car_maker_department_fmea_pdca = department_fmea_pdca[department_fmea_pdca["Car Maker"].isin([car_maker])]
        
    second_part_container = st.container(border=True)
    with second_part_container:
        # Second Chart --- Status of Each Department per Line
        open_count_2 = len(car_maker_department_fmea_pdca[car_maker_department_fmea_pdca["Status"]== "OPEN"])
        st.subheader(f"You have {open_count_2} OPEN items in {car_maker}!")
        second_chart = alt.Chart(car_maker_department_fmea_pdca).mark_bar().encode(
            x=alt.X('Line:N', title='Line'),
            y=alt.Y('count():Q', title='Count'),
            color='Status:N'
        ).properties(
            title = f"{department} Status of Items per Line in {car_maker}"
        )
        st.altair_chart(second_chart, use_container_width=True)
        
    third_part_container = st.container(border=True)
    with third_part_container:
        # Third Part --- Filter by Line
        line = st.selectbox("Select line:", car_maker_department_fmea_pdca["Line"].unique())
        
        line_cm_dept_fmea_pdca = car_maker_department_fmea_pdca[car_maker_department_fmea_pdca["Line"].isin([line])]
        line_cm_dept_fmea_pdca = line_cm_dept_fmea_pdca[line_cm_dept_fmea_pdca["Status"]=="OPEN"]
        
        # Filter data for delayed items with OPEN status and Target Date less than today
        df_delayed_items = line_cm_dept_fmea_pdca[
            (line_cm_dept_fmea_pdca["Status"] == "OPEN") &
            ((pd.to_datetime(line_cm_dept_fmea_pdca["Target Date"]) < datetime.today()) | line_cm_dept_fmea_pdca["Target Date"].isnull())
        ]
    
        # Display count of delayed items
        st.subheader(f"{len(df_delayed_items)} OPEN Item/s are DELAYED!")
        
        df_final_filter_styled = line_cm_dept_fmea_pdca.style.apply(
            lambda row: ['background-color: red' if row['Status'] == 'OPEN'
                        and (pd.isna(row['Target Date']) or row['Target Date'].date() < date.today()) else
                        'background-color: red' if pd.isna(row['Target Date']) else '' for _ in row],
            axis=1
        )
    
        # Display the DataFrame with Styler
        st.dataframe(df_final_filter_styled)
        
        # Download Button for Final Generated PDCA
        @st.cache_data
        def convert_df(df):
            return df.to_csv().encode("utf-8")
    
        csv = convert_df(line_cm_dept_fmea_pdca)
    
        st.download_button(
            label=f"Download {department} FMEA PDCA OPEN Items on Line {line}",
            data=csv,
            file_name=f"Line {line} FMEA PDCA OPEN Items - {department}.csv",
            mime="text/csv"
        )

# Merge Master Sample
if automation_app == "Merge Master Sample Automation":
  # App Title and Info
  st.title("Merge Master Sample")
  st.markdown("""How to Use: On your .xls file of merge master sample, delete the rows that contain
              the signatories and revisions. Then, unmerge the merged cells within the dataframe. Save the file as .csv.
              Drag and drop the file on the upload box and the data will be automatically edited.""")
  
  # Upload File --- Must Be CSV
  raw_data = st.file_uploader("Upload file here:")
  
  if raw_data is not None:
      raw_data = pd.read_csv(raw_data)
      st.title("Original Data")
      st.write(raw_data)
  
      # Concatenate Column Contents -- Conn, AcceNo, ExteNo into a new column 'Conn'
      raw_data['Conn'] = raw_data['Conn'].astype(str) + raw_data['AcceNo'].astype(str) + raw_data['ExteNo'].astype(str)
  
      # Convert 'Conn' column values to integers, handling NaN values and non-numeric values
      raw_data['Conn'] = pd.to_numeric(raw_data['Conn'].str.replace(r'[^0-9]', '', regex=True), errors='coerce', downcast='integer')
      raw_data["Conn"] = raw_data["Conn"]/10
  
      # Drop the 'AcceNo' and 'ExteNo' columns
      raw_data.drop(["AcceNo", "ExteNo"], axis=1, inplace=True)
      
      # Rename columns after "Attachment Process"
      rename_mapping = {}
      start_renaming = False
  
      for col in raw_data.columns:
          if col == "Attachment Process":
              start_renaming = True
          if start_renaming:
              new_col_name = col.split("(")[0].strip() + "**"
              rename_mapping[col] = new_col_name
  
      raw_data.rename(columns=rename_mapping, inplace=True)
      raw_data = raw_data.rename(columns={'Attachment Process**':"Attachment Process"})
      
      # Replace "●" values with corresponding column names
      for col in raw_data.columns:
          raw_data[col] = raw_data[col].apply(lambda x: col if x == '●' else x)
      
      # Concatenate "Length" to "PartsName" if "Length" has a value
      raw_data['PartsName'] = raw_data.apply(lambda row: f"{row['PartsName']} L={row['Length']}" if pd.notna(row['Length']) else row['PartsName'], axis=1)
  
      # Drop PartsClass, PartsCode, Length, Method, Qty, Attachment Process
      columns_to_drop = ['PartsClass', 'PartsCode', 'Length', 'Method', 'Qty', 'Attachment Process']
      raw_data.drop(columns=columns_to_drop, inplace=True)
      
      # Transpose the DataFrame without including the index
      transposed_data = raw_data.transpose().reset_index(drop=True)
  
      # Define a custom function to shift non-null values upwards
      def shift_cells_up(col):
          non_null_values = col.dropna()
          col[:len(non_null_values)] = non_null_values
          col[len(non_null_values):] = None
          return col
  
      # Apply the custom function to each column
      transposed_data = transposed_data.apply(shift_cells_up, axis=0)
      
      # Display Edited Data
      st.title("Edited Data")
      st.write(transposed_data)
      
      # Download Button
      @st.cache_data
      def convert_df(df):
          # IMPORTANT: Cache the conversion to prevent computation on every rerun
          return df.to_csv().encode('utf-8')
  
      csv = convert_df(transposed_data)
  
      st.download_button(
          label="Download Edited Data as CSV",
          data=csv,
          file_name='MergeMasterSample_Automated.csv',
          mime='text/csv',
      )
    st.write("")
    st.write("")





with open('style.css') as f:
    css = f.read()

st.markdown(f'<style>{css}</style>', unsafe_allow_html=True)
