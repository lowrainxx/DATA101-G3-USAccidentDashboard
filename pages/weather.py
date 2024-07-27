import dash
from dash import dcc, html, register_page, Input, Output
import plotly.express as px
import pandas as pd
import datetime

# Register Weather page
register_page(__name__, path='/weather')

# Sample data for the choropleth map
data = {
    'state': ['AL', 'AK', 'AZ', 'AR', 'CA', 'CO', 'CT', 'DE', 'FL', 'GA'],
    'population': [4903185, 731545, 7278717, 3017804, 39512223, 5758736, 3565287, 973764, 21477737, 10617423]
}

df1 = pd.DataFrame(data)

# Sample data for the treemap (you need to replace filtered_df with your actual dataframe)
# Assuming filtered_df is a DataFrame with 'State', 'City', 'Start_Time', and 'End_Time' columns
filtered_df = pd.DataFrame({
    'State': ['CA', 'CA', 'TX', 'TX', 'NY', 'NY', 'FL', 'FL', 'IL', 'IL'],
    'City': ['Los Angeles', 'San Francisco', 'Houston', 'Dallas', 'New York', 'Buffalo', 'Miami', 'Orlando', 'Chicago', 'Springfield'],
    'Counts': [100, 150, 200, 250, 300, 350, 400, 450, 500, 550],
    'Start_Time': pd.date_range(start='1/1/2020', periods=10, freq='ME'),
    'End_Time': pd.date_range(start='1/1/2021', periods=10, freq='ME')
})

# Initialize the Dash app
app = dash.Dash(__name__)

# Define the layout for the weather page
layout = html.Div([
    html.H1('Weather Page'),
    html.Div([
        html.Label('Select Time Range'),
        dcc.RangeSlider(
            id='time-range-slider',
            min=filtered_df['Start_Time'].min().timestamp(),
            max=filtered_df['End_Time'].max().timestamp(),
            value=[filtered_df['Start_Time'].min().timestamp(), filtered_df['End_Time'].max().timestamp()],
            marks={int(ts): datetime.datetime.fromtimestamp(ts).strftime('%Y-%m') for ts in filtered_df['Start_Time'].map(datetime.datetime.timestamp).unique()},
            step=None
        ),
    ], style={'width': '80%', 'margin': 'auto'}),
    dcc.Graph(id='choropleth-graph'),
    dcc.Graph(id='treemap-graph')
])

app.layout = layout

# Callback to update the graphs based on slider values
@app.callback(
    [Output('choropleth-graph', 'figure'),
     Output('treemap-graph', 'figure')],
    [Input('time-range-slider', 'value')]
)
def update_graphs(time_range):
    # Convert slider values back to datetime
    start_time = datetime.datetime.fromtimestamp(time_range[0])
    end_time = datetime.datetime.fromtimestamp(time_range[1])

    # Filter the dataframe based on the slider values
    filtered_df1 = df1  # Assuming df1 does not have time columns, it stays unchanged

    filtered_df2 = filtered_df[(filtered_df['Start_Time'] >= start_time) &
                               (filtered_df['End_Time'] <= end_time)]

    # Update choropleth map
    fig_choropleth = px.choropleth(filtered_df1,
                                   locations='state',
                                   locationmode="USA-states",
                                   color='population',
                                   scope="usa",
                                   title="US States Population",
                                   labels={'population': 'Population'},
                                   color_continuous_scale="Viridis")

    # Aggregate data by State and City for treemap
    state_city_counts = filtered_df2.groupby(['State', 'City']).size().reset_index(name='Counts')

    # Get top 5 cities per state
    top_cities_per_state = state_city_counts.groupby('State').apply(lambda x: x.nlargest(10, 'Counts')).reset_index(drop=True)

    # Get the top 5 states by total accident counts
    top_states = top_cities_per_state.groupby('State')['Counts'].sum().nlargest(5).index
    top_cities_top_states = top_cities_per_state[top_cities_per_state['State'].isin(top_states)]

    # Update treemap
    fig_treemap = px.treemap(top_cities_top_states,
                             path=['State', 'City'],
                             values='Counts')

    fig_treemap.update_layout(title="Top 5 Cities per Top 5 States by Accident Counts",
                              width=1000, height=700)

    return fig_choropleth, fig_treemap

if __name__ == '__main__':
    app.run_server(debug=True)
