import os
import pandas as pd


# Save individual files for isotopes and aragonite

def handle_csv(file, vars):
    file_name = file.replace(".csv", "")
    for item in vars[1:]:
        data = pd.read_csv(os.path.join('data', file), usecols=[vars[0], item])
        data = data.dropna()
        data.to_csv(os.path.join('data', f"{file_name}_{item}.csv"), index=False)


def core_files():
    vars_1100 = ['depth_m', 'd13C_pl', 'd18O_pl', 'aragonite']
    vars_1150 = ['depth_m', 'aragonite' , 'd18O_pl', 'd13C_pl', 'd13C_bulk', 'd18O_bulk']
    core_files = ['core_1100.csv', 'core_1150.csv']
    
    for file in core_files:
        if '1100' in file:
            handle_csv(file, vars_1100)
        elif '1150' in file:
            handle_csv(file, vars_1150)

    
def main():
    core_files()


if __name__ == "__main__":
    main()
