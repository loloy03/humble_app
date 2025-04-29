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
        default_index=-1,
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
    credentials_path = "control-tower-454909-84b11e26051b.json"
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

                with col1:
                    st.markdown("""
                    <div style='background-color: #ffffff; border-radius: 12px; padding: 20px; 
                                box-shadow: 0 4px 10px rgba(0,0,0,0.05); text-align: center;'>
                        <img src="https://cdn-icons-png.flaticon.com/512/3665/3665923.png" width="60"/>
                        <h4 style='margin-top: 10px;'>📦 Supplier Progress Tracker</h4>
                        <p style='font-size: 14px; color: #444;'>
                        Track deals, PIFs, valuations, and more for onboarded clients. 
                        View endorsement dates, signed documents, and activation status all in one place.
                        </p>
                    </div>
                    """, unsafe_allow_html=True)

                with col2:
                    st.markdown("""
                    <div style='background-color: #ffffff; border-radius: 12px; padding: 20px; 
                                box-shadow: 0 4px 10px rgba(0,0,0,0.05); text-align: center;'>
                        <img src="https://cdn-icons-png.flaticon.com/512/4248/4248443.png" width="60"/>
                        <h4 style='margin-top: 10px;'>📋 Account Masterlist</h4>
                        <p style='font-size: 14px; color: #444;'>
                        Access full account metadata, including revenue breakdown and status tags. 
                        Use filters to analyze active and inactive accounts.
                        </p>
                    </div>
                    """, unsafe_allow_html=True)

                with col3:
                    st.markdown("""
                    <div style='background-color: #ffffff; border-radius: 12px; padding: 20px; 
                                box-shadow: 0 4px 10px rgba(0,0,0,0.05); text-align: center;'>
                        <img src="https://cdn-icons-png.flaticon.com/512/3803/3803228.png" width="60"/>
                        <h4 style='margin-top: 10px;'>🧩 Prospects</h4>
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
                    height: 93px;
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
                    font-size: 14px;
                    font-weight: 600;
                    color: #666;
                    margin-bottom: 6px;
                }
                .info-value {
                    font-size: 20px;
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

                # === Plot background CSS ===
                PLOT_BGCOLOR = "rgba(0,0,0,0)"

                st.markdown(
                    f"""
                    <style>
                    .stPlotlyChart {{
                        position: relative;
                        outline: 4px solid {PLOT_BGCOLOR};
                        border-radius: 20px;
                        padding: 5px 5px 5px 0px;
                        background: linear-gradient(90deg, #f5e1ff, #d6caff);
                        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.12);
                        margin: auto;
                        max-width: 490px;
                    }}
                    .stPlotlyChart:hover {{
                        transform: translateY(-5px);
                        box-shadow: 0 12px 24px rgba(0, 0, 0, 0.18);
                    }}
                    .stPlotlyChart::before {{
                        content: "📊 Account Type Distribution";
                        position: absolute;
                        top: 10px;
                        left: 15px;
                        font-weight: 600;
                        font-size: 18px;
                        color: #333333;
                    }}
                    .metric-card {{
                        background: linear-gradient(90deg, #f5e1ff, #d6caff);
                        border-radius: 20px;
                        padding: 1.5rem 1.2rem;
                        margin-bottom: 1rem;
                        box-shadow: 0 6px 14px rgba(0, 0, 0, 0.08);
                        height: 205px;
                        display: flex;
                        flex-direction: column;
                        justify-content: flex-end;
                        transition: all 0.25s ease;
                    }}
                    .metric-card:hover {{
                        transform: translateY(-6px);
                        box-shadow: 0 10px 24px rgba(0, 0, 0, 0.15);
                    }}
                    .metric-title {{
                        color: #666;
                        font-weight: 600;
                        font-size: 14px;
                        margin-bottom: 6px;
                    }}
                    .metric-growth {{
                        font-size: 13px;
                        font-weight: 600;
                        margin-bottom: 4px;
                    }}
                    .metric-value {{
                        font-size: 26px;
                        font-weight: 800;
                        color: #1c1c1c;
                    }}
                    </style>
                    """, unsafe_allow_html=True
                )

            # === Month Filter Data ===
            month_filter = "All"
            if "Month-Year" in df.columns:
                months = sorted(df["Month-Year"].dropna().unique().tolist())

            # === Layout ===
            col1, col2, col3 = st.columns([1.5, 0.5, 1])

            # --- Column 1: Filter Label ---
            with col1:
                st.markdown("#### 📅 Filter by Month")
                month_filter = st.selectbox("📅 Filter by Month", ["All"] + months, key="month_filter_dropdown")

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

            # --- Column 2: Metric Cards (Interchanged Order) ---
            with col2:
                # Top Activation Month (row 1)
                st.markdown(f"""
                <div class='metric-card'>
                    <div class='metric-title'>Top Activation Month</div>
                    <div class='metric-value'>{top_month} ({top_count})</div>
                </div>
                """, unsafe_allow_html=True)

                # Total Activated Accounts (row 2)
                st.markdown(f"""
                <div class='metric-card'>
                    <div class='metric-title'>Total Activated Accounts</div>
                    <div class='metric-value'>{current_count}</div>
                </div>
                """, unsafe_allow_html=True)

            # --- Column 3: Pie Chart ---
            with col3:
                if "Account Type" in df.columns:
                    pie_df = df.copy()
                    if month_filter != "All" and "Month-Year" in df.columns:
                        pie_df = df[df["Month-Year"] == month_filter]

                    account_counts = pie_df["Account Type"].dropna().value_counts().reset_index()
                    account_counts.columns = ["Account Type", "Count"]

                    fig1 = px.pie(account_counts, values="Count", names="Account Type", hole=0.3)
                    fig1.update_traces(textposition='inside', textinfo='percent+label', textfont_size=12)
                    fig1.update_layout(
                        height=400,
                        width=380,
                        paper_bgcolor=PLOT_BGCOLOR,
                        plot_bgcolor="white",
                        margin=dict(t=60, b=20, l=10, r=10)
                    )

                    st.markdown("<div style='text-align: center;'>", unsafe_allow_html=True)
                    st.plotly_chart(fig1, use_container_width=False)
                    st.markdown("</div>", unsafe_allow_html=True)
                else:
                    st.warning("⚠️ 'Account Type' column not found in your dataset.")

                                # === Plot background CSS ===
                
                PLOT_BGCOLOR = "rgba(0,0,0,0)"

                st.markdown(
                    f"""
                    <style>
                    .stPlotlyChart {{
                        position: relative;
                        outline: 4px solid {PLOT_BGCOLOR};
                        border-radius: 20px;
                        padding: 5px 5px 5px 0px;
                        background: linear-gradient(90deg, #f5e1ff, #d6caff);
                        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.12);
                        margin: auto;
                        max-width: 490px;
                    }}
                    .stPlotlyChart:hover {{
                        transform: translateY(-5px);
                        box-shadow: 0 12px 24px rgba(0, 0, 0, 0.18);
                    }}
                    .stPlotlyChart::before {{
                        content: "📊 Account Type Distribution";
                        position: absolute;
                        top: 10px;
                        left: 15px;
                        font-weight: 600;
                        font-size: 18px;
                        color: #333333;
                    }}
                    .metric-card {{
                        background: linear-gradient(90deg, #f5e1ff, #d6caff);
                        border-radius: 20px;
                        padding: 1.5rem 1.2rem;
                        margin-bottom: 1rem;
                        box-shadow: 0 6px 14px rgba(0, 0, 0, 0.08);
                        height: 205px;
                        display: flex;
                        flex-direction: column;
                        justify-content: flex-end;
                        transition: all 0.25s ease;
                    }}
                    .metric-card:hover {{
                        transform: translateY(-6px);
                        box-shadow: 0 10px 24px rgba(0, 0, 0, 0.15);
                    }}
                    .metric-title {{
                        color: #666;
                        font-weight: 600;
                        font-size: 14px;
                        margin-bottom: 6px;
                    }}
                    .metric-growth {{
                        font-size: 13px;
                        font-weight: 600;
                        margin-bottom: 4px;
                    }}
                    .metric-value {{
                        font-size: 26px;
                        font-weight: 800;
                        color: #1c1c1c;
                    }}
                    </style>
                    """, unsafe_allow_html=True
                )

                # === Client Distribution Container ===
                with st.container():
                    # Visual container start
                    st.markdown("""
                    <div style="background-color: #F8F9FA; padding: 1.5rem; border-radius: 12px; box-shadow: 0 4px 14px rgba(0,0,0,0.08); margin-bottom: 2rem;">
                    <h5 style="margin-bottom: 1rem;">📈 Client Distribution (All Activated Clients)</h5>
                    """, unsafe_allow_html=True)

                    # Chart logic
                    df["Grouped Account"] = df["Account Name"].str.replace(r"(B\d+|Batch \d+| - [A-Za-z\s]+)", "", regex=True).str.strip()
                    grouped_counts = df["Grouped Account"].value_counts().reset_index()
                    grouped_counts.columns = ["Grouped Account", "Count"]

                    fastest_growing = None
                    if "Activation Date" in df.columns:
                        df["Activation Date"] = pd.to_datetime(df["Activation Date"])
                        last_30_days = datetime.now() - timedelta(days=30)
                        recent_df = df[df["Activation Date"] >= last_30_days]
                        recent_counts = recent_df["Grouped Account"].value_counts().reset_index()
                        recent_counts.columns = ["Grouped Account", "Recent Count"]
                        grouped_counts = grouped_counts.merge(recent_counts, on="Grouped Account", how="left").fillna(0)
                        fastest_growing = grouped_counts.sort_values(by="Recent Count", ascending=False).iloc[0]["Grouped Account"]

                    grouped_counts = grouped_counts.sort_values(by="Count", ascending=False)

                    fig2 = px.bar(
                        grouped_counts,
                        x="Grouped Account",
                        y="Count",
                        text="Count",
                        color="Grouped Account",
                        hover_data=["Recent Count"] if "Recent Count" in grouped_counts.columns else None,
                        title=""
                    )

                    fig2.update_layout(
                        height=450,
                        margin=dict(t=20, b=10, l=10, r=10),
                        title_font_size=18,
                        xaxis_title="",
                        yaxis_title="Number of Activations",
                        showlegend=False,
                        xaxis_tickangle=-45
                    )

                    fig2.update_traces(textposition='outside')

                    if fastest_growing:
                        fig2.add_annotation(
                            x=fastest_growing,
                            y=grouped_counts[grouped_counts["Grouped Account"] == fastest_growing]["Count"].values[0],
                            text="🚀 Fastest-Growing Client",
                            showarrow=True,
                            arrowhead=1,
                            ax=0,
                            ay=-50,
                            font=dict(color="green", size=13)
                        )

                    # Chart rendered outside the div (visually appears inside)
                    st.plotly_chart(fig2, use_container_width=True)

                    # Visual container end
                    st.markdown("</div>", unsafe_allow_html=True)