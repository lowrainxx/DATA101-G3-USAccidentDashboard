import dash
from dash import dcc, html
import plotly.express as px
import pandas as pd
from flask import Flask, render_template

# Flask server
server = Flask(__name__)

# Dash app
app = dash.Dash(__name__, server=server, url_base_pathname='/dash/')

# Dataset
# df = pd.read_csv('dataset/us_accidents_cut.csv')
df = px.data.iris() # Sample only

# Figures
fig1 = px.scatter(df, x='sepal_length', y='sepal_width', color='species', title='Figure 1')
fig2 = px.scatter(df, x='petal_length', y='petal_width', color='species', title='Figure 2')

# Layout here
app.layout = html.Div([
    html.Nav([
        html.A('Home', href='#home', className='nav-link'),
        html.A('Tab 1', href='#home', className='nav-link'),
        html.A('Tab 2', href='#home', className='nav-link'),
        html.A('Tab 3', href='#home', className='nav-link'),
        html.A('Tab 4', href='#home', className='nav-link'),
        html.A('Tab 5', href='#home', className='nav-link')
    ], className='navbar'),
    
    html.Div(children=[
        dcc.Graph(id='graph-1', figure=fig1, style={'flex': 1}),
        dcc.Graph(id='graph-2', figure=fig2, style={'flex': 1})
    ], style={'display': 'flex', 'flex-wrap': 'wrap'}),
    
    html.Div([
        html.H1('US Accidents'),
        dcc.Graph(figure=fig1),
    ], className='main-content'),
    
    html.Footer('© 2024 Group 3', className='footer')
])

@server.route('/')
def home():
    return render_template('home.html')

if __name__ == '__main__':
    server.run(debug=True)