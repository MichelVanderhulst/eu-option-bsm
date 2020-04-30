# import dash
# import dash_core_components as dcc
# import dash_html_components as html
# from dash.dependencies import Input, Output
# import pandas as pd
# import plotly.graph_objs as go

# external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

# app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

# server = app.server

# ################################################################################################################
# # LOAD AND PROCESS DATA
# df0 = pd.read_csv('./data/IHME_GBD_2017_HEALTH_SDG_1990_2030_SCALED_Y2018M11D08.CSV')
# loc_meta = pd.read_csv('./data/location_metadata.csv')

# # Indicator Value by country in wide format
# df = df0.pivot(index='location_name', columns='indicator_short', values='scaled_value')
# df = pd.merge(loc_meta, df.reset_index())
# indicators = df0.indicator_short.unique().tolist()
# indicator_key = df0.drop_duplicates('indicator_short').set_index('indicator_short')[
#     'ihme_indicator_description'].to_dict()

# ################################################################################################################

# top_markdown_text = '''
# ### Call/Put Replication Strategy Tool
# #### Michel Vanderhulst - 04/29/2020
# Master's thesis - Louvain School of Management 
# '''

# app.layout = html.Div([

#     # HEADER
#     dcc.Markdown(children=top_markdown_text),

#     # LEFT - CHOROPLETH MAP
#     html.Div([
#     	html.Label("Call or Put:"),
#         dcc.Dropdown(
#             id='CallOrPut',
#             options=[{'label':'European Call option', 'value':"Call"},
#             		 {'label':'European Put option', 'value':"Put"}],
#             value='Call'),
#         #
#         html.Div([
#         	html.Div([
#             	html.Label('Spot price'),
#             	dcc.Input(id="S", value=100, type='number')
#         	], className="six columns"),

#        		html.Div([
#             	html.Label("Strike"),
#             	dcc.Input(id="K", value=100, type='number')
#         	], className="six columns"),
#     	], className="row"),
#     	#
#     	html.Label('Drift'),
#         html.Div(id='updateDrift'),
#     	dcc.Slider(
#     		id='mu',
#         	min=-0.30,
#         	max=0.30,
#         	value=0.10,
#         	step=0.01),
#     	#
#         html.Label('Volatility'),
#         html.Div(id='updateVol'),
#     	dcc.Slider(
#     		id='sigma',
#         	min=0.15,
#         	max=0.50,
#         	step=0.01,
#         	value=0.10),
#         #
#         html.Label('Risk-free rate'),
#         html.Div(id='updateRf'),
#     	dcc.Slider(
#     		id='Rf',
#         	min=0,
#         	max=0.1,
#         	step=0.01,
#         	value=0.05),
#     	#
#     	html.Label('Maturity'),
#     	dcc.Slider(
#     		id='T',
#         	min=1,
#         	max=5,
#         	marks={i: '{}'.format(i) for i in range(6)},
#         	step=0.25,
#         	updatemode='drag',
#         	value=1),
#     	#
#     	html.Br(),
#     	html.Label('Transaction costs'), 
#     	dcc.Input(id="TC", value=0, type='number'),
#     	#
#     	dcc.Checklist(
#        		options=[
#        			{'label': 'Fixed TC', 'value': 'FTC'},
#         		{'label': 'Proportional TC', 'value': 'PTC'}], 
#         	value=[], #ADD AN S WHZN GOING ONLINE
#         	labelStyle={'display': 'inline-block'}),	
#     	#
#         dcc.Dropdown(
#             id='x-varname',
#             options=[{'label': i, 'value': i} for i in indicators],
#             value='SDG Index'),
#         dcc.Markdown(id='x-description'),
#         dcc.Graph(id='county-choropleth'),
#         dcc.Markdown('*Hover over map to select country for plots*'),
#     ], style={'float': 'left', 'width': '39%'}),

#     # RIGHT - SCATTERPLOT
#     html.Div([
#     	html.Div([
#         	html.Div([
#             	html.Label('Discretization step'),
#             	dcc.Input(id="dt", value=0.01, type='number')
#         			], className="six columns"),
#         #
#        		html.Div([
#             	html.Label("Portfolio rebalancing"),
#             	dcc.Input(id="dt_p", value=1, type='number')
#         			], className="six columns"),
#     		], className="row"),
#     	#
#         dcc.Dropdown(
#             id='y-varname',
#             options=[{'label': i, 'value': i} for i in indicators],
#             value='Under-5 Mort'
#         ),
#         dcc.Markdown(id='y-description'),
#         dcc.Graph(id='scatterplot'),
#     ], style={'float': 'right', 'width': '59%'}),

# ])


# @app.callback(
#     Output('x-description', 'children'),
#     [Input('x-varname', 'value')])
# def x_description(i):
#     return f'{indicator_key[i]}'


# @app.callback(
#     Output('y-description', 'children'),
#     [Input('y-varname', 'value')])
# def y_description(i):
#     return f'{indicator_key[i]}'


# @app.callback(
#     Output('county-choropleth', 'figure'),
#     [Input('x-varname', 'value')])
# def update_map(x_varname):
#     return dict(
#         data=[dict(
#             locations=df['ihme_loc_id'],
#             z=df[x_varname],
#             text=df['location_name'],
#             autocolorscale=False,
#             reversescale=True,
#             type='choropleth',
#         )],
#         layout=dict(
#             title=x_varname,
#             height=400,
#             margin={'l': 0, 'b': 0, 't': 40, 'r': 0},
#             geo=dict(showframe=False,
#                      projection={'type': 'Mercator'}))
#     )


# @app.callback(
#     Output('scatterplot', 'figure'),
#     [Input('x-varname', 'value'),
#      Input('y-varname', 'value'),
#      Input('county-choropleth', 'hoverData'),])
# def update_graph(x_varname, y_varname, hoverData):
#     if hoverData is None:  # Initialize before any hovering
#         location_name = 'Nigeria'
#     else:
#         location_name = hoverData['points'][0]['text']

#     # Make size of marker respond to map hover
#     df['size'] = 12
#     df.loc[df.location_name == location_name, 'size'] = 30

#     return {
#         'data': [
#             go.Scatter(
#                 x=df[df['super_region_name'] == i][x_varname],
#                 y=df[df['super_region_name'] == i][y_varname],
#                 text=df[df['super_region_name'] == i]['location_name'],
#                 mode='markers',
#                 opacity=0.7,
#                 marker={
#                     'size': df[df['super_region_name'] == i]['size'],
#                     'line': {'width': 0.5, 'color': 'white'}
#                 },
#                 name=i
#             ) for i in df.super_region_name.unique()
#         ],
#         'layout': go.Layout(
#             height=400,
#             xaxis={'title': x_varname},
#             yaxis={'title': y_varname},
#             margin={'l': 40, 'b': 40, 't': 10, 'r': 10},
#             # legend={'x': 0, 'y': 1},
#             hovermode='closest'
#         )
#     }

# @app.callback(Output('updateDrift', 'children'),
#               [Input('mu', 'value')])
# def display_value(value):
#     return 'Selected value: {}'.format(value)

# @app.callback(Output('updateVol', 'children'),
# 			  [Input('sigma', 'value')])
# def display_value2(value):
#     return 'Selected value: {}'.format(value)

# @app.callback(Output('updateRf', 'children'),
# 			  [Input('Rf', 'value')])
# def display_value3(value):
#     return 'Selected value: {}'.format(value)

# if __name__ == '__main__':
#     app.run_server(debug=True)

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.graph_objs as go
from EU_Option_BSM_GBM_V5 import *

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

server = app.server

################################################################################################################

################################################################################################################

top_markdown_text = '''
### Call/Put Replication Strategy Tool
#### Michel Vanderhulst - 04/29/2020
Master's thesis - Louvain School of Management
'''

app.layout = html.Div([

    # HEADER
    dcc.Markdown(children=top_markdown_text),

    # LEFT - CHOROPLETH MAP
    html.Div([
    	html.Label("Call or Put:"),
        dcc.Dropdown(
            id='CallOrPut',
            options=[{'label':'European Call option', 'value':"Call"},
            		 {'label':'European Put option', 'value':"Put"}],
            value='Call'),
        #
        html.Div([
        	html.Div([
            	html.Label('Spot price'),
            	dcc.Input(id="S", value=100, type='number')
        	], className="six columns"),

       		html.Div([
            	html.Label("Strike"),
            	dcc.Input(id="K", value=100, type='number')
        	], className="six columns"),
    	], className="row"),
    	#
    	html.Label('Drift'),
        html.Div(id='drift'),
    	dcc.Slider(
    		id='mu',
        	min=-0.30,
        	max=0.30,
        	value=0.10,
        	step=0.01),
    	#
        html.Label('Volatility'),
        html.Div(id='sigma'),
    	dcc.Slider(
    		id='vol',
        	min=0,
        	max=1,
        	step=0.01,
        	value=0.20),
        #
        html.Label('Risk-free rate'),
        html.Div(id='riskfree'),
    	dcc.Slider(
    		id='Rf',
        	min=0,
        	max=0.1,
        	step=0.01,
        	value=0.05),
    	#
    	html.Label('T'),
    	dcc.Slider(
    		id='T',
        	min=1,
        	max=5,
        	marks={i: '{}'.format(i) for i in range(6)},
        	step=0.25,
        	updatemode='drag',
        	value=3),
    	#
    	html.Br(),
    	html.Label('Transaction costs'),
    	dcc.Input(id="TransactionCosts", value=0, type='number'),
    	#
    	dcc.Checklist(
    		id = "FixedOrPropor",
       		options=[
       			{'label': 'Fixed TC', 'value': 'FTC'},
        		{'label': 'Proportional TC', 'value': 'PTC'}],
        	value=[], #ADD AN S WHEN GOING ONLINE
        	labelStyle={'display': 'inline-block'}),
    	#
    	dcc.Checklist(
    		id = "seed",
       		options=[
        		{'label': 'Fix random generation seed', 'value': "seed"}],
        	value=[], #ADD AN S WHEN GOING ONLINE
        	),
    	#
    ], style={'float': 'left', 'width': '39%'}),

    # RIGHT - SCATTERPLOT
    html.Div([
    	html.Div([
        	html.Div([
            	html.Label('Discretization step'),
            	dcc.Input(id="dt", value=0.01, type='number')
        			], className="six columns"),
        #
       		html.Div([
            	html.Label("Portfolio rebalancing"),
            	dcc.Input(id="dt_p", value=1, type='number')
        			], className="six columns"),
    		], className="row"),
    	#
        dcc.Graph(id='replication'),
    ], style={'float': 'right', 'width': '59%'}),

])

@app.callback(
    Output('replication', 'figure'),
    [Input('CallOrPut', 'value'),
     Input("S","value"),
     Input("K", "value"),
     Input("Rf", "value"),
     Input("T","value"),
     Input("mu","value"),
     Input("vol", "value"),
     Input("dt", "value"),
     Input("dt_p", "value"),
     Input("TransactionCosts", "value"),
	 Input("FixedOrPropor", "value"),
     Input("seed", "value"),])
def rep_strat(CallOrPut, S, K, Rf,T,mu,vol,dt,dt_p, TransactionCosts, FixedOrPropor, sde__seed):
	a, StockPrice, OptionIntrinsicValue, OptionPrice, EquityAccount, CashAccount, V_t = RepStrat_EU_Option_BSM_GBM_V4(CallOrPut, S, K, Rf, T, mu, vol, dt, dt_p, TransactionCosts, FixedOrPropor,  sde__seed)

	return{ #problème: comment ajouter plusieurs y dans le même plotly
    'data': [
        go.Scatter(
            x=list(a),
            y=StockPrice,
            text="Stock price simulation (GBM)",
            mode='lines',
            opacity=0.7,
            name="Stock price simulation (GBM)"),
        go.Scatter(
        	x=list(a),
        	y=OptionIntrinsicValue,
        	text="Option intrinsic value",
        	mode="lines",
        	opacity=0.7,
        	name="Option intrinsic value"),
        go.Scatter(
        	x=list(a),
        	y=OptionPrice,
        	text="Option price",
        	mode="lines",
        	opacity=0.7,
        	name="Option price"),
        go.Scatter(
        	x=list(a),
        	y=V_t,
        	text="SDE simulation",
        	mode="lines",
        	opacity=0.7,
        	name="SDE simulation"),  
        go.Scatter(
        	x=list(a),
        	y=EquityAccount+CashAccount,
        	text="Portfolio",
        	mode="lines",
        	opacity=0.7,
        	name="Portfolio"),
    ],
    'layout': go.Layout(
        #height=400,
        xaxis={'title': f"Discretized time to maturity (dt={dt})"},
        yaxis={'title': "USD"},
        # title={"title:" f"{CallOrPut} replication strategy"}
        #margin={'l': 40, 'b': 40, 't': 10, 'r': 10},
        # legend={'x': 0, 'y': 1},
        #hovermode='closest'
    )
}
	

@app.callback(Output('drift', 'children'),
              [Input('mu', 'value')])
def display_value(value):
    return 'Selected value: {}'.format(value)

@app.callback(Output('sigma', 'children'),
			  [Input('vol', 'value')])
def display_value2(value):
    return 'Selected value: {}'.format(value)

@app.callback(Output('riskfree', 'children'),
			  [Input('Rf', 'value')])
def display_value3(value):
    return 'Selected value: {}'.format(value)

if __name__ == '__main__':
    app.run_server(debug=True)