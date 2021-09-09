# public imports
import json
# local imports
from visualization import visualize
from data_into_csv import data_into_csv



def selection():
    input_value = input("Select a number: ").strip()
    if input_value == "break":
        return "break"
    try:
        input_value = int(input_value)
        if (input_value > 0) and (input_value < 5):
            return input_value
        else:
            print("You need to select a value from 1-3.")
            selection()
    except:
        print("You need to select a value from 1-3.")
        selection()

def main():
    while True:
        print("\n\n\n\nType 'break' to exit the script.")
        print("\n\nSelect what you want to do: \n\n")
        print(json.dumps([ # Pretty print
            "Visualize the Piotroski F-score of a stock: 1",
            "Visualize the PEG-ratio of a stock: 2",
            "Load stock perfomance-indicators into a CSV file: 3"
            ], indent=4))
        print("\n")

        input_value = selection()
        print("\n")
        if input_value == 1:
            response = visualize(1)
        elif input_value == 2:
            response = visualize(2)
        elif input_value == 3:
            response = data_into_csv()
            print(response)
        elif input_value == "break":
            print("\n")
            break
        if response == "break":
            print("\n\n\n")
            break
    pass



# BOILERPLATE
if __name__ == "__main__":
    main()