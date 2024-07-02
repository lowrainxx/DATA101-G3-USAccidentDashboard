import dash
from dash import dcc, html, register_page
import plotly.express as px
import pandas as pd

# Register Weather page
register_page(__name__, path='/weather')

# Dataset
# df = pd.read_csv('dataset/us_accidents_cut.csv')

# Sample data
data = {
    'state': ['AL', 'AK', 'AZ', 'AR', 'CA', 'CO', 'CT', 'DE', 'FL', 'GA'],
    'population': [4903185, 731545, 7278717, 3017804, 39512223, 5758736, 3565287, 973764, 21477737, 10617423]
}

df1 = pd.DataFrame(data)

# Choropleth map
fig = px.choropleth(df1,
                    locations='state',
                    locationmode="USA-states",
                    color='population',
                    scope="usa",
                    title="US States Population",
                    labels={'population': 'Population'},
                    color_continuous_scale="Viridis")

# Define the layout for the home page
layout = html.Div([
    html.Div([
        html.H1('US Accidents'),
        dcc.Graph(figure=fig),
    ], className='main-content')
])
