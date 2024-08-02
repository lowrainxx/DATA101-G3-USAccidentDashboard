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

state_mapping = {
    'IL': 'Illinois', 'CA': 'California', 'VA': 'Virginia', 'OH': 'Ohio', 'PA': 'Pennsylvania', 
    'SC': 'South Carolina', 'NJ': 'New Jersey', 'NY': 'New York', 'FL': 'Florida', 'NC': 'North Carolina', 
    'TX': 'Texas', 'AZ': 'Arizona', 'TN': 'Tennessee', 'MA': 'Massachusetts', 'WA': 'Washington', 
    'AL': 'Alabama', 'KY': 'Kentucky', 'GA': 'Georgia', 'MI': 'Michigan', 'LA': 'Louisiana', 
    'IN': 'Indiana', 'CT': 'Connecticut', 'MN': 'Minnesota', 'OR': 'Oregon', 'CO': 'Colorado', 
    'OK': 'Oklahoma', 'NV': 'Nevada', 'MD': 'Maryland', 'UT': 'Utah', 'MO': 'Missouri', 
    'KS': 'Kansas', 'NM': 'New Mexico', 'AR': 'Arkansas', 'NH': 'New Hampshire', 'NE': 'Nebraska', 
    'IA': 'Iowa', 'WI': 'Wisconsin', 'RI': 'Rhode Island', 'DE': 'Delaware', 'MS': 'Mississippi', 
    'ME': 'Maine', 'DC': 'District of Columbia', 'VT': 'Vermont', 'WV': 'West Virginia', 'WY': 'Wyoming', 
    'ID': 'Idaho', 'ND': 'North Dakota', 'MT': 'Montana', 'SD': 'South Dakota'
}

# Load data
if df is None:
    raise ValueError("database.py : DataFrame is not loaded.")


# New State
df_db = df.copy()
df_db['State'] = df_db['State'].map(state_mapping)

# Replace 'T' with ' ' in datetime columns
df['Start_Time'] = df['Start_Time'].astype(str).str.replace('T', ' ')
df['End_Time'] = df['End_Time'].astype(str).str.replace('T', ' ')


# Change data types
# df['Start_Time'] = pd.to_datetime(df['Start_Time'])
# df['End_Time'] = pd.to_datetime(df['End_Time'])

# Sort the data by ID
df_sorted = df_db.sort_values(by='ID')
initial_data = df_sorted.head(1000).to_dict('records')

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
            ], id='search-container'
        ),
        dcc.ConfirmDialog(
            id='id-not-found-dialog',
            message='ID not found. Please enter a valid ID.',
        ),
        dash_table.DataTable(
            id='db-table',
            columns=[
                {'name': 'ID', 'id': 'ID', 'sortable': True},
                {'name': 'Start Time', 'id': 'Start_Time', 'sortable': True},
                {'name': 'End Time', 'id': 'End_Time', 'sortable': True},
                {'name': 'Severity', 'id': 'Severity', 'sortable': True},
                {'name': 'State', 'id': 'State', 'sortable': True},
                {'name': 'County', 'id': 'County', 'sortable': False},
                {'name': 'City', 'id': 'City', 'sortable': False},
            ],
            data=initial_data,
            sort_action='custom',
            sort_mode='single',
            sort_by=[{'column_id': 'ID', 'direction': 'asc'}],  # Default sort by ID ascending
            page_action='none',
            style_table={'overflowX': 'auto'},
            style_cell={
                'textAlign': 'center',
                'minWidth': '100px', 'width': '100px', 'maxWidth': '100px',
                'color': 'black', 'fontSize' : '20px',
            },
            style_header={
                'backgroundColor': 'rgb(37, 37, 37)',  # Grey background for header
                'fontWeight': 'bold', 'fontSize' : '25px',
                'color': 'yellow',  # Yellow text color for header
            },
            style_data_conditional=[
                {
                    'if': {'state': 'active'},
                    'backgroundColor': 'rgba(0, 0, 0, 0.1)',  # light grey
                    'cursor': 'pointer',
                },
                {
                    'if': {'row_index': 'odd'},
                    'backgroundColor': 'rgb(255, 255, 229)',  # Light grey for odd rows
                },
                {
                    'if': {'row_index': 'even'},
                    'backgroundColor': 'rgb(243, 242, 192)',  # White for even rows
                },
                {
                    'if': {
                        'filter_query': '{row_index} = selected_row',
                        'column_id': 'any'
                    },
                    'backgroundColor': 'rgba(194,242,254)',  # Highlight color for selected row
                    'color': 'black',
                }
            ],
            style_header_conditional=[
            {
                'if': {'column_id': 'any'},
                'textDecoration': 'none',
                'color': 'yellow',  # Changing sort indicator color
            },
            {
                'if': {'state': 'selected'},
                'backgroundColor': 'rgba(255, 255, 204, 0.5)',  # Different background for selected sort column
            },
        ],
            
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


# Add a callback to handle row highlighting
@callback(
    Output('db-table', 'style_data_conditional'),
    Input('db-table', 'active_cell')
)
def update_styles(active_cell):
    if active_cell:
        row = active_cell['row']
        return [
            {
                'if': {'state': 'active'},
                'backgroundColor': 'rgba(194,242,254)',  # light grey
                'cursor': 'pointer',
            },
            {
                'if': {'row_index': 'odd'},
                'backgroundColor': 'rgb(255, 255, 229)',  # Light grey for odd rows
            },
            {
                'if': {'row_index': 'even'},
                'backgroundColor': 'rgb(243, 242, 192)',  # White for even rows
            },
            {
                'if': {'row_index': row},
                'backgroundColor': 'rgba(194,242,254)',  # Highlight color for selected row
                'color': 'black',
            }
        ]
    return [
        {
            'if': {'state': 'active'},
            'backgroundColor': 'rgba(0, 0, 0, 0.1)',  # light grey
            'cursor': 'pointer',
        },
        {
            'if': {'row_index': 'odd'},
            'backgroundColor': 'rgb(255, 255, 229)',  # Light grey for odd rows
        },
        {
            'if': {'row_index': 'even'},
            'backgroundColor': 'rgb(243, 242, 192)',  # White for even rows
        }
    ]

# Load More Rows and Handle Sorting
@callback(
    Output('db-table', 'data'),
    Input('load-more-button', 'n_clicks'),
    Input('db-table', 'sort_by'),
    State('db-table', 'data')
)
def load_more_data(n_clicks, sort_by, current_data):
    # Create a copy of the entire dataset
    df_db_copy = df_db.copy()

    # Convert datetime columns to strings and replace 'T' with ' '
    df_db_copy['Start_Time'] = df_db_copy['Start_Time'].astype(str).str.replace('T', ' ')
    df_db_copy['End_Time'] = df_db_copy['End_Time'].astype(str).str.replace('T', ' ')
    
    
    # Handle sorting
    if sort_by:
        for sort in sort_by:
            df_db_copy = df_db_copy.sort_values(by=sort['column_id'], ascending=sort['direction'] == 'asc')
    else:
        # Default sorting by ID ascending
        df_db_copy = df_db_copy.sort_values(by='ID', ascending=True)
    
    # Calculate the number of rows to display
    rows_to_display = (n_clicks + 1) * 1000
    return df_db_copy.head(rows_to_display).to_dict('records')

def create_details(selected_data):
    return html.Div([
        html.Div([
            html.Div([
                html.P(f"ID: {selected_data['ID']}", className='item-id'),
                html.P(f"Start Time: {selected_data['Start_Time']}", className='item-startTime'),
                html.P(f"End Time: {selected_data['End_Time']}", className='item-endTime'),
                html.P(f"Coordinates: {selected_data['Start_Lat']}, {selected_data['Start_Lng']}", className='item-cords'),
            ], className='detail-section'),
            html.Div([
                html.P(f"State: {state_mapping.get(selected_data['State'], selected_data['State'])}", className='item item-state'),
                html.P(f"County: {selected_data['County']}", className='item item-county'),
                html.P(f"City: {selected_data['City']}", className='item item-city'),
                html.P(f"Street: {selected_data['Street']}", className='item item-street'),
                html.P(f"Zipcode: {selected_data['Zipcode']}", className='item item-zipcode'),
            ], className='detail-section'),
            html.Div([
                html.P(f"Description: {selected_data['Description']}", className='item-description'),
                html.P(f"Severity: {selected_data['Severity']}", className='item-severity'),
            ], className='detail-section'),
        ], className='upper-section'),
        html.Div([
            html.Div([
                html.P(f"Weather Condition: {selected_data['Weather_Condition']}", className='item-weather'),
                html.P(f"Temperature: {selected_data['Temperature(F)']} °F", className='item-temperature'),
                html.P(f"Wind Chill: {selected_data['Wind_Chill(F)']} °F", className='item-windChill'),
            ], className='detail-section'),
            html.Div([
                html.P(f"Humidity: {selected_data['Humidity(%)']} %", className='item-humidity'),
                html.P(f"Pressure: {selected_data['Pressure(in)']} in", className='item-pressure'),
                html.P(f"Visibility: {selected_data['Visibility(mi)']} mi", className='item-visibility'),
            ], className='detail-section'),
            html.Div([
                html.P(f"Wind Direction: {selected_data['Wind_Direction']}", className='item-windDirection'),
                html.P(f"Wind Speed: {selected_data['Wind_Speed(mph)']} mph", className='item-windSpeed'),
                html.P(f"Precipitation: {selected_data['Precipitation(in)']} in", className='item-precipitation'),
            ], className='detail-section'),
        ], className='lower-section'),
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
                zoom=20
            )
            placeholder_fig.update_layout(mapbox_style="carto-positron", margin={"r":0,"t":0,"l":0,"b":0})
            empty_details = html.Div([], className='details-container')
            return False, [empty_details, dcc.Graph(figure=placeholder_fig, id='map-graph', style={'height': '300px'})], placeholder_fig, False

        if triggered_prop == 'search-button.n_clicks' and search_id:
            # Check if search_id is numeric, if so, prepend 'A-'
            if search_id.isnumeric():
                search_id = f'A-{search_id}'
            search_id = search_id.lower().replace('a-', '')
            
            # Find the row with the specified ID in the entire DataFrame
            selected_data = df_db[df_db['ID'].astype(str).str.lower().str.replace('a-', '') == search_id]
            if selected_data.empty:
                return is_open, dash.no_update, dash.no_update, True  # ID not found
            
            selected_data = selected_data.iloc[0]  # Get the first matching row as a series

            # Convert datetime columns to strings and replace 'T' with ' '
            selected_data['Start_Time'] = str(selected_data['Start_Time']).replace('T', ' ')
            selected_data['End_Time'] = str(selected_data['End_Time']).replace('T', ' ')
        
            # Apply state mapping
            selected_data['State'] = state_mapping.get(selected_data['State'], selected_data['State'])
            
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
                    zoom=20
                )
                fig.update_layout(mapbox_style="carto-positron", margin={"r":0,"t":0,"l":0,"b":0})
            else:
                fig = px.scatter_mapbox(
                    pd.DataFrame({'lat': [], 'lon': []}),
                    lat='lat',
                    lon='lon',
                    zoom=20
                )
                fig.update_layout(mapbox_style="carto-positron", margin={"r":0,"t":0,"l":0,"b":0})

            return True, [details, dcc.Graph(figure=fig, id='map-graph', style={'height': '300px'})], fig, False

    if active_cell:
        row = active_cell['row']
        selected_data = derived_virtual_data[row]
        
        # Convert datetime columns to strings and replace 'T' with ' '
        selected_data['Start_Time'] = str(selected_data['Start_Time']).replace('T', ' ')
        selected_data['End_Time'] = str(selected_data['End_Time']).replace('T', ' ')
        
        # Apply state mapping
        selected_data['State'] = state_mapping.get(selected_data['State'], selected_data['State'])

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
                zoom=20
            )
            fig.update_layout(mapbox_style="carto-positron", margin={"r":0,"t":0,"l":0,"b":0})
        else:
            fig = px.scatter_mapbox(
                pd.DataFrame({'lat': [], 'lon': []}),
                lat='lat',
                lon='lon',
                zoom=20
            )
            fig.update_layout(mapbox_style="carto-positron", margin={"r":0,"t":0,"l":0,"b":0})

        return True, [details, dcc.Graph(figure=fig, id='map-graph', style={'height': '300px'})], fig, False

    placeholder_fig = px.scatter_mapbox(
        pd.DataFrame({'lat': [], 'lon': []}),
        lat='lat',
        lon='lon',
        zoom=20
    )
    placeholder_fig.update_layout(mapbox_style="carto-positron", margin={"r":0,"t":0,"l":0,"b":0})
    empty_details = html.Div([], className='details-container')

    return is_open, [empty_details, dcc.Graph(figure=placeholder_fig, id='map-graph', style={'height': '300px'})], placeholder_fig, False
