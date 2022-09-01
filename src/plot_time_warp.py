import os
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection


def create_graph(min_distances, name, file, distance, target_time):

    x = []
    y = []
    for key in min_distances.keys():
        x.append(key)
        y.append(min_distances[key])
    data_graph = pd.DataFrame({'x': x, 'y': y})
    ax = sns.lineplot(data=data_graph, x='x', y='y')
    
    ax.set_ylim(ymin=0)
    ax.set_xlim(xmin=0)
    
    # Add red marker to lowest distance point
    marker = plt.Circle((target_time[0], round(distance, 2)), 0.2, color='r', zorder=2)
    ax.add_patch(marker)
    
    # Add horizontal & vertical lines
    line_h = [(0, distance), (target_time[0], distance)]
    line_v = [(target_time[0], 0), (target_time[0], distance)]
    lc = LineCollection([line_h, line_v], color=["gray","gray"], lw=0.5, linestyles='dashed', zorder=0)
    plt.gca().add_collection(lc)
    
    # ax.annotate(f"Target time: {target_time[0]} kyr",
    #         xy=(target_time[0], round(distance, 2)), xycoords='data',
    #         xytext=(0, -20), textcoords='offset points',
    #         arrowprops=dict(arrowstyle="->", color='gray'), 
    #         fontsize=8, color='gray'
    #         )
    
    ax.annotate(str(round(distance, 2)),
            xy=(0 - 0.08, round(distance, 2)), xycoords=('axes fraction','data'),
            fontsize=8, color='gray', va='center', ha='left'
            )
    
    ax.annotate(f"{target_time[0]} kyr",
            xy=(target_time[0] + 0.5, 0 + 0.1), xycoords=('data','axes fraction'),
            fontsize=8, color='gray', va='center', ha='left'
            )

    base_path = 'out_figures'
    if not os.path.exists(base_path):
        os.makedirs(base_path, exist_ok=True)    
    
    plt.savefig(os.path.join(base_path, f'dist-vs-time_{file.replace(".csv", "")}_1100.png'), transparent=False)
    plt.savefig(os.path.join(base_path, f'dist-vs-time_{file.replace(".csv", "")}_1100.svg'), transparent=False)
    plt.close()