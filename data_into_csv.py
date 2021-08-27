# public imports
import yfinance as yf
import pandas as pd
import numpy as np
import concurrent.futures
# local imports
import piotroski
import peg




def scrape_data(args):
    
    ticker = str(args[0])
    score = piotroski.f_score(ticker)
    ratio = peg.ratio(ticker)
    info = ticker.info

    try:
        industry = info['industry']
        if industry == "nan":
            industry = np.nan
    except:
        industry = np.nan
    try:
        sector = info['sector']
        if sector == "nan":
            sector = np.nan
    except:
        sector = np.nan
    try:
        country = info['country']
    except:
        country = np.nan
    try:
        priceToBook = info['priceToBook']
    except:
        priceToBook = np.nan
    try:
        marketCap = info['marketCap']
    except:
        marketCap = np.nan
    try:
        fiftyDayAverage = info['fiftyDayAverage']
    except:
        fiftyDayAverage = np.nan
    try:
        twoHundredAverage = info['twoHundredDayAverage']
    except:
        twoHundredAverage = np.nan
    try:
        profitMargin = info['profitMargins']
    except:
        profitMargin = np.nan
    try:
        grossMargin = info['grossMargins']
    except:
        grossMargin = np.nan

    print(str(args[1]) + " / " + str(args[2]))
    return score, ratio, industry, sector, country, priceToBook, marketCap, fiftyDayAverage, twoHundredAverage, profitMargin, grossMargin




def data_into_csv():
    
    csv_input = str(input("Enter the CSV file you want to modify: "))
    col_input = input("Enter the implicit Index of the CSV-Column containing Stock-Tickers: ")
    try:
        csv = pd.read_csv(csv_input, index_col=0)
    except:
        return "\n\nThe filename '" + csv_input + "' does not exist.\n\n"
    
    try:
        csv_tickers = csv.iloc[:,col_input]
        csv.rename({csv.columns[col_input]: 'Code'}, axis='columns')
        csv_tickers = csv_tickers.values
    except:
        return "\n\nThe Column does not contain Stock-Symbols.\n\n"

    counter_array = np.arange(csv_tickers.size)
    df_size = np.full(csv_tickers.size, csv_tickers.size)
    args = np.column_stack((csv_tickers, counter_array, df_size))

    with concurrent.futures.ThreadPoolExecutor() as executor:
        
        results = executor.map(scrape_data, args)

        scores = np.empty(0)            #piotroski F-scores
        peg_ratios = np.empty(0)        #pegRatios
        industries = np.empty(0)        #industries
        sectors = np.empty(0)           #sectors
        countries = np.empty(0)         #countries
        ptbs = np.empty(0)              #pricesToBooks
        mcaps = np.empty(0)             #marketCaps
        fiftyDayAvrgs = np.empty(0)     #fiftyDayAverages
        twoHundredAvrgs = np.empty(0)   #twoHundredAverages
        profitMargins = np.empty(0)     #profitMargins
        grossMargins = np.empty(0)      #grossMargins

        for result in results:
            scores = np.append(scores, result[0])
            peg_ratios = np.append(peg_ratios, result[1])
            industries = np.append(industries, result[2])
            sectors = np.append(sectors, result[3])
            countries = np.append(countries, result[4])
            ptbs = np.append(ptbs, result[5])
            mcaps = np.append(mcaps, result[6])
            fiftyDayAvrgs = np.append(fiftyDayAvrgs, result[7])
            twoHundredAvrgs = np.append(twoHundredAvrgs, result[8])
            profitMargins = np.append(profitMargins, result[9])
            grossMargins = np.append(grossMargins, result[10])

    csv['F-Score'] = scores
    csv['PEG ratio'] = peg_ratios
    csv['Industry'] = industries
    csv['Sector'] = sectors
    csv['Country'] = countries
    csv['Price to Book'] = ptbs
    csv['Market Cap'] = mcaps
    csv['50 Day Av'] = fiftyDayAvrgs
    csv['200 Day Av'] = twoHundredAvrgs
    csv['Profit Margin'] = profitMargins
    csv['Gross Margin'] = grossMargins
    csv.to_csv("cache/out.csv")

    return "\n\n'" + csv_input + "' successfully modified!"




# BOILERPLATE
if __name__ == "__main__":
    print(data_into_csv())