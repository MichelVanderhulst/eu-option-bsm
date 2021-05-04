####################################################################
################## LIBRARIES IMPORT ################################
## APP-RELATED LIBRARIES
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
import plotly.graph_objs as go

# Importing app header, body and graphs from the other .py scripts
from appHeader import header
from appBody import body, graphs

## Rep strat math function
from EU_Option_BSM_GBM import *

# Allowing rep strat excel export
import pandas as pd
import urllib.parse
####################################################################


####################################################################
################## CREATING THE APP ################################ 
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP], #modern-looking buttons, sliders, etc
	                      external_scripts=['https://cdnjs.cloudflare.com/ajax/libs/mathjax/2.7.4/MathJax.js?config=TeX-MML-AM_CHTML', "./assets/mathjax.js"], #LaTeX in app
	                      meta_tags=[{"content": "width=device-width"}] # app width adapts itself to the user device
	                      )
server = app.server

# building the app layout from header, body & graphs
app.layout = html.Div(
                id='main_page',
                children=[
                    dcc.Store(id='memory-output'),
                    header(),
                    body(),
                    graphs(),
                         ],
                     )
#####################################################################

#####################################################################
################## APP CALLBACKS : DYNAMICITY & INTERACTIVITY ######

##  RUNNING THE REPLICATION STRATEGY & IMPORTING THE VALUES
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
def get_rep_strat_data(CallOrPut, S, K, Rf,T,mu,vol,dt,dt_p, TransactionCosts, FixedOrPropor, seed):
    dt, K, discre_matu, StockPrice, OptionIntrinsicValue, OptionPrice, EquityAccount, CashAccount, Portfolio, V_t, f_t, f_x, f_xx, cash_bfr, cash_aft, equi_bfr, equi_aft, t = RepStrat_EU_Option_BSM_GBM(CallOrPut, S, K, Rf, T, mu, vol, dt, dt_p, TransactionCosts, FixedOrPropor, seed)          
    return dt, K, list(discre_matu), StockPrice, OptionIntrinsicValue, OptionPrice, EquityAccount, CashAccount, Portfolio, V_t, f_t, f_x, f_xx, cash_bfr, cash_aft, equi_bfr, equi_aft, t

## PLOT 1 : REP STRAT + OPTION PRICE + STOCK SIMULATION
@app.callback(
    Output('replication', 'figure'),
    [Input('memory-output', 'data'),])
def graph_rep_strat(data):
    dt, K, discre_matu, StockPrice, OptionIntrinsicValue, OptionPrice, EquityAccount, CashAccount, Portfolio, V_t, f_t, f_x, f_xx, cash_bfr, cash_aft, equi_bfr, equi_aft, t = data

    return{
    'data': [
        go.Scatter(
            x=discre_matu,
            y=StockPrice,
            mode='lines',
            line={'dash': 'solid', 'color': 'light blue'},
            opacity=0.7,
            name="Stock price simulation (GBM)"),
        go.Scatter(
          x=discre_matu,
          y=[K]*len(discre_matu),
          mode='lines', 
          line={'dash': 'dash'},
          opacity=0.7,
          name=f"Strike price",
          ),
        # go.Scatter(
        #   x=discre_matu,
        #   y=OptionIntrinsicValue,
        #   mode="lines",
        #   line={'dash': 'dash', 'color': 'green'},
        #   opacity=0.7,
        #   name="Option intrinsic value"),
        go.Scatter(
            x=discre_matu,
            y=OptionPrice,
            mode="lines",
            line={'dash': 'solid', 'color': 'green'},
            opacity=0.7,
            name="Option price"),
        # go.Scatter(
        #   x=discre_matu,
        #   y=V_t,
        #   mode="lines",
        #   opacity=0.7,
        #   name="SDE simulation"),  
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

## PLOT 2 : REP STRAT PORTFOLIO DETAILS (Cash account, equity account)
@app.callback(
    Output('port_details', 'figure'),
    [Input('memory-output', 'data'),])
def graph_portf_details(data):
    dt, K, discre_matu, StockPrice, OptionIntrinsicValue, OptionPrice, EquityAccount, CashAccount, Portfolio, V_t, f_t, f_x, f_xx, cash_bfr, cash_aft, equi_bfr, equi_aft, t = data
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

## PLOT 3 : HELD SHARES AT ALL TIMES IN EQUITY ACCOUNT
@app.callback(
    Output('held_shares', 'figure'),
    [Input('memory-output', 'data'),])
def graph_portf_details(data):
    dt, K, discre_matu, StockPrice, OptionIntrinsicValue, OptionPrice, EquityAccount, CashAccount, Portfolio, V_t, f_t, f_x, f_xx, cash_bfr, cash_aft, equi_bfr, equi_aft, t = data
    return{
    'data': [
        go.Scatter(
            x=discre_matu,
            y=f_x,
            mode='lines',
            line={'dash': 'solid', 'color': 'light blue'},
            opacity=0.7,
            name="Held shares (Delta)",
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

## PLOT 4 : OPTION GREEKS
@app.callback(
    Output('sde_deriv', 'figure'),
    [Input('memory-output', 'data'),])
def graph_portf_details(data):
    dt, K, discre_matu, StockPrice, OptionIntrinsicValue, OptionPrice, EquityAccount, CashAccount, Portfolio, V_t, f_t, f_x, f_xx, cash_bfr, cash_aft, equi_bfr, equi_aft, t = data
    return{
    'data': [
        go.Scatter(
            x=discre_matu,
            y=f_x,
            mode='lines',
            line={'dash': 'solid', 'color': 'light blue'},
            opacity=0.7,
            name="Delta",
            ),
        go.Scatter(
            x=discre_matu,
            y=f_t,
            mode='lines',
            opacity=0.7,
            name="Theta"),
        go.Scatter(
            x=discre_matu,
            y=f_xx,
            mode="lines",
            opacity=0.7,
            name="Gamma",
            yaxis="y2"),
    ],
    'layout': go.Layout(
        #height=400,
        margin={"t":15},
        xaxis={'title': f"Discretized time to maturity"},
        yaxis={'title': "Delta & Theta"},
        yaxis2={'title':'Gamma',
                'overlaying':'y',
                'side':'right'},
        legend=dict(
            x=0,
            y=1,
            traceorder='normal',
            bgcolor='rgba(0,0,0,0)'),
    )
}


## DOUBLE-CHECKING USER INPUT
@app.callback(Output('message_S', 'children'),
              [Input('S', 'value')])
def check_input_S(S):
    if S<0:
        return f'Cannot be lower than 0.'
    else:
        return ""

@app.callback(Output('message_K', 'children'),
              [Input('K', 'value')])
def check_input_K(K):
    if K<0:
        return f'Cannot be lower than 0.'
    else:
        return ""

@app.callback(Output('message_dt', 'children'),
              [Input('T', 'value'),
              Input("dt", "value")])
def check_input_dt(T, dt):
    if dt<0.001:
        return f'Lower than 0.001 will make the app run very slowly'
    elif dt > T:
        return f"Cannot be higher than {T}"
    else:
        return ""   

@app.callback(Output('message_dt_p', 'children'),
              [Input('T', 'value'),
              Input("dt", "value"),
              Input("dt_p","value")])
def check_input_dt_p(T, dt, dt_p):
    if dt_p<=0:
        return f'Cannot be lower than 1.'
    elif dt_p > (T/dt):
        return f"Cannot be higher than {T/dt}"
    else:
        return ""  

## INPUTS VISUALS
@app.callback(Output('drift', 'children'),
              [Input('mu', 'value')])
def display_value_mu(value):
    return f': {int(value*100)}%'

@app.callback(Output('sigma', 'children'),
              [Input('vol', 'value')])
def display_value_vol(value):
    return f': {int(value*100)}%'

@app.callback(Output('riskfree', 'children'),
              [Input('Rf', 'value')])
def display_value_Rf(value):
    return f': {int(value*100)}%'

@app.callback(Output('matu', 'children'),
              [Input('T', 'value')])
def display_value_T(value):
    if value==0.25 or value==0.5 or value==0.75:
        return f": {int(value*12)} months"
    elif value == 1:
        return f': {value} year'
    else:
        return f': {value} years'       

@app.callback(Output('TransactionCosts', 'value'),
              [Input('FixedOrPropor', 'value')])
def display_value_TC(value):
    if value=="NTC":
        return 0

@app.callback(Output('unit_TC', 'children'),
              [Input('FixedOrPropor', 'value')])
def display_unit_TC(value):
    if value == "FTC":
        return "$"
    elif value == "PTC":
        return "%"
    else:
        return ""

## EXCEL EXPORT
@app.callback(Output('download-link', 'href'), 
             [Input('memory-output', 'data')])
def update_download_link(data):
    dt, K, discre_matu, StockPrice, OptionIntrinsicValue, OptionPrice, EquityAccount, CashAccount, Portfolio, V_t, f_t, f_x, f_xx, cash_bfr, cash_aft, equi_bfr, equi_aft, t = data
    cash_bfr, cash_aft, equi_bfr, equi_aft, t = np.array(cash_bfr), np.array(cash_aft), np.array(equi_bfr), np.array(equi_aft), np.array(t)

    df = pd.DataFrame({"Time (in dt)":t,"Stock price":StockPrice, "Option intrinsic value":OptionIntrinsicValue, "Option price":OptionPrice,
                               "Delta":f_x, "Cash before":cash_bfr, "Equity before":equi_bfr, "Portfolio before":cash_bfr+equi_bfr,
                               "Cash after":cash_aft, "Equity after":equi_aft, "Portfolio after":cash_aft+equi_aft, "Replication strategy error":OptionPrice-cash_aft-equi_aft})
    df = df.round(6)
    csv_string = df.to_csv(index=False, encoding="utf-8")
    csv_string = 'data:text/csv;charset=utf-8,' + urllib.parse.quote(csv_string)
    return csv_string

## MISC. STUFF
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


## MAIN FUNCTION
if __name__ == '__main__':
    app.run_server(debug=True)
