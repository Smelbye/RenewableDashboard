import os
import dash
from dash import dcc
from dash import html
import matplotlib
import dash_bootstrap_components as dbc
from dash import html
from dash.dependencies import Input, Output
import plotly.express as px
import matplotlib.cm as cm
import pandas as pd

# Load and preprocess the data
data_files = os.listdir('dataset')
data_frames = {}

for file in data_files:
    df = pd.read_csv(f'dataset/{file}')
    key = file.split('.')[0]
    data_frames[key] = df

data_frames = {
    'renewable_share_energy': pd.read_csv('dataset/01 renewable-share-energy.csv'),
    'modern_renewable_energy_consumption': pd.read_csv('dataset/02 modern-renewable-energy-consumption.csv'),
    'modern_renewable_prod': pd.read_csv('dataset/03 modern-renewable-prod.csv'),
    'share_electricity_renewables': pd.read_csv('dataset/04 share-electricity-renewables.csv'),
    'hydropower_consumption': pd.read_csv('dataset/05 hydropower-consumption.csv'),
    'hydro_share_energy': pd.read_csv('dataset/06 hydro-share-energy.csv'),
    'share_electricity_hydro': pd.read_csv('dataset/07 share-electricity-hydro.csv'),
    'wind_generation': pd.read_csv('dataset/08 wind-generation.csv'),
    'cumulative_installed_wind_energy_capacity': pd.read_csv('dataset/09 cumulative-installed-wind-energy-capacity-gigawatts.csv'),
    'wind_share_energy': pd.read_csv('dataset/10 wind-share-energy.csv'),
    'share_electricity_wind': pd.read_csv('dataset/11 share-electricity-wind.csv'),
    'solar_energy_consumption': pd.read_csv('dataset/12 solar-energy-consumption.csv'),
    'installed_solar_PV_capacity': pd.read_csv('dataset/13 installed-solar-PV-capacity.csv'),
    'solar_share_energy': pd.read_csv('dataset/14 solar-share-energy.csv'),
    'share_electricity_solar': pd.read_csv('dataset/15 share-electricity-solar.csv'),
    'biofuel_production': pd.read_csv('dataset/16 biofuel-production.csv'),
    'installed_geothermal_capacity': pd.read_csv('dataset/17 installed-geothermal-capacity.csv'),
}    

    
# Dictionary to map the energy type to the corresponding column name and assign labels

energy_type_columns = {
    'renewable_share_energy': 'Renewables (% equivalent primary energy)',
    'hydropower_consumption': 'Electricity from hydro (TWh)',
    'wind_share_energy': 'Wind (% equivalent primary energy)',
    'solar_share_energy': 'Solar (% equivalent primary energy)',
}

energy_type_labels = {
    'renewable_share_energy': 'Renewable',
    'hydropower_consumption': 'Hydro',
    'wind_share_energy': 'Wind',
    'solar_share_energy': 'Solar',
}

#Helper Functions

def filter_continents(df):
    return df[df['Code'].notna()]

def get_continent_dataframes(df_consumption, df_production):
    continents = ['Africa', 'Asia', 'Europe', 'North America', 'Oceania', 'South America']
    consumption_columns_sum = ['Geo Biomass Other - TWh', 'Solar Generation - TWh', 'Wind Generation - TWh', 'Hydro Generation - TWh']
    production_columns_sum = ['Electricity from wind (TWh)', 'Electricity from hydro (TWh)', 'Electricity from solar (TWh)', 'Other renewables including bioenergy (TWh)']

    df_consumption['Total Consumption (TWh)'] = df_consumption[consumption_columns_sum].sum(axis=1)
    df_production['Total Production (TWh)'] = df_production[production_columns_sum].sum(axis=1)

    df_filtered_consumption = df_consumption[df_consumption['Entity'].isin(continents)].sort_values(by='Total Consumption (TWh)', ascending=False)
    df_filtered_production = df_production[df_production['Entity'].isin(continents)].sort_values(by='Total Production (TWh)', ascending=False)

    return df_filtered_consumption, df_filtered_production

def highest_renewable_share_percentage(year):
    df = data_frames['renewable_share_energy']
    df_filtered = df[df['Year'] == year]
    df_filtered = filter_continents(df_filtered)
    highest_percentage = df_filtered['Renewables (% equivalent primary energy)'].max()
    return highest_percentage

def second_biggest_continent(year):
    df_consumption = data_frames['modern_renewable_energy_consumption']
    df_production = data_frames['modern_renewable_prod']
    df_filtered_consumption, df_filtered_production = get_continent_dataframes(df_consumption[df_consumption['Year'] == year], df_production[df_production['Year'] == year])
    second_biggest = df_filtered_consumption.iloc[1]['Entity']
    return second_biggest

def highest_renewable_share_country(year):
    df = data_frames['renewable_share_energy']
    df_filtered = df[df['Year'] == year]
    df_filtered = filter_continents(df_filtered)
    highest_country = df_filtered.loc[df_filtered['Renewables (% equivalent primary energy)'].idxmax()]['Entity']
    return highest_country


# App and layout
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server

# Line Chart
@app.callback(
    Output('time-series-graph', 'figure'),
    Input('energy-type-dropdown', 'value'),
    Input('country-dropdown', 'value'),
)
def linechart(energy_type, countries):
    df = data_frames[energy_type]
    df_filtered = df[df['Entity'].isin(countries)].rename(columns={'Entity': 'Country'})

    column_name = energy_type_columns[energy_type]
    label_name = energy_type_labels[energy_type]

    # Limit the number of countries in the title to 3
    if len(countries) <=3:
        countries_str = ', '.join(countries)
    else:
        countries_str = ', '.join(countries[:3]) + ", and others"

    fig = px.line(df_filtered, x='Year', y=column_name, color='Country', title=f'Linechart comparison of {label_name} between {countries_str}')
    fig.update_layout(
        xaxis=dict(tickmode='array', tickvals=list(range(1970, 2021, 5)), tickangle=0),
        plot_bgcolor='aliceblue',
        yaxis=dict(gridcolor='lightgrey', gridwidth=0.5, zeroline=False),
        title=dict(
            text=f'Comparison of {label_name} Energy between {countries_str}',
            font=dict(size=22, family='Arial Black'),
        ),
        height=500
    )
    fig.update_xaxes(title_text='Year', title_font=dict(size=22, family='Arial, bold'))
    return fig

# Bar Chart 1
@app.callback(
    Output('comparison-graph', 'figure'),
    Input('year-slider', 'value'),
)
def barchart_1(year):
    df = data_frames['renewable_share_energy']
    df_filtered = df[df['Year'] == year]
    df_filtered = filter_continents(df_filtered)
    top_10 = df_filtered.nlargest(10, 'Renewables (% equivalent primary energy)')

    # Custom color scale
    color_scale = [(0, 'purple'), (0.6, 'steelblue'), (1, 'steelblue')]

    top_10 = top_10.sort_values(by='Renewables (% equivalent primary energy)', ascending=False)
    fig = px.bar(top_10, x='Entity', y='Renewables (% equivalent primary energy)', color='Renewables (% equivalent primary energy)', color_continuous_scale=color_scale, color_continuous_midpoint=None)
    fig.update_layout(
        plot_bgcolor='aliceblue',
        yaxis=dict(gridcolor='lightgrey', gridwidth=0.5, zeroline=False),
        showlegend=True,
        legend=dict(title=dict(text='')),
        title=dict(text='')
    )
    
    fig.update_xaxes(title_text='Country', title_font=dict(size=22, family='Arial, bold'))  
    fig.update_yaxes(title_text='Percentage % of Primary Energy in Renewables', title_font=dict(size=15, family='Arial, bold')) 
    fig.update_coloraxes(colorbar_title=dict(text=""))
    return fig

#Bar Chart 2
@app.callback(
    Output('continent-comparison-graph', 'figure'),
    Input('year-slider', 'value'),
)
def barchart_2(year):
    df_consumption = data_frames['modern_renewable_energy_consumption']
    df_production = data_frames['modern_renewable_prod']
    df_filtered_consumption, df_filtered_production = get_continent_dataframes(df_consumption[df_consumption['Year'] == year], df_production[df_production['Year'] == year])

    # Merging and reshaping data
    df_merged = df_filtered_consumption[['Entity', 'Total Consumption (TWh)']].merge(df_filtered_production[['Entity', 'Total Production (TWh)']], on='Entity', how='outer')
    df_merged = pd.melt(df_merged, id_vars='Entity', var_name='Type', value_name='TWh')

    # Add custom labels for the legend
    df_merged['Label'] = df_merged['Type'].replace({'Total Production (TWh)': 'Total Production', 'Total Consumption (TWh)': 'Total Consumption'})

    # Set color scale for the bar chart
    colorscale = ['royalblue', 'limegreen']

    fig = px.bar(df_merged, x='Entity', y='TWh', color='Label', text='TWh', barmode='group', color_discrete_sequence=colorscale)

    # Set text template and position for the bar chart
    fig.update_traces(texttemplate='%{text:.1f}', textposition='outside')

    # Set layout for the bar chart
    fig.update_layout(
        plot_bgcolor='aliceblue',
        yaxis=dict(gridcolor='lightgrey', gridwidth=0.5, zeroline=False),
        legend_title_text='Energy in TWh',
        legend=dict(itemsizing='constant', traceorder='reversed', x=1, y=1, xanchor='right', yanchor='top'), 
    )
    fig.update_xaxes(title_text='Continent', title_font=dict(size=22, family='Arial, bold'))
    fig.update_yaxes(title_text='TeraWatt Hour (TWh)', title_font=dict(size=15, family='Arial, bold'))
    return fig


unique_countries = sorted(df['Entity'].unique())

# Layout
layout_container = dbc.Container([
    dbc.Row([
        dbc.Col([
            html.H1("Renewable Energy Dashboard", style={'font-size': '3rem', 'font-weight': 'bold', 'color': 'forestgreen','textAlign': 'center'}),
            html.P("Welcome to this interactive data visualisation dashboard. \n\nThe dashboard contains of three different charts;\n\n1. Line Chart of Renewable Energy comparison between selected countries from 1965 - 2022 \n2. Bar Chart displaying the Top 10 Countries in Renewable Energy Share % of the country’s primary energy resources, including yearly selection choice \n3. Bar Chart comparison of Renewable Energy Consumption vs Production by Continents, including yearly selection choice \n\n", style={'font-size': '1.25rem', 'text-align': 'justify', 'white-space': 'pre-wrap', 'textAlign': 'center'}),
        ], width=12),
    ]),
    dbc.Row([
        dbc.Col([
            html.H2(["How has the ", html.Span("Renewable Energy Landscape", style={'color': 'forestgreen'}), " evolved across countries since 1965?"], style={'font-weight': 'bold'}),
            html.P("Explore the evolution of renewable energy shares in different countries, customize the chart by selecting the countries and energy types you're interested in.\nYou can choose between total renewable share or specific renewable energy sources such as hydro, wind, or solar.\nCompare the renewable energy production trends and the total renewable shares of countries over the years.\n\nInteract with the graph through the the drop-down menu to select energy type, or total renewables pr country, and then select the countries you want to view or compare.", style={'font-size': '16px', 'text-align': 'justify', 'white-space': 'pre-wrap'}),
        ], width=12),
    ]),
    dbc.Row([
        dbc.Col([
            html.Div([
                dcc.Dropdown(
                    id='energy-type-dropdown',
                    options=[{'label': energy_type_labels[key], 'value': key} for key in energy_type_columns],
                    value='renewable_share_energy',
                    multi=False,
                    style={'height': '100%', 'width': '100%'},
                ),
            ], style={'width': '15%', 'display': 'inline-block', 'vertical-align': 'top', 'padding-right': '15px', 'height': '100%'}),
            html.Div([
                dcc.Dropdown(
                    id='country-dropdown',
                    options=[{'label': country, 'value': country} for country in data_frames['renewable_share_energy']['Entity'].unique()],
                    value=['United States', 'China', 'Russia', 'India'],
                    multi=True,
                    style={'height': '100%', 'width': '100%'},
                ),
            ], style={'width': '40%', 'display': 'inline-block', 'vertical-align': 'top', 'padding-right': '15px', 'height': '100%'}),
        ], width=12, style={'height': '150px'}),
    ]),
    dbc.Row([
        dbc.Col([
            dcc.Graph(id='time-series-graph')
        ], width=12),
    ], style={'margin-top': '-90px'}),
    html.Div([
        dbc.Row([
            dbc.Col([
                html.H2(id='top10-title', style={'font-weight': 'bold'}),
                dbc.Col([
                        html.Div(id='highest-renewable-share-country', style={'margin-top': '20px'}),
                    ], width=10),
                dcc.Graph(id='comparison-graph')
            ], width=6),
            dbc.Col([
                html.Div([
                    html.H2(id='continent-title', children=["Renewable Energy ", html.Span("Consumption", style={'color': 'steelblue'}), " vs ", html.Span("Production", style={'color': 'limegreen'}), " by Continent"], style={'font-weight': 'bold'}),
                    dbc.Col([
                        html.Div(id='leading-continents', style={'margin-top': '20px'}),
                    ], width=10),
                    dcc.Graph(id='continent-comparison-graph'),
                ]),
            ], width=6),
        ]),
    ]),
    dbc.Row([
        dbc.Col([
            html.Div([
                dcc.Slider(
                    id='year-slider',
                    min=data_frames['renewable_share_energy']['Year'].min(),
                    max=data_frames['renewable_share_energy']['Year'].max(),
                    value=data_frames['renewable_share_energy']['Year'].max(),
                    marks={str(year): {'label': str(year), 'style': {'transform': 'rotate(-45deg)', 'color': 'steelblue'}} for year in data_frames['renewable_share_energy']['Year'].unique()},
                    step=None,
                ),
            ], style={'width': '100%', 'display': 'inline-block', 'padding-right': '15px'}),
        ]),
    ]),
], fluid=True, style={'padding-bottom': '35px'})


# Title and value handling
@app.callback(
    Output('top10-title', 'children'),
    Output('continent-title', 'children'),
    Output('highest-renewable-share-country', 'children'),
    Output('leading-continents', 'children'),
    Input('year-slider', 'value'),
)
def update_titles(year):
    top10_title = html.Span([
        html.Span("Top 10 Countries", style={'color': 'steelblue'}),
        f" in Renewable Energy Share {year}", 
    ])
    continent_title = html.Span([
        "Renewable Energy ", 
        html.Span("Consumption", style={'color': 'steelblue'}), 
        " vs ", 
        html.Span("Production", style={'color': 'limegreen'}), 
        f" by Continent {year}"
    ])

    # Find the highest renewable energy share country
    highest_country = highest_renewable_share_country(year)
    percentage = highest_renewable_share_percentage(year)
    highest_renewable_share_country_text = html.Span([
        html.Span(f"{highest_country}", style={'font-weight': 'bold'}),
        " had the highest renewable energy share in ",
        html.Span(f"{year}", style={'font-weight': 'bold'}),
        " with ",
        html.Span(f"{percentage:.2f}%", style={'font-weight': 'bold'}),
        " of its primary energy being renewables",
    ])

    # Find the leading continents in production and consumption
    df_consumption = data_frames['modern_renewable_energy_consumption']
    df_production = data_frames['modern_renewable_prod']
    df_filtered_consumption, df_filtered_production = get_continent_dataframes(df_consumption[df_consumption['Year'] == year], df_production[df_production['Year'] == year])

    leading_consumption_continent = df_filtered_consumption.loc[df_filtered_consumption['Total Consumption (TWh)'].idxmax()]['Entity']
    leading_production_continent = df_filtered_production.loc[df_filtered_production['Total Production (TWh)'].idxmax()]['Entity']
    second_biggest = second_biggest_continent(year)

    leading_continents = html.Span([
        "In ",
        html.Span(f"{year}", style={'font-weight': 'bold'}),
        ", ",
        html.Span(f"{leading_consumption_continent}", style={'font-weight': 'bold'}),
        " led in renewable energy consumption & production, with ",
        html.Span(f"{second_biggest}", style={'font-weight': 'bold'}),
        " being 2nd.",
    ])

    return top10_title, continent_title, highest_renewable_share_country_text, leading_continents

# Footer for the reference/dataset link
footer_style = {
    'position': 'absolute',
    'bottom': '0',
    'width': '100%',
    'height': '35px',
    'line-height': '35px',
    'text-align': 'right',
    'color': 'grey',
    'font-size': '14px',
}


app.layout = html.Div([
    layout_container,
    html.Footer("Dataset Source: https://www.kaggle.com/datasets/belayethossainds/renewable-energy-world-wide-19652022", style=footer_style)
], style={'position': 'relative', 'min-height': '100vh'})


if __name__ == "__main__":
    app.run_server(host="0.0.0.0", port=8080)