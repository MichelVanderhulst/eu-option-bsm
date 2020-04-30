#####################################################################################
# European Options
# Geometric Brownian Motion
### SOURCES:
## SLIDES Credit and Interest Rate Risk: sl. 27 & 30
## SDE Simulation: BSM.R file from Prof. Vrins
#####################################################################################

import numpy as np
#import matplotlib.pyplot as plt
from scipy.stats import norm
# import warnings
# warnings.filterwarnings("ignore", message="invalid value encountered in sqrt")
# warnings.filterwarnings("ignore", message="divide by zero encountered in double_scalars")
# warnings.filterwarnings("ignore", message="invalid value encountered in double_scalars")
# from VNiels.App.Classes.Input.Input_objects import spot_price, strike, risk_free_rate, maturity, drift, volatility, discretization_step, rebalancing_frequency, transaction_costs, fixed_transaction_costs, proportional_transaction_costs, sde_simul


def d1(S, strike, Rf, T, t, vol):
    if t<T:
        return (np.log(S / strike) + (T - t) * (Rf + 0.5 * vol * vol)) / (vol * np.sqrt(T - t))
    else:
        if S > strike:     # d1 = + infinity
            return 10E9
        elif S == strike:  # d1 = 0
            return 0
        elif S < strike:   # d1 = - infinity
            return -10E9

def d2(S, strike, Rf, T, t, vol):
    if t<T:
        return (np.log(S / strike) + (T - t) * (Rf - 0.5 * vol * vol)) / (vol * np.sqrt(T - t))
    else:
        if S > strike:     # d1 = + infinity
            return 10E9
        elif S == strike:  # d1 = 0
            return 0
        elif S < strike:   # d1 = - infinity
            return -10E9


def p_bs(S, strike, Rf, T, t, vol, phi):
    return phi*(S*norm.cdf(phi * d1(S, strike, Rf, T, t, vol)) - strike * np.exp(-Rf*(T-t)) * norm.cdf( phi*d2(S, strike, Rf, T, t, vol)))


def Delta(S, K, Rf, T, t, vol, phi):
    return  phi*norm.cdf(phi*d1(S, K, Rf, T, t, vol))


def Gamma(S, K, Rf, T, t, vol):
    return (norm.pdf(d1(S, K, Rf, T, t, vol)))/(S*vol*np.sqrt(T-t))


def Theta(S, K, Rf, T, t, vol, phi):
    return ( phi*(-Rf*K*np.exp(-Rf*(T-t))*norm.cdf(phi*d2(S, K, Rf, T, t, vol)))   -  ((S*vol*norm.pdf(d1(S, K, Rf, T, t, vol)))/(2*np.sqrt(T-t)))  )


def RepStrat_EU_Option_BSM_GBM_V4(CallOrPut, S,K,Rf,T,mu,vol,dt,RebalancingSteps, TransactionCosts, FixedOrPropor, sde_simulation):
    ####################################################################################################################
    #####################              START Derivative/Model variables initialization             #####################
    # S = spot_price.get_value()
    # K = strike.get_value()
    # Rf = risk_free_rate.get_value()
    # T = maturity.get_value()
    # mu = drift.get_value()
    # vol = volatility.get_value()
    # dt = discretization_step.get_value()
    # RebalancingSteps = rebalancing_frequency.get_value()
    # TransactionCosts = transaction_costs.get_value()
    # Fixed = fixed_transaction_costs.get_value()
    # Propor = proportional_transaction_costs.get_value()
    # sde_simulation = sde_simul.get_value()
    #S,K,Rf,T,mu,vol,dt,RebalancingSteps, TransactionCosts, Fixed, Propor, sde_simulation = 100, 100, 2, 2, 15, 15, 0.01, 1, 0,0,0,0
    #####################                END Derivative/Model variables initialization             #####################
    ####################################################################################################################

    ####################################################################################################################
    #####################  START derivative/model strings specifics, user input transformation,    #####################
    #####################        discretization of continuous [0,T] period and rebalancing period  #####################
    #####################        computation

    ####### derivative/model strings specifics
    
    phi= 0, 0, 0, r"$S_{i}=S_{i-1}e^{(\mu-\frac{\sigma^{2}}{2})\delta+\sigma*\sqrt{\delta}*z}$"
    deltarebal = r"$\delta_{rebal}$"
    if CallOrPut == "Call":
        phi = 1
        BSformula = "$S\Phi(d_1) - Ke ^ {rT}\Phi(d_2)$ = "
        Deltaformula = "$\Delta_t = \Phi(d_1(t,S_t))$"
    elif CallOrPut == "Put":
        phi = -1
        sign = "-"
        BSformula = "$K\Phi(-d_2)e^{rT}-S\Phi(-d_1) = $"
        Deltaformula = "$\Delta_t = - \Phi(-d_1(t,S_t))$"

    if FixedOrPropor == ["FTC"]:
        Fixed, Propor = 1, 0
    elif FixedOrPropor == ["PTC"]:
        Propor, Fixed = 1, 0 
    elif FixedOrPropor ==[]:
        Fixed, Propor = 0, 0
    elif FixedOrPropor == ["FTC", "PTC"] or FixedOrPropor == ["PTC", "FTC"]:
        Fixed, Propor = 1, 1

    if TransactionCosts == None:
        TransactionCosts = 0

    if sde_simulation == ["seed"]:
        np.random.seed(1)



    #######  user input transformation
    # Careful for Transaction Costs. Supposed to be in basis points. 1 BASIS POINT = 0.01 %
    Rf, mu, vol, TransactionCosts = Rf, mu, vol, TransactionCosts / 100

    ####### Discretization of maturity period
    # The matrix length depends on T and dt chosen by user.

    if dt == 0:
        dt = 0.01

    t = np.arange(0, T + dt, dt)
    nt = len(t)
    a = range(nt)

    ####### Rebalancing period computation
    # t_rebal is the rebalancing time.
    # If rebalancing steps = 1, then dt_rebal = dt, and therefore t_rebal = t.
    # If rebalancing steps > 1, then dt_rebal =/= dt, and therefore t_rebal =/= t.
    # It will be used for the portfolio rebalancing, given that in the later condition, its timeline will be different
    # than the stock's.
    dt_rebal = dt * RebalancingSteps
    t_rebal = np.arange(0, T + dt_rebal, dt_rebal)
    #####################    END derivative/model strings specifics, user input transformation,    #####################
    #####################        discretization of continuous [0,T] period and rebalancing period  #####################
    #####################        computation

    ####################################################################################################################
    #####################                  START accounts initialization                           #####################
    f_xx, f_t, f_x, V_t, CashAccount, EquityAccount, StockPrice, OptionIntrinsicValue, OptionPrice, BrownianMotion = \
        np.zeros(nt), np.zeros(nt), np.zeros(nt), np.zeros(nt), np.zeros(nt), np.zeros(nt), np.zeros(nt), np.zeros(nt),\
        np.zeros(nt), np.zeros(nt)
    dW = np.sqrt(dt) * np.random.randn(nt - 1)  # Increments of Brownian Motion
    #####################                      END accounts initialization                         #####################
    ####################################################################################################################

    ####################################################################################################################
    #####################                  START replication strategy                              #####################
    ####### t = 0.
    StockPrice[0] = S
    OptionIntrinsicValue[0] = max(0, phi * (S - K))
    OptionPrice[0] = p_bs(S, K, Rf, T, t[0], vol, phi)
    BrownianMotion[0] = 0
    f_x[0] = Delta(StockPrice[0], K, Rf, T, t_rebal[0], vol, phi)  # putcall parity! -delta(-d1) = delta(d1) - 1
    CashAccount[0] = OptionPrice[0] - f_x[0] * S - abs(f_x[0]) * (Fixed * TransactionCosts + StockPrice[0] * Propor * TransactionCosts)
    EquityAccount[0] = f_x[0] * S

    # In case user wishes for SDE Simulation Check

    f_xx[0] = Gamma(StockPrice[0], K, Rf, T, t_rebal[0], vol)
    f_t[0] = Theta(StockPrice[0], K, Rf, T, t_rebal[0], vol, phi)
    V_t[0] = OptionPrice[0]

    #######  0 < t <= T
    # Reminder : nt = len(np.arange(0,T+dt,dt))
    #           function range() is [1,nt[. 1 included, last of nt not included.
    #           This loop stops at maturity T.
    for i in range(1, nt):
        ####### Stock price simulation
        BrownianMotion[i] = BrownianMotion[i - 1] + dW[i - 1]
        StockPrice[i] = StockPrice[0] * np.exp((mu - 0.5 * (vol * vol)) * t[i] + vol * BrownianMotion[i])

        ####### Option intrinsic value & price
        OptionIntrinsicValue[i] = max(0, phi * (StockPrice[i] - K))
        OptionPrice[i] = p_bs(StockPrice[i], K, Rf, T, t[i], vol, phi)

        ####### Replication strategy
        # Portfolio is rebalanced every Rebalancing Step, so in order to recognize them we take the modulus of i, the
        # discretization step, and if it is equal to zero then i is an rebalancing step:
        if i % RebalancingSteps == 0:
            ####### Before rebalancing
            # accrued interest on CashAccount & Updating EquityAccount to stock price evolution
            CashAccount[i] = CashAccount[i - 1] * (1 + Rf * dt_rebal)
            EquityAccount[i] = f_x[i - 1] * StockPrice[i]

            ####### After reblancing
            # computing delta (# of shares to hold at this time t), ensuring equivalence of portfolio and selling/buying
            # shares to get delta and updating EquityAccount value with current Delta
            f_x[i] = Delta(StockPrice[i], K, Rf, T, t_rebal[int(i/RebalancingSteps)], vol, phi)
            CashAccount[i] = CashAccount[i] + EquityAccount[i] - f_x[i] * StockPrice[i] - abs(f_x[i] - f_x[i - 1]) * (Fixed * TransactionCosts + StockPrice[i] * Propor * TransactionCosts)
            EquityAccount[i] = f_x[i] * StockPrice[i]

            ####### In case user wishes for SDE Simulation Check

            f_xx[i] = Gamma(StockPrice[i], K, Rf, T, t_rebal[int(i / RebalancingSteps)], vol)
            f_t[i] = Theta(StockPrice[i], K, Rf, T, t_rebal[int(i / RebalancingSteps)], vol, phi)
            V_t[i] = V_t[i - 1] + (f_t[i - 1] + mu * StockPrice[i - 1] * f_x[i - 1] + 0.5 * (vol * vol) * (StockPrice[i - 1] * StockPrice[i - 1]) * f_xx[i - 1]) * dt_rebal + vol * StockPrice[i - 1] * f_x[i - 1] * dW[i - 1]

        # not a rebalancing step
        else:
            f_x[i] = f_x[i - 1]
            CashAccount[i] = CashAccount[i - 1]
            EquityAccount[i] = EquityAccount[i - 1]

            ####### In case user wishes for SDE Simulation Check
            f_xx[i] = f_xx[i - 1]
            f_t[i] = f_t[i - 1]
            V_t[i] = V_t[i - 1]
    #####################                  END replication strategy                                #####################
    ####################################################################################################################

    ####################################################################################################################
    #####################                  START graphics                                          #####################


    return a, StockPrice, OptionIntrinsicValue, OptionPrice, EquityAccount, CashAccount, V_t




    # plt.ion()
    # fig = plt.figure()
    # plt.suptitle(f"{CallOrPut} self-financing replication strategy")
    #
    # if sde_simulation == 0:
    #     plt.subplot(2, 2, 1)
    #     plt.plot()
    #     plt.title("Model and replication strategy description")
    #     plt.xticks([])
    #     plt.yticks([])
    #     textstr = '\n'.join((
    #         f"Black-Scholes-Merton model, with stock dynamics modeled with a geometric",
    #         f"brownian motion of drift {round(mu*100,2)}% and volatility {round(vol*100,2)}%: {GBM}",
    #         r"Its main assumptions are the absence of dividends, transactions costs, ",
    #         "constant risk-free rate and volatility, and allowed fractions of shares.",
    #         "",
    #         f"To prove that the BSM is arbitrage-free, let's replicate the {CallOrPut.lower()} option payoff",
    #         f"starting with only its BSM price: {BSformula} = {round(p_bs(S, K, Rf, T,0, vol,phi), 2)}.",
    #         f"To do so, compute at each rebalancing step {deltarebal} = {dt_rebal}:  {Deltaformula} which",
    #         "will tell the number of stock shares to hold at that moment in order to be",
    #         "delta-hedged ,i.e. hedged against the changes in the underlying's stock price.",
    #         "For example, $\Delta_0 = $" + str(round(f_x[0], 2)) + ", which means that at $t = 0$ we need to hold " + str(round(f_x[0], 2)) + " shares",
    #         "to delta-hedge the option, i.e. neutralize the extent of the move in the",
    #         "option's price relative to the underlying's asset price.",
    #         "",
    #         "Replication Strategy Error = Option payoff - Final Portfolio Value = " + str(round(OptionIntrinsicValue[-1]-(CashAccount[-1] + EquityAccount[-1]), 2)))) #+ ", Rebalance steps = " + str(RebalancingSteps)))
    #     plt.text(-0.03, 0.95, textstr, verticalalignment='top')
    #
    #     plt.subplot(2, 2, 2)
    #     plt.title(f"{CallOrPut} option replication strategy")
    #     plt.plot(a, CashAccount[:], label="Cash account")
    #     plt.plot(a, EquityAccount[:], label="Equity account")
    #     plt.plot(a, EquityAccount[:] + CashAccount[:], label="Portfolio")
    #     plt.ylabel("USD")
    #     plt.legend()
    #
    #     plt.subplot(2, 2, 3)
    #     plt.title("Held shares in the replication strategy")
    #     plt.plot(a, f_x[:], label=f"{Deltaformula}")
    #     plt.legend()
    #     plt.xlabel(f"Discretized maturity period ($\delta=${dt})")
    #     plt.ylabel("Held shares")
    #
    #     plt.subplot(2, 2, 4)
    #     plt.title(f"{CallOrPut} option GBM simulation")
    #     plt.plot(a, StockPrice[:], label="Stock price simulation (GBM)")
    #     plt.axhline(y=K, ls="dashed", label=f"Strike = {round(K,2)}")
    #     plt.plot(a, OptionIntrinsicValue[:], label=f"{CallOrPut} intrinsic value")
    #     plt.plot(a, OptionPrice[:], label=f"{CallOrPut} option price")
    #     plt.plot(a, EquityAccount[:] + CashAccount[:], label="Portfolio")
    #     plt.xlabel(f"Discretized maturity period ($\delta=${dt})")
    #     plt.ylabel("USD")
    #     plt.legend()
    #     plt.pause(0.002)
    #     plt.show()
    #
    # elif sde_simulation == 1:
    #     plt.subplot(2, 3, 1)
    #     plt.plot()
    #     plt.title("Model and replication strategy description")
    #     plt.xticks([])
    #     plt.yticks([])
    #     textstr = '\n'.join((str(round(OptionIntrinsicValue[-1]-(CashAccount[-1] + EquityAccount[-1]), 2)))) #+ ", Rebalance steps = " + str(RebalancingSteps)))
    #     plt.text(-0.03, 0.95, textstr, verticalalignment='top')
    #
    #     plt.subplot(2, 3, 2)
    #     plt.title(f"{CallOrPut} option replication strategy")
    #     plt.plot(a, CashAccount[:], label="Cash account")
    #     plt.plot(a, EquityAccount[:], label="Equity account")
    #     plt.plot(a, EquityAccount[:] + CashAccount[:], label="Portfolio")
    #     plt.ylabel("USD")
    #     plt.legend()
    #
    #     plt.subplot(2, 3, 3)
    #     plt.title("Held shares in the replication strategy")
    #     plt.plot(a, f_x[:], label=f"{Deltaformula}")
    #     plt.legend()
    #     # plt.xlabel(f"Discretized maturity period ($\delta=${dt})")
    #     plt.ylabel("Held shares")
    #
    #     plt.subplot(2,3,4)
    #     plt.title(f"{CallOrPut} option Greeks")
    #     plt.plot(a, f_x[:], label="Delta")
    #     plt.plot(a, f_t[:], label="Theta")
    #     plt.plot(a, f_xx[:], label="Gamma")
    #     plt.ylabel("USD")
    #     plt.legend()
    #
    #     gs = fig.add_gridspec(2, 3)
    #     fig.add_subplot(gs[-1,1:])
    #     #plt.subplot(2, 2, 4)
    #     plt.title(f"{CallOrPut} option GBM simulation")
    #     plt.plot(a, StockPrice[:], label="Stock price simulation (GBM)")
    #     plt.axhline(y=K, ls="dashed", label=f"Strike = {round(K,2)}")
    #     plt.plot(a, OptionIntrinsicValue[:], label=f"{CallOrPut} intrinsic value")
    #     plt.plot(a, OptionPrice[:], label=f"{CallOrPut} option price")
    #     plt.plot(a, V_t[:], label="SDE Simulation")
    #     plt.plot(a, EquityAccount[:] + CashAccount[:], label="Portfolio")
    #     plt.xlabel(f"Discretized maturity period ($\delta=${dt})")
    #     plt.ylabel("USD")
    #     plt.legend()
    #     plt.pause(0.002)
    #     plt.show()
    #####################                  END graphics                                          #######################
    ####################################################################################################################
#RepStrat_EU_Option_BSM_GBM_V4("Call")


# def p_bs(S, strike, Rf, T, t, vol, phi):
#     return phi*(S*CDFd1(S, strike, Rf, T, t, vol, phi) - strike*np.exp(-Rf*(T-t))*CDFd2(S, strike, Rf, T, t, vol, phi))
#
#
# def RepStrat_EU_Option_BSM_GBM_V4(CallOrPut):
#     S = spot_price.get_value()
#     K = strike.get_value()
#     Rf = risk_free_rate.get_value()
#     T = maturity.get_value()
#     mu = drift.get_value()
#     vol = volatility.get_value()
#     dt = discretization_step.get_value()
#     RebalancingSteps = rebalancing_frequency.get_value()
#     TransactionCosts = transaction_costs.get_value()
#     Fixed = fixed_transaction_costs.get_value()
#     Propor = proportional_transaction_costs.get_value()
#     sde_simulation = sde_simul.get_value()
#
#     # In case tests are needed
#     # S,K,Rf,T,mu,vol,dt,RebalancingSteps,TransactionCosts,Fixed,Propor=10,10,2,2,5,15,0.01,1,0,0,0
#
#     # Can be ignored. Just some strings that correspond to call or put.
#     phi, BSformula, Deltaformula, GBM = 0, 0, 0 , r"$S_{i}=S_{i-1}e^{(\mu-\frac{\sigma^{2}}{2})\delta+\sigma*\sqrt{\delta}*z}$"
#     deltarebal = r"$\delta_{rebal}$"
#     if CallOrPut == "Call":
#         phi = 1
#         BSformula = "$S\Phi(d_1) - Ke ^ {rT}\Phi(d_2)$ = "
#         Deltaformula = "$\Delta_t = \Phi(d_1(t,S_t))$"
#     elif CallOrPut == "Put":
#         phi = -1
#         sign = "-"
#         BSformula = "$K\Phi(-d_2)e^{rT}-S\Phi(-d_1) = $"
#         Deltaformula = "$\Delta_t = - \Phi(-d_1(t,S_t))$"
#
#
#     # User input is in %. We return to decimals.
#     # Careful for Transaction Costs. Supposed to be in basis points. 1 BASIS POINT = 0.01 %
#     Rf, mu, vol, TransactionCosts = Rf/100, mu/100, vol/100, TransactionCosts/100
#
#     # Discretization of maturity period. The matrix length depends on T and dt chosen by user.
#     t = np.arange(0,T+dt,dt)
#     nt = len(t)
#     a = range(nt)
#
#     # t_rebal is the rebalancing time.
#     # If rebalancing steps = 1, then dt_rebal = dt, and therefore t_rebal = t.
#     # If rebalancing steps > 1, then dt_rebal =/= dt, and therefore t_rebal =/= t.
#     # It will be used for the portfolio rebalancing, given that in the later condition, its timeline will be different
#     # than the stock's.
#     dt_rebal = dt * RebalancingSteps
#     t_rebal = np.arange(0, T+dt_rebal, dt_rebal)
#     # VS
#     # t_rebal is the rebalancing time. it will be incremented t_rebal += dt_rebal. Used for when dt =/= dt_rebal
#     # (ie when RebalancingSteps is different than 1)
#     # t_rebal = 0
#
#     CashAccount, EquityAccount, Delta, StockPrice, OptionIntrinsicValue, OptionPrice, BrownianMotion = np.zeros(nt), \
#                  np.zeros(nt), np.zeros(nt), np.zeros(nt), np.zeros(nt), np.zeros(nt), np.zeros(nt)
#     dW = np.sqrt(dt)*np.random.randn(nt-1) # Increments of Brownian Motion
#
#     # The first value, at t=0.
#     StockPrice[0] = S
#     OptionIntrinsicValue[0] = max(0, phi*(S - K))
#     OptionPrice[0] = p_bs(S, K, Rf, T,t[0], vol,phi)
#     BrownianMotion[0] = 0
#     Delta[0] = phi*CDFd1(S, K, Rf, T, t_rebal[0], vol, phi)     # putcall parity! -delta(-d1) = delta(d1) - 1
#     CashAccount[0] = OptionPrice[0] - Delta[0]*S - abs(Delta[0])*(Fixed*TransactionCosts + StockPrice[0]*Propor*TransactionCosts)
#     EquityAccount[0] = Delta[0]*S
#
#     # nt = len(np.arange(0,T+dt,dt)). range() is [1,nt[. 1 included, last of nt not included. This loop stops at maturity T.
#     for i in range(1,nt):
#         BrownianMotion[i] = BrownianMotion[i-1] + dW[i-1]
#         StockPrice[i] = StockPrice[0] * np.exp((mu - 0.5 * (vol * vol)) * t[i] + vol * BrownianMotion[i])
#         # VS
#         # z = np.random.randn(1)
#         # StockPrice[i] = StockPrice[i - 1] * np.exp((mu - 0.5 * (vol * vol)) * dt + vol * np.sqrt(dt) *z)
#
#         OptionIntrinsicValue[i] = max(0, phi*(StockPrice[i] - K))
#         OptionPrice[i] = p_bs(StockPrice[i], K, Rf, T, t[i], vol, phi)
#
#         # Portfolio is rebalanced every Rebalancing Step, so in order to recognize them we take the modulus of i, the
#         # discretization step, and if it is equal to zero then i is an rebalancing step:
#         if i % RebalancingSteps == 0:
#             # Before rebalancing : accrued interest on CashAccount & Updating EquityAccount to stock price evolution
#             CashAccount[i] = CashAccount[i - 1] * (1 + Rf * dt_rebal)
#             EquityAccount[i] = Delta[i-1]*StockPrice[i]
#
#             # After reblancing: computing delta (# of shares to hold at this time t), ensuring equivalence of portfolio
#             #                   and selling/buying shares to get delta and updating EquityAccount value with current Delta
#             Delta[i] = phi*CDFd1(StockPrice[i], K, Rf, T, t_rebal[int(i/RebalancingSteps)], vol, phi)
#             CashAccount[i] = CashAccount[i] + EquityAccount[i] - Delta[i]*StockPrice[i] - abs(Delta[i]-Delta[i-1])*(Fixed*TransactionCosts + StockPrice[i]*Propor*TransactionCosts)
#             EquityAccount[i] = Delta[i]*StockPrice[i]
#
#         else:
#             Delta[i] = Delta[i - 1]
#             CashAccount[i] = CashAccount[i - 1]
#             EquityAccount[i] = EquityAccount[i - 1]
#
#     #return (OptionPayoff[-1]-(CashAccount[-1] + EquityAccount[-1])
#
#     plt.ion()
#     plt.figure()
#     plt.suptitle(f"{CallOrPut} self-financing replication strategy")
#
#     plt.subplot(2, 2, 1)
#     plt.plot()
#     plt.title("Model and replication strategy description")
#     plt.xticks([])
#     plt.yticks([])
#     textstr = '\n'.join((
#         f"Black-Scholes-Merton model, with stock dynamics modeled with a geometric",
#         f"brownian motion of drift {mu*100}% and volatility {vol*100}%: {GBM}",
#         r"Its main assumptions are the absence of dividends, transactions costs, ",
#         "constant risk-free rate and volatility, and allowed fractions of shares.",
#         "",
#         f"To prove that the BSM is arbitrage-free, let's replicate the {CallOrPut.lower()} option payoff",
#         f"starting with only its BSM price: {BSformula} = {round(p_bs(S, K, Rf, T,0, vol,phi), 2)}.",
#         f"To do so, compute at each rebalancing step {deltarebal} = {dt_rebal}:  {Deltaformula} which",
#         "will tell the number of stock shares to hold at that moment in order to be",
#         "delta-hedged ,i.e. hedged against the changes in the underlying's stock price.",
#         "For example, $\Delta_0 = $" + str(round(phi*CDFd1(S, K, Rf, T, 0, vol, phi), 2)) + ", which means that at $t = 0$ we need to hold " + str(round(phi*CDFd1(S, K, Rf, T, 0, vol, phi), 2)) + " shares",
#         "to delta-hedge the option, i.e. neutralize the extent of the move in the",
#         "option's price relative to the underlying's asset price.",
#         "",
#         "Replication Strategy Error = Option payoff - Final Portfolio Value = " + str(round(OptionIntrinsicValue[-1]-(CashAccount[-1] + EquityAccount[-1]), 2)))) #+ ", Rebalance steps = " + str(RebalancingSteps)))
#     plt.text(-0.03, 0.95, textstr, verticalalignment='top')
#
#     plt.subplot(2, 2, 2)
#     plt.title(f"{CallOrPut} option replication strategy")
#     plt.plot(a, CashAccount[:], label="Cash account")
#     plt.plot(a, EquityAccount[:], label="Equity account")
#     plt.plot(a, EquityAccount[:] + CashAccount[:], label="Portfolio")
#     plt.ylabel("USD")
#     plt.legend()
#
#     plt.subplot(2, 2, 3)
#     plt.title("Held shares in the replication strategy")
#     plt.plot(a, Delta[:], label=f"{Deltaformula}")
#     plt.legend()
#     plt.xlabel(f"Discretized maturity period ($\delta=${dt})")
#     plt.ylabel("Held shares")
#
#     plt.subplot(2, 2, 4)
#     plt.title(f"{CallOrPut} option GBM simulation")
#     plt.plot(a, StockPrice[:], label="Stock price simulation (GBM)")
#     plt.axhline(y=K, ls="dashed", label=f"Strike = {int(K)}")
#     plt.plot(a, OptionIntrinsicValue[:], label=f"{CallOrPut} intrinsic value")
#     plt.plot(a, OptionPrice[:], label=f"{CallOrPut} option price")
#     plt.plot(a, EquityAccount[:] + CashAccount[:], label="Portfolio")
#     plt.xlabel(f"Discretized maturity period ($\delta=${dt})")
#     plt.ylabel("USD")
#     plt.legend()
#     plt.pause(0.002)
#     plt.show()
#
#
# def CDFd1(S, strike, Rf, T, t, vol, phi):
#     # At maturity t = T ----> so we have to take limits. Case t > T because of rounding errors sometimes it occurs.
#     if t >= T:
#         if phi == 1:
#             if S > strike:          # d1 = + infinity
#                 return 1            # cdf(+ infinity) = 1
#             elif S == strike:       # d1 = 0
#                 return 0.5          # cdf(0) = 0.5
#             elif S < strike:        # d1 = - infinity
#                 return 0            # cdf(- infinity) = 0
#         elif phi == -1:
#             if S > strike:          # d1 = + infinity
#                 return 0            # cdf(+ infinity) = 0
#             elif S == strike:       # d1 = 0
#                 return 0.5          # cdf(0) = 0.5
#             elif S < strike:        # d1 = - infinity
#                 return 1            # cdf(- infinity) = 1
#     else:
#         return norm.cdf( phi*( (np.log(S / strike) + (T - t) * (Rf + 0.5 * vol * vol)) / (vol * np.sqrt(T - t))  )   )
#
#
# def CDFd2(S, strike, Rf, T, t, vol, phi):
#     # idem
#     if t >= T:
#         if phi == 1:
#             if S > strike:          # d1 = + infinity
#                 return 1            # cdf(+ infinity) = 1
#             elif S == strike:       # d1 = 0
#                 return 0.5          # cdf(0) = 0.5
#             elif S < strike:        # d1 = - infinity
#                 return 0            # cdf(- infinity) = 0
#         elif phi == -1:
#             if S > strike:          # d1 = + infinity
#                 return 0            # cdf(+ infinity) = 0
#             elif S == strike:       # d1 = 0
#                 return 0.5          # cdf(0) = 0.5
#             elif S < strike:        # d1 = - infinity
#                 return 1            # cdf(- infinity) = 1
#     else:
#         return norm.cdf( phi*( (np.log(S / strike) + (T - t) * (Rf - 0.5 * vol * vol)) / (vol * np.sqrt(T - t))  )   )
#
# #RepStrat_EU_Option_BSM_GBM_V4("Put")
# #RepStrat_EU_Option_BSM_GBM_V4(100, 100, 1, 2, -15, 20, 0.0002, 1, 0.05, 0,0,"Put")
# # EU_Call_GBM_V3(S, strike, Rf, T, mu, vol, DiscretizationSteps, RebalancingSteps, TransactionCosts, Fixed, Propor):