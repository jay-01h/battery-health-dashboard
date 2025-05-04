from dash import Dash, dcc, html, Input, Output, State
import dash_bootstrap_components as dbc
import plotly.graph_objs as go
import requests
import pandas as pd
from datetime import datetime

# App Initialization
app = Dash(__name__, external_stylesheets=[dbc.themes.FLATLY])
server = app.server  # for deployment

# List of crypto coins to track
coins = {
    "bitcoin": "Bitcoin",
    "ethereum": "Ethereum",
    "solana": "Solana",
    "ripple": "XRP",
    "litecoin": "Litecoin"
}

def fetch_coin_data(coin_id):
    url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart?vs_currency=usd&days=30"
    response = requests.get(url)
    if response.status_code == 200:
        prices = response.json()['prices']
        df = pd.DataFrame(prices, columns=['timestamp', 'price'])
        df['date'] = pd.to_datetime(df['timestamp'], unit='ms')
        return df[['date', 'price']]
    else:
        return pd.DataFrame(columns=['date', 'price'])

# Navbar
navbar = dbc.NavbarSimple(
    brand="Crypto Trends Dashboard",
    color="primary",
    dark=True,
    className="mb-4"
)

# App Layout
app.layout = dbc.Container([
    navbar,
    dbc.Row([
        dbc.Col([
            html.H5("Select Cryptocurrencies to Compare:"),
            dcc.Dropdown(
                id='coin-dropdown',
                options=[{"label": name, "value": coin} for coin, name in coins.items()],
                value=["bitcoin", "ethereum"],
                multi=True,
                className="mb-4"
            ),
            dbc.Button("Refresh Data", id="refresh-button", color="info", className="mb-4")
        ], width=12)
    ]),
    dbc.Row([
        dbc.Col(dcc.Loading(
            dcc.Graph(id='price-graph'),
            type="circle"
        ), width=12)
    ]),
    html.Hr(),
    dbc.Row([
        dbc.Col(html.Footer("Data from CoinGecko | Created by Jaydeep Hajare!", className="text-center text-muted"))
    ])
], fluid=True)

# Callback to update graph
@app.callback(
    Output('price-graph', 'figure'),
    Input('refresh-button', 'n_clicks'),
    State('coin-dropdown', 'value')
)
def update_chart(n_clicks, selected_coins):
    fig = go.Figure()
    for coin in selected_coins:
        df = fetch_coin_data(coin)
        fig.add_trace(go.Scatter(x=df['date'], y=df['price'], mode='lines', name=coins[coin]))

    fig.update_layout(
        title="Cryptocurrency Price Trends (Past 30 Days)",
        xaxis_title="Date",
        yaxis_title="Price in USD",
        template="plotly_dark",
        legend_title="Cryptos",
        height=600
    )
    return fig

if __name__ == '__main__':
    app.run(debug=True)