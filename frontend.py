import base64
import io
import pandas as pd
from joblib import load
import dash
import dash_table
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html

app = dash.Dash(__name__)

# Load the model and vectorizer
classifier = load('malicious_tweet_classifier.joblib')
vectorizer = load('tfidf_vectorizer.joblib')

app.layout = html.Div([
    dcc.Upload(
        id='upload-data',
        children=html.Div([
            'Drag and Drop or ',
            html.A('Select Files')
        ]),
        style={
            'width': '100%',
            'height': '60px',
            'lineHeight': '60px',
            'borderWidth': '1px',
            'borderStyle': 'dashed',
            'borderRadius': '5px',
            'textAlign': 'center',
            'margin': '10px'
        },
        multiple=True
    ),
    html.Div(id='output-data-upload'),
])


@app.callback(
    Output('output-data-upload', 'children'),
    [Input('upload-data', 'contents')],
    [State('upload-data', 'filename')]
)

def update_output(contents, filename):
    if contents:
        content_type, content_string = ''.join(contents).split(',')
        decoded = base64.b64decode(content_string)
        try:
            df = pd.read_csv(io.StringIO(decoded.decode('utf-8')))
            text_vectorized = vectorizer.transform(df['Comment'])
            df['prediction'] = classifier.predict(text_vectorized)
            malicious_tweets = df[df['prediction'] == 1]

            return html.Div([
                html.H5(f"Detected Malicious Tweets in {filename}"),
                dash_table.DataTable(
                    id='malicious-tweets-table',
                    columns=[{"name": i, "id": i} for i in malicious_tweets.columns],
                    data=malicious_tweets.to_dict("records"),
                    style_table={'overflowX': 'auto'},
                )
            ])
        except Exception as e:
            print(e)
            return html.Div([
                'There was an error processing this file.'
            ])
    return html.Div([])



if __name__ == '__main__':
    app.run_server(debug=True)
