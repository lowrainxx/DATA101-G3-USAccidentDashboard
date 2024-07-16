# home.py
import dash
from dash import dcc, html, register_page
import plotly.express as px
import pandas as pd
import os
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)

# Register Home page
register_page(__name__, path='/')

current_directory = os.path.dirname(__file__)
csv_file_path = os.path.join(current_directory, '..', 'dataset', 'us_accidents_cut.csv')

# Load dataset in chunks
def load_data(file_path):
    logging.info("Loading data in chunks...")
    chunk_size = 100000  # chunk size based on memory availability
    chunks = []
    try:
        for chunk in pd.read_csv(file_path, chunksize=chunk_size, engine='python'):
            chunks.append(chunk)
        df = pd.concat(chunks, ignore_index=True)
        if df.empty:
            raise ValueError("The CSV file is empty")
        logging.info("Data loaded successfully.")
        return df
    except Exception as e:
        logging.error(f"Error loading CSV file: {e}")
        raise RuntimeError(f"Error loading CSV file: {e}")

df = load_data(csv_file_path)

# Figures
# Chloromap
accident_counts = df['State'].value_counts().reset_index()
accident_counts.columns = ['State', 'accident_count']

severity_counts = df['Severity'].value_counts().reset_index()
severity_counts.columns = ['Severity', 'count']

barsample = px.bar(severity_counts, x='Severity', y='count', title='Accidents by Severity')

# Define the layout for the home page
layout = html.Div([
    html.H1('Home Page'),
    html.Div(children=[
        dcc.Graph(id='severity-bar-chart', figure=barsample)
    ], style={'display': 'flex', 'flex-wrap': 'wrap'})
])
