import numpy as np
import pandas as pd
import plotly.graph_objects as go
from dash import dcc, html, register_page, Input, Output, callback
import dash_mantine_components as dmc
from assets.constants import months
from pathlib import Path
import math
import plotly.express as px

register_page(
    __name__,
    "/population_and_co2",
    title="Population and CO2",
    description="Visualisation of Population and CO2 data",
)



population = pd.read_csv('Datasets/population_and_co2/population_and_co2.csv')




def update_population_graph():
    return create_population_graph()

population['Density (P/Km²)'] = population['Density (P/Km²)'].apply(lambda x : math.log2(x+1))
def create_population_graph():
    fig = px.scatter(population, 
                 x="Annual CO₂ emissions", 
                 y="Population (2020)", 
                 size="Land Area (Km²)", 
                 color="Density (P/Km²)",
                 color_continuous_scale="Temps",
                 hover_name="Entity", 
                 hover_data=['Entity','Annual CO₂ emissions'],
                 labels={'Entity':'Country',
                         'Annual CO₂ emissions':'CO₂ Emission',
                         'Population (2020)':'Population',
                          'Density (P/Km²)':'Density (P/Km²)',
                         },
                 log_x=True,
                 log_y=True, 
                 size_max=40)

    # Update the title and adjust its location
    fig.update_layout(title="Population v. CO2 Emission, 2020", 
                    title_x=0.5)

    # Show the figure
    return fig

layout = html.Div([
    dcc.Graph(
        id='population-co2-graph',
        figure = create_population_graph(),
    )
])




