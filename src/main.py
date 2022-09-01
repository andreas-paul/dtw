import os
import ast
import sys
import json
from tkinter import W
import pandas as pd
import numpy as np
from loguru import logger as log
from sediment_time_warp import *
from plot_time_warp import create_graph

# TODO: Calculate min distance 1100 w/ new age model vs 1150

# If needed, change the logger level here (e.g., from DEBUG to INFO)
log.remove()
log.add(sys.stderr, level="DEBUG")

# Define some initial parameters here. 
# For example, if biostratigraphic data indicates that the age of oldest sediments in the core cannot exceed 245k years, set this number to 245. Similarly, set the min_age variable to the minimum age you except the core top to be. For piston core from the ocean bottom, it is a good idea to set this to 0, but if data is available, such as for example the topmost 10k years are missing, this variable can be set to start at something else than 0. 

min_age = 0  # in kiloyears (kyrs) before present
max_age = 600 # in kiloyears (kyrs) before present
time_step = 10  # in kiloyears

# # 1st run
# ref = "LR04stack"
# ref_path = f'data/{ref}.csv'
# ref_cols = ['time', 'd18O']
# names = ['1100', '1150']
# variables = ['d18O', 'aragonite']

# 2nd run
ref = "1100"
ref_path = f'out_warping-paths/dist-vs-time_core_{ref}_d18O_pl_LR04stack.txt'
ref_cols = ['time', 'value']
names = ['1150']
variables = ['d18O', 'aragonite']


def convert_warp_path_to_timeseries(target: list, data: list, warp_path: list):
    new_time = list()
    new_value = list()
    for item in warp_path:
        i = item[0]
        j = item[1]
        new_value.append(data[i])
        new_time.append(target[j])

    frame = list(zip(new_time, new_value))    
    dataset = pd.DataFrame(frame, columns=['time', 'value'])
    return dataset


def main():
    
    # Load general target    
    target = pd.read_csv(ref_path, usecols=ref_cols) 
    target = target[target['time'] <= max_age]
    
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

                # Use best path to create
                data_list = data.iloc[:,1].to_list()
                target_list = target.iloc[:,0].to_list()
                dataset = convert_warp_path_to_timeseries(target_list, data_list, dtw.best_path)                
                dataset.to_csv(os.path.join(base_path, f'dist-vs-time_{file.replace(".csv", "")}_{ref}.txt'), index=False)
                
                # Create plot
                create_graph(min_distances, name, file, distance, target_time)


if __name__ == "__main__":
    main()
