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

                month_filter = "All"
                if "Month-Year" in df.columns:
                    months = sorted(df["Month-Year"].dropna().unique().tolist())
                    month_filter = st.selectbox("📅 Filter by Endorsement Month", ["All"] + months)
                    if month_filter != "All":
                        df = df[df["Month-Year"] == month_filter]

                st.markdown("<h4 style='margin-top: 1rem;'>📊 Insights Summary</h4>", unsafe_allow_html=True)
                top1, top2 = st.columns(2)
                with top1:
                    metric_card("Total Activated Accounts", df["Account Name"].nunique())

                if month_filter == "All" and "Month-Year" in df.columns:
                    with top2:
                        top_month = df["Month-Year"].value_counts().idxmax()
                        top_count = df["Month-Year"].value_counts().max()
                        metric_card("Top Activation Month", f"{top_month} ({top_count})")

                col1, col2 = st.columns(2)
                with col1:
                    account_counts = df["Account Type"].dropna().value_counts().reset_index()
                    account_counts.columns = ["Account Type", "Count"]
                    fig1 = px.pie(account_counts, values="Count", names="Account Type",
                                title="Account Type Distribution", hole=0.3)
                    fig1.update_traces(textposition='inside', textinfo='percent+label', textfont_size=12)
                    fig1.update_layout(height=280, margin=dict(t=20, b=10, l=10, r=10), title_font_size=16)
                    st.plotly_chart(fig1, use_container_width=True)

                with col2:
                    df["Grouped Account"] = df["Account Name"].str.replace(r"(B\d+|Batch \d+| - [A-Za-z\s]+)", "", regex=True).str.strip()
                    grouped_counts = df["Grouped Account"].value_counts().reset_index()
                    grouped_counts.columns = ["Grouped Account", "Count"]
                    top_clients = grouped_counts.head(5)
                    fig2 = px.pie(top_clients, values="Count", names="Grouped Account",
                                title="Top 5 Client Distribution", hole=0.3)
                    fig2.update_traces(textposition='inside', textinfo='percent+label', textfont_size=12)
                    fig2.update_layout(height=280, margin=dict(t=30, b=10, l=10, r=10), title_font_size=16)
                    st.plotly_chart(fig2, use_container_width=True)

                  

# --------------------------------------------------------------------------------------------------------------------------------------------------------------------

            # --- Account Masterlist Logic ---
            if sheet_name == "📋 Account Masterlist" and "Account Name" in df.columns:
                selected_client = st.selectbox("Select a client", df["Account Name"].dropna().unique(), index=None)

                if selected_client:
                    # Get client data
                    client_data = df[df["Account Name"] == selected_client].iloc[0]

                    # Display Revenue Breakdown for the selected client
                    st.markdown(f"### 📊 Revenue Breakdown for {selected_client}")
                    fig = px.bar(
                        x=["Humble Revenue", "Supplier Revenue"],
                        y=[client_data["Humble Revenue"], client_data["Supplier Revenue"]],
                        labels={"x": "Revenue Type", "y": "Revenue (Amount)"},
                        title=f"Revenue for {selected_client}",
                        width=300,
                        height=250
                    )

                    fig.update_traces(texttemplate='%{y:.2f}%', textposition='outside', textfont_size=12)
                    st.plotly_chart(fig, use_container_width=True)

                    with st.expander("📋 View Client Data"):
                        st.dataframe(client_data.to_frame().T, use_container_width=True)
                else:
                    st.warning("Please select a valid client.")

# --------------------------------------------------------------------------------------------------------------------------------------------------------------------
#     guide_text = {
#         "📦 Supplier Progress Tracker": "Shows activated clients and key deal tracking info.",
#         "📋 Account Masterlist": "Central list of accounts with metadata, status, and tags.",
#         "🧩 Prospects": """
# 📑 **Inbound Scheduler** — for managing inbound, QC, and ocular requests.

# - Add requests to this sheet.
# - Tentative = soft reserve, Confirming = hard reserve.
# - You can add accounts without a date—they won’t show unless all schedule fields are filled.

# ✅ If confirmed:
# 1. Fill this [request form](https://docs.google.com/forms/u/0/d/e/1FAIpQLSe9fH7ZaeUu6D3ns960L8e26lAKJg67d0Xbkw6Bt58UlMTcVQ/formResponse)
# 2. Or notify SC, then remove the row once confirmed.
# """
#     }


            if sheet_name == "🧩 Prospects":
                # Convert 'Planned Date' to datetime for filtering
                df["Planned Date (Raw)"] = pd.to_datetime(df["Planned Date"], errors="coerce")

                # Create a display-friendly version of the date
                df["Planned Date"] = df["Planned Date (Raw)"].dt.strftime("%B %d, %Y")

                # Dropdown for week filtering
                date_filter = st.selectbox("📆 Filter by Schedule Timing", ["Past Week", "This Week", "Next Week"])

                # Today's date
                today = pd.Timestamp.today().normalize()

                # Filter logic
                if date_filter == "Past Week":
                    start_date = today - pd.Timedelta(days=today.weekday() + 7)
                    end_date = today - pd.Timedelta(days=today.weekday() + 1)
                elif date_filter == "This Week":
                    start_date = today - pd.Timedelta(days=today.weekday())
                    end_date = start_date + pd.Timedelta(days=6)
                elif date_filter == "Next Week":
                    start_date = today + pd.Timedelta(days=(7 - today.weekday()))
                    end_date = start_date + pd.Timedelta(days=6)

                # Apply filter using the raw datetime column
                filtered_df = df[(df["Planned Date (Raw)"] >= start_date) & (df["Planned Date (Raw)"] <= end_date)]

                # Output section
                st.markdown("### 📋 Inbound Schedule")
                if not filtered_df.empty:
                    st.dataframe(
                        filtered_df[["Account", "Planned Date", "Planned Time", "Schedule Status", "Purpose"]],
                        use_container_width=True
                    )
                else:
                    st.warning("No scheduled accounts in this time range.")

                # Embedded WH Schedule Viewer
                with st.expander("📅 View Full Warehouse Schedule"):
                    st.markdown("""
                    <div style="overflow: auto; width: 100%;">
                        <div style="transform: scale(0.8); transform-origin: top left; width: 1250px; height: 700px;">
                            <iframe src="https://docs.google.com/spreadsheets/d/e/2PACX-1vTwd6qAOGKpJzD6n_XmEtGT_UzZaJx8EvnAsT81K5ORXTw2fMOc5IzMYXiwQW5opGHp0_zsGzKwvAgj/pubhtml?gid=226802695&single=true"
                                    width="1600" height="900" frameborder="0"></iframe>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

# --------------------------------------------------------------------------------------------------------------------------------------------------------------------

            # --- Final Table (Full Sheet Data)
            if sheet_name in ["📦 Supplier Progress Tracker", "📋 Account Masterlist"]:
                st.markdown("### 📋 Full Sheet Data (Styled)")

                df_cleaned = df.dropna(subset=["Account Name", "Account Type"])

                # Shorten and linkify Google Drive links
                if "Google Drive Folder Link" in df_cleaned.columns:
                    df_cleaned["Google Drive Folder Link"] = df_cleaned["Google Drive Folder Link"].apply(
                        lambda url: f"[Open Folder]({url})" if pd.notna(url) and "http" in url else ""
                    )

                # Define JS badge renderer for Initial Deal Type
                deal_color_renderer = JsCode("""
                function(params) {
                    let status = params.value;
                    let color = {
                        'Closed Deal': '#b7eb8f',
                        'Open Deal': '#ffe58f',
                        'Ongoing': '#e6f7ff',
                        'Pending': '#fff1b8'
                    }[status] || '#d9d9d9';

                    let textColor = {
                        'Closed Deal': '#389e0d',
                        'Open Deal': '#d48806',
                        'Ongoing': '#1890ff',
                        'Pending': '#ad8b00'
                    }[status] || '#595959';

                    return `<span style="
                        background-color: ${color};
                        color: ${textColor};
                        padding: 4px 10px;
                        border-radius: 12px;
                        font-weight: 600;
                        font-size: 13px;
                        font-family: 'Nunito Sans', sans-serif';
                    ">${status}</span>`;
                }
                """)

                # ✅ Create the GridOptionsBuilder *first*
                gb = GridOptionsBuilder.from_dataframe(df_cleaned)

                # ✅ Configure column styling if it exists
                if "Initial Deal Type" in df_cleaned.columns:
                    gb.configure_column("Initial Deal Type", cellRenderer=deal_color_renderer)

                # Optional defaults
                gb.configure_default_column(resizable=True, filter=True)
                gridOptions = gb.build()

                # ✅ Render the table
                AgGrid(
                    df_cleaned,
                    gridOptions=gridOptions,
                    allow_unsafe_jscode=True,
                    height=450,
                    fit_columns_on_grid_load=True,
                    theme="streamlit"
                )

# INVENTORY DASHBOARD PAGE --------------------------------------------------------------------------------------------------------------------------------------------------

@st.cache_data(ttl=60)
def get_inventory_data():
    credentials_path = "inventory-dashboard-455009-3bee6b1a5b56.json"
    scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    credentials = Credentials.from_service_account_file(credentials_path, scopes=scopes)
    gc = gspread.authorize(credentials)

    spreadsheet_id = "1zjwGFngmxPszz_-imJvVqbhi856zgJLSpiI_WmIO9vI"
    sh = gc.open_by_key(spreadsheet_id)
    worksheet = sh.get_worksheet(2)
    data = worksheet.get_all_values()

    if not data:
        return pd.DataFrame()

    headers = data[0]
    df_data = data[1:]

    # Convert to DataFrame
    df = pd.DataFrame(df_data, columns=headers)

    # Clean blank rows: keep only rows where key fields are not empty
    df = df[df["Availability"].str.strip() != ""]  # Use another column like "Client" if preferred

    # Reset index
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


if page == "Inventory Dashboard":
    df_raw = get_inventory_data()
    df = preprocess_inventory_data(df_raw)

    st.title("## 📦 2025 Inventory Dashboard")

    # --- Metric Card Function ---
    def metric_card(title, value, suffix=""):
        st.markdown(f"""
            <div style='display:flex;align-items:center;background:#ffffff;
                border-radius:12px;box-shadow:0 4px 12px rgba(0,0,0,0.08);
                padding:20px 25px;margin-bottom:10px;border-left:6px solid #e06163;
                transition: all 0.3s ease;'>
                <div>
                    <div style='margin-bottom:5px;font-size:15px;color:#444;font-weight:500;'>{title}</div>
                    <div style='font-size:28px;font-weight:700;color:#1e3932;line-height:1.2;'>{value} {suffix}</div>
                </div>
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
            "total_skus": dataframe.shape[0],
            "total_sales": dataframe["Total Sold"].sum(),
            "avg_sales_cycle": dataframe["Sales Cycle"].mean(),
            "total_on_hand": dataframe["On Hand Qty"].sum(),
            "total_qty_sold": dataframe["Qty Sold"].sum(),
        }

    overview_metrics = compute_metrics(df)
    client_metrics = compute_metrics(filtered_df)

    # --- Tab Layout ---
    tab1, tab2 = st.tabs(["📊 Overview", "👤 Per Client"])

    # 📊 OVERVIEW TAB
    with tab1:
        st.markdown("### 📦 Inventory Summary (All Clients)")
        col1, col2, col3, col4, col5 = st.columns(5)
        with col1:
            metric_card("📦 Total SKUs", overview_metrics["total_skus"])
        with col2:
            metric_card("💸 Total Sales", f"₱{overview_metrics['total_sales']:,.2f}")
        with col3:
            metric_card("⏱️ Avg Sales Cycle", f"{overview_metrics['avg_sales_cycle']:.1f}", "days")
        with col4:
            metric_card("📍 On Hand", overview_metrics["total_on_hand"])
        with col5:
            metric_card("🛒 Qty Sold", overview_metrics["total_qty_sold"])

    # 👤 CLIENT TAB
    with tab2:
        st.markdown(f"### 👤 Inventory Summary - `{selected_client}`" if selected_client != "All" else "### 👤 Select a Client")
        if selected_client != "All":
            col1, col2, col3, col4, col5 = st.columns(5)
            with col1:
                metric_card("📦 Total SKUs", client_metrics["total_skus"])
            with col2:
                metric_card("💸 Total Sales", f"₱{client_metrics['total_sales']:,.2f}")
            with col3:
                metric_card("⏱️ Avg Sales Cycle", f"{client_metrics['avg_sales_cycle']:.1f}", "days")
            with col4:
                metric_card("📍 On Hand", client_metrics["total_on_hand"])
            with col5:
                metric_card("🛒 Qty Sold", client_metrics["total_qty_sold"])
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
            height=280  # Smaller height
        )
        st.plotly_chart(fig_avail, use_container_width=True)

    with col2:
        st.markdown("#### 📈 Monthly Sales Trend")
        filtered_df["Month"] = filtered_df["Date Sold"].dt.to_period("M").astype(str)
        sales_by_month = filtered_df.groupby("Month")["Total Sold"].sum().reset_index()
        fig_trend = px.line(sales_by_month, x="Month", y="Total Sold", title="", markers=True, height=280)
        st.plotly_chart(fig_trend, use_container_width=True)

    # --- Row 2: Client Summary (Full Width or Shared) ---
    col3, col4 = st.columns([1, 1])  # You can change this to [1] if you want full width

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

    # Optional: col4 can remain empty, or you can add another visual
    with col4:
        st.empty()
    # --- Outlier Detection: Slow Movers ---
    # st.subheader("🧊 Slow-Moving Inventory")
    # slow_movers = df[df["Sales Cycle"] > df["Sales Cycle"].mean() + df["Sales Cycle"].std()]
    #st.dataframe(slow_movers, use_container_width=True)

    # --- Full Table ---
    st.subheader("📋 Inventory Table")
    st.dataframe(filtered_df, use_container_width=True)
