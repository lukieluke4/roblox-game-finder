import requests
import time
import pprint
import random
from multiprocessing.dummy import Pool as ThreadPool
from PIL import Image, ImageChops
import io
import os

cookies = {}
api_session = ''

defaulticons = []
for file in os.listdir("defaulticons"):
    filename = os.fsdecode(file)
    defaulticons = defaulticons + [Image.open("defaulticons/" + filename).resize((10, 10), resample=Image.Resampling.NEAREST)]

def setCookie(cookie):
    global api_session

    session = requests.session()
    cookies = {".ROBLOSECURITY": cookie}
    requests.utils.add_dict_to_cookiejar(session.cookies, cookies)

    Header = session.post('https://catalog.roblox.com/')
    session.headers['X-CSRF-TOKEN'] = Header.headers['X-CSRF-TOKEN']
    session.headers["Origin"] = "https://www.roblox.com"
    session.headers["Referer"] = "https://www.roblox.com/"
     
    api_session = session

def getPlaceDetails(placeID):
    return api_session.get("https://games.roblox.com/v1/games/multiget-place-details?placeIds=" + str(placeID)).json()[0]

def multiGetPlaceDetails(placeList):
    place_strs = []
    result = []

    # max 20 per request
    for i in range(len(placeList)):
        if (i % 20 == 0):
            place_strs = place_strs + ["https://games.roblox.com/v1/games/multiget-place-details?"]
        place_strs[-1] = place_strs[-1] + "&placeIds=" + str(placeList[i])

    for place_str in place_strs:
        result = result + api_session.get(place_str).json()


    return result

def getUniverseDetails(uniID):
    return api_session.get("https://games.roblox.com/v1/games?universeIds=" + str(uniID)).json()['data'][0]

def getFriends(plr, max=200):
    data = api_session.get(f"https://friends.roblox.com/v1/users/{plr}/friends").json()["data"]
    result = []
    for i in data:
        result = result + [i["id"]]
    
    if len(result) > max:
        friends = []
        for i in range(max):
            friends = friends + [result[random.randint(0,len(result))]]
        result = friends
    
    return result

# returns a list of dictionaries
def multiGetUniverseDetails(uniList):
    if uniList == []: return
    uni_str = str(uniList[0])
    uniList = uniList[1:]
    for uni in uniList:
        uni_str = uni_str + "," + str(uni)
    return api_session.get("https://games.roblox.com/v1/games?universeIds=" + uni_str).json()['data']

def getUniverseVotes(uniID):
    return api_session.get(f"https://games.roblox.com/v1/games/{uniID}/votes").json()

def multiGetUniverseVotes(uniList):
    uni_str = str(uniList[0])
    uniList = uniList[1:]
    for uni in uniList:
        uni_str = uni_str + "," + str(uni)
    return api_session.get("https://games.roblox.com/v1/games/votes?universeIds=" + uni_str).json()['data']

def multiGetAgeRating(uniList):
    result = []
    for uniID in uniList:
        try:
            tmp = api_session.post("https://apis.roblox.com/experience-guidelines-api/experience-guidelines/get-age-recommendation", json= {"universeId": uniID}).json()
            tmp = tmp["ageRecommendationDetails"]["summary"]
            
            # no idea why i have to do this.
            result = result + [list(tmp.values())[0]["minimumAge"]]
        except:
            result = result + [0]

    return result
    
def multiGetVoiceEnabled(uniList):
    result = []
    for uniID in uniList:
        try:
            tmp = api_session.post("https://voice.roblox.com/v1/settings/verify/show-age-verification-overlay/" + str(uniID)).json()
            result = result + [tmp["universePlaceVoiceEnabledSettings"]["isUniverseEnabledForVoice"]]
        except:
            result = result + [False]
    return result

def getImage(url):
    u = requests.get(url)
    img = Image.open(io.BytesIO(u.content))

    return img

def multiGetIcons(uniList, size=150):
    uni_str = ''
    parsed = [[]]
    result = []
    imgs = []

    for i in uniList:
        uni_str = uni_str + str(i) + ","
    uni_str = uni_str[:-1]
    #rint(f"https://thumbnails.roblox.com/v1/games/icons?universeIds={uni_str}&returnPolicy=PlaceHolder&size={size}x{size}&format=Jpeg&isCircular=false")
    result = api_session.get(f"https://thumbnails.roblox.com/v1/games/icons?universeIds={uni_str}&returnPolicy=PlaceHolder&size={size}x{size}&format=Jpeg&isCircular=false").json()
    result = result["data"]
    for i in result: # dont get more than 10 at the same time, avoids rate limiting
        if len(parsed[-1]) > 10:
            parsed = parsed + []
        parsed[-1] = parsed[-1] + [i["imageUrl"]]

    for urls in parsed:
        pool = ThreadPool(len(urls))
        imgs = imgs + pool.map(getImage, urls)

    pool.close()
    pool.join()

    return imgs

def are_images_equal(img1, img2):
    equal_size = img1.height == img2.height and img1.width == img2.width

    if img1.mode == img2.mode == "RGBA":
        img1_alphas = [pixel[3] for pixel in img1.getdata()]
        img2_alphas = [pixel[3] for pixel in img2.getdata()]
        equal_alphas = img1_alphas == img2_alphas
    else:
        equal_alphas = True

    equal_content = not ImageChops.difference(
        img1.convert("RGB"), img2.convert("RGB")
    ).getbbox()

    return equal_size and equal_alphas and equal_content

def multiGetIsCustomIcon(uniList):
    result = []
    icons = multiGetIcons(uniList, 150)

    for icon in icons:
        icon = icon.resize((10, 10), resample=Image.Resampling.NEAREST)
        
        tmp = True
        for default in defaulticons:
            if not are_images_equal(icon, default):
                continue
            else:
                tmp = False
                break
        
        result = result + [tmp]
    
    return result    

def multiUniverseToList(uniList):
    if uniList == []: return
    final_result = []
    details = multiGetUniverseDetails(uniList)
    votes = multiGetUniverseVotes(uniList)
    is_custom_icon = multiGetIsCustomIcon(uniList)

    age_rating = multiGetAgeRating(uniList)

    placelist = []
    root_details = []
    for uni in details:
        placelist = placelist + [uni["rootPlaceId"]]

    root_details = multiGetPlaceDetails(placelist)
    
    for i in range(len(uniList)):
        #try:
        
        if not root_details[i]["isPlayable"]: continue
        result = {}
        # UniverseID
        result["UniverseID"] = uniList[i]
        # Avatartype
        result["AvatarType"] = details[i]["universeAvatarType"]
        # CreatorID
        result["CreatorID"] = details[i]["creator"]["id"]
        # CreatorName
        result["CreatorName"] = details[i]["creator"]["name"]
        # CreatorType
        result["CreatorType"] = details[i]["creator"]["type"]
        # DateCreated
        result["DateCreated"] = details[i]["created"]
        # Desc
        result["Desc"] = details[i]["sourceDescription"]
        # Dislikes
        try:
            result["Dislikes"] = votes[i]["downVotes"]

        except:
            result["Dislikes"] = -1

        # Favorites
        result["Favorites"] = details[i]["favoritedCount"]
        # HasVipServers
        result["HasVipServers"] = details[i]["createVipServersAllowed"]
        # IsPlayable
        result["isPlayable"] = root_details[i]["isPlayable"]
        # LastUpdated
        result["LastUpdated"] = details[i]["updated"]
        # LikeRatio
        try:
            result["LikeRatio"] = votes[i]["upVotes"] / (votes[i]["upVotes"] + votes[i]["downVotes"])
        except:
            result["LikeRatio"] = -1
        # Likes
        try:
            result["Likes"] = votes[i]["upVotes"]
        except:
            result["Likes"] = -1
        # MaxPlayers
        result["MaxPlayers"] = details[i]["maxPlayers"]
        # Price
        try:
            result["Price"] = int(details[i]["price"])
        except:
            result["Price"] = 0
        
        # RootPlaceID
        result["RootPlaceID"] = details[i]["rootPlaceId"]
        # Title
        result["Title"] = details[i]["sourceName"]
        # Uncopylocked
        result["Uncopylocked"] = details[i]["copyingAllowed"]
        # Visits
        result["Visits"] = details[i]["visits"]

        #result["AgeRating"] = age_rating[i]
        #result["VoiceEnabled"] = voice_enabled[i]
        result["HasCustomIcon"] = is_custom_icon[i]

        final_result = final_result + [result]
        #except BaseException as e:
         #   print(e)
    return final_result

def getUserFavorites(userID):
    favorites = api_session.get(f"https://games.roblox.com/v2/users/{userID}/favorite/games?accessFilter=2&limit=50&sortOrder=Asc").json()
    favorites = favorites["data"]

    ids = []
    for i in favorites:
        ids = ids + [i["id"]]
    return ids

def getUserCreated(userID):
    created = ''
    try:
        created = api_session.get(f"https://games.roblox.com/v2/users/{userID}/games?accessFilter=2&limit=50&sortOrder=Asc").json()
        created = created['data']
    except BaseException as e:
        print(e)
    ids = []
    for i in created:
        ids = ids + [i["id"]]
    return ids

def getUserGames(userID):
    return getUserCreated(userID) + getUserFavorites(userID)

def gameListToCreatorList(list):
    creators = []
    details = multiGetUniverseDetails(list)
    for uni in details:
        creator = uni["creator"]
        if creator["type"] == "Group": continue
        creators = creators + [creator["id"]]

    return creators
