from mycroft import MycroftSkill, intent_handler
# to shuffle lists
import random
# to call various search APIs and to communicate to the Sonos Node JS Server
import requests
# to get the identifiers for all types of music from the iTunes Search API
import itunes

class SonosMusicController(MycroftSkill):

    # important values for the skill to function
    # can be edited in the normal Mycroft Skill settings on home.mycroft.ai
    sonos_server_ip = ""
    room = ""
    url = ""

    def __init__(self):
        MycroftSkill.__init__(self)

    def initialize(self):
        SonosMusicController.sonos_server_ip = self.settings.get("sonos_server_ip")
        SonosMusicController.room = self.settings.get("room")
        # putting the values in str() is necessary
        SonosMusicController.url = "http://" + str(SonosMusicController.sonos_server_ip) + ":5005/" + str(SonosMusicController.room) + "/" 

        # connects with the mycroft-playback-control messagebus
        self.add_event("mycroft.audio.service.pause", self.pause)
        self.add_event("mycroft.audio.service.play", self.resume)
        self.add_event("mycroft.audio.service.playresume", self.resume)
        self.add_event("mycroft.audio.service.resume", self.resume)
        self.add_event("mycroft.audio.service.next", self.next_song)
        self.add_event("mycroft.audio.service.prev", self.previous_song)


    # general function to call the sonos api
    def sonos_api(action = ""):
        requests.get(SonosMusicController.url + str(action))

    # function to call the sonos api and to clear the queue
    def sonos_api_clear_queue(action = ""):
        requests.get(SonosMusicController.url + "clearqueue")
        requests.get(SonosMusicController.url + str(action))

    # function to clear the queue
    def clear_queue():
        requests.get(SonosMusicController.url + "clearqueue")

    # General controls for Sonos
    # controlled via the mycroft-playback-control messagebus
    def pause(self, message):
        SonosMusicController.sonos_api("pause")
    # controlled via the mycroft-playback-control messagebus
    def resume(self, message):
        self.speak_dialog('resume.dialog')
        SonosMusicController.sonos_api("play")
    def next_song(self, message):
        SonosMusicController.sonos_api("next")
    def previous_song(self, message):
        SonosMusicController.sonos_api("previous")
        
    @intent_handler('louder.intent')
    def louder(self, message):
        SonosMusicController.sonos_api("volume/+10")

    @intent_handler('quieter.intent')
    def quieter(self, message):
        SonosMusicController.sonos_api("volume/-10")


    # playing music on Sonos
    @intent_handler("play.song.intent")
    def play_song(self, message):
        trackId = search_song_applemusic(title = message.data.get('title'), interpreter = message.data.get('interpreter'))
        self.log.info(SonosMusicController.url + "applemusic/now/song:" + str(trackId))
        SonosMusicController.sonos_api_clear_queue(action = "applemusic/now/song:" + str(trackId))

    @intent_handler("play.album.intent")
    def play_album(self, message):
        collectionId = search_album_applemusic(title = message.data.get("title"), interpreter = message.data.get("interpreter"))
        self.log.info(collectionId)
        SonosMusicController.sonos_api_clear_queue(action = "applemusic/now/album:" + str(collectionId))

    @intent_handler("play.music.intent")
    def play_music(self, message):
        SonosMusicController.clear_queue()
        song_list = search_songs_of_artist_applemusic(interpreter = message.data.get("interpreter"))
        self.log.info(song_list)
        for current_song in song_list:
           if song_list[0] == current_song:
               SonosMusicController.sonos_api(action = "applemusic/now/song:" + str(current_song))
           elif song_list[30] == current_song:
               return
           else:
               SonosMusicController.sonos_api(action = "applemusic/queue/song:" + str(current_song))


def create_skill():
    return SonosMusicController()

# search algorithms:
# search functions for Apple Music:
# function for searching a song on Apple Music
def search_song_applemusic(title="", interpreter=""):
    # this is the url that returns a json file with the search results from the iTunes Search API (https://affiliate.itunes.apple.com/resources/documentation/itunes-store-web-service-search-api/)
    urlInFunction = "https://itunes.apple.com/search?term=" + str(title) + "&country=de&media=music&entity=song&attribute=songTerm&artistTerm=" + str(interpreter)
    response = requests.get(urlInFunction)
    resultsJson = response.json()
    bestResult = resultsJson["results"][0]
    trackId = bestResult["trackId"]
    return trackId

# function for searching an album on Apple Music
def search_album_applemusic(title="", interpreter=""):
    urlInFunction = "https://itunes.apple.com/search?term=" + str(title) + "&country=de&media=music&entity=album&attribute=albumTerm&artistTerm=" + str(interpreter)
    response = requests.get(urlInFunction)
    resultsJson = response.json()
    bestResult = resultsJson["results"][0]
    collectionId = bestResult["collectionId"]
    return collectionId

# function to search for songs of the specified interpreter on Apple Music
def search_songs_of_artist_applemusic(interpreter = ""):
    urlInFunction = "https://itunes.apple.com/search?term=" + str(interpreter) + " song&country=de&media=music&entity=song&limit=75&artistTerm=" + str(interpreter)
    response = requests.get(urlInFunction)
    resultsJson = response.json()
    song_list = []
    for current_entry in resultsJson["results"]:
        if "trackId" in current_entry:
            song_list.append(str(current_entry["trackId"]))

    random.shuffle(song_list)
    return song_list


# function to search for albums of the specified interpreter on Apple Music
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

