import pandas as pd
import os
import time
from sklearn import preprocessing as pre

DATA_DIR = 'Spring21_SE_project/data'



# get modelling data

def build_model(data_dir="../../data"):


    def split_data(data_dir):
        dir = data_dir + "/game_data"
        game_files = [ i for i in os.listdir(dir) if 'csv' in i] # fetch all file names in game data directoryy

        # converting files to dataframe files
        dfs_train, dfs_test = [],[]

        for i in game_files:
            gdf = pd.read_csv(i, parse_dates=["timestamp"])
            gdf = gdf.diff()[1:] # generates changes in values with each time period of 1 min
            gdf["game"] = i.split(".")[0].rsplit("_")[-1] # adds name of the game that has the data

            # Splitting the data to train/test 80/20
            train_stop_idx = round(gdf.shape[0] * 0.8)

            dfs_train.append(gdf[:train_stop_idx])
            dfs_test.append(gdf[train_stop_idx+1:])

        all_train_df = pd.concat(dfs_train)
        all_test_df = pd.concat(dfs_test)

    

        return pd.concat([all_train_df, all_test_df])

    def send_data():
        pass

    def fetch_data():
        pass

    def merge_all_data():
        pass


    def scale_data(train_df, test_df):
        scaler = pre.MinMaxScaler()
        x_scaled = scaler.fit_transform(train_df.values)
        return x_scaled

        scaled_train_df, scaled_test_df = None, None
        return scaled_train_df, scaled_test_df


    def train_model():
        return model



    all_train, all_test = split_data(data_dir)


    scaled_train, scaled_test = scale_data()
    model = train_model()



# build_model()

if __name__ == "__main__":
    game_dir = DATA_DIR + '/game_data'
    print(os.listdir(game_dir))