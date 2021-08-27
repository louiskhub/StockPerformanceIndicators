# public imports
import pandas as pd
import glob
# local imports
from piotroski import visual_f_score
from peg import visual_ratio

def load_csvs():
    path = 'cache'
    csv_list = glob.glob(path + "/*.csv")
    df = pd.concat((pd.read_csv(f, index_col=0) for f in csv_list))
    return df, csv_list

def visualize():
    ticker_input = input("Enter Stock-Ticker you want to compare: ")
    df, csv_list = load_csvs()
    visual_f_score(ticker_input, df, csv_list)
    #scope = (10, -10)
    #visual_ratio(ticker_input, df, csv_list, scope)


# BOILERPLATE
if __name__ == "__main__":
    visualize()