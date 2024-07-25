# home.py
import dash
from dash import dcc, html, register_page
import plotly.express as px
import dask.dataframe as dd
import os
import logging
from dash.dependencies import Input, Output
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

# Figures
# Chloromap
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

barsample = px.bar(severity_counts, x='Severity', y='count', title='Accidents by Severity')

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