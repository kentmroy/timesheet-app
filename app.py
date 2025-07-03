import streamlit as st
import pandas as pd
import io
from datetime import date

DATA_FILE = 'timesheets-v2-chatgpt.xlsx'

def load_data():
    try:
        df = pd.read_excel(DATA_FILE)
    except FileNotFoundError:
        df = pd.DataFrame(columns=[
            'Date', 'Project/Site', 'Name', 'Job Function 1', 'Hours Worked 1',
            'Job Function 2', 'Hours Worked 2', 'What was the total drive time for the day?'
        ])
    return df

def save_data(df):
    df.to_excel(DATA_FILE, index=False)

st.title("Employee Time Tracking App")

df_existing = load_data()

# Build dropdown options from your actual columns
name_options = sorted(df_existing['Name'].dropna().unique().tolist())
site_options = sorted(df_existing['Project/Site'].dropna().unique().tolist())
job_function_options = sorted(
    pd.concat([
        df_existing['Job Function 1'].dropna(),
        df_existing['Job Function 2'].dropna()
    ]).unique().tolist()
)

# --- Time Entry Form ---
st.header("Enter Time Worked")

# Use session state to reset form after submission
if "form_submitted" not in st.session_state:
    st.session_state["form_submitted"] = False

with st.form("entry_form"):
    entry_date = st.date_input("Date", value=date.today(), key="entry_date")
    employee = st.selectbox("Employee Name", options=[""] + name_options, key="employee")
    project = st.selectbox("Project/Site", options=[""] + site_options, key="project")
    job1 = st.selectbox("Job Function 1", options=[""] + job_function_options, key="job1")
    hours1 = st.number_input("Hours Worked 1", min_value=0.0, step=0.25, key="hours1")
    job2 = st.selectbox("Job Function 2 (optional)", options=[""] + job_function_options, key="job2")
    hours2 = st.number_input("Hours Worked 2 (optional)", min_value=0.0, step=0.25, key="hours2")
    travel = st.number_input("Travel Time (hours)", min_value=0.0, step=0.25, key="travel")
    submitted = st.form_submit_button("Submit Entry")

    if submitted:
        df = load_data()
        new_row = {
            'Date': entry_date,
            'Project/Site': project,
            'Name': employee,
            'Job Function 1': job1,
            'Hours Worked 1': hours1,
            'Job Function 2': job2,
            'Hours Worked 2': hours2,
            'What was the total drive time for the day?': travel
        }
        df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
        save_data(df)
        st.session_state["form_submitted"] = True
        st.success("Entry saved!")

# --- Reset form fields after submission ---
if st.session_state.get("form_submitted", False):
    st.session_state["entry_date"] = date.today()
    st.session_state["employee"] = ""
    st.session_state["project"] = ""
    st.session_state["job1"] = ""
    st.session_state["hours1"] = 0.0
    st.session_state["job2"] = ""
    st.session_state["hours2"] = 0.0
    st.session_state["travel"] = 0.0
    st.session_state["form_submitted"] = False
    st.experimental_rerun()

# --- Reporting Section ---
st.header("Time Report")
df = load_data()

if not df.empty:
    records = []
    for _, row in df.iterrows():
        if pd.notna(row['Job Function 1']) and row['Job Function 1'] and row['Hours Worked 1'] > 0:
            records.append({
                'Date': row['Date'],
                'Name': row['Name'],
                'Project/Site': row['Project/Site'],
                'Job Function': row['Job Function 1'],
                'Hours Worked': float(row['Hours Worked 1'])
            })
        if pd.notna(row['Job Function 2']) and row['Job Function 2'] and row['Hours Worked 2'] > 0:
            records.append({
                'Date': row['Date'],
                'Name': row['Name'],
                'Project/Site': row['Project/Site'],
                'Job Function': row['Job Function 2'],
                'Hours Worked': float(row['Hours Worked 2'])
            })
        if pd.notna(row['What was the total drive time for the day?']) and row['What was the total drive time for the day?'] > 0:
            records.append({
                'Date': row['Date'],
                'Name': row['Name'],
                'Project/Site': row['Project/Site'],
                'Job Function': 'Travel Time',
                'Hours Worked': float(row['What was the total drive time for the day?'])
            })
    report_df = pd.DataFrame(records)
    # Format for display (string, always two decimals)
    report_df["Hours Worked"] = report_df["Hours Worked"].map(lambda x: f"{x:.2f}")
    st.dataframe(report_df)
    # Format for Excel (float, rounded to two decimals)
    report_df_excel = report_df.copy()
    report_df_excel["Hours Worked"] = report_df_excel["Hours Worked"].astype(float).round(2)
    output = io.BytesIO()
    report_df_excel.to_excel(output, index=False, engine='openpyxl')
    output.seek(0)
    st.download_button(
        label="Download Report as Excel",
        data=output,
        file_name='time_report.xlsx',
        mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
else:
    st.info("No data entered yet.")
