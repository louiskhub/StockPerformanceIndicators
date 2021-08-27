# stock-performance-indicators

As my final project for the scientific python course I implemented visualizations of the following stock performance indicators:
- Piotroski F-Score (Explanation: https://www.investopedia.com/terms/p/piotroski-score.asp)
- PEG-ratio (Explanation: https://www.investopedia.com/terms/p/pegratio.asp)

To retreive the data needed for calculating these indicators I used the libary yfinance which scrapes Yahoo! Finance. To access this data one only a valid Stock-Ticker (i.e. 'APPL' for Apple, Inc.). This makes the libary pretty easy to access when retreiving data for a single Company. I tried to retreive data for as many stocks as possible and use them for comparison. To my knowledge this has never been publicised before (at least I did not find anything open source). I also found out why: Collecting the relevant data is far more complicated and unreliable. This is why this project is not really finished but rather turned out to be a prototype.

Please make sure to check you have installed all the packages listed in requirements.txt (e.g. with pip install -r requirements.txt) to ensure functioning code.

KNOWN ISSUES:
- yfinance does not always provide the data that Yahoo! Finance provides acurately. For instance: The PEG-ratio of RAA.DE is displayed on the website but cannot be retreived by yfinance.
- Options 3 & 4 are (currently) just dummies and the user only gets redirected to the "visualize" function. The final version will include both options

HOW TO USE REPO:
- clone it
- execute the main.py file in your command line prompt
