from dash import Dash, html, dcc, Input, Output
import plotly.express as px
import pandas as pd

# Load preprocessed dataset
df = pd.read_csv('cleaned_bikeshare.csv')

app = Dash(__name__)
app.title = "Ford GoBike Interactive Dashboard"

# Dropdown options
user_types = [{'label': x, 'value': x} for x in df['user_type'].dropna().unique()]
genders = [{'label': x, 'value': x} for x in df['member_gender'].dropna().unique()]
age_groups = [{'label': x, 'value': x} for x in df['age_group'].dropna().unique()]

card_style = {
    'backgroundColor': '#ffffff',
    'borderRadius': '10px',
    'padding': '15px 20px',
    'boxShadow': '0 2px 8px rgba(0,0,0,0.08)',
    'textAlign': 'center',
    'flex': '1',
    'margin': '5px'
}

app.layout = html.Div(style={'display': 'flex', 'fontFamily': 'Segoe UI, sans-serif', 'backgroundColor': '#f4f6f9', 'minHeight': '100vh'}, children=[
    
    # ----------------- SIDEBAR FILTERS -----------------
    html.Div(style={'width': '260px', 'backgroundColor': '#ffffff', 'padding': '25px 20px', 'boxShadow': '2px 0 8px rgba(0,0,0,0.05)'}, children=[
        html.H3("Filters", style={'color': '#1f2937', 'marginBottom': '20px'}),

        html.Label("User Type", style={'fontWeight': '600', 'color': '#4b5563'}),
        dcc.Dropdown(
            id='filter-user-type',
            options=user_types,
            value=[x['value'] for x in user_types],
            
        ),

        html.Label("Gender", style={'fontWeight': '600', 'color': '#4b5563'}),
        dcc.Dropdown(
            id='filter-gender',
            options=genders,
            value=[x['value'] for x in genders]
        ),

        html.Label("Age Group", style={'fontWeight': '600', 'color': '#4b5563'}),
        dcc.Dropdown(
            id='filter-age-group',
            options=age_groups,
            value=[x['value'] for x in age_groups]
        ),
    ]),

    # ----------------- MAIN CONTENT AREA -----------------
    html.Div(style={'flex': '1', 'padding': '25px 35px', 'overflowY': 'auto'}, children=[
        html.H2("Ford GoBike Interactive Dashboard", style={'color': '#111827', 'marginBottom': '20px'}),

        # SECTION 1: OVERVIEW KPIs
        html.H4("Overview KPIs", style={'color': '#374151', 'marginBottom': '10px'}),
        html.Div(style={'display': 'flex', 'gap': '15px', 'marginBottom': '25px'}, children=[
            html.Div(style=card_style, children=[
                html.H2(id='kpi-trips', style={'color': '#0284c7', 'margin': '0'}),
                html.Span("Trips", style={'color': '#6b7280', 'fontSize': '14px'})
            ]),
            html.Div(style=card_style, children=[
                html.H2(id='kpi-duration', style={'color': '#0f766e', 'margin': '0'}),
                html.Span("Avg Duration", style={'color': '#6b7280', 'fontSize': '14px'})
            ]),
            html.Div(style=card_style, children=[
                html.H2(id='kpi-bikes', style={'color': '#6366f1', 'margin': '0'}),
                html.Span("Active Bikes", style={'color': '#6b7280', 'fontSize': '14px'})
            ]),
        ]),

        # SECTION 2: TIME ANALYSIS (WEEKDAY ONLY)
        html.H4("Time Analysis", style={'color': '#374151', 'marginBottom': '10px'}),
        html.Div(style={'marginBottom': '25px'}, children=[
            html.Div(style={'backgroundColor': '#ffffff', 'padding': '15px', 'borderRadius': '10px', 'boxShadow': '0 2px 8px rgba(0,0,0,0.08)'}, children=[
                dcc.Graph(id='plot-weekday')
            ]),
        ]),

        # SECTION 3: USER ANALYSIS (USER TYPE & GENDER)
        html.H4("User Analysis", style={'color': '#374151', 'marginBottom': '10px'}),
        html.Div(style={'display': 'flex', 'gap': '15px'}, children=[
            html.Div(style={'flex': '1', 'backgroundColor': '#ffffff', 'padding': '15px', 'borderRadius': '10px', 'boxShadow': '0 2px 8px rgba(0,0,0,0.08)'}, children=[
                dcc.Graph(id='plot-user-type')
            ]),
            html.Div(style={'flex': '1', 'backgroundColor': '#ffffff', 'padding': '15px', 'borderRadius': '10px', 'boxShadow': '0 2px 8px rgba(0,0,0,0.08)'}, children=[
                dcc.Graph(id='plot-gender')
            ]),
        ]),
    ])
])

# ----------------- CALLBACK -----------------
@app.callback(
    Output('kpi-trips', 'children'),
    Output('kpi-duration', 'children'),
    Output('kpi-bikes', 'children'),
    Output('plot-weekday', 'figure'),
    Output('plot-user-type', 'figure'),
    Output('plot-gender', 'figure'),
    Input('filter-user-type', 'value'),
    Input('filter-gender', 'value'),
    Input('filter-age-group', 'value')
)
def update_dashboard(selected_users, selected_genders, selected_ages):
    dff = df[
        (df['user_type'].isin(selected_users or [])) &
        (df['member_gender'].isin(selected_genders or [])) &
        (df['age_group'].isin(selected_ages or []))
    ]

    total_trips = len(dff)
    if total_trips == 0:
        empty_fig = px.bar(title="No data available")
        return "0", "0 mins", "0", empty_fig, empty_fig, empty_fig

    # 1. KPIs
    trips_text = f"{total_trips:,}"
    avg_duration_text = f"{dff['duration_min'].mean():.1f} mins"
    active_bikes_text = f"{dff['bike_id'].nunique():,}"

    # 2. Weekday trend
    day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    day_counts = dff['day_of_week'].value_counts().reindex(day_order).fillna(0).reset_index()
    day_counts.columns = ['Day', 'Trips']
    fig_weekday = px.line(day_counts, x='Day', y='Trips', markers=True, title="Trips per Day of Week")
    fig_weekday.update_layout(margin=dict(l=20, r=20, t=40, b=20))

    # 3. User Type Donut chart
    fig_user = px.pie(
        dff, 
        names='user_type', 
        hole=0.45, 
        title="User Type Ratio",
        color_discrete_sequence=px.colors.qualitative.Set2
    )
    fig_user.update_layout(margin=dict(l=20, r=20, t=40, b=20))

    # 4. Gender distribution
    gender_counts = dff['member_gender'].value_counts().reset_index()
    gender_counts.columns = ['Gender', 'Count']
    fig_gender = px.bar(gender_counts, x='Gender', y='Count', color='Gender', title="Gender Distribution")
    fig_gender.update_layout(margin=dict(l=20, r=20, t=40, b=20), showlegend=False)

    return trips_text, avg_duration_text, active_bikes_text, fig_weekday, fig_user, fig_gender


if __name__ == '__main__':
    app.run(debug=True)