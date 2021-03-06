# public imports
import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
# local imports
import update
import visualization


def visual_f_score(main_ticker, df, csv_list):
    """Visualizes the Piotroski F-Score of one main stock and it's specified peers with Matplotlib.
    Explanation of the Score: https://www.investopedia.com/terms/p/piotroski-score.asp
    main_ticker = ticker string from user input
    df = filtered dataframe containing all the stocks for comparison
    csv_list = list of all CSV filepaths being passed to update.csv()
    """
    
    ticker_in_df = (df.Code == main_ticker).any() # checks if the main stock is in the database
    fscore_in_df = df.loc[(df.Code == main_ticker),"F-Score"].notna().any() # checks if the main stock's F-Score is in the database

    if ticker_in_df and fscore_in_df:
        main_score = df.loc[(df.Code == main_ticker), "F-Score"]
        main_index = df[df.Code == main_ticker].index[0]
        df.drop(index=main_index, inplace=True) # The dataframe should only contain the stocks for comparison
        df.reset_index(drop=True, inplace=True)
    else:
        yf_ticker = yf.Ticker(main_ticker) # We need to scrape Yahoo! Finance if the stock is not in out database
        if yf_ticker.info["regularMarketPrice"] == None: # Unavailability of market price indicates that
            print("\n" + main_ticker + " is not listed on Yahoo! Finance.\n") # the stock ticker is not listed
            return visualization.visualize(1)
        main_score = f_score(main_ticker)
        if main_score == None: # Check if Yahoo! Finance provided enough information for F-Score calculation
            update.csv(main_ticker, csv_list, ticker_in_df) # Let's update our CSV
            print("\nYahoo! Finance does not provide this metric for " + main_ticker + "\n")
            return visualization.visualize(1)
        update.csv(main_ticker, csv_list, ticker_in_df) # Let's update our CSV
    
    # Save every ticker with it's corresponding F-Score in arrays
    arr = df.loc[df.loc[:,"F-Score"].notna(),["Code","F-Score"]].values
    tickers = arr[:,0]
    y = arr[:,1]
    # sort the tickers after F-Score for prettier plotting
    sorted_indices = y.argsort(kind="quicksort")
    y = y[sorted_indices]
    tickers = tickers[sorted_indices]
    # Save the number of tickers for axes setting
    length = tickers.size
    x = np.arange(length)

    # Prepare the plotting
    fig = plt.figure(figsize=(17, 10), dpi=80)
    ax = fig.add_subplot()
    ax.set(
        title = "Piotroski F-scores",
        ylim = [-0.5, 9.5],             # The score reaches from 0 to 9 (0.5 margin is prettier)
        yticks = np.arange(10),
        xlim = [-1, length],
        xticks = x,
        ylabel = "Scores", 
        xlabel = "Tickers"
    )
    ax.set_xticklabels(tickers, rotation="45", ha="right", rotation_mode="anchor")
    plt.tick_params(
        axis="x",           # changes apply to the x-axis
        which="both",       # both major and minor ticks are affected
        bottom=False,       # ticks along the bottom edge are off
        top=False,          # ticks along the top edge are off
        labelbottom=False)
    ax.set_axisbelow(True)  # move the plt.grid into the background
    plt.grid(axis="y")

    # Plot the mean and standard deviation of the comparison F-Scores
    mean = np.mean(y)
    std_top = np.full(length, mean + np.std(y))
    std_down = np.full(length, mean - np.std(y))
    ax.fill_between(x, std_top, std_down, alpha=0.3)
    plt.plot(x,np.full(length, mean),"b-")

    sc = ax.scatter(x, y, s=5, c="black", marker='o')   # Plot the comparison stocks 
    main_x = np.searchsorted(y, main_score)             # Find out where to place the main stock along the x axis
    ax.scatter(main_x, main_score, s=100, c="red", marker='o', edgecolors='black') # Plot the main stock

    # Annotate the main stock (always displayed)
    main_annot = ax.annotate(main_ticker, (main_x,main_score),
                        xytext=(-30,30),
                        textcoords="offset points",
                        bbox=dict(boxstyle="round", fc="w"),
                        arrowprops=dict(shrinkB=5, arrowstyle="->"))
    # Make the annotation prettier than the annotations of the comparison stocks
    main_annot.get_bbox_patch().set_facecolor("red")
    main_annot.get_bbox_patch().set_alpha(0.5)

    # Hide the annotations of the comparison stocks
    annot = ax.annotate("", xy=(0,0),
                        xytext=(-20,20),
                        textcoords="offset points",
                        bbox=dict(boxstyle="round", fc="w"),
                        arrowprops=dict(arrowstyle="->"))
    annot.set_visible(False)

    def update_annot(ind):
        """If the user's curser hovers over comparison data points, their annotation is updated/displayed.
        ind = list of indexes for all points under the curser
        """
        pos = sc.get_offsets()[ind["ind"][0]]                               # Get position of curser
        annot.xy = pos
        text = "{}".format(" ".join([tickers[n] for n in ind["ind"]]))      # The annotation content
        annot.set_text(text)
        annot.get_bbox_patch().set_alpha(0.4)                               # Make annotation prettier

    def hover(event):
        """If the user's curser hovers over comparison datapoints, 'update_annot()' is called.
        event = motion_notify_event (curser hovers over datapoint)
        """
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

    fig.canvas.mpl_connect("motion_notify_event", hover)                    # Enable hover -> show annotation
    plt.show()
    pass

def f_score(ticker):
    """Returns the scraped Piotroski F-Score of a yf.Ticker object.
    Explanation of the Score: https://www.investopedia.com/terms/p/piotroski-score.asp
    ticker = ticker string from user input
    """
    
    yf_ticker = yf.Ticker(ticker)
    try:
        # scrape Yahoo! Finance as few times as possible to minimize computation time
        financials = yf_ticker.financials
        cf = yf_ticker.cashflow
        balance = yf_ticker.balance_sheet
        
        # fill array with the fulfilled/unfulfilled F-Score criteria
        criteria = np.array([
            net_income(financials),
            roa(balance, financials),
            operating_cf(cf),
            cf_ni_ratio(cf, financials),
            ltd(balance),
            leverage(balance),
            no_dilution(cf),
            gross_margin(financials),
            atr(balance, financials)
        ], dtype=np.bool_)

        criteria_fulfilled = criteria[criteria == True] # Reduce the array to the fullfilled criteria
        return criteria_fulfilled.size
    
    except:
        return None

def net_income(financials_df):
    """Checks if the latest reported Net Income is positive.
    Explanation of Net Income: https://www.investopedia.com/terms/n/netincome.asp
    financials_df = Financial Statement of the specified company
    """
    
    net_income = financials_df.iloc[financials_df.index.get_loc("Net Income"),0]
    if (net_income > 0):
        return True
    else:
        return False

def roa(balance_df, financials_df):
    """Checks if the ROA (Return on Assets) is positive.
    Explanation of ROA: https://www.investopedia.com/terms/r/returnonassets.asp
    balance_df = Balance Sheet of the specified company
    financials_df = Financial Statement of the specified company
    """

    total_assets = balance_df.iloc[balance_df.index.get_loc("Total Assets"),0]
    net_income = financials_df.iloc[financials_df.index.get_loc("Net Income"),0]
    roa = net_income/total_assets
    if (roa > 0):
        return True
    else:
        return False

def operating_cf(cf_df):
    """Checks if the latest reported OCF (Cashflow) is positive.
    Explanation of OCF: https://www.investopedia.com/terms/o/operatingcashflow.asp
    cf_df = Cashflow Statement of the specified company
    """
    
    cf = cf_df.iloc[cf_df.index.get_loc("Total Cash From Operating Activities"),0]
    if (cf > 0):
        return True
    else:
        return False

def cf_ni_ratio(cf_df, financials_df):
    """Checks if the latest reported Operating CF (Cashflow) is larger than the latest reported NI (Net Income).
    cf_df = Cashflow Statement of the specified company
    financials_df = Financial Statement of the specified company
    """
    
    cf = cf_df.iloc[cf_df.index.get_loc("Total Cash From Operating Activities"),0]
    net_income = financials_df.iloc[financials_df.index.get_loc("Net Income"),0]
    if (cf > net_income):
        return True
    else:
        return False

def ltd(balance_df):
    """Checks if the current LTD (Long Term Debt) was reduced since previous year
    Explanation of LTD: https://www.investopedia.com/terms/l/longtermdebt.asp
    balance_df = Balance Sheet of the specified company
    """
    
    lt_debt_curr = balance_df.iloc[balance_df.index.get_loc("Long Term Debt"),0]
    lt_debt_prev = balance_df.iloc[balance_df.index.get_loc("Long Term Debt"),1]
    if (lt_debt_curr < lt_debt_prev):
        return True
    else:
        return False

def leverage(balance_df):
    """Checks if the leverage exposure was reduced since previous year
    Explanation of Leverage: https://www.investopedia.com/terms/l/leverage.asp
    balance_df = Balance Sheet of the specified company
    """
    
    # current year
    assets_curr = balance_df.iloc[balance_df.index.get_loc("Total Current Assets"),0]
    liab_curr = balance_df.iloc[balance_df.index.get_loc("Total Current Liabilities"),0]
    ratio_curr = assets_curr/liab_curr # Working Capital ratio from current year
    # previous year
    assets_prev = balance_df.iloc[balance_df.index.get_loc("Total Current Assets"),1]
    liab_prev = balance_df.iloc[balance_df.index.get_loc("Total Current Liabilities"),1]
    ratio_prev = assets_prev/liab_prev # Working Capital ratio from previous year
    if (ratio_curr > ratio_prev):
        return True
    else:
        return False

def no_dilution(cf_df):
    """Checks if the shares of investors were NOT diluted since previous year
    Explanation of Dilution: https://www.investopedia.com/terms/d/dilution.asp
    cf_df = Cashflow Statement of the specified company
    """

    try:
        issued_stock = cf_df.iloc[cf_df.index.get_loc("Issuance Of Stock"),0] # Earnings of the company through stock issuance
    except:
        issued_stock = 0
    try:
        repurchased_stock = cf_df.iloc[cf_df.index.get_loc("Repurchase Of Stock"),0] # Expenditures of the company through stock repurchases
    except:
        repurchased_stock = 0
    if (issued_stock + repurchased_stock <= 0):
        return True
    else:
        return False

def gross_margin(financials_df):
    """Checks if the gross margin grew since previous year
    Explanation of the Gross Margin: https://www.investopedia.com/terms/g/grossmargin.asp
    financials_df = Financial Statement of the specified company
    """

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
        return True
    else:
        return False

def atr(balance_df, financials_df):
    """Checks ATR (Asset Turnover Ratio) grew since previous year
    Explanation of ATR: https://www.investopedia.com/terms/a/assetturnover.asp
    balance_df = Balance Sheet of the specified company
    financials_df = Financial Statement of the specified company
    """
    
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
        return True
    else:
        return False
