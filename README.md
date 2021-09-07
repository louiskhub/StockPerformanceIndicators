# stock performance indicators

## Important Notes

Please make sure that you have installed all the packages listed in `requirements.txt` (e.g. with pip install -r requirements.txt).

## Description

As my final project for the scientific python course I implemented visualizations of the following stock performance indicators (called PI in the following):
- Piotroski F-Score (Explanation: https://www.investopedia.com/terms/p/piotroski-score.asp)
- PEG-ratio (Explanation: https://www.investopedia.com/terms/p/pegratio.asp)

The user is asked to select a stock PI after running the `main.py` and can then enter the stock ticker (i.e. AAPL for Apple, Inc.). The selected PI of this company will then be compared with the PI of other stocks. These 'other stocks' can be filtered from the previously scraped database `/cache` by:
- country
- industry (Explanation: https://www.investopedia.com/terms/i/industry.asp)
- sector (Explanation: https://www.investopedia.com/terms/s/sector.asp)
- market capitalization category (Mega/Large/Mid/Small/Micro Cap) (Explanation: https://www.investopedia.com/terms/m/marketcapitalization.asp under **Market Cap and Investment Strategy**)

To retreive the data needed for these indicators I used the libary yfinance which scrapes Yahoo! Finance.
All the visualizations are done with matplotlib.

## The cached Stock Database

I tried to retreive data for as many stocks as possible and use them for comparison. To my knowledge this has never been publicised before (at least I did not find anything open source). I also found out why: Collecting the relevant data is far more complicated and unreliable. This is why this project is not really finished but rather turned out to be a prototype.

## Structure

Mind Map

## Known Issues

- Options 3 & 4 are (currently) just dummies and the user only gets redirected to the "visualize" function. The final version will include both options