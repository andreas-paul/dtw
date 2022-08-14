import os
import sys
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

ref = "LR04stack.txt"
ref_cols = ['Time_ka', 'd18O']


names = ['1100', '1150']
variables = ['d18O', 'aragonite']


def main():
    
    # Load general target    
    target = pd.read_csv(f'data/{ref}', sep='\s+', engine='python', usecols=ref_cols) 
    target = target[target['Time_ka'] <= max_age]
    
    # 
    for name in names:
        for var in variables:
            files = [x for x in os.listdir('data') if var in x and name in x]  
            for file in files:
                data = pd.read_csv(f'data/{file}', skip_blank_lines=True)
                dtw = SedimentTimeWarp(target=target, data=data, normalize=True, smooth=True, window_size=11, polynomial=3)
                simple_distance = dtw.simple_distance()    
                log.debug(f'Calculated distance (simple): {round(simple_distance, 2)} (rounded)')
                distance, target_time, min_distances = dtw.find_min_distance(0, max_age, time_step, warp_path=True)
                log.debug(f'Found minimum distance: {round(distance, 2)} at target time {target_time[0]} kyrs')                
                # log.debug(dtw.warping_path)
                
                # Create plot
                create_graph(min_distances, name, file, distance, target_time)



if __name__ == "__main__":
    main()













    
    
    


    # target.iloc[:,1] = zscore(target.iloc[:,1])
    # data.iloc[:,1] = zscore(data.iloc[:,1])

    # test_dtw = SedimentTimeWarp(target=target, data=data)
    # simple_distance = test_dtw.simple_distance(use_smoothed=True, window_size=11, polynomial=3) 

    # path = dtw.warping_path(data.iloc[:,1], target.iloc[:,1])
    # warped = dtw.warp(data.iloc[:,1], target.iloc[:,1], path)
    # fig = dtwvis.plot_warping(data.iloc[:,1], target.iloc[:,1], path, filename='figures/dtwvis_plot.png')
   
    # data['index'] = data.index
    # data['dtw_age'] = data['index'].apply(lambda x: test_dtw.map_warping_path(warped[1], x))

    # sns.lineplot(data=data, x='depth_m', y='dtw_age')
    # plt.savefig('figures/1100_d18O_dtw.png')
    # plt.close()

    # sns.lineplot(data=data, x='dtw_age', y='d18O_pl')
    # ax2 = plt.twinx()
    # sns.set_style("whitegrid", {'axes.grid' : False})
    # sns.lineplot(data=target, x='Time_ka', y='Benthic_d18O_per-mil', ax=ax2, color="r", legend=True, linestyle='dashed', linewidth='0.8')
    # plt.savefig('figures/1100-vs-stack.png')
    # plt.close()