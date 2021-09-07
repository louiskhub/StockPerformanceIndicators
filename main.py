# public imports
import json
# local imports
from visualization import visualize
import errors



def selection():
    input_value = input("Select a number: ").strip()
    if input_value == "break":
        return "break"
    try:
        input_value = int(input_value)
        if (input_value > 0) and (input_value < 5):
            return input_value
        else:
            print("You need to select a value from 1-4.")
            selection()
    except:
        print("You need to select a value from 1-4.")
        selection()

def main():
    while True:
        print("\n\nType 'break' to exit the script.")
        print("\n\nSelect what you want to do: \n")
        print(json.dumps([ # Pretty print
            "Visualize the Piotroski F-score of a stock: 1",
            "Visualize the PEG-ratio of a stock: 2",
            "Download a CSV file with stock tickers from eodhistoricaldata.com: 3",
            "Load stock perfomance-indicators into a CSV file: 4"
            ], indent=4))
        print("\n")

        input_value = selection()
        if input_value == 1:
            vis = visualize(1)
        elif input_value == 2:
            vis = visualize(2)
        elif input_value == 3:
            vis = visualize(1)
        elif input_value == 4:
            vis = visualize(2)
        elif input_value == "break":
            break
        if vis == "break":
            break
    pass



# BOILERPLATE
if __name__ == "__main__":
    main()