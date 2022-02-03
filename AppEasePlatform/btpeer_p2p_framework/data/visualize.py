import os
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from statistics import mean
import time

class Visualize:

    def __init__(self):
        pass


    # problem play length is different
    # solution visualize the aggregated using the shortest game period > 5 min
    def visualize(self, data_dir, feature):
        plt.ioff()
        plt.switch_backend('Agg') 
        feature_matrix = []

        for filename in os.listdir(data_dir):
            game_name = filename.split('_')[-1][:-4]
            df = pd.read_csv(os.path.join(data_dir, filename))
            feature_matrix.append(df[feature].tolist())

        feature_matrix.sort(key=len)

        for l in feature_matrix:
            if len(l) < 10:
                feature_matrix.remove(l)

        y = list(map(lambda x : sum(x) / len(x), zip(*feature_matrix)))
        x = [i for i in range(len(y))]
        ax = sns.lineplot(x=x, y=y)
        ax.set_title(feature + ' for ' + game_name)
        ax.set_ylabel(feature)
        ax.set_xlabel('minutes elapsed')

        filename = "visual_{}_{}.png".format(feature,"".join(time.strftime(time.ctime()).split()[-3:]).replace(":","").replace(":",""))
        # use feature name, date and time to ensure each plot is unique.
        plt.savefig(filename)
        plt.close()
        return filename