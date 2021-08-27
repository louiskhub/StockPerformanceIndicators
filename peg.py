# public imports
import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
# local imports
import errors
import update

def visual_ratio(ticker_input, df, csv_list, scope=(10,10)):
    """Visualizes the PEG-Ratio.
    Explanation of the PEG-Ratio: https://www.investopedia.com/terms/p/pegratio.asp
    """

    main_ticker = str(ticker_input)
    
    ticker_in_df = (df.Code == main_ticker).any()
    peg_in_df = df.loc[(df.Code == main_ticker),"PEG ratio"].notna().any()

    if ticker_in_df & peg_in_df:
        main_ratio = df.loc[(df.Code == main_ticker), "PEG ratio"]
        main_index = df[df["Code"] == main_ticker].index.item()
        df = df.drop(index=main_index)
    else:
        yf_ticker = yf.Ticker(main_ticker)
        if yf_ticker.info["regularMarketPrice"] == None:
            raise errors.TickerError(main_ticker)
        main_ratio = ratio(yf_ticker)
        if main_ratio == None:
            raise errors.MetricError(main_ticker)
        if ticker_in_df:
            df.loc[(df.Code == main_ticker),"PEG ratio"] = main_ratio
        else:
            usa_df = pd.read_csv("cache/usa.csv", index_col=0)
            update.csv(main_ticker, csv_list)
    
    ratio_notna = df.loc[:,"PEG ratio"].notna()
    ratio_max = df.loc[:,"PEG ratio"] < scope[0]
    ratio_min = df.loc[:,"PEG ratio"] > scope[1]
    
    arr = df.loc[(ratio_notna & ratio_max & ratio_min),["Code","PEG ratio"]].values
    tickers = arr[:,0]
    y = arr[:,1]
    sorted_indices = y.argsort(kind="quicksort")
    y = y[sorted_indices]
    tickers = tickers[sorted_indices]
    length = tickers.size
    x = np.arange(length)

    fig = plt.figure(figsize=(17, 10), dpi=80)
    ax = fig.add_subplot()

    ax.set(
        title = "PEG ratios",
        ylim = [np.amin(y), np.amax(y)],
        #yticks = np.arange(10),
        xlim = [-10, x.size + 10],
        xticks = x,
        ylabel = "Ratios", 
        xlabel = "Tickers"
    )
    ax.set_xticklabels(tickers, rotation="45", ha="right", rotation_mode="anchor")
    plt.tick_params(
        axis="x",          # changes apply to the x-axis
        which="both",      # both major and minor ticks are affected
        bottom=False,      # ticks along the bottom edge are off
        top=False,         # ticks along the top edge are off
        labelbottom=False)
    #ax.set_axisbelow(True) # move the plt.grid into the background
    #plt.grid(axis="y")

    mean = np.mean(y)
    std_top = np.full(length, mean + np.std(y))
    std_down = np.full(length, mean - np.std(y))
    ax.fill_between(x, std_top, std_down, alpha=0.3)
    plt.plot(x,np.full(length, mean),"b-")

    sc = ax.scatter(x, y, s=5, c="black", marker='o')
    main_x = np.searchsorted(y, main_ratio)
    ax.scatter(main_x, main_ratio, s=100, c="red", marker='o', edgecolors='black')

    main_annot = ax.annotate(main_ticker, (main_x,main_ratio),
                        xytext=(-30,30),
                        textcoords="offset points",
                        bbox=dict(boxstyle="round", fc="w"),
                        arrowprops=dict(shrinkB=5, arrowstyle="->"))
    main_annot.get_bbox_patch().set_facecolor("red")
    main_annot.get_bbox_patch().set_alpha(0.5)
    annot = ax.annotate("", xy=(0,0),
                        xytext=(-20,20),
                        textcoords="offset points",
                        bbox=dict(boxstyle="round", fc="w"),
                        arrowprops=dict(arrowstyle="->"))
    annot.set_visible(False)

    def update_annot(ind):
        pos = sc.get_offsets()[ind["ind"][0]]
        annot.xy = pos
        text = "{}".format(" ".join([tickers[n] for n in ind["ind"]]))
        annot.set_text(text)
        annot.get_bbox_patch().set_alpha(0.4)

    def hover(event):
        vis = annot.get_visible()
        if event.inaxes == ax:
            cont, ind = sc.contains(event)
            if cont:
                update_annot(ind)
                annot.set_visible(True)
                fig.canvas.draw_idle()
            else:
                if vis:
                    annot.set_visible(False)
                    fig.canvas.draw_idle()
    
    fig.canvas.mpl_connect("motion_notify_event", hover)

    plt.show()

    return df



def ratio(ticker):
    """Returns the PEG-Ratio of a yf.Ticker object.
    Explanation of the PEG-Ratio: https://www.investopedia.com/terms/p/pegratio.asp
    """
    ticker = yf.Ticker(ticker)
    try:
        peg_ratio = ticker.info['pegRatio']
    except:
        return None
    return peg_ratio