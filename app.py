import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
import plotly.graph_objs as go
from EU_Option_BSM_GBM_V5 import *
from descriptions import list_input
import base64

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP], external_scripts=['https://cdnjs.cloudflare.com/ajax/libs/mathjax/2.7.4/MathJax.js?config=TeX-MML-AM_CHTML', "./assets/mathjax.js"])
server = app.server

bg_color="#506784",
font_color="#F3F6FA"

email = "michelvanderhulst@student.uclouvain.be"



graph_rep_strat_text = ''' #### Replication strategy '''
graph_port_details_text = ''' #### Portfolio composition'''
graph_held_shares_text = ''' #### Held shares'''
graph_sde_deriv_text = ''' #### Option greeks '''
lul = 5

def header():
	return html.Div(
                id='app-page-header',
                children=[#html.Div(html.A(
		              #            id='lsm-logo', 
		              #            children=[html.Img(src='data:image/png;base64,{}'.format(base64.b64encode(open("output-onlinepngtools (1).png", 'rb').read()).decode()))],
		              #            href="https://uclouvain.be/en/faculties/lsm",
		              #            target="_blank", #open link in new tab
		              #            style={'margin':'20px'}
		              #              ), style={"display":"inline-block"}),
                    #
                    #
                    # html.Div(
	                   #  html.A(
	                   #  	id="nova-logo", 
	                   #  	children=[html.Img(src="data:image/png;base64,{}".format(base64.b64encode(open("output-onlinepngtools (2).png",'rb').read()).decode()))],
	                   #  	href="https://www2.novasbe.unl.pt/en/",
	                   #  	style={"margin":"-45px"}
	                   #  	  ), style={"display":"inline-block"}),
                    #
                    #
                    html.Div(children=[html.H3("European option replication strategy app"),
                    				   html.H4("Black-Scholes-Merton model")
                    				  ],
                       		 style={"display":"inline-block", "font-family":'sans-serif'}),
                    #
                    #
                    html.Div(children=[dbc.Button("About", id="popover-target", outline=True, style={"color":"white", 'border': 'solid 1px white'}),
                    	      		   dbc.Popover(children=[dbc.PopoverHeader("About"),
                    	      	       		   	             dbc.PopoverBody(["Michel Vanderhulst",                     	    
                    	      	       		   	             				  f"\n {email}", 
                    	      	       		   	             				  html.Hr(), 
                    	      	       		   	             				  "This app was built for my Master's Thesis, under the supervision of Prof. Frédéric Vrins (frederic.vrins@uclouvain.be)."
                    	      	       		   	             				  ],
                    	      	       		   	             				  #style={'padding':5}
                    	      	       		   	             				  ),
                    	      	       		   	             ],
                    	      	          		   id="popover",
                    	      	          		   #style={'width':'280px'},#,'height':'275px'},
                    	      	          		   is_open=False,
                    	      	          		   target="popover-target"),
                    	      		   ],
                    	      style={"display":"inline-block", "font-family":"sans-serif", 'marginLeft': '60%'}),
                		 ],
                style={
                    'background': bg_color,
                    'color': font_color,
                    'padding':20,
                    'margin':'-10px',
                }
            )



def body():
	return html.Div(children=[
            html.Div(id='left-column', children=[
                dcc.Tabs(
                    id='tabs', value='About this App',
                    children=[
                        dcc.Tab(
                            label='About this App',
                            value='About this App',
                            children=html.Div(children=[
                            	html.Br(),
                                html.H4('What is this app?', style={"text-align":"center"}),
                                html.P(
                                    """
                                    This app computes the replication strategy of vanilla European options on a set of given inputs, and compares its value against the traditional Black-Scholes-Merton
                                    price.                           
                                    """
                                ),
                                html.P(
                                    """
                                    The goal is to showcase that under the BSM model's assumptions (see "Model" tab), the price \(V_0\) given by the BSM formula is "arbitrage-free". Indeed, we show that in this case, 
                                    it is possible to build a strategy that 
                                    """
                                ),
                                html.Ul([html.Li("Can be initiated with \(V_0\) cash at time \(0\)."), 
                        				 html.Li('Is self-financing (i.e., no need to "feed" the strategy  with extra cash later'),
                        				 html.Li("Will deliver exactly the payoff of the option at maturity")]),
                                html.Hr(),
                                html.P(
                                    """
                                    Read more about options : 
                                    https://en.wikipedia.org/wiki/Option_(finance)
                                    
                                    """
                                ),
                            ])
                        ),
                        dcc.Tab(
                        	label="Model",
                        	value="Model",
                        	children=[html.Div(children=[
                        		html.Br(),
                        		html.H4("Model assumptions", style={"text-align":"center"}),
                        		"The BSM main assumptions are:",
                        		html.Ul([html.Li("It does not consider dividends and transaction costs"), 
                        				 html.Li("The volatility and risk-free rate are assumed constant"),
                        				 html.Li("Fraction of shares can be traded")]),
                        		html.P([
                        			"""Under BSM, the underlying asset's dynamics are modeled with a geometric Brownian motion: 
                        			$$dS_t = \mu S_tdt+\sigma S_tdW_t$$ Where \(\mu\) is the drift, \(\sigma\) the volatility, and \(dW_t\) the increment of a Brownian motion."""]),
                        		html.Hr(),
                        		html.H4("Type of options", style={"text-align":"center"}),
                        		html.P([
                        			"""
                        			The considered options are vanilla European options paying \(\psi(S_T)\) at maturity \(T\) where \(\psi(X)\) is the payoff function.
                        			For a call, the payoff function is \(\psi(S_T)=max(0,S_T-K)\) and for a put \(\psi(S_T)=max(0,K-S_T\) where K is the strike price.
                        			"""]),
                        		html.Hr(),
                        		html.H4("Option price", style={"text-align":"center"}),
								html.P([
                        			"""
                        			The call and put BSM pricing formula are well-known:
                        			$$C_t = S_t\Phi(d_1)-Ke^{-r(T-t)}\Phi(d_2)$$$$P_t = S_t\Phi(d_1)-Ke^{-r(T-t)}\Phi(d_2)$$ Where \(\Phi\) is the standard normal cumulative distribution function, 
                        			\(d_1\) and \(d_2\) constants \(d_1=\\frac{1}{\sigma\sqrt{T-t}}\left[ln(\\frac{S_t}{K})+(r+\\frac{\sigma^2}{2})(T-t)\\right]\), \(d_2=d_1-\sigma\\sqrt{T-t}\) where
                        			\(r\) is the risk-free rate. 
									These pricing formula originate from the BSM partial differential equation, which is valid for any type of European option:
                        			$$\\frac{\partial V_t}{\partial t}+\\frac{\sigma^{2}S^{2}_t}{2}\\frac{\partial^{2}V_t}{\partial S^{2}}+rS_t\\frac{\partial V_t}{\partial S} = rV_t$$
                        			Where \(V_t=f(t,S_t)\) the price of the option at time t. To get the pricing formulas, solve the PDE with terminal condition the payoff \(\psi(X)\) of the desired European-type option.
                        			"""]),
                        		])]),
                        # Where \(S_t\) is the price of the underlying asset at time t, \(\sigma\) the standard deviation of the underlying asset, \(r\) the risk-free rate. 
                        #
                        dcc.Tab(
                        	label="Approach",
                        	value="Methodology",
                        	children=[html.Div(children=[
                        		html.Br(),
                        		html.H4("Methodology followed", style={"text-align":"center"}),
                        		html.P([
                        			"""
                        			To prove that the BSM price is arbitrage-free, let us try to perfectly replicate it with a strategy. If the strategy is successfull, then 
                        			the BSM price is unique and therefore arbitrage-free.
                        			"""]),
                        		html.Hr(),
                        		html.H4("Replicating portfolio", style={"text-align":"center"}),
                        		html.Label("Step 1", style={'font-weight': 'bold'}),
                        		html.P([
                        			"""
                        			We infer the dynamics of the option price by applying Ito's lemma to the BSM PDE. Complying with Ito \(V_t=f(t,S_t)\):
                        			$$dV_t=\\left(f_t(t,S_t)+\\frac{\sigma^2S_t^2}{2}f_{xx}(t,S_t)\\right)dt+f_x(t,S_t)dS_t$$ Where \(f_i(t,S_t)\) are the partial derivatives.
                       				"""]),
                        		html.Label("Step 2", style={'font-weight': 'bold'}),
                       			html.P([
                       				"""
                       				The randomness embedded in \(S_t\), i.e. not knowing \(f(t,x)\), is taken care of by hedging \(dS_t\). This is better understood later on. Let us now  
                       				create a portfolio \(\Pi\) composed of a cash account and an equity account. At inception, we buy \(\Delta_0\) shares at cost \(\Delta_0S_0\). The reminder \(\Pi_0-\Delta_0S_0\) is cash.
                       				If the strategy is financially self-sufficiant, then 
                       				$$d\Pi_t=r(\Pi_t-\Delta_tS_t)dt+\Delta_tdS_t$$ 
                       				This means that the change in portfolio value results from the interests earned on the cash account and the gains/losses obtained by holding the stock. When we rebalance the portfolio to hold more
                       				(resp. less) shares, the cash is taken from (resp. placed on) the cash account. Notice that the cash account can go negative, in which case the interests will have to be paid (not received).                 
                       				"""]),
                       			# In other words, the only variation in the portfolio value is the risk-free received on the cash account and the underlying asset price variation.
                       			html.Label("Step 3", style={'font-weight': 'bold'}),
                       			html.P([
                       				"""
                       				In other words, the created portfolio \(\Pi\) will perfectly replicate the option price if \(\Delta_t=f_x(t,S_t)\). Indeed, the BSM PDE can be found from equating the two equations with that.
                       				"""]),
                       			html.P([
                       				"""
                       				\(\Delta_t=f_x(t,S_t)\) indicates the number of shares to hold at any instant in order to replicate the BSM price. 
                       				Deriving it, it is equal to \(\Delta_t = \nu\Phi(\nu d_1)\) Where \(\nu\) equals 1 for a call and -1 for a put.
                       				"""]),
                       			html.P([
                       				"""
                       				Holding \(\Delta_t = \nu\Phi(\nu d_1(t,S_t))\) at all times, we have found a strategy that perfectly replicates the BSM price, therefore proving it is the unique 
                       				price that prevents arbitrage opportunities. 
                       				"""]),
                       			html.P([
                       				""" 
                       				Indeed, because it is possible to generate the option’s payoff by being given exactly the cash amount \(V_0\) given by the BSM 
									formula, the option price must agree with \(V_0\). Otherwise, for \(k>0\), if the price of the option is \(V_0+k\), you can sell the option at \(V_0+k\), launch the strategy (which only requires \(V_0\)), and get a 
									profit of \(k\) today. At maturity, the strategy will deliver exactly the amount that you have to pay to the option’s buyer. If \(k<0\), do the opposite (buy the option, sell the strategy).
                       				"""]),
                       			html.P([
                       				"""
                       				The delta-hedging strategy is visually summarized in this table by Prof. Vrins (LSM, 2020). 
                       				"""]),
                       			dbc.Button("Show me the table", id="bsm-table-target", color="primary", className="mr-1",),
							    dbc.Popover(children=[dbc.PopoverHeader("delta-hedging strategy table"),
							            	 		  dbc.PopoverBody([html.Img(src="data:image/png;base64,{}".format(base64.b64encode(open("bsm-math.png",'rb').read()).decode())    , style={"width": "250%"})]),
							            	 		 ],
							            	 id="bsm-table",
							            	 is_open=False,
							        		 target="bsm-table-target",),
                        		])]),
                     	#
                     	#
                        dcc.Tab(
                            label='Inputs',
                            value='Inputs',
                            children=html.Div(children=[
                            					html.Br(),
                            					#
                            					html.P(
				                                    """
				                                    Place your mouse over any input to get its definition. Every time a parameter's value is changed, a new Brownian motion (hence the stock) is generated, 
				                                    unless "Set random generation seed" is selected. To analyze the impact of a parameter, it is advised to check this option.                 
				                                    """
				                                ),
                            					dcc.Dropdown(
                            						id='CallOrPut',
            										options=[{'label':'European Call option', 'value':"Call"},
            		 										 {'label':'European Put option', 'value':"Put"}],
            										value='Call'),
										        #
										        html.Br(),
										        #
										        html.Div(children=[html.Label('Spot price', title=list_input["Spot price"], style={'font-weight': 'bold', "text-align":"center", "width":"25%",'display': 'inline-block'} ),
										            			   dcc.Input(id="S", value=100, type='number', style={"width":"16%", 'display': 'inline-block'}),
										            			   html.Label("Strike", title=list_input["Strike"], style={'font-weight': 'bold',"text-align":"center", "width":"25%",'display': 'inline-block'} ),
										            			   dcc.Input(id="K", value=100, type='number', style={"width":"16%", 'display': 'inline-block'}),
										            			  ],),				       
										    	#
										    	html.Div(children=[html.Label("Drift", title=list_input["Drift"], style={'font-weight': 'bold', 'display': 'inline-block'}),
										    			  		   html.Label(id="drift", style={'display': 'inline-block'}),
										    			  		  ]),
										    	#
										    	dcc.Slider(id='mu', min=-0.30, max=0.30, value=0.10, step=0.01, marks={-0.30: '-30%', 0.30: '30%'}),
										    	#
										    	html.Div([html.Label('Volatility', title=list_input["Volatility"], style={'font-weight': 'bold', "display":"inline-block"}),
										    			  html.Label(id="sigma", style={"display":"inline-block"}),]),  
										    	#
										    	dcc.Slider(id='vol', min=0, max=1, step=0.01, value=0.20, marks={0:"0%", 1:"100%"}),
										        #
										        html.Div([html.Label('Risk-free rate', title=list_input["Risk-free rate"], style={'font-weight': 'bold', "display":"inline-block"}),
										    			  html.Label(id="riskfree", style={"display":"inline-block"}),]),  
										    	dcc.Slider(id='Rf', min=0, max=0.1, step=0.01, value=0.05, marks={0:"0%", 0.1:"10%"}),
										    	#
										    	html.Div([html.Label('Maturity', title=list_input["Maturity"], style={'font-weight':'bold', "display":"inline-block"}),
										    			  html.Label(id="matu", style={"display":"inline-block"}),]),										 
										    	dcc.Slider(id='T', min=0.25, max=5, # marks={i: '{}'.format(i) for i in range(6)},
										    			   marks={0.25:"3 months", 5:"5 years"}, step=0.25, value=3),
										    	#
										    	html.Br(),
										        html.Div([
										            	html.Label('Discretization step', title=list_input["Discretization step"], style={'font-weight': 'bold', "text-align":"left",'width': '50%', 'display': 'inline-block'}),
										            	dcc.Input(id="dt", value=0.01, type='number', style={"width":"16%", 'display': 'inline-block'}),
										        		]),
										        #
										       	html.Div([
										            	html.Label("Time between two rebalancing (in dt unit)", title=list_input["Rebalancing frequency"], style={'font-weight': 'bold', "text-align":"left",'width': '50%', 'display': 'inline-block'}),
										            	dcc.Input(id="dt_p", value=1, type='number', style={"width":"16%", 'display': 'inline-block'}),
										        		]),
										    	#
										    	html.Div([html.Label('Transaction costs', title=list_input["Transaction costs"], style={'font-weight': 'bold', "text-align":"left",'width': '50%', 'display': 'inline-block'}),
										    			  dcc.Input(id="TransactionCosts", value=0, type='number', style={"width":"16%", 'display': 'inline-block'}),
										    			]),
										    	#
										    	dcc.Checklist(
										    		id = "FixedOrPropor",
										       		options=[
										       			{'label': 'Fixed TC', 'value': 'FTC'},
										        		{'label': 'Proportional TC', 'value': 'PTC'}],
										        	value=[], #ADD AN S WHEN GOING ONLINE
										        	labelStyle={'padding':5, 'font-weight': 'bold', "text-align":"left", 'display': 'inline-block'}),
										    	#
										    	html.Label([dcc.Checklist(id = "seed",
										       							  options=[
										        								{'label': 'Set random generation seed', 'value': "seed"}],
										        								value=[], #ADD AN S WHEN GOING ONLINE
										        								labelStyle={'font-weight': 'bold', "text-align":"left", 'display': 'inline-block'}
										        	)], title=list_input["Seed"]),
                                            	])),
		],),], style={'float': 'left', 'width': '25%', 'margin':"30px"}),
	])


def graphs():
	return html.Div(id='right-column', 
					children=[
						html.Br(),
						html.Div([
				        	html.Div(children=[dcc.Markdown(children=graph_port_details_text),
					        				   dcc.Graph(id='port_details'),],
					        		 style={"float":"right", "width":"45%", "display":"inline-block"}),
				        	html.Div(children=[dcc.Markdown(children=graph_rep_strat_text),
				        					  dcc.Graph(id='replication'),],
				        			 style={"float":"right", "width":"55%", "display":"inline-block"}),
				        		]),
			        	html.Div([
			        		html.Div(children=[dcc.Markdown(children=graph_sde_deriv_text),
				        					   dcc.Graph(id='sde_deriv'),],
				        			 style={"float":"right", "width":"45%", "display":"inline-block"}),
			        		html.Div(children=[dcc.Markdown(children=graph_held_shares_text),
			        						   dcc.Graph(id='held_shares'),],
			        				 style={"float":"right", "width":"55%", "display":"inline-block"}),
				        		]),
							 ], 
					style={'float': 'right', 'width': '70%'})


app.layout = html.Div(
				id='main_page',
        		children=[
            		dcc.Store(id='memory-output'),
            		header(),
            		body(),
            		graphs(),
        		 		 ],
    				 )


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
	dt, K, discre_matu, StockPrice, OptionIntrinsicValue, OptionPrice, EquityAccount, CashAccount, Portfolio, V_t, f_t, f_x, f_xx = RepStrat_EU_Option_BSM_GBM_V5(CallOrPut, S, K, Rf, T, mu, vol, dt, dt_p, TransactionCosts, FixedOrPropor,  sde__seed)			
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
            line={'dash': 'solid', 'color': 'light blue'},
            opacity=0.7,
            name="Stock price simulation (GBM)"),
        # go.Scatter(
        # 	x=discre_matu,
        # 	y=[K]*len(discre_matu),
        # 	mode='lines',
        # 	opacity=0.7,
        # 	name=f"Strike = {K}",
        # 	),
        go.Scatter(
        	x=discre_matu,
        	y=OptionIntrinsicValue,
        	mode="lines",
        	line={'dash': 'dash', 'color': 'green'},
        	opacity=0.7,
        	name="Option intrinsic value"),
        go.Scatter(
        	x=discre_matu,
        	y=OptionPrice,
        	mode="lines",
        	line={'dash': 'solid', 'color': 'green'},
        	opacity=0.7,
        	name="Option price"),
        # go.Scatter(
        # 	x=discre_matu,
        # 	y=V_t,
        # 	mode="lines",
        # 	opacity=0.7,
        # 	name="SDE simulation"),  
        go.Scatter(
        	x=discre_matu,
        	y=Portfolio,
        	mode="lines",
        	line={'dash': 'solid', 'color': 'red'},
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
        xaxis={'title': f"Discretized time to maturity"},
        yaxis={'title': "Currency"},
        legend=dict(
	        x=0,
	        y=1,
	        traceorder='normal',
	        bgcolor='rgba(0,0,0,0)'),
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
            line={'dash': 'solid', 'color': 'orange'},
            opacity=0.7,
            name="Equity account"),
        go.Scatter(
        	x=discre_matu,
        	y=CashAccount,
        	mode='lines',
        	line={'dash': 'solid', 'color': 'purple'},
        	opacity=0.7,
        	name="Cash account",
        	),
        go.Scatter(
        	x=discre_matu,
        	y=Portfolio,
        	mode="lines",
        	line={'dash': 'solid', 'color': 'red'},
        	opacity=0.7,
        	name="Portfolio"),
    ],
    'layout': go.Layout(
        margin={"t":15},
        xaxis={'title': f"Discretized time to maturity"},
        yaxis={'title': "Currency"},
        legend=dict(
	        x=0,
	        y=1,
	        traceorder='normal',
	        bgcolor='rgba(0,0,0,0)'),
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
        xaxis={'title': f"Discretized time to maturity"},
        yaxis={'title': "Shares"},
        legend=dict(
	        x=0,
	        y=1,
	        traceorder='normal',
	        bgcolor='rgba(0,0,0,0)'),
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
        xaxis={'title': f"Discretized time to maturity"},
        yaxis={'title': "Currency"},
        legend=dict(
	        x=0,
	        y=1,
	        traceorder='normal',
	        bgcolor='rgba(0,0,0,0)'),
    )
}


@app.callback(Output('drift', 'children'),
              [Input('mu', 'value')])
def display_value(value):
    return f': {int(value*100)}%'

@app.callback(Output('sigma', 'children'),
			  [Input('vol', 'value')])
def display_value2(value):
    return f': {int(value*100)}%'

@app.callback(Output('riskfree', 'children'),
			  [Input('Rf', 'value')])
def display_value3(value):
    return f': {int(value*100)}%'

@app.callback(Output('matu', 'children'),
			  [Input('T', 'value')])
def display_value4(value):
	if value==0.25 or value==0.5 or value==0.75:
		return f": {int(value*12)} months"
	elif value == 1:
		return f': {value} year'
	else:
		return f': {value} years'

@app.callback(
    Output("popover", "is_open"),
    [Input("popover-target", "n_clicks")],
    [State("popover", "is_open")],
)
def toggle_popover(n, is_open):
    if n:
        return not is_open
    return is_open



@app.callback(
    Output("bsm-table", "is_open"),
    [Input("bsm-table-target", "n_clicks")],
    [State("bsm-table", "is_open")],
)
def toggle_popover(n, is_open):
    if n:
        return not is_open
    return is_open

if __name__ == '__main__':
    app.run_server(debug=True)