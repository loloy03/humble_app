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
import plotly.graph_objects as go
from plotly.subplots import make_subplots

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
            "Inbounds Dashboard", 
            "Outbounds Dashboard",
            "Inventory Dashboard", 
            "Humble Bot",
            "FAQs/Guide"
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
        <hr style="border: none; border-top: 1px solid #ffffff; margin: 10px 0;" />
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
    
# INVENTORY CONNECTION --------------------------------------------------------------------------------------------------------------------------------------------

@st.cache_data(ttl=60)
def get_inventory_data():
    credentials_path = "inventory-dashboard-455009-887625f925f2.json"
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


    # --- Client Filter Logic (OUTSIDE the function) ---
    client_options = sorted(df["Client"].unique())
    selected_client = st.selectbox("🔍 Choose Client for Detailed View", ["All"] + client_options)

    filtered_df = df if selected_client == "All" else df[df["Client"] == selected_client]

    # ✨ Fix "On Hand Qty" based on "Availability" (only inside memory, no file editing)
    filtered_df["On Hand Qty"] = filtered_df.apply(
        lambda row: 0 if str(row.get("Availability", "")).lower() == "sold" else row.get("On Hand Qty", 0),
        axis=1
    )


    # --- Metrics Calculation ---
    def compute_metrics(dataframe):
        return {
            "total_items": dataframe.shape[0],
            "total_sales": dataframe["Total Sold"].sum(),
            "avg_sales_cycle": dataframe["Sales Cycle"].mean(),
            "total_on_hand": dataframe["On Hand Qty"].sum(),  # Now no need to recompute inside compute_metrics
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

        with st.container():
            expander = st.expander("📋 View Overall Client Details", expanded=False)
            with expander:
                # 📋 Generate the per-client summary
                client_summary = df.groupby("Client").agg({
                    "On Hand Qty": "sum",
                    "Unit Price": "sum",
                    "Qty Sold": "sum",
                    "Total Sold": "sum"
                }).reset_index()

                # 📝 Rename for clarity
                client_summary = client_summary.rename(columns={
                    "Client": "Client",
                    "On Hand Qty": "Total On Hand Qty",
                    "Unit Price": "Total Unit Price",
                    "Qty Sold": "Total Qty Sold",
                    "Total Sold": "Total Sales"
                })

                # 💸 Format currency fields (optional but makes it cleaner)
                client_summary["Total Unit Price"] = client_summary["Total Unit Price"].apply(lambda x: f"₱{x:,.0f}")
                client_summary["Total Sales"] = client_summary["Total Sales"].apply(lambda x: f"₱{x:,.0f}")

                # 📊 Display the dataframe inside expander
                st.dataframe(client_summary, use_container_width=True)

    # 👤 CLIENT TAB
    with tab2:
        st.markdown(f"### Inventory Summary - `{selected_client}`" if selected_client != "All" else "### 👤 Select a Client")

        if selected_client != "All":
            spacer1, col1, col2, col3, col4, col5, spacer2 = st.columns([0.2, 0.6, 0.6, 0.6, 0.6, 0.6, 0.2])

            with col1:
                metric_card("Total Items", client_metrics["total_items"], "https://cdn-icons-png.flaticon.com/128/504/504528.png")

            with col2:
                metric_card("Total Sales", f"₱{client_metrics['total_sales']:,.0f}", "https://cdn-icons-png.flaticon.com/128/3367/3367562.png", "", "#e74c3c")

            with col3:
                metric_card("Avg Sales Cycle", f"{client_metrics['avg_sales_cycle']:.1f}", "https://cdn-icons-png.flaticon.com/128/9148/9148972.png", "days")
            
            with col4:
                metric_card("On Hand", client_metrics["total_on_hand"], "https://cdn-icons-png.flaticon.com/128/7480/7480113.png")
            with col5:
                metric_card("Qty Sold", client_metrics["total_qty_sold"], "https://cdn-icons-png.flaticon.com/128/15554/15554788.png")
           
            with st.container():
                expander = st.expander("📋 View Item Details", expanded=False)

                with expander:
                    columns_to_show = ["Description", "On Hand Qty", "Unit Price", "Qty Sold", "Total Sold"]
                    small_table = filtered_df[columns_to_show].sort_values("Total Sold", ascending=False).reset_index(drop=True)

                    # Display using st.data_editor instead of st.dataframe to fully hide index
                    st.data_editor(
                        small_table,
                        use_container_width=True,
                        height=300,
                        disabled=True,   # Prevent editing, looks like a read-only table
                        hide_index=True  # ✅ Hides the index column
                    )

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

        # ✨ Prepare Inventory Data
        inventory_df = filtered_df.copy()

        # ✨ Convert "Date Inbounded" to datetime safely
        inventory_df["Date Inbounded"] = pd.to_datetime(inventory_df["Date Inbounded"], errors="coerce")
        inventory_df = inventory_df.dropna(subset=["Date Inbounded", "Inbounded Qty"])

        # ✨ Fix quantities
        inventory_df["Inbounded Qty"] = pd.to_numeric(inventory_df["Inbounded Qty"], errors="coerce")
        inventory_df = inventory_df.dropna(subset=["Inbounded Qty"])

        # ✨ Extract Month Name Only from "Date Inbounded"
        inventory_df["Month"] = inventory_df["Date Inbounded"].dt.strftime("%b")  # 'Jan', 'Feb', etc.

        # ✨ Group by Month
        inbound_by_month = inventory_df.groupby("Month")["Inbounded Qty"].sum().reset_index()

        # ✨ Reorder months properly
        month_order = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
                    "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
        inbound_by_month["Month"] = pd.Categorical(inbound_by_month["Month"], categories=month_order, ordered=True)
        inbound_by_month = inbound_by_month.sort_values("Month")

        # ✨ Plot Bar Graph
        fig_inbound = px.bar(
            inbound_by_month,
            x="Inbounded Qty",
            y="Month",
            orientation="h",  # Horizontal bar
            text_auto=True,
            height=280
        )
        st.plotly_chart(fig_inbound, use_container_width=True)

        # ✨ Show Highest Month Caption
        if not inbound_by_month.empty:
            highest_month_row = inbound_by_month.loc[inbound_by_month["Inbounded Qty"].idxmax()]
            st.caption(f"📦 **Highest Month:** {highest_month_row['Month']} ({int(highest_month_row['Inbounded Qty'])} units)")

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

def render_delta(delta_value):
    if delta_value is None:
        return "<p class='metric-delta' style='visibility: hidden;'>--</p>"
    
    sign = "+" if delta_value >= 0 else "-"
    color = "green" if delta_value >= 0 else "red"
    return f"<p class='metric-delta' style='color:{color}'>{sign} {abs(delta_value):.1f}% </p>"

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
    st.title("📦 Inbounds Dashboard")
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

    # 🔄 Recalculate monthly quantities
    monthly_qty = df.groupby('Month_Year')['QTY'].sum().sort_index()

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

    # 💅 Updated CSS Card Styling
    card_style = """
    <style>
        .hover-card {
            background: linear-gradient(90deg, #fff0ff, #fceae6);
            border-radius: 20px;
            padding: 1.6rem 0.5rem 2rem 0.5rem;
            box-shadow: 0 4px 10px rgba(0,0,0,0.05);
            display: flex;
            line-height: 0.9;
            flex-direction: column;
            justify-content: flex-start; /* aligns top content */
            text-align: left;
            font-size: 20px;
            font-weight: 600;
            transition: transform 0.2s ease, box-shadow 0.2s ease;
            margin: auto;
            max-height: 210px;
        }

        .hover-card:hover {
            transform: translateY(-6px);
            box-shadow: 0 8px 20px rgba(0,0,0,0.12);
        }

        .hover-card h4 {
            margin: 0 0 12px 0;
            font-size: 18px; /* ✅ Uniform title size */
        }

        .hover-card p {
            margin: 4px 0;
            font-size: 14px;
        }

        .metric-number {
            font-size: 40px;
            font-weight: 700;
            color: #4c2882;
            margin-top: 7px;           /* ⬅️ Tighter space to the title */
            line-height: 1;
            text-align: left;
            height: auto;              /* ⬅️ Let it flow naturally */
        }

        .metric-delta {
            font-size: 12px;
            margin-top: 4px;
        }

        .month-value {
            font-size: 26px;
            font-weight: 650;
            margin: 5px 0;
            color: #6756BE;
        }
        
        .month-value-row {
            display: flex;
            justify-content: space-between;
            gap: 10px;
            font-size: 18px;
            margin: 2px 0;
            line-height: 1;

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

    # Top 5 accounts by inbound QTY
    top_accounts = (
        df_filtered.groupby('Account')['QTY']
        .sum()
        .sort_values(ascending=False)
        .head(5)
        .reset_index()
    )

    # 🟪 4 Column Layout
    spacer1, col1, col2, col3, col4, spacer2 = st.columns([0.2, 1.4, 1.1, 0.9, 1.1, 0.2])

    with col1:
        # Tier Legend Card
        st.markdown("""
        <div class='hover-card'>
            <img src="https://cdn-icons-png.flaticon.com/128/17057/17057101.png" width="40" style="margin-bottom: 1px; display: block;" />
            <h4>Tier Legend</h4>
            <div style="font-size: 25px; line-height: 0.7; padding-left: 8px;">
                <p>
                    <span style="font-weight: 750;color: #281048;">Tier 1&nbsp;&nbsp;</span>
                    <span style="font-weight: 650; font-size: 15px;">Brand New/Sealed</span>
                </p>
                <p>
                    <span style="font-weight: 750; color: #281048;">Tier 2&nbsp;&nbsp;</span>
                    <span style="font-weight: 650; font-size: 15px;">Used w/ Minor Defects</span>
                </p>
                <p>
                    <span style="font-weight: 750; color: #281048;">Tier 3&nbsp;&nbsp;</span>
                    <span style="font-weight: 650; font-size: 15px;">Used w/ Major Defects</span>
                </p>
                <p>
                    <span style="font-weight: 750; color: #281048;">Tier 4&nbsp;&nbsp;</span>
                    <span style="font-weight: 650; font-size: 15px;">Beyond Economical Repair (Scrap)</span>
                </p>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # ➡️ Light divider
        st.markdown("""<hr style="border: 0.5px solid #ffffff; margin: 8px 0 12px 0;">""", unsafe_allow_html=True)

        # ➡️ Tier 1-4 Percentage Chart (inside expander)
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
                hole=0.5,
                pull=0,
                rotation=90
            )

            fig.update_layout(
                height=370,
                margin=dict(t=30, b=30, l=10, r=10),
                showlegend=True,
                annotations=[dict(
                    text='Tier 4',     # Optional: center label
                    x=0.5,
                    y=0.42,            # Lower vertical position
                    font_size=16,
                    showarrow=False
                )]
            )

            st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown(f"""
        <div class='hover-card'>
            <img src="https://cdn-icons-png.flaticon.com/128/3624/3624106.png" width="40" style="margin-bottom: 8px;" />
            <h4>Total Inbound Qty</h4>
            <div class='metric-number'>{current_qty:,}</div>
            {render_delta(mom_delta)}
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
        <div class='hover-card'>
            <img src="https://cdn-icons-png.flaticon.com/128/1528/1528669.png" width="40" style="margin-bottom: 8px;" />
            <h4>Unique Accounts</h4>
            <div class='metric-number'>{unique_accounts}</div>
            {render_delta(unique_delta) if selected_month != "All" else "<p class='metric-delta' style='visibility: hidden;'>--</p>"}
        </div>
        """, unsafe_allow_html=True)

        # ➡️ Small light divider
        st.markdown("""
            <hr style="border: 0.5px solid #ffffff; margin: 8px 0 12px 0;">
        """, unsafe_allow_html=True)

        # ➡️ Add mini-table inside expander
        with st.expander("Top 5 Clients 📈"):
            st.dataframe(
                top_accounts.set_index('Account'),  # Set Account as index
                use_container_width=True,
                hide_index=False
            )

            # Smaller font for table + expander title
            st.markdown("""
                <style>
                    div[data-testid="stDataFrame"] div[role="grid"] {
                        font-size: 9px;
                    }
                    section[data-testid="stExpander"] > summary {
                        font-size: 12px;
                    }
                </style>
            """, unsafe_allow_html=True)

    # Column 4: Highest Inbound Months
    with col4:
        top_months_html = """
        <div class='hover-card'>
            <img src="https://cdn-icons-png.flaticon.com/128/16877/16877580.png" width="40" style="margin-bottom: 8px; display: block;" />
            <h4>Highest Inbound Months</h4>
        """
        for _, row in top_months.iterrows():
            top_months_html += f"""<div class='month-value-row'>
                <span class='month-left'>{row['Month']}</span>
                <span class='month-right'>{int(row['Inbound Qty']):,} units</span>
            </div>"""
        top_months_html += "</div>"

        st.markdown(top_months_html, unsafe_allow_html=True)

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

    # Start 2-column layout
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
                marker=dict(line=dict(width=0)),  # cleaner bars
                width=0.4,  # makes bars thinner
                text=[
                    f"{tier_pct_df.loc[month, tier]:,.0f} units ({tier_pct_percent.loc[month, tier]:.1f}%)"
                    for month in tier_pct_percent.index
                ],
                textposition="inside",
                insidetextanchor="start",
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
                    hovertemplate=f"{tier}: %{{y}} units"
                ))
            else:
                fig_count.add_trace(go.Scatter(
                    name=tier,
                    x=tier_count_df.index,
                    y=tier_count_df[tier],
                    mode="lines+markers",
                    hovertemplate=f"{tier}: %{{y}} units"
                ))

        fig_count.update_layout(
            barmode='group' if chart_type == "Bar" else None,
            height=360,
            margin=dict(l=40, r=20, t=30, b=30),
            xaxis=dict(title="Month"),
            yaxis=dict(title="Quantity"),
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
        st.markdown("### 🧮 Count per Type")

        fig_type = go.Figure()
        fig_type.add_trace(go.Bar(
            x=type_plot_df['Quantity'],
            y=type_plot_df['Cleaned Type'],
            orientation='h',
            text=[f"{qty:,} units ({pct:.1f}%)" for qty, pct in zip(type_plot_df['Quantity'], type_plot_df['Percent'])],
            textposition='outside',
            marker_color='#4c2882'
        ))

        fig_type.update_layout(
            height=500,
            margin=dict(l=60, r=20, t=30, b=30),
            yaxis=dict(title=""),
            xaxis=dict(title="Units"),
        )

        st.plotly_chart(fig_type, use_container_width=True)

    with col2:
        st.markdown("### 🛠️ Issues Count")

        fig_issue = go.Figure()
        fig_issue.add_trace(go.Bar(
            x=issue_plot_df['Quantity'],
            y=issue_plot_df['Processed Remarks'],
            orientation='h',
            text=[f"{qty:,} units" for qty in issue_plot_df['Quantity']],
            textposition='outside',
            marker_color='#4c2882'
        ))

        fig_issue.update_layout(
            height=500,
            margin=dict(l=60, r=20, t=30, b=30),
            yaxis=dict(title=""),
            xaxis=dict(title="Units"),
        )

        st.plotly_chart(fig_issue, use_container_width=True)

    # 📊 Dashboard Layout — Types of Issues per Tier | Tiers per Main Category

    st.divider()

    col1, col2 = st.columns([1, 1])

    # --------------------------
    # ▶️ COL 1: Types of Issues per Tier (horizontal grid)

    with col1:
        st.subheader("📊 Types of Issues per Tier")

        def clean_specific_remark(remark):
            if pd.isna(remark) or remark.strip() == "":
                return None
            remark = remark.strip()
            if "working" in remark.lower():
                return "Working"
            elif "defective" in remark.lower():
                return "Defective"
            else:
                return remark

        df_filtered["Processed Remarks"] = df_filtered["Specific Remarks"].apply(clean_specific_remark)
        df_issues_filtered = df_filtered[df_filtered["Processed Remarks"].notna()]

        issue_tier_matrix = (
            df_issues_filtered.groupby(["Processed Remarks", "Tier"])['QTY']
            .sum()
            .reset_index()
        )

        # Force Tier order for consistency
        issue_tier_matrix["Tier"] = pd.Categorical(
            issue_tier_matrix["Tier"],
            categories=["Tier 1", "Tier 2", "Tier 3", "Tier 4"],
            ordered=True
        )

        fig_heat = px.density_heatmap(
            issue_tier_matrix,
            x="Tier",
            y="Processed Remarks",
            z="QTY",
            color_continuous_scale="Purples",
            title="Types of Issues per Tier (Heatmap)",
        )

        fig_heat.update_layout(
            height=500,
            margin=dict(t=40, l=60, r=20, b=40),
            xaxis_title="Tier",
            yaxis_title="Issue"
        )

        st.plotly_chart(fig_heat, use_container_width=True)

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

        # Build stacked bar
        fig_stack = go.Figure()
        for tier in tier_cat_pivot.columns:
            fig_stack.add_trace(go.Bar(
                name=tier,
                x=tier_cat_pivot.index,
                y=tier_cat_pivot[tier],
                text=[f"{int(val):,} units" for val in tier_cat_pivot[tier]],
                hovertemplate=f"{tier}<br>%{{x}}: %{{y}} units<extra></extra>"
            ))

        fig_stack.update_layout(
            barmode="stack",
            height=500,
            margin=dict(t=30, b=40, l=60, r=20),
            xaxis_title="Main Category",
            yaxis_title="Total Units",
            legend_title="Tier"
        )

        st.plotly_chart(fig_stack, use_container_width=True)

    # --- Full Table ---
    st.subheader("📋 Inbounds Table")
    st.dataframe(df_filtered, use_container_width=True)
   

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

# -----------------------------------------------
# 4. Main Outbounds Dashboard
# -----------------------------------------------
if page == "Outbounds Dashboard":

    st.title("🚚 2025 Outbounds Dashboard")

    # Load and preprocess data
    df_raw = get_outbounds_dashboard_data()
    df = preprocess_outbound_data(df_raw)
    df["Main Category"] = df["Description"].apply(extract_main_category)

    # 📅 Filter by Month (under title)
    months = sorted(df["Month_Year"].dropna().unique().tolist(), key=lambda x: pd.to_datetime(x, format='%b %Y'))
    selected_month = st.selectbox("📅 Filter by Month of Outbound", options=["All"] + months, index=0, key="month_filters_dropdown")

    # Apply Month Filter
    filtered_df = df.copy()
    if selected_month != "All":
        filtered_df = filtered_df[filtered_df["Month_Year"] == selected_month]

    # Metrics
    total_qty = filtered_df["QTY"].sum()
    total_value = filtered_df["Total Value"].sum()
    unique_customers = filtered_df["Customer Name"].nunique()

    # Top Customers by Qty and Value
    top_customers_qty = filtered_df.groupby("Customer Name")["QTY"].sum().sort_values(ascending=False).head(5).reset_index()
    top_customers_value = filtered_df.groupby("Customer Name")["Total Value"].sum().sort_values(ascending=False).head(5).reset_index()

    # Top Months
    top_months = df.groupby("Month_Year")["QTY"].sum().sort_values(ascending=False).head(3).reset_index()

    # Inject the custom hover-card styling
    card_style = """
    <style>
        .hover-card {
            background: linear-gradient(90deg, #fff0ff, #fceae6);
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
            max-height: 210px;
        }
        .hover-card:hover {
            transform: translateY(-6px);
            box-shadow: 0 8px 20px rgba(0,0,0,0.12);
        }
        .hover-card h4 {
            margin: 0 0 12px 0;
            font-size: 18px;
        }
        .hover-card p {
            margin: 4px 0;
            font-size: 14px;
        }
        .metric-number {
            font-size: 35px;
            font-weight: 650;
            color: #4c2882;
            margin-top: 7px;
            line-height: 1;
            text-align: left;
            height: auto;
        }
        .metric-delta {
            font-size: 12px;
            margin-top: 4px;
        }
    </style>
    """

    month_card_style = """
    <style>
        .month-value-row {
            display: flex;
            justify-content: space-between;
            gap: 1px;
            font-size: 18px; 
            margin: 2px 0; 
            line-height: 1;
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
    st.markdown(month_card_style, unsafe_allow_html=True)


    # --- Row 1: Metrics (Hover Cards)
    spacer1, col1, col2, col3, col4, spacer2 = st.columns([0.2, 1, 1.2, 0.8, 1.1, 0.2])

    with col1:
        st.markdown(f"""
        <div class='hover-card'>
            <img src="https://cdn-icons-png.flaticon.com/128/3624/3624117.png" width="35" style="margin-bottom: 5px;" />
            <h4>Total Outbound Qty</h4>
            <div class='metric-number'>{int(total_qty):,}</div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class='hover-card'>
            <img src="https://cdn-icons-png.flaticon.com/128/1611/1611179.png" width="35" style="margin-bottom: 5px;" />
            <h4>Total Outbound Value</h4>
            <div class='metric-number'>₱{total_value:,.0f}</div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
        <div class='hover-card'>
            <img src="https://cdn-icons-png.flaticon.com/128/3126/3126647.png" width="35" style="margin-bottom: 5px;" />
            <h4>Unique Customers</h4>
            <div class='metric-number'>{unique_customers}</div>
        </div>
        """, unsafe_allow_html=True)

    with col4:
        top_months_html = """
        <div class='hover-card'>
            <img src="https://cdn-icons-png.flaticon.com/128/16877/16877580.png" width="40" style="margin-bottom: 8px; display: block;" />
            <h4>Highest Outbound Months</h4>
        """
        for _, row in top_months.iterrows():
            top_months_html += f"""<div class='month-value-row'>
                <span class='month-left'>{row['Month_Year']}</span>
                <span class='month-right'>{int(row['QTY']):,} units</span>
            </div>"""
        top_months_html += "</div>"

        st.markdown(top_months_html, unsafe_allow_html=True)

    # --- Row 2: Expandable Dataframes Section
    spacer1, row2_col1, row2_col2, row2_col3, spacer2 = st.columns([0.19, 1.3, 0.5, 0.5, 0.3])

    with row2_col1:
        with st.container():
            with st.expander("🔍 View Outbound SKU, Quantity, and Price Details", expanded=False):
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
            with st.expander("🏆 Top 5 Customers", expanded=False):
                try:
                    top5_customers = (
                        filtered_df
                        .groupby("Customer Name")[["QTY"]]
                        .sum()
                        .sort_values(by="QTY", ascending=False)
                        .head(5)
                        .reset_index()
                    )
                    top5_customers = top5_customers.rename(columns={
                        "Customer Name": "Customer",
                        "QTY": "Total Qty",
                    })
                    st.data_editor(
                        top5_customers,
                        hide_index=True,
                        use_container_width=True
                    )
                except Exception as e:
                    st.error(f"Error loading customers table: {e}")

    with row2_col3:
        # No content for now (blank)
        pass

    st.divider()


    # 📊 Charts Layout: 2 Columns x 2 Rows + 1 Full
    col_left1, col_right1 = st.columns(2)

    with col_left1:
        st.subheader("📊 Sold per Main Category")
        if not filtered_df.empty:
            main_category_summary = (
                filtered_df.groupby("Main Category")["QTY"]
                .sum().reset_index().sort_values("QTY", ascending=False)
            )
            fig_main_cat = px.bar(main_category_summary, x="QTY", y="Main Category", orientation="h", text="QTY")
            st.plotly_chart(fig_main_cat, use_container_width=True)
        else:
            st.info("No data available.")

    with col_right1:
        st.subheader("🏭 Supplier with Most Units Sold")
        if not filtered_df.empty:
            supplier_summary = (
                filtered_df.groupby("Supplier Name")["QTY"]
                .sum().reset_index().sort_values("QTY", ascending=False)
            )
            fig_supplier = px.bar(supplier_summary, x="QTY", y="Supplier Name", orientation="h", text="QTY")
            st.plotly_chart(fig_supplier, use_container_width=True)
        else:
            st.info("No data available.")

    st.divider()

    col_left2, col_right2 = st.columns(2)

    with col_left2:
        st.subheader("💸 Top Customers by Value")
        if not filtered_df.empty:
            # Round the Total Value and convert to int for display
            top_customers_value["Total Value Rounded"] = top_customers_value["Total Value"].round(0).astype(int)

            fig_top_value = px.bar(
                top_customers_value,
                x="Total Value",
                y="Customer Name",
                orientation="h",
                text="Total Value Rounded"
            )

            # 🎯 Place text inside the bar and style it
            fig_top_value.update_traces(
                textposition='inside',
                insidetextanchor='start',  # or 'middle' or 'end' depending on your style
                textfont=dict(color='white')  # makes text visible on dark bar
            )

            fig_top_value.update_layout(
                xaxis_tickformat=',',  # Adds commas to x-axis ticks
                margin=dict(l=100, r=30, t=30, b=30)
            )

            st.plotly_chart(fig_top_value, use_container_width=True)
        else:
            st.info("No data available.")

    with col_right2:
        st.subheader("📋 Top Customers by Quantity")
        if not filtered_df.empty:
            fig_top_qty = px.bar(top_customers_qty, x="QTY", y="Customer Name", orientation="h", text="QTY")
            st.plotly_chart(fig_top_qty, use_container_width=True)
        else:
            st.info("No data available.")

    st.divider()

    # 📈 Customer and Item Relationship (Scatter - Full Width)
    st.subheader("📈 Customer and Item Relationship")
    if not filtered_df.empty:
        customer_item_summary = (
            filtered_df.groupby("Customer Name")
            .agg({"Description": "nunique", "QTY": "sum"})
            .reset_index()
            .rename(columns={"Description": "Unique Items", "QTY": "Total Qty"})
        )

        # Create the scatter plot
        fig_scatter = px.scatter(
            customer_item_summary,
            x="Customer Name", y="Unique Items",
            size="Total Qty",
            labels={
                "Unique Items": "No. of Different Items",
                "Customer Name": "Customer"
            },
            title="Customer vs No. of Items Ordered (Bubble Size = Total QTY)"
        )

        # 🔧 Improve layout and remove text clutter
        fig_scatter.update_layout(
            xaxis_tickangle=45,
            showlegend=False,
            margin=dict(t=40, b=80),
            height=500
        )
        fig_scatter.update_traces(text=None)

        st.plotly_chart(fig_scatter, use_container_width=True)
    else:
        st.info("No data available.")

    st.divider()
    
    # 📄 Full Outbound Table
    st.subheader("📄 Full Outbound Transactions")
    st.dataframe(filtered_df, use_container_width=True)