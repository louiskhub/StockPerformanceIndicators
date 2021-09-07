# public imports
import pandas as pd
import glob
# local imports
import piotroski
import peg

def load_csvs():
    path = 'cache'
    csv_list = glob.glob(path + "/*.csv")
    df = pd.concat((pd.read_csv(f, index_col=0) for f in csv_list))
    return df, csv_list

def choose_comparison(ticker_input, indicator):
    print("\n\nCompare the " + indicator + " of " + ticker_input + " by:\n")
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
            choose_comparison()
    except:
        print("You need to select a value from 1-5.")
        choose_comparison()

def mcap_categorization(mcap):
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
    return mcap_cat

def filter_df(comp, df, input_value, indicator):
    ticker_in_df = (df.Code == input_value).any()
    if ticker_in_df:
        if comp == 1:
            country = df.at[df.index[(df.Code == input_value)],"Country"]
            df.drop(index=df.index[(df.Country != country)], inplace=True)
            df.reset_index(drop=True, inplace=True)
        elif comp == 2:
            industry = df.at[df.index[(df.Code == input_value)],"Industry"]
            df.drop(index=df.index[(df.Industry != industry)], inplace=True)
            df.reset_index(drop=True, inplace=True)
        elif comp == 3:
            sector = df.at[df.index[(df.Code == input_value)],"Sector"]
            df.drop(index=df.index[(df.Sector != sector)], inplace=True)
            df.reset_index(drop=True, inplace=True)
        elif comp == 4:
            mcap = df.at[df.index[(df.Code == input_value)],"Market Cap"]
            df.drop(index=df.index[(mcap_categorization(df.loc[:,"Market Cap"]) != mcap_categorization(mcap))], inplace=True)
            df.reset_index(drop=True, inplace=True)
        return df
    else:
        ticker = yf.Ticker(input_value)
        info = ticker.info
        if comp == 1:
            country = info["country"]
            df.drop(index=df.index[(df.Country != country)], inplace=True)
            df.reset_index(drop=True, inplace=True)
        elif comp == 2:
            industry = info["industry"]
            df.drop(index=df.index[(df.Industry != industry)], inplace=True)
            df.reset_index(drop=True, inplace=True)
        elif comp == 3:
            sector = info["sector"]
            df.drop(index=df.index[(df.Sector != sector)], inplace=True)
            df.reset_index(drop=True, inplace=True)
        elif comp == 4:
            mcap = info["marketCap"]
            df.drop(index=df.index[(mcap_categorization(df.loc[:,"Market Cap"]) != mcap_categorization(mcap))], inplace=True)
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
    if ticker_input == "break":
        return "break"
    df, csv_list = load_csvs()
    if indicator == 1:
        comp = choose_comparison(ticker_input, "Piotroski F-Score")
        df = filter_df(comp, df, ticker_input, indicator)
        piotroski.visual_f_score(ticker_input, df, csv_list)
    if indicator == 2:
        comp = choose_comparison(ticker_input, "PEG-Ratio")
        df = filter_df(comp, df, ticker_input, indicator)
        scope_min, scope_max = scope_input()
        if (scope_min and scope_max) != "break":
            if (scope_min != "") and (scope_max != ""):
                scope = (scope_max, scope_min)
                peg.visual_ratio(ticker_input, df, csv_list, scope)
            elif scope_min != "":
                scope = (10, scope_min)
                peg.visual_ratio(ticker_input, df, csv_list, scope)
            elif scope_max != "":
                scope = (scope_max, -10)
                peg.visual_ratio(ticker_input, df, csv_list, scope)
            else:
                peg.visual_ratio(ticker_input, df, csv_list)
        else:
            return "break"
    pass