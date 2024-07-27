import dash
from dash import dcc, html
from flask import Flask

# Flask server
server = Flask(__name__)

# Dash app
app = dash.Dash(__name__, server=server, use_pages=True)

# Layout here
app.layout = html.Div([
    html.Nav([
        dcc.Link('Home', href='/', className='nav-link'),
        dcc.Link('Weather', href='/weather', className='nav-link'),
        # dcc.Link('POI', href='/poi', className='nav-link'),
        dcc.Link('Database', href='/database', className='nav-link')
    ], className='navbar'),
    
    dash.page_container,  # Loads page starting here
    
    html.Footer('© 2024 Group 3', className='footer')
])

if __name__ == '__main__':
    server.run(debug=True)
    