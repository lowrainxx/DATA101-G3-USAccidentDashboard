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

 # Convert 'Start_Time' to datetime format
df['Start_Time'] = pd.to_datetime(df['Start_Time'])

# Function to prepare data
def prepare_data():

    # Calculate value counts for each hour, day, and month
    byhour = df['Hour'].value_counts().reset_index()
    byhour.columns = ['Hour', 'Count']
    byhour = byhour.sort_values(by="Hour")

    df['Month'] = df['Start_Time'].dt.to_period('M').astype(str)  # Ensure Month is in the correct format
    bymonth = df['Month'].value_counts().reset_index()
    bymonth.columns = ['Month', 'Count']
    bymonth['Month'] = pd.to_datetime(bymonth['Month'])
    bymonth = bymonth.sort_values(by="Month")
    
    byday = df['Day'].value_counts().reset_index()
    byday.columns = ['Day', 'Count']
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
        color_continuous_scale="blues",
    )
    fig_choropleth.update_layout(
        paper_bgcolor='rgba(0,0,0,0)', 
        plot_bgcolor='rgba(0,0,0,0)', # Transparent background
        width=1200, height=800,
        margin=dict(l=1, r=1, t=1, b=1),
        geo=dict(
            bgcolor='rgba(0,0,0,0)', # Set background color of the choropleth
            visible=True,
            lakecolor='rgba(0,0,0,0)',  
            showland=True,
            landcolor='rgba(0,0,0,0)',  
        ),
        coloraxis_colorbar=dict(
            title="Accident Count",
            orientation="h",
            tickfont=dict(size=15, color='Yellow'),  
            title_font=dict(size=20, color='Yellow', weight='bold'),  
            len=0.9, 
            thickness=10, 
            x=0.5,  # Center horizontally
            xanchor="center",  # Center the color bar horizontally
            y=0.9,  # Position above the plot
            yanchor="bottom"  # Anchor at the bottom of the specified y value
        )
    ) 
    return fig_choropleth

# Treemap based on accident counts per city within states
def create_treemap(filtered_df):
    state_city_counts = filtered_df.groupby(['State', 'City']).size().reset_index(name='Counts')
    top_states = state_city_counts.groupby('State')['Counts'].sum().nlargest(5).index
    top_cities_top_states = state_city_counts[state_city_counts['State'].isin(top_states)]

    # If you want to show more or fewer cities per state, adjust here
    # top_cities_per_state = top_cities_top_states.groupby('State').apply(lambda x: x.nlargest(10, 'Counts')).reset_index(drop=True)

    fig_treemap = px.treemap(
        top_cities_top_states,
        path=['State', 'City'],
        values='Counts',
        title="Top 5 States by Accident Counts",
        color_discrete_sequence=px.colors.sequential.haline,
    )

    fig_treemap.update_layout(
        paper_bgcolor='rgba(0,0,0,0)', 
        plot_bgcolor='rgba(0,0,0,0)', # Transparent background
        width=1000, height=700,
        margin=dict(l=1, r=20, t=30, b=1),
        geo=dict(
            bgcolor='rgba(0,0,0,0)', # Set background color of the choropleth
        ),title={
            'text': "Top 5 States with the Highest Accident Counts",
            'font': {
                'size': 20,  
                'color': 'Yellow', 
                'weight': 'bold',
            },
            'x': 0.5,  # Center align title horizontally
            'xanchor': 'center',  # Horizontal anchor point
            'y': 1,  # Vertical position of title
            'yanchor': 'top'  # Vertical anchor point
        },
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
    severity_weather['Severity'] = severity_weather['Severity'].astype(str)

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
        labels={'Count': 'Number of Accidents'},
        color_discrete_map={
            '1': '#fae363', # Light yellow
            '2': '#636efa', # Purpleish Blue
            '3': 'rgb(250, 167, 99)', # Light Orange
            '4': '#63d7fa', # Cyan
        },
    )
    fig_stacked_bar.update_layout(
        paper_bgcolor='rgba(0,0,0,0)', 
        plot_bgcolor='rgba(0,0,0,0)',
        height=800,
        margin=dict(l=1, r=1, t=30, b=50),
        xaxis=dict(
            title=dict(
                text='Weather Condition',
                font=dict(
                    size=20, color='lightblue', weight='bold'   
                )
            ),
            tickfont=dict(
                size=20, color='yellow'  
            ),
            linecolor='white', linewidth=2, 
        ),
        yaxis=dict(
            title=dict(
                text='Number of Accidents',
                font=dict(
                    size=25, color='lightblue',  weight='bold'   
                )
            ),
            tickfont=dict(
                size=20, color='yellow' , 
            ),
            linecolor='white', linewidth=2, 
        ),
        legend=dict(
            title=dict(
                text="Severity",
                font=dict(size=25, color='yellow', weight='bold')
            ),
            font=dict(size=30, color='yellow'),
        )
    )  
    return fig_stacked_bar

# Line chart accidents over time
def create_line_graph(selected_option, filtered_df):
    if filtered_df is None:
        filtered_df = df

    if selected_option == 'Hour':
        filtered_df['Hour'] = filtered_df['Start_Time'].dt.hour
        data = filtered_df['Hour'].value_counts().reset_index()
        data.columns = ['Hour', 'Count']
        data = data.sort_values(by='Hour')
        fig = px.line(data, x='Hour', y='Count', title='Accidents by Hour', markers=True)

    elif selected_option == 'DayOfTheMonth':
        filtered_df['Day'] = filtered_df['Start_Time'].dt.day
        data = filtered_df['Day'].value_counts().reset_index()
        data.columns = ['Day', 'Count']
        data = data.sort_values(by='Day')
        fig = px.line(data, x='Day', y='Count', title='Accidents by Day', markers=True)

    elif selected_option == 'Monthly':
        filtered_df['Month'] = filtered_df['Start_Time'].dt.to_period('M').astype(str)
        data = filtered_df['Month'].value_counts().reset_index()
        data.columns = ['Month', 'Count']
        data['Month'] = pd.to_datetime(data['Month'])
        data = data.sort_values(by='Month')
        fig = px.line(data, x='Month', y='Count', title='Accidents by Month', markers=True)

    fig.update_traces(
        line=dict(
            width=8, 
        ),
        marker=dict(
            size=15, color='yellow', 
        )
    )

    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)', 
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=1, r=1, t=30, b=1),
        title={
            'font': {
                'size': 28, 'color': 'Yellow', 'weight': 'bold',
            },
        'x': 0.1,  # Center align title horizontally
        'xanchor': 'center',  # Horizontal anchor point
        'y': 1,  # Vertical position of title
        'yanchor': 'top'  # Vertical anchor point
        },
        xaxis=dict(
            title=dict(
                text='Time Period',
                font=dict(
                    size=20, color='lightblue', weight='bold'   
                )
            ),
            tickfont=dict(
                size=20, color='yellow'  
            ),
            linecolor='white', linewidth=2, 
        ),
        yaxis=dict(
            title=dict(
                text='Number of Accidents',
                font=dict(
                    size=25, color='lightblue',  weight='bold'   
                )
            ),
            tickfont=dict(
                size=20, color='yellow' , 
            ),
            linecolor='white', linewidth=2, 
        ),
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

# Update the date range slider marks to include static start and end marks
marks = {int((date - df['Start_Time'].min()).days): date.strftime('%Y-%m') 
         for date in pd.date_range(df['Start_Time'].min(), df['Start_Time'].max(), freq='6MS')}

# Add static start and end marks
marks[0] = '2020-01-01'
marks[int((df['Start_Time'].max() - df['Start_Time'].min()).days)] = '2022-12-31'

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
    html.Div([
        html.Span('Date Range: ', id='date-range-label'),
        html.Span(id='date-range')
        ], id='date-range-display'
    ),
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
            marks=marks,
            tooltip={"always_visible": False},
            className="date-range-slider"
        ),
        # End Date Picker
        dcc.DatePickerSingle(
            id='end-date-picker',
            min_date_allowed=df['Start_Time'].min().date(),
            max_date_allowed=df['Start_Time'].max().date(),
            initial_visible_month=df['Start_Time'].max().date(),
            date=df['Start_Time'].max().date(),
            display_format='YYYY-MM-DD',
        ),
    ], className='datepicker-container'),
    html.Div([
        html.Button('Change Date Range', id='submit-button', n_clicks=0),
    ], className='submit-button-container'),

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

    html.Div([
        html.H2('Number of Accidents Over Time', id='linegraph-label'),
        dcc.RadioItems(
            id='linegraph-radioitems',
            options=[
                {'label': 'by Hour', 'value': 'Hour'},
                {'label': 'by Day', 'value': 'DayOfTheMonth'},
                {'label': 'by Month', 'value': 'Monthly'}
            ],
            value='Monthly',
            inline=True,
            className='linegraph-radioitems-container'
        ),
        html.Div(children=[
            dcc.Graph(id='linegraph')
        ], id='linegraph-container')
    ], className='linegraph-container'), 

    # Stacked bar chart for severity and weather conditions
    html.Div([
        html.H2('Accidents by Severity and Weather Conditions', id='stackedbar-label'),
        html.Div([
            html.Div([
                html.I(className='fas fa-filter'), 
            ], id='stackedbar-filter-icon'),
            html.Label('Weather Condition Filter'),
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
        ], id='stackedbar-filter-container'),
        html.Div(children=[
                dcc.Graph(id='severity-weather-stacked-bar')
            ], id='stackedbarchart-container'
        ),
    ], id='stackedbar-container'), 
])

# Callback to sync date picker and slider
@dash.callback(
    [Output('start-date-picker', 'date'),
     Output('end-date-picker', 'date'),
     Output('date-range-slider', 'value')],
    [Input('date-range-slider', 'value'),
     Input('start-date-picker', 'date'),
     Input('end-date-picker', 'date')],
    [State('start-date-picker', 'date'),
     State('end-date-picker', 'date'),
     State('date-range-slider', 'value')]
)
def sync_date_picker_slider(slider_range, start_date, end_date, current_start_date, current_end_date, current_slider_range):
    ctx = dash.callback_context
    triggered_id = ctx.triggered[0]['prop_id'].split('.')[0]

    if triggered_id == 'date-range-slider':
        start_date = (df['Start_Time'].min() + pd.Timedelta(days=slider_range[0])).date()
        end_date = (df['Start_Time'].min() + pd.Timedelta(days=slider_range[1])).date()
        return start_date, end_date, slider_range

    elif triggered_id in ['start-date-picker', 'end-date-picker']:
        start_date = pd.to_datetime(start_date).date()
        end_date = pd.to_datetime(end_date).date()
        slider_range[0] = (pd.to_datetime(start_date) - df['Start_Time'].min()).days
        slider_range[1] = (pd.to_datetime(end_date) - df['Start_Time'].min()).days
        return start_date, end_date, slider_range

    return current_start_date, current_end_date, current_slider_range

# Callback to display selected date range
@dash.callback(
    Output('date-range', 'children'),
    Input('submit-button', 'n_clicks'),
    State('start-date-picker', 'date'),
    State('end-date-picker', 'date')
)
def update_date_range_display(n_clicks, start_date, end_date):
    df_copy = df.copy()  # Ensure we're working with a copy

    if n_clicks:
        start_date = pd.to_datetime(start_date).strftime('%B %d, %Y')
        end_date = pd.to_datetime(end_date).strftime('%B %d, %Y')
        return f"{start_date} -> {end_date}"
    else:  # Default
        start_date = df_copy['Start_Time'].min().strftime('%B %d, %Y')
        end_date = df_copy['Start_Time'].max().strftime('%B %d, %Y')
        return f"{start_date} -> {end_date}"

# Combined callback to update all graphs based on date range
@dash.callback([
        Output('choropleth-map', 'figure'),
        Output('treemap', 'figure'),
        Output('linegraph', 'figure'),
        Output('severity-weather-stacked-bar', 'figure')
    ],[
        Input('submit-button', 'n_clicks'),
        Input('linegraph-radioitems', 'value'),
        Input('weather-condition-dropdown', 'value')
    ],[
        State('start-date-picker', 'date'),
        State('end-date-picker', 'date')
    ]
)
def update_all_graphs(n_clicks, selected_option, selected_weather_conditions, start_date, end_date):
    # Filter dataframe based on date range
    if n_clicks > 0 and start_date and end_date:
        filtered_df = df[(df['Start_Time'] >= start_date) & (df['Start_Time'] <= end_date)].copy()  # Ensure we're working with a copy
    else:
        filtered_df = df.copy()

    # Update choropleth map
    choropleth = create_choropleth(filtered_df)

    # Update treemap
    treemap = create_treemap(filtered_df)

    # Update accidents over time graph based on selected option
    accidents_over_time = create_line_graph(selected_option, filtered_df)
    
    # Update stacked bar chart with selected weather conditions
    stacked_bar_chart = create_stacked_bar_chart(filtered_df, selected_weather_conditions)
    
    return choropleth, treemap, accidents_over_time, stacked_bar_chart
