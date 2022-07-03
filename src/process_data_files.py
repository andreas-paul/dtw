import os
import pandas as pd


def core_files():
    vars_1100 = ['depth_m', 'd13C_pl', 'd18O_pl', 'aragonite']
    vars_1150 = ['depth_m', 'aragonite' , 'd18O_pl', 'd13C_pl', 'd13C_bulk', 'd18O_bulk']
    core_files = ['core_1100.csv', 'core_1150.csv']


    for file in core_files:    
        data = pd.read_csv(os.path.join('data', file), usecols=vars_1100 if '1100' in file else vars_1150)
        data.to_csv(os.path.join('data', file), index=False)

    
def main():
    core_files()


if __name__ == "__main__":
    main()
