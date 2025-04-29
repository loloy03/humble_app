import streamlit as st
import pandas as pd
import gspread
import streamlit as st
from oauth2client.service_account import ServiceAccountCredentials
from streamlit_gsheets import GSheetsConnection
from streamlit_option_menu import option_menu
from PIL import Image
from google.oauth2.service_account import Credentials

st.set_page_config(layout="wide")

# this is for styling
st.markdown(f"""
    <style>
        /* Main background color */
        .main {{
            background-color: #b3cf99;
        }}

        /* Text styling for markdown, text inputs, and number inputs */
        .stMarkdown, .stTextInput, .stNumberInput {{
            color: #2d5128;
            font-family: 'Helvetica', 'Arial', sans-serif;
        }}

        /* Heading styling */
        h1, h2, h3, h4, h5, h6 {{
            color: #262730;
            font-family: 'Helvetica', 'Arial', sans-serif;
        }}

        /* Button styling */
        .stButton button {{
            background-color: #2d5128;
            color: white;
            border-color: #2d5128;
            font-family: 'Helvetica', 'Arial', sans-serif;
        }}

        /* Secondary container background color */
        .secondary-container {{
            background-color: #e0e0ef;
        }}

        /* Custom text size */
        .custom-text {{
            font-size: 24px;
            font-family: 'Helvetica', 'Arial', sans-serif;
        }}

        /* Specific styling for class 'css-1d391kg' */
        .css-1d391kg, .css-1d391kg * {{
            background-color: #2d5128 !important;
            font-family: 'Helvetica', 'Arial', sans-serif;
        }}

        /* Optional additional styling for overall text and layout consistency */
        body {{
            font-family: 'Helvetica', 'Arial', sans-serif;
            color: #2d5128;
        }}
        .sidebar .sidebar-content {{
            background-color: #301934;
            color: #2d5128;
            font-family: 'Helvetica', 'Arial', sans-serif;
        }}
    </style>
""", unsafe_allow_html=True)

# sidebar
img = Image.open("humble_logo.png")
st.sidebar.image(
    img ,
    width= 260,
    channels= "RGB",
)
# write here what your webpage is about
st.sidebar.markdown(
    """
    <div style="background-color:##f2f2f2; padding:5px; border-radius:1px;">
        <h2 style="color:#4B0082; font-size:22px; font-weight:bold; text-align:center;">
            Humble Sustainability
        </h2>
    </div>
    <br>
    """,
    unsafe_allow_html=True
)

with st.sidebar:
    page = option_menu(
        menu_title="Operations Management System", 
        options=["Control Tower", "Inventory Dashboard", "Inbounds Dashboard", "Outbounds Dashboard", "FAQs/Guide", "Humble Bot"],
        icons=["arrow-right-circle", "arrow-right-circle", "arrow-right-circle", "arrow-right-circle", "arrow-right-circle", "arrow-right-circle"],
        menu_icon="box-seam-fill",
        default_index=0,
        styles={
            "container": {"padding": "0!important", "background-color": "#d0c3d6"},
            "icon": {"color": "#492865", "font-size": "12px"}, 
            "nav-link": {
                "font-size": "14px",
                "font-weight": "bold",
                "text-align": "left",
                "margin": "1px",
                "--hover-color": "#fefefe",
            },
            "nav-link-selected": {"background-color": "#e06163"},
            "menu-title": {"font-size": "17px", "font-weight": "bold", "text-align": "center"},
        },
    )

# Cache the authentication function to avoid repeated logins
if page == "Control Tower":
    # Set up authentication using your JSON credentials file
    credentials_path = "control-tower-454909-84b11e26051b.json"
    scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]

    # Authenticate with Google Sheets
    credentials = Credentials.from_service_account_file(credentials_path, scopes=scopes)
    gc = gspread.authorize(credentials)

    # Define the spreadsheet ID
    spreadsheet_id = "1pN7lbitNgDnXmV3u-9HoXl6N_UpAGvO5OfQhpvUKf6o"
    sh = gc.open_by_key(spreadsheet_id)
    worksheet = sh.get_worksheet(0)  # Select the first sheet
    data = worksheet.get_all_values()

    header_row_index = None
    for i, row in enumerate(data):
        if any(cell.strip() for cell in row):  
            header_row_index = i
            break

    if header_row_index is None:
        st.error("No valid header row found in the sheet.")
    else:
        # Extract headers from the detected header row
        headers = data[header_row_index]
        df_data = data[header_row_index + 1:]
        df = pd.DataFrame(df_data, columns=headers)
        df = df.dropna(how="all")

        # Streamlit UI
        st.markdown(
            """
            <h2 style="text-align: left; font-size: 30px; font-weight: bold; color: #333; margin-top: 20px;"> 🔍 Control Tower Viewer</h2>
            <h4 style="text-align: left; font-size: 18px; font-weight: normal; color: #666;">none</h4>
            """, 
            unsafe_allow_html=True
        )

        st.dataframe(df)







  
if page == "Inventory Dashboard":
    # Display Title and Description with center alignment and design
    st.markdown(
        """
        <h2 style="text-align: left; font-size: 30px; font-weight: bold; color: #333; margin-top: 20px;">📦📊 Inventory Dashboard</h2>
        <h4 style="text-align: left; font-size: 18px; font-weight: normal; color: #666;">none</h4>
        """, 
        unsafe_allow_html=True
    )
    url = "18qFvLbwSkQg3f-A87sLsLq6h7R3nWam0ZAjRPu5rujc"

    # Establishing a Google Sheets connection
    conn = st.connection("gsheets", type=GSheetsConnection)

    # Fetch existing data from the specified worksheet
    existing_data = conn.read(spreadsheet=url, usecols=list(range(7)), ttl=100)
    existing_data = existing_data.dropna(how="all")

    # st.dataframe(existing_data)

    products = ["Armchair", "Trolley", "Pallets"]
    color = ["orange", "black", "green"]

    with st.form(key="released_form"):
        production_id_text = st.text_input("Production ID* (Enter a number)", placeholder="e.g., 000-0-00000")
        product_type = st.selectbox("Product Released*", options=products, index=None)
        color_type = st.selectbox("Color*", options=color, index=None)
        quantity = st.number_input("Quantity*", value=0, step=1, format="%d")
        onboarding_date = st.date_input(label="Date")

        st.markdown("**required*")

        submit_button = st.form_submit_button(label="Submit Details")

        if submit_button:
            if not product_type or not color_type or not quantity or not onboarding_date:
                st.warning("Ensure all mandatory fields are filled.")
                st.stop()
            else:
                received_data = pd.DataFrame(
                    [
                        {
                            "PRODUCTION CODE": production_id_text,
                            "DATE": onboarding_date.strftime("%m-%d-%Y"),
                            "PRODUCT": product_type,
                            "COLOR": color_type,
                            "ITEM CODE": None,
                            "QUANTITY": quantity,
                            "STATUS": "RELEASED"
                            
                        }
                    ]
                )    
                # Create an empty DataFrame with the same columns for headers
                headers = ["PRODUCTION CODE", "DATE", "PRODUCT", "COLOR", "ITEM CODE", "QUANTITY", "STATUS"]
                display_data = pd.DataFrame(columns=headers)

                # Concatenate headers with the new data
                final_display_df = pd.concat([display_data, received_data], ignore_index=True)
        
                # Show only the header and new data in the DataFrame
                st.dataframe(final_display_df)
                st.success("Received Details successfully submitted!")

                # Use gspread to update the Google Sheets
                scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
                creds = ServiceAccountCredentials.from_json_keyfile_name("released-form-data-entry-36bcab03209d.json", scope)
                client = gspread.authorize(creds)
                sheet = client.open_by_url(f"https://docs.google.com/spreadsheets/d/{url}").sheet1

                # Convert the new data to a list of lists
                new_row = received_data.values.tolist()[0]

                # Append the new row to the sheet
                sheet.append_row(new_row)

if page == "Inbounds Dashboard":
    st.markdown(
        """
        <h2 style="text-align: left; font-size: 30px; font-weight: bold; color: #333; margin-top: 20px;">🚚 Inbounds Dashboard</h2>
        <h4 style="text-align: left; font-size: 10px; font-weight: normal; color: #666;">none</h4>
        """, 
        unsafe_allow_html=True
    )
    url= "1c9wqNXrRX5xrYcJlphQeAQNbbX5vZj9czWbNtnGxf7I"

    # Set up the credentials and client
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name("pallet-receive-form-data-entry-900b02a7c13d.json", scope)
    client = gspread.authorize(creds)

    # Open the Google Sheets document by URL and select the 'LOCATOR' sheet
    sheet = client.open_by_url(f"https://docs.google.com/spreadsheets/d/{url}/edit?gid=25345550#gid=25345550")
    worksheet = sheet.worksheet("PALLET RECEIVE")

    data = worksheet.get('A:I')

    existing_data = pd.DataFrame(data[3:], columns=data[2])

    products = ["Armchair", "Trolley", "Pallets"]
    color = ["orange", "black", "green"]

    with st.form(key="received_form"):
        production_id_text = st.text_input("Production ID* (Enter a number)", placeholder="e.g., 000-0-00000")
        product_type = st.selectbox("Product Received*", options=products, index=None)
        color_type = st.selectbox("Color*", options=color, index=None)
        quantity = st.number_input("Quantity*", value=0, step=1, format="%d")
        onboarding_date = st.date_input(label="Date")
        pallet_position = st.text_input("Position No.*", placeholder="e.g., P001")

        st.markdown("**required*")

        submit_button = st.form_submit_button(label="Submit Details")

        if submit_button:
            if not product_type or not color_type or not quantity or not onboarding_date:
                st.warning("Ensure all mandatory fields are filled.")
                st.stop()
            else:
                received_data = pd.DataFrame(
                    [
                        {
                            "PRODUCTION CODE": production_id_text,
                            "DATE": onboarding_date.strftime("%m-%d-%Y"),
                            "PRODUCT": product_type,
                            "COLOR": color_type,
                            "ITEM CODE": None,
                            "QUANTITY": quantity,
                            "POSITION NO.": pallet_position,
                            "STATUS": "RECEIVED"
                            
                        }
                    ]
                )    
                # Create an empty DataFrame with the same columns for headers
                headers = ["PRODUCTION CODE", "DATE", "PRODUCT", "COLOR", "ITEM CODE", "QUANTITY", "STATUS"]
                display_data = pd.DataFrame(columns=headers)

                # Concatenate headers with the new data
                final_display_df = pd.concat([display_data, received_data], ignore_index=True)
        
                # Show only the header and new data in the DataFrame
                st.dataframe(final_display_df)
                st.success("Received Details successfully submitted!")

                # Use gspread to update the Google Sheets
                scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
                creds = ServiceAccountCredentials.from_json_keyfile_name("received-form-data-entry-fe281fc8d580.json", scope)
                client = gspread.authorize(creds)
                sheet = client.open_by_url(f"https://docs.google.com/spreadsheets/d/{url}").sheet1

                # Convert the new data to a list of lists
                new_row = received_data.values.tolist()[0]

                # Append the new row to the sheet
                sheet.append_row(new_row)

if page == "Outbounds Dashboard":
    st.markdown(
        """
        <h2 style="text-align: left; font-size: 30px; font-weight: bold; color: #333; margin-top: 20px;">↗️ Outbounds Dashboard</h2>
        <h4 style="text-align: left; font-size: 18px; font-weight: normal; color: #666;">none</h4>
        """, 
        unsafe_allow_html=True
    )
    url = "1c9wqNXrRX5xrYcJlphQeAQNbbX5vZj9czWbNtnGxf7I"

    # Set up the credentials and client
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name("pallet-release-form-data-entry-bce5f3407732.json", scope)
    client = gspread.authorize(creds)

    # Open the Google Sheets document by URL and select the 'PALLET RELEASE' sheet
    sheet = client.open_by_url(f"https://docs.google.com/spreadsheets/d/{url}/edit?gid=25345550#gid=25345550")
    worksheet = sheet.worksheet("PALLET RELEASE")

    data = worksheet.get('A:I')
    existing_data = pd.DataFrame(data[3:], columns=data[2])

    products = ["Armchair", "Trolley", "Pallets"]
    colors = ["orange", "black", "green"]

    with st.form(key="received_form"):
        production_id_text = st.text_input("Production ID* (Enter a number)", placeholder="e.g., 000-0-00000")
        product_type = st.selectbox("Product Released*", options=products, index=None)
        color_type = st.selectbox("Color*", options=colors, index=None)
        quantity = st.number_input("Quantity*", value=0, step=1, format="%d")
        onboarding_date = st.date_input(label="Date")
        pallet_position = st.text_input("Position No.*", placeholder="e.g., P001")

        st.markdown("**required*")

        submit_button = st.form_submit_button(label="Submit Details")

        if submit_button:
            if not production_id_text or not product_type or not color_type or not quantity or not onboarding_date or not pallet_position:
                st.warning("Ensure all mandatory fields are filled.")
                st.stop()
            else:
                received_data = pd.DataFrame(
                    [
                        {
                            "PRODUCTION CODE": production_id_text,
                            "DATE": onboarding_date.strftime("%m-%d-%Y"),
                            "PRODUCT": product_type,
                            "COLOR": color_type,
                            "ITEM CODE": None,
                            "QUANTITY": quantity,
                            "POSITION NO.": pallet_position,
                            "STATUS": "RELEASED"
                        }
                    ]
                )
                # Create an empty DataFrame with the same columns for headers
                headers = ["PRODUCTION CODE", "DATE", "PRODUCT", "COLOR", "ITEM CODE", "QUANTITY", "STATUS"]
                display_data = pd.DataFrame(columns=headers)

                # Concatenate headers with the new data
                final_display_df = pd.concat([display_data, received_data], ignore_index=True)
        
                # Show only the header and new data in the DataFrame
                st.dataframe(final_display_df)
                st.success("Received Details successfully submitted!")

                # Use gspread to update the Google Sheets
                scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
                creds = ServiceAccountCredentials.from_json_keyfile_name("received-form-data-entry-fe281fc8d580.json", scope)
                client = gspread.authorize(creds)
                sheet = client.open_by_url(f"https://docs.google.com/spreadsheets/d/{url}").sheet1

                # Convert the new data to a list of lists
                new_row = received_data.values.tolist()[0]

                # Append the new row to the sheet
                sheet.append_row(new_row)

if page == "FAQs/Guide":
    st.markdown(
        """
        <h2 style="text-align: left; font-size: 30px; font-weight: bold; color: #333; margin-top: 20px;">❓FAQs/Guide</h2>
        <h4 style="text-align: left; font-size: 18px; font-weight: normal; color: #666;">none</h4>
        """, 
        unsafe_allow_html=True
    )


if page == "Humble Bot":
    st.markdown(
        """
        <h2 style="text-align: left; font-size: 24px; font-weight: bold; color: #333; margin-top: 20px;">🤖 Humble Bot</h2>
        <h4 style="text-align: left; font-size: 18px; font-weight: normal; color: #666;">none</h4>
        """, 
        unsafe_allow_html=True
    )