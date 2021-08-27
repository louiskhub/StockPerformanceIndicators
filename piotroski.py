# public imports
import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
# local imports
import errors
import update

def visual_f_score(ticker_input, df, csv_list):
    """Visualizes the Piotroski F-Score.
    Explanation of the Piotroski F-Score: 
    """

    main_ticker = str(ticker_input)
    
    ticker_in_df = (df.Code == main_ticker).any()
    fscore_in_df = df.loc[(df.Code == main_ticker),"F-Score"].notna().any()

    if ticker_in_df and fscore_in_df:
        main_score = df.loc[(df.Code == main_ticker), "F-Score"]
        main_index = df[df["Code"] == main_ticker].index.item()
        df = df.drop(index=main_index)
    else:
        yf_ticker = yf.Ticker(main_ticker)
        if yf_ticker.info["regularMarketPrice"] == None:
            raise errors.TickerError(main_ticker)
        main_score = f_score(main_ticker)
        if main_score == None:
            raise errors.MetricError(main_ticker)
        update.csv(main_ticker, csv_list, ticker_in_df)
    
    arr = df.loc[df.loc[:,"F-Score"].notna(),["Code","F-Score"]].values
    tickers = arr[:,0]
    y = arr[:,1]
    sorted_indices = y.argsort(kind="quicksort")
    y = y[sorted_indices]
    tickers = tickers[sorted_indices]
    length = tickers.size
    x = np.arange(length)

    fig = plt.figure(figsize=(17, 10), dpi=80)
    ax = fig.add_subplot()

    ax.set(
        title = "Piotroski F-scores",
        ylim = [-0.5, 9.5],
        yticks = np.arange(10),
        xlim = [-1, x.size],
        xticks = x,
        ylabel = "Scores", 
        xlabel = "Tickers"
    )
    ax.set_xticklabels(tickers, rotation="45", ha="right", rotation_mode="anchor")
    plt.tick_params(
        axis="x",          # changes apply to the x-axis
        which="both",      # both major and minor ticks are affected
        bottom=False,      # ticks along the bottom edge are off
        top=False,         # ticks along the top edge are off
        labelbottom=False)
    ax.set_axisbelow(True) # move the plt.grid into the background
    plt.grid(axis="y")

    mean = np.mean(y)
    std_top = np.full(length, mean + np.std(y))
    std_down = np.full(length, mean - np.std(y))
    ax.fill_between(x, std_top, std_down, alpha=0.3)
    plt.plot(x,np.full(length, mean),"b-")

    sc = ax.scatter(x, y, s=20, c="black", marker='o')
    main_x = np.searchsorted(y, main_score)
    ax.scatter(main_x, main_score, s=100, c="red", marker='o', edgecolors='black')

    main_annot = ax.annotate(main_ticker, (main_x,main_score),
                        xytext=(-30,30),
                        textcoords="offset points",
                        bbox=dict(boxstyle="round", fc="w"),
                        arrowprops=dict(shrinkB=5, arrowstyle="->"))
    main_annot.get_bbox_patch().set_facecolor("red")
    main_annot.get_bbox_patch().set_alpha(0.5)
    annot = ax.annotate("", xy=(0,0),
                        xytext=(-20,20),
                        textcoords="offset points",
                        bbox=dict(boxstyle="round", fc="w"),
                        arrowprops=dict(arrowstyle="->"))
    annot.set_visible(False)

    def update_annot(ind):
        pos = sc.get_offsets()[ind["ind"][0]]
        annot.xy = pos
        text = "{}".format(" ".join([tickers[n] for n in ind["ind"]]))
        annot.set_text(text)
        annot.get_bbox_patch().set_alpha(0.4)

    def hover(event):
        vis = annot.get_visible()
        if event.inaxes == ax:
            cont, ind = sc.contains(event)
            if cont:
                update_annot(ind)
                annot.set_visible(True)
                fig.canvas.draw_idle()
            else:
                if vis:
                    annot.set_visible(False)
                    fig.canvas.draw_idle()

    fig.canvas.mpl_connect("motion_notify_event", hover)

    plt.show()



def f_score(ticker):
    """Returns the Piotroski F-Score of a yf.Ticker object.
    Explanation of the Score: https://www.investopedia.com/terms/p/piotroski-score.asp
    """
    ticker = yf.Ticker(ticker)
    try:
        financials = ticker.financials
        cf = ticker.cashflow
        balance = ticker.balance_sheet

        criteria = np.array([
            net_income(financials),
            roa(balance, financials),
            operating_cf(cf),
            cf_ni_ratio(cf, financials),
            ltd(balance),
            leverage(balance),
            dilution(cf),
            gross_margin(financials),
            atr(balance, financials)
        ], dtype=np.bool_)

        criteria_fulfilled = criteria[criteria == 1]
        return criteria_fulfilled.size
    
    except:
        return None



def net_income(financials_df):
    """Checks if the latest reported Net Income is positive."""
    
    net_income = financials_df.iloc[financials_df.index.get_loc("Net Income"),0]
    if (net_income > 0):
        return 1
    else:
        return 0

def roa(balance_df, financials_df):
    """Checks if the ROA (Return on Assets) is positive."""

    total_assets = balance_df.iloc[balance_df.index.get_loc("Total Assets"),0]
    net_income = financials_df.iloc[financials_df.index.get_loc("Net Income"),0]
    roa = net_income/total_assets
    if (roa > 0):
        return 1
    else:
        return 0

def operating_cf(cf_df):
    """Checks if the latest reported Operating CF (Cashflow) is positive."""
    
    cf = cf_df.iloc[cf_df.index.get_loc("Total Cash From Operating Activities"),0]
    if (cf > 0):
        return 1
    else:
        return 0

def cf_ni_ratio(cf_df, financials_df):
    """Checks if the latest reported Operating CF (Cashflow) is larger than the latest reported NI (Net Income)."""
    
    cf = cf_df.iloc[cf_df.index.get_loc("Total Cash From Operating Activities"),0]
    net_income = financials_df.iloc[financials_df.index.get_loc("Net Income"),0]
    if (cf > net_income):
        return 1
    else:
        return 0

def ltd(balance_df):
    """Checks if the current LTD (Long Term Debt) was reduced since previous year"""
    
    lt_debt_curr = balance_df.iloc[balance_df.index.get_loc("Long Term Debt"),0]
    lt_debt_prev = balance_df.iloc[balance_df.index.get_loc("Long Term Debt"),1]
    if (lt_debt_curr < lt_debt_prev):
        return 1
    else:
        return 0

def leverage(balance_df):
    """Checks if the leverage exposure was reduced since previous year"""
    
    # current year
    assets_curr = balance_df.iloc[balance_df.index.get_loc("Total Current Assets"),0]
    liab_curr = balance_df.iloc[balance_df.index.get_loc("Total Current Liabilities"),0]
    ratio_curr = assets_curr/liab_curr # Working Capital ratio from current year
    # previous year
    assets_prev = balance_df.iloc[balance_df.index.get_loc("Total Current Assets"),1]
    liab_prev = balance_df.iloc[balance_df.index.get_loc("Total Current Liabilities"),1]
    ratio_prev = assets_prev/liab_prev # Working Capital ratio from previous year
    if (ratio_curr > ratio_prev):
        return 1
    else:
        return 0

def dilution(balance_df):
    """Checks if the shares of investors were NOT diluted since previous year"""

    issued_stock = balance_df.iloc[balance_df.index.get_loc("Issuance Of Stock"),0] # Earnings of the company through stock issuance
    try:
        repurchased_stock = balance_df.iloc[balance_df.index.get_loc("Repurchase Of Stock"),0] # Expenditures of the company through stock repurchases
    except:
        repurchased_stock = 0
    if (issued_stock + repurchased_stock <= 0):
        return 1
    else:
        return 0

def gross_margin(financials_df):
    """Checks if the gross margin grew since previous year"""

    # Net Sales (= Revenue)
    net_sales_curr = financials_df.iloc[financials_df.index.get_loc("Total Revenue"),0]
    net_sales_prev = financials_df.iloc[financials_df.index.get_loc("Total Revenue"),1]
    # COGS (= Cost of Goods Sold)
    cogs_curr = financials_df.iloc[financials_df.index.get_loc("Cost Of Revenue"),0] # No data available for COGS: Cost of Revenue is a similiar metric
    cogs_prev = financials_df.iloc[financials_df.index.get_loc("Cost Of Revenue"),1] # No data available for COGS: Cost of Revenue is a similiar metric
    # Gross Margins
    gross_margin_curr = net_sales_curr - cogs_curr
    gross_margin_prev = net_sales_prev - cogs_prev
    if (gross_margin_curr > gross_margin_prev):
        return 1
    else:
        return 0

def atr(balance_df, financials_df):
    """Checks ATR (Asset Turnover Ratio) grew since previous year"""
    
    # Net Sales (= Revenue)
    net_sales_curr = financials_df.iloc[financials_df.index.get_loc("Total Revenue"),0]
    net_sales_prev = financials_df.iloc[financials_df.index.get_loc("Total Revenue"),1]
    # Asset inventory change (previous period)
    beginning_assets_curr = balance_df.iloc[balance_df.index.get_loc("Total Assets"),1]
    ending_assets_curr = balance_df.iloc[balance_df.index.get_loc("Total Assets"),0]
    # Asset inventory change (period before previous period)
    beginning_assets_prev = balance_df.iloc[balance_df.index.get_loc("Total Assets"),2]
    ending_assets_prev = balance_df.iloc[balance_df.index.get_loc("Total Assets"),1]
    # Asset Turnover Ratios
    atr_curr = net_sales_curr / ((beginning_assets_curr + ending_assets_curr)/2)
    atr_prev = net_sales_prev / ((beginning_assets_prev + ending_assets_prev)/2)
    if (atr_curr > atr_prev):
        return 1
    else:
        return 0
