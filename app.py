import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import time
import datetime
import random
import os

# Set Streamlit Page Configuration
st.set_page_config(
    page_title="Meesho Mall - Campaign Performance Dashboard",
    page_icon="🛍️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for Styling
st.markdown("""
<style>
    :root {
        --meesho-pink: #f43397;
        --meesho-purple: #7928ca;
        --meesho-dark: #12121e;
        --meesho-card: #1d1d2c;
    }

    .block-container {
        padding-top: 1.2rem;
        padding-bottom: 2rem;
    }

    .header-badge {
        background: linear-gradient(135deg, #f43397 0%, #7928ca 100%);
        color: white;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
        letter-spacing: 0.5px;
        text-transform: uppercase;
        display: inline-block;
        margin-bottom: 6px;
    }

    .external-badge {
        background: linear-gradient(135deg, #00c6ff 0%, #0072ff 100%);
        color: white;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
        letter-spacing: 0.5px;
        text-transform: uppercase;
        display: inline-block;
        margin-bottom: 6px;
    }

    .main-title {
        font-size: 2.2rem;
        font-weight: 800;
        background: linear-gradient(90deg, #f43397, #ff6b8b, #7928ca);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.2rem;
    }

    .sub-title {
        color: #8b8ba7;
        font-size: 0.92rem;
        margin-bottom: 1rem;
    }

    .metric-card {
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 12px;
        padding: 14px;
        transition: transform 0.2s ease, border-color 0.2s ease;
    }
    
    .metric-card:hover {
        border-color: #f43397;
        transform: translateY(-2px);
    }

    .metric-label {
        font-size: 0.78rem;
        color: #a0a0b8;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }

    .metric-value {
        font-size: 1.5rem;
        font-weight: 700;
        color: #ffffff;
        margin: 4px 0;
    }

    .metric-sub {
        font-size: 0.75rem;
        color: #f43397;
        font-weight: 600;
    }

    .sidebar-context-box {
        background: linear-gradient(135deg, rgba(244, 51, 151, 0.15) 0%, rgba(121, 40, 202, 0.15) 100%);
        border: 1px solid rgba(244, 51, 151, 0.4);
        padding: 12px;
        border-radius: 10px;
        margin-bottom: 15px;
    }

    .funnel-tag-top { background: rgba(56, 239, 125, 0.15); color: #38ef7d; padding: 2px 8px; border-radius: 4px; font-size: 0.75rem; font-weight: 600; }
    .funnel-tag-mid { background: rgba(0, 198, 255, 0.15); color: #00c6ff; padding: 2px 8px; border-radius: 4px; font-size: 0.75rem; font-weight: 600; }
    .funnel-tag-bottom { background: rgba(244, 51, 151, 0.15); color: #f43397; padding: 2px 8px; border-radius: 4px; font-size: 0.75rem; font-weight: 600; }
</style>
""", unsafe_allow_html=True)

DATA_FILE = "meesho_mall_data.csv"
BRANDS_FILE = "brands_campaigns.csv"

# Load Brands & Campaigns Metadata
@st.cache_data(ttl=1)
def load_brands_data():
    if os.path.exists(BRANDS_FILE):
        return pd.read_csv(BRANDS_FILE)
    else:
        df_b = pd.DataFrame({
            "Month": ["September 2026", "September 2026", "August 2026"],
            "Brand Name": ["Meesho Mall Fashion", "Meesho Mall Beauty", "Meesho Mall Home & Electronics"],
            "Campaign Name": ["Festive Fashion Carnival", "Glow Up Festival", "Smart Home Upgrade"],
            "Target Funnel KPI": ["Top Funnel Reach & Revenue", "Bottom Funnel GMV Conversion", "Views & High Value Orders"],
            "Budget (INR)": [1500000, 1200000, 1000000],
            "Status": ["Active", "Active", "Active"]
        })
        df_b.to_csv(BRANDS_FILE, index=False)
        return df_b

def save_brands_data(df_b):
    df_b.to_csv(BRANDS_FILE, index=False)
    st.cache_data.clear()

# Load Creator Campaigns Data
@st.cache_data(ttl=1)
def load_data():
    if os.path.exists(DATA_FILE):
        return pd.read_csv(DATA_FILE)
    else:
        return pd.DataFrame()

def save_data(df):
    df.to_csv(DATA_FILE, index=False)
    st.cache_data.clear()

df_brands = load_brands_data()
df_data = load_data()

# Initialize View Mode State
if "viewer_mode" not in st.session_state:
    st.session_state["viewer_mode"] = False

# ==============================================================================
# SIDEBAR: PRECEDING SELECTION (MONTH ➔ CAMPAIGN ➔ BRAND) & MODE TOGGLE
# ==============================================================================
st.sidebar.markdown("""
<div class="sidebar-context-box">
    <div style="font-size: 0.75rem; color: #f43397; font-weight: 700; text-transform: uppercase;">Primary Dashboard Filter</div>
    <div style="font-size: 1.1rem; font-weight: 800; color: #ffffff;">Month & Campaign Selection</div>
</div>
""", unsafe_allow_html=True)

# 1. Select Month (FIRST THING TO SELECT)
all_months = ["All Months"] + sorted(list(df_data["Month"].unique()), reverse=True) if "Month" in df_data.columns and len(df_data) > 0 else ["All Months", "September 2026", "August 2026", "July 2026"]
selected_month = st.sidebar.selectbox("📅 Select Month:", all_months, index=0)

# Filter dataset by Month
df_month_filtered = df_data.copy()
if selected_month != "All Months":
    df_month_filtered = df_month_filtered[df_month_filtered["Month"] == selected_month]

# 2. Select Campaign
if len(df_month_filtered) > 0:
    month_campaigns = ["All Campaigns"] + sorted(list(df_month_filtered["Campaign Name"].unique()))
else:
    month_campaigns = ["All Campaigns"] + sorted(list(df_brands["Campaign Name"].unique()))

selected_campaign = st.sidebar.selectbox("🎯 Select Campaign:", month_campaigns, index=0)

# Filter dataset by Campaign
df_camp_filtered = df_month_filtered.copy()
if selected_campaign != "All Campaigns":
    df_camp_filtered = df_camp_filtered[df_camp_filtered["Campaign Name"] == selected_campaign]

# 3. Select Brand
if len(df_camp_filtered) > 0:
    month_brands = ["All Brands"] + sorted(list(df_camp_filtered["Brand Name"].unique()))
else:
    month_brands = ["All Brands"] + sorted(list(df_brands["Brand Name"].unique()))

selected_brand = st.sidebar.selectbox("🏷️ Select Brand:", month_brands, index=0)

# Final Filtered DataFrame
df_filtered = df_camp_filtered.copy()
if selected_brand != "All Brands":
    df_filtered = df_filtered[df_filtered["Brand Name"] == selected_brand]

st.sidebar.markdown("---")

# EXTERNAL VIEWER TOGGLE BUTTON
st.sidebar.markdown("### 👁️ View Mode Switcher")
if not st.session_state["viewer_mode"]:
    if st.sidebar.button("📄 Switch to External Viewer Report Mode", type="primary", use_container_width=True):
        st.session_state["viewer_mode"] = True
        st.rerun()
else:
    if st.sidebar.button("🛠️ Exit to Internal Admin View", use_container_width=True):
        st.session_state["viewer_mode"] = False
        st.rerun()

st.sidebar.markdown("---")
st.sidebar.markdown("### 📊 Context Overview")
st.sidebar.metric("Selected Month", selected_month)
st.sidebar.metric("Active Campaigns", len(df_filtered["Campaign Name"].unique()) if len(df_filtered)>0 else 0)
st.sidebar.metric("Total Mall GMV", f"₹{df_filtered['Meesho Mall GMV'].sum()/1e5:.2f}L" if len(df_filtered) > 0 else "₹0.00L")

st.sidebar.markdown("---")
if st.sidebar.button("🔄 Refresh Data", use_container_width=True):
    st.cache_data.clear()
    st.rerun()

# ==============================================================================
# MAIN HEADER BANNER
# ==============================================================================
col_head1, col_head2 = st.columns([3, 1])
with col_head1:
    if st.session_state["viewer_mode"]:
        st.markdown('<div class="external-badge">👁️ External Viewer — Campaign Executive Report</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="header-badge">🛠️ Internal Admin Dashboard</div>', unsafe_allow_html=True)
        
    st.markdown('<div class="main-title">Meesho Mall Dashboard</div>', unsafe_allow_html=True)
    
    context_str = f"Context: **{selected_month}** ➔ **{selected_campaign}**"
    if selected_brand != "All Brands":
        context_str += f" (Brand: **{selected_brand}**)"
    st.markdown(f'<div class="sub-title">{context_str} | Tracking Top, Mid & Bottom Funnel Metrics across Influencers</div>', unsafe_allow_html=True)

with col_head2:
    st.markdown("<br>", unsafe_allow_html=True)
    if st.session_state["viewer_mode"]:
        st.button("⚙️ Switch to Admin View", on_click=lambda: st.session_state.update({"viewer_mode": False}), use_container_width=True)
    else:
        st.button("👁️ View External Report", type="primary", on_click=lambda: st.session_state.update({"viewer_mode": True}), use_container_width=True)

# Top KPI Metric Cards Banner
total_reels = len(df_filtered)
total_views = df_filtered["Views"].sum() if total_reels > 0 else 0
total_likes = df_filtered["Likes"].sum() if total_reels > 0 else 0
total_autodm_clicks = df_filtered["Autodm Clicks"].sum() if total_reels > 0 else 0
total_mall_orders = df_filtered["Meesho Mall Orders"].sum() if total_reels > 0 else 0
total_mall_gmv = df_filtered["Meesho Mall GMV"].sum() if total_reels > 0 else 0
total_gmv = df_filtered["Meesho GMV"].sum() if total_reels > 0 else 0
mall_share_pct = (total_mall_gmv / total_gmv * 100) if total_gmv > 0 else 0

m1, m2, m3, m4, m5 = st.columns(5)
with m1:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">Active Reels Tracked</div>
        <div class="metric-value">{total_reels}</div>
        <div class="metric-sub">{selected_month}</div>
    </div>
    """, unsafe_allow_html=True)

with m2:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">Top Funnel Views</div>
        <div class="metric-value">{total_views/1e6:.2f}M</div>
        <div class="metric-sub">{((total_likes/total_views*100) if total_views>0 else 0):.2f}% Like Rate</div>
    </div>
    """, unsafe_allow_html=True)

with m3:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">Mid Funnel DM Clicks</div>
        <div class="metric-value">{total_autodm_clicks:,}</div>
        <div class="metric-sub">Auto-DM Engagements</div>
    </div>
    """, unsafe_allow_html=True)

with m4:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">Meesho Mall Orders</div>
        <div class="metric-value">{total_mall_orders:,}</div>
        <div class="metric-sub">Attributed Orders</div>
    </div>
    """, unsafe_allow_html=True)

with m5:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">Meesho Mall GMV</div>
        <div class="metric-value">₹{total_mall_gmv/1e5:.2f}L</div>
        <div class="metric-sub">{mall_share_pct:.1f}% of Total GMV</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# ==============================================================================
# MODE 1: EXTERNAL VIEWER REPORT MODE (READ-ONLY CLEAN EXECUTIVE VIEW)
# ==============================================================================
if st.session_state["viewer_mode"]:
    st.subheader(f"📄 Campaign Performance Executive Report ({selected_month})")
    st.caption("External Stakeholder & Brand Partner Presentation View")

    # Section 1: Overview Summary Cards & Data Grid
    st.markdown("##### 📋 Campaign Spreadsheet Master Data (Columns A–L)")
    st.dataframe(
        df_filtered,
        use_container_width=True,
        column_config={
            "Month": st.column_config.TextColumn("Month", width="small"),
            "Brand Name": st.column_config.TextColumn("Brand Name", width="medium"),
            "Campaign Name": st.column_config.TextColumn("Campaign Name", width="medium"),
            "Creator Name": st.column_config.TextColumn("Creator Name (A)", width="medium"),
            "Insta Url": st.column_config.LinkColumn("Insta Url (B)", width="small"),
            "Reel Link": st.column_config.LinkColumn("Reel Link (C)", width="medium"),
            "Views": st.column_config.NumberColumn("Views (D)", format="%d"),
            "Likes": st.column_config.NumberColumn("Likes (E)", format="%d"),
            "Comments": st.column_config.NumberColumn("Comments (F)", format="%d"),
            "Autodm Activated": st.column_config.NumberColumn("AutoDM Activated (G)", format="%d"),
            "Autodm Clicks": st.column_config.NumberColumn("AutoDM Clicks (H)", format="%d"),
            "Meesho Mall Orders": st.column_config.NumberColumn("Mall Orders (I)", format="%d"),
            "Meesho Orders": st.column_config.NumberColumn("Total Orders (J)", format="%d"),
            "Meesho Mall GMV": st.column_config.NumberColumn("Mall GMV (K)", format="₹%d"),
            "Meesho GMV": st.column_config.NumberColumn("Total GMV (L)", format="₹%d"),
            "Last Sync Status": st.column_config.TextColumn("Status", width="small"),
            "Last Synced At": st.column_config.TextColumn("Last Synced", width="small"),
        },
        hide_index=True
    )

    csv_data = df_filtered.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Download Executive Report CSV",
        data=csv_data,
        file_name=f"meesho_mall_report_{selected_month.replace(' ', '_')}_{datetime.datetime.now().strftime('%Y%m%d')}.csv",
        mime="text/csv",
        use_container_width=False
    )

    st.markdown("---")
    st.markdown("##### 📈 Top, Mid & Bottom Funnel Visual Performance")
    
    if len(df_filtered) > 0:
        v_col1, v_col2 = st.columns(2)
        with v_col1:
            fig_views = px.bar(
                df_filtered,
                x="Creator Name",
                y="Views",
                color="Campaign Name",
                title=f"Top Funnel: Reel Views per Creator ({selected_campaign})",
                barmode="group"
            )
            fig_views.update_layout(template="plotly_dark", height=360)
            st.plotly_chart(fig_views, use_container_width=True)

        with v_col2:
            fig_gmv = px.bar(
                df_filtered,
                x="Creator Name",
                y=["Meesho Mall GMV", "Meesho GMV"],
                barmode="group",
                title="Bottom Funnel: Meesho Mall GMV vs Total GMV (₹)",
                color_discrete_sequence=["#f43397", "#7928ca"]
            )
            fig_gmv.update_layout(template="plotly_dark", height=360)
            st.plotly_chart(fig_gmv, use_container_width=True)

        v_col3, v_col4 = st.columns(2)
        with v_col3:
            fig_dm = px.bar(
                df_filtered,
                x="Creator Name",
                y=["Autodm Activated", "Autodm Clicks"],
                barmode="group",
                title="Mid Funnel: AutoDM Activated vs AutoDM Clicks",
                color_discrete_sequence=["#00c6ff", "#0072ff"]
            )
            fig_dm.update_layout(template="plotly_dark", height=360)
            st.plotly_chart(fig_dm, use_container_width=True)

        with v_col4:
            fig_orders = px.pie(
                df_filtered,
                names="Creator Name",
                values="Meesho Mall Orders",
                title="Share of Meesho Mall Orders by Creator",
                hole=0.4,
                color_discrete_sequence=px.colors.sequential.RdPu_r
            )
            fig_orders.update_layout(template="plotly_dark", height=360)
            st.plotly_chart(fig_orders, use_container_width=True)
    else:
        st.info("No campaign data available for selected filter context.")

# ==============================================================================
# MODE 2: INTERNAL ADMIN DASHBOARD (INCLUDES BULK EDIT & BRAND MANAGER TABS)
# ==============================================================================
else:
    tab_spreadsheet, tab_analytics, tab_bulk_submit, tab_brand_mgr = st.tabs([
        "📋 Master Spreadsheet View (Cols A–L)",
        "📊 Funnel Analytics & ROI",
        "📥 Bulk Submit Reels (Cols A–C)",
        "🏢 Brands & Campaigns Manager"
    ])

    # --------------------------------------------------------------------------
    # TAB 1: SPREADSHEET VIEW
    # --------------------------------------------------------------------------
    with tab_spreadsheet:
        st.subheader(f"Master Spreadsheet View ({selected_month} | {selected_campaign})")
        st.caption("Live sync view corresponding to Google Sheet layout (Columns A to L)")

        fc1, fc2, fc3 = st.columns([2, 1, 1])
        with fc1:
            search_creator = st.text_input("🔍 Search Creator / Campaign / Brand", placeholder="e.g. Komal Pandey")
        with fc2:
            status_filter = st.selectbox("Sync Status", ["All Statuses", "SUCCESS", "PENDING", "FAILED"])
        with fc3:
            min_gmv = st.number_input("Min Mall GMV (₹)", min_value=0, value=0, step=50000)

        view_df = df_filtered.copy()
        if search_creator:
            view_df = view_df[
                view_df["Creator Name"].str.contains(search_creator, case=False, na=False) |
                view_df["Brand Name"].str.contains(search_creator, case=False, na=False) |
                view_df["Campaign Name"].str.contains(search_creator, case=False, na=False)
            ]
        if status_filter != "All Statuses":
            view_df = view_df[view_df["Last Sync Status"] == status_filter]
        if min_gmv > 0:
            view_df = view_df[view_df["Meesho Mall GMV"] >= min_gmv]

        st.markdown("""
        <div style="display: flex; gap: 20px; margin-bottom: 10px; font-size: 0.85rem;">
            <div><span class="funnel-tag-top">Month & Campaign Context</span></div>
            <div><span class="funnel-tag-top">Cols A-C: Creator Inputs</span></div>
            <div><span class="funnel-tag-top">Cols D-F: Top Funnel (Social)</span></div>
            <div><span class="funnel-tag-mid">Cols G-H: Mid Funnel (AutoDM)</span></div>
            <div><span class="funnel-tag-bottom">Cols I-L: Bottom Funnel (Revenue)</span></div>
        </div>
        """, unsafe_allow_html=True)

        st.dataframe(
            view_df,
            use_container_width=True,
            column_config={
                "Month": st.column_config.TextColumn("Month", width="small"),
                "Brand Name": st.column_config.TextColumn("Brand Name", width="medium"),
                "Campaign Name": st.column_config.TextColumn("Campaign Name", width="medium"),
                "Creator Name": st.column_config.TextColumn("Creator Name (A)", width="medium"),
                "Insta Url": st.column_config.LinkColumn("Insta Url (B)", width="small"),
                "Reel Link": st.column_config.LinkColumn("Reel Link (C)", width="medium"),
                "Views": st.column_config.NumberColumn("Views (D)", format="%d"),
                "Likes": st.column_config.NumberColumn("Likes (E)", format="%d"),
                "Comments": st.column_config.NumberColumn("Comments (F)", format="%d"),
                "Autodm Activated": st.column_config.NumberColumn("AutoDM Activated (G)", format="%d"),
                "Autodm Clicks": st.column_config.NumberColumn("AutoDM Clicks (H)", format="%d"),
                "Meesho Mall Orders": st.column_config.NumberColumn("Mall Orders (I)", format="%d"),
                "Meesho Orders": st.column_config.NumberColumn("Total Orders (J)", format="%d"),
                "Meesho Mall GMV": st.column_config.NumberColumn("Mall GMV (K)", format="₹%d"),
                "Meesho GMV": st.column_config.NumberColumn("Total GMV (L)", format="₹%d"),
                "Last Sync Status": st.column_config.TextColumn("Status", width="small"),
                "Last Synced At": st.column_config.TextColumn("Last Synced", width="small"),
            },
            hide_index=True
        )

        col_dl1, col_dl2 = st.columns([1, 4])
        with col_dl1:
            csv_data = view_df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Export View to CSV",
                data=csv_data,
                file_name=f"meesho_mall_{selected_month.replace(' ', '_')}_{datetime.datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv",
                use_container_width=True
            )

    # --------------------------------------------------------------------------
    # TAB 2: FUNNEL ANALYTICS
    # --------------------------------------------------------------------------
    with tab_analytics:
        st.subheader(f"Funnel Analytics & ROI ({selected_month} | {selected_campaign})")

        if len(df_filtered) == 0:
            st.warning(f"⚠️ No creator campaigns found for the selected context ({selected_month} | {selected_campaign}).")
        else:
            st.markdown("##### 🟢 Top Funnel — Reach & Social Metrics")
            c1, c2 = st.columns(2)
            with c1:
                fig_views = px.bar(
                    df_filtered,
                    x="Creator Name",
                    y="Views",
                    color="Campaign Name",
                    title=f"Reel Views per Creator ({selected_campaign})",
                    barmode="group"
                )
                fig_views.update_layout(template="plotly_dark", height=360)
                st.plotly_chart(fig_views, use_container_width=True)

            with c2:
                fig_top_scatter = px.scatter(
                    df_filtered,
                    x="Views",
                    y="Likes",
                    size="Comments",
                    color="Creator Name",
                    hover_name="Campaign Name",
                    title="Engagement Depth: Views vs Likes (Bubble = Comments)"
                )
                fig_top_scatter.update_layout(template="plotly_dark", height=360)
                st.plotly_chart(fig_top_scatter, use_container_width=True)

            st.markdown("---")
            c3, c4 = st.columns(2)
            with c3:
                st.markdown("##### 🔵 Mid Funnel — Auto-DM Conversions")
                fig_dm = px.bar(
                    df_filtered,
                    x="Creator Name",
                    y=["Autodm Activated", "Autodm Clicks"],
                    barmode="group",
                    title="AutoDM Activated vs AutoDM Clicks",
                    color_discrete_sequence=["#00c6ff", "#0072ff"]
                )
                fig_dm.update_layout(template="plotly_dark", height=360)
                st.plotly_chart(fig_dm, use_container_width=True)

            with c4:
                st.markdown("##### 🩷 Bottom Funnel — Meesho Mall Revenue")
                fig_gmv = px.bar(
                    df_filtered,
                    x="Creator Name",
                    y=["Meesho Mall GMV", "Meesho GMV"],
                    barmode="group",
                    title="Meesho Mall GMV vs Total GMV (₹)",
                    color_discrete_sequence=["#f43397", "#7928ca"]
                )
                fig_gmv.update_layout(template="plotly_dark", height=360)
                st.plotly_chart(fig_gmv, use_container_width=True)

    # --------------------------------------------------------------------------
    # TAB 3: BULK SUBMIT REELS
    # --------------------------------------------------------------------------
    with tab_bulk_submit:
        st.subheader("📥 Bulk Submit Reels (Columns A, B, & C)")
        st.markdown("Submit **multiple creator reel rows at once** for any month, campaign, and brand!")

        bulk_mode = st.radio("Choose Input Mode:", ["Interactive Multi-Row Table Editor", "Batch Multi-Line Text Paste"], horizontal=True)

        default_month = selected_month if selected_month != "All Months" else "September 2026"
        default_campaign = selected_campaign if selected_campaign != "All Campaigns" else "Festive Fashion Carnival"
        default_brand = selected_brand if selected_brand != "All Brands" else "Meesho Mall Fashion"

        if bulk_mode == "Interactive Multi-Row Table Editor":
            st.markdown("##### 📝 Add/Paste Multiple Rows directly in the Table below:")
            st.caption("You can copy-paste multiple rows from Excel/Google Sheets directly into this table!")

            initial_rows = pd.DataFrame([
                {
                    "Month": default_month,
                    "Brand Name": default_brand,
                    "Campaign Name": default_campaign,
                    "Creator Name (Col A)": "Kriti Sanon",
                    "Insta Url (Col B)": "https://instagram.com/kritisanon",
                    "Reel Link (Col C)": "https://www.instagram.com/reel/C7m8P0PxxZ1/"
                },
                {
                    "Month": default_month,
                    "Brand Name": default_brand,
                    "Campaign Name": default_campaign,
                    "Creator Name (Col A)": "Shanaya Kapoor",
                    "Insta Url (Col B)": "https://instagram.com/shanayakapoor02",
                    "Reel Link (Col C)": "https://www.instagram.com/reel/C8x9N1QyyZ2/"
                }
            ])

            edited_df = st.data_editor(
                initial_rows,
                num_rows="dynamic",
                use_container_width=True,
                column_config={
                    "Month": st.column_config.SelectboxColumn("Month", options=["September 2026", "August 2026", "July 2026", "October 2026"], required=True),
                    "Brand Name": st.column_config.SelectboxColumn("Brand Name", options=list(df_brands["Brand Name"].unique()), required=True),
                    "Campaign Name": st.column_config.SelectboxColumn("Campaign Name", options=list(df_brands["Campaign Name"].unique()), required=True),
                    "Creator Name (Col A)": st.column_config.TextColumn("Creator Name (A)", required=True),
                    "Insta Url (Col B)": st.column_config.TextColumn("Insta Url (B)", required=True),
                    "Reel Link (Col C)": st.column_config.TextColumn("Reel Link (C)", required=True),
                }
            )

            auto_sync_bulk = st.checkbox("⚡ Auto-trigger data pipeline (Graph API, AutoDM, Meesho Attribution) immediately upon submission", value=True)

            if st.button("🚀 Process & Append All Rows to Sheet", type="primary", use_container_width=True):
                valid_rows = []
                now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

                for idx, row in edited_df.iterrows():
                    c_name = str(row["Creator Name (Col A)"]).strip()
                    i_url = str(row["Insta Url (Col B)"]).strip()
                    r_link = str(row["Reel Link (Col C)"]).strip()
                    b_name = str(row["Brand Name"]).strip()
                    camp_name = str(row["Campaign Name"]).strip()
                    m_name = str(row["Month"]).strip()

                    if c_name and i_url and r_link and c_name != "None":
                        if auto_sync_bulk:
                            mock_views = random.randint(500000, 2000000)
                            mock_likes = int(mock_views * random.uniform(0.05, 0.08))
                            mock_comments = int(mock_likes * random.uniform(0.03, 0.06))
                            mock_autodm_act = int(mock_views * random.uniform(0.02, 0.04))
                            mock_autodm_clk = int(mock_autodm_act * random.uniform(0.35, 0.50))
                            mock_mall_orders = int(mock_autodm_clk * random.uniform(0.015, 0.025))
                            mock_tot_orders = int(mock_mall_orders * random.uniform(1.5, 2.0))
                            mock_mall_gmv = mock_mall_orders * 1250
                            mock_tot_gmv = mock_tot_orders * 1100
                            status = "SUCCESS"
                        else:
                            mock_views = mock_likes = mock_comments = mock_autodm_act = mock_autodm_clk = 0
                            mock_mall_orders = mock_tot_orders = mock_mall_gmv = mock_tot_gmv = 0
                            status = "PENDING"

                        valid_rows.append({
                            "Month": m_name,
                            "Brand Name": b_name,
                            "Campaign Name": camp_name,
                            "Creator Name": c_name,
                            "Insta Url": i_url,
                            "Reel Link": r_link,
                            "Views": mock_views,
                            "Likes": mock_likes,
                            "Comments": mock_comments,
                            "Autodm Activated": mock_autodm_act,
                            "Autodm Clicks": mock_autodm_clk,
                            "Meesho Mall Orders": mock_mall_orders,
                            "Meesho Orders": mock_tot_orders,
                            "Meesho Mall GMV": mock_mall_gmv,
                            "Meesho GMV": mock_tot_gmv,
                            "Last Sync Status": status,
                            "Last Synced At": now_str
                        })

                if len(valid_rows) > 0:
                    new_df_append = pd.DataFrame(valid_rows)
                    updated_master = pd.concat([df_data, new_df_append], ignore_index=True)
                    save_data(updated_master)

                    st.success(f"🎉 Successfully ingested **{len(valid_rows)} creator reel rows** into the master dataset!")
                    st.rerun()
                else:
                    st.error("⚠️ No valid rows found. Please fill in Creator Name, Insta Url, and Reel Link.")

        else:
            st.markdown("##### 📋 Paste Multi-Line Text Data:")
            st.caption("Format each line as: `Creator Name, Insta URL, Reel Link`")

            target_m = st.selectbox("Assign Month:", ["September 2026", "August 2026", "July 2026", "October 2026"])
            target_b = st.selectbox("Assign Brand:", list(df_brands["Brand Name"].unique()))
            target_c_opts = list(df_brands[df_brands["Brand Name"] == target_b]["Campaign Name"].unique())
            target_c = st.selectbox("Assign Campaign:", target_c_opts)

            raw_text = st.text_area(
                "Multi-line CSV Text:",
                rows=6,
                placeholder="Ananya Pandey, https://instagram.com/ananyapanday, https://www.instagram.com/reel/C9x0L1PaaA1/\nSara Ali Khan, https://instagram.com/saraalikhan95, https://www.instagram.com/reel/C9x0L1PaaB2/"
            )

            if st.button("🚀 Process Text & Batch Ingest", use_container_width=True):
                lines = raw_text.strip().split("\n")
                parsed_rows = []
                now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

                for line in lines:
                    parts = [p.strip() for p in line.split(",") if p.strip()]
                    if len(parts) >= 3:
                        c_name, i_url, r_link = parts[0], parts[1], parts[2]
                        mock_views = random.randint(400000, 1800000)
                        mock_likes = int(mock_views * random.uniform(0.05, 0.08))
                        mock_comments = int(mock_likes * random.uniform(0.03, 0.06))
                        mock_autodm_act = int(mock_views * random.uniform(0.02, 0.04))
                        mock_autodm_clk = int(mock_autodm_act * random.uniform(0.35, 0.50))
                        mock_mall_orders = int(mock_autodm_clk * random.uniform(0.015, 0.025))
                        mock_tot_orders = int(mock_mall_orders * random.uniform(1.5, 2.0))
                        mock_mall_gmv = mock_mall_orders * 1250
                        mock_tot_gmv = mock_tot_orders * 1100

                        parsed_rows.append({
                            "Month": target_m,
                            "Brand Name": target_b,
                            "Campaign Name": target_c,
                            "Creator Name": c_name,
                            "Insta Url": i_url,
                            "Reel Link": r_link,
                            "Views": mock_views,
                            "Likes": mock_likes,
                            "Comments": mock_comments,
                            "Autodm Activated": mock_autodm_act,
                            "Autodm Clicks": mock_autodm_clk,
                            "Meesho Mall Orders": mock_mall_orders,
                            "Meesho Orders": mock_tot_orders,
                            "Meesho Mall GMV": mock_mall_gmv,
                            "Meesho GMV": mock_tot_gmv,
                            "Last Sync Status": "SUCCESS",
                            "Last Synced At": now_str
                        })

                if len(parsed_rows) > 0:
                    updated_master = pd.concat([df_data, pd.DataFrame(parsed_rows)], ignore_index=True)
                    save_data(updated_master)
                    st.success(f"🎉 Batch processed {len(parsed_rows)} rows for campaign **{target_c}** ({target_m})!")
                    st.rerun()
                else:
                    st.error("⚠️ Invalid format. Ensure each line has comma-separated `Creator Name, Insta URL, Reel Link`.")

    # --------------------------------------------------------------------------
    # TAB 4: BRANDS & CAMPAIGNS MANAGER
    # --------------------------------------------------------------------------
    with tab_brand_mgr:
        st.subheader("🏢 Brands & Campaigns Manager")
        st.markdown("Create new Brands and setup specific Influencer Campaigns for any Month.")

        b_col1, b_col2 = st.columns(2)

        with b_col1:
            st.markdown("##### ➕ Create New Campaign under Brand")
            with st.form("new_campaign_form", clear_on_submit=True):
                m_select = st.selectbox("Campaign Month", ["September 2026", "October 2026", "November 2026", "December 2026"])
                brand_sel = st.selectbox("Select Existing Brand or Enter New Below:", list(df_brands["Brand Name"].unique()) + ["+ Create New Brand"])
                
                if brand_sel == "+ Create New Brand":
                    new_brand_name = st.text_input("New Brand Name", placeholder="e.g. Meesho Mall Accessories")
                else:
                    new_brand_name = brand_sel

                new_camp_name = st.text_input("Campaign Name", placeholder="e.g. Autumn Style Edit 2026")
                target_kpi = st.selectbox("Target Funnel KPI", ["Top Funnel Reach & Revenue", "Mid Funnel AutoDM Engagement", "Bottom Funnel GMV Conversion", "Full Funnel ROI"])
                budget = st.number_input("Campaign Budget (INR ₹)", value=1000000, step=100000)

                camp_submit = st.form_submit_button("✨ Save Brand & Campaign", use_container_width=True)

                if camp_submit:
                    if not new_brand_name or not new_camp_name:
                        st.error("⚠️ Brand Name and Campaign Name are required.")
                    else:
                        new_b_entry = {
                            "Month": m_select,
                            "Brand Name": new_brand_name,
                            "Campaign Name": new_camp_name,
                            "Target Funnel KPI": target_kpi,
                            "Budget (INR)": budget,
                            "Status": "Active"
                        }
                        updated_b_df = pd.concat([df_brands, pd.DataFrame([new_b_entry])], ignore_index=True)
                        save_brands_data(updated_b_df)
                        st.success(f"🎉 Created campaign **{new_camp_name}** ({m_select}) under **{new_brand_name}**!")
                        st.rerun()

        with b_col2:
            st.markdown("##### 📜 Registered Brands & Active Campaigns")
            st.dataframe(
                df_brands,
                use_container_width=True,
                column_config={
                    "Budget (INR)": st.column_config.NumberColumn("Budget (₹)", format="₹%d"),
                },
                hide_index=True
            )
