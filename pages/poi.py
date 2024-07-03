import dash
from dash import dcc, html, register_page
import plotly.express as px
import pandas as pd

# Register Weather page
register_page(__name__, path='/poi')

layout = html.Div([
    html.H1('POI Page')
])