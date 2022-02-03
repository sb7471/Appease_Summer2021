import pandas as pd
import numpy as np
import os
import statistics
import math

class QuickQuery:
    def __init__(self):
        pass

    def get_mean(self, col_name, data_dir):
        num_rows = 0
        means = []
        for filename in os.listdir(data_dir):
            df = pd.read_csv(os.path.join(data_dir, filename))
            means.extend(df[col_name])
            num_rows += len(df.iloc[:, 0])
        return sum(means) / len(means), num_rows

    def get_median(self, col_name, data_dir):
        num_rows = 0
        meds = []
        for filename in os.listdir(data_dir):
            df = pd.read_csv(os.path.join(data_dir, filename))
            # meds.append(df[col_name].median())
            meds.extend(df[col_name])
            num_rows += len(df.iloc[:, 0])
        return statistics.median(meds), num_rows

    def get_mode(self, col_name, data_dir):
        num_rows = 0
        modes = []
        for filename in os.listdir(data_dir):
            df = pd.read_csv(os.path.join(data_dir, filename))
            modes.extend(df[col_name].tolist())
            num_rows += len(df.iloc[:, 0])

        return max(set(modes), key=modes.count),  num_rows

    def get_variance(self, col_name, data_dir):
        num_rows = 0
        vars = []
        for filename in os.listdir(data_dir):
            df = pd.read_csv(os.path.join(data_dir, filename))
            vars.extend(df[col_name])
            num_rows += len(df.iloc[:, 0])

        return np.var(vars), num_rows

    def get_stdev(self, col_name, data_dir):
        variance = self.get_variance(col_name, data_dir)
        stdev = math.sqrt(variance[0])

        return stdev, variance[1]

    def switcher(self, stat, col_name, dir ):

        switch = {
            'mean': self.get_mean(col_name, dir),
            'median': self.get_median(col_name, dir),
            'mode': self.get_mode(col_name, dir),
            'variance': self.get_variance(col_name, dir),
            'stdev': self.get_stdev(col_name, dir)
        }

        return switch[stat]



    def descriptive_stats(self, stat, col_name, game_dir=None, health_dir=None, visualize=False):

        if game_dir is not None:
            grtval, num_rows_game = self.switcher(stat, col_name, game_dir)
            # print(f'The {stat} of {col_name} for the selected game data is {grtval:.3f}')
        return num_rows_game, grtval, str(grtval)

        # if health_dir is not None:
        #     hrtval, num_rows_health = self.switcher(stat, col_name, health_dir)
            # print(f'The {stat} of {col_name} for the selected health data is {hrtval:.3f}')
