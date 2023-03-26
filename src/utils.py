import pandas as pd

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