import dash
from dash import dcc, html, Input, Output, State
import pandas as pd
import plotly.express as px
import openpyxl

app = dash.Dash(__name__)

app.layout = html.Div([
    html.H1("Parameter Analysis"),
    dcc.Input(id='url', type='text', value='https://www.arcgis.com/sharing/rest/content/items/d364201435d94bb1a402036b78da0466/data'),
    dcc.Dropdown(id='params', multi=True),
    dcc.Graph(id='histogram'),
    dcc.Store(id='data-store')  # Add a Store component to store the data
])

@app.callback(
    [Output('params', 'options'), Output('params', 'value')],
    Output('data-store', 'data'),
    Input('url', 'value')
)
def load_data(url):
    xls = pd.ExcelFile(url)
    param_choices = []
    data_dict = {}
    for sheet_name in xls.sheet_names:
        data = pd.read_excel(url, sheet_name=sheet_name)
        param_choices.extend(list(data['Parameter Name'].unique()))
        data['Year'] = sheet_name  # Add 'Year' based on sheet name
        data_dict[sheet_name] = data.to_json()
    return [{'label': param, 'value': param} for param in param_choices], param_choices[0:3], data_dict

@app.callback(
    Output('histogram', 'figure'),
    Input('params', 'value'),
    State('data-store', 'data')  # Access the data from the Store component
)
def update_histogram(selected_params, data_dict):
    if data_dict is None:
        return {}
    
    filtered_data = []
    for year, data_json in data_dict.items():
        data = pd.read_json(data_json)
        filtered_data.append(data[data['Parameter Name'].isin(selected_params)])
    
    combined_data = pd.concat(filtered_data)
    
    fig = px.histogram(combined_data, x='Arithmetic Mean', color='Parameter Name', facet_col='Year', barmode='group')
    fig.update_layout(
        title="Histogram of Arithmetic Means for Each Parameter and Year",
        xaxis_title="Arithmetic Mean",
        yaxis_title="Frequency",
        legend=dict(orientation="h"),
    )
    
    return fig

if __name__ == '__main__':
    app.run_server(debug=True)
