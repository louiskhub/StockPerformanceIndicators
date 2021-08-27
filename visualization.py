# public imports
import pandas as pd
import glob
# local imports
from indicators import piotroski
from indicators import peg

def load_csvs():
    path = 'cache'
    csv_list = glob.glob(path + "/*.csv")
    df = pd.concat((pd.read_csv(f, index_col=0) for f in csv_list))
    return df, csv_list

def scope_input():
    try:
        try:
            scope_min = int(input("Enter the MINIMAL PEG-ratio to be displayed (Default is -10): "))
            scope_max = int(input("Enter the MAXIMAL PEG-ratio to be displayed (Default is 10): "))
            return scope_min, scope_max
        except:
            print("You need to select an integer.")
            return scope_input()
    except KeyboardInterrupt:
        print("\n\nInterrupted!")

def visualize(indicator):
    try:
        ticker_input = input("Enter the stock ticker of the company you want to compare to it's peers: ")
        df, csv_list = load_csvs()
        if indicator == 1:
            piotroski.visual_f_score(ticker_input, df, csv_list)
        if indicator == 2:
            scope_min, scope_max = scope_input()
            if (scope_min is not None) and (scope_max is not None):
                scope = (scope_max, scope_min)
                peg.visual_ratio(ticker_input, df, csv_list, scope)
            else:
                peg.visual_ratio(ticker_input, df, csv_list)
    except KeyboardInterrupt:
        print("\n\nInterrupted!")