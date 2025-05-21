import streamlit as st
import pandas as pd

# Configuration
st.set_page_config(layout="wide")

# CSS styling
st.markdown("""
    <style>
    #MainMenu {visibility:hidden;}
    footer {visibility:hidden;}
    header {visibility:hidden;}
    .block-container {padding-top: 0rem; padding-bottom: 0rem;}
    </style>
""", unsafe_allow_html=True)

footer = """
<style>
.footer {
    position: fixed;
    left: 0;
    bottom: 0;
    width: 100%;
    background-color: black;
    color: white;
    align-items: center;
    padding: 3px 10px;
    font-size: 12px !important;
    z-index: 1000;
}

.footer-center {
    text-align: left;
}

</style>

<div class="footer">
    <div class="footer-center">&copy; Kent Katigbak | rev. 1.0 | 2025</div>
</div>
"""

st.markdown(footer, unsafe_allow_html=True)

# Sort by selected columns
def multi_level_sort(df, sort_columns):
    return df.sort_values(by=sort_columns, ascending=True)

# Extract groups where A-columns are same and B-columns are all different
def extract_filtered_consecutive_groups(df, columns_same, columns_diff):
    # Step 1: Detect changes in columns_same (Group A)
    change = pd.Series(False, index=df.index)
    for col in columns_same:
        change |= df[col] != df[col].shift()
    group = change.cumsum()

    # Assign group number
    df['_group'] = group

    # Step 2: Check each group for conditions
    filtered_blocks = []
    for grp_id, grp_df in df.groupby('_group'):
        if len(grp_df) <= 1:
            continue  # Only keep groups longer than 1

        # Check all A-columns are same (they should be due to grouping, but safe to recheck)
        same_a = all(grp_df[col].nunique() == 1 for col in columns_same)
        
        # Check all B-columns are different (nunique should equal group length)
        diff_b = all(grp_df[col].nunique() == len(grp_df) for col in columns_diff) if columns_diff else True

        if same_a and diff_b:
            filtered_blocks.append(grp_df)

    # Combine all valid groups
    result_df = pd.concat(filtered_blocks) if filtered_blocks else pd.DataFrame(columns=df.columns)
    return result_df.drop(columns=['_group'], errors='ignore')

# Streamlit UI
st.title("Advanced Wire Data Sorting App")

# Upload
uploaded_file = st.file_uploader("Upload an Excel file (.xls)", type='xls')

if uploaded_file:
    df = pd.read_excel(uploaded_file)
    # st.subheader("Uploaded Data")
    # st.dataframe(df)

    # Multiselect for "same" columns (Group A)
    columns_same = st.multiselect("Select columns for SAME consecutive values (Group A):", options=df.columns)

    # Multiselect for "different" columns (Group B)
    columns_diff = st.multiselect("Select columns for DIFFERENT consecutive values (Group B):", options=df.columns)

    if columns_same:
        # Sort
        sorted_df = multi_level_sort(df, columns_same + columns_diff)
        # st.subheader("Sorted Data")
        # st.dataframe(sorted_df)

        # Filter
        filtered_df = extract_filtered_consecutive_groups(sorted_df, columns_same, columns_diff)
        st.subheader("Output Table")
        st.dataframe(filtered_df)

