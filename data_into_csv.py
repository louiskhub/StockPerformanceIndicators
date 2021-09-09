# public imports
import yfinance as yf
import pandas as pd
import numpy as np
import concurrent.futures
# local imports
import piotroski
import peg



def scrape_data(args):
    
    ticker = str(args[0]).strip()
    score = piotroski.f_score(ticker)
    ratio = peg.ratio(ticker)
    info = yf.Ticker(ticker).info

    try:
        industry = info['industry']
    except:
        industry = None
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

    print(str(args[1]) + " / " + str(args[2]))
    return score, ratio, industry, sector, priceToBook, marketCap, fiftyDayAverage, twoHundredAverage, profitMargin, grossMargin


def data_into_csv():
    
    print("\n")
    csv_input = str(input("Enter the CSV file you want to modify: ")).strip()
    if csv_input == "break":
        return "break"
    print("\n")
    col_input = (input("Enter the implicit Index of the CSV-Column containing Stock-Tickers: ").strip())
    if col_input == "break":
        return "break"
    col_input = int(col_input)
    print("\n\n")

    try:
        csv = pd.read_csv(csv_input, index_col=0)
    except:
        return "The filename '" + csv_input + "' does not exist.\n\n\n\n"
    
    try:
        csv_tickers = csv.iloc[:,col_input-1]
        csv = csv.rename({csv.columns[col_input-1]: 'Code'}, axis='columns')
        csv_tickers = csv_tickers.values
    except:
        return "The Column does not contain Stock-Symbols.\n\n\n\n"

    counter_array = np.arange(csv_tickers.size)
    df_size = np.full(csv_tickers.size, csv_tickers.size-1)
    args = np.column_stack((csv_tickers, counter_array, df_size))

    with concurrent.futures.ThreadPoolExecutor() as executor:
        
        results = executor.map(scrape_data, args)

        scores = np.empty(0, dtype=np.ubyte)        #piotroski F-scores
        peg_ratios = np.empty(0)                    #pegRatios
        industries = np.empty(0, dtype=np.str_)     #industries
        sectors = np.empty(0, dtype=np.str_)        #sectors
        ptbs = np.empty(0)                          #pricesToBooks
        mcaps = np.empty(0)                         #marketCaps
        fiftyDayAvrgs = np.empty(0)                 #fiftyDayAverages
        twoHundredAvrgs = np.empty(0)               #twoHundredAverages
        profitMargins = np.empty(0)                 #profitMargins
        grossMargins = np.empty(0)                  #grossMargins

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
    csv.to_csv(csv_input)

    return "\n\n'" + csv_input + "' successfully filled!\n"


# BOILERPLATE
if __name__ == "__main__":
    print(data_into_csv())