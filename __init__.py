from mycroft import MycroftSkill, intent_handler
import requests
import json

# important values for the skill to function
sonos_server_ip = "192.168.1.220"
room = "Küche"
url = "http://" + sonos_server_ip + ":5005/" + room + "/"

# search algorithms
# function for searching a song on Apple Music
def search_song_applemusic(title="", interpreter=""):
    # this is the url that returns a json file with the search results from the iTunes Search API (https://affiliate.itunes.apple.com/resources/documentation/itunes-store-web-service-search-api/)
    urlInFunction = "https://itunes.apple.com/search?term=" + title +  "&country=de&media=music&entity=song&attribute=songTerm&artistTerm=" + interpreter
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
    bestResult = results["results"][0]
    collectionId = bestResult["collectionId"]
    return collectionId


class SonosMusicController(MycroftSkill):

    def __init__(self):
        MycroftSkill.__init__(self)

   
    # function for searching the essentials playlist of an interpreter
    # def search_essentials_playlist:
	# this is currently not working because the iTunes Search API doesn't allow searches for playlists

    # General controls for Sonos
    @intent_handler('pause.intent')
    def pause(self, message):
        requests.get(url + "pause")

    @intent_handler('resume.intent')
    def resume(self, message):
        self.log.info(url + "play")
        self.speak_dialog('resume.dialog')
        requests.get(url + "play")
        
    @intent_handler('louder.intent')
    def louder(self, message):
        requests.get(url + "volume/+10")

    @intent_handler('quieter.intent')
    def quieter(self, message):
        requests.get(url + "volume/-10")


    # playing music on Sonos
    @intent_handler('play.intent')
    def play_music(self, message):
        print("title: " + message.data.get('title') + message.data.get('interpreter'))
        trackId=search_song_applemusic(message.data.get('title'), message.data.get('interpreter'))
        requests.get(url + "applemusic/now/song:" + str(trackId))

def create_skill():
    return SonosMusicController()
