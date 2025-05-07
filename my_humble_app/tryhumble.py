import streamlit as st
import pandas as pd
import gspread
import numpy as np
from oauth2client.service_account import ServiceAccountCredentials
from streamlit_gsheets import GSheetsConnection
from streamlit_option_menu import option_menu
from PIL import Image
from google.oauth2.service_account import Credentials
import plotly.express as px
import base64
from io import BytesIO
import plotly.express as px
import calendar 
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import google.generativeai as genai
import streamlit.components.v1 as components
from datetime import datetime
import time
import os
import re

# --- PAGE SETUP ---
st.set_page_config(page_title="Humble OMS Login", layout="wide", initial_sidebar_state="expanded")

# ✅ GLOBAL Google Sheets API credentials (shared across all logic)
credentials_path = "inventory-dashboard-455009-55fd550abb75.json"
scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
credentials = Credentials.from_service_account_file(credentials_path, scopes=scopes)
gc = gspread.authorize(credentials)

# --- SESSION STATE ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# --- HARDCODED CREDENTIALS ---
USERNAME = "humble"
PASSWORD = "HumbleWarehouse!"

# --- LOGIN LOGIC ----------------------------------------------------
if not st.session_state.logged_in:
    st.markdown("""
        <style>
            /* Center the block & limit its width */
            .block-container {
                max-width: 450px;
                margin: auto;
                padding-top: 100px;
            }
            .login-title {
                font-size: 40px;
                font-weight: 750;
                margin-bottom: 8px;
                text-align: center;
            }
            .login-subtitle {
                color: gray;
                font-size: 15px;
                margin-bottom: 20px;
                text-align: center;
            }
            .stTextInput input {
                font-size: 13px;
            }
            .stButton > button {
                width: 100%;
                border-radius: 20px;
                background-color: #1C0033;
                color: white;
                padding: 8px 16px;
                font-weight: bold;
                font-size: 14px;
                border: none;
                outline: none;
                transition: background-color 0.3s ease;
            }
            .stButton > button:hover {
                background-color: #333333;
                cursor: pointer;
            }
            .stButton > button:focus {
                outline: none;
                box-shadow: none;
            }
            </style>
    """, unsafe_allow_html=True)

    st.markdown('<div class="login-title">Welcome back!</div>', unsafe_allow_html=True)
    st.markdown('<div class="login-subtitle">Log in to the Humble OMS</div>', unsafe_allow_html=True)

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Log In"):
        if username == USERNAME and password == PASSWORD:
            st.session_state.logged_in = True
            st.success("")
            st.rerun()
        else:
            st.error("Incorrect username or password.")

    st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# --- CONFIG ---
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
model = genai.GenerativeModel("models/gemini-1.5-pro-latest")

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# --- Load Font & Custom Styling ---
st.markdown("""
<link href="https://fonts.googleapis.com/css2?family=Nunito+Sans:wght@400;600;700&display=swap" rel="stylesheet">
<style>
    * {
        font-family: 'Nunito Sans', sans-serif !important;
    }
    section[data-testid="stSidebar"] {
        width: 300px !important;
        min-width: 300px !important;
        background-color: #1C0033; /* Darker purple-black */
        border-top-right-radius: 15px;
        border-bottom-right-radius: 25px;
        padding: 1rem 0.5rem 5rem 0.5rem;
    }
    .sidebar-header {
        display: flex;
        align-items: center;
        gap:10px;
        margin-bottom: 0.5rem;
    }
    .sidebar-header img {
        width: 45px;
        height: 45px;
    }
    .sidebar-header span {
        font-weight: 700;
        font-size: 16px;
        color: white;
    }
    .footer {
        position: fixed;
        bottom: 25px;
        left: 25px;
    }
    .footer div {
        color: white;
        font-size: 14px;
        font-weight: 600;
        padding: 6px 0;
        cursor: pointer;
    }
    .footer div:hover {
        text-decoration: underline;
    }
    /* Hover styling for sidebar nav links */
    div[data-testid="stSidebar"] ul li:hover a {
        background-color: rgba(255, 168, 242, 0.2);  /* lighter pink with more subtle opacity */
        color: #FFA8F2 !important;
        font-weight: 500;
        border-radius: 6px;
        padding-top: 6px !important;
        padding-bottom: 6px !important;
    }
    section[data-testid="stSidebar"] {
        padding-top: 0.5rem !important;  /* Reduce top padding */
    }
</style>
""", unsafe_allow_html=True)

# --- Convert Logo to Base64 ---
def logo_to_base64(img):
    buffer = BytesIO()
    img.save(buffer, format="PNG")  # JPEG is correct for .jpg files
    return base64.b64encode(buffer.getvalue()).decode()

# --- Load and Encode Logo ---
logo = Image.open("humble.png")
logo_base64 = logo_to_base64(logo)

# --- Sidebar Logo without Rounded Corners ---
st.sidebar.markdown(
    f"""
    <img src="data:image/png;base64,{logo_base64}" 
         style="width: 320px; height: auto; border-radius: 0px; display: block; margin: 0 auto;" />
    """,
    unsafe_allow_html=True
)

# --- Sidebar Container with Top + Bottom Layout ---
st.markdown("""
<style>
[data-testid="stSidebar"] > div:first-child {
    display: flex;
    flex-direction: column;
    height: 100vh;
    justify-content: space-between;
    overflow: hidden !important;
}
</style>
""", unsafe_allow_html=True)

st.sidebar.markdown("""
<div style="color: gray; font-size: 13.5px; font-weight: 650; margin: 0.5px 0 0.5px 0.5px; text-transform: uppercase; letter-spacing: 1px;">
    Menu
</div>
""", unsafe_allow_html=True)

# --- Sidebar Menu ---
st.markdown("""
<style>
/* Force sidebar width */
.css-1d391kg {
    width: 260px !important;
    min-width: 260px !important;
}
</style>
""", unsafe_allow_html=True)

with st.sidebar:
    page = option_menu(
        menu_title= None,
        options=[
            "Control Tower", 
            "Inbounds Dashboard", 
            "Outbounds Dashboard",
            "Inventory Dashboard", 
            "Humble Bot",
            "System Guide", 
            "Contact Us",
            "Logout",
        ],
        icons=["house", "file-arrow-down", "file-arrow-up", "box2", "question-lg", "chat", "info-circle", "box-arrow-right"],
        default_index=0,
        key="main_page",
        styles={
            "container": {
                "padding": "0rem",
                "background-color": "#1C0033",
                "border-radius": "0px",
                "margin": "0",
                "width": "260px",  # NEW
                "min-width": "260px",  # NEW
                "overflow": "hidden",  # NEW
            },
            "icon": {
                "color": "#fffff",
                "font-size": "13.5px",
                "margin-right": "8px",
                "position": "relative",
                "left": "-1px"
            },
            "nav-link": {
                "font-family": "Segoe UI, sans-serif",
                "font-size": "12px",
                "font-weight": "450",
                "text-align": "left",
                "color": "#ffffff",
                "margin": "4px 0",
                "padding": "9px 9px 9px 6px",
                "border-radius": "4px",
                "white-space": "nowrap",
                "overflow": "hidden",
                "text-overflow": "ellipsis",
                "transition": "all 0.4s ease",
                "--hover-color": "rgba(66, 165, 247, 0.2)" # blue
            },
            "nav-link-selected": {
                "font-family": "Segoe UI, sans-serif",
                "background-color": "#e35d60",  
                "color": "#ffffff", # pink
                "icon": "#ffffff",
                "font-weight": "700",
            }
        }
    )
    
# CONTROL TOWER CONNECTION --------------------------------------------------------------------------------------------------------------------------------------------


@st.cache_data(ttl=60)
def get_control_tower_data(sheet_index=0):
    credentials_path = "control-tower-454909-57dd2ea0f2bc.json"
    scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    credentials = Credentials.from_service_account_file(credentials_path, scopes=scopes)
    gc = gspread.authorize(credentials)

    spreadsheet_id = "1pN7lbitNgDnXmV3u-9HoXl6N_UpAGvO5OfQhpvUKf6o"
    sh = gc.open_by_key(spreadsheet_id)
    worksheet = sh.get_worksheet(sheet_index)
    data = worksheet.get_all_values()

    if not data:
        return pd.DataFrame()

    # Dynamically determine header row index based on sheet
    if sheet_index == 2:
        header_row_index = 9  # Prospects sheet (row 10)
    elif sheet_index == 3:
        header_row_index = 5  # WH Schedule Viewer (row 6 - based on image)
    else:
        header_row_index = 2  # **For Supplier Progress Tracker, header in row 3 (index 2)**

    headers = data[header_row_index]
    df_data = data[header_row_index + 1:]  # Data starts from the next row after header (row 4)

    df = pd.DataFrame(df_data, columns=headers)

    # Clean empty rows and columns
    df = df.dropna(how="all", axis=0)
    df = df.dropna(how="all", axis=1)

    return df


# CONTROL TOWER DASHBOARD PAGE --------------------------------------------------------------------------------------------------------------------------------------------------

if page == "Control Tower":

    # 💅 Optional: insert this above the tabs for better tab styling
    st.markdown("""
    <style>
    [data-testid="stTabs"] button {
        font-size: 16px !important;
        font-weight: 600 !important;
        padding: 10px 20px !important;
        margin-right: 6px !important;
    }
    [data-testid="stTabs"] button[aria-selected="true"] {
        border-bottom: 4px solid #ff4b4b !important;
    }
    </style>
    """, unsafe_allow_html=True)

    st.markdown("<h2 style='margin-bottom: 0.5rem;'>🔍 Control Tower Viewer</h2>", unsafe_allow_html=True)

    # 🔗 Sheet link expander
    with st.expander("🔗 View Spreadsheet Link", expanded=False):
        st.markdown("""
        [BD x OPS Supplier Control Tower](https://docs.google.com/spreadsheets/d/1pN7lbitNgDnXmV3u-9HoXl6N_UpAGvO5OfQhpvUKf6o/edit?gid=810324430)
        """, unsafe_allow_html=True)

    tab_labels = ["📦 Supplier Progress Tracker", "📋 Account Masterlist", "🧩 Prospects"]
    selected_tab = st.radio("Select a tab", tab_labels, horizontal=True)

    sheet_indices = {
        "📦 Supplier Progress Tracker": 0,
        "📋 Account Masterlist": 1,
        "🧩 Prospects": 2
    }

    sheet_index = sheet_indices[selected_tab]
    df = get_control_tower_data(sheet_index=sheet_index)

    if df.empty:
        st.error("No data found.")
    else:
        st.markdown(f"<h4 style='margin-bottom: 0.2rem;'>{selected_tab}</h4>", unsafe_allow_html=True)


# ----------------------------- SUPPLIER PROGRESS TRACKER --------------------------------------------------------------------------------------------------------
        if selected_tab == "📦 Supplier Progress Tracker":
            if "Endorsement Date" in df.columns:
                df["Endorsement Date"] = pd.to_datetime(df["Endorsement Date"], errors="coerce")
                df["Month-Year"] = df["Endorsement Date"].dt.strftime("%B %Y")

            # === Styles ===
            st.markdown("""
            <style>
            .info-card {
                background: linear-gradient(90deg, #e1e7fe, #cfdafd);
                border-radius: 22px;
                padding: 24px 20px;
                box-shadow: 0 12px 28px rgba(0, 0, 0, 0.08);
                height: 80px;
                display: flex;
                flex-direction: column;
                justify-content: center;
                align-items: flex-start;
                transition: all 0.2s ease-in-out;
            }
            .info-card:hover {
                transform: scale(1.03) translateY(-6px);
                box-shadow: 0 20px 38px rgba(0, 0, 0, 0.16);
                transition: all 0.2s ease-in-out;
            }
            .info-label {
                font-size: 12px;
                font-weight: 550;
                color: #666;
                margin-bottom: 2px;
            }
            .info-value {
                font-size: 17px;
                font-weight: 700;
                color: #1e1e1e;
            }
            .pill {
                background-color: #e6f4ea;
                color: #34a853;
                padding: 6px 12px;
                border-radius: 999px;
                font-weight: 600;
                font-size: 18px;
                display: inline-block;
                width: fit-content;
                margin-top: 3px;
            }
            .pill-missing {
                color: #d93025;
                font-weight: 600;
            }
            .drive-link {
                font-weight: 600;
                font-size: 14.5px;
                color: #3f51b5;
                text-decoration: none;
                margin-top: 4px;
            }
            </style>
            """, unsafe_allow_html=True)

            # === Row 1: Dropdown, Deal Status, Google Drive ===
            col1, col2, col3 = st.columns([3.5, 1.75, 1.75])

            account_list = df["Account Name"].dropna().unique()

            selected_client = col1.selectbox(
                "Select a supply client",
                account_list,
                index=len(account_list) - 1 if len(account_list) > 0 else None,
                key="client_dropdown"
            )

            if selected_client:
                row = df[df["Account Name"] == selected_client].iloc[0]
                deal_status = "Closed Deal" if row.get("Closing Date") or row.get("Signed Closed Deal") else "Ongoing"
                gdrive = row.get("Google Drive Folder Link")
                account_type = row.get("Account Type", "N/A")
                deal_type = row.get("Initial Deal Type", "N/A")
                endorsement = row.get("Endorsement Date")
                endorsement_date = endorsement.strftime("%b %d, %Y") if pd.notnull(endorsement) else "N/A"
                pif_link = row.get("PIF Link")
                pif_completed = bool(row.get("PIF Submission Date") or pif_link)
                pif_display = f"✅ <a href='{pif_link}' target='_blank'>PIF Link</a>" if pif_completed else "<span class='pill-missing'>⚠️ Pending </span>"

                # Column 2 – Deal Status
                with col2:
                    st.markdown(f"""
                    <div class="info-card">
                        <div class="info-label">Deal Status</div>
                        <div class="pill">{deal_status}</div>
                    </div>
                    """, unsafe_allow_html=True)

                # Column 3 – Google Drive
                with col3:
                    if gdrive:
                        st.markdown(f"""
                        <div class="info-card">
                            <div class="info-label">Google Drive</div>
                            <a class="drive-link" href="{gdrive}" target="_blank">📁 Google Drive Folder</a>
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.markdown("""
                        <div class="info-card">
                            <div class="info-label">Google Drive</div>
                            <div class="info-value" style="color:#888;">No link</div>
                        </div>
                        """, unsafe_allow_html=True)

                # === Divider ===
                st.markdown("""
                    <hr style='margin-top: -10px; margin-bottom: 25px; border: none; border-top: 1.5px solid transparent;' />
                """, unsafe_allow_html=True)

                # === Row 2: Account Type, Endorsement Date, Deal Type, PIF ===
                col1, col2, col3, col4 = st.columns(4)

                with col1:
                    st.markdown(f"""
                    <div class="info-card">
                        <div class="info-label">Account Type</div>
                        <div class="info-value">{account_type}</div>
                    </div>
                    """, unsafe_allow_html=True)

                with col2:
                    st.markdown(f"""
                    <div class="info-card">
                        <div class="info-label">Endorsement Date</div>
                        <div class="info-value">{endorsement_date}</div>
                    </div>
                    """, unsafe_allow_html=True)

                with col3:
                    st.markdown(f"""
                    <div class="info-card">
                        <div class="info-label">Deal Type</div>
                        <div class="info-value">{deal_type}</div>
                    </div>
                    """, unsafe_allow_html=True)

                with col4:
                    st.markdown(f"""
                    <div class="info-card">
                        <div class="info-label">PIF Status</div>
                        <div class="info-value">{pif_display}</div>
                    </div>
                    """, unsafe_allow_html=True)

                # === Divider ===
                st.markdown("""
                    <hr style='margin-top: -10px; margin-bottom: 25px; border: none; border-top: 1.5px solid transparent;' />
                """, unsafe_allow_html=True)

                
                # === Divider ===
                st.markdown("""
                    <hr style='margin-top: 30px; margin-bottom: 30px; border: none; border-top: 2px solid #ccc;' />
                """, unsafe_allow_html=True)

            # === Metric Cards CSS (no chart containers) ===
            st.markdown("""
            <style>
            .metric-card {
                background-color: #f5e1ff;
                border-radius: 20px;
                padding: 1.5rem 1.2rem;
                margin-bottom: 1rem;
                box-shadow: 0 6px 14px rgba(0, 0, 0, 0.08);
                height: 190px;
                display: flex;
                flex-direction: column;
                justify-content: flex-end;
                transition: all 0.25s ease;
            }
            .metric-card:hover {
                transform: translateY(-6px);
                box-shadow: 0 10px 24px rgba(0, 0, 0, 0.15);
            }
            .metric-title {
                color: #666;
                font-weight: 550;
                font-size: 12px;
                margin-bottom: 6px;
            }
            .metric-growth {
                font-size: 13px;
                font-weight: 600;
                margin-bottom: 4px;
            }
            .metric-value {
                font-size: 22px;
                font-weight: 700;
                color: #1c1c1c;
            }
            </style>
            """, unsafe_allow_html=True)

            # === Layout ===
            col1, col2, col3 = st.columns([1.5, 0.5, 1])

            # --- Column 1: Filter Label ---
            with col1:
                st.markdown("#### 📅 Filter by Month")
                month_filter = "All"
                if "Month-Year" in df.columns:
                    months = sorted(
                        df["Month-Year"].dropna().unique(),
                        key=lambda x: pd.to_datetime(x, format='%B %Y')
                    )
                    month_filter = st.selectbox("Select a month", ["All"] + months, key="month_filter_dropdown")

            # === Date Preparation ===
            if "Endorsement Date" in df.columns:
                df["Endorsement Date"] = pd.to_datetime(df["Endorsement Date"], errors='coerce')

            # === Filter df for visualizations and metric counts ===
            filtered_df = df.copy()
            if month_filter != "All" and "Month-Year" in df.columns:
                filtered_df = df[df["Month-Year"] == month_filter]

            # === Activated Account Count (based on selected month, count all rows) ===
            if month_filter != "All":
                current_count = df[df["Month-Year"] == month_filter].shape[0]
            else:
                current_count = df.shape[0]

            # === Top Activation Month (by total rows, not unique) ===
            top_month = df["Month-Year"].value_counts().idxmax() if "Month-Year" in df.columns else "N/A"
            top_count = df["Month-Year"].value_counts().max() if "Month-Year" in df.columns else 0

            # Define defaults to avoid NameErrors
            if month_filter == "All" or "Month-Year" not in df.columns:
                percent_change = None
                percent_change_str = None
                growth_color = "#999"
                growth_symbol = ""
                previous_month_datetime = None
            else:
                selected_month_datetime = pd.to_datetime(month_filter, format='%B %Y')
                previous_month_datetime = selected_month_datetime - pd.DateOffset(months=1)
                previous_month_str = previous_month_datetime.strftime('%B %Y')

                current_count = df[df["Month-Year"] == month_filter].shape[0]
                previous_count = df[df["Month-Year"] == previous_month_str].shape[0] if previous_month_str in df["Month-Year"].values else 0

                if previous_count > 0:
                    percent_change = ((current_count - previous_count) / previous_count) * 100
                    percent_change_str = f"{abs(percent_change):.2f}%"
                    growth_color = "green" if percent_change > 0 else "red"
                    growth_symbol = "+" if percent_change > 0 else "−"
                else:
                    percent_change = None
                    percent_change_str = None
                    growth_color = "#999"
                    growth_symbol = ""

            # --- Column 2: Metric Cards ---
            with col2:
                # No. of Activations card (dynamic by month or All)
                st.markdown(f"""
                <div class='metric-card' style='padding: 10px 15px;'>
                    <img src='https://cdn-icons-png.flaticon.com/128/12458/12458553.png' width='35' style='margin-bottom:8px;opacity:0.7;'/>
                    <div class='metric-title' style='font-size:14px; color: #666;'>No. of Activations</div>
                    <div class='metric-value' style='line-height: 1.0; font-size: 25px; font-weight: 700;'>
                        {current_count}
                    </div>
                    <div style='font-size: 12px; margin-top: 4px; color: #999; font-style: italic; font-weight:600;'>
                        {"for " + month_filter if month_filter != "All" else "All Months"}
                    </div>
                </div>
                """, unsafe_allow_html=True)

                # Growth vs Last Month card
                st.markdown(f"""
                <div class='metric-card' style='padding: 10px 15px;'>
                    <img src='https://cdn-icons-png.flaticon.com/128/5405/5405826.png' width='35' style='margin-bottom:8px;opacity:0.7;'/>
                    <div class='metric-title' style='font-size:14px; color: #666;'>Monthly Activation Growth</div>
                    <div class='metric-value' style='line-height: 1.0; font-size: 25px; font-weight: 700; color:{growth_color};'>
                        {f"{growth_symbol} {percent_change_str}" if percent_change_str else "N/A"}
                    </div>
                    <div style='font-size: 12px; margin-top: 4px; color: #999; font-style: italic; font-weight:500;'>
                        {f"vs {previous_month_datetime.strftime('%B %Y')}" if previous_month_datetime else "—"}
                    </div>
                </div>
                """, unsafe_allow_html=True)

            # --- Column 3: Pie Chart ---
            with col3:
                if "Account Type" in df.columns:
                    pie_df = df.copy()
                    if month_filter != "All":
                        pie_df = df[df["Month-Year"] == month_filter]

                    account_counts = pie_df["Account Type"].dropna().value_counts().reset_index()
                    account_counts.columns = ["Account Type", "Count"]

                    fig1 = px.pie(account_counts, values="Count", names="Account Type", hole=0.3)
                    fig1.update_traces(textposition='inside', textinfo='percent+label', textfont_size=12)
                    fig1.update_layout(
                        height=400,
                        width=380,
                        paper_bgcolor="rgba(0,0,0,0)",
                        plot_bgcolor="white",
                        margin=dict(t=60, b=20, l=10, r=10)
                    )

                    st.markdown("### 📊 Account Type Distribution")
                    st.plotly_chart(fig1, use_container_width=False)
                else:
                    st.warning("⚠️ 'Account Type' column not found in your dataset.")

            # === COMBINED BAR CHART: Client Distribution by Account Type ===
            df_filtered = df if month_filter == "All" else df[df["Month-Year"] == month_filter]

            if "Account Name" in df_filtered.columns and "Account Type" in df_filtered.columns:
                df_filtered["Grouped Account"] = df_filtered["Account Name"].str.replace(
                    r"(B\d+|Batch \d+| - [A-Za-z\s]+)", "", regex=True).str.strip()

                grouped_counts = df_filtered.groupby(["Grouped Account", "Account Type"]).size().reset_index(name="Count")

                fig2 = px.bar(
                    grouped_counts,
                    x="Grouped Account",
                    y="Count",
                    color="Account Type",
                    barmode="stack",  # Or "group" for side-by-side bars
                    text="Count",
                    title=""
                )

                fig2.update_layout(
                    height=450,
                    margin=dict(t=20, b=10, l=10, r=10),
                    xaxis_title="",
                    yaxis_title="Number of Activations",
                    xaxis_tickangle=-45,
                    showlegend=True,
                    plot_bgcolor="white",
                    paper_bgcolor="rgba(0,0,0,0)"
                )
                fig2.update_traces(textposition='outside')

                st.markdown(f"""
                    <div style='margin-bottom: -1rem;'>
                        <h4 style='margin-bottom: 0.2rem;'>📈 Client Distribution by Account Type</h4>
                        <p style='font-size: 14px; color: #888; margin-top: 0;'>{month_filter} Clients</p>
                    </div>
                    """, unsafe_allow_html=True)

                st.plotly_chart(fig2, use_container_width=True)

            else:
                st.warning("⚠️ 'Account Name' and/or 'Account Type' column not found in your dataset.")

# --------------------------------------------------------------------------------------------------------------------------------------------------------------------

        if selected_tab == "📋 Account Masterlist" and "Account Name" in df.columns:
            selected_client = st.selectbox("Select a client", df["Account Name"].dropna().unique(), index=None, key="client_selector")

            if selected_client:
                client_data = df[df["Account Name"] == selected_client].iloc[0]

                deal_status_raw = str(client_data.get("Deal Status", "")).strip().lower()

                # Display the badge only for open/closed deals
                if deal_status_raw == "open":
                    badge_label = "OPEN DEAL"
                    badge_color = "#2ecc71"  # green
                elif deal_status_raw == "closed":
                    badge_label = "CLOSED DEAL"
                    badge_color = "#e74c3c"  # red
                else:
                    badge_label = None
                    badge_color = None

                # Render badge only if defined
                if badge_label and badge_color:
                    st.markdown(f"""
                    <div style='
                        display: inline-block;
                        background-color:{badge_color};
                        color:white;
                        padding:10px 20px;
                        border-radius:40px;
                        font-size:18px;
                        font-weight:600;
                        margin-bottom: 10px;
                    '>
                        {badge_label}
                    </div>
                    """, unsafe_allow_html=True)

                # --- Layout: Two Columns ---
                col1, col2 = st.columns([1, 1])

                with col1:
                    st.markdown(f"#### 📊 Revenue Breakdown for {selected_client}")
                    fig_bar = px.bar(
                        x=["Humble Revenue", "Supplier Revenue"],
                        y=[client_data["Humble Revenue"], client_data["Supplier Revenue"]],
                        labels={"x": "Revenue Type", "y": "Revenue (Amount)"},
                        width=250,
                        height=220
                    )
                    fig_bar.update_traces(
                        texttemplate='%{y:.2f}',
                        textposition='outside',
                        textfont_size=11,
                        marker=dict(line=dict(width=1), color='#1f77b4'),
                        width=0.3  # <--- controls bar width (lower = thinner)
                    )
                    fig_bar.update_layout(margin=dict(l=10, r=10, t=40, b=10))
                    st.plotly_chart(fig_bar, use_container_width=True)

                with col2:
                    st.markdown("")

                # --- View Detailed Client Row ---
                with st.expander("📋 View Client Data"):
                    st.dataframe(
                        df[df["Account Name"] == selected_client].reset_index(drop=True),
                        use_container_width=True
                    )
            else:
                st.warning("Please select a valid client.")
# --------------------------------------------------------------------------------------------------------------------------------------------------------------------

        if selected_tab == "🧩 Prospects":
            st.markdown("### Inbound Schedule Tracker")

            # --- Date Parsing ---
            df["Planned Date (Raw)"] = pd.to_datetime(df["Planned Date"], errors="coerce")
            df["Planned Date"] = df["Planned Date (Raw)"].dt.strftime("%B %d, %Y")
            df["Planned Month"] = df["Planned Date (Raw)"].dt.strftime("%B %Y")
            df["Month Sort"] = df["Planned Date (Raw)"].dt.to_period("M")

            # --- Month Dropdown ---
            month_options = df.sort_values("Month Sort")["Planned Month"].dropna().unique().tolist()
            month_options.insert(0, "All")
            current_month_str = pd.Timestamp.today().strftime("%B %Y")
            default_month_index = month_options.index(current_month_str) if current_month_str in month_options else 0

            selected_month = st.selectbox(
                "📆 Filter by Month",
                month_options,
                index=default_month_index,
                key="month_filter_dropdown_prospects"
            )

            # --- Filter by Month ---
            if selected_month == "All":
                filtered_df = df.copy()
            else:
                filtered_df = df[df["Planned Month"] == selected_month].copy()

                # Apply Week filter on top of month filter
                filtered_df = filtered_df

            # --- Output Table ---
            st.markdown("### 📋 Inbound Schedule")
            if not filtered_df.empty:
                st.dataframe(
                    filtered_df[["Account", "Planned Date", "Planned Time", "Schedule Status", "Purpose"]],
                    use_container_width=True
                )
            else:
                st.warning("⚠️ No scheduled accounts for the selected filters.")

            # --- Embedded Schedule Viewer ---
            with st.expander("📅 View Full Warehouse Schedule"):
                st.markdown("""
                <div style="overflow: auto; width: 100%;">
                    <div style="transform: scale(0.8); transform-origin: top left; width: 1250px; height: 700px;">
                        <iframe src="https://docs.google.com/spreadsheets/d/e/2PACX-1vTwd6qAOGKpJzD6n_XmEtGT_UzZaJx8EvnAsT81K5ORXTw2fMOc5IzMYXiwQW5opGHp0_zsGzKwvAgj/pubhtml?gid=226802695&single=true"
                                width="1600" height="900" frameborder="0"></iframe>
                    </div>
                </div>
                """, unsafe_allow_html=True)
# DATAFRAME --------------------------------------------------------------------------------------------------------------------------------------------------

        # --- Final Table (Full Sheet Data) --- Displayed at the bottom after all content
        if selected_tab == "📦 Supplier Progress Tracker":
            st.markdown("### 📋 Full Sheet Data")
            st.dataframe(df, use_container_width=True)

        elif selected_tab == "📋 Account Masterlist":
            st.markdown("### 📄 Full Sheet Data")

            if "Inbound Report" in df.columns:
                # Filter: Exclude rows that are all empty except for Inbound Report = FALSE
                def keep_row(row):
                    inbound = str(row.get("Inbound Report", "")).strip().lower()
                    other_data = row.drop(labels=["Inbound Report"]).astype(str).str.strip()
                    return inbound != "false" or any(other_data)

                filtered_df = df[df.apply(keep_row, axis=1)].copy()

                # Replace TRUE/FALSE with ✅ / ⬜ in display
                def render_checkbox(val):
                    val = str(val).strip().lower()
                    if val == "true":
                        return "✅"
                    elif val == "false":
                        return "⬜"
                    else:
                        return ""

                if not filtered_df.empty:
                    if "Inbound Report" in filtered_df.columns:
                        filtered_df["Inbound Report"] = filtered_df["Inbound Report"].apply(render_checkbox)
                    st.dataframe(filtered_df.reset_index(drop=True), use_container_width=True)
                else:
                    st.info("✅ No entries found after filtering.")
            else:
                st.error("⚠️ 'Inbound Report' column not found in the sheet.")

# INVENTORY CONNECTION --------------------------------------------------------------------------------------------------------------------------------------------

@st.cache_data(ttl=60)
def get_inventory_data():
    credentials_path = "inventory-dashboard-455009-55fd550abb75.json"
    scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    credentials = Credentials.from_service_account_file(credentials_path, scopes=scopes)
    gc = gspread.authorize(credentials)

    spreadsheet_id = "1zjwGFngmxPszz_-imJvVqbhi856zgJLSpiI_WmIO9vI"
    sh = gc.open_by_key(spreadsheet_id)
    worksheet = sh.get_worksheet(4)
    data = worksheet.get_all_values()

    if not data:
        return pd.DataFrame()

    raw_headers = data[1]
    headers = []
    seen = set()
    for h in raw_headers:
        h_clean = h.strip()
        if h_clean == "" or h_clean in seen:
            continue
        headers.append(h_clean)
        seen.add(h_clean)

    df_data = [row[:len(headers)] for row in data[2:]]  # Trim each row to header length

    df = pd.DataFrame(df_data, columns=headers)
    df = df[df["Client"].str.strip() != ""]  # Safe fallback filter

    df = df.reset_index(drop=True)
    return df


def preprocess_inventory_data(df):
    numeric_cols = [
        "Buy Price", "Total Buy Price", "Selling Price", "Total Selling Price",
        "Qty Sold", "On Hand Qty", "Total Sold", "Profit", "Profit Margin"
    ]

    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col].astype(str).str.replace("₱", "").str.replace(",", "").str.strip(), errors='coerce').fillna(0)

    date_columns = ["Date Inbounded", "Date Sold"]
    for col in date_columns:
        df[col] = pd.to_datetime(df[col], errors='coerce')

    df["Sales Cycle"] = pd.to_numeric(df["Sales Cycle"], errors='coerce').fillna(0).astype(int)
    df["On Hand Qty"] = pd.to_numeric(df["On Hand Qty"], errors='coerce').fillna(0).astype(int)
    df["Qty Sold"] = pd.to_numeric(df["Qty Sold"], errors='coerce').fillna(0).astype(int)

    # Optional Profit Calculation
    df["Profit"] = df["Total Sold"] - df["Total Buy Price"]
    df["Profit Margin"] = df["Profit"] / df["Total Buy Price"].replace(0, np.nan) * 100
    df["Profit Margin"] = df["Profit Margin"].replace([np.inf, -np.inf], 0).fillna(0).round(2)

    return df


# INVENTORY DASHBOARD --------------------------------------------------------------------------------------------------------------------------------------------

if page == "Inventory Dashboard":
    df_raw = get_inventory_data()
    df = preprocess_inventory_data(df_raw)

    st.title("2025 Inventory Dashboard")

    # 🔗 Sheet link expander
    with st.expander("🔗 View Spreadsheet Link", expanded=False):
        st.markdown("""
        [Copy of BD Demand On Hand Inventory](https://docs.google.com/spreadsheets/d/1zjwGFngmxPszz_-imJvVqbhi856zgJLSpiI_WmIO9vI)
        """, unsafe_allow_html=True)

    st.markdown("""
    <style>
    .metric-card {
        background: linear-gradient(90deg, #fff0ff, #cfdafd);
        border-radius: 20px;
        padding: 1.2rem 1.2rem 0.5rem 1.2rem;
        margin-bottom: 2px;
        box-shadow: 0 8px 20px rgba(0,0,0,0.12);
        height: 155px;
        display: flex;
        flex-direction: column;
        justify-content: flex-end;     /* Bottom vertical alignment */
        align-items: flex-start;       /* Left horizontal alignment */
        transition: all 0.25s ease;
        text-align: left;
        max-width: 200px;
        width: 100%;
        margin: 0 auto 1rem auto;
    }
    .metric-card:hover {
        transform: translateY(-6px);
        box-shadow: 0 10px 24px rgba(0, 0, 0, 0.15);
    }
    </style>
    """, unsafe_allow_html=True)

    # --- Metric Card Function ---
    def metric_card(title, value, icon_url, suffix="", value_color="#1c1c1c"):
        st.markdown(f"""
            <div class="metric-card">
                <div style="margin-bottom: 25px;">
                    <img src="{icon_url}" width="32" style="opacity: 0.6;" />
                </div>
                <div style='color: #555; font-weight: 550; font-size: 12px; margin-bottom: 3px;'>{title}</div>
                <div style='font-size: 24px; font-weight: 750; color: {value_color};'>{value} {suffix}</div>
            </div>
        """, unsafe_allow_html=True)

    filtered_df = df.copy()

    # ✨ Fix "On Hand Qty" based on "Availability" (only inside memory, no file editing)
    filtered_df["On Hand Qty"] = filtered_df.apply(
        lambda row: 0 if str(row.get("Availability", "")).lower() == "sold" else row.get("On Hand Qty", 0),
        axis=1
    )

    # 🟦 Extract planned data BEFORE calling compute_metrics
    planned_df = filtered_df[filtered_df["Availability"].str.lower() == "planned"]

    # --- Metrics Calculation ---
    def compute_metrics(dataframe, planned_df):
        dataframe["Inbounded Qty"] = pd.to_numeric(dataframe["Inbounded Qty"], errors="coerce").fillna(0)
        dataframe["Qty Sold"] = pd.to_numeric(dataframe["Qty Sold"], errors="coerce").fillna(0)
        dataframe["Total Sold"] = pd.to_numeric(dataframe["Total Sold"], errors="coerce").fillna(0)
        dataframe["Sales Cycle"] = pd.to_numeric(dataframe["Sales Cycle"], errors="coerce").fillna(0)

        planned_df["Inbounded Qty"] = pd.to_numeric(planned_df["Inbounded Qty"], errors="coerce").fillna(0)
        planned_value = planned_df["Total Buy Price"].sum()
        planned_qty = planned_df["Inbounded Qty"].sum()

        return {
            "total_items": dataframe.shape[0],
            "inbounded_value": dataframe["Total Buy Price"].sum(),
            "inbounded_qty": dataframe["Inbounded Qty"].sum(),
            "total_sales": dataframe["Total Sold"].sum(),
            "avg_sales_cycle": dataframe["Sales Cycle"].mean(),
            "total_on_hand": dataframe["Inbounded Qty"].sum() - dataframe["Qty Sold"].sum(),
            "total_qty_sold": dataframe["Qty Sold"].sum(),
            "remaining_value": dataframe["Total Buy Price"].sum() - dataframe["Total Sold"].sum(),
            "planned_value": planned_value,
            "planned_qty": planned_qty
        }

    overview_metrics = compute_metrics(filtered_df, planned_df)

    # --- Tab Layout ---
    page = st.radio(
        "Navigate Inventory",
        ["Inventory Overview", "Inventory Per Client", "Upload Inventory", "Update Inventory"],
        horizontal=True
    )

    # 📊 OVERVIEW TAB
    if page == "Inventory Overview":

        st.markdown("### Inventory Summary")
        
        # ✅ Step 1: Convert "YY MMM Inbounded" to datetime format (e.g., "2025 Apr" → datetime)
        df["Parsed Month"] = pd.to_datetime(df["YY MMM Inbounded"], format="%Y %b", errors="coerce")

        # ✅ Step 2: Drop NaN and sort
        sorted_months = df.dropna(subset=["Parsed Month"]) \
                        .sort_values("Parsed Month")["YY MMM Inbounded"] \
                        .unique()

        # ✅ Step 3: Month filter dropdown (sorted chronologically)
        selected_month = st.selectbox("📅 Filter by Month Inbounded", ["All"] + list(sorted_months))

        # ✅ Step 4: Apply filter
        filtered_df = df.copy()
        if selected_month != "All":
            filtered_df = filtered_df[filtered_df["YY MMM Inbounded"] == selected_month]

        # ✅ Step 5: Filter planned from filtered set
        planned_df = filtered_df[filtered_df["Availability"].str.lower() == "planned"]

        # ✅ Step 6: Recompute metrics
        overview_metrics = compute_metrics(filtered_df, planned_df)

        col1, col2, col3, col4 = st.columns([2, 2, 2, 2])  # Col1 = placeholder, rest balanced

        # --- Column 1: Placeholder for Planned Inbound ---
        with col1:
            metric_card(
                "Planned Inbound - Total Amount",
                f"₱{overview_metrics['planned_value']:,.0f}",
                "https://cdn-icons-png.flaticon.com/128/11502/11502264.png")

            metric_card(
                "No. of Planned Inbound",
                f"{int(overview_metrics['planned_qty']):,} items",
                "https://cdn-icons-png.flaticon.com/128/3061/3061153.png")

        # --- Column 2: Inbounded Items ---
        with col2:
            metric_card("Inbound - Total Amount", f"₱{overview_metrics['inbounded_value']:,.0f}", "https://cdn-icons-png.flaticon.com/128/17762/17762977.png")
            metric_card("No. of Inbounded Items", f"{int(overview_metrics['inbounded_qty']):,} items", "https://cdn-icons-png.flaticon.com/128/3624/3624106.png")


        # --- Column 3: Sold Items ---
        with col3:
            metric_card("Sold - Total Amount", f"₱{overview_metrics['total_sales']:,.0f}", "https://cdn-icons-png.flaticon.com/128/10614/10614830.png", "", "#ff7582")
            metric_card("No. of Sold Items", f"{int(overview_metrics['total_qty_sold']):,} items", "https://cdn-icons-png.flaticon.com/128/16804/16804957.png")

        # --- Column 4: Remaining Stock ---
        remaining_value = max(overview_metrics["inbounded_value"] - overview_metrics["total_sales"], 0)

        with col4:
            metric_card("Remaining - Total Amount", f"₱{remaining_value:,.0f}", "https://cdn-icons-png.flaticon.com/128/1611/1611179.png", "", "#355c7d")
            metric_card("No. of Remaining Items", f"{int(overview_metrics['total_on_hand']):,} items", "https://cdn-icons-png.flaticon.com/128/11475/11475431.png")

        with st.container():
            expander = st.expander("📋 View Overall Client Details", expanded=False)
            with expander:
                client_summary = df.groupby("Client").agg({
                    "On Hand Qty": "sum",
                    "Buy Price": "sum",
                    "Qty Sold": "sum",
                    "Total Sold": "sum"
                }).reset_index()

                client_summary = client_summary.rename(columns={
                    "Client": "Client",
                    "On Hand Qty": "Total On Hand Qty",
                    "Buy Price": "Total Buy Price",
                    "Qty Sold": "Total Qty Sold",
                    "Total Sold": "Total Sold"
                })

                client_summary["Total Buy Price"] = client_summary["Total Buy Price"].apply(lambda x: f"₱{x:,.0f}")
                client_summary["Total Sold"] = client_summary["Total Sold"].apply(lambda x: f"₱{x:,.0f}")

                st.dataframe(client_summary, use_container_width=True)

        # --- Row 1: Availability + Monthly Sales Trend ---
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("#### 📊 Availability Breakdown")
            availability_counts = filtered_df["Availability"].value_counts().reset_index()
            availability_counts.columns = ["Availability", "Count"]
            fig_avail = px.pie(
                availability_counts,
                names="Availability",
                values="Count",
                title="",
                height=280
            )
            st.plotly_chart(fig_avail, use_container_width=True, key="availability_chart_tab1")

        with col2:
            st.markdown("#### 📈 Monthly Sales Trend")
            filtered_df["Month"] = filtered_df["Date Sold"].dt.to_period("M").astype(str)
            sales_by_month = filtered_df.groupby("Month")["Total Sold"].sum().reset_index()
            fig_trend = px.line(sales_by_month, x="Month", y="Total Sold", title="", markers=True, height=280)
            
            st.plotly_chart(fig_trend, use_container_width=True, key="monthly_sales_trend_tab1")

        # --- Row 2: Client Summary + Highest Inventory Month ---
        col3, col4 = st.columns([1, 1])
        with col3:
            st.markdown("#### 👥 Client-Based Summary")

            # Format and sort data
            summary_df = df.groupby("Client").agg({
                "Total Sold": "sum",
                "Qty Sold": "sum",
                "Sales Cycle": "mean"
            }).reset_index()

            summary_df = summary_df.sort_values("Total Sold", ascending=False)  # Sort here

            # Format labels: ₱ with commas (rounded)
            summary_df["Formatted Total"] = summary_df["Total Sold"].apply(lambda x: f"₱{int(round(x)):,}")

            # Make sure "Client" is categorical to preserve sort order
            summary_df["Client"] = pd.Categorical(summary_df["Client"], categories=summary_df["Client"], ordered=True)

            # Create bar chart
            fig_client = px.bar(
                summary_df,
                x="Client",
                y="Total Sold",
                text="Formatted Total",
                title="",
                height=320
            )

            # Styling the bars and text
            fig_client.update_traces(
                textposition="outside",
                marker_color="#1f77b4",
                textfont=dict(size=12)
            )

            # Layout adjustments
            fig_client.update_layout(
                yaxis_title="Total Sold (₱)",
                xaxis_title="Client",
                xaxis_tickangle=-30,
                margin=dict(t=20, b=80, l=60, r=20),
                height=360
            )

            st.plotly_chart(fig_client, use_container_width=True, key="client_summary_tab1")

        with col4:
            st.markdown("#### 🏆 Highest Inventory Month")

            # ✅ Read from "YY MMM Inbounded"
            inventory_df = filtered_df.copy()
            inventory_df = inventory_df[["YY MMM Inbounded", "Inbounded Qty"]].dropna()
            
            # Remove invalid years (like 1899)
            inventory_df = inventory_df[inventory_df["YY MMM Inbounded"].str.startswith(("2024", "2025"))]

            # Convert Inbounded Qty to numeric
            inventory_df["Inbounded Qty"] = pd.to_numeric(inventory_df["Inbounded Qty"], errors="coerce")
            inventory_df = inventory_df.dropna(subset=["Inbounded Qty"])

            # Rename column for plotting
            inventory_df = inventory_df.rename(columns={"YY MMM Inbounded": "Month_Year"})

            # Group by Month-Year
            inbound_by_month = inventory_df.groupby("Month_Year")["Inbounded Qty"].sum().reset_index()

            # Sort top-to-bottom by highest qty
            inbound_by_month = inbound_by_month.sort_values("Inbounded Qty", ascending=True)

            # Ensure this order is used in Y-axis
            inbound_by_month["Month_Year"] = pd.Categorical(
                inbound_by_month["Month_Year"],
                categories=inbound_by_month["Month_Year"],  # maintain top-to-bottom order
                ordered=True
            )

            # Add labels
            inbound_by_month["Label"] = inbound_by_month["Inbounded Qty"].apply(lambda x: f"{int(x):,} units")

            # Plot
            fig_inbound = px.bar(
                inbound_by_month,
                x="Inbounded Qty",
                y="Month_Year",
                orientation="h",
                text="Label",
                height=320
            )

            fig_inbound.update_traces(
                textposition="outside",
                marker_color="#3b82f6",
                textfont=dict(size=12)
            )

            fig_inbound.update_layout(
                xaxis_title="Inbounded Quantity",
                yaxis_title="Month (2024–2025)",
                margin=dict(l=80, r=20, t=20, b=40)
            )

            st.plotly_chart(fig_inbound, use_container_width=True, key="highest_month_tab")

            if not inbound_by_month.empty:
                highest = inbound_by_month.loc[inbound_by_month["Inbounded Qty"].idxmax()]
                st.caption(f"📦 **Highest Month:** {highest['Month_Year']} ({int(highest['Inbounded Qty']):,} units)")


        # --- Full Table ---
        st.subheader("📋 Inventory Table")
        st.dataframe(filtered_df, use_container_width=True)

    if page == "Inventory Per Client":

        client_options = sorted(df["Client"].unique())
        selected_client = st.selectbox("🔍 Choose Client for Detailed View", client_options)

        filtered_df = df[df["Client"] == selected_client]

        # Recompute metrics for the selected client only
        planned_df = filtered_df[filtered_df["Availability"].str.lower() == "planned"]
        client_metrics = compute_metrics(filtered_df, planned_df)

        st.markdown(f"### Inventory Summary - `{selected_client}`")

        if selected_client != "All":
            col1, col2, col3, col4 = st.columns([2, 2, 2, 2])

            with col1:
                metric_card("Planned Inbound - Total Amount", f"₱{client_metrics['planned_value']:,.0f}", "https://cdn-icons-png.flaticon.com/128/11502/11502264.png")
                metric_card("No. of Planned Inbound", f"{int(client_metrics['planned_qty']):,} items", "https://cdn-icons-png.flaticon.com/128/3061/3061153.png")

            with col2:
                metric_card("Inbound - Total Amount", f"₱{client_metrics['inbounded_value']:,.0f}", "https://cdn-icons-png.flaticon.com/128/17762/17762977.png")
                metric_card("No. of Inbounded Items", f"{int(client_metrics['inbounded_qty']):,} items", "https://cdn-icons-png.flaticon.com/128/3624/3624106.png")

            with col3:
                metric_card("Sold - Total Amount", f"₱{client_metrics['total_sales']:,.0f}", "https://cdn-icons-png.flaticon.com/128/10614/10614830.png", "", "#ff7582")
                metric_card("No. of Sold Items", f"{int(client_metrics['total_qty_sold']):,} items", "https://cdn-icons-png.flaticon.com/128/16804/16804957.png")

            with col4:
                remaining_value = max(0, client_metrics["inbounded_value"] - client_metrics["total_sales"])
                metric_card("Remaining - Total Amount", f"₱{remaining_value:,.0f}", "https://cdn-icons-png.flaticon.com/128/1611/1611179.png", "", "#355c7d")
                metric_card("No. of Remaining Items", f"{int(client_metrics['total_on_hand']):,} items", "https://cdn-icons-png.flaticon.com/128/11475/11475431.png")

            # ✅ Move this OUTSIDE the columns so it spans full width
            with st.container():
                expander = st.expander("📋 View Item List", expanded=False)
                with expander:
                    columns_to_show = [
                        "Description",
                        "On Hand Qty",
                        "Buy Price",
                        "Qty Sold",
                        "Total Sold"
                    ]

                    item_table = filtered_df[columns_to_show].dropna(subset=["Description"])
                    item_table = item_table.sort_values("Total Sold", ascending=False).reset_index(drop=True)

                    item_table["Buy Price"] = item_table["Buy Price"].apply(lambda x: f"₱{x:,.0f}")
                    item_table["Total Sold"] = item_table["Total Sold"].apply(lambda x: f"₱{x:,.0f}")

                    st.data_editor(
                        item_table,
                        use_container_width=True,
                        height=350,
                        disabled=True,
                        hide_index=True
                    )

        else:
            st.info("Select a specific client from the dropdown above to view detailed metrics.")
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("#### 📊 Availability Breakdown")
            availability_counts = filtered_df["Availability"].value_counts().reset_index()
            availability_counts.columns = ["Availability", "Count"]
            fig_avail = px.pie(
                availability_counts,
                names="Availability",
                values="Count",
                title="",
                height=280
            )
            st.plotly_chart(fig_avail, use_container_width=True, key="availability_chart_tab2")

        with col2:
            st.markdown("#### 👥 Client-Based Summary")

            # Format data
            summary_df = df.groupby("Client").agg({
                "Total Sold": "sum",
                "Qty Sold": "sum",
                "Sales Cycle": "mean"
            }).reset_index()

            # Format labels: ₱ with commas (rounded)
            summary_df["Formatted Total"] = summary_df["Total Sold"].apply(lambda x: f"₱{int(round(x)):,}")
            summary_df = summary_df.sort_values("Total Sold", ascending=False)  # 👈 Add this line

            # Create bar chart
            fig_client = px.bar(
                summary_df,
                x="Client",
                y="Total Sold",
                text="Formatted Total",
                title="",
                height=320
            )

            # Styling the bars and text
            fig_client.update_traces(
                textposition="outside",
                marker_color="#1f77b4",
                textfont=dict(size=12)
            )

            # Layout adjustments
            fig_client.update_layout(
                yaxis_title="Total Sold (₱)",
                xaxis_title="Client",
                xaxis_tickangle=-30,
                margin=dict(t=20, b=80, l=60, r=20),
                height=360
            )

            st.plotly_chart(fig_client, use_container_width=True, key="client_summary_tab2")


    if page == "Upload Inventory":
        st.subheader("Upload Inventory")

        sheet_url = st.text_input("Paste the Google Sheet URL of the PIF")

        def clean_numeric_column(series):
            return pd.to_numeric(
                series.astype(str)
                .str.replace("₱", "", regex=False)
                .str.replace(",", "", regex=False)
                .str.strip(),
                errors="coerce"
            ).fillna(0)

        if sheet_url:
            try:
                match = re.search(r"/spreadsheets/d/([a-zA-Z0-9-_]+)", sheet_url)
                if not match:
                    st.error("❌ Invalid Google Sheets URL")
                else:
                    sheet_id = match.group(1)
                    sh = gc.open_by_key(sheet_id)

                    inbound_ws = sh.worksheet("Inbound Report")
                    offer_ws = sh.worksheet("Offer/Valuation")

                    client_name = offer_ws.acell("D3").value
                    date_received = inbound_ws.acell("D3").value

                    inbound_raw = inbound_ws.get_all_values()
                    raw_header_row = inbound_raw[5][2:]
                    headers = []
                    seen = set()
                    for h in raw_header_row:
                        h_clean = h.strip()
                        headers.append(h_clean if h_clean and h_clean not in seen else f"Unnamed_{len(headers)}")
                        seen.add(h_clean)

                    data_rows = [row[2:2+len(headers)] for row in inbound_raw[6:] if any(row[2:])]
                    inbound_df = pd.DataFrame(data_rows, columns=headers)

                    # Clean column names and strip whitespace
                    inbound_df.columns = inbound_df.columns.str.strip().str.replace("\n", " ").str.replace(r"\s+", " ", regex=True)

                    # Filter non-empty SKU/Product rows
                    inbound_df = inbound_df[
                        (inbound_df["Humble SKU"].astype(str).str.strip() != "") &
                        (inbound_df["Product Name"].astype(str).str.strip() != "")
                    ].reset_index(drop=True)

                    if inbound_df.empty:
                        st.warning("⚠️ The Inbound Report sheet is empty.")
                    else:
                        parsed_date = pd.to_datetime(date_received, errors="coerce")
                        date_str = parsed_date.strftime("%-m/%-d/%y") if not pd.isna(parsed_date) else ""
                        month_str = parsed_date.strftime("%b") if not pd.isna(parsed_date) else ""
                        yy_mmm_str = parsed_date.strftime("%Y %b") if not pd.isna(parsed_date) else ""
                        num_valid_rows = len(inbound_df)

                        # Clean numeric fields
                        inbound_df["Actual Quantity"] = clean_numeric_column(inbound_df["Actual Quantity"])
                        inbound_df["Unit Offer Price"] = clean_numeric_column(inbound_df["Unit Offer Price"])
                        inbound_df["Unit Valuation"] = clean_numeric_column(inbound_df["Unit Valuation"])
                        inbound_df["Total Offer Price"] = clean_numeric_column(inbound_df["Total Offer Price"])
                        inbound_df["Total Valuation"] = clean_numeric_column(inbound_df["Total Valuation"])

                        # Process only needed columns
                        processed = pd.DataFrame({
                            "Client": [client_name] * num_valid_rows,
                            "HUMBLE SKU": inbound_df["Humble SKU"],
                            "Description": inbound_df["Product Name"],
                            "Inbounded Qty": inbound_df["Actual Quantity"],
                            "On Hand Qty": inbound_df["Actual Quantity"],
                            "Buy Price": inbound_df["Unit Offer Price"],
                            "Total Buy Price": inbound_df["Total Offer Price"],
                            "Selling Price": inbound_df["Unit Valuation"],
                            "Total Selling Price": inbound_df["Total Valuation"],
                            "Availability": ["On Hand"] * num_valid_rows,
                            "Date Inbounded": [date_str] * num_valid_rows,
                        })

                        st.success("✅ Preview: Inbounds ready to append")
                        st.dataframe(processed)

                        if st.button("Append to Inventory Backend"):
                            inventory_ws = gc.open_by_key("1zjwGFngmxPszz_-imJvVqbhi856zgJLSpiI_WmIO9vI").get_worksheet(4)
                            existing_values = inventory_ws.get_all_values()

                            first_data_row = 2
                            key_col_indices = [0, 1, 2]
                            first_empty_row = None

                            for i, row in enumerate(existing_values[first_data_row - 1:], start=first_data_row):
                                if all((len(row) <= col or str(row[col]).strip() == "") for col in key_col_indices):
                                    first_empty_row = i
                                    break

                            if first_empty_row is None:
                                first_empty_row = len(existing_values) + 1

                            # Map processed columns to specific columns in the sheet
                            column_map = {
                                "Client": "A",
                                "HUMBLE SKU": "B",
                                "Description": "C",
                                "Inbounded Qty": "D",
                                "On Hand Qty": "E",
                                "Buy Price": "G",
                                "Total Buy Price": "H",
                                "Selling Price": "I",
                                "Total Selling Price": "J",
                                "Availability": "M",
                                "Date Inbounded": "O"
                            }

                            for col_name, col_letter in column_map.items():
                                cell_range = f"{col_letter}{first_empty_row}:{col_letter}{first_empty_row + num_valid_rows - 1}"
                                values = processed[col_name].values.reshape(-1, 1).tolist()
                                inventory_ws.update(cell_range, values, value_input_option="USER_ENTERED")

                            st.success(f"✅ Successfully added {num_valid_rows} rows to Inventory Sheet!")

            except Exception as e:
                st.error(f"❌ Error: {e}")
                
    if page == "Update Inventory":
        st.subheader("📝 Update Inventory")

        df_inventory = get_inventory_data()
        df_available = df_inventory[df_inventory["Availability"].str.lower() != "sold"].copy()

        client_list = sorted(df_available["Client"].unique())
        selected_client = st.selectbox("Select Client", client_list)

        filtered_by_client = df_available[df_available["Client"] == selected_client]
        desc_list = sorted(filtered_by_client["Description"].unique())
        selected_desc = st.selectbox("Select Description", desc_list)

        filtered_combo = filtered_by_client[filtered_by_client["Description"] == selected_desc]
        price_list = sorted(filtered_combo["Total Buy Price"].unique())
        selected_price = st.selectbox("Select Total Buy Price", price_list)

        final_row = filtered_combo[filtered_combo["Total Buy Price"] == selected_price].iloc[0]

        def safe_int(val):
            try:
                return int(str(val).replace(",", "").strip())
            except:
                return 0

        def safe_float(val):
            try:
                return float(str(val).replace("₱", "").replace(",", "").strip())
            except:
                return 0.0

        original_qty_sold = safe_int(final_row["Qty Sold"])
        original_on_hand = safe_int(final_row["On Hand Qty"])
        unit_price = safe_float(final_row["Buy Price"])

        max_qty_sold = original_on_hand + original_qty_sold
        new_qty_sold = st.number_input("Qty Sold", min_value=0, max_value=max_qty_sold, value=original_qty_sold)

        new_on_hand = max(original_on_hand - (new_qty_sold - original_qty_sold), 0)
        selling_price = safe_float(final_row["Selling Price"])
        computed_total_sold = new_qty_sold * selling_price

        st.markdown(f"On Hand Qty: `{new_on_hand}`")
        st.markdown(f"Total Sold: ₱{computed_total_sold:,.2f}")

        if st.button("Update Inventory Row"):
            try:
                inventory_ws = gc.open_by_key("1zjwGFngmxPszz_-imJvVqbhi856zgJLSpiI_WmIO9vI").get_worksheet(4)
                row_number = df_inventory[
                    (df_inventory["Client"] == selected_client) &
                    (df_inventory["Description"] == selected_desc) &
                    (df_inventory["Total Buy Price"] == selected_price)
                ].index[0] + 3

                inventory_ws.update(f"E{row_number}", [[new_on_hand]])           # On Hand Qty
                inventory_ws.update(f"F{row_number}", [[new_qty_sold]])          # Qty Sold
                inventory_ws.update(f"K{row_number}", [[computed_total_sold]])   # Total Sold

                # Optional: compute Profit = Total Sold - Total Buy Price
                buy_price = safe_float(final_row["Total Buy Price"])
                profit = computed_total_sold - buy_price
                inventory_ws.update(f"L{row_number}", [[profit]])                # Profit

                if new_on_hand == 0:
                    inventory_ws.update(f"M{row_number}", [["Sold"]])            # Availability

                st.success("Inventory row updated successfully.")

            except Exception as e:
                st.error(f"Failed to update sheet: {e}")

# INBOUNDS CONNECTION --------------------------------------------------------------------------------------------------------------------------------------------

@st.cache_data(ttl=60)
def get_inventory_data():
    credentials_path = "inbounds-dashboard-7bbf8f7a4f59.json"
    scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    credentials = Credentials.from_service_account_file(credentials_path, scopes=scopes)
    gc = gspread.authorize(credentials)

    spreadsheet_id = "1C13KdQDIssPB02vWd-ma2t6yWDpiIDB28e7dkc2M-vc"
    sh = gc.open_by_key(spreadsheet_id)
    worksheet = sh.get_worksheet(1)
    data = worksheet.get_all_values()

    if not data:
        return pd.DataFrame()

    raw_headers = data[0]
    headers = [h.strip() for h in raw_headers if h.strip() != ""]
    df_data = [row[:len(headers)] for row in data[1:] if any(cell.strip() for cell in row)]
    df = pd.DataFrame(df_data, columns=headers)

    # Convert Date
    date_col = headers[0]
    df[date_col] = pd.to_datetime(df[date_col], errors="coerce")
    df = df[df[date_col].dt.year == 2025]

    # Format date nicely
    df[date_col] = df[date_col].dt.strftime("%b %d, %Y").str.replace(" 0", " ")

    if "Month" in df.columns:
        df.drop(columns=["Month"], inplace=True)

    # Convert QTY to numeric
    if "QTY" in df.columns:
        df["QTY"] = pd.to_numeric(df["QTY"], errors="coerce")

    return df.reset_index(drop=True)

def render_delta(delta):
    if delta is None:
        return ""

    symbol = "↑" if delta > 0 else ("↓" if delta < 0 else "→")
    color = "green" if delta > 0 else ("red" if delta < 0 else "gray")
    return f"""<span style='color:{color}; font-size:12px; font-weight:600;'>
        {symbol} {abs(delta):.2f}% <i>vs last month</i>
    </span>"""

# Safely shorten labels and ensure uniqueness
def make_unique_labels(labels, max_length=25):
    seen = {}
    result = []
    for label in labels:
        short = label if len(label) <= max_length else label[:max_length].rstrip() + "..."
        if short in seen:
            seen[short] += 1
            short += f" ({seen[short]})"
        else:
            seen[short] = 1
        result.append(short)
    return result

# INBOUNDS DASHBOARD -----------------------------------------------------------------------------------------

if page == "Inbounds Dashboard":
    # 1. Get and clean raw data
    df_raw = get_inventory_data()
    df = df_raw.copy()

    valid_tiers = ["Tier 1", "Tier 2", "Tier 3", "Tier 4"]

    # 2. Extract fields
    df['Date Parsed'] = pd.to_datetime(df['Date'], errors='coerce')
    df['Month_Year'] = df['Date Parsed'].dt.strftime('%b %Y')

    # 3. Available months
    available_months = sorted(
        df['Month_Year'].dropna().unique(),
        key=lambda x: pd.to_datetime(x, format='%b %Y')
    )

    # 4. Title and dropdown
    st.title("Inbounds Dashboard")

    # 🔗 Sheet link expander
    with st.expander("🔗 View Spreadsheet Link", expanded=False):
        st.markdown("""
        [2025 Humble Inbounds](https://docs.google.com/spreadsheets/d/1C13KdQDIssPB02vWd-ma2t6yWDpiIDB28e7dkc2M-vc/edit?gid=1810444796)
        """, unsafe_allow_html=True)

    selected_month = st.selectbox("📅 Filter by Month of Inbound", options=["All"] + available_months, index=0, key="month_filter_dropdown")

    # 5. Filter by month
    if selected_month != "All":
        df_filtered = df[df['Month_Year'] == selected_month]
    else:
        df_filtered = df.copy()

    # 6. Recompute metrics
    monthly_qty = df.groupby('Month_Year')['QTY'].sum().sort_index()

    if selected_month != "All":
        current_qty = monthly_qty.get(selected_month, 0)

        current_month_datetime = pd.to_datetime(selected_month, format='%b %Y')
        previous_month_datetime = current_month_datetime - pd.DateOffset(months=1)
        previous_month_str = previous_month_datetime.strftime('%b %Y')
        previous_qty = monthly_qty.get(previous_month_str, 0)

        if previous_qty > 0:
            mom_delta = ((current_qty - previous_qty) / previous_qty) * 100
        else:
            mom_delta = 0.00
    else:
        current_qty = int(df['QTY'].sum())
        mom_delta = None

    # Unique accounts
    unique_accounts = df_filtered['Account'].nunique()

    # Top inbound months (full data, not filtered)
    top_months = (
        df.groupby('Month_Year')['QTY'].sum()
        .sort_values(ascending=False)
        .head(3)
        .reset_index()
        .rename(columns={'Month_Year': 'Month', 'QTY': 'Inbound Qty'})
    )

    # 👉 If a specific month is selected
    if selected_month != "All":
        # Current month quantity
        current_qty = monthly_qty.get(selected_month, 0)

        # Find previous month
        current_month_datetime = pd.to_datetime(selected_month, format='%b %Y')
        previous_month_datetime = current_month_datetime - pd.DateOffset(months=1)
        previous_month_str = previous_month_datetime.strftime('%b %Y')

        # Previous month quantity
        previous_qty = monthly_qty.get(previous_month_str, 0)

        # Calculate Month-over-Month delta
        if previous_qty > 0:
            mom_delta = ((current_qty - previous_qty) / previous_qty) * 100
        else:
            mom_delta = 0.00
    else:
        # For "All", just total sum, no MoM delta
        current_qty = int(df['QTY'].sum())
        mom_delta = None

    if selected_month != "All":
        # Get current and previous unique accounts
        current_accounts = df_filtered['Account'].nunique()

        # Get previous month
        current_month_datetime = pd.to_datetime(selected_month, format='%b %Y')
        prev_month = (current_month_datetime - pd.DateOffset(months=1)).strftime('%b %Y')

        df_prev = df[df['Month_Year'] == prev_month]
        prev_accounts = df_prev['Account'].nunique()

        if prev_accounts > 0:
            unique_delta = ((current_accounts - prev_accounts) / prev_accounts) * 100
        else:
            unique_delta = 0.00
    else:
        unique_delta = None

    # ✅ Now safe to compute metrics
    total_qty = int(df_filtered['QTY'].sum())
    unique_accounts = df_filtered['Account'].nunique()
    total_offer_price = (
        df_filtered['Total Offer Price']
        .astype(str)
        .str.replace('₱', '', regex=False)
        .str.replace(',', '', regex=False)
        .replace('', '0')  # if there are empty strings
        .astype(float)
        .sum()
    )

    card_style = """
    <style>
    .hover-card {
        background: linear-gradient(90deg, #fff0ff, #fceae6);
        border-radius: 20px;
        padding: 1.6rem 0.5rem 2rem 0.5rem;
        box-shadow: 0 4px 10px rgba(0,0,0,0.05);
        display: flex;
        flex-direction: column;
        justify-content: flex-start;
        text-align: left;
        font-size: 15px;
        font-weight: 600;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
        margin: auto;
        max-height: 185px;     
        min-width: 165px;     
        flex-shrink: 1;
        overflow: hidden;
    }

    .hover-card:hover {
        transform: translateY(-6px);
        box-shadow: 0 8px 20px rgba(0,0,0,0.12);
        position: relative;
        overflow: hidden;  /* prevents shadows or children from leaking */
    }

    .hover-card h4 {
        margin: 0 0 12px 0;
        font-size: 15px;
        margin-bottom: 1px;
    }

    .hover-card p {
        margin: 4px 0;
        font-size: 12px;
    }

    .metric-number {
        font-size: 32px;
        font-weight: 700;
        color: #4c2882;
        margin-top: 9px;
        line-height: 0.9;
        text-align: left;
    }

    .metric-delta {
        font-size: 11px;
        margin-top: 4px;
        margin-bottom: 0;
    }

    .month-value {
        font-size: 26px;
        font-weight: 650;
        margin: 5px 0;
        margin-bottom: 15x;
        color: #6756BE;
    }

    .month-value-row {
        display: flex;
        justify-content: space-between;
        gap: 10px;
        font-size: 14px;
        margin: 2px 0;
        line-height: 1.2;
        flex-wrap: wrap;
        word-break: break-word;
    }

    .month-left {
        font-weight: 600;
    }

    .month-right {
        font-weight: 650;
        color: #e25858;
    }
    </style>
    """
    st.markdown(card_style, unsafe_allow_html=True)

    # Clean offer price column
    df_filtered['Cleaned Offer Price'] = (
        df_filtered['Total Offer Price']
        .astype(str)
        .str.replace('₱', '', regex=False)
        .str.replace(',', '', regex=False)
        .replace(['', 'nan', 'NaN'], '0')
        .astype(float)
    )

    # Aggregate top accounts
    top_accounts = (
        df_filtered
        .groupby('Account', as_index=False)
        .agg({
            'QTY': 'sum',
            'Cleaned Offer Price': 'sum'
        })
        .rename(columns={
            'QTY': 'Quantity',
            'Cleaned Offer Price': 'Offer Price'
        })
        .sort_values(by='Quantity', ascending=False)
        .head(5)
    )

    # Format offer price for display
    top_accounts['Offer Price'] = top_accounts['Offer Price'].apply(lambda x: f"₱{x:,.0f}")

    # 🟪 4 Column Layout
    col1, col2, col3, col4, col5 = st.columns([1.3, 1, 1, 1, 1.3])

    with col1:
        # Tier Legend Card
        st.markdown("""
        <div class='hover-card'>
            <img src="https://cdn-icons-png.flaticon.com/128/17057/17057101.png" width="40" style="margin-bottom: 1px; display: block;" />
            <h4>Tier Legend</h4>
            <div style="font-size: 14px; line-height: 0.75; padding-left: 8px;">
                <div style="margin-bottom: 6px;">
                    <span style="font-weight: 750;color: #281048;">Tier 1</span>
                    <span style="font-weight: 650; font-size: 13px;"> – Brand New/Sealed</span>
                </div>
                <div style="margin-bottom: 6px;">
                    <span style="font-weight: 750;color: #281048;">Tier 2</span>
                    <span style="font-weight: 650; font-size: 13px;"> – Used w/ Minor Defects</span>
                </div>
                <div style="margin-bottom: 6px;">
                    <span style="font-weight: 750;color: #281048;">Tier 3</span>
                    <span style="font-weight: 650; font-size: 13px;"> – Used w/ Major Defects</span>
                </div>
                <div>
                    <span style="font-weight: 750;color: #281048;">Tier 4</span>
                    <span style="font-weight: 650; font-size: 13px;"> – Beyond Economical         Repair</span>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class='hover-card'>
            <img src="https://cdn-icons-png.flaticon.com/128/3624/3624106.png" width="40" style="margin-bottom: 8px;" />
            <h4>Inbound Quantity</h4>
            <div class='metric-number'>{current_qty:,}</div>
            <div class='metric-delta'>{render_delta(mom_delta)}</div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
        <div class='hover-card'>
            <img src="https://cdn-icons-png.flaticon.com/128/1091/1091994.png" width="40" style="margin-bottom: 8px;" />
            <h4>Offer Price</h4>
            <div class='metric-number'>₱{total_offer_price:,.0f}</div>
            <div class='metric-delta' style='visibility:hidden;'>--</div>  <!-- placeholder for alignment -->
        </div>
        """, unsafe_allow_html=True)

    with col4:
        st.markdown(f"""
        <div class='hover-card'>
            <img src="https://cdn-icons-png.flaticon.com/128/1528/1528669.png" width="40" style="margin-bottom: 8px;" />
            <h4>No. of Accounts</h4>
            <div class='metric-number'>{unique_accounts}</div>
            <div class='metric-delta'>{render_delta(unique_delta) if selected_month != "All" else ""}</div>
        </div>
        """, unsafe_allow_html=True)

        # ➡️ Small light divider
        st.markdown("""
            <hr style="border: 0.5px solid #ffffff; margin: 8px 0 12px 0;">
        """, unsafe_allow_html=True)

    # Column 4: Highest Inbound Months
    with col5:
        top_months_html = """
        <div class='hover-card'>
            <img src="https://cdn-icons-png.flaticon.com/128/16877/16877580.png" width="40" style="margin-bottom: 2px; display: block;" />
            <h4>Top Inbound Months</h4>
        """
        for _, row in top_months.iterrows():
            top_months_html += f"""<div class='month-value-row'>
                <span class='month-left'>{row['Month']}</span>
                <span class='month-right'>{int(row['Inbound Qty']):,} units</span>
            </div>"""
        top_months_html += "</div>"

        st.markdown(top_months_html, unsafe_allow_html=True)

    st.markdown("<hr style='border: 0.5px solid white; margin: 5px 0;'>", unsafe_allow_html=True)

    # Expandable Section — 3 Column Layout
    col1, col2, col3 = st.columns([1, 1, 1])

    # ➡️ Column 1: Tier Breakdown Pie
    with col1:
        with st.expander("Tier 1–4 Breakdown 📊"):
            tier_summary = (
                df_filtered[df_filtered['Tier'].isin(valid_tiers)]
                .groupby('Tier')['QTY']
                .sum()
                .reset_index()
                .sort_values(by='Tier')
            )

            fig = px.pie(
                tier_summary,
                names='Tier',
                values='QTY',
                hole=0.5
            )

            fig.update_traces(
                textposition='outside',
                insidetextorientation='radial',
                pull=0,
                rotation=90
            )

            fig.update_layout(
                height=370,
                margin=dict(t=30, b=30, l=10, r=10),
                showlegend=True,
                annotations=[dict(
                    text='Tier 4',
                    x=0.5,
                    y=0.42,
                    font_size=16,
                    showarrow=False
                )]
            )

            st.plotly_chart(fig, use_container_width=True)

    # ITEM AND OFFER PRICE
    with col2:
        with st.expander("SKU, Inbound QTY, and Offer Price"):

            # Clean up offer price values
            df_filtered['Cleaned Offer Price'] = (
                df_filtered['Total Offer Price']
                .astype(str)
                .str.replace('₱', '', regex=False)
                .str.replace(',', '', regex=False)
                .replace(['', 'nan', 'NaN'], '0')
                .astype(float)
            )

            # Group by SKU
            offer_summary_df = (
                df_filtered
                .groupby(['SKU'], as_index=False)
                .agg({
                    'QTY': 'sum',
                    'Cleaned Offer Price': 'sum'
                })
                .rename(columns={
                    'QTY': 'Total Inbound Qty',
                    'Cleaned Offer Price': 'Total Offer Price'
                })
            )

            # Format offer price
            offer_summary_df['Total Offer Price'] = offer_summary_df['Total Offer Price'].apply(
                lambda x: f"₱{x:,.2f}"
            )

            # Show table
            st.dataframe(offer_summary_df, use_container_width=True, hide_index=True)

            # Optional: make table cleaner
            st.markdown("""
                <style>
                    div[data-testid="stDataFrame"] div[role="grid"] {
                        font-size: 9px;
                    }
                </style>
            """, unsafe_allow_html=True)

    # ➡️ Column 3: Top Clients Table
    with col3:
        with st.expander("Top 5 Clients 📈"):
            top_accounts_display = top_accounts[["Account", "Offer Price", "Quantity"]].set_index("Account")

            st.dataframe(
                top_accounts_display,
                use_container_width=True,
                hide_index=False
            )

    st.divider()

    # Filter only valid Tiers
    tier_data = df_filtered[df_filtered['Tier'].isin(valid_tiers)]

    # Pivot for percentages (Feature 6)
    tier_pct_df = (
        tier_data
        .groupby(['Month_Year', 'Tier'])['QTY']
        .sum()
        .reset_index()
        .pivot(index='Month_Year', columns='Tier', values='QTY')
        .fillna(0)
    )

    tier_pct_df = tier_pct_df.sort_index(key=lambda x: pd.to_datetime(x, format='%b %Y'))

    # Force all tiers to be present as columns
    for tier in valid_tiers:
        if tier not in tier_pct_df.columns:
            tier_pct_df[tier] = 0

    # Reorder columns for consistency
    tier_pct_df = tier_pct_df[valid_tiers]

    # Recalculate percentages (with all columns now guaranteed)
    tier_pct_percent = tier_pct_df.div(tier_pct_df.sum(axis=1), axis=0) * 100

    # Pivot for counts (Feature 7)
    tier_count_df = tier_pct_df.copy()  # already sorted

    # x2-column layout
    col_left, col_right = st.columns(2)

    # 📊 FEATURE 6: Tier % Breakdown Per Month
    with col_left:
        st.subheader("📊 Tier % per Month")
        fig_pct = go.Figure()

        for tier in valid_tiers:
            fig_pct.add_trace(go.Bar(
                name=tier,
                y=tier_pct_percent.index,
                x=tier_pct_percent[tier],
                orientation='h',
                marker=dict(line=dict(width=0)),
                width=0.4,
                text=[f"{int(y):,} units" for y in tier_count_df[tier]],
                textposition='auto',
                hovertemplate=f"{tier}: %{{x:.1f}}%<br>%{{text}}"
            ))

        fig_pct.update_layout(
            barmode='stack',
            height=380,
            bargap=0.25,  # adds vertical spacing between bars
            margin=dict(l=40, r=20, t=30, b=30),
            xaxis=dict(title="Percentage"),
            yaxis=dict(title="Month"),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )

        st.plotly_chart(fig_pct, use_container_width=True)


    # 📈 FEATURE 7: Tier Count Trend Per Month
    with col_right:
        st.subheader("📈 Tier Count per Month")

        chart_type = st.radio(
            "Chart Type", ["Bar", "Line"],
            horizontal=True, key="tier_chart_toggle"
        )

        fig_count = go.Figure()

        for tier in valid_tiers:
            if chart_type == "Bar":
                fig_count.add_trace(go.Bar(
                    name=tier,
                    x=tier_count_df.index,
                    y=tier_count_df[tier],
                    text=[f"{int(y):,} units" for y in tier_count_df[tier]],  # ✅ show labels
                    textposition='outside',
                    hovertemplate=f"{tier}: %{{y}} units"
                ))
            else:
                fig_count.add_trace(go.Scatter(
                    name=tier,
                    x=tier_count_df.index,
                    y=tier_count_df[tier],
                    mode="lines+markers+text",
                    text=[f"{int(y):,} units" for y in tier_count_df[tier]],  # optional for line
                    textposition='top center',
                    hovertemplate=f"{tier}: %{{y}} units"
                ))

        fig_count.update_layout(
            barmode='group' if chart_type == "Bar" else None,
            height=400,
            margin=dict(l=40, r=20, t=30, b=40),
            xaxis=dict(title="Month"),
            yaxis=dict(title="Quantity"),
            uniformtext_minsize=8,
            uniformtext_mode='hide'
        )

        st.plotly_chart(fig_count, use_container_width=True)
    
    st.divider()

    # 🛠 Function to clean Specific Remarks
    def clean_specific_remark(remark):
        if pd.isna(remark) or remark.strip() == "":
            return None  # Exclude empty
        remark = remark.strip()
        if "working" in remark.lower():
            return "Working"
        elif "defective" in remark.lower():
            return "Defective"
        else:
            return remark  # Keep full text if no keyword matched

    # ----------------------------
    # 🎛️ Filter options
    col_tier, col_account = st.columns(2)

    with col_tier:
        tier_filter = st.selectbox(
            "Filter by Tier (optional)",
            ["All"] + valid_tiers,
            key="category_tier_filter"
        )

    with col_account:
        account_filter = st.selectbox(
            "Filter by Account (optional)",
            ["All"] + sorted(df_filtered['Account'].unique()),
            key="category_account_filter"
        )
        
    # ----------------------------
    # 📄 Apply filters to base DataFrame
    df_cat_filtered = df_filtered.copy()
    if tier_filter != "All":
        df_cat_filtered = df_cat_filtered[df_cat_filtered['Tier'] == tier_filter]

    if account_filter != "All":
        df_cat_filtered = df_cat_filtered[df_cat_filtered['Account'] == account_filter]

    # ----------------------------
    # 📊 Count per Cleaned Type
    type_counts = df_cat_filtered.groupby("Cleaned Type")['QTY'].sum().sort_values(ascending=False)
    type_percent = (type_counts / type_counts.sum()) * 100

    type_plot_df = pd.DataFrame({
        'Cleaned Type': type_counts.index,
        'Quantity': type_counts.values,
        'Percent': type_percent.values
    })

    # ----------------------------
    # 🧰 Issues Count Chart (Processed Remarks)
    # Apply the cleaning
    df_cat_filtered["Processed Remarks"] = df_cat_filtered["Specific Remarks"].apply(clean_specific_remark)

    # Remove empty processed remarks
    df_issues_filtered = df_cat_filtered[df_cat_filtered["Processed Remarks"].notna()]

    # Group and sort
    issue_counts = df_issues_filtered.groupby("Processed Remarks")['QTY'].sum().sort_values(ascending=False)
    issue_plot_df = issue_counts.head(10).reset_index().rename(columns={'QTY': 'Quantity'})

    # ----------------------------
    # 📊 Chart Layout: 2 Columns
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### Count per Type")

        # 1. Sort by Quantity descending, then reverse for top-to-bottom layout
        type_plot_df = type_plot_df.sort_values(by='Quantity', ascending=False)

        # 2. Format Percent and Labels
        type_plot_df['Label'] = [
            f"{int(qty):,} units ({int(pct)}%)" for qty, pct in zip(type_plot_df['Quantity'], type_plot_df['Percent'])
        ]

        # 3. Plot with reversed y for top-to-bottom effect
        fig_type = go.Figure()
        fig_type.add_trace(go.Bar(
            x=type_plot_df['Quantity'],
            y=type_plot_df['Cleaned Type'],
            orientation='h',
            text=type_plot_df['Label'],
            textposition='outside',
            marker_color='#4c2882'
        ))

        fig_type.update_layout(
            height=500,
            margin=dict(l=60, r=20, t=30, b=30),
            yaxis=dict(title="", automargin=True, autorange='reversed'),  # 👈 This flips top to bottom
            xaxis=dict(title="Units", tickformat=",d"),
        )

        st.plotly_chart(fig_type, use_container_width=True)

    with col2:
        st.markdown("### Issues Count")

        # Group by 'Matrix Description' and sum QTY
        issues_df = df_filtered[df_filtered["Matrix Description"].notna() & (df_filtered["Matrix Description"].str.strip() != "")]

        # Proceed only if there's valid data
        if not issues_df.empty:
            issue_counts = (
                issues_df.groupby("Matrix Description")["QTY"]
                .sum()
                .reset_index()
                .rename(columns={"Matrix Description": "Issue", "QTY": "Quantity"})
                .sort_values(by="Quantity", ascending=False)
            )

            # Limit to Top 10
            issue_counts = issue_counts.head(10)

            # Wrap long labels
            issue_counts["Issue Wrapped"] = issue_counts["Issue"].apply(lambda x: "<br>".join([x[i:i+30] for i in range(0, len(x), 30)]))

            fig_issue = go.Figure()
            fig_issue.add_trace(go.Bar(
                x=issue_counts['Quantity'],
                y=issue_counts['Issue Wrapped'],
                orientation='h',
                text=[f"{int(qty):,} units" for qty in issue_counts['Quantity']],
                textposition='outside',
                marker_color='#4c2882'
            ))

            fig_issue.update_layout(
                height=500,
                margin=dict(l=60, r=20, t=30, b=30),
                yaxis=dict(title="", tickfont=dict(size=11)),
                xaxis=dict(title="Units"),
            )
            fig_issue.update_yaxes(autorange="reversed")

            st.plotly_chart(fig_issue, use_container_width=True)
        else:
            st.info("No valid issue data available for the selected month.")

    # 📊 Dashboard Layout — Types of Issues per Tier | Tiers per Main Category

    st.divider()

    col1, col2 = st.columns([1, 1])

    # --------------------------
    # ▶️ COL 1: Types of Issues per Tier (horizontal grid)

    with col1:
        st.subheader("📊 Types of Issues per Tier")

        # Ensure filtered, non-empty rows
        issues_df = df_filtered[
            df_filtered["Matrix Description"].notna() &
            (df_filtered["Matrix Description"].str.strip() != "")
        ]

        if not issues_df.empty:
            # Group data
            issue_tier_matrix = (
                issues_df.groupby(["Matrix Description", "Tier"])["QTY"]
                .sum()
                .reset_index()
            )

            # Step 1: Compute total quantity per issue (to sort)
            issue_totals = (
                issue_tier_matrix.groupby("Matrix Description")["QTY"]
                .sum()
                .sort_values(ascending=False)
                .reset_index()
                .rename(columns={"Matrix Description": "Issue", "QTY": "TotalQty"})
            )

            # Step 2: Merge to original df
            issue_tier_matrix = issue_tier_matrix.merge(issue_totals, left_on="Matrix Description", right_on="Issue")

            # Step 3: Create shortened labels (for x-axis) + hover text
            issue_tier_matrix["Issue Label"] = issue_tier_matrix["Issue"].apply(
                lambda x: x if len(x) <= 25 else x[:25] + "..."
            )
            issue_tier_matrix["Hover"] = issue_tier_matrix["Issue"]

            # Step 5: Tier ordering
            issue_tier_matrix["Tier"] = pd.Categorical(
                issue_tier_matrix["Tier"],
                categories=["Tier 1", "Tier 2", "Tier 3", "Tier 4"],
                ordered=True
            )

            # Step 6: Sort x-axis by total quantity descending
            sorted_issues = (
                issue_tier_matrix.groupby("Issue Label")["QTY"]
                .sum()
                .sort_values(ascending=False)
                .index
                .tolist()
            )

            # Set Issue Label as ordered categorical using sorted order
            issue_tier_matrix["Issue Label"] = pd.Categorical(
                issue_tier_matrix["Issue Label"],
                categories=sorted_issues,
                ordered=True
            )

            # Step 7: Plot with correct order
            fig_bar = px.bar(
                issue_tier_matrix.sort_values(by=["Issue Label", "Tier"]),
                x="Issue Label",
                y="QTY",
                color="Tier",
                barmode="group",
                hover_name="Hover",
                labels={"QTY": "Units", "Issue Label": "Issue"},
            )

            fig_bar.update_layout(
                height=500,
                margin=dict(t=40, l=60, r=20, b=40),
                xaxis_title="Issue",
                yaxis_title="Units",
                xaxis_tickangle=45
            )

            st.plotly_chart(fig_bar, use_container_width=True)

    # --------------------------
    # ▶️ COL 2: Tiers per Main Category

    with col2:
        st.subheader("📊 Tiers per Main Category")

        # Define main categories and tier order
        main_categories = ["Desktop", "Laptop", "Monitor", "Mobile Phone"]
        tier_order = ["Tier 1", "Tier 2", "Tier 3", "Tier 4"]

        # Filter and group by Cleaned Type and Tier
        df_tiers = (
            df_filtered[df_filtered['Cleaned Type'].isin(main_categories)]
            .groupby(["Cleaned Type", "Tier"])['QTY']
            .sum()
            .reset_index()
        )

        # Pivot table
        tier_cat_pivot = df_tiers.pivot(index="Cleaned Type", columns="Tier", values="QTY").fillna(0)
        tier_cat_pivot = tier_cat_pivot.reindex(columns=tier_order, fill_value=0)

        # Build stacked bar chart
        fig_stack = go.Figure()

        # ➕ Add tier-wise bars with text labels
        for tier in tier_cat_pivot.columns:
            fig_stack.add_trace(go.Bar(
                name=tier,
                x=tier_cat_pivot.index,
                y=tier_cat_pivot[tier],
                text=[f"{int(val):,} units" if val > 0 else "" for val in tier_cat_pivot[tier]],
                textposition="inside",  # Can also try "outside" or "auto"
                hovertemplate=f"{tier}<br>%{{x}}: %{{y}} units<extra></extra>"
            ))

        # ➕ Add total units at top of each stack
        totals = tier_cat_pivot.sum(axis=1)
        fig_stack.add_trace(go.Scatter(
            x=tier_cat_pivot.index,
            y=totals,
            mode="text",
            text=[f"{int(val):,} units" for val in totals],
            textposition="top center",
            showlegend=False,
            hoverinfo="skip"
        ))

        # ✅ Layout
        fig_stack.update_layout(
            barmode="stack",
            height=500,
            margin=dict(t=30, b=40, l=60, r=20),
            xaxis_title="Main Category",
            yaxis_title="Total Units",
            legend_title="Tier"
        )

        # Display the chart
        st.plotly_chart(fig_stack, use_container_width=True)


    # --- Full Table ---
    st.subheader("📋 Inbounds Table")
    st.dataframe(df_filtered, use_container_width=True)
   

# OUTBOUNDS CONNECTION --------------------------------------------------------------------------------------------------------------------------------------------

@st.cache_data(ttl=60)
def get_outbounds_dashboard_data(sheet_index=1):
    credentials_path = "outbounds-dashboard-b4e9901c3361.json"
    scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    credentials = Credentials.from_service_account_file(credentials_path, scopes=scopes)
    gc = gspread.authorize(credentials)

    spreadsheet_id = "1Md7tsA-oFNrqGbcbSFkOiWprUFh6hZKxTuP0edarfTU"
    sh = gc.open_by_key(spreadsheet_id)
    worksheet = sh.get_worksheet(sheet_index)
    data = worksheet.get_all_values()

    if not data:
        return pd.DataFrame()

    headers = data[0]
    df_data = data[1:]

    df = pd.DataFrame(df_data, columns=headers)
    df = df.dropna(how="all", axis=0)
    df = df.dropna(how="all", axis=1)

    return df

# -----------------------------------------------
# 2. Preprocess Data
# -----------------------------------------------
def preprocess_outbound_data(df):
    if "Price" in df.columns:
        df["Price"] = df["Price"].str.replace("\u20b1", "", regex=False).str.replace(",", "", regex=False).replace("", "0").astype(float)

    if "QTY" in df.columns:
        df["QTY"] = pd.to_numeric(df["QTY"], errors='coerce').fillna(0).astype(int)

    if "Weight" in df.columns:
        df["Weight"] = pd.to_numeric(df["Weight"], errors='coerce').fillna(0).astype(float)

    if "Pullout Date" in df.columns:
        df["Pullout Date"] = pd.to_datetime(df["Pullout Date"], errors='coerce')
        df["Month_Year"] = df["Pullout Date"].dt.strftime('%b %Y')

    df["Total Value"] = df["QTY"] * df["Price"]

    return df.reset_index(drop=True)

# -----------------------------------------------
# 3. Extract Main Category from Description
# -----------------------------------------------
keywords = [
    "Desktop", "Headset", "Keyboard", "Laptop", "Monitor", "Mouse",
    "Mobile Phone", "Telephone", "Tablet", "Server", "UPS", "Cable",
    "Printer", "Switch", "Office Supplies", "Others", "Hard Disk",
    "Speaker", "Camera", "Powerbank", "Microphone", "TV", "Battery"
]

def extract_main_category(description):
    if pd.isna(description):
        return "Others"
    description = description.lower()
    for keyword in keywords:
        if keyword.lower() in description:
            return keyword
    return "Others"

def render_outbound_delta(delta):
    if delta is None:
        return ""

    symbol = "↑" if delta > 0 else ("↓" if delta < 0 else "→")
    color = "green" if delta > 0 else ("red" if delta < 0 else "gray")

    return f"""<span style='color:{color}; font-weight:600; font-size:11px; margin-top: 10px;'>
        {symbol} {abs(delta):.2f}% <i>vs last month</i>
    </span>"""

def wrap_label(text, width=15):
    return '<br>'.join([text[i:i+width] for i in range(0, len(text), width)])

def wrap_label(label, width=15):
    return "<br>".join([label[i:i+width] for i in range(0, len(label), width)])

# Outbounds Dashboard ----------------------------------------------------------------------------------------------

if page == "Outbounds Dashboard":

    st.title("Outbounds Dashboard")

    # 🔗 Sheet link expander
    with st.expander("🔗 View Spreadsheet Link", expanded=False):
        st.markdown(""" 
        [All Pullout Transmittals](https://docs.google.com/spreadsheets/d/1Md7tsA-oFNrqGbcbSFkOiWprUFh6hZKxTuP0edarfTU/edit?gid=1080537819)
        """, unsafe_allow_html=True)

    # Load and preprocess data
    df_raw = get_outbounds_dashboard_data()
    df = preprocess_outbound_data(df_raw)
    df["Main Category"] = df["Description"].apply(extract_main_category)

    # 📅 Month filter
    months = sorted(df["Month_Year"].dropna().unique().tolist(), key=lambda x: pd.to_datetime(x, format='%b %Y'))
    selected_month = st.selectbox("📅 Filter by Month of Outbound", options=["All"] + months, index=0, key="month_filters_dropdown")

    # Apply filter
    filtered_df = df.copy()
    if selected_month != "All":
        filtered_df = filtered_df[filtered_df["Month_Year"] == selected_month]

    # Metric values
    total_qty = filtered_df["QTY"].sum()
    total_value = filtered_df["Total Value"].sum()
    unique_customers = filtered_df["Customer Name"].nunique()

    # Delta logic
    def pct_change(curr, prev):
        if prev == 0:
            return None
        return ((curr - prev) / prev) * 100

    if selected_month != "All":
        current_month = pd.to_datetime(selected_month, format='%b %Y')
        prev_month_str = (current_month - pd.DateOffset(months=1)).strftime('%b %Y')

        df_prev = df[df["Month_Year"] == prev_month_str]

        prev_total_qty = df_prev["QTY"].sum() if not df_prev.empty else 0
        prev_total_value = df_prev["Total Value"].sum() if not df_prev.empty else 0
        prev_unique_customers = df_prev["Customer Name"].nunique() if not df_prev.empty else 0

        qty_delta = pct_change(total_qty, prev_total_qty)
        value_delta = pct_change(total_value, prev_total_value)
        customers_delta = pct_change(unique_customers, prev_unique_customers)
    else:
        qty_delta = value_delta = customers_delta = None

    # Top Customers
    top_customers_qty = filtered_df.groupby("Customer Name")["QTY"].sum().sort_values(ascending=False).head(5).reset_index()
    top_customers_value = filtered_df.groupby("Customer Name")["Total Value"].sum().sort_values(ascending=False).head(5).reset_index()

    # Top Months
    top_months = df.groupby("Month_Year")["QTY"].sum().sort_values(ascending=False).head(3).reset_index()

    # Hover card styling
    card_style = """
    <style>
        .hover-card {
            background: linear-gradient(90deg, #ffffff, #d2e1f3);
            border-radius: 20px;
            padding: 1.6rem 0.5rem 2rem 0.5rem;
            box-shadow: 0 4px 10px rgba(0,0,0,0.05);
            display: flex;
            line-height: 0.9;
            flex-direction: column;
            justify-content: flex-start;
            text-align: left;
            font-size: 28px;
            font-weight: 650;
            transition: transform 0.2s ease, box-shadow 0.2s ease;
            margin: auto;
            max-height: 155px;     
            min-width: 210px;     
        }
        .hover-card:hover {
            transform: translateY(-6px);
            box-shadow: 0 8px 20px rgba(0,0,0,0.12);
        }
        .hover-card h4 {
            margin: 0 0 12px 0;
            font-size: 15px;
            margin-bottom: -12px;
            margin-top: -10px;
        }
        .hover-card p {
            margin: 4px 0;
            font-size: 12px;
        }
        .metric-number {
            font-size: 35px;
            font-weight: 650;
            color: #4c2882;
            margin-top: 15px;
            line-height: 0.9;
            text-align: left;
            height: auto;
        }
        .metric-delta {
            font-size: 12px;
            margin-top: -10px;
        }
        .month-value {
            font-size: 20px;
            font-weight: 650;
            margin: 0px 0;
            margin-bottom: -30px;
            margin-top: 50px;
            color: #6756BE;
        }
        .month-value-row {
            display: flex;
            justify-content: space-between;
            gap: 5px;
            font-size: 13px;
            margin-top: 30px;
            margin: 2px 0;
            line-height: 1;
            flex-wrap: wrap;
            word-break: break-word;
        }
        .month-left {
            font-weight: 600;
        }
        .month-right {
            font-weight: 650;
            color: #e25858;
        }
    </style>
    """
    st.markdown(card_style, unsafe_allow_html=True)

    # 📊 Metric Cards
    spacer1, col1, col2, col3, col4, spacer2 = st.columns([0.2, 1.1, 1.32, 1.1, 1, 0.2])

    with col1:
        st.markdown(f"""
        <div class='hover-card'>
            <img src="https://cdn-icons-png.flaticon.com/128/3624/3624117.png" width="30" style="margin-bottom: 5px;" />
            <h4>Outbound Quantity</h4>
            <div class='metric-number'>{int(total_qty):,}</div>
            {render_outbound_delta(qty_delta)}
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class='hover-card'>
            <img src="https://cdn-icons-png.flaticon.com/128/1611/1611179.png" width="30" style="margin-bottom: 5px;" />
            <h4>Outbound Value</h4>
            <div class='metric-number'>₱{total_value:,.0f}</div>
            {render_outbound_delta(value_delta)}
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
        <div class='hover-card'>
            <img src="https://cdn-icons-png.flaticon.com/128/3126/3126647.png" width="30" style="margin-bottom: 5px;" />
            <h4>No. of Customers</h4>
            <div class='metric-number'>{unique_customers}</div>
            {render_outbound_delta(customers_delta)}
        </div>
        """, unsafe_allow_html=True)

    with col4:
        top_months_html = """
        <div class='hover-card'>
            <img src="https://cdn-icons-png.flaticon.com/128/16877/16877580.png" width="30" style="margin-bottom: 5px;" />
            <h4>Top Outbound Months</h4>
        """
        for _, row in top_months.iterrows():
            top_months_html += f"""<div class='month-value-row'>
                <span class='month-left'>{row['Month_Year']}</span>
                <span class='month-right'>{int(row['QTY']):,} units</span>
            </div>"""
        top_months_html += "</div>"

        st.markdown(top_months_html, unsafe_allow_html=True)

    st.markdown("<hr style='border: 0.5px solid white; margin: 10px 0;'>", unsafe_allow_html=True)

    # --- Row 2: Expandable Dataframes Section
    row2_col1, row2_col2, row2_col3 = st.columns([1, 1, 1])

    with row2_col1:
        with st.container():
            with st.expander("Outbound SKU, Quantity, and Price", expanded=False):
                try:
                    sku_qty_df = filtered_df[["SKU", "QTY", "Total Value"]].copy()
                    sku_qty_df = sku_qty_df.rename(columns={
                        "SKU": "SKU",
                        "QTY": "Quantity",
                        "Total Value": "Price (₱)"
                    })
                    st.data_editor(
                        sku_qty_df,
                        hide_index=True,
                        use_container_width=True
                    )
                except Exception as e:
                    st.error(f"Error loading SKU table: {e}")

    with row2_col2:
        with st.container():
            with st.expander("Top 5 Customers by Value", expanded=False):
                try:
                    top5_customers = (
                        filtered_df
                        .groupby("Customer Name")[["Total Value"]]
                        .sum()
                        .sort_values(by="Total Value", ascending=False)
                        .head(5)
                        .reset_index()
                    )
                    top5_customers = top5_customers.rename(columns={
                        "Customer Name": "Customer",
                        "Total Value": "Outbound Value",
                    })

                    # Optional: format as currency
                    top5_customers["Outbound Value"] = top5_customers["Outbound Value"].apply(lambda x: f"₱{x:,.2f}")

                    st.data_editor(
                        top5_customers,
                        hide_index=True,
                        use_container_width=True
                    )
                except Exception as e:
                    st.error(f"Error loading customers table: {e}")

    with row2_col3:
        with st.container():
            with st.expander("Top 5 Customers by Profit Margin", expanded=False):
                try:
                    # Ensure profit margin is numeric and cleaned
                    filtered_df["Profit Margin"] = pd.to_numeric(
                        filtered_df["Profit Margin"]
                        .astype(str)
                        .str.replace("%", "", regex=False),
                        errors="coerce"
                    )

                    # Group and get top 5 by average profit margin
                    top5_margin = (
                        filtered_df
                        .groupby("Customer Name")["Profit Margin"]
                        .mean()
                        .sort_values(ascending=False)
                        .head(5)
                        .reset_index()
                    )

                    # Format
                    top5_margin = top5_margin.rename(columns={
                        "Customer Name": "Customer",
                        "Profit Margin": "Avg Profit Margin (%)"
                    })
                    top5_margin["Avg Profit Margin (%)"] = top5_margin["Avg Profit Margin (%)"].apply(
                        lambda x: f"{x:.2f}%"
                    )

                    st.data_editor(
                        top5_margin,
                        hide_index=True,
                        use_container_width=True
                    )

                except Exception as e:
                    st.error(f"Error loading profit margin table: {e}")

    st.divider()


    # 📊 Charts Layout: 2 Columns x 2 Rows + 1 Full
    col_left1, col_right1 = st.columns(2)

    with col_left1:
        st.subheader("📊 Sold per Main Category")
        if not filtered_df.empty:
            main_category_summary = (
                filtered_df.groupby("Main Category")["QTY"]
                .sum().reset_index()
                .sort_values("QTY", ascending=False)
            )

            fig_main_cat = px.bar(
                main_category_summary,
                x="QTY",
                y="Main Category",
                orientation="h",
                text=[f"{qty:,.0f} units" for qty in main_category_summary["QTY"]]
            )

            fig_main_cat.update_traces(
                textposition='outside',
                textfont=dict(color='black')
            )

            fig_main_cat.update_layout(
                xaxis_title="Quantity",
                yaxis_title="Main Category",
                margin=dict(l=80, r=30, t=30, b=30)
            )

            fig_main_cat.update_yaxes(autorange="reversed")  # Highest on top
            st.plotly_chart(fig_main_cat, use_container_width=True)
        else:
            st.info("No data available.")

    with col_right1:
        st.subheader("🏭 Supplier with Most Units Sold")
        if not filtered_df.empty:
            supplier_summary = (
                filtered_df.groupby("Supplier Name")["QTY"]
                .sum().reset_index()
                .sort_values("QTY", ascending=False)
            )

            fig_supplier = px.bar(
                supplier_summary,
                x="QTY",
                y="Supplier Name",
                orientation="h",
                text=[f"{qty:,.0f} units" for qty in supplier_summary["QTY"]]
            )

            fig_supplier.update_traces(
                textposition='outside',
                textfont=dict(color='black')
            )

            fig_supplier.update_layout(
                xaxis_title="Quantity",
                yaxis_title="Supplier Name",
                margin=dict(l=100, r=30, t=30, b=30)
            )

            fig_supplier.update_yaxes(autorange="reversed")  # Highest on top
            st.plotly_chart(fig_supplier, use_container_width=True)
        else:
            st.info("No data available.")

    st.divider()

    col_left2, col_right2 = st.columns(2)

    with col_left2:
        st.subheader("💸 Top Customers by Value and Profit Margin")
        if not filtered_df.empty:
            # Ensure numeric Profit Margin
            # Convert to numeric (handles % strings or NaNs safely)
            filtered_df["Profit Margin"] = pd.to_numeric(
                filtered_df["Profit Margin"].astype(str).str.replace('%', '', regex=False),
                errors="coerce"
            ) 

            # Group and aggregate
            top_customers_value = (
                filtered_df.groupby("Customer Name")
                .agg({"Total Value": "sum", "Profit Margin": "mean"})
                .sort_values(by="Total Value", ascending=False)
                .head(5)
                .reset_index()
            )

            # Wrapping and formatting
            top_customers_value["Customer Wrapped"] = top_customers_value["Customer Name"].apply(wrap_label)
            top_customers_value["Value Label"] = top_customers_value["Total Value"].apply(lambda x: f"₱{int(round(x)):,}")
            top_customers_value["Profit Margin %"] = top_customers_value["Profit Margin"]

            fig = go.Figure()

            # Bar for Total Value
            fig.add_bar(
                x=top_customers_value["Customer Wrapped"],
                y=top_customers_value["Total Value"],
                name="Total Value (₱)",
                marker=dict(color="#4B0082"),
                text=top_customers_value["Value Label"],
                textposition="outside"
            )

            # Line for Profit Margin
            fig.add_scatter(
                x=top_customers_value["Customer Wrapped"],
                y=top_customers_value["Profit Margin %"],
                name="Profit Margin (%)",
                mode="lines+markers",
                line=dict(color="skyblue", width=3, dash="dot"),
                marker=dict(size=8),
                yaxis="y2"
            )

            fig.update_layout(
                xaxis=dict(title="Customer"),
                yaxis=dict(
                    title="Total Value (₱)",
                    tickformat=",",
                    showgrid=True
                ),
                yaxis2=dict(
                    title="Profit Margin (%)",
                    overlaying="y",
                    side="right",
                    tickformat=".0f",
                    range=[0, max(50, top_customers_value["Profit Margin %"].max() * 1.1)],
                    showgrid=False
                ),
                legend=dict(orientation="h", y=1.15, x=1, xanchor="right"),
                margin=dict(l=40, r=60, t=60, b=80)
            )

            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No data available.")

    with col_right2:
        st.subheader("📋 Top Customers by Quantity")
        if not filtered_df.empty:
            top_customers_qty["Qty Label"] = top_customers_qty["QTY"].apply(lambda x: f"{int(x):,} units")
            top_customers_qty["Customer Wrapped"] = top_customers_qty["Customer Name"].apply(lambda x: wrap_label(x))

            fig_top_qty = px.bar(
                top_customers_qty,
                x="QTY",
                y="Customer Wrapped",
                orientation="h",
                text="Qty Label"
            )

            fig_top_qty.update_traces(
                textposition='outside',
                textfont=dict(size=12),
                marker=dict(color="#1f77b4")
            )

            fig_top_qty.update_layout(
                xaxis_title="Quantity",
                yaxis_title="Customer",
                yaxis=dict(autorange="reversed"),
                bargap=0.25,
                margin=dict(l=140, r=40, t=30, b=30)
            )

            st.plotly_chart(fig_top_qty, use_container_width=True)
        else:
            st.info("No data available.")

    st.divider()

    # --- Full Table ---
    st.subheader("📋 Outbounds Table")
    st.dataframe(filtered_df, use_container_width=True)

 # --- Humble Bot Connection ---------------------------------------------------------------

# GSheets Setup
@st.cache_data(ttl=300)
def load_faq_from_gsheets():
    credentials_path = "humblesustainability-systems-2517c09a5a25.json"
    if not os.path.exists(credentials_path):
        raise FileNotFoundError(f"Credentials file not found at: {credentials_path}.")

    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]
    credentials = Credentials.from_service_account_file(credentials_path, scopes=scopes)
    gc = gspread.authorize(credentials)
    sheet = gc.open_by_url("https://docs.google.com/spreadsheets/d/1RJIE5Ryt1J3xT7YKnBA2rvh6CYoDbGh0HGVWEtenvTE/edit").sheet1
    data = sheet.get_all_records()
    faq_df = pd.DataFrame(data)
    return faq_df

# Humble Bot --------------------------------------------------

if page == "Humble Bot":
    gemini_key = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=gemini_key)
    model = genai.GenerativeModel("models/gemini-1.5-pro-latest")

    # ---------------------- CUSTOM STYLES ----------------------
    st.markdown("""
    <style>
    .chat-container {
        display: flex;
        flex-direction: column;
        max-width: 300px;
        margin: auto;
    }
    .user-msg, .bot-msg {
        padding: 10px 15px;
        border-radius: 18px;
        margin: 6px 0;
        font-size: 15px;
        max-width: 75%;
        word-wrap: break-word;
        animation: fadeIn 0.3s ease-in-out;
    }
    .user-msg {
        background-color: #814bf5;
        color: white;
        align-self: flex-end;
        border-bottom-right-radius: 2px;
    }
    .bot-msg {
        background-color: #f0f0f0;
        color: #333;
        align-self: flex-start;
        border-bottom-left-radius: 2px;
    }
    button[kind="secondary"] {
        border-radius: 999px !important;
        border: 1px solid #000 !important;
        background-color: white !important;
        color: black !important;
        font-size: 5px !important;  /* smaller font */
        font-weight: 500 !important;
        padding: 0.2rem 0.8rem !important;  /* tighter spacing */
        white-space: nowrap !important;
        margin: 3px 4px !important;
        line-height: 1.2 !important;
    }
    .header-box {
        background: linear-gradient(135deg, #6a11cb, #2575fc);
        padding: 14px 20px;
        border-radius: 14px;
        margin-bottom: 24px;
        box-shadow: 0 3px 6px rgba(0,0,0,0.1);
        transition: transform 0.3s, box-shadow 0.3s;
    }
    .header-box:hover {
        transform: translateY(-6px);
        box-shadow: 0 8px 20px rgba(0,0,0,0.12);
    }
    </style>
    """, unsafe_allow_html=True)

    # ---------------------- HEADER ----------------------
    st.markdown("""
    <div class="header-box">
        <div style="display: flex; align-items: center;">
            <img src="https://cdn-icons-png.flaticon.com/128/17115/17115982.png" width="65" style="margin-right: 10px;" />
            <div>
                <h4 style="margin: 0; color: #fff;">Humble Bot</h4>
                <p style="margin: -10; font-size: 15px; color: #f4f4f4;">Your all-in-one assistant for Humble Sustainability.</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ---------------------- FAQ FUNCTIONALITY ----------------------
    try:
        faq_df = load_faq_from_gsheets()

        # Drop only if Question or Answer is missing or empty
        faq_df = faq_df.dropna(subset=['Question', 'Answer'])
        faq_df = faq_df[
            (faq_df['Question'].str.strip() != "") &
            (faq_df['Answer'].str.strip() != "")
        ]

        category_list = sorted([
            cat for cat in faq_df['Category'].unique().tolist()
            if cat and str(cat).strip() != ""
        ])
        
        # Session state setup
        if "selected_category" not in st.session_state:
            st.session_state.selected_category = None
        if "selected_question" not in st.session_state:
            st.session_state.selected_question = None

        st.markdown("**Select a FAQ Category:**")
        cat_cols = st.columns(len(category_list))
        for i, cat in enumerate(category_list):
            with cat_cols[i]:
                if st.button(cat):
                    st.session_state.selected_category = cat
                    st.session_state.selected_question = None

        # Show questions
        if st.session_state.selected_category:
            filtered_df = faq_df[faq_df['Category'] == st.session_state.selected_category]
            st.markdown(f"**Questions under {st.session_state.selected_category}:**")
            st.markdown("<div class='scroll-box'>", unsafe_allow_html=True)
            q_cols = st.columns(2)
            for i, q in enumerate(filtered_df['Question'].tolist()):
                with q_cols[i % 2]:
                    if st.button(q):
                        st.session_state.selected_question = q
            st.markdown("</div>", unsafe_allow_html=True)

        # Show answer
        if st.session_state.selected_question:
            answer = filtered_df.loc[filtered_df['Question'] == st.session_state.selected_question, 'Answer'].values[0]
            st.markdown(f"""
            <div class="chat-container">
                <div class="bot-msg">{answer}</div>
            </div>
            """, unsafe_allow_html=True)

        # Custom input
        custom_input = st.chat_input("Ask a question...")
        if custom_input:
            st.markdown(f"""
            <div class="chat-container">
                <div class="user-msg">{custom_input}</div>
            </div>
            """, unsafe_allow_html=True)

            match = faq_df[faq_df['Question'].str.lower().str.strip() == custom_input.lower().strip()]
            if not match.empty:
                response_text = match.iloc[0]['Answer']
            else:
                context = "\n\n".join([f"Q: {q}\nA: {a}" for q, a in faq_df[['Question','Answer']].values])
                prompt = f"You are Humble Bot, the official assistant for Humble Sustainability. Use only the trusted internal knowledge below when responding.\n\n{context}\n\nQ: {custom_input}\nA:"
                with st.spinner("Thinking..."):
                    try:
                        response = model.generate_content(prompt)
                        response_text = response.text.strip()
                        if len(response_text) < 10:
                            response_text = "I'm not sure yet. You may contact the Humble team for support."
                    except Exception as e:
                        response_text = f"❌ Error: {e}"

            st.markdown(f"""
            <div class="chat-container">
                <div class="bot-msg">{response_text}</div>
            </div>
            """, unsafe_allow_html=True)

    except Exception as e:
        st.error(f"Failed to load FAQs from Google Sheets: {e}")
        
# --- OMS Guide Tab (with Sidebar Theme and Section Toggle) -----------------------------------------------------------------------------
if page == "System Guide":
    st.markdown("""
    <style>
        .guide-section {
            background-color: #f6f3fc;
            padding: 1.5rem;
            border-radius: 14px;
            margin-bottom: 1rem;
            box-shadow: 0 1px 5px rgba(0, 0, 0, 0.04);
        }
        .guide-title {
            font-size: 32px;
            font-weight: 800;
            margin-bottom: 15px;
            color: #3c175f;
        }
        .guide-body {
            font-size: 17px;
            line-height: 1.7;
            color: #222;
        }
        ul li, ol li {
            margin-bottom: 0.5rem;
        }
    </style>
    """, unsafe_allow_html=True)

    st.markdown("""
    <style>
    /* Existing styles */
    .guide-section {
        background-color: white;
        padding: 1.5rem;
        border-radius: 14px;
        margin-bottom: 1rem;
        box-shadow: 0 1px 5px rgba(0, 0, 0, 0.04);
        transition: all 0.2s ease-in-out;
    }
    .guide-section:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.12);
        background-color: #f9f9ff;
    }
    ul li, ol li {
        margin-bottom: 0.2rem;
    }

    /* Gradient Header Card */
    .oms-header-card {
        background: linear-gradient(90deg, #5f3dc4, #4c6ef5);
        color: white;
        padding: 1.5rem 2rem;
        border-radius: 18px;
        margin-bottom: 2.5rem;
        box-shadow: 0px 4px 10px rgba(0,0,0,0.12);
        display: flex;
        align-items: center;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    .oms-header-card:hover {
        transform: translateY(-2px);
        box-shadow: 0px 8px 20px rgba(0, 0, 0, 0.2);
    }
    .oms-header-icon {
        width: 50px;
        height: 50px;
        margin-right: 1.5rem;
    }
    .oms-header-text {
        display: flex;
        flex-direction: column;
    }
    .oms-header-title {
        font-size: 26px;
        font-weight: 800;
        margin-bottom: 4px;
    }
    .oms-header-subtitle {
        font-size: 16px;
        font-weight: 400;
        opacity: 0.95;
    }
    </style>

    <div class='oms-header-card'>
        <img class='oms-header-icon' src='https://cdn-icons-png.flaticon.com/128/7887/7887082.png' alt='OMS Icon'>
        <div class='oms-header-text'>
            <div class='oms-header-title'>OMS System Guide</div>
            <div class='oms-header-subtitle'>
                Welcome to Humble Sustainability’s Operations Management System!<br>
                This guide walks you through each core module—designed to enhance warehouse scalability, streamline operations, and enable data-driven efficiency.
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    with st.expander("📊 Control Tower"):
        st.markdown("""
        <div class='guide-section'>
            <div class='guide-body'>
                <p><b>Overview:</b> Central hub for supplier onboarding, activation tracking, and client progress.</p>
                <p><b>Purpose:</b></p>
                <ul>
                    <li>Standardize supplier workflows</li>
                    <li>Track PIF completion & deals in real time</li>
                    <li>Enhance onboarding throughput</li>
                </ul>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("### Supplier Progress Tracker", unsafe_allow_html=True)
        st.markdown("""
        <div class='guide-section'>
            <div class='guide-body'>
                <p><b>Steps:</b></p>
                <ol>
                    <li>Select a supply client</li>
                    <li>Monitor: Deal Status, Endorsement Date, Account Type, PIF Status</li>
                    <li>Use Month Filter for specific periods</li>
                    <li>Check: Activation Metrics, Account Breakdown</li>
                </ol>
                <p><b>Impact:</b> Solves prior onboarding delays and improves scalability.</p>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("### Account Masterlist", unsafe_allow_html=True)
        st.markdown("""
        <div class='guide-section'>
            <div class='guide-body'>
                <p><b>Steps:</b></p>
                <ol>
                    <li>Browse onboarded supply clients</li>
                    <li>Check PIF Status (✔️/❌), Revenue, Inbound/Outbound Volumes</li>
                    <li>Use badges:</li>
                </ol>
                <ul>
                    <li>🟥 Red = Low Revenue</li>
                    <li>🟩 Green = High Revenue</li>
                </ul>
                <p><b>Impact:</b> Enables strategic prioritization and better resource allocation.</p>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("### Prospects", unsafe_allow_html=True)
        st.markdown("""
        <div class='guide-section'>
            <div class='guide-body'>
                <p><b>Steps:</b></p>
                <ul>
                    <li>View Oculars, QCs, Pickup Schedules</li>
                    <li>Filter by Week/Month</li>
                    <li>Click Google Calendar links to sync</li>
                </ul>
                <p><b>Impact:</b> Prevents scheduling overlaps and improves warehouse prep.</p>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with st.expander("📥 Inbounds Dashboard"):
        st.markdown("""
        <div class='guide-section'>
            <div class='guide-body'>
                <p><b>Steps:</b></p>
                <ol>
                    <li>Select Month to analyze inbound data</li>
                    <li>Check: Total Quantity, Unique Clients, MoM Growth</li>
                    <li>Use Donut Chart for Tier %</li>
                    <li>Inspect Tier Movement & Issue Matrix</li>
                    <li>Scroll to view Raw Records</li>
                </ol>
                <p><b>Impact:</b> Fixes manual validation gaps and improves stock accuracy.</p>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with st.expander("📤 Outbounds Dashboard"):
        st.markdown("""
        <div class='guide-section'>
            <div class='guide-body'>
                <p><b>Steps:</b></p>
                <ol>
                    <li>Filter by Month</li>
                    <li>Review: Quantity, Value, Client Served</li>
                    <li>Charts:</li>
                </ol>
                <ul>
                    <li>Monthly Trends</li>
                    <li>Supplier Contributions</li>
                    <li>Customer-Item Bubbles</li>
                </ul>
                <ol start="4">
                    <li>Export via Full Outbound Records Table</li>
                </ol>
                <p><b>Impact:</b> Enhances demand response, reduces mismatches, and boosts satisfaction.</p>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with st.expander("📦 Inventory Dashboard"):
        st.markdown("""
        <div class='guide-section'>
            <div class='guide-body'>
                <p><b>Steps:</b></p>
                <ol>
                    <li>Choose a client or all-inventory view</li>
                    <li>Check: On-Hand, Items Sold, Avg Sales Cycle</li>
                    <li>See: Category, Tier Breakdown, Monthly Trends</li>
                    <li>Explore SKU-level records for deep dive</li>
                </ol>
                <p><b>Impact:</b> Prevents overstock, reduces waste, and supports circular economy.</p>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with st.expander("🤖 Humble Bot"):
        st.markdown("""
        <div class='guide-section'>
            <div class='guide-body'>
                <p><b>Steps:</b></p>
                <ol>
                    <li>Choose a category or type your question</li>
                    <li>Matched ➔ Instant FAQ-based response</li>
                    <li>Not matched ➔ Gemini fallback with answer</li>
                </ol>
                <p><b>Impact:</b> Replaces repetitive team inquiries and accelerates task guidance.</p>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with st.expander("OMS Troubleshooting"):
        st.markdown("""
        <div class='guide-section'>
            <div class='guide-body'>
                <p><b>Steps:</b></p>
                <ol>
                    <li>  </li>
                    <li>  </li>
                    <li>  </li>
                </ol>
                <p><b>  </p>
            </div>
        </div>
        """, unsafe_allow_html=True)


# CONTACT US ----------------------------------------------------------------------------------------------------------------------------

if page == "Contact Us":
    st.markdown("""
        <style>
            html, body, [data-testid="stAppViewContainer"] {
                overflow: hidden !important;
                height: 100vh !important;
            }
        </style>
    """, unsafe_allow_html=True)

    # Layout: Info left, Form right
    col_left, col_right = st.columns([1.5, 1])

    # Header and Author Info
    with col_left:
        st.markdown("""
            <h6 style='color:#5A4FCF;'>Contact Us</h6>
            <h1 style='margin-top: -10px;'>Get In Touch With Us</h1>
            <p style='max-width: 750px; color: #3D2E90; font-size: 20px; font-weight: 650'>Humble Sustainability Operations Management System</p>
            <h4 style='margin-top: 0px;'>Authors</h4>
        """, unsafe_allow_html=True)

        # Audrey
        st.markdown("""
            <div style='display: flex; align-items: center; margin-bottom: 8px;'>
                <img src="https://cdn-icons-png.flaticon.com/128/13435/13435928.png" width="20"/>
                <div style='margin-left: 10px; font-size: 14px; font-weight: 500;'><b>Audrey Marie C. Olona</b><br><span style='color:#777;'>Supply Chain Intern</span></div>
            </div>
            <div style='display: flex; align-items: center; margin-bottom: 3px;'>
                <img src="https://cdn-icons-png.flaticon.com/128/9171/9171491.png" width="20"/>
                <span style='margin-left: 10px; font-size: 13px;'>(+63) 981 258 0954</span>
            </div>
            <div style='display: flex; align-items: center; margin-bottom: 3px;'>
                <img src="https://cdn-icons-png.flaticon.com/128/18384/18384266.png" width="20"/>
                <span style='margin-left: 10px; font-size: 13px;'>olonaaudreyy@gmail.com</span>
            </div>
            <div style='display: flex; align-items: center; margin-bottom: 3px;'>
                <img src="https://cdn-icons-png.flaticon.com/128/4319/4319160.png" width="20"/>
                <span style='margin-left: 10px; font-size: 13px;'>Pamantasan ng Lungsod ng Maynila</span>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<div style='height: 30px;'></div>", unsafe_allow_html=True)

        # Charles
        st.markdown("""
        <div style='display: flex; align-items: center; margin-bottom: 8px;'>
            <img src="https://cdn-icons-png.flaticon.com/128/13435/13435928.png" width="20"/>
            <div style='margin-left: 10px; font-size: 14px; font-weight: 500;'><b>Charles Daniel U. Dy</b><br><span style='color:#777;'>Warehouse Intern</span></div>
        </div>
        <div style='display: flex; align-items: center; margin-bottom: 3px;'>
            <img src="https://cdn-icons-png.flaticon.com/128/9171/9171491.png" width="20"/>
            <span style='margin-left: 10px; font-size: 13px;'>(+63) 949 949 1245</span>
        </div>
        <div style='display: flex; align-items: center; margin-bottom: 3px;'>
            <img src="https://cdn-icons-png.flaticon.com/128/18384/18384266.png" width="20"/>
            <span style='margin-left: 10px; font-size: 13px;'>dycharlesdaniel@gmail.com</span>
        </div>
        <div style='display: flex; align-items: center; margin-bottom: 3px;'>
            <img src="https://cdn-icons-png.flaticon.com/128/4319/4319160.png" width="20"/>
            <span style='margin-left: 10px; font-size: 13px;'>Pamantasan ng Lungsod ng Maynila</span>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<div style='height: 30px;'></div>", unsafe_allow_html=True)

        # Darryl
        st.markdown("""
        <div style='display: flex; align-items: center; margin-bottom: 8px;'>
            <img src="https://cdn-icons-png.flaticon.com/128/13435/13435928.png" width="20"/>
            <div style='margin-left: 10px; font-size: 14px; font-weight: 500;'><b>Darryl Sarmiento</b><br><span style='color:#777;'>Head of Excellence and Strategy</span></div>
        </div>
        <div style='display: flex; align-items: center; margin-bottom: 3px;'>
            <img src="https://cdn-icons-png.flaticon.com/128/9171/9171491.png" width="20"/>
            <span style='margin-left: 10px; font-size: 13px;'>(+63) 987 654 3210</span>
        </div>
        <div style='display: flex; align-items: center; margin-bottom: 3px;'>
            <img src="https://cdn-icons-png.flaticon.com/128/18384/18384266.png" width="20"/>
            <span style='margin-left: 10px; font-size: 13px;'>darryl@humblesustainability.com</span>
        </div>
        """, unsafe_allow_html=True)

    # Right Column - Submit a Bug
    with col_right:
        st.markdown("""
        <div style='background-color:#3D2E90; padding: 15px; border-radius: 15px; margin-top: 30px;'>
            <h4 style='color:white;'>Submit a Bug</h4>
        """, unsafe_allow_html=True)

        with st.form("bug_form", clear_on_submit=True):  # <-- clears automatically
            name = st.text_input("Your Name", key="bug_name")
            email = st.text_input("Your Email", key="bug_email")
            page = st.text_input("Page (optional)", key="bug_page")
            description = st.text_area("Bug Description", key="bug_description")
            submitted = st.form_submit_button("Submit Bug")

        st.markdown("</div>", unsafe_allow_html=True)

        if submitted:
            st.success("Thank you! Your bug report has been submitted!")

            credentials_path = "oms-bug-responses-59ca4ab5fd4f.json"
            scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
            credentials = Credentials.from_service_account_file(credentials_path, scopes=scopes)
            gc = gspread.authorize(credentials)

            spreadsheet_id = "1qss1KO4ii2spKbW2BCVvht8xzxTf9Br6ugofABDCP-M"
            sh = gc.open_by_key(spreadsheet_id)
            worksheet = sh.worksheet("Form Responses")

            from datetime import datetime  # Make sure this is imported correctly
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            worksheet.append_row([
                timestamp,
                st.session_state["bug_name"],
                st.session_state["bug_email"],
                st.session_state["bug_page"],
                st.session_state["bug_description"]
            ])

# --- LOGOUT FUNCTION ------------------------------------------------

if page == "Logout":
    st.session_state.logged_in = False
    st.success("You have been logged out.")
    st.rerun()

# --- LOGIN LOGIC ----------------------------------------------------

if not st.session_state.logged_in:
    st.markdown("""
        <style>
            /* Center the block & limit its width */
            .block-container {
                max-width: 450px;
                margin: auto;
                padding-top: 100px;
            }
            .login-title {
                font-size: 40px;
                font-weight: 750;
                margin-bottom: 8px;
                text-align: center;
            }
            .login-subtitle {
                color: gray;
                font-size: 15px;
                margin-bottom: 20px;
                text-align: center;
            }
            .stTextInput input {
                font-size: 13px;
            }
            .stButton > button {
                width: 100%;
                border-radius: 20px;
                background-color: #1C0033;
                color: white;
                padding: 8px 16px;
                font-weight: bold;
                font-size: 14px;
                border: none;
                outline: none;
                transition: background-color 0.3s ease;
            }
            .stButton > button:hover {
                background-color: #333333;
                cursor: pointer;
            }
            .stButton > button:focus {
                outline: none;
                box-shadow: none;
            }
            </style>
    """, unsafe_allow_html=True)

    st.markdown('<div class="login-title">Welcome back!</div>', unsafe_allow_html=True)
    st.markdown('<div class="login-subtitle">Log in to the Humble OMS</div>', unsafe_allow_html=True)

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Log In"):
        if username == USERNAME and password == PASSWORD:
            st.session_state.logged_in = True
            st.success("Login successful!")
            st.rerun()
        else:
            st.error("Incorrect username or password.")

    st.markdown('</div>', unsafe_allow_html=True)
    st.stop()
