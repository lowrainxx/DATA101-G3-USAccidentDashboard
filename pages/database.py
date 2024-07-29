import dash
from dash import dcc, html, register_page
import plotly.express as px
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

layout = html.Div(
    className='database-container', 
    children=[
        html.H1('Database Page', className='db-title'),
        html.H1('Database Page', className='db-title')
    ]
)