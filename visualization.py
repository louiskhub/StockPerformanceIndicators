# public imports
import pandas as pd
import glob
import json
import yfinance as yf
# local imports
import piotroski
import peg

def load_csvs():
    """Returns dataframe containing all CSV files from directory 'cache' and returns a list of the filepaths.
    """

    path = 'cache'
    csv_list = glob.glob(path + "/*.csv") # collect all filepaths
    df = pd.concat((pd.read_csv(f, index_col=0) for f in csv_list)) # concatenate all files to one dataframe
    return df, csv_list

def choose_comparison(ticker_input, indicator):
    """Returns user input for filtering of the cached stock database.
    ticker_input = stock ticker chosen by user
    indicator = value 1 or 2 resembling the stock PI the user chose in 'main.py'
    """

    # user prompt
    print("\n\nCompare the " + indicator + " of " + ticker_input + " by:\n\n")
    print(json.dumps([ # Pretty print
        "Industry: 1",
        "Sector: 2",
        "Market Capitalization: 3",
        "All cached stocks : 4"
        ], indent=4))
    print("\n")

    # user input
    input_value = input("Select a number: ").strip()
    if input_value == "break":
        return "break"
    # catch input errors
    try:
        input_value = int(input_value)
        if (input_value > 0) and (input_value < 5):
            return input_value
        else:
            print("\n\n\n\nYou need to select a value from 1-4!\n\n")
            return choose_comparison(ticker_input, indicator)
    except:
        print("\n\n\n\nYou need to select a value from 1-4!\n\n")
        return choose_comparison(ticker_input, indicator)

def mcap_categorization(mcap):
    """Returns either
    Market Capitalization Category of a single Market Capitalization
    OR
    Series of Market Capitalization Categories of a Series containing Market Capitalizations.
    mcap = single Market Capitalization or ‚Series containing Market Capitalizations.
    """

    try: # Code for single Market Capitalization
        if mcap > 200000000000:                                     # mcap > 200b
            mcap_cat = "MEGA"
        elif 200000000000 > mcap > 10000000000:                     #= 200b > mcap > 10b
            mcap_cat = "LARGE"
        elif 10000000000 > mcap > 2000000000:                       #= 10b > mcap > 2b
            mcap_cat = "MID"
        elif 2000000000 > mcap > 300000000:                         #= 2b > mcap > 300m
            mcap_cat = "SMALL"
        else:                                                       #= 300m > mcap
            mcap_cat = "MICRO"
    
    except: # Code for Series containing Market Capitalizations
        for index, value in mcap.items():
            if value > 200000000000:
                mcap[index] = "MEGA"
            elif 200000000000 > value > 10000000000:
                mcap[index] = "LARGE"
            elif 10000000000 > value > 2000000000:
                mcap[index] = "MID"
            elif 2000000000 > value > 300000000:
                mcap[index] = "SMALL"
            else:
                mcap[index] = "MICRO"
            mcap_cat = mcap
    
    return mcap_cat

def filter_df(comp, df, input_value, indicator):
    """Returns dataframe after user-specified filters were applied.
    comp = user specified filter
    df = dataframe containing stock info for comparison
    ticker_input = stock ticker chosen by user
    indicator = value 1 or 2 resembling the stock PI the user chose in 'main.py'
    """

    ticker_in_df = (df.Code == input_value).any() # Checks if the main ticker is in the dataframe
    if ticker_in_df:
        if comp == 1:
            industry = df.loc[(df.Code == input_value),"Industry"].item() # industry of the main stock
            df.drop(df[df.Industry != industry].index, inplace=True) # drop all stocks from different industries than main stock
            df.reset_index(drop=True, inplace=True)
        elif comp == 2:
            sector = df.loc[(df.Code == input_value),"Sector"].item() # sector of the main stock
            df.drop(df[df.Sector != sector].index, inplace=True) # drop all stocks from different sector than main stock
            df.reset_index(drop=True, inplace=True)
        elif comp == 3:
            mcap = df.loc[(df.Code == input_value),"Market Cap"].item() # Market Capitalization of the main stock
            df.drop(df[(mcap_categorization(df.loc[:,"Market Cap"].copy()) != mcap_categorization(mcap))].index, inplace=True) # drop all stocks in different market capitalization category than main stock
            df.reset_index(drop=True, inplace=True)
    else:
        ticker = yf.Ticker(input_value) # if the main ticker is not in the dataframe Yahoo! Finance has to be scraped
        info = ticker.info
        if info["regularMarketPrice"] == None: # Unavailability of market price indicates that
            print("\n" + input_value + " is not listed on Yahoo! Finance.\n") # the stock ticker is not listed
            return visualize(indicator)
        if comp == 1:
            industry = info["industry"]
            df.drop(df[df.Industry != industry].index, inplace=True)
            df.reset_index(drop=True, inplace=True)
        elif comp == 2:
            sector = info["sector"]
            df.drop(df[df.Sector != sector].index, inplace=True)
            df.reset_index(drop=True, inplace=True)
        elif comp == 3:
            mcap = info["marketCap"]
            df.drop(df[(mcap_categorization(df.loc[:,"Market Cap"].copy()) != mcap_categorization(mcap))].index, inplace=True)
            df.reset_index(drop=True, inplace=True)
    # Comparison is only useful with enough data points available
    if df.index.size > 1:
        return df
    else:
        print("\n\nUnfortunately there are no cached stocks available for your selection. Please try again.\n")
        return visualize(indicator)

def scope_input():
    """Returns user-specified scope of PEG-ratio or an empty string.
    """
    
    # user prompt
    scope_min = input("Enter the MINIMAL PEG-ratio to be displayed (Default is -10): ").strip()
    if scope_min == "break":
        return "break", "break"
    scope_max = input("Enter the MAXIMAL PEG-ratio to be displayed (Default is 10): ").strip()
    if scope_max == "break":
        return "break", "break"

    if scope_min == "" and scope_max == "": # empty strings are returned if user only hits "Enter"
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
    # catch input errors
    except:
        print("You need to select an Integer or press 'Enter' for the default value.")
        return scope_input()

def visualize(indicator):
    """Prompts user for stock ticker input and calls functions based on user input in 'choose_comparison()', 'scope_input()' and 'main.py'.
    indicator = value 1 or 2 resembling the stock PI the user chose in 'main.py'
    """
    
    # user prompt
    ticker_input = str(input("Enter the stock ticker of the company you want to compare to it's peers: ")).strip().upper()
    if ticker_input == "BREAK":
        return "break"
    
    df, csv_list = load_csvs() # get the large dataframe and all filepaths
    df.reset_index(drop=True, inplace=True) # better one time too much as one time too few

    if indicator == 1:
        comp = choose_comparison(ticker_input, "Piotroski F-Score") # filter selection by user
        if comp == "break":
            return "break"
        df_filtered = filter_df(comp, df, ticker_input, indicator) # filter the dataframe
        piotroski.visual_f_score(ticker_input, df_filtered, csv_list) # plot the F-Score
    
    elif indicator == 2:
        comp = choose_comparison(ticker_input, "PEG-Ratio")
        if comp == "break":
            return "break"
        df_filtered = filter_df(comp, df, ticker_input, indicator)
        scope_min, scope_max = scope_input()
        if (scope_min and scope_max) != "break":
            # check if user specified a (partial) scope
            if (scope_min != "") and (scope_max != ""):
                scope = (scope_max, scope_min)
                peg.visual_ratio(ticker_input, df_filtered, csv_list, scope) # plot the PEG-Ratio with specified scope
            elif scope_min != "":
                scope = (10, scope_min)
                peg.visual_ratio(ticker_input, df_filtered, csv_list, scope)
            elif scope_max != "":
                scope = (scope_max, -10)
                peg.visual_ratio(ticker_input, df_filtered, csv_list, scope)
            else:
                peg.visual_ratio(ticker_input, df_filtered, csv_list) # plot the PEG-Ratio with default scope
        else:
            return "break"