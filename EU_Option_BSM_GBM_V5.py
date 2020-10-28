#####################################################################################
# European Options
# Geometric Brownian Motion
### SOURCES:
## SLIDES Credit and Interest Rate Risk: sl. 27 & 30
## SDE Simulation: BSM.R file from Prof. Vrins
#####################################################################################

import numpy as np
from scipy.stats import norm
# import pandas as pd


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


def RepStrat_EU_Option_BSM_GBM_V5(CallOrPut, S,K,Rf,T,mu,vol,dt,RebalancingSteps, TransactionCosts, FixedOrPropor, seed):

    # In case of error in input: return nothing
    arguments = [CallOrPut, S,K,Rf,T,mu,vol,dt,RebalancingSteps, FixedOrPropor, seed] #TC skipped bc can just assume its 0
    for arg in arguments:
        if arg == None:
            return [0], [0], [0], [0], [0], [0], [0], [0], [0], [0], [0], [0], [0], [0], [0], [0], [0], [0]

    if  S < 0 or K < 0 or dt <= 0 or RebalancingSteps < 1 or RebalancingSteps > T/dt:
        return [0], [0], [0], [0], [0], [0], [0], [0], [0], [0], [0], [0], [0], [0], [0], [0], [0], [0]
        #dt, K, discre_matu, StockPrice, OptionIntrinsicValue, OptionPrice, EquityAccount, CashAccount, Portfolio, V_t, f_t, f_x, f_xx
    if TransactionCosts == None:
        TransactionCosts = 0


    ####################################################################################################################
    #####################  START derivative/model strings specifics, user input transformation,    #####################
    #####################        discretization of continuous [0,T] period and rebalancing period  #####################
    #####################        computation

    ####### derivative specifics

    if CallOrPut == "Call":
        phi = 1
    elif CallOrPut == "Put":
        phi = -1

    Fixed, Propor = 0, 0
    if FixedOrPropor == "NTC" or FixedOrPropor == []:
        Fixed, Propor = 0, 0

    elif FixedOrPropor == "FTC":
        Fixed, Propor = 1, 0
        TransactionCosts = TransactionCosts

    elif FixedOrPropor == "PTC":
        Fixed, Propor = 0, 1 
        TransactionCosts = TransactionCosts / 100

    # Seed is always fixed. 
    np.random.seed(1)
    # unless user wants new seed everytime
    if seed == ["seed"]:
        np.random.seed(np.random.randint(low=2, high=50000))
    


    ####### Discretization of maturity period
    # The matrix length depends on T and dt chosen by user.
    
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

    cash_bfr, cash_aft, equi_bfr, equi_aft = np.zeros(nt), np.zeros(nt), np.zeros(nt), np.zeros(nt)
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

    f_xx[0] = Gamma(StockPrice[0], K, Rf, T, t_rebal[0], vol)
    f_t[0] = Theta(StockPrice[0], K, Rf, T, t_rebal[0], vol, phi)
    V_t[0] = OptionPrice[0]

    cash_bfr[0], cash_aft[0], equi_bfr[0], equi_aft[0] = OptionPrice[0], CashAccount[0], 0, EquityAccount[0]

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

            cash_bfr[i], equi_bfr[i] = CashAccount[i], EquityAccount[i]

            ####### After reblancing
            # computing delta (# of shares to hold at this time t), ensuring equivalence of portfolio and selling/buying
            # shares to get delta and updating EquityAccount value with current Delta
            f_x[i] = Delta(StockPrice[i], K, Rf, T, t_rebal[int(i/RebalancingSteps)], vol, phi)
            CashAccount[i] = CashAccount[i] + EquityAccount[i] - f_x[i] * StockPrice[i] - abs(f_x[i] - f_x[i - 1]) * (Fixed * TransactionCosts + StockPrice[i] * Propor * TransactionCosts)
            EquityAccount[i] = f_x[i] * StockPrice[i]

            cash_aft[i], equi_aft[i] = CashAccount[i], EquityAccount[i]


            f_xx[i] = Gamma(StockPrice[i], K, Rf, T, t_rebal[int(i / RebalancingSteps)], vol)
            f_t[i] = Theta(StockPrice[i], K, Rf, T, t_rebal[int(i / RebalancingSteps)], vol, phi)
            V_t[i] = V_t[i - 1] + (f_t[i - 1] + mu * StockPrice[i - 1] * f_x[i - 1] + 0.5 * (vol * vol) * (StockPrice[i - 1] * StockPrice[i - 1]) * f_xx[i - 1]) * dt_rebal + vol * StockPrice[i - 1] * f_x[i - 1] * dW[i - 1]

        # not a rebalancing step
        else:
            f_x[i] = f_x[i - 1]
            CashAccount[i] = CashAccount[i - 1]
            EquityAccount[i] = EquityAccount[i - 1]

            f_xx[i] = f_xx[i - 1]
            f_t[i] = f_t[i - 1]
            V_t[i] = V_t[i - 1]

            cash_bfr[i], cash_aft[i], equi_bfr[i], equi_aft[i] = cash_bfr[i-1], cash_aft[i-1], equi_bfr[i-1], equi_aft[i-1]
    #####################                  END replication strategy                                #####################
    ####################################################################################################################

    # df = pd.DataFrame({"Stock price":StockPrice, "Option intrinsic value":OptionIntrinsicValue, "Option price":OptionPrice,
    #                            "Delta":f_x, "Cash before":cash_bfr, "Equity before":equi_bfr, "Portfolio before":cash_bfr+equi_bfr,
    #                            "Cash after":cash_aft, "Equity after":equi_aft, "Portfolio after":cash_aft+equi_aft, "Replication strategy error":OptionPrice-cash_aft-equi_aft},
    #                      index=t)

    ####################################################################################################################
    #####################                  START graphics                                          #####################


    return dt, K, a, StockPrice, OptionIntrinsicValue, OptionPrice, EquityAccount, CashAccount, EquityAccount+CashAccount, V_t, f_t, f_x, f_xx, cash_bfr, cash_aft, equi_bfr, equi_aft, t






# #####################################################################################
# # European Options
# # Geometric Brownian Motion
# ### SOURCES:
# ## SLIDES Credit and Interest Rate Risk: sl. 27 & 30
# ## SDE Simulation: BSM.R file from Prof. Vrins
# #####################################################################################

# import numpy as np
# from scipy.stats import norm


# def d1(S, strike, Rf, T, t, vol):
#     if t<T:
#         return (np.log(S / strike) + (T - t) * (Rf + 0.5 * vol * vol)) / (vol * np.sqrt(T - t))
#     else:
#         if S > strike:     # d1 = + infinity
#             return 10E9
#         elif S == strike:  # d1 = 0
#             return 0
#         elif S < strike:   # d1 = - infinity
#             return -10E9

# def d2(S, strike, Rf, T, t, vol):
#     if t<T:
#         return (np.log(S / strike) + (T - t) * (Rf - 0.5 * vol * vol)) / (vol * np.sqrt(T - t))
#     else:
#         if S > strike:     # d1 = + infinity
#             return 10E9
#         elif S == strike:  # d1 = 0
#             return 0
#         elif S < strike:   # d1 = - infinity
#             return -10E9


# def p_bs(S, strike, Rf, T, t, vol, phi):
#     return phi*(S*norm.cdf(phi * d1(S, strike, Rf, T, t, vol)) - strike * np.exp(-Rf*(T-t)) * norm.cdf( phi*d2(S, strike, Rf, T, t, vol)))


# def Delta(S, K, Rf, T, t, vol, phi):
#     return  phi*norm.cdf(phi*d1(S, K, Rf, T, t, vol))


# def Gamma(S, K, Rf, T, t, vol):
#     return (norm.pdf(d1(S, K, Rf, T, t, vol)))/(S*vol*np.sqrt(T-t))


# def Theta(S, K, Rf, T, t, vol, phi):
#     return ( phi*(-Rf*K*np.exp(-Rf*(T-t))*norm.cdf(phi*d2(S, K, Rf, T, t, vol)))   -  ((S*vol*norm.pdf(d1(S, K, Rf, T, t, vol)))/(2*np.sqrt(T-t)))  )


# def RepStrat_EU_Option_BSM_GBM_V5(CallOrPut, S,K,Rf,T,mu,vol,dt,RebalancingSteps, TransactionCosts, FixedOrPropor, sde_simulation):

#     ####################################################################################################################
#     #####################  START derivative/model strings specifics, user input transformation,    #####################
#     #####################        discretization of continuous [0,T] period and rebalancing period  #####################
#     #####################        computation

#     ####### derivative/model strings specifics
    
#     phi= 0
#     #, 0, 0, r"$S_{i}=S_{i-1}e^{(\mu-\frac{\sigma^{2}}{2})\delta+\sigma*\sqrt{\delta}*z}$"
#     # deltarebal = r"$\delta_{rebal}$"
#     if CallOrPut == "Call":
#         phi = 1
#         # BSformula = "$S\Phi(d_1) - Ke ^ {rT}\Phi(d_2)$ = "
#         # Deltaformula = "$\Delta_t = \Phi(d_1(t,S_t))$"
#     elif CallOrPut == "Put":
#         phi = -1
#         # sign = "-"
#         # BSformula = "$K\Phi(-d_2)e^{rT}-S\Phi(-d_1) = $"
#         # Deltaformula = "$\Delta_t = - \Phi(-d_1(t,S_t))$"

#     if FixedOrPropor == ["FTC"]:
#         Fixed, Propor = 1, 0
#     elif FixedOrPropor == ["PTC"]:
#         Propor, Fixed = 1, 0 
#     elif FixedOrPropor ==[]:
#         Fixed, Propor = 0, 0
#     elif FixedOrPropor == ["FTC", "PTC"] or FixedOrPropor == ["PTC", "FTC"]:
#         Fixed, Propor = 1, 1

#     if TransactionCosts == None:
#         TransactionCosts = 0

#     if sde_simulation == ["seed"]:
#         np.random.seed(1)



#     #######  user input transformation
#     # Careful for Transaction Costs. Supposed to be in basis points. 1 BASIS POINT = 0.01 %
#     Rf, mu, vol, TransactionCosts = Rf, mu, vol, TransactionCosts / 100

#     ####### Discretization of maturity period
#     # The matrix length depends on T and dt chosen by user.

#     if dt == 0:
#         dt = 0.01

#     t = np.arange(0, T + dt, dt)
#     nt = len(t)
#     a = range(nt)

#     ####### Rebalancing period computation
#     # t_rebal is the rebalancing time.
#     # If rebalancing steps = 1, then dt_rebal = dt, and therefore t_rebal = t.
#     # If rebalancing steps > 1, then dt_rebal =/= dt, and therefore t_rebal =/= t.
#     # It will be used for the portfolio rebalancing, given that in the later condition, its timeline will be different
#     # than the stock's.
#     dt_rebal = dt * RebalancingSteps
#     t_rebal = np.arange(0, T + dt_rebal, dt_rebal)
#     #####################    END derivative/model strings specifics, user input transformation,    #####################
#     #####################        discretization of continuous [0,T] period and rebalancing period  #####################
#     #####################        computation

#     ####################################################################################################################
#     #####################                  START accounts initialization                           #####################
#     f_xx, f_t, f_x, V_t, CashAccount, EquityAccount, StockPrice, OptionIntrinsicValue, OptionPrice, BrownianMotion = \
#         np.zeros(nt), np.zeros(nt), np.zeros(nt), np.zeros(nt), np.zeros(nt), np.zeros(nt), np.zeros(nt), np.zeros(nt),\
#         np.zeros(nt), np.zeros(nt)
#     dW = np.sqrt(dt) * np.random.randn(nt - 1)  # Increments of Brownian Motion
#     #####################                      END accounts initialization                         #####################
#     ####################################################################################################################

#     ####################################################################################################################
#     #####################                  START replication strategy                              #####################
#     ####### t = 0.
#     StockPrice[0] = S
#     OptionIntrinsicValue[0] = max(0, phi * (S - K))
#     OptionPrice[0] = p_bs(S, K, Rf, T, t[0], vol, phi)
#     BrownianMotion[0] = 0
#     f_x[0] = Delta(StockPrice[0], K, Rf, T, t_rebal[0], vol, phi)  # putcall parity! -delta(-d1) = delta(d1) - 1
#     CashAccount[0] = OptionPrice[0] - f_x[0] * S - abs(f_x[0]) * (Fixed * TransactionCosts + StockPrice[0] * Propor * TransactionCosts)
#     EquityAccount[0] = f_x[0] * S

#     f_xx[0] = Gamma(StockPrice[0], K, Rf, T, t_rebal[0], vol)
#     f_t[0] = Theta(StockPrice[0], K, Rf, T, t_rebal[0], vol, phi)
#     V_t[0] = OptionPrice[0]

#     #######  0 < t <= T
#     # Reminder : nt = len(np.arange(0,T+dt,dt))
#     #           function range() is [1,nt[. 1 included, last of nt not included.
#     #           This loop stops at maturity T.
#     for i in range(1, nt):
#         ####### Stock price simulation
#         BrownianMotion[i] = BrownianMotion[i - 1] + dW[i - 1]
#         StockPrice[i] = StockPrice[0] * np.exp((mu - 0.5 * (vol * vol)) * t[i] + vol * BrownianMotion[i])

#         ####### Option intrinsic value & price
#         OptionIntrinsicValue[i] = max(0, phi * (StockPrice[i] - K))
#         OptionPrice[i] = p_bs(StockPrice[i], K, Rf, T, t[i], vol, phi)

#         ####### Replication strategy
#         # Portfolio is rebalanced every Rebalancing Step, so in order to recognize them we take the modulus of i, the
#         # discretization step, and if it is equal to zero then i is an rebalancing step:
#         if i % RebalancingSteps == 0:
#             ####### Before rebalancing
#             # accrued interest on CashAccount & Updating EquityAccount to stock price evolution
#             CashAccount[i] = CashAccount[i - 1] * (1 + Rf * dt_rebal)
#             EquityAccount[i] = f_x[i - 1] * StockPrice[i]

#             ####### After reblancing
#             # computing delta (# of shares to hold at this time t), ensuring equivalence of portfolio and selling/buying
#             # shares to get delta and updating EquityAccount value with current Delta
#             f_x[i] = Delta(StockPrice[i], K, Rf, T, t_rebal[int(i/RebalancingSteps)], vol, phi)
#             CashAccount[i] = CashAccount[i] + EquityAccount[i] - f_x[i] * StockPrice[i] - abs(f_x[i] - f_x[i - 1]) * (Fixed * TransactionCosts + StockPrice[i] * Propor * TransactionCosts)
#             EquityAccount[i] = f_x[i] * StockPrice[i]


#             f_xx[i] = Gamma(StockPrice[i], K, Rf, T, t_rebal[int(i / RebalancingSteps)], vol)
#             f_t[i] = Theta(StockPrice[i], K, Rf, T, t_rebal[int(i / RebalancingSteps)], vol, phi)
#             V_t[i] = V_t[i - 1] + (f_t[i - 1] + mu * StockPrice[i - 1] * f_x[i - 1] + 0.5 * (vol * vol) * (StockPrice[i - 1] * StockPrice[i - 1]) * f_xx[i - 1]) * dt_rebal + vol * StockPrice[i - 1] * f_x[i - 1] * dW[i - 1]

#         # not a rebalancing step
#         else:
#             f_x[i] = f_x[i - 1]
#             CashAccount[i] = CashAccount[i - 1]
#             EquityAccount[i] = EquityAccount[i - 1]

#             f_xx[i] = f_xx[i - 1]
#             f_t[i] = f_t[i - 1]
#             V_t[i] = V_t[i - 1]
#     #####################                  END replication strategy                                #####################
#     ####################################################################################################################

#     ####################################################################################################################
#     #####################                  START graphics                                          #####################


#     return dt, K, a, StockPrice, OptionIntrinsicValue, OptionPrice, EquityAccount, CashAccount, EquityAccount+CashAccount, V_t, f_t, f_x, f_xx



