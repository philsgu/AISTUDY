import streamlit as st
import pandas as pd
from datetime import datetime
from oauth2client.service_account import ServiceAccountCredentials
import gspread


today = datetime.today().strftime("%Y-%m-%d")
st.title("AI Study Tally Results Dashboard")

st.subheader(today)

scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
credentials = ServiceAccountCredentials.from_json_keyfile_name('accesspysheet-e2f8e30d6903.json', scope)
client = gspread.authorize(credentials)

spreadsheet = client.open_by_url('https://docs.google.com/spreadsheets/d/1O032uW-6c4QX-zd5ZUfLIuuhQacLjGy1rw6htGao6PY/edit?usp=sharing')
sheet = spreadsheet.get_worksheet(0)
data = sheet.get_all_values()
df = pd.DataFrame(data[1:], columns=data[0])
df2 = pd.read_csv('GME_2024_Residents.csv')
# Rename the column 'What is your samc email?' to 'Email' in df
df.rename(columns={'What is your samc email?': 'Email'}, inplace=True)
# Convert all email values to lowercase and remove any extraneous characters in df
df['Email'] = df['Email'].str.lower().str.strip()

# Convert all email values to lowercase and remove any extraneous characters in df2
df2['Email'] = df2['Email'].str.lower().str.strip()

# incomplete
filtered = df2[~df2['Email'].isin(df['Email'])]
print(len(filtered))

st.subheader(f"Total INCOMPLETE Survey: {len(filtered)}/{len(df2)}")
st.write(f"Percentage Incomplete: {(len(filtered)/len(df2))*100:.2f}%")
st.write(f"Percentage Complete: {((len(df2)-len(filtered))/len(df2))*100:.2f}%")

def create_table(dept_name, filtered=filtered, df2=df2):
    st.divider()
    st.subheader(f"{dept_name} INCOMPLETE Survey")
    dept_df = filtered[filtered['Program'] == dept_name][['FirstName', 'LastName', 'Program', 'Status', 'Email']]
    dept_df.index = dept_df.index + 1  # Start index with 1
    st.write(f'Incomplete Survey Count: {len(dept_df)}/{len(df2[df2["Program"] == dept_name])}')
    return st.dataframe(dept_df)

for dept in df2['Program'].unique():
    create_table(dept)    
    
    