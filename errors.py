class TickerError(Exception):
    """Exception raised if the input ticker is not listed on Yahoo! Finance.
    Attributes:
        ticker -- input ticker which caused the error
        msg -- explanation of the error
    """

    def __init__(self, ticker_input, msg = "is not listed on Yahoo! Finance."):
        self.ticker_input = ticker_input
        self.msg = msg
        super().__init__(self.msg)
    def __str__(self):
        return f'"{self.ticker_input.upper()}" {self.msg}'



class MetricError(Exception):
    """Exception raised if the input Metric is not provided by Yahoo! Finance for the specified yf.Ticker.
    Attributes:
        ticker -- input ticker which caused the error
        msg -- explanation of the error
    """

    def __init__(self, ticker_input, msg = "Yahoo! Finance does not provide this metric for "):
        self.ticker_input = ticker_input
        self.msg = msg
        super().__init__(self.msg)
    def __str__(self):
        return f'{self.msg}"{self.ticker_input.upper()}".'