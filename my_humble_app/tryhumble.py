import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from streamlit_gsheets import GSheetsConnection
from streamlit_option_menu import option_menu
from PIL import Image
from google.oauth2.service_account import Credentials
import plotly.express as px
from datetime import datetime, timedelta
from st_aggrid import AgGrid, GridOptionsBuilder, JsCode
import base64
from io import BytesIO
import plotly.express as px
import calendar 

# --- PAGE SETUP ---
st.set_page_config(layout="wide")

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
with st.sidebar:
    page = option_menu(
        menu_title= None,
        options=[
            "Control Tower", 
            "Inventory Dashboard", 
            "Inbounds Dashboard", 
            "Outbounds Dashboard",
            "FAQs/Guide", 
            "Humble Bot"
        ],
        icons=["house", "box2", "file-arrow-down", "file-arrow-up", "question-lg", "chat"],
        default_index=0,
        key="main_page",
        styles={
            "container": {
                "padding": "0rem 0rem",
                "background-color": "#1C0033",
                "border-radius": "0px",
                "margin": "0",
                "position": "relative",
                "left": "0px"
            },
            "icon": {
                "color": "#fffff",
                "font-size": "13.5px",
                "margin-right": "8px",
                "position": "relative",
                "left": "-2px"
            },
            "nav-link": {
                "font-family": "Segoe UI, sans-serif",
                "font-size": "13px",
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

    st.markdown("""
        <hr style="border: none; border-top: 1px solid #ffffff33; margin: 10px 0;" />
    """, unsafe_allow_html=True)

    # Bottom: Footer Navigation
    selected_footer = option_menu(
        menu_title=None,
        options=["Guide", "Contact Us", "Log Out"],
        icons=["info-circle", "chat-left-dots", "box-arrow-right"],
        default_index=-1,
        key="footer_page",
        styles={
            "container": {
                "padding": "0rem 0rem",
                "background-color": "#1C0033",
                "border-radius": "0px",
                "margin": "0",
                "position": "relative",
                "left": "0px"
            },
            "icon": {
                "color": "#fffff",
                "font-size": "13.5px",
                "margin-right": "8px",
                "position": "relative",
                "left": "-2px"
            },
            "nav-link": {
                "font-family": "Segoe UI, sans-serif",
                "font-size": "13px",
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
                "background-color": "#e35d60", # pink 
                "color": "#ffffff", # pink
                "icon": "#ffffff",
                "font-weight": "700",
            }
        }
    )


def metric_card(title, value, suffix=""):
    st.markdown(f"""
        <div style='display: flex; align-items: flex-start; background: #ffffff;
            border-radius: 10px; box-shadow: 0 2px 6px rgba(0,0,0,0.06);
            padding: 12px 16px; margin-bottom: 8px; border-left: 5px solid #e06163;
            min-height: 75px; max-height: 75px; overflow: hidden; transition: all 0.2s ease;'>
            <div style='width: 100%;'>
                <div style='margin-bottom: 4px; font-size: 12.5px; color: #444; font-weight: 500;
                            white-space: nowrap; overflow: hidden; text-overflow: ellipsis;'>
                    {title}
                </div>
                <div style='font-size: 16px; font-weight: 700; color: #1e3932; line-height: 1.2;
                            display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical;
                            overflow: hidden; text-overflow: ellipsis;'>
                    {value} {suffix}
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
# CONTROL TOWER CONNECTION --------------------------------------------------------------------------------------------------------------------------------------------


@st.cache_data(ttl=60)
def get_control_tower_data(sheet_index=0):
    credentials_path = "control-tower-454909-57be7bcbb0a5.json"
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

    tab_labels = ["📘 User Guide", "📦 Supplier Progress Tracker", "📋 Account Masterlist", "🧩 Prospects"]
    sheet_indices = [None, 0, 1, 2]
    tabs = st.tabs(tab_labels)

    for tab, sheet_name, sheet_index in zip(tabs, tab_labels, sheet_indices):
        with tab:
            st.markdown(f"<h4 style='margin-bottom: 0.2rem;'>{sheet_name}</h4>", unsafe_allow_html=True)

            if sheet_name == "📘 User Guide":
                st.markdown("### How to Use the Control Tower")

                col1, col2, col3 = st.columns(3)

                card_style = """
                    <style>
                        .hover-card {
                            background-color: #ffffff;
                            border-radius: 12px;
                            padding: 20px;
                            box-shadow: 0 4px 10px rgba(0,0,0,0.05);
                            text-align: center;
                            transition: transform 0.2s ease, box-shadow 0.2s ease;
                        }
                        .hover-card:hover {
                            transform: translateY(-6px);
                            box-shadow: 0 8px 20px rgba(0,0,0,0.12);
                        }
                    </style>
                """
                st.markdown(card_style, unsafe_allow_html=True)

                with col1:
                    st.markdown("""
                    <div class='hover-card'>
                        <img src="https://cdn-icons-png.flaticon.com/128/16133/16133264.png" width="60"/>
                        <h4 style='margin-top: 10px;'>Supplier Progress Tracker</h4>
                        <p style='font-size: 14px; color: #444;'>
                        Track deals, PIFs, valuations, and more for onboarded clients. 
                        View endorsement dates, signed documents, and activation status all in one place.
                        </p>
                    </div>
                    """, unsafe_allow_html=True)

                with col2:
                    st.markdown("""
                    <div class='hover-card'>
                        <img src="https://cdn-icons-png.flaticon.com/128/6012/6012311.png" width="60"/>
                        <h4 style='margin-top: 10px;'>Account Masterlist</h4>
                        <p style='font-size: 14px; color: #444;'>
                        Access full account metadata, including revenue breakdown and status tags. 
                        Use filters to analyze active and inactive accounts.
                        </p>
                    </div>
                    """, unsafe_allow_html=True)

                with col3:
                    st.markdown("""
                    <div class='hover-card'>
                        <img src="https://cdn-icons-png.flaticon.com/128/10656/10656229.png" width="60"/>
                        <h4 style='margin-top: 10px;'>Prospects</h4>
                        <p style='font-size: 14px; color: #444;'>
                        Manage incoming schedules such as oculars, QC, and inbounds. 
                        Linked to the Inbound Scheduler — updates in real time based on form submissions.
                        </p>
                    </div>
                    """, unsafe_allow_html=True)

                continue  # ✅ Skip the rest of the loop

            # ✅ For all other tabs, load the data safely
            if sheet_index is not None:
                df = get_control_tower_data(sheet_index=sheet_index)
                if df.empty:
                    st.error("No data found.")
                    continue
            else:
                continue 


# ----------------------------- SUPPLIER PROGRESS TRACKER --------------------------------------------------------------------------------------------------------
            if sheet_name == "📦 Supplier Progress Tracker":
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
                    border-left: 4px solid #605399;
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
                    border-left: 4px solid #605399; /* Adjust color and width as needed */
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

                if month_filter != "All":
                    current_count = df[df["Month-Year"] == month_filter].shape[0]
                    
                    # Logic to get previous month and compare
                    selected_month_datetime = pd.to_datetime(month_filter, format='%B %Y')
                    previous_month_datetime = selected_month_datetime - pd.DateOffset(months=1)
                    previous_month_str = previous_month_datetime.strftime('%B %Y')

                    # Check if previous month data exists (from Feb onwards)
                    if previous_month_str in df["Month-Year"].values:
                        previous_count = df[df["Month-Year"] == previous_month_str].shape[0]

                        # Calculate percentage change
                        if previous_count > 0:
                            percent_change = ((current_count - previous_count) / previous_count) * 100
                            percent_change_str = f"{percent_change:.2f}%"
                            growth_symbol = "🔼" if percent_change > 0 else "🔽"
                            growth_color = "green" if percent_change > 0 else "red"
                        else:
                            percent_change_str = "N/A"
                            growth_symbol = ""
                            growth_color = "black"
                    else:
                        percent_change_str = None  # No previous month data (e.g., Jan 2025)
                else:
                    current_count = df.shape[0]
                    percent_change_str = None  # Don't show percentage for "All"

                # --- Column 2: Metric Cards (Interchanged Order) ---
                with col2:
                    st.markdown(f"""
                    <div class='metric-card'>
                        <img src='https://cdn-icons-png.flaticon.com/128/12458/12458553.png' width='35' style='margin-bottom:10px;opacity:0.7;'/>
                        <div class='metric-title'>Top Activation Month</div>
                        <div class='metric-value'>
                            {top_month} 
                            <span style='font-size:13px; color:green;'>{top_count} clients</span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

                    if percent_change_str:
                        percent_display = f"{'+' if percent_change > 0 else ''}{int(percent_change)}%"
                        st.markdown(f"""
                        <div class='metric-card'>
                            <img src='https://cdn-icons-png.flaticon.com/128/3126/3126647.png' width='35' style='margin-bottom:10px;opacity:0.7;'/>
                            <div class='metric-title'>Total Activated Accounts</div>
                            <div class='metric-value'>{current_count}</div>
                            <div class='metric-growth' style='color:{growth_color};'>{percent_display} vs last month</div>
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.markdown(f"""
                        <div class='metric-card'>
                            <img src='https://cdn-icons-png.flaticon.com/128/3126/3126647.png' width='35' style='margin-bottom:10px;opacity:0.7;'/>
                            <div class='metric-title'>Total Activated Accounts</div>
                            <div class='metric-value'>{current_count}</div>
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

            if sheet_name == "📋 Account Masterlist" and "Account Name" in df.columns:
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

            if sheet_name == "🧩 Prospects":
                st.markdown("### Inbound Schedule Tracker")

                # --- Date Parsing ---
                df["Planned Date (Raw)"] = pd.to_datetime(df["Planned Date"], errors="coerce")
                df["Planned Date"] = df["Planned Date (Raw)"].dt.strftime("%B %d, %Y")
                df["Planned Month"] = df["Planned Date (Raw)"].dt.strftime("%B %Y")
                df["Month Sort"] = df["Planned Date (Raw)"].dt.to_period("M")

                # --- Month Dropdown ---
                month_options = df.sort_values("Month Sort")["Planned Month"].dropna().unique().tolist()
                month_options.insert(0, "All")

                # Get current month string (e.g. "April 2025")
                current_month_str = pd.Timestamp.today().strftime("%B %Y")

                # Set default index: if current month is in the list, use it, else fallback to index 0
                default_month_index = month_options.index(current_month_str) if current_month_str in month_options else 0

                # Month selector
                selected_month = st.selectbox(
                    "📆 Filter by Month",
                    month_options,
                    index=default_month_index,
                    key="month_filter_dropdown_prospects"
                )
                # --- Week Radio Filter (Horizontal, No "All") ---
                selected_week = st.radio(
                    "🗓️ Filter by Week",
                    ["Past Week", "This Week", "Next Week"],
                    key="week_filter_radio",
                    horizontal=True
                )

                # --- Filter by Month ---
                if selected_month == "All":
                    filtered_df = df.copy()
                else:
                    filtered_df = df[df["Planned Month"] == selected_month].copy()

                # --- Filter by Week ---
                today = pd.Timestamp.today().normalize()
                if selected_week == "Past Week":
                    start_date = today - pd.Timedelta(days=today.weekday() + 7)
                    end_date = today - pd.Timedelta(days=today.weekday() + 1)
                elif selected_week == "This Week":
                    start_date = today - pd.Timedelta(days=today.weekday())
                    end_date = start_date + pd.Timedelta(days=6)
                elif selected_week == "Next Week":
                    start_date = today + pd.Timedelta(days=(7 - today.weekday()))
                    end_date = start_date + pd.Timedelta(days=6)

                # Apply Week Filter
                filtered_df = filtered_df[
                    (filtered_df["Planned Date (Raw)"] >= start_date) & (filtered_df["Planned Date (Raw)"] <= end_date)
                ]

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
            if sheet_name == "📦 Supplier Progress Tracker":
                st.markdown("### 📋 Full Sheet Data")
                st.dataframe(df, use_container_width=True)

            elif sheet_name == "📋 Account Masterlist":
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
    credentials_path = "inventory-dashboard-455009-887625f925f2.json"
    scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    credentials = Credentials.from_service_account_file(credentials_path, scopes=scopes)
    gc = gspread.authorize(credentials)

    spreadsheet_id = "1zjwGFngmxPszz_-imJvVqbhi856zgJLSpiI_WmIO9vI"
    sh = gc.open_by_key(spreadsheet_id)
    worksheet = sh.get_worksheet(2)
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
    currency_columns = ["Unit Price", "Total Price", "Total Sold"]
    for col in currency_columns:
        df[col] = (
            df[col]
            .str.replace("₱", "", regex=False)
            .str.replace(",", "", regex=False)
            .replace("", "0")  # replace empty strings
            .astype(float)
        )

    date_columns = ["Date Inbounded", "Date Sold"]
    for col in date_columns:
        df[col] = pd.to_datetime(df[col], errors='coerce')

    df["Sales Cycle"] = pd.to_numeric(df["Sales Cycle"], errors='coerce').fillna(0).astype(int)
    df["On Hand Qty"] = pd.to_numeric(df["On Hand Qty"], errors='coerce').fillna(0).astype(int)
    df["Qty Sold"] = pd.to_numeric(df["Qty Sold"], errors='coerce').fillna(0).astype(int)

    return df

# INVENTORY DASHBOARD --------------------------------------------------------------------------------------------------------------------------------------------


if page == "Inventory Dashboard":
    df_raw = get_inventory_data()
    df = preprocess_inventory_data(df_raw)

    st.title("2025 Inventory Dashboard")

    st.markdown("""
    <style>
    .metric-card {
        background: linear-gradient(90deg, #fff0ff, #cfdafd);
        border-radius: 20px;
        padding: 1.2rem 1.2rem 0.5rem 1.2rem;
        margin-bottom: 1rem;
        box-shadow: 0 8px 20px rgba(0,0,0,0.12);
        height: 162px;
        display: flex;
        flex-direction: column;
        justify-content: flex-end;     /* Bottom vertical alignment */
        align-items: flex-start;       /* Left horizontal alignment */
        border-left: 6px solid #605399;
        transition: all 0.25s ease;
        text-align: left;
        max-width: 188px;
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
                <div style="margin-bottom: 10px;">
                    <img src="{icon_url}" width="32" style="opacity: 0.6;" />
                </div>
                <div style='color: #555; font-weight: 550; font-size: 13px; margin-bottom: 3px;'>{title}</div>
                <div style='font-size: 28px; font-weight: 750; color: {value_color};'>{value} {suffix}</div>
            </div>
        """, unsafe_allow_html=True)

        # --- Client Filter Logic ---
    client_options = sorted(df["Client"].unique())
    selected_client = st.selectbox("🔍 Choose Client for Detailed View", ["All"] + client_options)

    # Apply filter if not All
    filtered_df = df if selected_client == "All" else df[df["Client"] == selected_client]

    # --- Metrics Calculation ---
    def compute_metrics(dataframe):
        return {
            "total_items": dataframe.shape[0],
            "total_sales": dataframe["Total Sold"].sum(),
            "avg_sales_cycle": dataframe["Sales Cycle"].mean(),
            "total_on_hand": dataframe["On Hand Qty"].sum(),
            "total_qty_sold": dataframe["Qty Sold"].sum(),
        }

    overview_metrics = compute_metrics(df)
    client_metrics = compute_metrics(filtered_df)

    # --- Tab Layout ---
    tab1, tab2 = st.tabs(["📊 Inventory Overview", "👤 Inventory Per Client"])

    # 📊 OVERVIEW TAB
    with tab1:
        st.markdown("### Inventory Summary")
        spacer1, col1, col2, col3, col4, col5, spacer2 = st.columns([0.2, 0.6, 0.6, 0.6, 0.6, 0.6, 0.2])
        with col1:
            metric_card("Total Items", overview_metrics["total_items"], "https://cdn-icons-png.flaticon.com/128/504/504528.png")
        with col2:
            metric_card("Total Sales", f"₱{overview_metrics['total_sales']:,.0f}", "https://cdn-icons-png.flaticon.com/128/3367/3367562.png", "", "#b94e34")
        with col3:
            metric_card("Avg Sales Cycle", f"{overview_metrics['avg_sales_cycle']:.1f}", "https://cdn-icons-png.flaticon.com/128/9148/9148972.png", "days")
        with col4:
            metric_card("On Hand", overview_metrics["total_on_hand"], "https://cdn-icons-png.flaticon.com/128/7480/7480113.png")
        with col5:
            metric_card("Qty Sold", overview_metrics["total_qty_sold"], "https://cdn-icons-png.flaticon.com/128/15554/15554788.png")

    # 👤 CLIENT TAB
    with tab2:
        st.markdown(f"### Inventory Summary - `{selected_client}`" if selected_client != "All" else "### 👤 Select a Client")
        if selected_client != "All":
            spacer1, col1, col2, col3, col4, col5, spacer2 = st.columns([0.2, 0.6, 0.6, 0.6, 0.6, 0.6, 0.2])
            with col1:
                metric_card("Total Items", client_metrics["total_items"], "https://cdn-icons-png.flaticon.com/128/504/504528.png")
            with col2:
                metric_card("Total Sales", f"₱{client_metrics['total_sales']:,.2f}", "https://cdn-icons-png.flaticon.com/128/3367/3367562.png", "", "#e74c3c")
            with col3:
                metric_card("Avg Sales Cycle", f"{client_metrics['avg_sales_cycle']:.1f}", "https://cdn-icons-png.flaticon.com/128/9148/9148972.png", "days")
            with col4:
                metric_card("On Hand", client_metrics["total_on_hand"], "https://cdn-icons-png.flaticon.com/128/7480/7480113.png")
            with col5:
                metric_card("Qty Sold", client_metrics["total_qty_sold"], "https://cdn-icons-png.flaticon.com/128/15554/15554788.png")
        else:
            st.info("Select a specific client from the dropdown above to view detailed metrics.")

    st.divider()

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
        st.plotly_chart(fig_avail, use_container_width=True)

    with col2:
        st.markdown("#### 📈 Monthly Sales Trend")
        filtered_df["Month"] = filtered_df["Date Sold"].dt.to_period("M").astype(str)
        sales_by_month = filtered_df.groupby("Month")["Total Sold"].sum().reset_index()
        fig_trend = px.line(sales_by_month, x="Month", y="Total Sold", title="", markers=True, height=280)
        st.plotly_chart(fig_trend, use_container_width=True)

    # --- Row 2: Client Summary + Highest Inventory Month ---
    col3, col4 = st.columns([1, 1])

    with col3:
        st.markdown("#### 👥 Client-Based Summary")
        client_summary = df.groupby("Client").agg({
            "Total Sold": "sum",
            "Qty Sold": "sum",
            "Sales Cycle": "mean"
        }).reset_index()

        fig_client = px.bar(
            client_summary,
            x="Client",
            y="Total Sold",
            title="",
            text="Total Sold",
            height=280
        )
        st.plotly_chart(fig_client, use_container_width=True)

    with col4:
        st.markdown("#### 🏆 Highest Inventory Month")

        inventory_by_month = filtered_df.copy()
        inventory_by_month["Month"] = inventory_by_month["Date Inbounded"].dt.to_period("M").astype(str)
        monthly_inventory = inventory_by_month.groupby("Month")["On Hand Qty"].sum().reset_index()

        highest_month = monthly_inventory.loc[monthly_inventory["On Hand Qty"].idxmax()]
        highlight_color = "#605399"

        fig_inv = px.bar(
            monthly_inventory.sort_values("On Hand Qty", ascending=True),
            x="On Hand Qty",
            y="Month",
            orientation="h",
            title="",
            height=280
        )
        fig_inv.update_traces(marker_color=[
            highlight_color if m == highest_month["Month"] else "#dcdcdc"
            for m in monthly_inventory["Month"]
        ])
        fig_inv.update_layout(
            showlegend=False,
            margin=dict(t=20),
        )

        st.plotly_chart(fig_inv, use_container_width=True)
        st.caption(f"📦 **{highest_month['Month']}** had the highest inventory: **{int(highest_month['On Hand Qty']):,} units**")

    # --- Full Table ---
    st.subheader("📋 Inventory Table")
    st.dataframe(filtered_df, use_container_width=True)

# INBOUNDS CONNECTION --------------------------------------------------------------------------------------------------------------------------------------------

@st.cache_data(ttl=60)
def get_inventory_data():
    credentials_path = "inbounds-dashboard-0d48bc43c7e4.json"
    scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    credentials = Credentials.from_service_account_file(credentials_path, scopes=scopes)
    gc = gspread.authorize(credentials)

    spreadsheet_id = "1C13KdQDIssPB02vWd-ma2t6yWDpiIDB28e7dkc2M-vc"
    sh = gc.open_by_key(spreadsheet_id)
    worksheet = sh.get_worksheet(1)
    data = worksheet.get_all_values()

    if not data:
        return pd.DataFrame()

    # 🔧 Correct header row
    raw_headers = data[0]
    headers = [h.strip() for h in raw_headers if h.strip() != ""]

    # 🔧 Start from row 1 (data rows)
    df_data = [row[:len(headers)] for row in data[1:] if any(cell.strip() for cell in row)]

    df = pd.DataFrame(df_data, columns=headers)

    numeric_columns = ["QTY"]
    for col in numeric_columns:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    return df.reset_index(drop=True)

if page == "Inbounds Dashboard":
    df_raw = get_inventory_data()
    # If you have a function like preprocess_inventory_data, call it here
    # df = preprocess_inventory_data(df_raw)
    df = df_raw  # Placeholder
    st.title("Inbounds Dashboard")
    st.dataframe(df, use_container_width=True)

# OUTBOUNDS CONNECTION --------------------------------------------------------------------------------------------------------------------------------------------

@st.cache_data(ttl=60)
def get_outbounds_dashboard_data(sheet_index=0):
    credentials_path = "outbounds-dashboard-856b41a4ec59.json"
    scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    credentials = Credentials.from_service_account_file(credentials_path, scopes=scopes)
    gc = gspread.authorize(credentials)

    spreadsheet_id = "1Md7tsA-oFNrqGbcbSFkOiWprUFh6hZKxTuP0edarfTU"
    sh = gc.open_by_key(spreadsheet_id)
    worksheet = sh.get_worksheet(sheet_index)
    data = worksheet.get_all_values()

    if not data:
        return pd.DataFrame()

    header_row_index = 0  # Correct: headers are in row 1 (0-indexed)
    headers = data[header_row_index]
    df_data = data[header_row_index + 1:]

    df = pd.DataFrame(df_data, columns=headers)
    df = df.dropna(how="all", axis=0)
    df = df.dropna(how="all", axis=1)

    return df

def preprocess_inventory_data(df):
    currency_columns = ["Unit Price", "Total Price", "Total Sold"]
    for col in currency_columns:
        if col in df.columns:  # ✅ Only process if column exists
            df[col] = (
                df[col]
                .str.replace("₱", "", regex=False)
                .str.replace(",", "", regex=False)
                .replace("", "0")  # Replace empty strings
                .astype(float)
            )

    date_columns = ["Date Inbounded", "Date Sold"]
    for col in date_columns:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors='coerce')

    numeric_columns = ["Sales Cycle", "On Hand Qty", "Qty Sold"]
    for col in numeric_columns:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype(int)

    return df

# OUTBOUNDS DASHBOARD --------------------------------------------------------------------------------------------------------------------------------------------

if page == "Outbounds Dashboard":
    df_raw = get_outbounds_dashboard_data()
    try:
        df = preprocess_inventory_data(df_raw)
    except KeyError as e:
        st.error(f"Missing expected column: {e}")
        df = df_raw

    st.title("Outbounds Dashboard")
    st.dataframe(df, use_container_width=True)