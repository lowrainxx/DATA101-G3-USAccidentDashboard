import dash
from dash import dcc, html, register_page
import plotly.express as px
import pandas as pd
import os

# Register Home page
register_page(__name__, path='/')

current_directory = os.path.dirname(__file__)
csv_file_path = os.path.join(current_directory, '..', 'dataset', 'us_accidents_cut.csv')

# Dataset
try:
    # df = pd.read_csv('../dataset/us_accidents_clean.csv')
    df = pd.read_csv(csv_file_path)
    if df.empty:
        raise ValueError("The CSV file is empty")
except Exception as e:
    raise RuntimeError(f"Error loading CSV file: {e}")
# df = px.data.iris() # Sample only

# Figures
# Chloromap
accident_counts = df['State'].value_counts().reset_index()
accident_counts.columns = ['State', 'accident_count']

severity_counts = df['Severity'].value_counts().reset_index()
severity_counts.columns = ['Severity', 'count']

barsample = px.bar(severity_counts, x='Severity', y='count', title='Accidents by Severity')

# chloromap = px.choropleth(df,
#                     locations='State',
#                     locationmode="USA-states",
#                     color='Severity',
#                     scope="usa",
#                     title="Chloropleth Map",
#                     labels={'accident_count': 'Number of Accidents'},
#                     color_continuous_scale="Viridis")

# treemap = px.treemap(df,
#                  path=['State', 'City'],
#                  values='value',
#                  title='Treemap')

# Define the layout for the home page
layout = html.Div([
    html.H1('Home Page'),
    html.Div(children=[
        dcc.Graph(id='severity-bar-chart', figure=barsample)
        # dcc.Graph(id='graph-1', figure=chloromap, style={'flex': 1})
        # dcc.Graph(id='graph-1', figure=treemap, style={'flex': 1})
    ], style={'display': 'flex', 'flex-wrap': 'wrap'})
])
