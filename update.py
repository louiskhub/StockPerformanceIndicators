# public imports
import yfinance as yf
import pandas as pd
import numpy as np
# local imports
import piotroski
import peg

def csv(ticker, csv_list, ticker_in_df):
    """Updated a csv file with information about the main stock specified by the user.
    ticker = ticker string from user input
    csv_list = list of all CSV filepaths
    ticker_in_df = True if the ticker exists already in the database
    """
    
    # If the ticker is not already included in a csv and there is no specific csv fitting to the main stock
    filepath = "cache/usa.csv" # usa.csv gets appended with the stock information 
    df_usa = pd.read_csv(filepath, index_col=0)
    df = df_usa

    yf_ticker = yf.Ticker(ticker) # Yahoo! Finance has to be scraped
    info = yf_ticker.info
    country = info['country'] # The most fitting csv is chosen by country/exchange
    if country == "China": # This is not because I think that HK is part of China but rather for avoidance 
        country = "Hong Kong" # of mixups in the current Ticker-Database!
    elif country == "United States":
        country = "USA"
    elif country == "United Kingdom":
        country = "UK"

    if ticker_in_df:
        for path in csv_list:
            frame = pd.read_csv(path, index_col=0)
            if (frame.Code == ticker).any():
                filepath = path
                df = frame
                index = df.loc[(df.Code == ticker), "Code"].index.item() # set the index of the ticker in the corresponding csv
                break
    else:
        for path in csv_list:
            frame = pd.read_csv(path, index_col=0)
            if (frame.Country == country).any(): # choose the most fittin csv by country
                filepath = path
                df = frame
                break
        df = df.append(pd.Series(dtype='object'), ignore_index=True) # append an empty row to the dataframe
        index = df.index.size - 1 # set the index (last row of dataframe)

    # Fill the corresponding row with stock info
    df.loc[index, "Code"] = ticker
    df.loc[index, "Name"] = info["longName"]
    df.loc[index, "F-Score"] = piotroski.f_score(ticker)
    df.loc[index, "PEG-Ratio"] = peg.ratio(ticker)
    df.loc[index, "Industry"] = info['industry']
    df.loc[index, "Sector"] = info['sector']
    df.loc[index, "Price to Book"] = info['priceToBook']
    df.loc[index, "Market Cap"] = info['marketCap']
    df.loc[index, "50 Day Av"] = info['fiftyDayAverage']
    df.loc[index, "200 Day Av"] = info['twoHundredDayAverage']
    df.loc[index, "Profit Margin"] = info['profitMargins']
    df.loc[index, "Gross Margin"] = info['grossMargins']
    # Generalization: Only fill in this info, if the CSV has columns for them (CSV's from EOD have but others might not)
    if "Name" in df.columns:
        df.loc[index, "Name"] = info["longName"]
    if "Country" in df.columns:
        df.loc[index, "Country"] = country
    if "Exchange" in df.columns:
        df.loc[index, "Exchange"] = info["exchange"]
    if "Currency" in df.columns:
        df.loc[index, "Currency"] = info["financialCurrency"]
    
    df.reset_index(drop=True, inplace=True)
    df.to_csv(filepath) # save the CSV
    pass