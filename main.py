# public imports
import json
# local imports
from visualization import visualize



def user_input():
    try:
        input_value = int("Selection: ")
    except:
        print("You need to select a value from 1-4.")
        return user_input()
    if (input_value > 0) and (input_value < 5):
        return input_value
    else:
        print("You need to select a value from 1-4.")
        return user_input()

def user_terminal():
    try:
        while True:
            print("\nPress Ctrl+C to exit.")
            print("\n\nSelect what you want to do: \n")
            print(json.dumps([ # Pretty print
                "Visualize the Piotroski F-score of a stock: 1",
                "Visualize the PEG-ratio of a stock: 2",
                "Download a CSV file with stock tickers from eodhistoricaldata.com: 3",
                "Load stock perfomance-indicators into a CSV file: 4",
                ], indent=4))
            print("\n")

            input_value = user_input()
            if input_value == 1:
                visualize(input_value)
            elif input_value == 2:
                visualize(input_value)
            elif input_value == 3:
                visualize(peg_ratio)
            elif input_value == 4:
                visualize(peg_ratio)

    except KeyboardInterrupt:
        print("\n\nInterrupted!")
    pass



# BOILERPLATE
if __name__ == "__main__":
    user_terminal()