import streamlit as st
import pandas as pd
import io
from datetime import date

DATA_FILE = 'timesheet_data.xlsx'

def load_data():
    try:
        df = pd.read_excel(DATA_FILE)
    except FileNotFoundError:
        df = pd.DataFrame(columns=[
            'Date', 'Name', 'Project/Site',
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
if "form_submitted" not in st.session_state:
    st.session_state["form_submitted"] = False

with st.form("entry_form"):
    entry_date = st.date_input("Date", value=date.today(), key="entry_date")
    employee = st.selectbox("Employee Name", options=[""] + sorted(load_data()['Name'].dropna().unique().tolist()), key="employee")
    project = st.selectbox("Project/Site", options=[""] + sorted(load_data()['Project/Site'].dropna().unique().tolist()), key="project")
    job1 = st.selectbox("Job Function 1", options=[""] + sorted(pd.concat([load_data()['Job Function 1'].dropna(), load_data()['Job Function 2'].dropna()]).unique().tolist()), key="job1")
    hours1 = st.number_input("Hours Worked 1", min_value=0.0, step=0.25, key="hours1")
    job2 = st.selectbox("Job Function 2 (optional)", options=[""] + sorted(pd.concat([load_data()['Job Function 1'].dropna(), load_data()['Job Function 2'].dropna()]).unique().tolist()), key="job2")
    hours2 = st.number_input("Hours Worked 2 (optional)", min_value=0.0, step=0.25, key="hours2")
    travel = st.number_input("Travel Time (hours)", min_value=0.0, step=0.25, key="travel")
    submitted = st.form_submit_button("Submit Entry")

    if submitted:
        df = load_data()
        new_row = {
            'Date': entry_date,
            'Name': employee,
            'Project/Site': project,
            'Job Function 1': job1,
            'Hours Worked 1': hours1,
            'Job Function 2': job2,
            'Hours Worked 2': hours2,
            'Travel Time': travel
        }
        df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
        save_data(df)
        st.session_state["form_submitted"] = True
        st.success("Entry saved!")

# --- Reset form fields after submission ---
if st.session_state.get("form_submitted", False):
    # Reset all form fields
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
        if pd.notna(row['Travel Time']) and row['Travel Time'] > 0:
            records.append({
                'Date': row['Date'],
                'Name': row['Name'],
                'Project/Site': row['Project/Site'],
                'Job Function': 'Travel Time',
                'Hours Worked': float(row['Travel Time'])
            })
    report_df = pd.DataFrame(records)
    report_df["Hours Worked"] = report_df["Hours Worked"].map(lambda x: f"{x:.2f}")
    st.dataframe(report_df)
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