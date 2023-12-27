import tkinter as tk
import pandas as pd
import pickle as pkl
import robloxapi
import re
from PIL import ImageTk, Image
import requests
import io
from multiprocessing.dummy import Pool as ThreadPool
import time
import urllib
import webbrowser
import pyperclip

robloxapi.setCookie("")

WINDOW_FRAMES_X = 3
WINDOW_FRAMES_Y = 3

page = 0

CLRMAP = [["#111", "#222", "#111", "#222", "#111", "#222"],["#222", "#111", "#222", "#111", "#222"],["#111", "#222", "#111", "#222", "#111", "#222"],["#222", "#111", "#222", "#111", "#222"],["#111", "#222", "#111", "#222", "#111", "#222"]]

GAME_FRAME_SCALE = [170, 230]

FONT = {"heading": "Consolas 20 bold", 'gametitle': "Consolas 10", 'mini_details': "Consolas 10", 'desc_title': "Consolas 15 bold"}

BLACK = "#1A1A1A"

with open("test.pkl", "rb") as f:
    obj = pkl.load(f)

df = pd.DataFrame(obj)
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

def removeParens(text):
    text = re.sub("\(.*\)|\s-\s.*", '', text)
    text = re.sub("\[.*\]|\s-\s.*", '', text)
    text = re.sub("\{.*\}|\s-\s.*", '', text)
    try:
        while text[0] == " ":
            text = text[1:]
    except:
        print("huh")

    return text

def stringSearch(df, str):
    # special search operators:
    # "Cat" AND ("Dog" OR "Bird")
    # ^ Searches for things with dogs and cats, cats and birds, or cats/dogs/birds.
    str = str.split("OR")

def applySearch():
    global page
    global df
    page = 0
    df = pd.DataFrame(obj)

    visits_search.int_search()
    favorites_search.int_search()
    likes_search.int_search()
    dislikes_search.int_search()
    price_search.int_search()
    maxplr_search.int_search()
    title_search.str_search()
    desc_search.str_search()
    creator_search.str_search()
    created_search.date_search()
    updated_search.date_search()
    avatar_search.str_search()
    uncopylocked_search.bool_search()
    #voice_search

    df.reset_index(drop=True, inplace=True)

    updatePage()

def pageUp():
    global page
    games_per_page = WINDOW_FRAMES_X * WINDOW_FRAMES_Y
    page = page + games_per_page 
    if page > len(df.index):
        page = page - games_per_page 
    updatePage()

def pageDown():
    global page
    games_per_page = WINDOW_FRAMES_X * WINDOW_FRAMES_Y
    page = page - games_per_page
    if page < 0: page = 0

    updatePage()

def updatePage():
    global page
    games_per_page = WINDOW_FRAMES_X * WINDOW_FRAMES_Y
    
    threadarr = []

    uniIDs = []
    for y in range(WINDOW_FRAMES_X):
        for x in range(WINDOW_FRAMES_Y):
            try:
                uniIDs = uniIDs + [df.loc[y * WINDOW_FRAMES_X + x + page].to_dict()["UniverseID"]]
            except:
                continue

    imgs = robloxapi.multiGetIcons(uniIDs)

    for y in range(WINDOW_FRAMES_X):
        for x in range(WINDOW_FRAMES_Y):
            try:
                g_frames[y][x]["title"].config(text = 
                        removeParens(df.loc[y * WINDOW_FRAMES_X + x + page].to_dict()["Title"])[:21])
                g_frames[y][x]["favorites"].config(text = 
                                "Favorites: " + str(df.loc[y * WINDOW_FRAMES_X + x + page].to_dict()["Favorites"]))
                g_frames[y][x]["visits"].config(text = 
                                "Visits: " + str(df.loc[y * WINDOW_FRAMES_X + x + page].to_dict()["Visits"]))

                g_frames[y][x]["img"] = ImageTk.PhotoImage(imgs[y * WINDOW_FRAMES_X + x])
                g_frames[y][x]["img_label"].config(image = g_frames[y][x]["img"])
            except:
                resetGame(y, x)

    page_title.config(text=f"Page {page//(games_per_page) + 1}/{len(df.index)//games_per_page + 2}")

def getImage(url):
    u = requests.get(url)
    img = Image.open(io.BytesIO(u.content))

    return img

def playGame():
    global currentgame
    webbrowser.open('roblox://placeId=' + str(currentgame))

def showDetails(x, y):
    global currentgame
    desc_img = g_frames[x][y]["img"]
    desc_icon.config(image=desc_img)

    game_details = df.loc[x * WINDOW_FRAMES_X + y + page].to_dict()

    desc_title.config(text=game_details["Title"])
    desc_desc.config(text=game_details["Desc"])
    currentgame = game_details["RootPlaceID"]

def resetGame(x, y):
    g_frames[x][y]["img"] = tk.PhotoImage(file='no_image.png')
    g_frames[x][y]["img_label"].config(image=g_frames[x][y]["img"])

    g_frames[x][y]["title"].config(text="N/A")
    g_frames[x][y]["favorites"].config(text="Favorites: 0")
    g_frames[x][y]["visits"].config(text="Visits: 0")

    g_frames[x][y]["frame"].pack(side=tk.LEFT)

window = tk.Tk()
window.resizable(width=False,height=False)



# ------------------------------
# -------- GAME DETAILS --------
# ------------------------------

desc_frame = tk.Frame(window, width=GAME_FRAME_SCALE[0]*2, height=GAME_FRAME_SCALE[1]*WINDOW_FRAMES_X, bg=BLACK, border=5)
desc_frame.pack_propagate(0)
desc_frame.pack(side=tk.RIGHT)

desc_img = tk.PhotoImage(file="no_image.png")
desc_icon = tk.Label(desc_frame, image = desc_img, background=BLACK)
desc_icon.pack(side=tk.TOP)

desc_title = tk.Label(desc_frame, font=FONT['desc_title'], fg="white", bg=BLACK, wraplength=GAME_FRAME_SCALE[0]*2 - 10)
desc_title.pack(side=tk.TOP)

desc_desc = tk.Label(desc_frame, font=FONT['gametitle'], fg="white", bg=BLACK, wraplength=GAME_FRAME_SCALE[0]*2 - 10, height=29, justify='left', anchor="n")
desc_desc.pack(side=tk.TOP, anchor=tk.N)

currentgame = 0

desc_buttons = tk.Frame(desc_frame, width=GAME_FRAME_SCALE[0]*2 - 10, height=20, bg=BLACK)
desc_buttons.pack(side=tk.BOTTOM, anchor=tk.S)

desc_play = tk.Button(desc_buttons, font=FONT['gametitle'], fg="white", bg="#131", text="Play", command=playGame)


# ------------------------------
# ------ SEARCHING THINGS ------
# ------------------------------

search_frame = tk.Frame(window, width=GAME_FRAME_SCALE[0]*2, height=GAME_FRAME_SCALE[1]*WINDOW_FRAMES_X, bg=BLACK, border=5)
search_frame.pack_propagate(0)
search_frame.pack(side=tk.LEFT)

search_title = tk.Label(search_frame, text="Filter", font=FONT["heading"], bg=BLACK, fg="white")
search_title.pack(side=tk.TOP)

class search_input:
    global search_frame

    def __init__(self, parent, text, data=""):
        self.input_frame = tk.Frame(parent, width = GAME_FRAME_SCALE[0]*2 - 10, height=30,bg=BLACK)
        self.input_frame.pack(side=tk.TOP, anchor=tk.N)
        self.input_frame.pack_propagate(0)

        self.input_input = tk.Entry(self.input_frame, width = 20,bg=BLACK, fg="white", font=FONT["gametitle"])
        self
        self.input_input.pack(side=tk.RIGHT, anchor=tk.W)

        self.input_title = tk.Label(self.input_frame, font=FONT["gametitle"], text=text,bg=BLACK, fg="white")
        self.input_title.pack(side=tk.LEFT, anchor=tk.E)

        self.data = data
    
    def get_input(self):
        return self.input_input.get()
    
    def int_search(self):
        if self.get_input() == "": return
        global df
        tmp = self.get_input().split(" ")
        for i in range(len(tmp)):
            tmp[i] = int(tmp[i])

        if tmp[1] >= 0:
            df = df[df[self.data] <= tmp[1]]
        else:
            df = df[df[self.data] >= tmp[0]]

    def date_search(self):
        if self.get_input() == "": return
        global df
        tmp = self.get_input().split(" ")
        # after first date
        df = df[df[self.data] >= tmp[0]]
        # before last date
        df = df[df[self.data] <= tmp[1]]
    
    def str_search(self):
        if self.get_input() == "": return 
        tmp = self.get_input()
        global df
        if tmp.find("\\c") == 0:
            df = df[df[self.data].str.lower().str.contains(self.get_input())]
        else:
            df = df[df[self.data].str.contains(self.get_input())]
        
    def avatar_search(self):
        if self.get_input() == "": return 
        global df
        tmp = self.get_input().lower()

        if tmp.find("6") > -1:
            print("r6")
            df = df[df[self.data].str.contains("R6")]
        if tmp.find("15") > -1:
            print("r15")
            df = df[df[self.data].str.contains("R15")]
        else:
            print("choice")
            df = df[df[self.data].str.contains("Choice")]

        print(df)
    
    def bool_search(self):
        if self.get_input() == "": return
        global df
        tmp = self.get_input().lower()[0]
        if tmp == "t":
            df = df[df[self.data]]
            print(df)
        else:
            df = df[not df[self.data]]

visits_search = search_input(search_frame, "Visits (int)", "Visits")
favorites_search = search_input(search_frame, "Favorites (int)", "Favorites")
likes_search = search_input(search_frame, "Likes (int)", "Likes")
dislikes_search = search_input(search_frame, "Dislikes (int)", "Dislikes")
price_search = search_input(search_frame, "Price (int)", "Price")
maxplr_search = search_input(search_frame, "Max Players (int)", "MaxPlayers")
title_search = search_input(search_frame, "Title (str)", "Title")
desc_search = search_input(search_frame, "Description (str)", "Desc")
creator_search = search_input(search_frame, "Creator (str)", "CreatorName")
created_search = search_input(search_frame, "Date Created (date)", "DateCreated")
updated_search = search_input(search_frame, "Date Updated (date)", "LastUpdated")
avatar_search = search_input(search_frame, "Avatar (R6/R15/Any)", "AvatarType")
uncopylocked_search = search_input(search_frame, "Uncopylocked (T/F)", "Uncopylocked")
voice_search = search_input(search_frame, "Voice Chat (T/F)", "VoiceChatEnabled")
voice_search = search_input(search_frame, "Starred (T/F)")

# search button
search_button = tk.Button(search_frame, text="Search", bg="#220", fg="#FFA", command=applySearch)
search_button.pack(side=tk.TOP)

# ---- PAGINATION
page_frame = tk.Frame(search_frame, width=GAME_FRAME_SCALE[0]*2 - 10, height=40, bg=BLACK)
page_frame.pack_propagate(0)
page_frame.pack(side=tk.BOTTOM)

page_button_frame = tk.Frame(page_frame, width=GAME_FRAME_SCALE[0]*2 - 10, height=20, bg=BLACK)
page_button_frame.pack_propagate(0)
page_button_frame.pack(side=tk.BOTTOM)

next_page = tk.Button(page_button_frame, width=22, height=1, text="-->", bg=BLACK, fg="white", command=pageUp)
next_page.pack(side=tk.RIGHT)

prev_page = tk.Button(page_button_frame, width=22, height=1, text="<--", bg=BLACK, fg="white", command=pageDown)
prev_page.pack(side=tk.LEFT)

page_title = tk.Label(page_frame, text="Page 0/0", bg=BLACK, fg="white")
page_title.pack(side=tk.BOTTOM)

# ------------------------------
# -------- DISPLAY GAME --------
# ------------------------------

g_frames = []
game_rows = []
g_events = []
for x in range(WINDOW_FRAMES_X):
    game_rows = game_rows + [tk.Frame(window)]
    g_frames = g_frames + [[]]
    for y in range(WINDOW_FRAMES_Y):
        g_frames[x] = g_frames[x] + [{"frame": tk.Frame(game_rows[x], height=GAME_FRAME_SCALE[1], width=GAME_FRAME_SCALE[0], bg=CLRMAP[x][y], borderwidth=10)}]
        g_frames[x][y]["frame"].pack_propagate(0)

        g_frames[x][y]["img"] = tk.PhotoImage(file='no_image.png')
        g_frames[x][y]["img_label"] = tk.Label(g_frames[x][y]["frame"], image=g_frames[x][y]["img"], bg=CLRMAP[x][y], fg="white")
        g_frames[x][y]["img_label"].bind("<Button-1>", lambda e,x=x,y=y: showDetails(x, y))
        g_frames[x][y]["img_label"].pack(side=tk.TOP)

        g_frames[x][y]["title"] = tk.Label(g_frames[x][y]["frame"], text="N/A", bg=CLRMAP[x][y], fg="white", font=FONT['mini_details'])
        g_frames[x][y]["title"].pack(side=tk.TOP, anchor=tk.W)
        g_frames[x][y]["favorites"] = tk.Label(g_frames[x][y]["frame"], text="Favorites: 0", bg=CLRMAP[x][y], fg="white", font=FONT['mini_details'])
        g_frames[x][y]["favorites"].pack(side=tk.TOP, anchor=tk.W)
        g_frames[x][y]["visits"] = tk.Label(g_frames[x][y]["frame"], text="Visits: 0", bg=CLRMAP[x][y], fg="white", font=FONT['mini_details'])
        g_frames[x][y]["visits"].pack(side=tk.TOP, anchor=tk.W)

        g_frames[x][y]["frame"].pack(side=tk.LEFT)
    
    game_rows[x].pack(side=tk.TOP)



window.mainloop()