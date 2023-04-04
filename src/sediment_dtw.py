import numpy as np
import pandas as pd
from pathlib import Path
import multiprocessing as mp
from typing import Union, List
from loguru import logger as log
from scipy.stats import zscore
from plotting import *
from savitzky_golay import savitzky_golay
from dtaidistance import dtw
from dtaidistance import dtw_visualisation as dtwvis


class SedimentDTW:

    """
    A class representing a dynamic time warp object using sedimentary core (or similar) data.

    Attributes
    ----------
    target: pd.DataFrame
        A reference data set, e.g. the Lisiecki & Raymo benthic stack (LR04). Must not contain missing values (nan)
        Format:
            1st column: continous variable (e.g. age, time, depth)
            2nd column: values

    data: pd.DataFrame
        Actual data. Must not contain missing values (nan).
        Format:
            1st column: continous variable (e.g. age, time, depth)
            2nd column: values

    normalize: bool
        Defaults to true. Calculates zscore for values column (usually 2nd column, index 1)

    smooth: bool
        Defaults to true. Applies the savitzky-golay smoothing algorithm to values column. Default values: window-size=11, polynomial=3.

    window_size: int
        Used if smooth = True. Parameter for savitzky-golay algorithm

    polynomial: int
        Used if smooth = True. Parameter for savitzky-golay algorithm

    Methods
    -------


    Example usage
    -------------




    
    """

    def __init__(self, target, data, normalize: bool = False, smooth: bool = False, window_size: int = 11, polynomial: int = 3):

        if type(target) is not pd.DataFrame:
            raise TypeError("Target is not the correct type. Allowed type: pandas.DataFrame")
        
        if type(data) is not pd.DataFrame:
            raise TypeError("Data is not the correct type. Allowed type: pandas.DataFrame")
     
        # # Input validation
        # if type(target) is not pd.Series and type(target) is not list and type(target) is not np.array:
        #     raise TypeError("Target is not the correct type. Allowed types: pandas.Series, list, numpy.array")
        
        # if type(data) is not pd.Series and type(data) is not list and type(data) is not np.array:
        #     raise TypeError("Target is not the correct type. Allowed types: pandas.Series, list, numpy.array")
        
        self._target = target.copy()
        self._data = data.copy()

        if self._target.iloc[:,1].isnull().values.any():
            log.exception("Target must not contain empty rows (nan). Please remove rows first and retry.")
            raise TypeError
        
        if self._data.iloc[:,1].isnull().values.any():
            log.exception("Data must not contain empty rows (nan). Please remove rows first and retry.")
            raise TypeError
        
        if normalize:
            self._target.iloc[:,1] = zscore(self._target.iloc[:,1])
            self._data.iloc[:,1] = zscore(self._data.iloc[:,1])

        if smooth:
            self._data.iloc[:,1] = self.smooth_time_series(self._data.iloc[:,1], window_size=window_size, polynomial=polynomial)
        
        log.debug("Time-warp object created successfully!")


    @staticmethod
    def smooth_time_series(time_series: Union[pd.Series, list, np.array], 
                            window_size: int = 11, polynomial: int = 3):
        """Smooth a time-series using Savitzky-Golay smoothing algorithm
        """        
        return savitzky_golay(time_series, window_size, polynomial)


    @staticmethod
    def get_warping_path(data, target, target_time: Union[int, float]):       
        _target = target[target.iloc[:,0] <= target_time]
        _distance, paths = dtw.warping_paths(data.iloc[:,1], _target.iloc[:,1])
        best_path = dtw.best_path(paths)        
        return best_path, paths, _distance



    @staticmethod
    def map_warping_path(warping_path, index: int):
        """Map the warping path to the original indices"""
        for item in warping_path:
            if item[0] == index:
                return item[1]

    def simple_distance(self):
        """Calculate Euclidian distance for a given target/data pair        
        """
        distance: float = dtw.distance(self._data.iloc[:,1], self._target.iloc[:,1])                  
        return distance
    
    @staticmethod
    def convert_dictproxy_to_dict(dict_proxy_dict):
        import json
        return json.dumps(dict_proxy_dict.copy())
    

    @staticmethod
    def calculate_distance(time, target, data, min_distances_dict):
        _target = target[target.iloc[:,0] <= time]
        distance = dtw.distance(data.iloc[:,1], _target.iloc[:,1])
        min_distances_dict[int(time)] = distance


    def find_min_distance(self, start_time: Union[int, float], end_time: Union[int, float], 
                          time_step_size: Union[int, float], warp_path: bool = False):
        """Find the minimum Euclidian distance(s) for a given target/data pair by stepping
        through the range of the target series given by [start_time: <time_step_size> :end_time]. 
        This is basically the same as simple_distance() but with the added functionality of looping.

        Parameters
        ----------
        start_time: int or float
            The minimum range value to filter the target time-series by (0 > start_time). 
            Needs to be larger than the time_step_size, and larger than 0.

        end_time: int or float
            The maximum range value to filter the target time-series by 0 > end_time). 
            Needs to be larger than the start_time, time_step_size, and larger than 0.

        time_step_size: int or float
            The step size used to filter the target time-series, iterating through the target from start_time to
            end_time in steps=time_step_size.

        Returns
        -------
        distance: float
            The smallest distance found in the search.

        target_time: list[float]
            A list of time associated with the distance variable.

        min_distances: dict
            A dictionary containing time_step:distance pairs, the raw 
            data from which both distance and target_time where selected.

        Example usage
        -------------
        
        """

        times = np.arange(start=start_time, stop=end_time, step=time_step_size) 
        manager = mp.Manager()
        min_distances_dict = manager.dict()
        n_cores = mp.cpu_count() - 1
        if n_cores <= 0:
            raise Exception("Invalid number of CPUs - exiting")

        pool = mp.Pool(n_cores)
        for time in times:           
            pool.apply_async(self.calculate_distance, args=(time, self._target, self._data, min_distances_dict))

        pool.close()
        pool.join()

        distance: float = min(min_distances_dict.values())
        time: float = [k for k, v in min_distances_dict.items() if v==distance][0]

        if warp_path:
            self.best_path, self.paths, _distance = self.get_warping_path(self._data, self._target, time)  
            log.debug(f"{distance}, {_distance}")
            if distance != _distance:
                raise ValueError(f"Distances between iterative best curve and best path not equal: {distance} vs {_distance}")

        return distance, time, min_distances_dict
