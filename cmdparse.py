import pickle as pkl
import pandas as pd
with open("test.pkl", "rb") as f:
    object = pkl.load(f)

df = pd.DataFrame(object)
columns = list(df.columns.values)
filterable = {
    "Title": "str",
    "Desc": "str",
    "Uncopylocked": "bool",
    "HasVipServers": "bool",
    "MaxPlayers": "num",
    "LikeRatio": "num",
    "Likes": "num",
    "Dislikes": "num",
    "Visits": "num",
    "Favorites": "num",
    "AvatarType": "avatar",
    "CreatorID": "num",
    "CreatorName": "str",
    "CreatorType": "creatortype",
    "UniverseID": "num",
    "RootPlaceID": "num"
}
filtkeys = list(filterable.keys())
user = -1

def filter(df, key):
    if filterable[key] == "num":
        min = float(input("Min: "))
        max = float(input("Max (-1 for no max): "))
        if max > 0:
            df = df[df[key] < max]
        if min != 0:
            df = df[df[key] > min]
        return df
    
    if filterable[key] == "bool":
        keep = input("T/F?: ").upper()[0] == 'T'
        if keep:
            df = df[df[key]]
        else:
            df = df[not df[key]]
        return df

    if filterable[key] == "avatar":
        choice = ["R15", "R6", "Choice"]
        remove = int(input("Choose one to remove: 0: R15 | 1:R6 | 2: PlayerChoice"))
        df = df[not df[key].str.contains(choice[remove])]
        return df
    
    if filterable[key] == "creatortype":
        choice = ["User", "Group"]
        remove = int(input("Choose one to remove: 0: User | 1: Group "))
        df = df[not df[key].str.contains(choice[remove])]
        return df
    
    if filterable[key] == "str":
        search = input("What do you want to search for?: ")
        df = df[df[key].str.contains(search)]
        return df

def nav_format(df, num):
    data = df.to_dict('records')[num]
    return f"{num % 8 + 1} ({num}): {data["Title"]:30.30s} | {str(data["RootPlaceID"]):11s} | Visits: {str(data["Visits"]):11s}| Favorites: {str(data["Favorites"]):10s}| Ratio: {str(data["LikeRatio"])[:4]:4s}"

def nav_menu(df, start):
    print("\n-----")
    for i in range(8):
        if start + i - 1 > len(df.index): break
        print(nav_format(df, start + i))
    
    return input("9: Previous Page\n0: Next Page\nE: Exit \n")

def printMenu():
    print("00: Finish")
    for i in range(len(filtkeys),):
        print(f"{(i+1)//10}{(i+1)%10}: {filtkeys[i]}")
    print("------")

if __name__ == "__main__":
    while True:
        printMenu()
        user = int(input("Action: "))
        while user != 0:
            df = filter(df, filtkeys[user - 1])
            
            printMenu()
            user = int(input("Action: "))

        page = 0
        print("Results:", len(df.index))
        while str(user).lower() != "e":
            user = nav_menu(df, page)
            if user == "9":
                page = page - 8
                if page < 0: page = 0
            if user == "0":
                page = page + 8
                if page + 8 > len(df.index): page = len(df.index)-8

        print(df)