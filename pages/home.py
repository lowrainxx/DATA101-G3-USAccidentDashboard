import dash
from dash import dcc, html, register_page
import plotly.express as px
import pandas as pd

# Register Home page
register_page(__name__, path='/')

# Dataset
# df = pd.read_csv('dataset/us_accidents_cut.csv')
df = px.data.iris() # Sample only

# Figures
fig1 = px.scatter(df, x='sepal_length', y='sepal_width', color='species', title='Figure 1')
fig2 = px.scatter(df, x='petal_length', y='petal_width', color='species', title='Figure 2')

# Define the layout for the home page
layout = html.Div([
    html.H1('Home Page'),
    html.Div(children=[
        dcc.Graph(id='graph-1', figure=fig1, style={'flex': 1}),
        dcc.Graph(id='graph-2', figure=fig2, style={'flex': 1})
    ], style={'display': 'flex', 'flex-wrap': 'wrap'})
])
