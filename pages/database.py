import dash
from dash import dcc, html, register_page, dash_table, callback, Output, Input, State
import dash_bootstrap_components as dbc
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
                {'name': 'End Time', 'id': 'End_Time'},
                {'name': 'Severity', 'id': 'Severity'},
                {'name': 'State', 'id': 'State'},
                {'name': 'County', 'id': 'County'},
                {'name': 'City', 'id': 'City'},
            ],
            data=df_sorted.head(1000).to_dict('records'), 
            page_size=50,
            style_table={'overflowX': 'auto'},
            style_cell={
                'textAlign': 'center',
                'minWidth': '100px', 'width': '100px', 'maxWidth': '100px'
            },
            style_header={
                'backgroundColor': 'rgb(230, 230, 230)',
                'fontWeight': 'bold'
            },
            style_data_conditional=[{
                'if': {'state': 'active'},  # on hover
                'backgroundColor': 'rgba(0, 0, 0, 0.1)',  # light grey
                'cursor': 'pointer'
            }]
        ),
        html.Div(
            children=[
                html.Button('Load More', id='load-more-button', n_clicks=0)
            ],
            style={'textAlign': 'center', 'margin': '20px'}
        ),
        dbc.Modal(
            [
                # dbc.ModalHeader(
                #     dbc.ModalTitle("Accident Details"),
                #     close_button=True, 
                #     className='modal-header'
                # ),
                dbc.ModalHeader(
                    [
                        dbc.ModalTitle("Accident Details"),
                        dbc.Button(
                            "X",
                            id="modal-close-button",
                            className="btn-close",
                            n_clicks=0
                        )
                    ],
                    className='modal-header',
                    close_button=False
                ),
                dbc.ModalBody(id='modal-body', className='modal-body')
            ],
            id='accident-modal',
            size='lg',
            is_open=False,
            backdrop='static',
            keyboard=False,
            className='accident-modal'
        ),
    ]
)

# Load More Rows
@callback(
    Output('db-table', 'data'),
    Input('load-more-button', 'n_clicks'),
    State('db-table', 'data')
)
def load_more_data(n_clicks, current_data):
    if n_clicks == 0:
        return df_sorted.head(1000).to_dict('records')

    # Calculate the number of rows to display
    rows_to_display = (n_clicks + 1) * 1000
    return df_sorted.head(rows_to_display).to_dict('records')

# Modal Overlay
@callback(
    Output('accident-modal', 'is_open'),
    Output('modal-body', 'children'),
    Input('db-table', 'active_cell'),
    Input('modal-close-button', 'n_clicks'),
    State('db-table', 'data'),
    State('accident-modal', 'is_open')
)
def display_modal(active_cell, close_clicks, data, is_open):
    ctx = dash.callback_context

    if ctx.triggered:
        if ctx.triggered[0]['prop_id'] == 'modal-close-button.n_clicks':
            return False, ""

    if active_cell:
        row = active_cell['row']
        selected_data = data[row]
        details = html.Div([
            html.P(f"ID: {selected_data['ID']}"),
            html.P(f"Start Time: {selected_data['Start_Time']}"),
            html.P(f"End Time: {selected_data['End_Time']}"),
            html.P(f"Severity: {selected_data['Severity']}"),
            html.P(f"State: {selected_data['State']}"),
            html.P(f"County: {selected_data['County']}"),
            html.P(f"City: {selected_data['City']}")
        ])
        return True, details

    return is_open, ""

