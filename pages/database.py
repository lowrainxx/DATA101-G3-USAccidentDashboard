import dash
from dash import dcc, html, register_page, dash_table, callback, Output, Input, State
import pandas as pd
import logging
from data import df

# Setup logging
logging.basicConfig(level=logging.INFO)

# Register Database
register_page(__name__, path='/database')

# Load data
if df is None:
    raise ValueError("database.py : DataFrame is not loaded.")

# Sort the data by ID
df_sorted = df.sort_values(by='ID')

layout = html.Div(
    className='database-container',
    children=[
        html.H1('Accident Database', className='db-title'),
        dash_table.DataTable(
            id='db-table',
            columns=[
                {'name': 'ID', 'id': 'ID'},
                {'name': 'Start Time', 'id': 'Start_Time'},
                {'name': 'Severity', 'id': 'Severity'},
                {'name': 'State', 'id': 'State'},
                {'name': 'County', 'id': 'County'},
                {'name': 'City', 'id': 'City'},
                {'name': 'Street', 'id': 'Street'},
            ],
            data=df_sorted.to_dict('records'), #.head(100)
            page_size=50,
            style_table={'overflowX': 'auto'},
            style_cell={'textAlign': 'left'},
            style_header={
                'backgroundColor': 'rgb(230, 230, 230)',
                'fontWeight': 'bold'
            },
        ),
        html.Div(
            children=[
                html.Button('Load More', id='load-more-button', n_clicks=0)
            ],
            style={'textAlign': 'center', 'margin': '20px'}
        ),
    ]
)

@callback(
    Output('db-table', 'data'),
    Input('load-more-button', 'n_clicks'),
    State('db-table', 'data')
)
def load_more_data(n_clicks, current_data):
    if n_clicks == 0:
        return df_sorted.head(100).to_dict('records')

    # Calculate the number of rows to display
    rows_to_display = (n_clicks + 1) * 100
    return df_sorted.head(rows_to_display).to_dict('records')
