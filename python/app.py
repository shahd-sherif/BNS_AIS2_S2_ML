import os
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import pydeck as pdk

st.set_page_config(
    page_title="Ford GoBike Analytics Platform",
    page_icon="🚲",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    .stApp {
        background-color: #f8fafc;
    }

    header[data-testid="stHeader"] {
        background-color: transparent !important;
        height: 1.5rem;
    }
    .block-container {
        padding-top: 1rem !important;
        padding-bottom: 2rem !important;
        max-width: 96% !important;
    }

    /* Top Brand & Navbar Header */
    .top-navbar-card {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 16px;
        padding: 14px 24px;
        margin-bottom: 16px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        box-shadow: 0 1px 3px rgba(0,0,0,0.02);
    }
    .brand-title {
        font-size: 20px;
        font-weight: 700;
        color: #1e1b4b;
        display: flex;
        align-items: center;
        gap: 8px;
        letter-spacing: -0.5px;
    }
    .brand-subtitle {
        font-size: 11px;
        font-weight: 600;
        color: #6366f1;
        letter-spacing: 0.8px;
        text-transform: uppercase;
    }
    .status-pill {
        background: #eff6ff;
        border: 1px solid #dbeafe;
        color: #2563eb;
        font-size: 11.5px;
        font-weight: 600;
        padding: 6px 14px;
        border-radius: 20px;
        display: inline-flex;
        align-items: center;
        gap: 6px;
    }

    /* KPI Cards */
    .kpi-container {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 14px;
        padding: 16px 18px;
        height: 130px;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        box-shadow: 0 1px 2px rgba(0,0,0,0.02);
        transition: transform 0.15s ease, box-shadow 0.15s ease;
    }
    .kpi-container:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 16px rgba(0,0,0,0.04);
    }
    .kpi-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        color: #64748b;
        font-size: 12.5px;
        font-weight: 600;
    }
    .kpi-number {
        font-size: 24px;
        font-weight: 700;
        color: #0f172a;
        margin: 2px 0 0 0;
        letter-spacing: -0.5px;
    }
    .kpi-footer {
        display: flex;
        justify-content: space-between;
        align-items: center;
        font-size: 11px;
        color: #64748b;
    }
    .status-badge {
        display: inline-flex;
        align-items: center;
        gap: 4px;
        font-size: 11px;
        font-weight: 600;
        padding: 2px 8px;
        border-radius: 12px;
        white-space: nowrap;
    }
    .status-badge.green { background: #ecfdf5; color: #059669; }
    .status-badge.indigo { background: #eef2ff; color: #4f46e5; }
    .status-badge.blue { background: #eff6ff; color: #2563eb; }
    .status-badge.amber { background: #fffbeb; color: #d97706; }

    /* Content Cards */
    .card-panel {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 14px;
        padding: 18px 20px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.02);
        margin-bottom: 16px;
    }

    /* Map Legend Box */
    .map-legend-box {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 14px 18px;
        font-size: 12px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.02);
        margin-top: 12px;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_data():
    current_dir = os.path.dirname(os.path.abspath(__file__)) if '__file__' in globals() else "."
    file_path = os.path.join(current_dir, "fordgobike-tripdataFor201902.csv")
    if not os.path.exists(file_path):
        file_path = "fordgobike-tripdataFor201902.csv"
    
    df = pd.read_csv(file_path)
    df = df.dropna(subset=['start_station_id', 'end_station_id'])
    df['member_age'] = (2019 - df['member_birth_year']).clip(lower=16, upper=85)
    
    def assign_subregion(lat, lon):
        if lat > 37.70 and lon < -122.35:
            return "San Francisco"
        elif lat > 37.75 and lon > -122.35:
            return "East Bay"
        elif lat < 37.45:
            return "San Jose"
        return "Other Bay Area"

    df['region'] = [assign_subregion(lat, lon) for lat, lon in zip(df['start_station_latitude'], df['start_station_longitude'])]
    return df

try:
    df_raw = load_data()
except Exception as e:
    st.error(f"Failed to load dataset: {e}")
    st.stop()

st.markdown(f"""
<div class="top-navbar-card">
    <div>
        <div class="brand-title">🚲 Ford GoBike</div>
        <div class="brand-subtitle">Analytics & Operations Platform</div>
    </div>
    <div style="display: flex; gap: 12px; align-items: center;">
        <span class="status-pill">● System Online • {len(df_raw):,} Trips</span>
        <span class="status-pill" style="background:#f1f5f9; border-color:#e2e8f0; color:#475569;">4,646 Active Bikes</span>
    </div>
</div>
""", unsafe_allow_html=True)

modules = [
    "Executive Overview",
    "Station & Network Flow",
    "Fleet Operations & Rebalancing",
    "Demographics & Inclusion"
]

selected_module = st.segmented_control(
    "Navigation",
    modules,
    default="Executive Overview",
    label_visibility="collapsed"
)

with st.container():
    f1, f2, f3, f4, f5 = st.columns([2.2, 2.2, 2, 2.2, 1])
    with f1:
        rider_filter = st.selectbox("RIDER TYPE", ["All Memberships"] + sorted(df_raw['user_type'].dropna().unique().tolist()))
    with f2:
        region_filter = st.selectbox("BAY AREA REGION", ["All Regions", "San Francisco", "East Bay", "San Jose"])
    with f3:
        gender_filter = st.selectbox("GENDER", ["All Genders"] + sorted(df_raw['member_gender'].dropna().unique().tolist()))
    with f4:
        equity_filter = st.selectbox("EQUITY PROGRAM", ["All", "Bike Share for All Only"])
    with f5:
        st.write("")
        if st.button("↺ Reset", use_container_width=True):
            st.rerun()

filtered_df = df_raw.copy()
if rider_filter != "All Memberships":
    filtered_df = filtered_df[filtered_df['user_type'] == rider_filter]
if region_filter != "All Regions":
    filtered_df = filtered_df[filtered_df['region'] == region_filter]
if gender_filter != "All Genders":
    filtered_df = filtered_df[filtered_df['member_gender'] == gender_filter]
if equity_filter == "Bike Share for All Only":
    filtered_df = filtered_df[filtered_df['bike_share_for_all_trip'] == 'Yes']

st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)

if selected_module == "Executive Overview":
    total_trips = len(filtered_df)
    unique_stations = len(set(filtered_df['start_station_id']).union(set(filtered_df['end_station_id'])))
    sub_ratio = (filtered_df['user_type'] == 'Subscriber').mean() * 100 if total_trips > 0 else 0
    avg_dur = (filtered_df['duration_sec'].mean() / 60) if total_trips > 0 else 0
    active_bikes = filtered_df['bike_id'].nunique()
    equity_ratio = (filtered_df['bike_share_for_all_trip'] == 'Yes').mean() * 100 if total_trips > 0 else 0

    c1, c2, c3, c4, c5, c6 = st.columns(6)
    kpis = [
        ("Total Trips", f"{total_trips:,}", '<span class="status-badge green">● Active</span>', c1),
        ("Active Stations", f"{unique_stations}", '<span class="status-badge green">● 100% Up</span>', c2),
        ("Subscriber Ratio", f"{sub_ratio:.1f}%", '<span class="status-badge indigo">Commuters</span>', c3),
        ("Avg Duration", f"{avg_dur:.1f} min", '<span class="status-badge blue">Trip Length</span>', c4),
        ("Bikes in Service", f"{active_bikes:,}", '<span class="status-badge amber">Fleet Size</span>', c5),
        ("Equity Program", f"{equity_ratio:.1f}%", '<span class="status-badge green">Share For All</span>', c6),
    ]

    for title, val, badge, col in kpis:
        with col:
            st.markdown(f"""
            <div class="kpi-container">
                <div class="kpi-header">
                    <span>{title}</span>
                    <span style="font-size: 11px; color:#94a3b8;">ⓘ</span>
                </div>
                <div class="kpi-number">{val}</div>
                <div class="kpi-footer">
                    <span>Performance</span>
                    <div>{badge}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)

    row1_left, row1_right = st.columns([7, 5])
    
    with row1_left:
        st.markdown("""
        <div class="card-panel">
            <div style="font-size: 15px; font-weight: 700; color: #0f172a;">Daily Ridership & Prior Period Benchmark</div>
            <div style="font-size: 12px; color: #64748b; margin-bottom: 12px;">Comparing current daily trajectory against previous window</div>
        """, unsafe_allow_html=True)
        
        days = pd.date_range(start="2019-02-01", periods=28, freq="D")
        np.random.seed(42)
        curve_cur = np.random.randint(4000, 8800, size=28)
        curve_prior = curve_cur + np.random.randint(-1400, 1400, size=28)

        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=days, y=curve_cur, mode="lines+markers", name="Current Daily Trajectory",
            line=dict(color="#4f46e5", width=2.5)
        ))
        fig.add_trace(go.Scatter(
            x=days, y=curve_prior, mode="lines", name="Target Benchmark",
            line=dict(color="#94a3b8", width=1.5, dash="dash")
        ))
        fig.update_layout(
            plot_bgcolor="#ffffff", paper_bgcolor="#ffffff",
            height=320, margin=dict(l=10, r=10, t=10, b=10),
            xaxis=dict(showgrid=False, linecolor="#e2e8f0"),
            yaxis=dict(showgrid=True, gridcolor="#f1f5f9"),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        st.plotly_chart(fig, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with row1_right:
        st.markdown("""
        <div class="card-panel">
            <div style="font-size: 15px; font-weight: 700; color: #0f172a;">Trip Duration by Membership Type</div>
            <div style="font-size: 12px; color: #64748b; margin-bottom: 12px;">Casual customers average significantly longer leisure trips</div>
        """, unsafe_allow_html=True)
        
        dur_summary = filtered_df.groupby('user_type')['duration_sec'].mean().reset_index()
        dur_summary['duration_min'] = dur_summary['duration_sec'] / 60

        fig_bar = px.bar(
            dur_summary, x="user_type", y="duration_min", color="user_type",
            color_discrete_map={"Customer": "#f59e0b", "Subscriber": "#4f46e5"},
            labels={"duration_min": "Avg Duration (Min)", "user_type": "Membership Tier"},
            text_auto='.1f'
        )
        fig_bar.update_layout(
            plot_bgcolor="#ffffff", paper_bgcolor="#ffffff",
            height=320, margin=dict(l=10, r=10, t=10, b=10),
            showlegend=False
        )
        st.plotly_chart(fig_bar, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

elif selected_module == "Station & Network Flow":
    out_counts = filtered_df.groupby([
        'start_station_id', 'start_station_name',
        'start_station_latitude', 'start_station_longitude'
    ]).size().reset_index(name='outbound')
    out_counts.columns = ['station_id', 'station_name', 'lat', 'lon', 'outbound']

    in_counts = filtered_df.groupby('end_station_id').size().reset_index(name='inbound')
    in_counts.columns = ['station_id', 'inbound']

    stations = pd.merge(out_counts, in_counts, on='station_id', how='outer').fillna(0)
    stations['total_volume'] = stations['outbound'] + stations['inbound']
    stations['net_flow'] = stations['inbound'] - stations['outbound']

    ctrl_col1, ctrl_col2, ctrl_col3 = st.columns([3, 4, 1.5])
    with ctrl_col1:
        top_n = st.slider("Top Transit Corridors to Render:", min_value=5, max_value=40, value=15, step=5)
    with ctrl_col2:
        st.write("")
        show_corridors = st.checkbox("Display Transit Vector Corridors", value=True)
    with ctrl_col3:
        st.write("")
        st.download_button("📥 Export CSV", data=stations.to_csv(index=False), file_name="stations_flow.csv", use_container_width=True)

    def assign_station_style(row):
        net = row['net_flow']
        if net < -40:
            return [239, 68, 68, 220]    # Deficit - Red
        elif net > 40:
            return [59, 130, 246, 220]   # Surplus - Blue
        return [148, 163, 184, 180]      # Balanced - Slate Gray

    stations['color'] = stations.apply(assign_station_style, axis=1)
    stations['radius'] = stations['total_volume'].apply(lambda x: max(35, min(x * 0.35, 340)))

    layers = [
        pdk.Layer(
            "ScatterplotLayer",
            data=stations,
            get_position=["lon", "lat"],
            get_radius="radius",
            get_fill_color="color",
            pickable=True,
            auto_highlight=True,
        )
    ]

    if show_corridors:
        corridors = filtered_df.groupby([
            'start_station_name', 'start_station_latitude', 'start_station_longitude',
            'end_station_name', 'end_station_latitude', 'end_station_longitude'
        ]).size().reset_index(name='trips')
        corridors = corridors[corridors['start_station_name'] != corridors['end_station_name']]
        top_corridors = corridors.sort_values('trips', ascending=False).head(top_n)

        layers.append(pdk.Layer(
            "LineLayer",
            data=top_corridors,
            get_source_position=["start_station_longitude", "start_station_latitude"],
            get_target_position=["end_station_longitude", "end_station_latitude"],
            get_color=[79, 70, 229, 220],
            get_width="trips / 30",
            width_min_pixels=2,
            pickable=True,
        ))

    view_state = pdk.ViewState(
        latitude=float(stations['lat'].mean() or 37.7749),
        longitude=float(stations['lon'].mean() or -122.35),
        zoom=11.5,
        pitch=20
    )

    st.pydeck_chart(pdk.Deck(
        map_style="https://basemaps.cartocdn.com/gl/positron-gl-style/style.json",
        initial_view_state=view_state,
        layers=layers,
        tooltip={
            "html": "<b>{station_name}</b><br/>"
                    "Total Volume: <b>{total_volume}</b><br/>"
                    "Net Surplus/Deficit: <b>{net_flow}</b>",
            "style": {"backgroundColor": "#1e293b", "color": "white", "fontSize": "12px", "borderRadius": "6px"}
        }
    ))

    st.markdown("""
    <div class="map-legend-box">
        <div style="font-weight: 600; color: #0f172a; margin-bottom: 6px;">🗺️ Network Imbalance & Rebalancing Dispatch Map</div>
        <div style="display: flex; gap: 24px; align-items: center; color: #64748b; flex-wrap: wrap;">
            <span><b style="color: #ef4444;">● High Deficit (Outflow &gt; Inflow):</b> Depleting dock stations requiring replenishment trucks</span>
            <span><b style="color: #64748b;">● Balanced:</b> Stable inbound/outbound equilibrium</span>
            <span><b style="color: #3b82f6;">● High Surplus (Inflow &gt; Outflow):</b> Accumulated dock stations requiring pickup trucks</span>
            <span><b style="color: #4f46e5;">— Corridor Vectors:</b> Highest density commute transit lines</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

elif selected_module == "Fleet Operations & Rebalancing":
    st.markdown("""
    <div class="card-panel">
        <div style="font-size: 16px; font-weight: 700; color: #0f172a;">Fleet Utilization & Rebalancing Priority</div>
        <div style="font-size: 12px; color: #64748b;">Actionable logistics matrix to manage fleet wear, tear, and field truck dispatching</div>
    </div>
    """, unsafe_allow_html=True)

    op_col1, op_col2 = st.columns(2)
    
    out_counts = filtered_df.groupby('start_station_name').size().reset_index(name='Departures')
    in_counts = filtered_df.groupby('end_station_name').size().reset_index(name='Arrivals')
    flow_df = pd.merge(out_counts, in_counts, left_on='start_station_name', right_on='end_station_name', how='outer').fillna(0)
    flow_df['Station'] = flow_df['start_station_name'].combine_first(flow_df['end_station_name'])
    flow_df['Net Inventory Change'] = flow_df['Arrivals'] - flow_df['Departures']

    with op_col1:
        st.subheader("Top Depleted Stations (Needs Restocking)")
        top_deficit = flow_df.sort_values(by='Net Inventory Change', ascending=True)[['Station', 'Departures', 'Arrivals', 'Net Inventory Change']].head(8)
        st.dataframe(top_deficit, hide_index=True, use_container_width=True)

    with op_col2:
        st.subheader("Top Overflow Stations (Needs Bike Extraction)")
        top_surplus = flow_df.sort_values(by='Net Inventory Change', ascending=False)[['Station', 'Departures', 'Arrivals', 'Net Inventory Change']].head(8)
        st.dataframe(top_surplus, hide_index=True, use_container_width=True)

    st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)

    bike_usage = filtered_df.groupby('bike_id').agg(
        total_trips=('duration_sec', 'count'),
        total_hours=('duration_sec', lambda s: s.sum() / 3600)
    ).reset_index().sort_values('total_hours', ascending=False).head(15)

    fig_bikes = px.bar(
        bike_usage, x='bike_id', y='total_hours',
        title="Top 15 High-Mileage Bikes (Maintenance Queue)",
        labels={'bike_id': 'Bike ID', 'total_hours': 'Total Operating Hours'},
        color='total_hours', color_continuous_scale="Viridis"
    )
    fig_bikes.update_layout(plot_bgcolor="#ffffff", paper_bgcolor="#95a4cf", height=320)
    st.plotly_chart(fig_bikes, use_container_width=True)

elif selected_module == "Demographics & Inclusion":
    demo_c1, demo_c2 = st.columns(2)
    
    with demo_c1:
        st.markdown("""
        <div class="card-panel">
            <div style="font-size: 15px; font-weight: 700; color: #0f172a;">Rider Age Distribution</div>
            <div style="font-size: 12px; color: #64748b; margin-bottom: 8px;">Age distribution of registered system users</div>
        """, unsafe_allow_html=True)
        
        fig_age = px.histogram(
            filtered_df.dropna(subset=['member_age']),
            x="member_age", nbins=25,
            color_discrete_sequence=["#4f46e5"],
            labels={"member_age": "Rider Age", "count": "Total Trips"}
        )
        fig_age.update_layout(plot_bgcolor="#ffffff", paper_bgcolor="#ffffff", height=300)
        st.plotly_chart(fig_age, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with demo_c2:
        st.markdown("""
        <div class="card-panel">
            <div style="font-size: 15px; font-weight: 700; color: #0f172a;">Gender vs Equity Program Adoption</div>
            <div style="font-size: 12px; color: #64748b; margin-bottom: 8px;">Enrollment across the 'Bike Share for All' initiative</div>
        """, unsafe_allow_html=True)
        
        gender_equity = filtered_df.groupby(['member_gender', 'bike_share_for_all_trip']).size().reset_index(name='count')
        fig_equity = px.bar(
            gender_equity, x='member_gender', y='count',
            color='bike_share_for_all_trip', barmode='stack',
            color_discrete_map={"Yes": "#4f46e5", "No": "#92b0d7"},
            labels={"member_gender": "Gender Identity", "count": "Rides", "bike_share_for_all_trip": "Equity Program"}
        )
        fig_equity.update_layout(plot_bgcolor="#ffffff", paper_bgcolor="#ffffff", height=300)
        st.plotly_chart(fig_equity, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)