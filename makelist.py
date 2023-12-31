import robloxapi
import dask.dataframe as dd
import pandas as pd
import pprint
import random
import time
import pickle

robloxapi.setCookie(input("gimme cookie lol: "))

# number of games to grab at a time. techincally the total is infinite
MAX_GAMES_TOTAL = 100

# number of games to process at a time, don't exceed 100 probably
MAX_GAMES_BATCH = 100

# number of friends to use based on people. more friends = different favorites, but less unknown games from creators
MAX_FRIENDS = 15

last_time = int(time.time())

# format for dataframe
try:
    with open("test.pkl", "rb") as f:
        object = pickle.load(f)
    df = pd.DataFrame(object)
except:
    df = pd.DataFrame({ 'UniverseID': [],
                        'AgeRating': [],
                        'AvatarType': [],
                        'CreatorID': [],
                        'CreatorName': [],
                        'CreatorType': [],
                        'DateCreated': [],
                        'Desc': [],
                        'Dislikes': [],
                        'Favorites': [],
                        'HasVipServers': [],
                        'HasCustomIcon': [],
                        #'IsPlayable': [], - redundant
                        'LastUpdated': [],
                        'LikeRatio': [],
                        'Likes': [],
                        'MaxPlayers': [],
                        'Price': [],
                        'RootPlaceID': [],
                        'Title': [],
                        'Uncopylocked': [],
                        'Visits': [],
                        #'VoiceEnabled': [], 
                        })

last_count = len(df.index)

print("---------")
games = []
player_list = [856356, 31969401, 221844, 499749, 554744114, 614603, 1221485, 6081066, 33322713, 417443]

count = 0

while True:
    try:
        print(player_list)
        while len(games) < MAX_GAMES_TOTAL:
            try:
                print("currently looking at:")
                print(len(games))
                current_plr = player_list[random.randrange(0, len(player_list))]
                current_favs = robloxapi.getUserFavorites(current_plr)

                new_creators = robloxapi.gameListToCreatorList(current_favs)    
                
                friends = robloxapi.getFriends(current_plr, MAX_FRIENDS)

                player_list = list(set(player_list + new_creators + friends))
                games = games + current_favs + robloxapi.getUserCreated(current_plr)

            except BaseException as e:
                print("probably timed out")
                print(e)
                time.sleep(3)
            
        while len(games) > 0:
            games = list(set(games))
            for i in range(len(games)//MAX_GAMES_BATCH + 1):
                print(i, " / ", (len(games) // MAX_GAMES_BATCH) + 1, "games searching")
                partial_games = games[MAX_GAMES_BATCH * i: MAX_GAMES_BATCH * i + MAX_GAMES_BATCH]
                count = count + 1
            
                gameData = robloxapi.multiUniverseToList(partial_games)
                if gameData == -1: continue # if game is unplayable, don't add it to the list

                df2 = pd.DataFrame(gameData, columns=df.columns)
                df = pd.concat([df, df2])

            games = []

            new_plr = []
            for plr in range(10):
                new_plr = new_plr + [player_list[random.randrange(0, len(player_list))]]
            player_list = new_plr

            df = df.drop_duplicates(subset=["UniverseID"], keep='last')

            df.to_pickle("test.pkl")

            print("\n\n\n\n\n---------")
            print("\nBATCH DONE!\n")
            print("Current game count:", len(df.index))
            print("New games:", len(df.index) - last_count)
            last_count = len(df.index)

            print("Time taken:", int(time.time() - last_time), "seconds")
            last_time = time.time()

            print("\n---------")
    except BaseException as e:
        print("frick")
        print(e)
        time.sleep(10)