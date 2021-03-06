# public imports
import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
# local imports
import update
import visualization

def visual_ratio(main_ticker, df, csv_list, scope=(10,-10)):
    """Visualizes the PEG-Ratio of one main stock and it's specified peers with Matplotlib.
    Explanation of the PEG-Ratio: https://www.investopedia.com/terms/p/pegratio.asp
    main_ticker = ticker string from user input
    df = filtered dataframe containing all the stocks for comparison
    csv_list = list of all CSV filepaths being passed to update.csv()
    scope (kwarg) = user specified range of PEG-ratios
    """
    
    ticker_in_df = (df.Code == main_ticker).any() # checks if the main stock is in the database
    peg_in_df = df.loc[(df.Code == main_ticker),"PEG-Ratio"].notna().any() # checks if the main stock's F-Score is in the database

    if ticker_in_df & peg_in_df:
        main_ratio = df.loc[(df.Code == main_ticker), "PEG-Ratio"].item()
        main_index = df[df["Code"] == main_ticker].index.item()
        df.drop(index=main_index, inplace=True)
        df.reset_index(drop=True, inplace=True)
    else:
        yf_ticker = yf.Ticker(main_ticker) # We need to scrape Yahoo! Finance if the stock is not in out database
        if yf_ticker.info["regularMarketPrice"] == None: # Unavailability of market price indicates that
            print("\n" + main_ticker + " is not listed on Yahoo! Finance.\n") # the stock ticker is not listed
            return visualization.visualize(2)
        main_ratio = ratio(main_ticker)
        if main_ratio == None: # Check if Yahoo! Finance provided enough information for PEG-ratio calculation
            update.csv(main_ticker, csv_list, ticker_in_df) # Let's update our CSV
            print("\nYahoo! Finance does not provide this metric for " + main_ticker + "\n")
            return visualization.visualize(2)
        update.csv(main_ticker, csv_list, ticker_in_df) # Let's update our CSV
    
    # Notify the user that the main stock's PEG-ratio does not fit into the specified scope
    if (main_ratio < scope[1]):
        print("\nThe minimum scope specified is not low enough to display the PEG-ratio of " + main_ticker)
        print("Please select a minimum scope below " + str(main_ratio) + "\n")
        return visualization.visualize(2)
    elif (main_ratio > scope[0]):
        print("\nThe maximum scope specified is not high enough to display the PEG-ratio of " + main_ticker)
        print("Please select a maximum scope above " + str(main_ratio) + "\n")
        return visualization.visualize(2)
    
    # boolean masks for df-cleaning for unfitting values
    ratio_notna = df.loc[:,"PEG-Ratio"].notna()
    ratio_max = df.loc[:,"PEG-Ratio"] < scope[0]
    ratio_min = df.loc[:,"PEG-Ratio"] > scope[1]
    
    # Save every ticker with it's corresponding PEG-ratio in arrays
    arr = df.loc[(ratio_notna & ratio_max & ratio_min),["Code","PEG-Ratio"]].values # clean df
    tickers = arr[:,0]
    y = arr[:,1]
    # sort the tickers after PEG-ratio for prettier plotting
    sorted_indices = y.argsort(kind="quicksort")
    y = y[sorted_indices]
    tickers = tickers[sorted_indices]
    # Save the number of tickers for axes setting
    length = tickers.size
    x = np.arange(length)

    # Prepare the plotting
    fig = plt.figure(figsize=(17, 10), dpi=80)
    ax = fig.add_subplot()
    # Set the scope of the y-axis according to user specifications
    ymax = np.amax(y)
    ymin = np.amin(y)
    # Because the main stock's PEG-ratio is not included in the comparison-array we have to make sure that it is plotted
    if main_ratio > ymax:
        ymax = main_ratio 
    elif main_ratio < ymin:
        ymin = main_ratio
    ax.set(
        title = "PEG-Ratios",
        ylim = [ymin-5, ymax+5],    # Limit the PEG-ratio display to user specifications (with margin for looks)
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

    # Plot the mean and standard deviation of the comparison PEG-Ratios
    mean = np.mean(y)
    std_top = np.full(length, mean + np.std(y))
    std_down = np.full(length, mean - np.std(y))
    ax.fill_between(x, std_top, std_down, alpha=0.3)
    plt.plot(x,np.full(length, mean),"b-")

    sc = ax.scatter(x, y, s=5, c="black", marker='o')   # Plot the comparison stocks 
    main_x = np.searchsorted(y, main_ratio)             # Find out where to place the main stock along the x axis
    ax.scatter(main_x, main_ratio, s=100, c="red", marker='o', edgecolors='black') # Plot the main stock

    # Annotate the main stock (always displayed)
    main_annot = ax.annotate(main_ticker, (main_x,main_ratio),
                        xytext=(-30,30),
                        textcoords="offset points",
                        bbox=dict(boxstyle="round", fc="w"),
                        arrowprops=dict(shrinkB=5, arrowstyle="->"))
    # Make the annotation prettier than the annotations of the comparison stocks
    main_annot.get_bbox_patch().set_facecolor("red")
    main_annot.get_bbox_patch().set_alpha(0.5)

    # Hide the annotations of the comparison stocks
    annot = ax.annotate("", xy=(0,0),
                        xytext=(-20,20),
                        textcoords="offset points",
                        bbox=dict(boxstyle="round", fc="w"),
                        arrowprops=dict(arrowstyle="->"))
    annot.set_visible(False)

    def update_annot(ind):
        """If the user's curser hovers over comparison data points, their annotation is updated/displayed.
        ind = list of indexes for all points under the curser
        """
        pos = sc.get_offsets()[ind["ind"][0]]                               # Get position of curser
        annot.xy = pos
        text = "{}".format(" ".join([tickers[n] for n in ind["ind"]]))      # The annotation content
        annot.set_text(text)
        annot.get_bbox_patch().set_alpha(0.4)                               # Make annotation prettier

    def hover(event):
        """If the user's curser hovers over comparison datapoints, 'update_annot()' is called.
        event = motion_notify_event (curser hovers over datapoint)
        """
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
    
    fig.canvas.mpl_connect("motion_notify_event", hover)                    # Enable hover -> show annotation
    plt.show()
    pass

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