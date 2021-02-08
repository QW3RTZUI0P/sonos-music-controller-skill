# Search Algorithms:
# used to call various search APIs 
import requests
# used to shuffle lists
import random

# search functions for Apple Music:
# function for searching a song on Apple Music
# returns a dict with the trackId, the trackName and the artistName
def search_song_applemusic(title="", interpreter=""):
    # this is the url that returns a json file with the search results from the iTunes Search API (https://affiliate.itunes.apple.com/resources/documentation/itunes-store-web-service-search-api/)
    urlInFunction = "https://itunes.apple.com/search?term=" + str(title) + "&country=de&media=music&entity=song&attribute=songTerm&artistTerm=" + str(interpreter)
    response = requests.get(urlInFunction)
    results_json = response.json()
    best_result = results_json["results"][0]
    result_dict = {"trackId": best_result["trackId"], "trackName": best_result["trackName"], "artistName": best_result["artistName"]}
    return result_dict

# function for searching an album on Apple Music
# returns a dict with the collectionId, the collectionName and the artistName
def search_album_applemusic(title="", interpreter=""):
    urlInFunction = "https://itunes.apple.com/search?term=" + str(title) + "&country=de&media=music&entity=album&attribute=albumTerm&artistTerm=" + str(interpreter)
    response = requests.get(urlInFunction)
    results_json = response.json()
    best_result = results_json["results"][0]
    result_dict = {"collectionId": best_result["collectionId"], "collectionName": best_result["collectionName"], "artistName": best_result["artistName"]}
    return result_dict

# function to search for songs of the specified interpreter on Apple Music
# returns a dict with the artistName and a list of trackIds
def search_songs_of_artist_applemusic(interpreter = ""):
    urlInFunction = "https://itunes.apple.com/search?term=" + str(interpreter) + " song&country=de&media=music&entity=song&limit=75&artistTerm=" + str(interpreter)
    response = requests.get(urlInFunction)
    results_json = response.json()
    song_list = []
    for current_entry in results_json["results"]:
        if "trackId" in current_entry:
            song_list.append(str(current_entry["trackId"]))

    random.shuffle(song_list)
    # value to check the given interpreter, sometimes it doesn't play songs from the specified interpreter
    # because the stt engine didn't understand the word
    real_interpreter = results_json["results"][0]["artistName"]
    result_dict = {"song_list": song_list, "interpreter": str(real_interpreter)}
    return result_dict


# function to search for albums of the specified interpreter on Apple Music
# currently not in use
def search_albums_of_artist_applemusic(interpreter = ""):
    urlInFunction = "https://itunes.apple.com/search?term=" + str(interpreter) + " album&country=de&media=music&entity=album&artistTerm=" + str(interpreter)
    response = requests.get(urlInFunction)
    resultsJson = response.json()
    wrong_album_list = resultsJson["results"]
    right_album_list = validate_entries_for(array = wrong_album_list, key = "artistName", value = str(interpreter))
    return right_album_list

# function for searching a playlist on Apple Music
# this is currently not working because the iTunes Search API doesn't support searching for playlists
def search_playlist_applemusic(title="", interpreter=""):
    return

# function for search the Essentials playlist of an artist on Apple Music
# this is currently not working because the iTunes Search API doesn't support searching for playlists


def search_essentials_applemusic(interpreter=""):
    return


# function that returns all dictionary items of the given array which have the given value as the value for the given key
def validate_entries_for(array = [], key = "", value = ""):
    results_list = []
    for entry in array:
        if key in entry:
            if entry[key].lower() == value:
                results_list.append(entry)

    return results_list


