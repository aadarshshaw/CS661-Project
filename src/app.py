import dash
from dash import Dash

from lib.appshell import create_appshell

app = Dash(
    __name__,
    suppress_callback_exceptions=True,
    use_pages=True,
    update_title=None,
)

app.layout = create_appshell(dash.page_registry.values())
server = app.server

if __name__ == "__main__":
    app.run_server(host="0.0.0.0", debug=False)
