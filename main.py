import streamlit as st
import pandas as pd
from datetime import datetime
from oauth2client.service_account import ServiceAccountCredentials
import gspread
from supabase import create_client, Client
from st_supabase_connection import SupabaseConnection
from st_login_form import login_form


conn = st.connection("supabase", type=SupabaseConnection)
users = conn.table("Streamlit_Users").select("*").execute()
#st.write(users)

def create_google_url(share_url):
    return share_url.replace("/edit?usp=sharing", "/gviz/tq?tqx=out:csv")

client = login_form(
    user_tablename="Streamlit_Users",
    username_col="username",
    password_col="password",
    constrain_password=True,
    login_error_message="🔐 Incorrect username or password",
    create_title="🚀 Create New Account",
    login_title="🔑 Login with Existing Account",
    allow_guest=False,
    allow_create=False,

)
# Handle authentication status
if st.session_state["authenticated"]:
    # Logout button
    if st.button("🚪 Logout"):
        st.session_state.authenticated = False
        st.session_state.username = None
        st.rerun()
    if st.session_state["username"]:
        st.success(f"Welcome back, {st.session_state['username']}!")
        # Your protected content for logged-in users
        sheet1 = st.secrets["Google_Sheet"]['sheet1']
        sheet2 = st.secrets["Google_Sheet"]['sheet2']
        json_key = st.secrets["Google_Secret"]

        today = datetime.today().strftime("%m-%d-%Y")
        st.title("AI Study Dashboard")
        st.subheader("This dashboard shows the number of incomplete surveys for each department.")

        st.image('tallyai-400_50.png', caption='https://tinyurl.com/tallyai')

        st.subheader(today)

        # scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
        # credentials = ServiceAccountCredentials.from_json_keyfile_dict(json_key, scope)
        # client = gspread.authorize(credentials)

        # spreadsheet = client.open_by_key(sheet1)
        # sheet = spreadsheet.get_worksheet(0)
        # data = sheet.get_all_values()

        # spreadsheet2 = client.open_by_key(sheet2)
        # sheet2 = spreadsheet2.get_worksheet(0)
        # data2 = sheet2.get_all_values()

        df = pd.read_csv(create_google_url(sheet1)) #pd.DataFrame(data[1:], columns=data[0])
        df2 = pd.read_csv(create_google_url(sheet2)) #pd.DataFrame(data2[1:], columns=data2[0])
        # Rename the column 'What is your samc email?' to 'Email' in df
        df.rename(columns={'What is your SAMC email?': 'Email'}, inplace=True)
        df2.rename(columns={'What is your SAMC email?': 'Email'}, inplace=True)
        # Convert all email values to lowercase and remove any extraneous characters in df
        df['Email'] = df['Email'].str.lower().str.strip()

        # Convert all email values to lowercase and remove any extraneous characters in df2
        df2['Email'] = df2['Email'].str.lower().str.strip()

        # incomplete
        filtered = df2[~df2['Email'].isin(df['Email'])]
        print(len(filtered))

        st.subheader(f"Total COMPLETED: {len(df2)-len(filtered)}/{len(df2)}")
        st.write(f"No. of INCOMPLETE: {len(filtered)}")
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
        


# Password migration utility (run once)
# if st.toggle("Run password hashing migration (admin only)"):
#     try:
#         client.hash_current_passwords()
#         st.success("All passwords migrated to hashed format!")
#     except Exception as e:
#         st.error(f"Migration failed: {str(e)}")

# sheet1 = st.secrets["Google_Sheet"]['sheet1']
# sheet2 = st.secrets["Google_Sheet"]['sheet2']
# json_key = st.secrets["Google_Secret"]

# today = datetime.today().strftime("%Y-%m-%d")
# st.title("AI Study Tally Results Dashboard")

# st.subheader(today)

# scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
# credentials = ServiceAccountCredentials.from_json_keyfile_dict(json_key, scope)
# client = gspread.authorize(credentials)

# spreadsheet = client.open_by_url(sheet1)
# sheet = spreadsheet.get_worksheet(0)
# data = sheet.get_all_values()

# spreadsheet2 = client.open_by_url(sheet2)
# sheet2 = spreadsheet2.get_worksheet(0)
# data2 = sheet2.get_all_values()

# df = pd.DataFrame(data[1:], columns=data[0])
# df2 = pd.DataFrame(data2[1:], columns=data2[0])
# # Rename the column 'What is your samc email?' to 'Email' in df
# df.rename(columns={'What is your samc email?': 'Email'}, inplace=True)
# # Convert all email values to lowercase and remove any extraneous characters in df
# df['Email'] = df['Email'].str.lower().str.strip()

# # Convert all email values to lowercase and remove any extraneous characters in df2
# df2['Email'] = df2['Email'].str.lower().str.strip()

# # incomplete
# filtered = df2[~df2['Email'].isin(df['Email'])]
# print(len(filtered))

# st.subheader(f"Total INCOMPLETE Survey: {len(filtered)}/{len(df2)}")
# st.write(f"Percentage Incomplete: {(len(filtered)/len(df2))*100:.2f}%")
# st.write(f"Percentage Complete: {((len(df2)-len(filtered))/len(df2))*100:.2f}%")

# def create_table(dept_name, filtered=filtered, df2=df2):
#     st.divider()
#     st.subheader(f"{dept_name} INCOMPLETE Survey")
#     dept_df = filtered[filtered['Program'] == dept_name][['FirstName', 'LastName', 'Program', 'Status', 'Email']]
#     dept_df.index = dept_df.index + 1  # Start index with 1
#     st.write(f'Incomplete Survey Count: {len(dept_df)}/{len(df2[df2["Program"] == dept_name])}')
#     return st.dataframe(dept_df)

# for dept in df2['Program'].unique():
#     create_table(dept)    
    
    
