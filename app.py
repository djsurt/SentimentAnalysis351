import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import os
import sqlite3
import plotly.graph_objs as go
import pandas as pd
import requests
import psycopg2


external_css = ["https://stackpath.bootstrapcdn.com/bootstrap/4.5.0/css/bootstrap.min.css"]
external_js = ["https://stackpath.bootstrapcdn.com/bootstrap/4.5.0/js/bootstrap.min.js", "gajs.js"]


app = dash.Dash(__name__, external_stylesheets=external_css,
                external_scripts=external_js)


# conn = psycopg2.connect(host="localhost", database="reddit",
#                                         user="postgres", password="abc123")
# conn = psycopg2.connect(host="csds351.crl8z4r48ftj.us-east-1.rds.amazonaws.com", database="reddit",
#                                         user="postgres", password="csds351group6")

app.title = 'Real-Time Reddit Monitor'


app.layout = html.Div(
    [
        html.H1(
            "Real Time Sentiment Analysis on Current World News!",
            className="card bg-light text-dark text-center mb-4",
            style={"padding": "20px"}
        ),

        html.Div(
            [
                html.Span(
                    [
                        html.Span(
                            "Search the term:",
                            style={
                                "background-color": "#f9c7c9", 
                                "padding": "10px",
                                "display": "flex",
                                "min-width": "max-content"
                            }
                        ),
                        dcc.Input(
                            id="searchinput",
                            type="text",
                            placeholder="Search here",
                            style={
                                "margin": "0 0 0 5px"
                            }
                        ),
                    ],
                    style={
                        "display": "flex",
                        "width": "100%",
                        "height": "fit-content",
                        "flex-direction": "row",
                        "align-items": "center"
                    }
                ),
                html.Span(
                    [
                        html.Span(
                            "Select subreddit:",
                            style={
                                "background-color": "#f9c7c9", 
                                "padding": "10px", 
                                "display": "flex",
                                "min-width": "max-content"
                            }
                        ),
                        dcc.Dropdown(
                            id="subreddit-dropdown",
                            options=[
                                {"label": "All", "value": "all"},
                                {"label": "World News", "value": "worldnews"},
                                {"label": "AskReddit", "value": "AskReddit"},
                                {"label": "Movies", "value": "Movies"},
                            ],
                            style={
                                "width": "100%",
                                "margin": "0 0 0 5px"
                            },
                            value="worldnews"
                        )
                    ],
                    style={
                        "display": "flex",
                        "width": "100%",
                        "height": "fit-content",
                        "flex-direction": "row",
                        "align-items": "center"
                    }
                )
            ],
            className="card mb-4",
            style={
                "display": "grid",
                "grid-template-columns": "4fr 6fr",
                "column-gap": "20px",
                "padding": "20px",
                "align-items": "center",
                "justify-items": "center"
            }
        ),
        
        dcc.Interval(id="graph-update", interval=1 * 1000, n_intervals=0),
        dcc.Interval(id="pie-graph-update", interval=1 * 1000, n_intervals=0),
        dcc.Interval(id="recent-table-update", interval=2 * 1000, n_intervals=0),
        
        
        html.Div(
            dcc.Graph(id="live-graph", animate=False),
            className="row",
            style={"padding": "20px"}
        ),

        html.Div(
            dcc.Graph(id="long-live-graph", animate=False),
            className="row",
            style={"padding": "20px"}
        ),
           
        html.Div(
            [
                html.Div(
                    dcc.Graph(id="pie-live-graph", animate=False),
                    className="col-12 col-md-6 mb-4",
                    style={"padding": "20px"}
                ),
            ],
            className="row",
        ),
        
        html.Div(
            id="recent-threads-table",
            className="row",
            style={"padding": "20px"}
        ),
        
        html.Div(
            [
                html.H2(
                    "By: Isha Das, Ben Flock, Dhananjay Surti, Zach Youssef",
                    className="card-header text-white text-center",
                    style={"background-color": "#929292"}
                ),
                html.H3(
                    "CSDS 351: Group 6",
                    className="card-body text-center",
                    style={"background-color": "#e3dede", "padding": "20px"}
                ),
            ],
            className="card mb-4",
            style={"padding": "20px"}
        ),
        
        html.Hr(),
        html.Div(id="subreddit_term"),
        html.Div(id="search_term"),
        
    ],
    style={"margin": "20px 10%", "padding": "20px"}
)



@app.callback(
    dash.dependencies.Output('subreddit_term', 'children'),
    [dash.dependencies.Input('subreddit-dropdown', 'value'), dash.dependencies.Input("searchinput", "value")])
def update_output(value1, value2):
    #listener.subred(value1)
    #listener.topic(value2)
    return


# @app.callback(
#     dash.dependencies.Output('live-graph', 'figure'),
#     [dash.dependencies.Input('graph-update', 'n_intervals'), Input('searchinput', 'value')])
# def update_graph(n_intervals, searchterm):

#     searchterm = searchterm.lower()

#     conn.cursor()
#     df = pd.read_sql("SELECT * FROM threads WHERE thread LIKE %s ORDER BY time DESC LIMIT 50",
#                      conn, params=('%' + searchterm + '%',))
#     df.sort_values('time', inplace=True)
#     df['time'] = pd.to_datetime(df['time'])
#     df.dropna(inplace=True)

#     X = df['time'].tail(100)
#     Y = df.sentiment.values[-100:]

#     fig = go.Scatter(
#         x=X,
#         y=Y,
#         name='Scatter',
#         line_shape='linear',
#         mode='lines',
#         line=dict(width=3.5, color='orange'),
#         fill='tozeroy', fillcolor='rgba(255, 192, 128, 0.3)',
#     )

#     layout = go.Layout(xaxis=dict(range=[min(X, default=0), max(X, default=1)]),
#                         yaxis=dict(range=[-1, 1]),
#                         title="The average sentiment for {} is {p:5.2f}!".format(searchterm, p=(sum(Y) / len(Y)) if len(Y) != 0 else 0),
#                         plot_bgcolor='white',
#                         paper_bgcolor='white')

#     fig = {'data': [fig], 'layout': layout}

#     return fig



# @app.callback(
#     dash.dependencies.Output('long-live-graph', 'figure'),
#     [dash.dependencies.Input('graph-update', 'n_intervals'), Input('searchinput', 'value')])
# def update_long_graph(n_intervals, searchterm):

#     searchterm = searchterm.lower()

#     conn.cursor()
#     df = pd.read_sql("SELECT * FROM threads WHERE thread LIKE %s ORDER BY time DESC",
#                      conn, params=('%' + searchterm + '%',))
#     df.sort_values('time', inplace=True)
#     df['time'] = pd.to_datetime(df['time'])
#     df['sentiment_smoothed'] = df['sentiment'].rolling(int(len(df)/20)).mean()
#     df.dropna(inplace=True)

#     X = df['time']
#     Y = df.sentiment_smoothed.values[:]

#     fig = go.Scatter(
#         x=X,
#         y=Y,
#         name='Scatter', line_shape='spline',
#         fill='tozeroy',  fillcolor='rgba(255, 102, 204, 0.3)', mode='none',
#     )

#     return {'data': [fig], 
#             'layout': go.Layout(xaxis=dict(range=[min(X, default=0), max(X, default=1)]),
#                                 yaxis=dict(range=[min(Y, default=0), max(Y, default=1)]),
#                                 title="The long-term average sentiment for {} is {p:5.2f} (20 moving average)!".format(searchterm, p=(sum(Y) / len(Y)) if len(Y) != 0 else 0))}


# @app.callback(
#     dash.dependencies.Output('pie-live-graph', 'figure'),
#     [dash.dependencies.Input('pie-graph-update', 'n_intervals'), Input(component_id='searchinput', component_property='value')])
# def update_pie_graph(n_intervals, searchterm):

#     conn.cursor()
#     df = pd.read_sql("SELECT * FROM threads WHERE thread LIKE %s",
#                      conn, params=('%' + searchterm + '%',))

#     labels = ['Positive', 'Neutral', 'Negative']
#     values = [sum(n > 0 for n in df['sentiment']),
#               sum(n == 0 for n in df['sentiment']), sum(n < 0 for n in df['sentiment'])]
#     colors = ['green', 'gold',  'red']

#     trace = go.Pie(labels=labels, values=values,
#                    hoverinfo='label+percent', textinfo='value', marker=dict(colors=colors, line=dict(color='#000000', width=2)))

#     return {"data": [trace], 'layout': go.Layout(
#         title='Overall Sentiment count for {}!'.format(
#             searchterm),
#         showlegend=True)}


def generate_table(df, max_rows=10):
    return html.H4(
        children=[
            html.H2(children=["Latest 10 feeds"], style={'textAlign': 'center'}), 
            html.Table(
                className="table table-responsive table-striped table-bordered table-hover",
                children=[
                    html.Thead(
                        html.Tr(
                            children=[
                                html.Th(col.title()) for col in df.columns.values
                            ]
                        )
                    ),
                    html.Tbody(
                        [
                            html.Tr(
                                children=[
                                    html.Td(data) for data in d
                                ]
                            )
                            for d in df.values.tolist()
                        ]
                    )
                ], 
                style={"height": "400px", 'overflowY': 'auto'}
            )
        ]
    )


# @app.callback(Output('recent-threads-table', 'children'),
#               [Input(component_id='searchinput', component_property='value'), Input('recent-table-update', 'n_intervals')])
# def update_recent_threads(searchterm, n_intervals):
#     if searchterm:
#         df = pd.read_sql("SELECT * FROM threads WHERE thread LIKE %s ORDER BY time DESC LIMIT 10",
#                          conn, params=('%' + searchterm + '%',))
#     else:
#         df = pd.read_sql(
#             "SELECT * FROM threads ORDER BY time DESC LIMIT 10", conn)

#     #df['Time'] = pd.to_datetime(df['time'])
#     df['Time'] = pd.to_datetime(df['time']).dt.strftime('%Y/%m/%d %H:%M:%S')
#     df.dropna(inplace=True)

#     df['Live Feed'] = df['thread'].str[:]
#     df = df[['Time', 'Live Feed', 'sentiment']]

#     return generate_table(df, max_rows=10)


server = app.server
if __name__ == '__main__':
    app.run_server(debug=False)
