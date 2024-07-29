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

    severity_counts = df['Severity'].value_counts().reset_index()
    severity_counts.columns = ['Severity', 'count']

    severity_weather = df.groupby(['Severity', 'Weather_Condition']).size().reset_index(name='Count')

    stacked_bar = px.bar(
        severity_weather,
        x='Severity',
        y='Count',
        color='Weather_Condition',
        title='Number of Accidents by Severity and Weather Conditions',
        labels={'Count': 'Number of Accidents'},
    )
    return df, stacked_bar, byhour, bymonth, byday

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
        title="Accidents by State",
        labels={'Accident_Count': 'Accident Count'},
        color_continuous_scale="Viridis"
    )
    fig_choropleth.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)') # Transparent background
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
        title="Top 5 Cities per Top 5 States by Accident Counts"
    )
    fig_treemap.update_layout(width=1000, height=700)
    return fig_treemap

# Donut Charts
def create_pie_charts(filtered_df):
    pie_charts = []
    for severity in range(1, 5):
        # Filter for the specific severity
        severity_counts = filtered_df[filtered_df['Severity'] == severity]
        
        # Calculate the percentage of each severity out of the total accidents
        total_accidents = len(filtered_df)
        severity_count = len(severity_counts)
        percentage = (severity_count / total_accidents) * 100

        # Create a DataFrame for the pie chart
        severity_df = pd.DataFrame({
            'Severity': [f'Severity {severity}', 'Others'],
            'Count': [severity_count, total_accidents - severity_count],
            'Percentage': [percentage, 100 - percentage]
        })

        # Create the pie chart
        pie_chart = px.pie(severity_df, names='Severity', values='Percentage', title=f'Severity {severity} Accidents',)
        pie_chart.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
        pie_charts.append(pie_chart)
    
    return pie_charts

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
df, stacked_bar, byhour, bymonth, byday = prepare_data()

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
    html.H2('Select Date Range'),
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

    html.Div([
        html.Div([
            dcc.Graph(id='choropleth-map'),
        ], style={'display': 'inline-block', 'width': '60%', 'vertical-align': 'top'}),

        html.Div([
            dcc.Graph(id='treemap')
        ], style={'display': 'inline-block', 'width': '40%', 'vertical-align': 'top'})

        # html.Div([
        #     html.Div([
        #         dcc.Graph(id='pie-chart-severity-1'),
        #         dcc.Graph(id='pie-chart-severity-2')
        #     ], style={'display': 'flex'}),

        #     html.Div([
        #         dcc.Graph(id='pie-chart-severity-3'),
        #         dcc.Graph(id='pie-chart-severity-4')
        #     ], style={'display': 'flex'})
        # ], style={'display': 'inline-block', 'width': '49%', 'vertical-align': 'top'})
    ], style={'width': '100%', 'height': '100%' , 'display': 'flex'}),

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
        dcc.Graph(id='graph')
    ], style={'display': 'flex', 'flex-wrap': 'wrap', 'width': '48%', 'margin': '0 auto'}),

    # stacked bar chart for severity and weather conditions
    html.H2('Accidents by Severity and Weather Conditions'),
    html.Div(children=[
        dcc.Graph(id='severity-weather-stacked-bar', figure=stacked_bar)
    ], style={'display': 'flex', 'flex-wrap': 'wrap', 'width': '48%', 'margin': '0 auto'}),
])

# Callback to update line graph
@dash.callback(
    Output('graph', 'figure'),
    Input('radioitems', 'value')
)
def update_graph(selected_option):
    if selected_option == 'Hour':
        fig = px.line(byhour, x='Hour', y='Count', title='Accidents by Hour')
    elif selected_option == 'DayOfTheMonth':
        fig = px.line(byday, x='Day', y='Count', title='Accidents by Day of the Month')
    elif selected_option == 'Monthly':
        fig = px.line(bymonth, x='Month', y='Count', title='Accidents by Month')
    return fig

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

# Combined callback to update all graphs based on date range
@dash.callback(
    [Output('choropleth-map', 'figure'),
     Output('treemap', 'figure')],
    #  Output('pie-chart-severity-1', 'figure'),
    #  Output('pie-chart-severity-2', 'figure'),
    #  Output('pie-chart-severity-3', 'figure'),
    #  Output('pie-chart-severity-4', 'figure')],
    Input('submit-button', 'n_clicks'),
    State('start-date-picker', 'date'),
    State('end-date-picker', 'date')
)
def update_all_graphs(n_clicks, start_date, end_date):
    if n_clicks > 0:
        filtered_df = df[(df['Start_Time'] >= start_date) & (df['Start_Time'] <= end_date)]

        # Update choropleth map
        choropleth = create_choropleth(filtered_df)
        
        # Update treemap
        treemap = create_treemap(filtered_df)
        
        # Create pie charts
        # pie_charts = create_pie_charts(filtered_df)
        
        return choropleth, treemap #, pie_charts[0], pie_charts[1], pie_charts[2], pie_charts[3]
    
    # Return original figures if no clicks
    # pie_charts = create_pie_charts(df)
    return create_choropleth(df), create_treemap(df) #, pie_charts[0], pie_charts[1], pie_charts[2], pie_charts[3]

logging.info('DONE HOME.PY')
