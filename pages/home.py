# home.py
import dash
from dash import dcc, html, register_page
import plotly.express as px
import logging
from dash.dependencies import Input, Output, State
import pandas as pd
from data import df

# Setup logging
logging.basicConfig(level=logging.INFO)

# Register Home page
register_page(__name__, path='/')

# Load data
if df is None:
    raise ValueError("home.py : DataFrame is not loaded.")

# Function to prepare data
def prepare_data():
    byhour = df['Hour'].value_counts().reset_index()
    byhour.columns = ['Hour', 'Count']
    bymonth = df['Month'].value_counts().reset_index()
    bymonth.columns = ['Month', 'Count']
    byday = df['Day'].value_counts().reset_index()
    byday.columns = ['Day', 'Count']

    byhour = byhour.sort_values(by="Hour")
    bymonth = bymonth.sort_values(by="Month")
    byday = byday.sort_values(by="Day")

    return df, byhour, bymonth, byday

# Choropleth map based on accident counts per state
def create_choropleth(filtered_df):
    accident_counts = filtered_df['State'].value_counts().reset_index()
    accident_counts.columns = ['State', 'Accident_Count']

    fig_choropleth = px.choropleth(
        accident_counts,
        locations='State',
        locationmode="USA-states",
        color='Accident_Count',
        scope="usa",
        labels={'Accident_Count': 'Accident Count'},
        color_continuous_scale="Viridis"
    )
    fig_choropleth.update_layout(
        paper_bgcolor='rgba(0,0,0,0)', 
        plot_bgcolor='rgba(0,0,0,0)', # Transparent background
        width=1200, height=800,
        margin=dict(l=1, r=1, t=1, b=1),
        geo=dict(
            bgcolor='white', # Set background color of the choropleth
            showcoastlines=True,
        ),
    ) 
    return fig_choropleth

# Treemap based on accident counts per city within states
def create_treemap(filtered_df):
    state_city_counts = filtered_df.groupby(['State', 'City']).size().reset_index(name='Counts')
    top_cities_per_state = state_city_counts.groupby('State').apply(lambda x: x.nlargest(10, 'Counts')).reset_index(drop=True)
    top_states = top_cities_per_state.groupby('State')['Counts'].sum().nlargest(5).index
    top_cities_top_states = top_cities_per_state[top_cities_per_state['State'].isin(top_states)]

    fig_treemap = px.treemap(
        top_cities_top_states,
        path=['State', 'City'],
        values='Counts',
        title="Top 10 Cities per Top 5 States by Accident Counts"
    )
    fig_treemap.update_layout(
        width=700, 
        height=700
    )
    return fig_treemap

#stacked bar chart
def create_stacked_bar_chart(filtered_df, selected_weather_conditions):
    weather_columns = ['Sand', 'Dust', 'Fog', 'Cloudy', 'Windy', 'Fair', 'Snow', 'Wintry Mix', 'Squall', 'Rain',
                       'Sleet', 'Hail', 'Thunderstorm', 'Tornado', 'Haze', 'Drizzle', 'Mist', 'Shower', 'Smoke']
    
    # If 'All' is selected, use all weather conditions
    if 'All' in selected_weather_conditions:
        selected_weather_conditions = weather_columns
    
    weather_conditions = []

    for weather in selected_weather_conditions:
        if weather in weather_columns:
            temp_df = filtered_df[filtered_df[weather] == True]
            temp_df_grouped = temp_df.groupby('Severity').size().reset_index(name='Count')
            temp_df_grouped['Weather_Condition'] = weather
            weather_conditions.append(temp_df_grouped)

    if not weather_conditions:
        return px.bar(title='No Data Available for Selected Filters')

    severity_weather = pd.concat(weather_conditions, ignore_index=True)

    # Sorting by total count per weather condition
    total_counts = severity_weather.groupby('Weather_Condition')['Count'].sum().reset_index()
    total_counts = total_counts.sort_values(by='Count', ascending=False)
    sorted_conditions = total_counts['Weather_Condition'].tolist()

    severity_weather['Weather_Condition'] = pd.Categorical(severity_weather['Weather_Condition'], categories=sorted_conditions, ordered=True)

    # Sorting each weather condition by severity count
    severity_weather = severity_weather.sort_values(by=['Weather_Condition', 'Count'], ascending=[True, False])

    fig_stacked_bar = px.bar(
        severity_weather,
        x='Weather_Condition',
        y='Count',
        color='Severity',
        title='Number of Accidents by Severity and Weather Conditions',
        labels={'Count': 'Number of Accidents'},
    )
    fig_stacked_bar.update_layout(
        width=1800, 
        height=800
    )  
    return fig_stacked_bar

#Line chart accidents over time
def create_accidents_over_time_graph(selected_option):
    if selected_option == 'Hour':
        fig = px.line(byhour, x='Hour', y='Count', title='Accidents by Hour')
    elif selected_option == 'DayOfTheMonth':
        fig = px.line(byday, x='Day', y='Count', title='Accidents by Day of the Month')
    elif selected_option == 'Monthly':
        fig = px.line(bymonth, x='Month', y='Count', title='Accidents by Month')
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)', 
        plot_bgcolor='rgba(0,0,0,0)'
    )
    return fig

df['Start_Time'] = pd.to_datetime(df['Start_Time'])
start_date = df['Start_Time'].min()
end_date = df['Start_Time'].max()
date_range = pd.date_range(start=start_date, end=end_date, freq='6ME')

# Group by day and count the number of accidents per day
accidents_per_day = df.groupby(df['Start_Time'].dt.date).size()
average_per_day = accidents_per_day.mean()
accidents_per_month = df.groupby(df['Start_Time'].dt.to_period('M')).size()
average_per_month = accidents_per_month.mean()
accidents_per_year = df.groupby(df['Start_Time'].dt.to_period('Y')).size()
average_per_year = accidents_per_year.mean()
each_severity_counts = df['Severity'].value_counts().sort_index()

# Prepare data once and reuse in callbacks
df, byhour, bymonth, byday = prepare_data()

def format_number_with_spaces(number):
    return '{:,.0f}'.format(number).replace(',', ' ')

# Define the layout for the home page
layout = html.Div([

    # Stats
    html.Div([
        html.Div([
            html.Div([
                html.Span(f'{format_number_with_spaces(average_per_day)}', className='stat-value'),
                html.Span('Average per Day', className='stat-label')
            ], className='stat-container'),
            html.Div([
                html.Span(f'{format_number_with_spaces(average_per_month)}', className='stat-value'),
                html.Span('Average per Month', className='stat-label')
            ], className='stat-container'),
            html.Div([
                html.Span(f'{format_number_with_spaces(average_per_year)}', className='stat-value'),
                html.Span('Average per Year', className='stat-label')
            ], className='stat-container'),
            html.Div([
                html.Span(f'{format_number_with_spaces(each_severity_counts[1])}', className='stat-value'),
                html.Span('Total Accidents with Severity 1', className='stat-label')
            ], className='stat-container'),
            html.Div([
                html.Span(f'{format_number_with_spaces(each_severity_counts[2])}', className='stat-value'),
                html.Span('Total Accidents with Severity 2', className='stat-label')
            ], className='stat-container'),
            html.Div([
                html.Span(f'{format_number_with_spaces(each_severity_counts[3])}', className='stat-value'),
                html.Span('Total Accidents with Severity 3', className='stat-label')
            ], className='stat-container'),
            html.Div([
                html.Span(f'{format_number_with_spaces(each_severity_counts[4])}', className='stat-value'),
                html.Span('Total Accidents with Severity 4', className='stat-label')
            ], className='stat-container')
        ], className='stats'),
    ]),

    # Date Range
    html.Div(id='date-range-display'),
    html.Div([
        # Start Date Picker
        dcc.DatePickerSingle(
            id='start-date-picker',
            min_date_allowed=df['Start_Time'].min().date(),
            max_date_allowed=df['Start_Time'].max().date(),
            initial_visible_month=df['Start_Time'].min().date(),
            date=df['Start_Time'].min().date(),
            display_format='YYYY-MM-DD'
        ),
        # Slider
        dcc.RangeSlider(
            id='date-range-slider',
            min=0,
            max=(df['Start_Time'].max() - df['Start_Time'].min()).days,
            value=[0, (df['Start_Time'].max() - df['Start_Time'].min()).days],
            marks={int((date - start_date).days): date.strftime('%Y-%m') for date in date_range}, 
            tooltip={"placement": "bottom", "always_visible": True},
            className="date-range-slider"
        ),
        # End Date Picker
        dcc.DatePickerSingle(
            id='end-date-picker',
            min_date_allowed=df['Start_Time'].min().date(),
            max_date_allowed=df['Start_Time'].max().date(),
            initial_visible_month=df['Start_Time'].max().date(),
            date=df['Start_Time'].max().date(),
            display_format='YYYY-MM-DD'
        ),
        # Submit
        html.Button('Submit', id='submit-button', n_clicks=0)
    ], className='datepicker-container'),

    # Chloropleth & Tree Map
    html.Div([
            html.Div([
                    dcc.Graph(id='choropleth-map'),
                ], id='chloropleth-map-container',
            ),

            html.Div([
                    dcc.Graph(id='treemap')
                ], id='treemap-container',
            ),
        ], id='ct-container'
    ),

    html.H2('Number of Accidents over Time'),
    dcc.RadioItems(
        id='radioitems',
        options=[
            {'label': 'Hour', 'value': 'Hour'},
            {'label': 'DayOfTheMonth', 'value': 'DayOfTheMonth'},
            {'label': 'Monthly', 'value': 'Monthly'}
        ],
        value='DayOfTheMonth',
        inline=True
    ),
    html.Div(children=[
            dcc.Graph(id='linegraph')
        ], id='linegraph-container'
    ), 

    ##
    # Filter dropdown for weather condition
    # Stacked bar chart for severity and weather conditions
    html.H2('Accidents by Severity and Weather Conditions'),
    html.Div([
        html.Label('Weather Condition'),
        dcc.Dropdown(
            id='weather-condition-dropdown',
            options=[
                {'label': 'All', 'value': 'All'}  # Option to show all weather conditions
            ] + [{'label': condition, 'value': condition} for condition in
                ['Sand', 'Dust', 'Fog', 'Cloudy', 'Windy', 'Fair', 'Snow', 'Wintry Mix', 'Squall', 'Rain',
                'Sleet', 'Hail', 'Thunderstorm', 'Tornado', 'Haze', 'Drizzle', 'Mist', 'Shower', 'Smoke']],
            value=['All'],  # Default value
            multi=True,  # Allow multiple selections
            style={'width': '300px', 'margin': '0'}
        ),
        html.Div(children=[
                dcc.Graph(id='severity-weather-stacked-bar')
            ], id='stackedbarchart-container'
        ),
        
    ], id='stackedbar-container'), 
])

# Callback to update line graph
# @dash.callback(
#     Output('linegraph', 'figure'),
#     Input('radioitems', 'value')
# )
# def update_graph(selected_option):
#     if selected_option == 'Hour':
#         fig = px.line(byhour, x='Hour', y='Count', title='Accidents by Hour')
#     elif selected_option == 'DayOfTheMonth':
#         fig = px.line(byday, x='Day', y='Count', title='Accidents by Day of the Month')
#     elif selected_option == 'Monthly':
#         fig = px.line(bymonth, x='Month', y='Count', title='Accidents by Month')
#     return fig

# Standalone callback to update the stacked bar chart based on the weather condition dropdown
@dash.callback(
    Output('severity-weather-stacked-bar', 'figure'),
    [Input('weather-condition-dropdown', 'value')],
    [State('start-date-picker', 'date'),
     State('end-date-picker', 'date')]
)
def update_stacked_bar_chart(selected_weather_conditions, start_date, end_date):
    filtered_df = df[(df['Start_Time'] >= start_date) & (df['Start_Time'] <= end_date)]
    
    # Update stacked bar chart with selected weather conditions
    return create_stacked_bar_chart(filtered_df, selected_weather_conditions)

# Callback to sync date picker and slider
@dash.callback(
    [Output('start-date-picker', 'date'),
     Output('end-date-picker', 'date'),
     Output('date-range-slider', 'value')],
    [Input('date-range-slider', 'value'),
     Input('start-date-picker', 'date'),
     Input('end-date-picker', 'date')]
)
def sync_date_picker_slider(slider_range, start_date, end_date):
    ctx = dash.callback_context
    triggered_id = ctx.triggered[0]['prop_id'].split('.')[0]

    if triggered_id == 'date-range-slider':
        start_date = (df['Start_Time'].min() + pd.Timedelta(days=slider_range[0])).date()
        end_date = (df['Start_Time'].min() + pd.Timedelta(days=slider_range[1])).date()
    elif triggered_id in ['start-date-picker', 'end-date-picker']:
        start_date = pd.to_datetime(start_date).date()
        end_date = pd.to_datetime(end_date).date()
        slider_range[0] = (pd.to_datetime(start_date) - df['Start_Time'].min()).days
        slider_range[1] = (pd.to_datetime(end_date) - df['Start_Time'].min()).days

    return start_date, end_date, slider_range

# Callback to display selected date range
@dash.callback(
    Output('date-range-display', 'children'),
    Input('submit-button', 'n_clicks'),
    State('start-date-picker', 'date'),
    State('end-date-picker', 'date')
)
def update_date_range_display(n_clicks, start_date, end_date):
    if n_clicks:
        start_date = pd.to_datetime(start_date).strftime('%B %d, %Y')
        end_date = pd.to_datetime(end_date).strftime('%B %d, %Y')
        return f"Date Range: {start_date} -> {end_date}"
    else: # Default
        start_date = df['Start_Time'].min().strftime('%B %d, %Y')
        end_date = df['Start_Time'].max().strftime('%B %d, %Y')
        return f"Date Range: {start_date} -> {end_date}"
    
# Combined callback to update all graphs based on date range
@dash.callback(
    [
        Output('choropleth-map', 'figure'),
        Output('treemap', 'figure'),
        Output('linegraph', 'figure')
    ],
    Input('submit-button', 'n_clicks'),
    State('start-date-picker', 'date'),
    State('end-date-picker', 'date'),
    State('radioitems', 'value')
)
def update_all_graphs(n_clicks, start_date, end_date, time_interval):
    if n_clicks > 0:
        filtered_df = df[(df['Start_Time'] >= start_date) & (df['Start_Time'] <= end_date)]

        # Update choropleth map
        choropleth = create_choropleth(filtered_df)
        
        # Update treemap
        treemap = create_treemap(filtered_df)

        # Update accidents over time
        accidents_over_time = create_accidents_over_time_graph(time_interval)
        
        return choropleth, treemap, accidents_over_time 
    
    # Return original figures if no clicks
    return create_choropleth(df), create_treemap(df), create_accidents_over_time_graph('DayOfTheMonth')