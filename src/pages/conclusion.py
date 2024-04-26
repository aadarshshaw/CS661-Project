from dash import html, register_page
import dash_mantine_components as dmc

register_page(
    __name__,
    "/conclusion",
    title="Conclusion",
    description="Conclusion",
)

layout = html.Div(
    [
        dmc.Text("Conclusion", align="center", style={"fontSize": 30}),
        html.P(
            "It is pretty obvious that the amount of CO2 released to the atmosphere has been increased significantly in last 70 years, causing a variety of unwanted consequences all over the world: natural disasters such as fires and tornados and glacial meltdown."
        ),
        html.Center(
            html.H3("It's never too late!"),
        ),
        html.P(
            "Some say that we hit the point 'no-return' for global warming, yet we know that mother nature can heal anything. If we act together now, before losing all the forests, icebergs and infinite number of different species living on earth, we can still heal our world."
        ),
        html.Center(
            html.H3("What can we do?"),
        ),
        html.P(
            "We can start by reducing the amount of CO2 we release to the atmosphere. We can use public transportation, reduce the amount of plastic we use, recycle, plant trees, and many more. We can also raise awareness about the issue and encourage people to take action."
        ),
        html.Center(
            html.H3("Let's act now!"),
        ),
    ]
)
