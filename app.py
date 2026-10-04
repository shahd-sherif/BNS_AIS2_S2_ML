import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

# --- 1. إعدادات الصفحة ---
st.set_page_config(
    page_title="Ford GoBike Analytics",
    page_icon="🚲",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 2. تخصيص التنسيق (CSS) لمطابقة تصميم الصورة ---
st.markdown("""
<style>
    /* القائمة الجانبية الداكنة */
    [data-testid="stSidebar"] {
        background-color: #0d1b2a;
        color: #ffffff;
    }
    [data-testid="stSidebar"] * {
        color: #e0e1dd !important;
    }
    
    /* خلفية الصفحة الرئيسية */
    .stApp {
        background-color: #f8fafc;
    }
    
    /* بطاقات مؤشرات الأداء (KPI Cards) */
    .kpi-card {
        background: #ffffff;
        border-radius: 12px;
        padding: 16px 20px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.06);
        border: 1px solid #e2e8f0;
        margin-bottom: 12px;
    }
    .kpi-title {
        font-size: 13px;
        color: #64748b;
        font-weight: 500;
        margin-bottom: 6px;
    }
    .kpi-value {
        font-size: 26px;
        font-weight: 700;
        color: #0f172a;
    }
    .kpi-sub {
        font-size: 12px;
        color: #94a3b8;
        margin-top: 4px;
    }
    
    /* بطاقات الرؤى النصية (Insight Cards) */
    .insight-card {
        background: #ffffff;
        border-radius: 10px;
        padding: 14px;
        margin-bottom: 12px;
        border: 1px solid #e2e8f0;
    }
    .insight-title {
        font-size: 14px;
        font-weight: 600;
        color: #1e293b;
        display: flex;
        align-items: center;
        gap: 6px;
    }
    .insight-desc {
        font-size: 12px;
        color: #64748b;
        margin-top: 5px;
        line-height: 1.4;
    }
</style>
""", unsafe_allow_html=True)

# --- 3. تجهيز بيانات وهمية تحاكي الداتا الفعلية ---
@st.cache_data
def load_data():
    dates = pd.date_range(end=pd.Timestamp.today(), periods=30)
    current_rides = np.random.randint(3000, 9000, size=30)
    prior_rides = current_rides + np.random.randint(-1500, 1500, size=30)
    
    df = pd.DataFrame({
        "date": dates,
        "current_period": current_rides,
        "prior_week": prior_rides
    })
    return df

df = load_data()

# --- 4. القائمة الجانبية (Sidebar) ---
with st.sidebar:
    st.markdown("### 🚲 Ford GoBike")
    st.caption("ANALYTICS PLATFORM")
    st.markdown("---")
    
    selected_module = st.radio(
        "ANALYTICS MODULES",
        [
            "📊 Executive Overview",
            "🗺️ Station & Network Flow",
            "👥 Time & Rider Demographics",
            "📈 Rider & Trip Dynamics"
        ],
        index=0
    )
    
    st.markdown("<br><br><br><br>", unsafe_allow_html=True)
    st.success("🟢 Supabase Cloud\n\n174.7k trips loaded")

# --- 5. شريط الفلاتر العلوي ---
st.markdown("#### Ford GoBike Analytics > **Executive Overview**")

filter_cols = st.columns([2, 2, 2, 2, 2, 1])
with filter_cols[0]:
    time_filter = st.selectbox("TIME", ["ALL", "7D", "30D", "90D"])
with filter_cols[1]:
    rider_filter = st.selectbox("RIDER", ["All Memberships", "Subscriber", "Customer"])
with filter_cols[2]:
    region_filter = st.selectbox("REGION", ["All Bay Area", "San Francisco", "San Jose", "East Bay"])
with filter_cols[3]:
    gender_filter = st.selectbox("GENDER", ["All Genders", "Male", "Female", "Other"])
with filter_cols[4]:
    day_filter = st.selectbox("DAY", ["All Days", "Weekday", "Weekend"])
with filter_cols[5]:
    st.write("")
    st.write("")
    if st.button("🔄 Reset"):
        st.experimental_rerun()

st.markdown("---")

# --- 6. بطاقات المؤشرات (KPI Cards) ---
kpi_cols = st.columns(6)

metrics = [
    {"title": "Total Trips", "val": "174,724", "sub": "🟢 Active"},
    {"title": "Active Stations", "val": "329", "sub": "Operational"},
    {"title": "Subscriber Ratio", "val": "90.5%", "sub": "90.5% vs 9.5%"},
    {"title": "Average Trip Duration", "val": "11.7 min", "sub": "Commute range"},
    {"title": "Peak Commute", "val": "17:00", "sub": "Evening rush (PM Peak)"},
    {"title": "Rebalance Alerts", "val": "11", "sub": "⚠️ Needs Van Dispatch"}
]

for col, m in zip(kpi_cols, metrics):
    with col:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-title">{m['title']}</div>
            <div class="kpi-value">{m['val']}</div>
            <div class="kpi-sub">{m['sub']}</div>
        </div>
        """, unsafe_allow_html=True)

# --- 7. المخطط البياني والتحليلات النصية (Insights) ---
main_col, insights_col = st.columns([2.2, 1])

with main_col:
    st.markdown("##### Daily Ridership & Prior Period Benchmark")
    st.caption("Comparing current daily trajectory against previous corresponding window")
    
    # رسم بياني تفاعلي باستخدام Plotly
    fig = go.Figure()
    
    # خط الفترة الحالية (متصل وأخضر)
    fig.add_trace(go.Scatter(
        x=df["date"],
        y=df["current_period"],
        mode="lines",
        name="Current Period",
        line=dict(color="#00a896", width=2.5)
    ))
    
    # خط الفترة السابقة (متقطع ورمادي)
    fig.add_trace(go.Scatter(
        x=df["date"],
        y=df["prior_week"],
        mode="lines",
        name="Prior Week (Same Day)",
        line=dict(color="#94a3b8", width=1.5, dash="dash")
    ))
    
    fig.update_layout(
        plot_bgcolor="#ffffff",
        paper_bgcolor="#ffffff",
        margin=dict(l=20, r=20, t=20, b=20),
        xaxis=dict(showgrid=False, linecolor="#cbd5e1"),
        yaxis=dict(showgrid=True, gridcolor="#f1f5f9"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        height=380
    )
    st.plotly_chart(fig, use_container_width=True)

with insights_col:
    st.markdown("##### Computed System Insights `REAL-TIME`")
    st.caption("Synthesized algorithmically from current slice of trip records.")
    
    insights = [
        {
            "icon": "📅",
            "title": "Weekly Commute Crest",
            "desc": "Thursday dominates peak throughput, registering 18.6% higher trip density than the 7-day median."
        },
        {
            "icon": "🚐",
            "title": "Fleet Redistribution Demand",
            "desc": "11 critical stations require van dispatch (|net flow| >= 200 rides) to restore bay capacity."
        },
        {
            "icon": "👤",
            "title": "Subscription Dominance",
            "desc": "Subscribers account for 90.5% of total volume with an average duration of 11.7 min, reflecting utility commuting."
        },
        {
            "icon": "🎯",
            "title": "Rider Cohort Dynamic",
            "desc": "Casual riders display 2.0x longer duration (21.7m vs 10.7m) for recreational exploration."
        }
    ]
    
    for item in insights:
        st.markdown(f"""
        <div class="insight-card">
            <div class="insight-title">{item['icon']} {item['title']}</div>
            <div class="insight-desc">{item['desc']}</div>
        </div>
        """, unsafe_allow_html=True)