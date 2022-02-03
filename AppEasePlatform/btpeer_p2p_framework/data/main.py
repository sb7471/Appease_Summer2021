
from data_generator import DataGenerator
from filter import Filter
from quickQuery import QuickQuery
from visualize import Visualize
import os




if __name__ == '__main__':
    # data = DataGenerator()
    # # enter the number of users you want to generate data for
    # data.gen_registration_data(num_users=5)
    # usernames = [file[:-4] for file in os.listdir('registration_data')]
    # # enter the number of days you want to generate data for
    # data.gen_health_data(usernames=usernames, num_days=3)
    # data.gen_game_data()
    filter = Filter()
    # filter.get_game_names('game_data')
    # filter.get_game_usernames('game_data')
    # game_files = filter.filter(
    #     gdir='game_data',
    #     start_date='03-01-2021',
    #     end_date='03-02-2021',
    #     game='Clash-of-Clans',
    #     username=None
    # )
    # if not game_files:
    #     print('No game files found for that criteria. Please try again.')
    #     exit()
    #
    # # game_files = filter.filter_by_username('game_data', 'jPWP4625')
    # health_files = filter.get_health_data_from_game_files('health_data', game_files)
    # if not health_files:
    #     print('No health files found for that criteria. Please try again.')
    #     exit()
    # # print(game_files)
    # # print(health_files)
    # filter.send_to_zip(
    #     zip_dir='zip_data',
    #     zip_name='myzip',
    #     game_dir='game_data',
    #     game_files=game_files,
    #     health_dir='health_data',
    #     health_files=health_files,
    #     rm_files=False)

    # qq = QuickQuery()
    # fgdl = os.path.join('zip_data', 'game_data')
    # fhdl = os.path.join('zip_data', 'health_data')
    # qq.descriptive_stats('mean', 'heart_rate', game_dir=fgdl, health_dir=fhdl)
    # qq.descriptive_stats('median', 'heart_rate', game_dir=fgdl, health_dir=fhdl)
    # qq.descriptive_stats('mode', 'heart_rate', game_dir=fgdl, health_dir=fhdl)
    # qq.descriptive_stats('variance', 'heart_rate', game_dir=fgdl, health_dir=fhdl)
    # qq.descriptive_stats('stdev', 'heart_rate', game_dir=fgdl, health_dir=fhdl)

    vis = Visualize()
    vis.visualize(os.path.join('zip_data', 'game_data'), 'heart_rate')




