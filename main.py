import dash
from dash import dcc, html
import plotly.express as px

app = dash.Dash(__name__)
df = px.data.iris() # Sample only
fig = px.scatter(df, x='sepal_width', y='sepal_length')

# Layout here
app.layout = html.Div([
    html.Nav([
        html.A('Home', href='#home', className='nav-link'),
        html.A('Tab 1', href='#home', className='nav-link')
    ], className='navbar'),
    
    html.Div([
        html.H1('US Accidents'),
        dcc.Graph(figure=fig),
    ], className='main-content'),
    
    html.Footer('© 2024 Group 3', className='footer')
])

if __name__ == '__main__':
    app.run_server(debug=True)