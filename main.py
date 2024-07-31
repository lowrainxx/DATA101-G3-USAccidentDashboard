import dash
from dash import dcc, html, callback, Output, Input
from flask import Flask
import logging
from data import df

# Setup logging
logging.basicConfig(level=logging.INFO)

# External Stylesheets
external_stylesheets = [
    'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css',
    'https://fonts.googleapis.com/css?family=Audiowide&effect=3d|3d-float',
    'https://fonts.googleapis.com/css?family=Roboto+Mono',
    'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css',
]

# Flask server
server = Flask(__name__)

# Dash app
app = dash.Dash(__name__, server=server, use_pages=True, external_stylesheets=external_stylesheets)
app.title = "US Accidents Dashboard"

total_accidents = f"{df.shape[0]:,}".replace(',', ' ')

# Layout here
app.layout = html.Div([
    dcc.Location(id='url', refresh=False),  # Current pathname
    html.Nav([
        dcc.Link('Home', href='/', className='nav-link', id='link-home'),
        dcc.Link('Database', href='/database', className='nav-link', id='link-database'),
        html.Span(f"US Accidents 2020-2022", className='title font-effect-3d-float'),
        html.Div([
            html.Span(f"Total Accidents: ", className='total-accidents-text'),
            html.Span(f"{total_accidents}", className='total-accidents-value')
        ], className='total-accidents'),
        
    ], className='navbar'),
    
    dash.page_container,  # Loads page starting here
    
    html.Footer('© 2024 DATA101 Group 3', className='footer')
])

@app.callback(
    [Output('link-home', 'className'),
     Output('link-database', 'className')],
    Input('url', 'pathname')
)
def update_active_link(pathname):
    if pathname == '/':
        return ['nav-link active', 'nav-link']
    elif pathname == '/database':
        return ['nav-link', 'nav-link active']
    else:
        # Default to Home if the pathname is not recognized
        return ['nav-link active', 'nav-link']

if __name__ == '__main__':
    server.run(debug=True)
