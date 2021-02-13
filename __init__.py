from mycroft import MycroftSkill, intent_handler
# contains all the necessary search algorithms to search for music on the various services
from .search_algorithms import *
import time
import soco


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
    # value that stores whether the Sonos speaker is playing
    is_sonos_playing = False

    # values for the soco package
    all_speakers = []
    speaker = None

    def __init__(self):
        MycroftSkill.__init__(self)

    def initialize(self):
        SonosMusicController.sonos_server_ip = self.settings.get(
            "sonos_server_ip")
        SonosMusicController.room = self.settings.get("room")
        SonosMusicController.radio01 = self.settings.get("radio")
        # putting the values in str() is necessary
        SonosMusicController.url = "http://" + \
            str(SonosMusicController.sonos_server_ip) + \
            ":5005/" + str(SonosMusicController.room) + "/"

        # connects with the mycroft-playback-control messagebus
        self.add_event("mycroft.audio.service.pause", self.pause)
        self.add_event("mycroft.audio.service.play", self.resume)
        self.add_event("mycroft.audio.service.playresume", self.resume)
        self.add_event("mycroft.audio.service.resume", self.resume)
        self.add_event("mycroft.audio.service.next", self.next_song)
        self.add_event("mycroft.audio.service.prev", self.previous_song)
        # sets up the listeners to lower and increase the volume of the Sonos speakers
        self.add_event("recognizer_loop:wakeword",
                       self.reduce_volume_of_sonos_speaker)
        self.add_event("recognizer_loop:audio_output_end",
                       self.increase_volume_of_sonos_speaker)

    def initialize_soco():
        SonosMusicController.all_speakers = soco.discover()
        for current_speaker in SonosMusicController.speakers:
            if current_speaker.player_name == SonosMusicController.room:
                SonosMusicController.speaker = current_speaker

        break

    # general function to call the sonos api
    def sonos_api(action=""):
        requests.get(SonosMusicController.url + str(action))

    # function to call the sonos api and to clear the queue
    def sonos_api_clear_queue(action=""):
        requests.get(SonosMusicController.url + "clearqueue")
        requests.get(SonosMusicController.url + str(action))

    # function to clear the queue
    def clear_queue():
        requests.get(SonosMusicController.url + "clearqueue")

    # functions to automatically lower the volume of the Sonos speaker and to increase it again when Mycroft has finished speaking

    def reduce_volume_of_sonos_speaker(self):
        # gets the current volume level of the Sonos speaker and stores it in volume
        state = requests.get(SonosMusicController.url + "state")
        state_json = state.json()
        if state_json.get("playbackState") == "PLAYING":
            SonosMusicController.volume = state_json['volume']
            self.log.info("Reducing volume of Sonos speaker")
            # reduces the volume of the Sonos speaker
            SonosMusicController.sonos_api(action="volume/5")
        else:
            SonosMusicController.volume = "0"

    def increase_volume_of_sonos_speaker(self):
        if SonosMusicController.volume != "0":
            # increases the volume of the Sonos speaker
            self.log.info("Increasing volume on Sonos speaker")
            SonosMusicController.sonos_api(
                action="volume/" + str(SonosMusicController.volume))

    # General controls for Sonos
    # controlled via the mycroft-playback-control messagebus

    def pause(self, message):
        SonosMusicController.sonos_api("pause")
        SonosMusicController.increase_volume_of_sonos_speaker(self)
    # controlled via the mycroft-playback-control messagebus

    def resume(self, message):
        SonosMusicController.sonos_api("play")
        SonosMusicController.increase_volume_of_sonos_speaker(self)

    def next_song(self, message):
        SonosMusicController.sonos_api("next")
        SonosMusicController.increase_volume_of_sonos_speaker(self)

    def previous_song(self, message):
        SonosMusicController.sonos_api("previous")
        SonosMusicController.increase_volume_of_sonos_speaker(self)

    @intent_handler('louder.intent')
    def louder(self, message):
        loudness = int(SonosMusicController.volume) + 10
        self.log.info(loudness)
        SonosMusicController.sonos_api("volume/" + str(loudness))

    @intent_handler('quieter.intent')
    def quieter(self, message):
        loudness = int(SonosMusicController.volume) - 10
        SonosMusicController.sonos_api("volume/" + str(loudness))

    # playing music on Sonos

    @intent_handler("play.song.intent")
    def play_song(self, message):
        result_dict = search_song_applemusic(title=message.data.get(
            'title'), interpreter=message.data.get('interpreter'))
        self.log.info("Playing " + str(result_dict["trackName"]) + " by " + str(
            result_dict["artistName"]) + " on " + str(SonosMusicController.room))
        SonosMusicController.sonos_api_clear_queue(
            action="applemusic/now/song:" + str(result_dict["trackId"]))
        self.speak_dialog("playing.song", {
                          "title": result_dict["trackName"], "interpreter": result_dict["artistName"]})
        time.sleep(8)
        SonosMusicController.sonos_api(action="play")

    @intent_handler("play.album.intent")
    def play_album(self, message):
        result_dict = search_album_applemusic(title=message.data.get(
            "title"), interpreter=message.data.get("interpreter"))
        self.log.info("Playing the album " + str(results_dict["collectionName"]) + " by " + str(
            result_dict["artistName"]) + " on " + str(SonosMusicController.room))
        SonosMusicController.sonos_api_clear_queue(
            action="applemusic/now/album:" + str(result_dict["collectionId"]))
        self.speak_dialog("playing.album", {
                          "title": result_dict["collectionName"], "interpreter": result_dict["artistName"]})
        time.sleep(8)
        SonosMusicController.sonos_api(action="play")

    @intent_handler("play.music.intent")
    def play_music(self, message):
        SonosMusicController.clear_queue()
        result_dict = search_songs_of_artist_applemusic(
            interpreter=message.data.get("interpreter"))
        self.log.info("Playing songs by " +
                      result_dict["interpreter"] + " on " + str(SonosMusicController.room))
        self.speak_dialog("playing.music", {
                          "interpreter": result_dict["interpreter"]})
        for current_song in result_dict["song_list"]:
            if result_dict["song_list"][0] == current_song:
                SonosMusicController.sonos_api(
                    action="applemusic/now/song:" + str(current_song))
            elif result_dict["song_list"][30] == current_song:
                return
            else:
                SonosMusicController.sonos_api(
                    action="applemusic/queue/song:" + str(current_song))

            if (result_dict["song_list"][10] == current_song) or (result_dict["song_list"][20] == current_song):
                state = requests.get(SonosMusicController.url + "state")
                state_json = state.json()
                if str(state_json["playbackState"]) == "STOPPED":
                    SonosMusicController.sonos_api(action="play")

    @intent_handler("play.radio.intent")
    def play_radio(self, message):
        title = message.data.get("title")
        radiostation = ""
        self.speak_dialog("playing.radio", {"radio": str(title)})
        if title == "":
            radiostation = SonosMusicController.radio01
        elif SonosMusicController.radio01 in title:
            radiostation = "favorite/radiogong"

        SonosMusicController.sonos_api_clear_queue(action=radiostation)


def create_skill():
    return SonosMusicController()
