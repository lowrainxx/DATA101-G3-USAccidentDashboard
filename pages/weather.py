import dash
from dash import dcc, html, register_page, callback, Input, Output
import plotly.express as px
import pandas as pd

# Register Weather page
register_page(__name__, path='/weather')

# Sample data for the choropleth map
data = {
    'state': ['AL', 'AK', 'AZ', 'AR', 'CA', 'CO', 'CT', 'DE', 'FL', 'GA'],
    'population': [4903185, 731545, 7278717, 3017804, 39512223, 5758736, 3565287, 973764, 21477737, 10617423]
}

df1 = pd.DataFrame(data)

# Sample data for the treemap (you need to replace filtered_df with your actual dataframe)
filtered_df = pd.DataFrame({
    'State': ['CA', 'CA', 'TX', 'TX', 'NY', 'NY', 'FL', 'FL', 'IL', 'IL'],
    'City': ['Los Angeles', 'San Francisco', 'Houston', 'Dallas', 'New York', 'Buffalo', 'Miami', 'Orlando', 'Chicago', 'Springfield'],
    'Counts': [100, 150, 200, 250, 300, 350, 400, 450, 500, 550],
    'Start_Time': pd.date_range(start='1/1/2020', periods=10, freq='M'),
    'End_Time': pd.date_range(start='1/1/2020', periods=10, freq='M') + pd.DateOffset(months=1)
})

# Define the layout for the weather page
layout = html.Div([
    html.Div([
        html.H1('Weather Page'),
        html.Label('Select Time Range:'),
        dcc.DatePickerRange(
            id='date-picker-range',
            start_date=filtered_df['Start_Time'].min(),
            end_date=filtered_df['End_Time'].max(),
            display_format='YYYY-MM-DD'
        ),
    ], style={'text-align': 'center', 'padding': '10px'}),
    html.Div([
        dcc.Graph(id='choropleth-map'),
        dcc.Graph(id='treemap')
    ], className='main-content')
])

# Callback to update the graphs based on the selected date range
@callback(
    [Output('choropleth-map', 'figure'),
     Output('treemap', 'figure')],
    [Input('date-picker-range', 'start_date'),
     Input('date-picker-range', 'end_date')]
)
def update_graphs(start_date, end_date):
    filtered_df_range = filtered_df[
        (filtered_df['Start_Time'] >= start_date) & (filtered_df['End_Time'] <= end_date)
    ]

    # Update choropleth map
    fig_choropleth = px.choropleth(df1,
                                   locations='state',
                                   locationmode="USA-states",
                                   color='population',
                                   scope="usa",
                                   title="US States Population",
                                   labels={'population': 'Population'},
                                   color_continuous_scale="Viridis")

    # Aggregate data by State and City
    state_city_counts = filtered_df_range.groupby(['State', 'City']).size().reset_index(name='Counts')

    # Get top 5 cities per state
    top_cities_per_state = state_city_counts.groupby('State').apply(lambda x: x.nlargest(10, 'Counts')).reset_index(drop=True)

    # Get the top 5 states by total accident counts
    top_states = top_cities_per_state.groupby('State')['Counts'].sum().nlargest(5).index
    top_cities_top_states = top_cities_per_state[top_cities_per_state['State'].isin(top_states)]

    # Creating the treemap
    fig_treemap = px.treemap(top_cities_top_states,
                             path=['State', 'City'],
                             values='Counts')

    fig_treemap.update_layout(title="Top 5 Cities per Top 5 States by Accident Counts",
                              width=1000, height=700)

    return fig_choropleth, fig_treemap
