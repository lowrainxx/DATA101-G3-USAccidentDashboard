# weather.py
import dash
from dash import dcc, html, register_page
import plotly.express as px
import pandas as pd
import dask.dataframe as dd
import os
import logging
from dash.dependencies import Input, Output, State

# Setup logging
logging.basicConfig(level=logging.INFO)

# Register Weather page
register_page(__name__, path='/weather')

# Define the path to the CSV file
current_directory = os.path.dirname(__file__)
csv_file_path = os.path.join(current_directory, '..', 'dataset', 'us_accidents_clean.csv')

# Load dataset using Dask
def load_data(file_path):
    logging.info("Loading data using Dask...")
    try:
        ddf = dd.read_csv(file_path)
        df = ddf.compute()
        if df.empty:
            raise ValueError("The CSV file is empty")
        logging.info("Data loaded successfully using Dask.")
        return df
    except Exception as e:
        logging.error(f"Error loading CSV file: {e}")
        raise RuntimeError(f"Error loading CSV file: {e}")

df = load_data(csv_file_path)

# Convert 'Start_Time' to datetime
df['Start_Time'] = pd.to_datetime(df['Start_Time'])
df['End_Time'] = pd.to_datetime(df['End_Time'])

# Choropleth map based on accident counts per state
def create_choropleth(filtered_df):
    accident_counts = filtered_df['State'].value_counts().reset_index()
    accident_counts.columns = ['State', 'Accident_Count']

    fig_choropleth = px.choropleth(
        accident_counts,
        locations='State',
        locationmode="USA-states",
        color='Accident_Count',
        scope="usa",
        title="Accidents by State",
        labels={'Accident_Count': 'Accident Count'},
        color_continuous_scale="Viridis"
    )
    return fig_choropleth

# Treemap based on accident counts per city within states
def create_treemap(filtered_df):
    state_city_counts = filtered_df.groupby(['State', 'City']).size().reset_index(name='Counts')
    top_cities_per_state = state_city_counts.groupby('State').apply(lambda x: x.nlargest(10, 'Counts')).reset_index(drop=True)
    top_states = top_cities_per_state.groupby('State')['Counts'].sum().nlargest(5).index
    top_cities_top_states = top_cities_per_state[top_cities_per_state['State'].isin(top_states)]

    fig_treemap = px.treemap(
        top_cities_top_states,
        path=['State', 'City'],
        values='Counts',
        title="Top 5 Cities per Top 5 States by Accident Counts"
    )
    fig_treemap.update_layout(width=1000, height=700)
    return fig_treemap

# Define the layout for the weather page
layout = html.Div([
    html.H1('Weather Page'),
    html.Div([
        # Date Range
        html.H2('Select Date Range'),
        html.Div([
            dcc.DatePickerSingle(
                id='weather-start-date-picker',
                min_date_allowed=df['Start_Time'].min().date(),
                max_date_allowed=df['Start_Time'].max().date(),
                initial_visible_month=df['Start_Time'].min().date(),
                date=df['Start_Time'].min().date(),
                display_format='YYYY-MM-DD'
            ),
            dcc.RangeSlider(
                id='weather-date-range-slider',
                min=0,
                max=(df['Start_Time'].max() - df['Start_Time'].min()).days,
                value=[0, (df['Start_Time'].max() - df['Start_Time'].min()).days],
                marks={
                    i: (df['Start_Time'].min() + pd.Timedelta(days=i)).strftime('%Y-%m-%d') for i in range(0, (df['Start_Time'].max() - df['Start_Time'].min()).days + 1, 30)
                },
                tooltip={"placement": "bottom", "always_visible": True},
                className="date-range-slider"        
            ),
            dcc.DatePickerSingle(
                id='weather-end-date-picker',
                min_date_allowed=df['Start_Time'].min().date(),
                max_date_allowed=df['Start_Time'].max().date(),
                initial_visible_month=df['Start_Time'].max().date(),
                date=df['Start_Time'].max().date(),
                display_format='YYYY-MM-DD'
            ),
            html.Button('Submit', id='weather-submit-button', n_clicks=0)
        ], style={'display': 'flex', 'justify-content': 'center', 'align-items': 'center', 'margin': '20px 0'}),
        dcc.Graph(id='choropleth-map'),
        dcc.Graph(id='treemap')  # Adding the treemap to the layout
    ], className='main-content')
])

# Callback to sync date picker and slider
@dash.callback(
    [Output('weather-start-date-picker', 'date'),
     Output('weather-end-date-picker', 'date'),
     Output('weather-date-range-slider', 'value')],
    [Input('weather-date-range-slider', 'value'),
     Input('weather-start-date-picker', 'date'),
     Input('weather-end-date-picker', 'date')]
)
def sync_date_picker_slider(slider_range, start_date, end_date):
    ctx = dash.callback_context
    triggered_id = ctx.triggered[0]['prop_id'].split('.')[0]

    if triggered_id == 'weather-date-range-slider':
        start_date = (df['Start_Time'].min() + pd.Timedelta(days=slider_range[0])).date()
        end_date = (df['Start_Time'].min() + pd.Timedelta(days=slider_range[1])).date()
    elif triggered_id in ['weather-start-date-picker', 'weather-end-date-picker']:
        start_date = pd.to_datetime(start_date).date()
        end_date = pd.to_datetime(end_date).date()
        slider_range[0] = (pd.to_datetime(start_date) - df['Start_Time'].min()).days
        slider_range[1] = (pd.to_datetime(end_date) - df['Start_Time'].min()).days

    return start_date, end_date, slider_range

# Callback to update graphs based on date range
@dash.callback(
    [Output('choropleth-map', 'figure'),
     Output('treemap', 'figure')],
    Input('weather-submit-button', 'n_clicks'),
    State('weather-start-date-picker', 'date'),
    State('weather-end-date-picker', 'date')
)
def update_weather_graphs(n_clicks, start_date, end_date):
    if n_clicks > 0:
        start_date = pd.to_datetime(start_date)
        end_date = pd.to_datetime(end_date)
        filtered_df = df[(df['Start_Time'] >= start_date) & (df['Start_Time'] <= end_date)]
        choropleth = create_choropleth(filtered_df)
        treemap = create_treemap(filtered_df)
        return choropleth, treemap
    return create_choropleth(df), create_treemap(df)

logging.info('DONE WEATHER.PY')
