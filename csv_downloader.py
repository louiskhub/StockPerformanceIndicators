# public imports
import pandas as pd

download_link_1 = "https://eodhistoricaldata.com/api/exchange-symbol-list/"
download_link_2 = "?api_token="
token = "" # Enter your token here
"""
usa = pd.read_csv(download_link_1 + "US" + download_link_2 + token, index_col=0)
london = pd.read_csv(download_link_1 + "LSE" + download_link_2 + token, index_col=0)
xetra = pd.read_csv(download_link_1 + "XETRA" + download_link_2 + token, index_col=0)
toronto = pd.read_csv(download_link_1 + "TO" + download_link_2 + token, index_col=0)
hongkong = pd.read_csv(download_link_1 + "HK" + download_link_2 + token, index_col=0)
shenzhen = pd.read_csv(download_link_1 + "SHE" + download_link_2 + token, index_col=0)
australia = pd.read_csv(download_link_1 + "AU" + download_link_2 + token, index_col=0)
moskau = pd.read_csv(download_link_1 + "MCX" + download_link_2 + token, index_col=0)
"""
print("\nCSVs downloaded!")

"""
london.iloc[:,0] = london.iloc[:,0].apply(lambda x: str(x) + ".L")
xetra.iloc[:,0] = xetra.iloc[:,0].apply(lambda x: str(x) + ".DE")
toronto.iloc[:,0] = toronto.iloc[:,0].apply(lambda x: str(x) + ".TO")
hongkong.iloc[:,0] = hongkong.iloc[:,0].apply(lambda x: str(x) + ".HK")
shenzhen.iloc[:,0] = shenzhen.iloc[:,0].apply(lambda x: str(x) + ".SZ")
australia.iloc[:,0] = australia.iloc[:,0].apply(lambda x: str(x) + ".AX")
moskau.iloc[:,0] = moskau.iloc[:,0].apply(lambda x: str(x) + ".ME")
"""
print("\nSuffixes added!")

filepath = "csv_downloads/"
"""
usa.to_csv(filepath + "usa.csv")
xetra.to_csv(filepath + "xetra.csv")
london.to_csv(filepath + "london.csv")
toronto.to_csv(filepath + "toronto.csv")
hongkong.to_csv(filepath + "hongkong.csv")
shenzhen.to_csv(filepath + "shenzhen.csv")
australia.to_csv(filepath + "australia.csv")
moskau.to_csv(filepath + "moskau.csv")
"""
print("\nCSV Files created!\n\n")