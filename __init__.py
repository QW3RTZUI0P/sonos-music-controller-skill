from mycroft import MycroftSkill, intent_handler
# to transform the json strings returned by the APIs to python dictionaries
import json
# to call various search APIs and to communicate to the Sonos Node JS Server
import requests

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


    # General controls for Sonos
    # controlled via the mycroft-playback-control messagebus
    def pause(self, message):
        requests.get(SonosMusicController.url + "pause")
    # controlled via the mycroft-playback-control messagebus
    def resume(self, message):
        self.speak_dialog('resume.dialog')
        requests.get(SonosMusicController.url + "play")
        
    @intent_handler('louder.intent')
    def louder(self, message):
        requests.get(SonosMusicController.url + "volume/+10")

    @intent_handler('quieter.intent')
    def quieter(self, message):
        requests.get(SonosMusicController.url + "volume/-10")


    # playing music on Sonos
    @intent_handler('play.intent')
    def play_music(self, message):
        trackId = search_song_applemusic(message.data.get('title'), message.data.get('interpreter'))
        self.log.info(SonosMusicController.url + "applemusic/now/song:" + str(trackId))
        requests.get(SonosMusicController.url + "applemusic/now/song:" + str(trackId))

def create_skill():
    return SonosMusicController()

# search algorithms:
# search functions for Apple Music:
# function for searching a song on Apple Music
def search_song_applemusic(title="", interpreter=""):
    # this is the url that returns a json file with the search results from the iTunes Search API (https://affiliate.itunes.apple.com/resources/documentation/itunes-store-web-service-search-api/)
    urlInFunction = "https://itunes.apple.com/search?term=" + title + \
        "&country=de&media=music&entity=song&attribute=songTerm&artistTerm=" + interpreter
    response = requests.get(urlInFunction)
    resultsJson = response.json()
    bestResult = resultsJson["results"][0]
    trackId = bestResult["trackId"]
    return trackId

# function for searching an album on Apple Music
def search_album_applemusic(title="", interpreter=""):
    urlInFunction = "https://itunes.apple.com/search?term=" + title + "&country=de&media=music&entity=album&attribute=albumTerm&artistTerm=" + interpreter
    response = requests.get(urlInFunction)
    resultsJson = response.json()
    bestResult = resultsJson["results"][0]
    collectionId = bestResult["collectionId"]
    return collectionId


# function for searching a playlist on Apple Music
# this is currently not working because the iTunes Search API doesn't support searching for playlists
def search_playlist_applemusic(title="", interpreter=""):
    return

# function for search the Essentials playlist of an artist on Apple Music
# this is currently not working because the iTunes Search API doesn't support searching for playlists


def search_essentials_applemusic(interpreter=""):
    return

