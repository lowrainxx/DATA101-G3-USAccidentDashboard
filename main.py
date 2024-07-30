import dash
from dash import dcc, html
from flask import Flask
import logging
from data import df

# Setup logging
logging.basicConfig(level=logging.INFO)

# External Stylesheets
external_stylesheets = ['https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css']

# Flask server
server = Flask(__name__)

# Dash app
app = dash.Dash(__name__,  server=server, use_pages=True, external_stylesheets=external_stylesheets)
app.title = "US Accidents Dashboard"

total_accidents = f"{df.shape[0]:,}".replace(',', ' ')

# Layout here
app.layout = html.Div([
    html.Nav([
        dcc.Link('Home', href='/', className='nav-link'),
        dcc.Link('Database', href='/database', className='nav-link'),
        html.Span(f"US Accidents 2020-2022", className='nav-link title'),
        html.Span(f"Total Accidents: {total_accidents}", className='nav-link total-accidents')
    ], className='navbar'),
    
    dash.page_container,  # Loads page starting here
    
    html.Footer('© 2024 DATA101 Group 3', className='footer')
])

if __name__ == '__main__':
    server.run(debug=True)
