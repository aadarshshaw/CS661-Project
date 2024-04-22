import pandas as pd
import plotly.graph_objects as go
import dash
from dash import dcc, html, register_page, callback
from dash.dependencies import Input, Output
from pathlib import Path
import dash_mantine_components as dmc

register_page(
    __name__,
    "/sources_co2_emission",
    title="Sources of CO2 emission",
    description="Sources of CO2 emission",
)

parsed_path = (
    Path(__file__).parents[2]
    / "Datasets"
    / "sources_co2_emission"
    / "co2_emm_annual_fossil_land_use.xlsx"
)

# Read data from Excel file
sources = pd.read_excel(parsed_path)

params = ['Total CO2 Emission', 
            'CO2 Emission from Fossil Fuels', 
            'CO2 Emission from Land Use Change'
        ]

def create_source_graph(sources, country):
    fig = go.Figure()
    # print(sources[])
    for param in ['Total CO2 Emission', 'CO2 Emission from Fossil Fuels', 'CO2 Emission from Land Use Change']:
        fig.add_trace(go.Scatter(x=sources[sources['Entity'] == country]['Year'],
            y=sources[sources['Entity'] == country][param],
            mode='lines+markers',
            name=param
        )
    )
    fig.update_layout(title='CO2 Emissions',
        xaxis_title='Year',
        yaxis_title='CO2 Emission (metric tons)',
        showlegend=True
    )
    return fig

def create_select_country(sources):
    return dmc.Select(
        id="country-select",
        data = sources['Entity'].unique(),
        placeholder="Select a Country",
        value="India",
    )

layout = html.Div(
    [
        dmc.Text("Sources of CO2 Emission", align="center", style={"fontSize": 30}),
        dmc.Container(
            create_select_country(sources),
            size="lg",
            pt=20,
            style={
                "position": "fixed",
                "z-index": "100",
                "bottom": "0",
                "width": "100%",
                "background-color": "white",
                "margin-left": "-10px",
                "padding-bottom": "10px",
            },
        ),
        dmc.Grid(
            children=[
                dmc.Col(
                    dcc.Graph(
                        id="co2-emissions-graph",
                        figure=create_source_graph(sources, "India"),
                        style={"height":"60vh"},
                    ),
                    span=12,
                )
            ]
        )
    ]
)

@callback(
    Output('co2-emissions-graph', 'figure'),
    Input('country-select', 'value'),
)

def update_plot(selected_country):
    filtered_df = sources[sources['Entity'] == selected_country]
    updated_fig = go.Figure()
    updated_fig = create_source_graph(filtered_df, selected_country)
    return updated_fig


