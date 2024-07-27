# home.py
import dash
from dash import dcc, html, register_page
import plotly.express as px
import dask.dataframe as dd
import os
import logging
from dash.dependencies import Input, Output, State
import pandas as pd

# Setup logging
logging.basicConfig(level=logging.INFO)

# Register Home page
register_page(__name__, path='/')

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

# Line Chart 
byhour = df['Hour'].value_counts().reset_index()
byhour.columns = ['Hour', 'Count']
bymonth = df['Month'].value_counts().reset_index()
bymonth.columns = ['Month', 'Count']
byday = df['Day'].value_counts().reset_index()
byday.columns = ['Day', 'Count']

byhour = byhour.sort_values(by="Hour")
bymonth = bymonth.sort_values(by="Month")
byday = byday.sort_values(by="Day")

accident_counts = df['State'].value_counts().reset_index()
accident_counts.columns = ['State', 'accident_count']

severity_counts = df['Severity'].value_counts().reset_index()
severity_counts.columns = ['Severity', 'count']

barsample = px.bar(severity_counts, x='Severity', y='count', title='[SAMPLE] Accidents by Severity')

#stacked bar chart
severity_weather = df.groupby(['Severity', 'Weather_Condition']).size().reset_index(name='Count')

stacked_bar = px.bar(
    severity_weather,
    x='Severity',
    y='Count',
    color='Weather_Condition',
    title='Number of Accidents by Severity and Weather Conditions',
    labels={'Count': 'Number of Accidents'},
)

# Define the layout for the home page
layout = html.Div([

    html.H1('Home Page'),
    
    # Date Range
    html.H2('Select Date Range'),
    html.Div([
        # Start Date Picker
        dcc.DatePickerSingle(
            id='start-date-picker',
            min_date_allowed=df['Start_Time'].min().date(),
            max_date_allowed=df['Start_Time'].max().date(),
            initial_visible_month=df['Start_Time'].min().date(),
            date=df['Start_Time'].min().date(),
            display_format='YYYY-MM-DD'
        ),
        # Slider
        dcc.RangeSlider(
            id='date-range-slider',
            min=0,
            max=(df['Start_Time'].max() - df['Start_Time'].min()).days,
            value=[0, (df['Start_Time'].max() - df['Start_Time'].min()).days],
            marks={
                i: (df['Start_Time'].min() + pd.Timedelta(days=i)).strftime('%Y-%m-%d') for i in range(0, (df['Start_Time'].max() - df['Start_Time'].min()).days + 1, 30)
            },
            tooltip={"placement": "bottom", "always_visible": True},
            className="date-range-slider"        
        ),
        # End Date Picker
        dcc.DatePickerSingle(
            id='end-date-picker',
            min_date_allowed=df['Start_Time'].min().date(),
            max_date_allowed=df['Start_Time'].max().date(),
            initial_visible_month=df['Start_Time'].max().date(),
            date=df['Start_Time'].max().date(),
            display_format='YYYY-MM-DD'
        ),
        # Submit
        html.Button('Submit', id='submit-button', n_clicks=0)
    ], style={'display': 'flex', 'justify-content': 'center', 'align-items': 'center', 'margin': '20px 0'}),

    html.Div(children=[
        dcc.Graph(id='severity-bar-chart', figure=barsample)
    ], style={'display': 'flex', 'flex-wrap': 'wrap', 'width': '48%', 'margin': '0 auto'}),
    
    html.H2('Number of Accidents over Time'),
    dcc.RadioItems(
        id='radioitems',
        options=[
            {'label': 'Hour', 'value': 'Hour'},
            {'label': 'DayOfTheMonth', 'value': 'DayOfTheMonth'},
            {'label': 'Monthly', 'value': 'Monthly'}
        ],
        value='DayOfTheMonth',
        inline=True
    ),
    html.Div(children=[
        dcc.Graph(id='graph')
    ], style={'display': 'flex', 'flex-wrap': 'wrap', 'width': '48%', 'margin': '0 auto'}),

    # stacked bar chart for severity and weather conditions
    html.H2('Accidents by Severity and Weather Conditions'),
    html.Div(children=[
        dcc.Graph(id='severity-weather-stacked-bar', figure=stacked_bar)
    ], style={'display': 'flex', 'flex-wrap': 'wrap', 'width': '48%', 'margin': '0 auto'}),
])

# Callback to update graph
@dash.callback(
    Output('graph', 'figure'),
    Input('radioitems', 'value')
)
def update_graph(selected_option):
    if selected_option == 'Hour':
        fig = px.line(byhour, x='Hour', y='Count', title='Accidents by Hour')
    elif selected_option == 'DayOfTheMonth':
        fig = px.line(byday, x='Day', y='Count', title='Accidents by Day of the Month')
    elif selected_option == 'Monthly':
        fig = px.line(bymonth, x='Month', y='Count', title='Accidents by Month')
    return fig

@dash.callback(
    [Output('start-date-picker', 'date'),
     Output('end-date-picker', 'date'),
     Output('date-range-slider', 'value')],
    [Input('date-range-slider', 'value'),
     Input('start-date-picker', 'date'),
     Input('end-date-picker', 'date')]
)
def sync_date_picker_slider(slider_range, start_date, end_date):
    ctx = dash.callback_context
    triggered_id = ctx.triggered[0]['prop_id'].split('.')[0]

    if triggered_id == 'date-range-slider':
        start_date = df['Start_Time'].min() + pd.Timedelta(days=slider_range[0])
        end_date = df['Start_Time'].min() + pd.Timedelta(days=slider_range[1])
    elif triggered_id == 'start-date-picker':
        start_date = pd.to_datetime(start_date)
        end_date = pd.to_datetime(end_date)
        slider_range[0] = (start_date - df['Start_Time'].min()).days
    elif triggered_id == 'end-date-picker':
        start_date = pd.to_datetime(start_date)
        end_date = pd.to_datetime(end_date)
        slider_range[1] = (end_date - df['Start_Time'].min()).days

    return start_date.date(), end_date.date(), slider_range

# Callback to update barsample based on date range
@dash.callback(
    Output('severity-bar-chart', 'figure'),
    Input('submit-button', 'n_clicks'),
    State('start-date-picker', 'date'),
    State('end-date-picker', 'date')
)
def update_barsample(n_clicks, start_date, end_date):
    if n_clicks > 0:
        filtered_df = df[(df['Start_Time'] >= start_date) & (df['Start_Time'] <= end_date)]
        severity_counts_filtered = filtered_df['Severity'].value_counts().reset_index()
        severity_counts_filtered.columns = ['Severity', 'count']
        barsample_filtered = px.bar(severity_counts_filtered, x='Severity', y='count', title='Accidents by Severity')
        return barsample_filtered
    return barsample

logging.info('DONE HOME.PY')