# public imports
import yfinance as yf
import pandas as pd
import numpy as np
import concurrent.futures
# local imports
import piotroski
import peg


def scrape_data(args):
    """Returns several stock PI's scraped from Yahoo! Finance.
    args = 2D-array containing stock tickers, counters and length of the ticker-list
    """

    ticker = args[0].strip() # make sure the ticker does not contain whitespace
    
    score = piotroski.f_score(ticker)
    ratio = peg.ratio(ticker)

    # get all useful stock information
    info = yf.Ticker(ticker).info # save the info-dict in a variable to minimize computation time
    try:
        industry = info['industry']
    except:
        industry = None # Make sure that cells in the csv without data are really empty 
    try:
        sector = info['sector']
    except:
        sector = None
    try:
        priceToBook = info['priceToBook']
    except:
        priceToBook = None
    try:
        marketCap = info['marketCap']
    except:
        marketCap = None
    try:
        fiftyDayAverage = info['fiftyDayAverage']
    except:
        fiftyDayAverage = None
    try:
        twoHundredAverage = info['twoHundredDayAverage']
    except:
        twoHundredAverage = None
    try:
        profitMargin = info['profitMargins']
    except:
        profitMargin = None
    try:
        grossMargin = info['grossMargins']
    except:
        grossMargin = None

    print(str(args[1]) + " / " + str(args[2])) # print the counter
    return score, ratio, industry, sector, priceToBook, marketCap, fiftyDayAverage, twoHundredAverage, profitMargin, grossMargin

def data_into_csv():
    """Fills Ticker-CSV with the scraped stock information and PI's.
    """
    
    # get user inputs
    print("\n")
    csv_input = input("Enter the CSV file you want to modify: ").strip()
    if csv_input == "break":
        return "break"
    print("\n")
    col_input = (input("Enter the implicit Index of the CSV-Column containing Stock-Tickers: ").strip())
    # important for generalization (not every CSV has the stock tickers in the same column)
    if col_input == "break":
        return "break"
    col_input = int(col_input)
    print("\n\n")

    # Catch input-errors
    try:
        csv = pd.read_csv(csv_input, index_col=0)
    except:
        return "The filename '" + csv_input + "' does not exist.\n\n\n\n"
    try:
        csv_tickers = csv.iloc[:,col_input-1]
        csv = csv.rename({csv.columns[col_input-1]: 'Code'}, axis='columns') # rename ticker-column for generalization
        csv_tickers = csv_tickers.values # stock ticker array
    except:
        return "The Column does not contain Stock-Symbols.\n\n\n\n"

    # counter for user to estimate runtime (array needed for executor.map)
    counter_array = np.arange(csv_tickers.size)
    df_size = np.full(csv_tickers.size, csv_tickers.size-1)
    # wrap the arrays to one argument for executor.map
    args = np.column_stack((csv_tickers, counter_array, df_size))

    
    with concurrent.futures.ThreadPoolExecutor() as executor: # use ThreadPool for faster webscraping
        
        results = executor.map(scrape_data, args)   # scrape all stock info

        # create array for every stock info
        scores = np.empty(0, dtype=np.ubyte)        # piotroski F-scores with values 0-9
        peg_ratios = np.empty(0)                    # PEG ratios
        industries = np.empty(0, dtype=np.str_)     # Industries
        sectors = np.empty(0, dtype=np.str_)        # Sectors
        ptbs = np.empty(0)                          # pricesToBooks
        mcaps = np.empty(0)                         # marketCaps
        fiftyDayAvrgs = np.empty(0)                 # fiftyDayAverages
        twoHundredAvrgs = np.empty(0)               # twoHundredAverages
        profitMargins = np.empty(0)                 # profitMargins
        grossMargins = np.empty(0)                  # grossMargins

        # fill arrays
        for result in results:
            scores = np.append(scores, result[0])
            peg_ratios = np.append(peg_ratios, result[1])
            industries = np.append(industries, result[2])
            sectors = np.append(sectors, result[3])
            ptbs = np.append(ptbs, result[4])
            mcaps = np.append(mcaps, result[5])
            fiftyDayAvrgs = np.append(fiftyDayAvrgs, result[6])
            twoHundredAvrgs = np.append(twoHundredAvrgs, result[7])
            profitMargins = np.append(profitMargins, result[8])
            grossMargins = np.append(grossMargins, result[9])

    # fill dataframe columns
    csv['F-Score'] = scores
    csv['PEG-Ratio'] = peg_ratios
    csv['Industry'] = industries
    csv['Sector'] = sectors
    csv['Price to Book'] = ptbs
    csv['Market Cap'] = mcaps
    csv['50 Day Av'] = fiftyDayAvrgs
    csv['200 Day Av'] = twoHundredAvrgs
    csv['Profit Margin'] = profitMargins
    csv['Gross Margin'] = grossMargins
    csv.to_csv(csv_input) # save in csv

    return "\n\n'" + csv_input + "' successfully filled!\n"