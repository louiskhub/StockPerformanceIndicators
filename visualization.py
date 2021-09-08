# public imports
import pandas as pd
import glob
import json
import yfinance as yf
# local imports
import piotroski
import peg

def load_csvs():
    path = 'cache'
    csv_list = glob.glob(path + "/*.csv")
    df = pd.concat((pd.read_csv(f, index_col=0) for f in csv_list))
    return df, csv_list

def choose_comparison(ticker_input, indicator):
    print("\n\nCompare the " + indicator + " of " + ticker_input + " by:\n\n")
    print(json.dumps([ # Pretty print
        "Country: 1",
        "Industry: 2",
        "Sector: 3",
        "Market Capitalization: 4",
        "All cached stocks : 5"
        ], indent=4))
    print("\n")
    input_value = input("Select a number: ").strip()
    if input_value == "break":
        return "break"
    try:
        input_value = int(input_value)
        if (input_value > 0) and (input_value < 6):
            return input_value
        else:
            print("You need to select a value from 1-5.")
            choose_comparison(ticker_input, indicator)
    except:
        print("You need to select a value from 1-5.")
        choose_comparison(ticker_input, indicator)

def mcap_categorization(mcap):
    try:
        if mcap > 200000000000: #= 200b
            mcap_cat = "MEGA"
        elif 200000000000 > mcap > 10000000000: #= 10b
            mcap_cat = "LARGE"
        elif 10000000000 > mcap > 2000000000: #= 2b
            mcap_cat = "MID"
        elif 2000000000 > mcap > 300000000: #= 300m
            mcap_cat = "SMALL"
        else:
            mcap_cat = "MICRO"
    except:
        for index, value in mcap.items():
            if value > 200000000000: #= 200b
                mcap[index] = "MEGA"
            elif 200000000000 > value > 10000000000: #= 10b
                mcap[index] = "LARGE"
            elif 10000000000 > value > 2000000000: #= 2b
                mcap[index] = "MID"
            elif 2000000000 > value > 300000000: #= 300m
                mcap[index] = "SMALL"
            else:
                mcap[index] = "MICRO"
            mcap_cat = mcap
    return mcap_cat

def filter_df(comp, df, input_value, indicator):
    ticker_in_df = (df.Code == input_value).any()
    if ticker_in_df:
        if comp == 1:
            country = df.loc[(df.Code == input_value),"Country"].item()
            df.drop(df[df.Country != country].index, inplace=True)
            df.reset_index(drop=True, inplace=True)
        elif comp == 2:
            industry = df.loc[(df.Code == input_value),"Industry"].item()
            df.drop(df[df.Industry != industry].index, inplace=True)
            df.reset_index(drop=True, inplace=True)
        elif comp == 3:
            sector = df.loc[(df.Code == input_value),"Sector"].item()
            df.drop(df[df.Sector != sector].index, inplace=True)
            df.reset_index(drop=True, inplace=True)
        elif comp == 4:
            mcap = df.loc[(df.Code == input_value),"Market Cap"].item()

            df.drop(df[(mcap_categorization(df.loc[:,"Market Cap"].copy()) != mcap_categorization(mcap))].index, inplace=True)
            df.reset_index(drop=True, inplace=True)
    else:
        ticker = yf.Ticker(input_value)
        info = ticker.info
        if comp == 1:
            country = info["country"]
            if country == "China": # This is not because I think that HK is part of China but rather for avoidance 
                country = "Hong Kong" # of mixups in the Ticker-Database!
            elif country == "United States":
                country = "USA"
            elif country == "United Kingdom":
                country = "UK"
            df.drop(df[df.Country != country].index, inplace=True)
            df.reset_index(drop=True, inplace=True)
        elif comp == 2:
            industry = info["industry"]
            df.drop(df[df.Industry != industry].index, inplace=True)
            df.reset_index(drop=True, inplace=True)
        elif comp == 3:
            sector = info["sector"]
            df.drop(df[df.Sector != sector].index, inplace=True)
            df.reset_index(drop=True, inplace=True)
        elif comp == 4:
            mcap = info["marketCap"]
            df.drop(df[(mcap_categorization(df.loc[:,"Market Cap"].copy()) != mcap_categorization(mcap))].index, inplace=True)
            df.reset_index(drop=True, inplace=True)
    if df.index.size > 0:
        return df
    else:
        print("\n\nUnfortunately there are no cached stocks available for your selection. Please try again.\n")
        return visualize(indicator)

def scope_input():
    scope_min = input("Enter the MINIMAL PEG-ratio to be displayed (Default is -10): ").strip()
    if scope_min == "break":
        return "break", "break"
    scope_max = input("Enter the MAXIMAL PEG-ratio to be displayed (Default is 10): ").strip()
    if scope_max == "break":
        return "break", "break"
    if scope_min == "" and scope_max == "":
        return scope_min, scope_max
    try:
        if scope_max == "":
            scope_min = int(scope_min)
            return scope_min, scope_max
        if scope_min == "":
            scope_max = int(scope_max)
            return scope_min, scope_max
        scope_min = int(scope_min)
        scope_max = int(scope_max)
        return scope_min, scope_max
    except:
        print("You need to select an Integer or press 'Enter' for the default value.")
        return scope_input()

def visualize(indicator):
    ticker_input = str(input("Enter the stock ticker of the company you want to compare to it's peers: ")).strip().upper()
    if ticker_input == "BREAK":
        return "break"
    df, csv_list = load_csvs()
    df.reset_index(drop=True, inplace=True)
    if indicator == 1:
        comp = choose_comparison(ticker_input, "Piotroski F-Score")
        if comp == "break":
            return "break"
        df_filtered = filter_df(comp, df, ticker_input, indicator)
        piotroski.visual_f_score(ticker_input, df_filtered, csv_list)
    if indicator == 2:
        comp = choose_comparison(ticker_input, "PEG-Ratio")
        if comp == "break":
            return "break"
        df_filtered = filter_df(comp, df, ticker_input, indicator)
        scope_min, scope_max = scope_input()
        if (scope_min and scope_max) != "break":
            if (scope_min != "") and (scope_max != ""):
                scope = (scope_max, scope_min)
                peg.visual_ratio(ticker_input, df_filtered, csv_list, scope)
            elif scope_min != "":
                scope = (10, scope_min)
                peg.visual_ratio(ticker_input, df_filtered, csv_list, scope)
            elif scope_max != "":
                scope = (scope_max, -10)
                peg.visual_ratio(ticker_input, df_filtered, csv_list, scope)
            else:
                peg.visual_ratio(ticker_input, df_filtered, csv_list)
        else:
            return "break"