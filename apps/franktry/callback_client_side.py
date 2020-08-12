'''https://dash.plotly.com/clientside-callbacks
Note: There are a few limitations to keep in mind:

    Clientside callbacks execute on the browser's main thread and wil block rendering and events processing while being executed.
    Dash does not currently support asynchronous clientside callbacks and will fail if a Promise is returned.
    Clientside callbacks are not possible if you need to refer to global variables on the server or a DB call is required.'''
import dash
from dash.dependencies import Input, Output
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd

import json

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

df = pd.read_csv('https://raw.githubusercontent.com/plotly/datasets/master/gapminderDataFiveYear.csv')

available_countries = df['country'].unique()

app.layout = html.Div([
    dcc.Graph(
        id='clientside-graph'
    ),
    dcc.Store(
        id='clientside-figure-store',
        data=[{
            'x': df[df['country'] == 'Canada']['year'],
            'y': df[df['country'] == 'Canada']['pop']
        }]
    ),
    'Indicator',
    dcc.Dropdown(
        id='clientside-graph-indicator',
        options=[
            {'label': 'Population', 'value': 'pop'},
            {'label': 'Life Expectancy', 'value': 'lifeExp'},
            {'label': 'GDP per Capita', 'value': 'gdpPercap'}
        ],
        value='pop'
    ),
    'Country',
    dcc.Dropdown(
        id='clientside-graph-country',
        options=[
            {'label': country, 'value': country}
            for country in available_countries
        ],
        value='Canada'
    ),
    'Graph scale',
    dcc.RadioItems(
        id='clientside-graph-scale',
        options=[
            {'label': x, 'value': x} for x in ['linear', 'log']
        ],
        value='linear'
    ),
    html.Hr(),
    html.Details([
        html.Summary('Contents of figure storage'),
        dcc.Markdown(
            id='clientside-figure-json'
        )
    ])
])


@app.callback(
    Output('clientside-figure-store', 'data'),
    [Input('clientside-graph-indicator', 'value'),
     Input('clientside-graph-country', 'value')]
)
def update_store_data(indicator, country):
    dff = df[df['country'] == country]
    return [{
        'x': dff['year'],
        'y': dff[indicator],
        'mode': 'markers'
    }]


app.clientside_callback(
    """
    function(data, scale) {
        return {
            'data': data,
            'layout': {
                 'yaxis': {'type': scale}
             }
        }
    }
    """,
    Output('clientside-graph', 'figure'),
    [Input('clientside-figure-store', 'data'),
     Input('clientside-graph-scale', 'value')]
)


@app.callback(
    Output('clientside-figure-json', 'children'),
    [Input('clientside-figure-store', 'data')]
)
def generated_figure_json(data):
    return '```\n'+json.dumps(data, indent=2)+'\n```'


if __name__ == '__main__':
    app.run_server(debug=True)