import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.graph_objs as go
import pandas as pd
import psycopg2
import configparser

app = dash.Dash(__name__)

def twitterUI(app):

    def generate_table(data, max_rows=10):
        return html.Table(
            className="table table-responsive table-striped table-bordered table-hover",
            children=[
                html.Thead(
                    html.Tr(
                        children=[
                            html.Th(col.title()) for col in data.columns.values
                        ]
                    )
                ),
                html.Tbody(
                    [
                        html.Tr(
                            children=[
                                html.Td(data.iloc[i][col]) for col in data.columns.values
                            ]
                        )
                        for i in range(min(len(data), max_rows))
                    ]
                )
            ],
            style={"height": "400px", 'overflowY': 'auto'}
        )

    # Replace the sample data with your actual data
    sample_data = {
        'Time': ['2023-04-09 14:30:00', '2023-04-09 14:20:00', '2023-04-09 14:10:00'],
        'Tweet': ['This is a malicious tweet.', 'This is a normal tweet.', 'Another malicious tweet found.'],
        'Malicious': [True, False, True]
    }

    df = pd.DataFrame(sample_data)

    return html.Div(
        [
            html.H1(
                'Twitter Malicious Posts Detector',
                className="card text-white text-center mb-4",
                style={"padding": "20px", "background-color": "#1DA1F2", "border-radius": "10px"}
            ),

            html.Div(
                [
                    html.Div(
                        generate_table(df, max_rows=10),
                        className="col-12 mb-4 table-container"
                    )
                ],
                className="row"
            ),
        ],
        style={"margin": "20px 10%", "padding": "20px"}
    )

app.layout = twitterUI(app)

if __name__ == '__main__':
    app.run_server(debug=True)