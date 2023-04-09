from dash import Dash, html, Input, Output, ctx
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output
from reddit import redditUI
from twitter import twitterUI

external_css = ["https://stackpath.bootstrapcdn.com/bootstrap/4.5.0/css/bootstrap.min.css"]

app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP, './custom-styles.css'])

app.title = 'Real-Time Reddit Monitor'


app.layout = html.Div(
    [
        reddit_button := html.Button(
            "Go to Reddit Analysis Page",
            style={"margin": "auto", "width": "fit-content"},
            id="reddit_button"
        ),
        twitter_button := html.Button(
            "Go to Twitter Analysis Page",
            style={"margin": "auto", "width": "fit-content"},
            id="twitter_button"
        ),
        page := html.Div(
            id="page"
        )
    ],
)

@app.callback(
    Output('page', component_property='children'),
    Input("twitter_button", component_property="n_clicks"),
    Input("reddit_button", component_property="n_clicks")
)
def switchDisplay(click, idkArgTwo):
    if "twitter_button" == ctx.triggered_id:
        return twitterUI(app)
    else:
        return redditUI(app)

server = app.server
if __name__ == '__main__':
    app.run_server(debug=False)
