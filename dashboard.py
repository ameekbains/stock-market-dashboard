import dash
from dash import dcc, html, Input, Output
import plotly.graph_objs as go
import pandas as pd
import yfinance as yf

app = dash.Dash(__name__)

# Sample list of stock symbols for dropdown menu
stock_symbols = ['AAPL', 'MSFT', 'GOOGL', 'AMZN']

app.layout = html.Div([
    html.H1("Stock Market Data Dashboard", style={'textAlign': 'center'}),
    
    html.Div([
        dcc.Dropdown(
            id='stock-symbol',
            options=[{'label': symbol, 'value': symbol} for symbol in stock_symbols],
            value=['AAPL'],  # Default to AAPL
            multi=True,  # Allow multiple selection
            style={'width': '50%'}
        ),
        dcc.DatePickerRange(
            id='date-picker',
            start_date_placeholder_text="Start Date",
            end_date_placeholder_text="End Date",
            style={'margin-left': '20px'}
        ),
    ], style={'display': 'flex', 'justify-content': 'center', 'margin-bottom': '20px'}),
    
    dcc.Graph(id='stock-chart'),
    
    dcc.Graph(id='comparison-chart'),
    
    html.Div(id='correlation-output')
    
])

def get_stock_data(symbol, start_date, end_date):
    stock = yf.Ticker(symbol)
    stock_data = stock.history(start=start_date, end=end_date)
    return stock_data

@app.callback(
    [Output('stock-chart', 'figure'),
     Output('comparison-chart', 'figure'),
     Output('correlation-output', 'children')],
    [Input('stock-symbol', 'value'),
     Input('date-picker', 'start_date'),
     Input('date-picker', 'end_date')])
def update_charts(stock_symbols, start_date, end_date):
    # Fetch stock data for selected symbols
    stock_data = pd.concat([get_stock_data(symbol, start_date, end_date)['Close'] for symbol in stock_symbols], axis=1)
    stock_data.columns = stock_symbols
    
    # Line chart for individual stocks
    individual_chart = go.Figure()
    for symbol in stock_symbols:
        individual_chart.add_trace(go.Scatter(x=stock_data.index, y=stock_data[symbol], mode='lines', name=symbol))
    individual_chart.update_layout(title="Stock Prices", xaxis_title='Date', yaxis_title='Price')
    
    # Comparison chart
    comparison_chart = go.Figure()
    for symbol in stock_symbols:
        comparison_chart.add_trace(go.Scatter(x=stock_data.index, y=stock_data[symbol] / stock_data[symbol].iloc[0], mode='lines', name=symbol))
    comparison_chart.update_layout(title="Stock Comparison", xaxis_title='Date', yaxis_title='Relative Price')
    
    # Correlation calculation
    correlation = stock_data.corr().round(2)
    correlation_output = html.Table([
        html.Thead(html.Tr([html.Th('')] + [html.Th(symbol) for symbol in stock_symbols])),
        html.Tbody([html.Tr([html.Th(symbol)] + [html.Td(correlation.loc[symbol, s]) for s in stock_symbols]) for symbol in stock_symbols])
    ])
    
    return individual_chart, comparison_chart, correlation_output

if __name__ == '__main__':
    app.run_server(debug=True)
