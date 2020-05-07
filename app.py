import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
import plotly.graph_objs as go
from EU_Option_BSM_GBM_V5 import *
from descriptions import list_input
import base64

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

# app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
image_filename = "bsm-math.png"
encoded_image = base64.b64encode(open(image_filename, 'rb').read())

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

server = app.server

top_markdown_text = '''
### Call/Put Replication Strategy Tool
#### Michel Vanderhulst 
#### Master's thesis - Louvain School of Management
'''

graph_rep_strat_text = ''' #### Replication strategy '''

graph_port_details_text = ''' #### Portfolio composition'''
graph_held_shares_text = ''' #### Held shares'''
graph_sde_deriv_text = ''' #### Option greeks '''


app.layout = html.Div([
	dcc.Store(id='memory-output'),
    # HEADER
    dcc.Markdown(children=top_markdown_text),
    #
    dbc.Button(
        "Show me the math", 
        id="popover-target", 
        color="primary", 
        className="mr-1",
        #size="lg",
        ),
    dbc.Popover(
        [
            dbc.PopoverHeader("CRR model math"),
            dbc.PopoverBody([html.Img(src='data:image/png;base64,{}'.format(encoded_image.decode())    , style={"width": "250%"})]),
        ],
        id="popover",
        is_open=False,
        target="popover-target",
        ),
    html.Br(),
    html.Br(),
    # LEFT - CHOROPLETH MAP
    html.Div([
        dcc.Dropdown(
            id='CallOrPut',
            options=[{'label':'European Call option', 'value':"Call"},
            		 {'label':'European Put option', 'value':"Put"}],
            value='Call'),
        #
        html.Div([
            	html.Label('Spot price', title=list_input["Spot price"]),
            	dcc.Input(id="S", value=100, type='number'),
            	],style={'width': '49%', 'display': 'inline-block'}),
       	html.Div([
            	html.Label("Strike", title=list_input["Strike"]),
            	dcc.Input(id="K", value=100, type='number')
        		],style={'width': '49%', 'display': 'inline-block'}),

    	#
    	html.Label('Drift', title=list_input["Drift"]),
        html.Div(id='drift'),
    	dcc.Slider(
    		id='mu',
        	min=-0.30,
        	max=0.30,
        	value=0.10,
        	step=0.01),
    	#
        html.Label('Volatility', title=list_input["Volatility"]),
        html.Div(id='sigma'),
    	dcc.Slider(
    		id='vol',
        	min=0,
        	max=1,
        	step=0.01,
        	value=0.20),
        #
        html.Label('Risk-free rate', title=list_input["Volatility"]),
        html.Div(id='riskfree'),
    	dcc.Slider(
    		id='Rf',
        	min=0,
        	max=0.1,
        	step=0.01,
        	value=0.05),
    	#
    	dcc.Markdown(children=graph_rep_strat_text),
        dcc.Graph(id='replication'),
        #
        dcc.Markdown(children=graph_held_shares_text),
        dcc.Graph(id='held_shares'),

    ], style={'float': 'left', 'width': '50%'}),

    # RIGHT - SCATTERPLOT
    html.Div([
    	html.Label('Maturity', title=list_input["Maturity"]),
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
        html.Div([
            	html.Label('Discretization step', title=list_input["Discretization step"]),
            	dcc.Input(id="dt", value=0.01, type='number')
        		],style={'width': '49%', 'display': 'inline-block'}),
        #
       	html.Div([
            	html.Label("Portfolio rebalancing", title=list_input["Rebalancing frequency"]),
            	dcc.Input(id="dt_p", value=1, type='number')
        		],style={'width': '49%', 'display': 'inline-block'}),
    	#
    	html.Label('Transaction costs', title=list_input["Transaction costs"]),
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
    	html.Br(),
    	html.Br(),
    	html.Br(),
    	html.Br(),
    	dcc.Markdown(children=graph_port_details_text),
        dcc.Graph(id='port_details'),
        #
        dcc.Markdown(children=graph_sde_deriv_text),
        dcc.Graph(id='sde_deriv'),

    ], style={'float': 'right', 'width': '50%'}),


])



@app.callback(
	Output('memory-output', 'data'),
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
def get_rep_strat_data(CallOrPut, S, K, Rf,T,mu,vol,dt,dt_p, TransactionCosts, FixedOrPropor, sde__seed):
	dt, K, discre_matu, StockPrice, OptionIntrinsicValue, OptionPrice, EquityAccount, CashAccount, Portfolio, V_t, f_t, f_x, f_xx = RepStrat_EU_Option_BSM_GBM_V4(CallOrPut, S, K, Rf, T, mu, vol, dt, dt_p, TransactionCosts, FixedOrPropor,  sde__seed)
																
	return dt, K, list(discre_matu), StockPrice, OptionIntrinsicValue, OptionPrice, EquityAccount, CashAccount, Portfolio, V_t, f_t, f_x, f_xx


@app.callback(
    Output('replication', 'figure'),
    [Input('memory-output', 'data'),])
def graph_rep_strat(data):
	dt, K, discre_matu, StockPrice, OptionIntrinsicValue, OptionPrice, EquityAccount, CashAccount, Portfolio, V_t, f_t, f_x, f_xx = data

	return{
    'data': [
        go.Scatter(
            x=discre_matu,
            y=StockPrice,
            mode='lines',
            opacity=0.7,
            name="Stock price simulation (GBM)"),
        go.Scatter(
        	x=discre_matu,
        	y=[K]*len(discre_matu),
        	mode='lines',
        	opacity=0.7,
        	name=f"Strike = {K}",
        	),
        go.Scatter(
        	x=discre_matu,
        	y=OptionIntrinsicValue,
        	mode="lines",
        	opacity=0.7,
        	name="Option intrinsic value"),
        go.Scatter(
        	x=discre_matu,
        	y=OptionPrice,
        	mode="lines",
        	opacity=0.7,
        	name="Option price"),
        go.Scatter(
        	x=discre_matu,
        	y=V_t,
        	mode="lines",
        	opacity=0.7,
        	name="SDE simulation"),  
        go.Scatter(
        	x=discre_matu,
        	y=Portfolio,
        	mode="lines",
        	opacity=0.7,
        	name="Portfolio"),
        go.Scatter(
        	x=[None], 
        	y=[None], 
        	mode='markers',
            name=f'Payoff - Portfolio: {round(OptionIntrinsicValue[-1]-EquityAccount[-1]-CashAccount[-1],2)}'),
    ],
    'layout': go.Layout(
        title={'yref':"paper",
        		'y':1,
        		"yanchor":"bottom"},
        margin={"t":15},
        xaxis={'title': f"Discretized time to maturity (dt={dt})"},
        yaxis={'title': "USD"},
    )
}


@app.callback(
    Output('port_details', 'figure'),
    [Input('memory-output', 'data'),])
def graph_portf_details(data):
	dt, K, discre_matu, StockPrice, OptionIntrinsicValue, OptionPrice, EquityAccount, CashAccount, Portfolio, V_t, f_t, f_x, f_xx = data
	return{
    'data': [
        go.Scatter(
            x=discre_matu,
            y=EquityAccount,
            mode='lines',
            opacity=0.7,
            name="Equity account"),
        go.Scatter(
        	x=discre_matu,
        	y=CashAccount,
        	mode='lines',
        	opacity=0.7,
        	name="Cash account",
        	),
        go.Scatter(
        	x=discre_matu,
        	y=Portfolio,
        	mode="lines",
        	opacity=0.7,
        	name="Portfolio"),
    ],
    'layout': go.Layout(
        margin={"t":15},
        xaxis={'title': f"Discretized time to maturity (dt={dt})"},
        yaxis={'title': "USD"},
    )
}


@app.callback(
    Output('held_shares', 'figure'),
    [Input('memory-output', 'data'),])
def graph_portf_details(data):
	dt, K, discre_matu, StockPrice, OptionIntrinsicValue, OptionPrice, EquityAccount, CashAccount, Portfolio, V_t, f_t, f_x, f_xx = data
	return{
    'data': [
        go.Scatter(
        	x=discre_matu,
        	y=f_x,
        	mode='lines',
        	opacity=0.7,
        	name="Held shares",
        	),
    ],
    'layout': go.Layout(
        margin={"t":15},
        xaxis={'title': f"Discretized time to maturity (dt={dt})"},
        yaxis={'title': "USD"},
    )
}

@app.callback(
    Output('sde_deriv', 'figure'),
    [Input('memory-output', 'data'),])
def graph_portf_details(data):
	dt, K, discre_matu, StockPrice, OptionIntrinsicValue, OptionPrice, EquityAccount, CashAccount, Portfolio, V_t, f_t, f_x, f_xx = data
	return{
    'data': [
        go.Scatter(
            x=discre_matu,
            y=f_t,
            mode='lines',
            opacity=0.7,
            name="Theta"),
        go.Scatter(
        	x=discre_matu,
        	y=f_x,
        	mode='lines',
        	opacity=0.7,
        	name="Delta",
        	),
        go.Scatter(
        	x=discre_matu,
        	y=f_xx,
        	mode="lines",
        	opacity=0.7,
        	name="Gamma"),
    ],
    'layout': go.Layout(
        #height=400,
        margin={"t":15},
        xaxis={'title': f"Discretized time to maturity (dt={dt})"},
        yaxis={'title': "USD"},
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

@app.callback(
    Output("popover", "is_open"),
    [Input("popover-target", "n_clicks")],
    [State("popover", "is_open")],
)
def toggle_popover(n, is_open):
    if n:
        return not is_open
    return is_open

if __name__ == '__main__':
    app.run_server(debug=True)