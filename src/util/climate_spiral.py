import pandas as pd
import numpy as np
import plotly.graph_objects as go
from pathlib import Path
from assets.constants import months

coordinate_df = (
    Path(__file__).parents[2]
    / "Datasets"
    / "Surface Temperatures"
    / "coordinate_df.csv"
)

coordinate_df = pd.read_csv(coordinate_df)
TEMP_MAX, TEMP_MIN = (1.48, -0.81)


def temp_to_r(temp, min_=TEMP_MIN, max_=TEMP_MAX, scale=10):
    return scale * (temp - min_) / (max_ - min_)


def create_climate_spiral(year):
    fig = go.Figure(
        data=[
            go.Scatter3d(
                x=coordinate_df[coordinate_df["z"] < year]["x"],
                y=coordinate_df[coordinate_df["z"] < year]["y"],
                z=coordinate_df[coordinate_df["z"] < year]["z"],
                mode="lines",
                line=dict(
                    color=coordinate_df[
                        "z"
                    ],  # You can specify a different column for colors
                    colorscale="Turbo",
                    width=1,
                ),
            )
        ]
    )

    radius_1 = temp_to_r(-1 - TEMP_MIN)
    radius_2 = temp_to_r(-TEMP_MIN)
    radius_3 = temp_to_r(1 - TEMP_MIN)

    # Create data for the circle
    theta_circle = np.linspace(0, 2 * np.pi, 13)[
        :-1
    ]  # Reverse the order to make it clockwise
    z_circle = [2020] * 12  # Set z to 2020 for the circle
    radius = 15  # Adjust the radius of the circle
    x_circle = radius * np.cos(theta_circle)
    y_circle = radius * np.sin(theta_circle)

    month_labels = []
    for i, month in enumerate(months):
        x_label = (
            1.1 * radius * np.cos(i * 2 * np.pi / 12)
        )  # Adjust the radius of the labels
        y_label = (
            1.1 * radius * np.sin(i * 2 * np.pi / 12)
        )  # Adjust the radius of the labels
        month_labels.append(
            go.Scatter3d(
                x=[x_label],
                y=[y_label],
                z=[year],
                mode="text",
                text=[month],
                textfont=dict(size=12, color="red"),  # Set color to white
                showlegend=False,
            )
        )

    # Create a trace for the circle
    circle_trace = go.Scatter3d(
        x=x_circle,
        y=y_circle,
        z=z_circle,
        mode="markers",  # Change mode to markers
        marker=dict(size=0.5, color="white"),  # Set marker size and color
        showlegend=False,
    )

    # Add the circle and month labels to the existing plot
    fig.add_trace(circle_trace)
    fig.add_traces(month_labels)

    # Add additional circles with specific radii and labels
    circles = [
        {"radius": radius_1, "label": "-1 °C", "color": "black"},
        {"radius": radius_2, "label": "0 °C", "color": "black"},
        {"radius": radius_3, "label": "1 °C", "color": "black"},
    ]

    for i, circle in enumerate(circles):
        theta_circle = np.linspace(0, 2 * np.pi, 100)

        z_circle = [year] * 100
        x_circle = circle["radius"] * np.cos(theta_circle)
        y_circle = circle["radius"] * np.sin(theta_circle)

        circle_trace = go.Scatter3d(
            x=x_circle,
            y=y_circle,
            z=z_circle,
            mode="lines",
            line=dict(color="black", width=4),  # Increase line thickness
            showlegend=False,
        )
        fig.add_trace(circle_trace)

        # Add annotations for the labels
        x_label = circle["radius"] * np.cos(
            np.pi / 4
        )  # Adjust the position of the label
        y_label = circle["radius"] * np.sin(
            np.pi / 4
        )  # Adjust the position of the label
        z_label = year
        fig.add_trace(
            go.Scatter3d(
                x=[x_label],
                y=[y_label],
                z=[z_label],
                mode="text",
                text=[circle["label"]],
                textfont=dict(color="black", size=10),
                showlegend=False,
            )
        )

    # Update layout

    fig.update_layout(
        title=f"Global Surface Temperature Anomaly in {year} Climate Spiral",
        scene=dict(
            xaxis=dict(showticklabels=False, title="", visible=False),
            yaxis=dict(showticklabels=False, title="", visible=False),
            zaxis_title="Year",
        ),
        height=600,
        showlegend=False,
        plot_bgcolor="rgba(0, 0, 0, 0)",
        paper_bgcolor="rgba(0, 0, 0, 0)",
    )

    return fig
