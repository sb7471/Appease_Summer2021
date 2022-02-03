
import os, shutil
import pandas as pd
import datetime as dt


class Filter:

    def __init__(self):
        self.GAME_IND = 3
        self.GAME_DATE_IND = 0
        self.GAME_USERNAME_IND = 2
        self.HEALTH_DATE_IND = 0
        self.HEALTH_USERNAME_IND = 1

    def get_game_names(self, dir):
        games = set()
        for filename in os.listdir(dir):
            games.add(filename.split('_')[self.GAME_IND][:-4])
        for game in games:
            print(game)

    def get_game_usernames(self, dir):
        games = set()
        for filename in os.listdir(dir):
            games.add(filename.split('_')[self.GAME_USERNAME_IND])
        for game in games:
            print(game)

    def filter_by_game(self, filenames, game_name):

        fn = []

        for filename in filenames:

            if filename.split('_')[self.GAME_IND][:-4] == game_name:
                fn.append(filename)

        return fn

    def filter_by_username(self, filenames, username):

        fn = []

        for filename in filenames:

            if filename.split('_')[self.GAME_USERNAME_IND] == username:
                fn.append(filename)

        return fn

    def filter_by_date(self, filenames, start_date, end_date):

        fn = []
        start_date = pd.to_datetime(start_date)
        end_date = pd.to_datetime(end_date)

        for filename in filenames:

            date = pd.to_datetime(filename.split('_')[self.GAME_DATE_IND])

            if start_date <= date <= end_date:
                fn.append(filename)

        return fn

    def load_game_filenames(self, gdir):
        return [filename for filename in os.listdir(gdir)]

    def empty_folder(self, data_dir):
        for file in os.scandir(data_dir):
            os.remove(file.path)

#     right now returning the number of files queried and the number of files returned after filtering
    def filter(self, gdir=None, start_date=None, end_date=None, game=None, username=None):

        # get ALL game files
        filenames = self.load_game_filenames(gdir)
        # get the number of game files
        num_queried_files = len(filenames)

        # filter by date, game, or username
        if start_date and end_date:
            filenames = self.filter_by_date(filenames, start_date, end_date)
        if game:
            filenames = self.filter_by_game(filenames, game)
        if username:
            filenames = self.filter_by_username(filenames, username)

        # get the number of game files after filtering
        num_filtered_files = len(filenames)

        # retrieves the health data associated with the fame files
        def get_health_data_from_game_files(dir, game_files):
            health_files = []
            for game_file in game_files:
                gd = game_file.split('_')
                date, username = gd[self.GAME_DATE_IND], gd[self.GAME_USERNAME_IND]
                for filename in os.listdir(dir):
                    hd = filename.split('_')
                    if hd[self.HEALTH_DATE_IND] == date and hd[self.HEALTH_USERNAME_IND] == username:
                        health_files.append(filename)
            return health_files

        def output_to_dir(game_files, health_files, parent_dir, overwrite=True):
            filtered_game_data = os.path.join(parent_dir, 'filtered_game_data')
            filtered_health_data = os.path.join(parent_dir, 'filtered_health_data')
            game_data = os.path.join(parent_dir, 'game_data')
            health_data = os.path.join(parent_dir, 'health_data')

            # check to make sure output dirs exist and create them if they don't
            if not(os.path.isdir(filtered_game_data)):
                os.mkdir(filtered_game_data)
            if not(os.path.isdir(filtered_health_data)):
                os.mkdir(filtered_health_data)


            # clear the filtered dirs of previous data
            if overwrite:
                self.empty_folder(filtered_game_data)
                self.empty_folder(filtered_health_data)

            # set source and dest dirs to copy files
            game_source, game_dest = game_data, filtered_game_data
            health_source, health_dest = health_data, filtered_health_data

            # copy filtered game and health files over
            for game_file in game_files:
                source = os.path.join(game_source, game_file)
                dest = os.path.join(game_dest, game_file)
                shutil.copy(source, dest)

            for health_file in health_files:
                source = os.path.join(health_source, health_file)
                dest = os.path.join(health_dest, health_file)
                shutil.copy(source, dest)

        hdir = os.path.join(os.path.dirname(gdir), 'health_data')
        health_files = get_health_data_from_game_files(hdir, filenames)
        output_to_dir(filenames, health_files, os.path.dirname(gdir))


        return num_queried_files, num_filtered_files


    # def send_to_zip(self, zip_dir, zip_name, game_dir=None, health_dir=None, game_files=None, health_files=None, rm_files=True):
    #
    #
    #     if game_dir is not None and game_files is not None:
    #         os.mkdir(os.path.join(zip_dir, 'game_data'))
    #         for game_file in game_files:
    #             source = os.path.join(game_dir, game_file)
    #             dest = os.path.join(zip_dir, 'game_data', game_file)
    #             shutil.copy(source, dest)
    #     if health_dir is not None and health_files is not None:
    #         os.mkdir(os.path.join(zip_dir, 'health_data'))
    #         for health_file in health_files:
    #             source = os.path.join(health_dir, health_file)
    #             dest = os.path.join(zip_dir, 'health_data', health_file)
    #             shutil.copy(source, dest)
    #
    #     # make zip file
    #     shutil.make_archive(zip_name, 'zip', zip_dir)
    #
    #     # delete data in zip_data
    #     if rm_files:
    #         if game_dir is not None:
    #             shutil.rmtree(os.path.join(zip_dir, game_dir))
    #         if health_dir is not None:
    #             shutil.rmtree(os.path.join(zip_dir, health_dir))



