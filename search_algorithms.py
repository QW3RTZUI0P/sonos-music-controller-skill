# Search Algorithms:
# used to call various search APIs 
import requests
import urllib.parse
# used to shuffle lists
import random
from .static_values import *

# general functions (to make __init__.py less complicated when using different music services)
def search_song(title = "", artist = "", country_code = "", service = "", self = None):
    if service == "spotify":
        return search_song_spotify(title = title, artist = artist, country_code = country_code)
    elif service == "apple_music":
        return search_song_applemusic(title = title, artist = artist, country_code = country_code, self = self)

def search_album(title = "", artist = "", country_code = "", service = ""):
    if service == "spotify":
        return search_album_spotify(title = title, artist = artist, country_code = country_code)
    if service == "apple_music":
        return search_album_applemusic(title = title, artist = artist, country_code = country_code)

def search_songs_of_artist(artist = "", country_code = "", service = ""):
    if service == "spotify":
        return search_songs_of_artist_spotify(artist = artist, country_code = country_code)

    elif service == "apple_music":
        return search_songs_of_artist_applemusic(artist = artist, country_code = country_code)

# Apple Music:
# returns a dict with the title and the artist of the song with the given id on Apple Music
def lookup_id_applemusic(music_service_id = "", country_code = "us"):
    url_in_function = applemusic_api_url + "lookup?id=" + str(music_service_id) + "&country=" + str(country_code)
    response = requests.get(url = applemusic_api_url + "lookup", params = {"id": str(music_service_id), "country": str(country_code)})
    results_json = response.json()
    best_result = results_json.get("results")[0]
    result_dict = {"title": best_result.get("trackName"), "artist": best_result.get("artistName")}
    return result_dict

# function for searching a song on Apple Music
# returns a dict with the trackId, the trackName and the artistName
def search_song_applemusic(title="", artist="", country_code = "us", self = None):
    # replaces every space with + (important for the API to work properly)
    title_in_url = str(title).replace(" ", "+")
    artist_in_url = str(artist).replace(" ", "+")
    title_and_artist = title_in_url + "+" + artist_in_url
    # the parameters that will be passed on to the iTunes Search API
    url_params = {}
    if artist == None:
        url_params = {"term": title_in_url, "media": "music", "country": str(country_code), "entity": "song", "attribute": "songTerm",  "limit":"10"}
    else:
        url_params = {"term": title_in_url, "media": "music", "country": str(country_code), "entity": "song", "attribute": "songTerm", "limit": "10"}

    url_params_string = urllib.parse.urlencode(url_params, safe='+äöü')
    response = requests.get(url = applemusic_api_search, params = url_params_string)
    results_json = response.json().get("results")
    best_result = None
    # makes sure that the song is from the specified artist
    if artist == None:
        best_result = results.json[0]
    else:
        for current_result in results_json:
            if current_result.get("artistName").lower() == str(artist):
                best_result = current_result
                break
        # TODO: throw custom error: Mycroft couldn't find any songs with the specified name by the specified artist
        if best_result == None:
            best_result = results_json[0]

    result_dict = {"trackId": best_result.get("trackId"), "trackName": best_result.get("trackName"), "artistName": best_result.get("artistName")}
    return result_dict

# function for searching an album on Apple Music
# returns a dict with the songIds of the tracks in the album, the collectionName and the artistName
def search_album_applemusic(title="", artist="", country_code = "us"):
    # replaces every space with + (important for the API to work properly)
    title_in_url = str(title).replace(" ", "+")
    artist_in_url = str(artist).replace(" ", "+")

    url_album = ""
    url_songs = ""
    url_album_params = {}
    url_songs_params = {}
    if artist == None:
        url_album_params = {"term": title_in_url, "media": "music", "country": str(country_code), "entity": "album", "albumTerm": title_in_url, "attribute": "albumTerm", "limit": 1}
        url_songs_params = {"term": title_in_url, "media": "music", "country": str(country_code), "entity": "song", "albumTerm": title_in_url}

    else: 
        url_album_params = {"term": title_in_url, "media": "music", "country": str(country_code), "entity": "album", "albumTerm": title_in_url, "artistTerm": artist_in_url, "attribute": "albumTerm", "limit": "1"}
        url_songs_params = {"term": title_in_url + " " + artist_in_url, "media": "music", "country": str(country_code), "entity": "song", "albumTerm": title_in_url, "artistTerm": artist_in_url}


    url_album_params_string = urllib.parse.urlencode(url_album_params, safe = '+äöü')
    url_songs_params_string = urllib.parse.urlencode(url_songs_params, safe='+äöü')
    response_album = requests.get(url = applemusic_api_search, params = url_album_params_string)
    response_songs = requests.get(url = applemusic_api_search, params = url_songs_params_string)
    results_album = response_album.json()
    results_songs = response_songs.json()
    best_album_result = results_album.get("results")[0]
    song_id_list = []
    
    for index in range(0, best_album_result.get("trackCount")):
        current_id = results_songs.get("results")[index].get("trackId")
        song_id_list.append(current_id)

    result_dict = {"songIds": song_id_list, "collectionName": best_album_result.get("collectionName"), "artistName": best_album_result.get("artistName")}
    return result_dict

# function to search for songs of the specified artist on Apple Music
# returns a dict with the artistName and a list of trackIds
def search_songs_of_artist_applemusic(artist = "", country_code = "us"):
    # replaces every space with + (important for the API to work properly)
    artist_in_url = str(artist).replace(" ", "+") 
    url_params = {"term": artist_in_url, "media": "music", "country": str(country_code), "entity": "song", "attribute": "artistTerm", "limit": "100"}
    url_params_string = urllib.parse.urlencode(url_params, safe='+äöü')
    response = requests.get(url = applemusic_api_search, params = url_params_string)
    results_json = response.json()
    song_id_list = []
    for current_entry in results_json.get("results"):
        if "trackId" in current_entry:
            song_id_list.append(str(current_entry.get("trackId")))

    # randomly chooses 30 songs out of the 100 returned by the api (to not play the same 30 songs all the time)
    final_song_id_list = random.sample(song_id_list, 30)
    result_dict = {"song_list": final_song_id_list, "artist": str(artist)}
    return result_dict


# function to search for albums of the specified artist on Apple Music
# currently not in use
def search_albums_of_artist_applemusic(artist = ""):
    urlInFunction = applemusic_api_url + "search?term=" + str(artist) + " album&country=de&media=music&entity=album&artistTerm=" + str(artist)
    response = requests.get(urlInFunction)
    resultsJson = response.json()
    wrong_album_list = resultsJson["results"]
    right_album_list = validate_entries_for(array = wrong_album_list, key = "artistName", value = str(artist))
    return right_album_list

# function for searching a playlist on Apple Music
# this is currently not working because the iTunes Search API doesn't support searching for playlists
def search_playlist_applemusic(title="", artist=""):
    pass

# function for search the Essentials playlist of an artist on Apple Music
# this is currently not working because the iTunes Search API doesn't support searching for playlists
def search_essentials_applemusic(artist=""):
    pass


# function that returns all dictionary items of the given array which have the given value as the value for the given key
# currently not in use
def validate_entries_for(array = [], key = "", value = ""):
    results_list = []
    for entry in array:
        if key in entry:
            if entry[key].lower() == value:
                results_list.append(entry)

    return results_list



# Spotify:
# returns the public Spotify access token currently available on open.spotify.com via web scraping
# this is a very unstable and ugly piece of code, but for now it'll do (someone with a little bit web scraping experience could surely do a better job here ;))
def get_spotify_access_token():
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36"}
    response = requests.get(spotify_access_token_url, headers = headers)
    # finds the location where the accessToken is
    index = response.text.find('"accessToken')
    liste = response.text[index:index+300]
    part01 = liste.split('":"')[1]
    # gets the access token
    token = part01.split('","')[0]
    return token

# returns a dict with the trackId, the trackName and the artistName
def search_song_spotify(title = "", artist = "", country_code = ""):
    url_params = {}
    if artist == None:
        url_params = {"q": str(title), "type": "track", "limit": "5"}
    else: 
        url_params = {"q": str(title) + " " + str(artist), "type": "track", "limit": "5"}
        
    token = get_spotify_access_token()
    headers = {"Authorization": "Bearer " + token}
    response = requests.get(url = spotify_api_url, params = url_params, headers = headers)
    json = response.json()
    best_result = json.get("tracks").get("items")[0]
    trackId = best_result.get("uri").split(":")[2]
    result_dict = {"trackId": trackId, "trackName": best_result.get("name"), "artistName": best_result.get("artists")[0].get("name")}
    return result_dict

# returns a dict with the songIds of the tracks in the album, the collectionName and the artistName
def search_album_spotify(title = "", artist = "", country_code = ""):
    url = ""
    url_params = {}
    if artist == None:
        url_params = {"q": str(title), "type": "album"}
    else:
        url_params = {"q": str(title) + " " + str(artist), "type": "album"}
    token = get_spotify_access_token()
    headers = {"Authorization": "Bearer " + token}

    response = requests.get(url = spotify_api_url, params = params, headers = headers)
    json = response.json()
    results = json.get("tracks").get("items")
    first_result = results[0]
    track_count = first_result.get("album").get("total_tracks")
    song_id_list = []
    for index in range(0, track_count):
        song_id_list.append(results[index].get("uri").split(":")[2])

    result_dict = {"songIds": song_id_list, "collectionName": first_result.get("album").get("name"), "artistName": first_result.get("artists")[0].get("name")}
    return result_dict


# returns a dict with the list of songIds and the artistName
def search_songs_of_artist_spotify(artist = "", country_code = ""):
    url_params = {"q": str(artist), "type": "track", "limit": "30"}
    token = get_spotify_access_token()
    headers = {"Authorization": "Bearer " + token}
    response = requests.get(url = spotify_api_url, params = url_params, headers = headers)
    json = response.json()
    results = json.get("tracks").get("items")
    song_id_list = []
    for index in range(0, 30):
        song_id_list.append(results[index].get("uri").split(":")[2])

    result_dict = {"song_list": song_id_list, "artist": str(results[0].get("artists")[0].get("name"))}
    return result_dict
