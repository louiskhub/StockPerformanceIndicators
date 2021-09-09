# public imports
import pandas as pd
import numpy as np

download_link_1 = "https://eodhistoricaldata.com/api/exchange-symbol-list/"
download_link_2 = "?api_token="
token = "" # Enter your API-token here (You get one when creating a free account on https://eodhistoricaldata.com/)


# Download the CSV files containing the Ticker symbols
# You can find the documentation here: https://eodhistoricaldata.com/financial-apis/exchanges-api-list-of-tickers-and-trading-hours/

usa = pd.read_csv(download_link_1 + "US" + download_link_2 + token)
london = pd.read_csv(download_link_1 + "LSE" + download_link_2 + token)
xetra = pd.read_csv(download_link_1 + "XETRA" + download_link_2 + token)
toronto = pd.read_csv(download_link_1 + "TO" + download_link_2 + token)
hongkong = pd.read_csv(download_link_1 + "HK" + download_link_2 + token)
shenzhen = pd.read_csv(download_link_1 + "SHE" + download_link_2 + token)
australia = pd.read_csv(download_link_1 + "AU" + download_link_2 + token)
moskau = pd.read_csv(download_link_1 + "MCX" + download_link_2 + token)

print("\nCSVs downloaded!")


# Preprocess the data

# We only want Stocks (not ETFs, etc. because we cannot get PI's from Yahoo! Finance for them)
usa.drop(index=usa.index[(usa.Type != "Common Stock")], inplace=True)
# We only want rows with content
usa.dropna(axis=0, how="all", inplace=True)
usa.reset_index(drop=True, inplace=True)

london.drop(index=london.index[(london.Type != "Common Stock")], inplace=True)
london.dropna(axis=0, how="all", inplace=True)
london.reset_index(drop=True, inplace=True)
# For every non-USA stock ticker we need to append a suffix to the ticker specifying the Exchange: https://www.gnucash.org/docs/v4/C/gnucash-help/fq-spec-yahoo.html
london.iloc[:,0] = london.iloc[:,0].apply(lambda x: str(x) + ".L")

xetra.drop(index=xetra.index[(xetra.Type != "Common Stock")], inplace=True)
xetra.dropna(axis=0, how="all", inplace=True)
xetra.reset_index(drop=True, inplace=True)
xetra.iloc[:,0] = xetra.iloc[:,0].apply(lambda x: str(x) + ".DE")

toronto.drop(index=toronto.index[(toronto.Type != "Common Stock")], inplace=True)
toronto.dropna(axis=0, how="all", inplace=True)
toronto.reset_index(drop=True, inplace=True)
toronto.iloc[:,0] = toronto.iloc[:,0].apply(lambda x: str(x) + ".TO")

hongkong.drop(index=hongkong.index[(hongkong.Type != "Common Stock")], inplace=True)
hongkong.dropna(axis=0, how="all", inplace=True)
hongkong.reset_index(drop=True, inplace=True)
hongkong.iloc[:,0] = hongkong.iloc[:,0].apply(lambda x: str(x) + ".HK")

shenzhen.drop(index=shenzhen.index[(shenzhen.Type != "Common Stock")], inplace=True)
shenzhen.dropna(axis=0, how="all", inplace=True)
shenzhen.reset_index(drop=True, inplace=True)
shenzhen.iloc[:,0] = shenzhen.iloc[:,0].apply(lambda x: str(x) + ".SZ")

australia.drop(index=australia.index[(australia.Type != "Common Stock")], inplace=True)
australia.dropna(axis=0, how="all", inplace=True)
australia.reset_index(drop=True, inplace=True)
australia.iloc[:,0] = australia.iloc[:,0].apply(lambda x: str(x) + ".AX")

moskau.drop(index=moskau.index[(moskau.Type != "Common Stock")], inplace=True)
moskau.dropna(axis=0, how="all", inplace=True)
moskau.reset_index(drop=True, inplace=True)
moskau.iloc[:,0] = moskau.iloc[:,0].apply(lambda x: str(x) + ".ME")

print("\nPreprocessing done!")


# Save the dataframes as csv's in the "cache/" directory
filepath = "cache/"

usa.to_csv(filepath + "usa.csv")
xetra.to_csv(filepath + "xetra.csv")
london.to_csv(filepath + "london.csv")
toronto.to_csv(filepath + "toronto.csv")
hongkong.to_csv(filepath + "hongkong.csv")
shenzhen.to_csv(filepath + "shenzhen.csv")
australia.to_csv(filepath + "australia.csv")
moskau.to_csv(filepath + "moskau.csv")

print("\nCSV Files created!\n\n")