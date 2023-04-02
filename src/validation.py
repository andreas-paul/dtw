import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from loguru import logger as log
from src.sediment_dtw import SedimentDTW
from plot_time_warp import create_graph

from dtaidistance import dtw
from dtaidistance import dtw_visualisation as dtwvis

np.random.seed(1234)

# SINE WAVE

# Set parameters
min = 0  
max = 50 
step = 5 

# Create sine wave
sine = np.arange(min, max, 0.1)
amplitude = np.sin(sine)

# Create noise and add to amplitude
noisy_amp = amplitude + np.random.uniform(-1, 1, len(sine))

# # Duplicate noisy curve but cut at different lengths to simulate cores
# lengths = list(np.random.randint(min, len(sine), 10))
# lengths.sort()
# if 500 not in lengths:
#     lengths.append(500)

# cost = list()
# for length in lengths:
#     data = noisy_amp[0:length]
#     log.info(len(data))
#     distance = SedimentDTW(target=amplitude, data=data, normalize=False)
#     simple_distance = distance.simple_distance()  
#     log.info(simple_distance)
#     cost.append(simple_distance)

# plt.plot(cost)
# plt.show()


# -------------------------------------------------------------------------
# Testing
# s1 = [0, 0, 1, 2, 1, 0, 1, 0, 0]
# s2 = [0, 1, 2, 0, 0, 0, 0, 0, 0]

s1 = np.array([0., 0, 1, 2, 1, 0, 1, 0, 0, 2, 1, 0, 0])
s2 = np.array([0., 1, 2, 3, 1, 0, 0, 0, 2, 1, 0, 0, 0])


distance = SedimentDTW(target=s2, data=s1, normalize=True)
simple_distance = distance.simple_distance() 
direct_dtw_distance = dtw.distance(s1, s2, use_pruning=True)

log.info(f"SedimentDTW simple_distance {simple_distance}")
log.info(f"Direct DTW distance: {direct_dtw_distance}")

# Plot sine wave with noise
# plt.plot(sine, amplitude)
# plt.plot(sine, noisy_amp)
# plt.show()

print(dtw.distance(amplitude, amplitude))
print(dtw.distance(amplitude, noisy_amp))

noisy_amp_sub = np.random.choice(noisy_amp, 300, replace=False)
print(dtw.distance(amplitude, noisy_amp_sub))

# # Plot sine wave with noise
# plt.plot(sine, amplitude)
# plt.plot(noisy_amp_sub)
# plt.show()


distance, target_time, min_distances = distance.find_min_distance(0, 14, 1, name="test")
print(distance)
print(min_distances)

plt.plot(min_distances.keys(), min_distances.values())
plt.show()