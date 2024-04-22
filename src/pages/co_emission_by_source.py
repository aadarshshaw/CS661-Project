import pandas as pd
import plotly.graph_objects as go
from dash import dcc, html, register_page, Input, Output, callback
import dash_mantine_components as dmc
from pathlib import Path

register_page(
    __name__,
    "/co2_vis_source",
    title="CO2 Emissions spare Visualisation",
    description="Visualisation of CO2 emission throughout the World Based on Source",
)


df = pd.read_csv(
    Path(__file__).parents[2]
    / "Datasets"
    / "CO2_Emissions"
    / "per-capita-co2-by-source.csv"
)

# Rename columns
df.rename(
    columns={
        "Annual CO₂ emissions from coal (per capita)": "coal",
        "Annual CO₂ emissions from oil (per capita)": "oil",
        "Annual CO₂ emissions from gas (per capita)": "gas",
        "Annual CO₂ emissions from flaring (per capita)": "flaring",
        "Annual CO₂ emissions from cement (per capita)": "cement",
        "Annual CO₂ emissions from other industry (per capita)": "other",
    },
    inplace=True,
)

# Calculate total CO₂ emissions for each entity
df["Total CO₂ emissions"] = df[
    ["coal", "oil", "gas", "flaring", "cement", "other"]
].sum(axis=1)
df = df[df["Year"] > 1850]
# Get unique entities
entities = df["Entity"].unique()

# Sort the DataFrame based on total CO₂ emissions
df_sorted = df.sort_values(by="Total CO₂ emissions", ascending=True)

# Get the bottom 5 entities
# default_entities = df_sorted['Entity'].tail(5).tolist()
# Get top three countries by default
default_entities = ["World", "India", "United States", "China", "South America"]

# Initialize the Dash app

# Define the layout of the app
layout = html.Div(
    [
        dmc.Text("CO₂ Emissions by Source", style={"fontSize": 30}, align="center"),
        dmc.Space(h=20),
        dmc.Grid(
            [
                dmc.Col(
                    dmc.MultiSelect(
                        id="country-dropdown",
                        data=[
                            {"label": entity, "value": entity} for entity in entities
                        ],
                        value=default_entities,  # Set default value to bottom 5 entities
                    ),
                    span=12,
                ),
                dmc.Col(dcc.Graph(id="bar-chart"), span=12),
                dmc.Col(
                    dmc.Slider(
                        id="year-slider",
                        min=df["Year"].min(),
                        max=df["Year"].max(),
                        value=df["Year"].max(),
                        marks=[
                            {"label": str(year), "value": year}
                            for year in range(df["Year"].min(), df["Year"].max(), 10)
                        ],
                    ),
                    span=12,
                ),
            ]
        ),
    ]
)


# Define callback to update the bar chart based on selected countries
@callback(
    Output("bar-chart", "figure"),
    [Input("country-dropdown", "value"), Input("year-slider", "value")],
)
def update_bar_chart(selected_entities, selected_year):
    # Filter data for selected year and entities
    selected_data = df[
        (df["Entity"].isin(selected_entities)) & (df["Year"] == selected_year)
    ].copy()

    # Create traces for each source
    traces_sources = []
    colors = [
        "#606060",
        "#9C0000",
        "#800070",
        "#A52A2A",
        "#008000",
        "#0000AA",
    ]  # Black, Red, Purple, Brown, Green, Blue
    for i, source_column in enumerate(
        ["coal", "oil", "gas", "flaring", "cement", "other"]
    ):
        hover_text = [
            f"{source_column}: {value:.2f}" if value >= 1 else ""
            for value in selected_data[source_column]
        ]  # Custom hover text
        column_text = [
            f"{value:.2f}t" if value >= 1 else ""
            for value in selected_data[source_column]
        ]  # Custom text for columns

        # Define hover template
        hover_template = f"%{{x:.2f}}t:<br>"
        trace = go.Bar(
            y=selected_data["Entity"],
            x=selected_data[source_column],
            orientation="h",
            name=source_column,
            marker=dict(color=colors[i]),  # Apply custom color
            hoverinfo="none",  # Skip default hover text
            hovertemplate=hover_template,  # Custom hover template
            text=column_text,  # Text displayed on columns
        )
        traces_sources.append(trace)

    # Create layout
    layout = go.Layout(
        title=f"Per Capita CO₂ Emissions by Source ({selected_year}) (in tonnes per person)",
        xaxis=dict(title="Total CO₂ Emissions (Metric Tons)"),
        yaxis=dict(title="Country"),
        barmode="stack",  # Stack bars on top of each other
    )

    # Create and return the figure
    fig = go.Figure(data=traces_sources, layout=layout)
    return fig
