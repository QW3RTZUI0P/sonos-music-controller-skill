from mycroft import MycroftSkill, intent_handler
# to shuffle lists
import random
# to call various search APIs and to communicate to the Sonos Node JS Server
import requests

class SonosMusicController(MycroftSkill):

    # important values for the skill to function 
    # can be edited in the normal Mycroft Skill settings on home.mycroft.ai
    sonos_server_ip = ""
    room = ""
    url = ""
    # radio stations. Can be edited on home.mycroft.ai
    radio01 = ""
    # value that stores the volume of the Sonos speaker when Mycroft lowers its volume
    volume = ""

    def __init__(self):
        MycroftSkill.__init__(self)

    def initialize(self):
        SonosMusicController.sonos_server_ip = self.settings.get("sonos_server_ip")
        SonosMusicController.room = self.settings.get("room")
        SonosMusicController.radio01 = self.settings.get("radio")
        # putting the values in str() is necessary
        SonosMusicController.url = "http://" + str(SonosMusicController.sonos_server_ip) + ":5005/" + str(SonosMusicController.room) + "/" 

        # connects with the mycroft-playback-control messagebus
        self.add_event("recognizer_loop:wakeword", self.activation_confirmation_noise_on_sonos)
        self.add_event("speak", self.output_speech_on_sonos)
        self.add_event("mycroft.audio.service.pause", self.pause)
        self.add_event("mycroft.audio.service.play", self.resume)
        self.add_event("mycroft.audio.service.playresume", self.resume)
        self.add_event("mycroft.audio.service.resume", self.resume)
        self.add_event("mycroft.audio.service.next", self.next_song)
        self.add_event("mycroft.audio.service.prev", self.previous_song)
        # sets up the listeners to lower and increase the volume of the Sonos speakers
        self.add_event("recognizer_loop:wakeword", self.reduce_volume_of_sonos_speaker)
        self.add_event("recognizer_loop:audio_output_end", self.increase_volume_of_sonos_speaker)


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

    # function to make the activation noise on the Sonos speaker
    # requires the file start_listening.wav in the folder node-sonos-http-api/static/clips on the machine where the node js server runs
    # the start_listening.wav file can be found in mycroft-core/mycroft/res/snd/start_listening.wav
    def activation_confirmation_noise_on_sonos(self, message):
        SonosMusicController.sonos_api(action = "clip/start_listening.wav/45")


    # function to output speech over the Sonos speaker using the TTS feature of the node js sonos server
    def output_speech_on_sonos(self, message):
        self.log.info("Sonos Utterance: " + str(message.data))
        SonosMusicController.sonos_api(action = "say/" + str(message.data.get("utterance")) + "/de-de")



    # functions to automatically lower the volume of the Sonos speaker and to increase it again when Mycroft has finished speaking
    def reduce_volume_of_sonos_speaker(self, message):
        # gets the current volume level of the Sonos speaker and stores it in volume
        state = requests.get(SonosMusicController.url + "state")
        stateJson = state.json() 
        SonosMusicController.volume = stateJson['volume']
        # reduces the volume of the Sonos speaker
        SonosMusicController.sonos_api(action = "volume/5")

    def increase_volume_of_sonos_speaker(self, message):
        # increases the volume of the Sonos speaker
        SonosMusicController.sonos_api(action = "volume/" + str(SonosMusicController.volume))


    # General controls for Sonos
    # controlled via the mycroft-playback-control messagebus
    def pause(self, message):
        SonosMusicController.sonos_api("pause")
        SonosMusicController.increase_volume_of_sonos_speaker()
    # controlled via the mycroft-playback-control messagebus
    def resume(self, message):
        self.speak_dialog('resume.dialog')
        SonosMusicController.sonos_api("play")
        SonosMusicController.increase_volume_of_sonos_speaker()
    def next_song(self, message):
        SonosMusicController.sonos_api("next")
        SonosMusicController.increase_volume_of_sonos_speaker()
    def previous_song(self, message):
        SonosMusicController.sonos_api("previous")
        SonosMusicController.increase_volume_of_sonos_speaker()  
        
    @intent_handler('louder.intent')
    def louder(self, message):
        loudness = int(SonosMusicController.volume) + 10
        SonosMusicController.sonos_api("volume/" + str(loudness))

    @intent_handler('quieter.intent')
    def quieter(self, message):
        loudness = int(SonosMusicController.volume) - 10
        SonosMusicController.sonos_api("volume/" + str(loudness))


    # playing music on Sonos
    @intent_handler("play.song.intent")
    def play_song(self, message):
        result_dict = search_song_applemusic(title = message.data.get('title'), interpreter = message.data.get('interpreter'))
        self.log.info("Playing " + str(result_dict["trackName"]) + " by " + str(result_dict["artistName"]) + " on " + str(SonosMusicController.room))
        self.speak_dialog("playing.song", {"title": result_dict["trackName"], "interpreter": result_dict["artistName"]})
        SonosMusicController.sonos_api_clear_queue(action = "applemusic/now/song:" + str(result_dict["trackId"]))

    @intent_handler("play.album.intent")
    def play_album(self, message):
        result_dict = search_album_applemusic(title = message.data.get("title"), interpreter = message.data.get("interpreter"))
        self.log.info("Playing the album " + str(results_dict["collectionName"]) + " by " + str(result_dict["artistName"]) + " on " + str(SonosMusicController.room))
        self.speak_dialog("playing.album", {"title": result_dict["collectionName"], "interpreter": result_dict["artistName"]})
        SonosMusicController.sonos_api_clear_queue(action = "applemusic/now/album:" + str(result_dict["collectionId"]))

    @intent_handler("play.music.intent")
    def play_music(self, message):
        SonosMusicController.clear_queue()
        result_dict = search_songs_of_artist_applemusic(interpreter = message.data.get("interpreter"))
        self.log.info("Playing songs by " + result_dict["interpreter"] + " on " + str(SonosMusicController.room))
        self.speak_dialog("playing.music", {"interpreter": result_dict["interpreter"]}) 
        for current_song in result_dict["song_list"]:
           if song_list[0] == current_song:
               SonosMusicController.sonos_api(action = "applemusic/now/song:" + str(current_song))
           elif song_list[30] == current_song:
               return
           else:
               SonosMusicController.sonos_api(action = "applemusic/queue/song:" + str(current_song))

    @intent_handler("play.radio.intent")
    def play_radio(self, message):
        title = message.data.get("title")
        radiostation = ""
        self.speak_dialog("playing.radio", {"radio": str(title)})
        if title == "":
            radiostation = SonosMusicController.radio01
        elif SonosMusicController.radio01 in title:
            radiostation = "favorite/radiogong"

        SonosMusicController.sonos_api_clear_queue(action = radiostation)



def create_skill():
    return SonosMusicController()

# search algorithms:
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
def search_album_applemusic(title="", interpreter=""):
    urlInFunction = "https://itunes.apple.com/search?term=" + str(title) + "&country=de&media=music&entity=album&attribute=albumTerm&artistTerm=" + str(interpreter)
    response = requests.get(urlInFunction)
    results_json = response.json()
    best_result = results_json["results"][0]
    result_dict = {"collectionId": best_result["collectionId"], "collectionName": best_result["collectionName"], "artistName": best_result["artistName"]}
    return result_dict

# function to search for songs of the specified interpreter on Apple Music
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

