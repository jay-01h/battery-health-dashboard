from dash import Dash, dcc, html, Input, Output, State, MATCH
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.graph_objs as go
from datetime import datetime

# Load and preprocess data
df = pd.read_csv('battery_data.csv', parse_dates=['Time Stamp'])
df.rename(columns={'Time Stamp': 'timestamp'}, inplace=True)

METRICS = {
    'Voltage': 'Voltage (V)',
    'Current': 'Current (A)',
    'Temperature': 'Temperature (°C)',
    'Capacity': 'Capacity (Ah)',
    'WhAccu': 'Accumulated Wh'
}

# Initialize app
app = Dash(__name__, external_stylesheets=[dbc.themes.LUX])
server = app.server

# Navbar
navbar = dbc.Navbar(
    dbc.Container(
        dbc.NavbarBrand('Battery Health Dashboard', className='mx-auto',
                        style={'fontSize': '1.5rem', 'fontWeight': 'bold', 'color': 'white'}),
        fluid=True
    ),
    color='dark', dark=True, className='mb-4'
)

# Layout
app.layout = dbc.Container(fluid=True, children=[
    navbar,

    # Intro text with styling
    dbc.Row(dbc.Col(html.Div([
        html.P(
            "Welcome to the live monitoring dashboard for battery health across multiple packs. "
            "Analyze key metrics such as voltage, temperature, capacity, and more over time. "
            "Use the filters below to customize your view and gain insights into battery performance.",
            className="lead text-center", style={'fontSize': '1.2rem'}
        )
    ]), width=12), className='mb-4'),

    # Filters
    dbc.Row([
        dbc.Col([
            html.Label('Metrics to Plot:'),
            dcc.Dropdown(id='metric-dropdown',
                         options=[{'label': name, 'value': col} for col, name in METRICS.items()],
                         value=['Voltage', 'Capacity'],
                         multi=True)
        ], width=4, className='p-2'),
        dbc.Col([
            html.Label('Date Range:'),
            html.Br(),
            dcc.DatePickerRange(id='date-picker-range',
                                start_date=df['timestamp'].min().date(),
                                end_date=df['timestamp'].max().date(),
                                min_date_allowed=df['timestamp'].min().date(),
                                max_date_allowed=df['timestamp'].max().date(),
                                display_format='DD-MM-YYYY',
                                style={'width': '100%'},
                                className='p-2',
                                persistence=True,
                                
                                )
        ], width=4,className='p-2 text-center'),
        dbc.Col([
            html.Label('Last Updated:'),
            html.Div(id='last-updated', style={'fontWeight': 'bold'}),     
        ], width=3, className='p-2 text-end'),
    ], className='mb-4'),

    # KPIs
    dbc.Row([
        dbc.Col(dbc.Card(dbc.CardBody([
            html.H6('Avg Voltage', className='card-title'),
            html.H4(id='kpi-voltage', className='card-text')
        ]), color='info', inverse=True), width=4),
        dbc.Col(dbc.Card(dbc.CardBody([
            html.H6('Avg Temperature', className='card-title'),
            html.H4(id='kpi-temperature', className='card-text')
        ]), color='danger', inverse=True), width=4),
        dbc.Col(dbc.Card(dbc.CardBody([
            html.H6('Avg Capacity', className='card-title'),
            html.H4(id='kpi-capacity', className='card-text')
        ]), color='success', inverse=True), width=4)
    ], className='mb-4'),

    dcc.Interval(id='interval-component', interval=60 * 1000, n_intervals=0),

    # Graphs per battery pack
    *[
        dbc.Row(dbc.Col(dcc.Loading(dcc.Graph(
            id={'type': 'trend-graph', 'index': pack}
        ), type='default'), width=12), className='mb-5')
        for pack in sorted(df['battery_id'].unique())
    ],

    html.Hr(),
    dbc.Row(dbc.Col(html.Footer(
        'Jaydeep Hajare | PowerCo ', className='text-center text-muted'
    ), width=12))
])

# Helper function
def filter_df(start_date, end_date):
    mask = (
        (df['timestamp'] >= pd.to_datetime(start_date)) &
        (df['timestamp'] <= pd.to_datetime(end_date))
    )
    return df.loc[mask]

# KPI callback
@app.callback(
    [Output('kpi-voltage', 'children'),
     Output('kpi-temperature', 'children'),
     Output('kpi-capacity', 'children'),
     Output('last-updated', 'children')],
    [Input('date-picker-range', 'start_date'),
     Input('date-picker-range', 'end_date'),
     Input('interval-component', 'n_intervals')]
)
def update_kpis(start_date, end_date, n_intervals):
    filtered = filter_df(start_date, end_date)
    avg_v = f"{filtered['Voltage'].mean():.2f} V"
    avg_t = f"{filtered['Temperature'].mean():.2f} °C"
    avg_c = f"{filtered['Capacity'].mean():.2f} Ah"
    last_updated = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return avg_v, avg_t, avg_c, last_updated

# Graph callback
@app.callback(
    Output({'type': 'trend-graph', 'index': MATCH}, 'figure'),
    [Input('metric-dropdown', 'value'),
     Input('date-picker-range', 'start_date'),
     Input('date-picker-range', 'end_date'),
     Input('interval-component', 'n_intervals')],
    [State({'type': 'trend-graph', 'index': MATCH}, 'id')]
)
def update_trend_graph(selected_metrics, start_date, end_date, n_intervals, graph_id):
    pack = graph_id['index']
    filtered = filter_df(start_date, end_date)
    filtered = filtered[filtered['battery_id'] == pack]

    fig = go.Figure()
    for metric in selected_metrics:
        fig.add_trace(go.Scatter(
            x=filtered['timestamp'],
            y=filtered[metric],
            mode='lines+markers',
            name=METRICS.get(metric, metric)
        ))
    fig.update_layout(
        title=f'Pack {pack} Metrics Over Time',
        xaxis_title='Timestamp',
        yaxis_title='Value',
        template='plotly_white',
        legend_title='Metric',
        height=400
    )
    return fig

if __name__ == '__main__':
    app.run(debug=True)
