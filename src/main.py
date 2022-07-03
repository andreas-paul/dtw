import sys
import pandas as pd
from loguru import logger as log
from sediment_time_warp import *


log.remove()
log.add(sys.stderr, level="DEBUG")


def main():
    data = pd.read_csv('data/core_1100.csv', usecols=['depth_m', 'd18O_pl'])    
    
    target = pd.read_csv('data/LR04stack.txt', sep='\s+', engine='python', usecols=['Time_ka', 'd18O']) 
    target = target[target['Time_ka'] <= 245]

    test_dtw = SedimentTimeWarp(target=target, data=data, normalize=True, smooth=True, window_size=11, polynomial=3)

    simple_distance = test_dtw.simple_distance()    
    log.debug(f'Calculated distance: {round(simple_distance, 2)} (rounded)')
    
    distance, target_time, min_distances = test_dtw.find_min_distance(0, 245, 10, warp_path=True)
    log.debug(f'Found minimum distance: {round(distance, 2)} (rounded), with target time = {target_time} and minimum distance = {min_distances}')
    log.debug(test_dtw.warping_path)


if __name__ == "__main__":
    main()













    
    
    
    # _, _, results = test_dtw.find_min_distance(100, 1000, 5, warp_path=True)

    # x = []
    # y = []
    # for key in results.keys():
    #     x.append(key)
    #     y.append(results[key])
    # data_graph = pd.DataFrame({'x': x, 'y': y})
    # sns.lineplot(data=data_graph, x='x', y='y')
    # plt.savefig('figures/dist-vs-time_smooth.png', transparent=True)
    # plt.close()

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