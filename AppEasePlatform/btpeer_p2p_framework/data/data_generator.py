
import string
import random
import scipy.stats
import datetime as dt
import pandas as pd
import os
import uuid
import names


class DataGenerator:

    def __init__(self):

        self.MIN_HEARTRATE = 40
        self.MAX_HEARTRATE = 200
        self.MEAN_HEARTRATE = 80
        self.STDEV_HEARTRATE = 10
        self.BLOOD_TYPES = ('O-', 'O+', 'A-', 'A+', 'B-', 'B+', 'AB-', 'AB+')
        self.SEX = ('male', 'female')
        self.START_DATE = '2021-03-01'
        self.END_DATE = '2021-03-31'
        self.START_TIME = '07:00:00'
        self.END_TIME = '21:00:00'
        self.MINUTES_IN_TIMEFRAME = 840
        self.MAX_STEPS = 100
        self.MIN_STEPS = 0
        self.MEAN_STEPS = 10
        self.STDEV_STEPS = 10
        self.CALORIES_PER_STEP = 0.04
        self.MAX_GAMETIME = 180 #minutes
        self.MIN_GAMETIME = 5 #minutes
        self.GAMES = ('Angry-Birds', 'Clash-of-Clans', 'Brawl-Stars', 'Injustice-2', 'Catan')
        self.MAX_GAMES_PER_DAY = 3
        self.MIN_GAMES_PER_DAY = 1
        self.WAKE_PERIOD = 60 #time after waking up before games are played in minutes


    # generates a unique 8 character username that has 4 letters followed by 4 digits
    # fxn also checks to see if the username exists. If it does exist then loops again and generates a new username
    # a new username is then appended to the username file
    # def gen_user_name(self, number_of_users=1):
    #
    #     un_file = open('usernames.txt', 'a+')
    #     existing_un = set(line.strip() for line in un_file)
    #     for i in range(number_of_users):
    #         username = []
    #         while True:
    #             for i in range(8):
    #                 username.append(random.choice(string.ascii_letters)) if i < 4 else username.append(str(random.randint(0, 9)))
    #
    #             un = ''.join(username)
    #
    #             if un in existing_un:
    #                 username = []
    #                 print('Username Taken')
    #             else:
    #                 break
    #
    #         un_file.write(un + '\n')
    #     un_file.close()

    def gen_user_name(self):

        username = []
        for i in range(8):
            username.append(random.choice(string.ascii_letters)) if i < 4 else username.append(str(random.randint(0, 9)))
        return ''.join(username)

    def gen_registration_data(self, num_users=1):

        for i in range(num_users):

            sex = random.choice(self.SEX)

            rdf = pd.DataFrame()
            rdf['username'] = [self.gen_user_name()]
            rdf['password'] = [uuid.uuid4()]
            rdf['blood_type'] = [random.choice(self.BLOOD_TYPES)]
            rdf['sex'] = [sex]
            rdf['name'] = [names.get_full_name(gender=sex)]
            rdf['age'] = [random.randint(10, 17)]
            rdf['DOB'] = [dt.date.today() - dt.timedelta(days= int(rdf['age'][0] * 365))]

            # print(rdf)

            filename = str(rdf['username'][0] + '.csv')
            rdf.to_csv(os.path.join('registration_data', filename), index=False)

    def gen_heart_rate(self):

        lower = self.MIN_HEARTRATE
        upper = self.MAX_HEARTRATE
        mu = self.MEAN_HEARTRATE
        sigma = self.STDEV_HEARTRATE
        N = self.MINUTES_IN_TIMEFRAME

        samples = scipy.stats.truncnorm.rvs((lower - mu) / sigma, (upper - mu) / sigma, loc=mu, scale=sigma, size=N)
        samples = [int(i) for i in samples]

        return samples

    def gen_steps(self):

        max_steps_per_min = [10, 25, 50] #low, medium, high activity levels
        al = random.choice(max_steps_per_min)
        steps = [0]
        for i in range(1, self.MINUTES_IN_TIMEFRAME):
            steps.append(random.randint(0, al) + steps[i-1])

        return steps

    def gen_distance(self, steps):
        miles_per_step = (1 / random.randint(1750, 2500)) #min 1750 steps == 1 mile | max 2500 steps == 1 mile
        return [i * miles_per_step for i in steps]

    def gen_active_calores(self, steps):
        return [i * self.CALORIES_PER_STEP for i in steps]



    # generates health data and exports each day recorded as a csv file
    # export goes to 'health_data/date_username_health.csv'
    def gen_health_data(self, usernames=None, num_days=1):

        for username in usernames:
            timestamp = dt.datetime.strptime(self.START_DATE + ' ' + self.START_TIME, "%Y-%m-%d %H:%M:%S")

            for day in range(num_days):
                time = []
                for minute in range(self.MINUTES_IN_TIMEFRAME):
                    time.append(timestamp)
                    timestamp += dt.timedelta(minutes=1)

                df = pd.DataFrame()
                df['timestamp'] = time
                df['heart_rate'] = self.gen_heart_rate()
                df['steps'] = self.gen_steps()
                df['distance(miles)'] = self.gen_distance(df['steps'])
                df['active_calories_burned'] = self.gen_active_calores(df['steps'])

                path = [str(timestamp).split(' ')[0], '_', username, '_', 'health.csv']
                df.to_csv(os.path.join('health_data', ''.join(path)), index=False)

                hr, mins, sec = int(self.START_TIME[:2]), int(self.START_TIME[3:5]), int(self.START_TIME[6:8])
                timestamp = timestamp.replace(hour=hr, minute=mins, second=sec)
                timestamp += dt.timedelta(days=1)


    # for simplicity can only play one game per day for now
    def gen_game_data(self):

        for file in os.listdir('health_data'):
            hdf = pd.read_csv(os.path.join('health_data', file))
            tvars = file.split('_')
            date, username = tvars[0], tvars[1]
            hdf['timestamp'] = pd.to_datetime(hdf['timestamp'])
            hdf = hdf.set_index('timestamp')
            # num_games = random.randint(self.MIN_GAMES_PER_DAY, self.MAX_GAMES_PER_DAY)
            # for i in range(num_games):
            game = random.choice(self.GAMES)
            mins_played = random.randint(self.MIN_GAMETIME, self.MAX_GAMETIME)

            start_time = dt.datetime.strptime(date + ' ' + self.START_TIME, "%Y-%m-%d %H:%M:%S") + \
                         dt.timedelta(minutes=random.randint(self.WAKE_PERIOD, self.MINUTES_IN_TIMEFRAME - self.MAX_GAMETIME))

            end_time = start_time + dt.timedelta(minutes=mins_played)
            start_time, end_time = start_time.strftime("%H:%M:%S"), end_time.strftime("%H:%M:%S")

            gdf = hdf.between_time(start_time, end_time)
            game_path = [date, '_', start_time.replace(':', '-'), '_', username, '_', game, '.csv']
            gdf.to_csv(os.path.join('game_data', ''.join(game_path)))











