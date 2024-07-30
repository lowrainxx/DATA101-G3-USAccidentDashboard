import dash
from dash import dcc, html, register_page, dash_table, callback, Output, Input, State
import dash_bootstrap_components as dbc
import pandas as pd
import logging
from data import df
import plotly.express as px

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
        html.Div(
            children=[
                dcc.Input(
                    id='search-id-input',
                    type='text',
                    placeholder='Search by ID...',
                ),
                html.Button(
                    html.I(className='fas fa-search'), 
                    id='search-button', 
                    n_clicks=0
                ),
            ],
            style={'marginBottom': '20px'}
        ),
        dcc.ConfirmDialog(
            id='id-not-found-dialog',
            message='ID not found. Please enter a valid ID.',
        ),
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
            page_action='none',
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
                'if': {'state': 'active'},
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
        dbc.Modal([
                html.Div([
                    dbc.ModalHeader([
                        dbc.ModalTitle("Accident Details", className='modal-title'),
                        dbc.Button(
                            "X",
                            id="modal-close-button",
                            className="btn-close",
                            n_clicks=0
                        ),
                    ], className='modal-header', close_button=False),
                    dbc.ModalBody(
                        html.Div(
                            id='modal-body-content', 
                            children=[
                                html.Div([], className='details-container'),
                                dcc.Graph(id='map-graph', style={'height': '300px'})
                            ],
                            className='modal-body'
                        )
                    )
                ], className='modal-content', id='modal-content')
            ],
            id='accident-modal',
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

def create_details(selected_data):
    return html.Div([
                html.Div([
                    html.P(f"ID: {selected_data['ID']}", className='item-id'),
                    html.P(f"Start Time: {selected_data['Start_Time']}", className='item-startTime'),
                    html.P(f"End Time: {selected_data['End_Time']}", className='item-endTime'),
                    html.P(f"Coordinates {selected_data['Start_Lat']}, {selected_data['Start_Lng']}", className='item-cords'),
                ], className='detail-main'),
                html.Div([
                    html.P(f"State: {selected_data['State']}", className='item item-state'),
                    html.P(f"County: {selected_data['County']}", className='item item-county'),
                    html.P(f"City: {selected_data['City']}", className='item item-city'),
                    html.P(f"Street: {selected_data['Street']}", className='item item-street'),
                    html.P(f"Zipcode: {selected_data['Zipcode']}", className='item item-zipcode'),
                ], className='detail-address'),
                html.P(f"Description: {selected_data['Description']}", className='item-description'),
                html.Div([
                    html.P(f"Severity: {selected_data['Severity']}", className='item-severity'),
                    html.P(f"Weather Condition: {selected_data['Weather_Condition']}", className='item-weather'),
                ], className='detail-other'),
                html.Div([
                    html.Div([
                        html.P(f"Temperature: {selected_data['Temperature(F)']}F", className='item-temperature'),
                        html.P(f"Wind Chill: {selected_data['Wind_Chill(F)']}F", className='item-windChill'),
                        html.P(f"Humidity: {selected_data['Humidity(%)']}%", className='item-humidity'),
                        html.P(f"Pressure: {selected_data['Pressure(in)']}in", className='item-pressure'),
                    ], className='detail-weather-top'),
                    html.Div([
                        html.P(f"Visibility: {selected_data['Visibility(mi)']}mi", className='item-visibility'),
                        html.P(f"Wind Direction: {selected_data['Wind_Direction']}", className='item-windDirection'),
                        html.P(f"Wind Speed: {selected_data['Wind_Speed(mph)']}mph", className='item-windSpeed'),
                        html.P(f"Precipitation: {selected_data['Precipitation(in)']}in", className='item-precipitation'),
                    ], className='detail-weather-top'),
                ], className='detail-weather')
            ], className='details-container')

# Modal Overlay
@callback(
    Output('accident-modal', 'is_open'),
    Output('modal-body-content', 'children'),
    Output('map-graph', 'figure'),
    Output('id-not-found-dialog', 'displayed'),
    Input('db-table', 'active_cell'),
    Input('modal-close-button', 'n_clicks'),
    Input('search-button', 'n_clicks'),
    State('search-id-input', 'value'),
    State('db-table', 'derived_virtual_data'),
    State('accident-modal', 'is_open')
)
def display_modal(active_cell, close_clicks, search_clicks, search_id, derived_virtual_data, is_open):
    ctx = dash.callback_context

    if ctx.triggered:
        triggered_prop = ctx.triggered[0]['prop_id']
        if triggered_prop == 'modal-close-button.n_clicks':
            placeholder_fig = px.scatter_mapbox(
                pd.DataFrame({'lat': [], 'lon': []}),
                lat='lat',
                lon='lon',
                zoom=10
            )
            placeholder_fig.update_layout(mapbox_style="carto-positron", margin={"r":0,"t":0,"l":0,"b":0})
            empty_details = html.Div([], className='details-container')
            return False, [empty_details, dcc.Graph(figure=placeholder_fig, id='map-graph', style={'height': '300px'})], placeholder_fig, False

        if triggered_prop == 'search-button.n_clicks' and search_id:
            # Find the row with the specified ID in the entire DataFrame
            search_id = search_id.lower()
            selected_data = df[df['ID'].astype(str).str.lower() == search_id]
            if selected_data.empty:
                return is_open, dash.no_update, dash.no_update, True  # ID not found
            
            selected_data = selected_data.iloc[0]  # Get the first matching row as a series

            details = create_details(selected_data)

            # Create the map figure only if lat/lon are present
            if 'Start_Lat' in selected_data and 'Start_Lng' in selected_data:
                fig = px.scatter_mapbox(
                    pd.DataFrame({
                        'lat': [selected_data['Start_Lat']],
                        'lon': [selected_data['Start_Lng']],
                        'text': [f"Accident ID: {selected_data['ID']}"]
                    }),
                    lat='lat',
                    lon='lon',
                    text='text',
                    zoom=10
                )
                fig.update_layout(mapbox_style="carto-positron", margin={"r":0,"t":0,"l":0,"b":0})
            else:
                fig = px.scatter_mapbox(
                    pd.DataFrame({'lat': [], 'lon': []}),
                    lat='lat',
                    lon='lon',
                    zoom=10
                )
                fig.update_layout(mapbox_style="carto-positron", margin={"r":0,"t":0,"l":0,"b":0})

            return True, [details, dcc.Graph(figure=fig, id='map-graph', style={'height': '300px'})], fig, False

    if active_cell:
        row = active_cell['row']
        selected_data = derived_virtual_data[row]
        details = create_details(selected_data)

        # Create the map figure only if lat/lon are present
        if 'Start_Lat' in selected_data and 'Start_Lng' in selected_data:
            fig = px.scatter_mapbox(
                pd.DataFrame({
                    'lat': [selected_data['Start_Lat']],
                    'lon': [selected_data['Start_Lng']],
                    'text': [f"Accident ID: {selected_data['ID']}"]
                }),
                lat='lat',
                lon='lon',
                text='text',
                zoom=10
            )
            fig.update_layout(mapbox_style="carto-positron", margin={"r":0,"t":0,"l":0,"b":0})
        else:
            fig = px.scatter_mapbox(
                pd.DataFrame({'lat': [], 'lon': []}),
                lat='lat',
                lon='lon',
                zoom=10
            )
            fig.update_layout(mapbox_style="carto-positron", margin={"r":0,"t":0,"l":0,"b":0})

        return True, [details, dcc.Graph(figure=fig, id='map-graph', style={'height': '300px'})], fig, False

    placeholder_fig = px.scatter_mapbox(
        pd.DataFrame({'lat': [], 'lon': []}),
        lat='lat',
        lon='lon',
        zoom=10
    )
    placeholder_fig.update_layout(mapbox_style="carto-positron", margin={"r":0,"t":0,"l":0,"b":0})
    empty_details = html.Div([], className='details-container')

    return is_open, [empty_details, dcc.Graph(figure=placeholder_fig, id='map-graph', style={'height': '300px'})], placeholder_fig, False
