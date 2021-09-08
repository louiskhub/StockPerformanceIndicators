# public imports
import yfinance as yf
import pandas as pd
import numpy as np
# local imports
import piotroski
import peg

def csv(ticker, csv_list, ticker_in_df):
    
    filepath = "cache/usa.csv"
    df_usa = pd.read_csv(filepath, index_col=0)
    df = df_usa

    yf_ticker = yf.Ticker(ticker)
    info = yf_ticker.info
    country = info['country']
    if country == "China": # This is not because I think that HK is part of China but rather for avoidance 
        country = "Hong Kong" # of mixups in the Ticker-Database!
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
                index = df.loc[(df.Code == ticker), "Code"].index.item()
                break
    else:
        for path in csv_list:
            frame = pd.read_csv(path, index_col=0)
            if (frame.Country == country).any():
                filepath = path
                df = frame
                break
        df = df.append(pd.Series(dtype='object'), ignore_index=True)
        index = df.index.size - 1

    df.loc[index, "Code"] = ticker
    df.loc[index, "Name"] = info["longName"]
    df.loc[index, "Country"] = country
    df.loc[index, "Exchange"] = info["exchange"]
    df.loc[index, "Currency"] = info["financialCurrency"]
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
    df.reset_index(drop=True, inplace=True)
    df.to_csv(filepath)

    pass