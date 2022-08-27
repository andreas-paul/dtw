import os
import sys
import ast
import pandas as pd
from loguru import logger as log
from sediment_time_warp import *
from plot_time_warp import create_graph


# If needed, change the logger level here (e.g., from DEBUG to INFO)
log.remove()
log.add(sys.stderr, level="DEBUG")

# Define some initial parameters here. 
# For example, if biostratigraphic data indicates that the age of oldest sediments in the core cannot exceed 245k years, set this number to 245. Similarly, set the min_age variable to the minimum age you except the core top to be. For piston core from the ocean bottom, it is a good idea to set this to 0, but if data is available, such as for example the topmost 10k years are missing, this variable can be set to start at something else than 0. 

min_age = 0  # in kiloyears (kyrs) before present
max_age = 600  # in kiloyears (kyrs) before present
time_step = 10  # in kiloyears

ref = "LR04stack"
ref_cols = ['Time_ka', 'd18O']

names = ['1100', '1150']
variables = ['d18O', 'aragonite']

# TMP
# target = pd.read_csv(f'data/{ref}.txt', sep='\s+', engine='python', usecols=ref_cols) 
# target = target[target['Time_ka'] <= max_age]
# data = pd.read_csv('data/core_1100_aragonite.csv', skip_blank_lines=True)
# with open('out_warping-paths/dist-vs-time_core_1100_aragonite_LR04stack.txt', 'r') as f:
#     warping_path = ast.literal_eval(f.readline())
    
# count = 0
# for item in warping_path:
#     count += 1
# print(count)


# def map_warping_paths(warping_path, target, data) -> pd.DataFrame:
#     """Map the warping path coming from dtaidistance package between time series
#     """
#     # As row indices
#     # left: data
#     # right: target (ref)
#     # [(0, 0), (1, 1), (2, 2), ...]



def main():
    
    # Load general target    
    target = pd.read_csv(f'data/{ref}.txt', sep='\s+', engine='python', usecols=ref_cols) 
    target = target[target['Time_ka'] <= max_age]
    
    # Move through cores and find distance(s)
    for name in names:        
        for var in variables:
            
            files = [x for x in os.listdir('data') if var in x and name in x]  
            for file in files:
                
                data = pd.read_csv(f'data/{file}', skip_blank_lines=True)
                dtw = SedimentTimeWarp(target=target, data=data, normalize=True, smooth=True, window_size=11, polynomial=3)               
                
                simple_distance = dtw.simple_distance()    
                log.debug(f'Calculated distance (simple): {round(simple_distance, 2)} (rounded)')
                
                distance, target_time, min_distances = dtw.find_min_distance(0, max_age, time_step, 
                                                                             name=f'dist-vs-time_{file.replace(".csv", "")}_{ref}.png', warp_path=True, plot_warping_path=True)                
                log.debug(f'Found minimum distance: {round(distance, 2)} at target time {target_time[0]} kyrs')       
                                
                base_path = 'out_warping-paths'
                if not os.path.exists(base_path):
                    os.makedirs(base_path, exist_ok=True)
                    
                with open(os.path.join(base_path, f'dist-vs-time_{file.replace(".csv", "")}_{ref}.txt'), 'w') as f:
                    f.write(str(dtw.best_path)) 
                
                # Create plot
                create_graph(min_distances, name, file, distance, target_time)


if __name__ == "__main__":
    main()
