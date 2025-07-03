import streamlit as st
import pandas as pd
import io
from datetime import date

DATA_FILE = 'timesheet_data.xlsx'

# Helper to load or create the data file
def load_data():
    try:
        df = pd.read_excel(DATA_FILE)
    except FileNotFoundError:
        df = pd.DataFrame(columns=[
            'Date', 'Employee', 'Project/Site',
            'Job Function 1', 'Hours Worked 1',
            'Job Function 2', 'Hours Worked 2',
            'Travel Time'
        ])
    return df

def save_data(df):
    df.to_excel(DATA_FILE, index=False)

st.title("Employee Time Tracking App")

# --- Time Entry Form ---
st.header("Enter Time Worked")
with st.form("entry_form"):
    entry_date = st.date_input("Date", value=date.today())
    employee = st.text_input("Employee Name")
    project = st.text_input("Project/Site")
    job1 = st.text_input("Job Function 1")
    hours1 = st.number_input("Hours Worked 1", min_value=0.0, step=0.25)
    job2 = st.text_input("Job Function 2 (optional)")
    hours2 = st.number_input("Hours Worked 2 (optional)", min_value=0.0, step=0.25)
    travel = st.number_input("Travel Time (hours)", min_value=0.0, step=0.25)
    submitted = st.form_submit_button("Submit Entry")

    if submitted:
        df = load_data()
        new_row = {
            'Date': entry_date,
            'Employee': employee,
            'Project/Site': project,
            'Job Function 1': job1,
            'Hours Worked 1': hours1,
            'Job Function 2': job2,
            'Hours Worked 2': hours2,
            'Travel Time': travel
        }
        # Use pd.concat instead of append (append is deprecated)
        df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
        save_data(df)
        st.success("Entry saved!")

# --- Reporting Section ---
st.header("Time Report")
df = load_data()

if not df.empty:
    # Transform data to long format for reporting
    records = []
    for _, row in df.iterrows():
        if pd.notna(row['Job Function 1']) and row['Job Function 1'] and row['Hours Worked 1'] > 0:
            records.append({
                'Date': row['Date'],
                'Employee': row['Employee'],
                'Project/Site': row['Project/Site'],
                'Job Function': row['Job Function 1'],
                'Hours Worked': row['Hours Worked 1']
            })
        if pd.notna(row['Job Function 2']) and row['Job Function 2'] and row['Hours Worked 2'] > 0:
            records.append({
                'Date': row['Date'],
                'Employee': row['Employee'],
                'Project/Site': row['Project/Site'],
                'Job Function': row['Job Function 2'],
                'Hours Worked': row['Hours Worked 2']
            })
        if pd.notna(row['Travel Time']) and row['Travel Time'] > 0:
            records.append({
                'Date': row['Date'],
                'Employee': row['Employee'],
                'Project/Site': row['Project/Site'],
                'Job Function': 'Travel Time',
                'Hours Worked': row['Travel Time']
            })
    report_df = pd.DataFrame(records)
    st.dataframe(report_df)

    # Download report as Excel using an in-memory buffer
    output = io.BytesIO()
    report_df.to_excel(output, index=False, engine='openpyxl')
    output.seek(0)
    st.download_button(
        label="Download Report as Excel",
        data=output,
        file_name='time_report.xlsx',
        mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
else:
    st.info("No data entered yet.")
