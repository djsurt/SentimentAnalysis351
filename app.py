from dash import Dash, html, Input, Output, dcc, ctx, State
import dash_bootstrap_components as dbc
import plotly.graph_objs as go
import pandas as pd
import psycopg2
import configparser
import tensorflow as tf
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import numpy as np
import base64
import io


app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP, './custom-styles.css'])
app.title = 'Real-Time Reddit Monitor'

#Method to create a table for twitter
def generate_twitter_table(data, max_rows=10):
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

#Layout of the actual application
app.layout = html.Div(
    [
        #Switching between reddit and twitter logic
        reddit_button := html.Button(
            "Go to Reddit Analysis Page",
            style={"margin": "auto", "width": "fit-content", "display": "none"},
            id="reddit_button"
        ),
        twitter_button := html.Button(
            "Go to Twitter Analysis Page",
            style={"margin": "auto", "width": "fit-content"},
            id="twitter_button"
        ),
        #display of twitter dashboard
        page := html.Div(
            [
                # Twitter dashboard display
                twitter_content := html.Div(
                    [
                        html.Div(
                            [
                                html.H1(
                                    'Twitter Malicious Posts Detector',
                                    className="card text-white text-center mb-4",
                                    style={"padding": "20px", "background-color": "#1DA1F2", "border-radius": "10px"}
                                ),

                                html.Div([
                                    dcc.Upload(
                                        id='upload-file',
                                        children=html.Div([
                                            'Drag and Drop or ',
                                            html.A('Select File')
                                        ]),
                                        style={
                                            'width':'100%',
                                            'height':'60px',
                                            'lineHeight': '60px',
                                            'borderWidth': '1px',
                                            'borderStyle': 'dashed',
                                            'borderRadius': '5px',
                                            'textAlign': 'center',
                                            'margin': '10px'
                                        },
                                        multiple=True
                                    ),
                                ]),

                                html.Div(
                                    html.Button('Upload', id='upload-button', n_clicks=0),
                                    style={
                                        'width': '100%',
                                        'display': 'flex',
                                        'justifyContent': 'center',
                                        'alignItems': 'center',
                                        'marginBottom': '10px'
                                    }
                                ),


                                html.Div(
                                    [
                                    html.Span(
                                         "Search the term:",
                                            className="input-label"
                                        ),
                                        dcc.Input(
                                            id="searchinput-1",
                                            type="text",
                                            placeholder="Search here",
                                            className="input-field",
                                            value=" "
                                        ),
                                    ],
                                    className="input-container",
                                    style={"display": "inline-block", "padding-right": "10px"}
                                ),
                                

                                html.Div(
                                    [
                                        html.Div(
                                            html.Div(id='output-file-content'),
                                            className="col-12 mb-4 table-container"
                                        )
                                    ],
                                    className="row"
                                ),
                            
                                html.Div(
                                    [
                                        html.Div(
                                            html.Div(id='search-output'),
                                            className="col-12 mb-4 table-container"
                                        )
                                    ],
                                    className="row"
                                ),

                                

                                html.Div([
                                    html.Button('Clean Database', id='my-button'),
                                    html.Div(id='db-output'),
                                ]),
                            ],
                            style={"margin": "20px 10%", "padding": "20px"}
                        )
                    ],
                    id="twitter_content",
                    style={"display": "none"}
                ),

                # Reddit dashboard display
                reddit_content := html.Div(
                    [
                        html.Div(
                            [
                                #The nav bar
                                html.H1(
                                    [
                                        html.Img(
                                            src="https://www.redditstatic.com/desktop2x/img/favicon/apple-icon-57x57.png",
                                            style={"vertical-align": "middle", "margin-right": "10px", "width": "40px"}
                                        ),
                                        "Real Time Sentiment Analysis on Various Subreddits!"
                                    ],
                                    className="card text-white text-center mb-4",
                                    style={"padding": "20px", "background-color": "#FF4500", "border-radius": "10px"}
                                ),
                                #Bar for seraching term and subreddit and stuff.
                                html.Div(
                                    [
                                        html.Div(
                                            [
                                                html.Span(
                                                    "Search the term:",
                                                    className="input-label"
                                                ),
                                                dcc.Input(
                                                    id="searchinput",
                                                    type="text",
                                                    placeholder="Search here",
                                                    className="input-field",
                                                    value=""
                                                ),
                                            ],
                                            className="input-container",
                                            style={"display": "inline-block", "padding-right": "10px"}
                                        ),
                                        #Choosing the subreddit
                                        html.Div(
                                            [
                                                html.Span(
                                                    "Select subreddit:",
                                                    className="input-label"
                                                ),
                                                dcc.Dropdown(
                                                    id="subreddit-dropdown",
                                                    options=[
                                                        {"label": "All", "value": "all"},
                                                        {"label": "World News", "value": "worldnews"},
                                                        {"label": "AskReddit", "value": "AskReddit"},
                                                        {"label": "Movies", "value": "movies"},
                                                    ],
                                                    className="input-field",
                                                    style={"width": "100%"},
                                                    value="AskReddit"
                                                )
                                            ],
                                            className="input-container",
                                            style={"display": "inline-block", "width": "60%"}
                                        ),
                                    ],
                                    className="input-header card mb-4",
                                    style={"border-radius": "10px", "padding": "20px"}
                                ),
                                
                                dcc.Interval(id="graph-update", interval=10 * 1000, n_intervals=0),
                                dcc.Interval(id="pie-graph-update", interval=10 * 1000, n_intervals=0),
                                dcc.Interval(id="recent-table-update", interval=20 * 1000, n_intervals=0),
                                #All the graphs
                                html.Div(
                                    [
                                        html.Div(
                                            dcc.Graph(id="live-graph", animate=False),
                                            className="col-12 col-md-6 mb-4 graph"
                                        ),
                                        html.Div(
                                            dcc.Graph(id="long-live-graph", animate=False),
                                            className="col-12 col-md-6 mb-4 graph"
                                        ),
                                        html.Div(
                                            dcc.Graph(id="pie-live-graph", animate=False),
                                            className="col-12 col-md-6 mb-4 graph"
                                        ),
                                        html.Div(
                                            id="recent-threads-table",
                                            className="col-12 col-md-6 mb-4 graph"
                                        ),
                                        html.Div(
                                            id="recent-malicious-table",
                                            className="col-12 col-md-6 mb-4 graph"
                                        ),
                                    ],
                                    className="row"
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
                                )
                                
                            ],
                            style={"margin": "20px 10%", "padding": "20px"}
                        )
                    ],
                    id="reddit_content",
                    style={"display": "none"}
                )
            ],
            id="page"
        )
    ],
)

'''
Buttons to switch display
'''
@app.callback(
    Output('twitter_content', component_property='style'),
    [Input("twitter_button", component_property="n_clicks"),
    Input("reddit_button", component_property="n_clicks")]
)
def switchTwitter(click, n_clicks):
    if "twitter_button" == ctx.triggered_id:
        return {"display": "contents"}
    else:
        return {"display": "none"}
    
@app.callback(
    Output('reddit_content', component_property='style'),
    [Input("twitter_button", component_property="n_clicks"),
    Input("reddit_button", component_property="n_clicks")]
)
def switchReddit(click, n_clicks):
    if "twitter_button" == ctx.triggered_id:
        return {"display": "none"}
    else:
        return {"display": "contents"}

@app.callback(
    Output('reddit_button', component_property='style'),
    [Input("twitter_button", component_property="n_clicks"),
     Input("reddit_button", "n_clicks")]
)
def toggleReddit(click, n_clicks):
    if "twitter_button" == ctx.triggered_id:
        return {"display": "block"}
    else:
        return {"display": "none"}

@app.callback(
    Output('twitter_button', component_property='style'),
    [Input("twitter_button", component_property="n_clicks"),
     Input("reddit_button", "n_clicks")]
)
def toggleTwitter(click, n_clicks):
    if "twitter_button" == ctx.triggered_id:
        return {"display": "none"}
    else:
        return {"display": "block"}

server = app.server

config = configparser.ConfigParser()
config.read('postgres.ini')
conn = psycopg2.connect(host=config['DEFAULT']['POSTGRES_HOST'], database="reddit",
                                        user="postgres", password=config['DEFAULT']['POSTGRES_PASSWORD'])
config = configparser.ConfigParser()
config.read('postgres.ini')
twitter_conn = psycopg2.connect(host=config['DEFAULT']['POSTGRES_HOST'], database="reddit",
                                        user="postgres", password=config['DEFAULT']['POSTGRES_PASSWORD'])

# -----------------------------------------------------------------------------------------
'''
Twitter Callbacks
'''


# -----------------------------------------------------------------------------------------
'''
Reddit Callbacks
'''
@app.callback(
    Output('live-graph', 'figure'),
    [Input('graph-update', 'n_intervals'), Input('searchinput', 'value'),Input('subreddit-dropdown', 'value'),])
def update_graph(n_intervals, searchterm, subreddit):

    searchterm = searchterm.lower()


    conn.cursor()
    df = pd.read_sql("SELECT * FROM threads WHERE thread LIKE %s AND subreddit Like %s ORDER BY time DESC LIMIT 50",
                    conn, params=('%' + searchterm + '%','%'+subreddit+'%'))
    df.sort_values('time', inplace=True)
    df['time'] = pd.to_datetime(df['time'])
    df.dropna(inplace=True)

    X = df['time'].tail(100)
    Y = df.sentiment.values[-100:]

    fig = go.Scatter(
        x=X,
        y=Y,
        name='Scatter',
        line_shape='linear',
        mode='lines',
        line=dict(width=3.5, color='orange'),
        fill='tozeroy', 
        fillcolor='rgba(255, 192, 128, 0.3)',
    )

    layout = go.Layout(
        xaxis=dict(range=[min(X, default=0), max(X, default=1)]),
        yaxis=dict(range=[-1, 1]),
        title="The average sentiment for {} is {p:5.2f}!".format(searchterm, p=(sum(Y) / len(Y)) if len(Y) != 0 else 0),
        plot_bgcolor='white',
        paper_bgcolor='white'
    )

    fig = {'data': [fig], 'layout': layout}

    return fig



@app.callback(
    Output('long-live-graph', 'figure'),
    [Input('graph-update', 'n_intervals'), Input('searchinput', 'value'),Input('subreddit-dropdown', 'value'),])
def update_long_graph(n_intervals, searchterm, subreddit):

    searchterm = searchterm.lower()

    conn.cursor()
    df = pd.read_sql("SELECT * FROM threads WHERE thread LIKE %s AND subreddit LIKE %s  ORDER BY time DESC",
                    conn, params=('%' + searchterm + '%','%' + subreddit + '%'))
    df.sort_values('time', inplace=True)
    df['time'] = pd.to_datetime(df['time'])
    df['sentiment_smoothed'] = df['sentiment'].rolling(int(len(df)/20)).mean()
    df.dropna(inplace=True)

    X = df['time']
    Y = df.sentiment_smoothed.values[:]

    fig = go.Scatter(
        x=X,
        y=Y,
        name='Scatter', 
        line_shape='spline',
        fill='tozeroy',  
        fillcolor='rgba(255, 102, 204, 0.3)', 
        mode='none',
    )

    return {
        'data': [fig], 
        'layout': go.Layout(
            xaxis=dict(range=[min(X, default=0), max(X, default=1)]),
            yaxis=dict(range=[min(Y, default=0), max(Y, default=1)]),
            title="The long-term average sentiment for {} is {p:5.2f} (20 moving average)!".format(searchterm, p=(sum(Y) / len(Y)) if len(Y) != 0 else 0)
        )
    }


@app.callback(
    Output('pie-live-graph', 'figure'),
    [Input('pie-graph-update', 'n_intervals'), Input('searchinput', 'value'),Input('subreddit-dropdown', 'value'),])
def update_pie_graph(n_intervals, searchterm, subreddit):
    searchterm = searchterm.lower()

    conn.cursor()
    df = pd.read_sql("SELECT * FROM threads WHERE thread LIKE %s AND subreddit LIKE %s",
                    conn, params=('%' + searchterm + '%','%' + subreddit + '%'))

    labels = ['Positive', 'Neutral', 'Negative']
    values = [
        sum(n > 0 for n in df['sentiment']),
        sum(n == 0 for n in df['sentiment']), 
        sum(n < 0 for n in df['sentiment'])
    ]
    colors = ['green', 'gold',  'red']

    trace = go.Pie(
        labels=labels, 
        values=values,
        hoverinfo='label+percent', 
        textinfo='value', 
        marker=dict(colors=colors, line=dict(color='#000000', width=2))
    )

    return {
        "data": [trace], 
        'layout': go.Layout(
            title='Overall Sentiment count for {}!'.format(searchterm),
            showlegend=True
        )
    }


@app.callback(Output('recent-threads-table', 'children'),
            [Input(component_id='searchinput', component_property='value'), Input('recent-table-update', 'n_intervals'),Input('subreddit-dropdown', 'value'), ])
def update_recent_threads(searchterm, n_intervals, subreddit):
    searchterm = searchterm.lower()
    if searchterm:
        df = pd.read_sql("SELECT * FROM threads WHERE thread LIKE %s AND subreddit LIKE %s ORDER BY time DESC LIMIT 10",
                        conn, params=('%' + searchterm + '%', '%' + subreddit + '%'))
    else:
        df = pd.read_sql(
            "SELECT * FROM threads WHERE subreddit LIKE %s ORDER BY time DESC LIMIT 10", conn, params=('%' + subreddit + '%',))

    #df['Time'] = pd.to_datetime(df['time'])
    df['Time'] = pd.to_datetime(df['time']).dt.strftime('%Y/%m/%d %H:%M:%S')
    df.dropna(inplace=True)

    df['Live Feed'] = df['thread'].str[:]
    df = df[['Time', 'Live Feed', 'sentiment', 'subreddit']]

    return generate_table(df,"Latest 10 posts" ,max_rows=10)

@app.callback(Output('recent-malicious-table', 'children'),
            [Input('subreddit-dropdown', 'value'), Input('recent-table-update', 'n_intervals'), ])
def update_recent_malicious(subreddit, n_intervals):
    df = pd.read_sql(
        "SELECT * FROM malicious_posts WHERE subreddit LIKE %s ORDER BY time DESC LIMIT 10", conn, params=('%' + subreddit + '%',))
    df['Time'] = pd.to_datetime(df['time']).dt.strftime('%Y/%m/%d %H:%M:%S')
    df.dropna(inplace=True)

    df['Live Feed'] = df['thread'].str[:]
    df = df[['Time', 'Live Feed', 'sentiment', 'subreddit']]

    return generate_table(df, "Malicious Posts" ,max_rows=10)

# -----------------------------------------------------------------------------------------

def generate_table(df,table_title, max_rows=10):
    return html.Span(
        children=[
            html.H2(children=[table_title], style={'textAlign': 'center'}), 
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

#------------Uploading file stuff
@app.callback(Output('output-file-content', 'children'),
              Input('upload-button', 'n_clicks'),
              State('upload-file', 'contents'),
              State('upload-file', 'filename'),)
def display_file_content(n_clicks, contents_list, filenames_list):
    if n_clicks > 0:
        if contents_list is not None:
            children = []
            for contents, filename in zip(contents_list, filenames_list):
                content_type, content_string = contents.split(',')
                decoded = base64.b64decode(content_string)
                file_data = io.StringIO(decoded.decode('utf-8'))

                df = pd.read_csv(file_data)

                # Method to insert into a postgres database
                insert_data_to_db(df)
                children.append(html.P(f"Data from file '{filename}' has been inserted into the database."))

            return children
        return "No files uploaded."
    return "Click the 'Upload' button to process files."



@app.callback(Output('search-output', 'children'),
              Input('searchinput-1', 'value'))
def search_term(searchterm):
    if searchterm is not None:
        df = pd.read_sql(
            "SELECT * FROM twitter_threads WHERE thread LIKE %s LIMIT 10", conn, params=('%' + searchterm + '%',))
        return generate_table(df, "Twitter Post Sentiment", max_rows=10)
    return "No search term entered."

def insert_data_to_db(df):
    try:
        cur = conn.cursor()
        analyzer = SentimentIntensityAnalyzer()
        for index, row in df.iterrows():
            t = row['text'].lower()
            vs = analyzer.polarity_scores(t)["compound"]
            values = (t, vs)
            cur.execute("""
                INSERT INTO twitter_threads (thread, sentiment)
                VALUES (%s, %s)
            """, (t, vs))
        conn.commit()
        df = pd.read_sql("SELECT * FROM twitter_threads", con=conn)
        print(df)
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)

@app.callback(
    Output('db-output', 'children'),
    [Input('my-button', 'n_clicks')]
)
def update_output(n_clicks):
    try:
        cur = conn.cursor()
        cur.execute("""
            DELETE FROM twitter_threads
        """)
        conn.commit()
        df = pd.read_sql("SELECT * FROM twitter_threads", con=conn)
        print(df)
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    return ''

if __name__ == '__main__':
    app.run_server(debug=False)
