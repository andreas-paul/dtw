import numpy as np
import pandas as pd
from pathlib import Path
from typing import Union
from loguru import logger as log
from scipy.stats import zscore
from plot_time_warp import *
from savitzky_golay import savitzky_golay
from dtaidistance import dtw
from dtaidistance import dtw_visualisation as dtwvis


class SedimentTimeWarp:

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

    def __init__(self, target: pd.DataFrame, data: pd.DataFrame, normalize: bool = True, smooth: bool = True, window_size: int = 11, polynomial: int = 3):

        self._target: pd.DataFrame = target.copy()
        self._data: pd.DataFrame = data.copy()

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
            # self.target.iloc[:,1] = self.smooth_time_series(self.target.iloc[:,1], window_size=window_size, polynomial=polynomial)
            self._data.iloc[:,1] = self.smooth_time_series(self._data.iloc[:,1], window_size=window_size, polynomial=polynomial)
        
        log.debug(f"Using '{self._target.columns[1]}' as target and '{self._data.columns[1]}' as data")
        log.debug(f'normalization set to {normalize}; smoothing set to {smooth}')
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
        _, paths = dtw.warping_paths(data.iloc[:,1], _target.iloc[:,1])
        best_path = dtw.best_path(paths)        
        return best_path, paths

    @staticmethod
    def map_warping_path(warping_path, index: int):
        """Map the warping path to the original indices"""
        for item in warping_path:
            if item[0] == index:
                return item[1]

    @staticmethod
    def monte_carlo(self):
        """Perform complex Monte Carlo simulation of various 
        parameters to find minimum Euclidian distance(s) for 
        given target/data pair.        
        """
        pass


    def simple_distance(self):
        """Calculate Euclidian distance for a given target/data pair        
        """      
        distance: float = dtw.distance(self._data.iloc[:,1], self._target.iloc[:,1])                  
        return distance


    def find_min_distance(self, start_time: Union[int, float], end_time: Union[int, float], time_step_size: Union[int, float], name: str,  
                            warp_path: bool = False, plot_warping_path: bool = False):
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

        warp_path: bool
            If true, also calculates the warping path for the age corresponding to the minimum distance found.

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

        min_distances: dict = {}

        # TODO: Parallelize this
        for i in range(start_time, end_time, time_step_size):
            if i > 0:
                log.debug(f"End time: {i}")
                _target = self._target[self._target.iloc[:,0] <= i]
                distance = dtw.distance(self._data.iloc[:,1], _target.iloc[:,1])
                min_distances[i] = distance

        distance: float = min(min_distances.values())
        target_time: list[float] = [k for k, v in min_distances.items() if v==distance]
        log.debug(f'Minimum distance found: ~{round(distance, 2)} at time_step_size={target_time[0]}')

        if warp_path:
            self.best_path, self.paths = self.get_warping_path(self._data, self._target, target_time[0])   
        
        if plot_warping_path:
            dtwvis.plot_warping(self._data.iloc[:,1], self._target.iloc[:,1], self.best_path, Path('out_warping-paths', name))
            dtwvis.plot_warpingpaths(self._data.iloc[:,1], self._target.iloc[:,1], self.paths, self.best_path, Path('out_warping-paths', f"matrix_{name}") )
            
        return distance, target_time, min_distances


