from mycroft import MycroftSkill, intent_handler
# used to get the placement of the Mycroft device
from mycroft.api import DeviceApi
# used to control the Sonos speakers
import soco
# used to make breaks in the code
import time
# contains all the necessary search algorithms to search for music on the various services
from .search_algorithms import *
# contains important (static) values for the music services
from .static_values import *


class SonosMusicController(MycroftSkill):

    # important values for the skill to function
    # can be edited in the normal Mycroft Skill settings on home.mycroft.ai
    sonos_server_ip = ""
    room = ""
    url = ""
    country_code = ""
    # radio stations. Can be edited on home.mycroft.ai
    radio01 = ""
    # value that stores the volume of the Sonos speaker when Mycroft lowers its volume
    volume = "0"
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
        SonosMusicController.room = str(DeviceApi().get()["description"])
        SonosMusicController.radio01 = self.settings.get("radio")
        # putting the values in str() is necessary
        SonosMusicController.url = "http://" + \
            str(SonosMusicController.sonos_server_ip) + \
            ":5005/" + str(SonosMusicController.room) + "/"

        SonosMusicController.country_code = str(DeviceApi().get_location()["city"]["state"]["country"]["code"]).lower()

        # initializes soco
        SonosMusicController.initialize_soco()

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
        for current_speaker in SonosMusicController.all_speakers:
            if current_speaker.player_name == SonosMusicController.room:
                SonosMusicController.speaker = current_speaker


    # general function to call the sonos api
    def sonos_api(action=""):
        requests.get(SonosMusicController.url + str(action))

    # function to call the sonos api and to clear the queue
    def sonos_api_clear_queue(action=""):
        requests.get(SonosMusicController.url + "clearqueue")
        requests.get(SonosMusicController.url + str(action))

    # function to clear the queue
    def clear_queue():
        SonosMusicController.speaker.clear_queue()
        # requests.get(SonosMusicController.url + "clearqueue")

    # plays the given uris (most of the time a fancy string that contains some important information)
    # the first uri in the list will be played immediately, all the other ones are being added to the queue
    # uris can either be urls or Sonos intern uris, e.g. x-sonos-http:SOME_ID&SOME_SERVICE_ID&SOME_OTHER_ID
    def play_uris(uri_list = []):
        for current_uri in uri_list:
            if uri_list[0] == current_uri:
                SonosMusicController.speaker.play_uri(current_uri)
            else:
                SonosMusicController.speaker.add_uri_to_queue(current_uri)


    # functions to automatically lower the volume of the Sonos speaker and to increase it again when Mycroft has finished speaking

    def reduce_volume_of_sonos_speaker(self):
        # gets the current volume level of the Sonos speaker and stores it in volume
        # state = requests.get(SonosMusicController.url + "state")
        # state_json = state.json()
        if SonosMusicController.speaker.get_current_transport_info().get("current_transport_state") == "PLAYING":
            SonosMusicController.volume = str(SonosMusicController.speaker.volume)
            self.log.info("Reducing volume of Sonos speaker")
            # reduces the volume of the Sonos speaker
            SonosMusicController.speaker.volume = "5"
            # SonosMusicController.sonos_api(action="volume/5")
        else:
            # this just tells increase_volume_of_sonos_speaker() not to increase the volume
            SonosMusicController.volume = "0"

    def increase_volume_of_sonos_speaker(self):
        if SonosMusicController.volume != "0":
            # increases the volume of the Sonos speaker
            self.log.info("Increasing volume on Sonos speaker")
            SonosMusicController.speaker.volume = SonosMusicController.volume
            SonosMusicController.volume = "0"

    # General controls for Sonos
    # controlled via the mycroft-playback-control messagebus

    def pause(self, message):
        SonosMusicController.speaker.pause()
        
    def resume(self, message):
        SonosMusicController.speaker.play()
        
    def next_song(self, message):
        SonosMusicController.speaker.next()
        
    def previous_song(self, message):
        SonosMusicController.speaker.previous()
        
    @intent_handler('louder.intent')
    def louder(self, message):
        old_volume = SonosMusicController.volume
        new_volume = old_volume + 10
        SonosMusicController.speaker.volume = new_volume

    @intent_handler('quieter.intent')
    def quieter(self, message):
        old_volume = SonosMusicController.volume
        new_volume = old_volume - 10
        SonosMusicController.speaker.volume = new_volume


    # takes the given identifier and converts it to an uri (currently only Apple Music)
    def convert_to_uri(identifier = ""):
        uri = "x-sonos-http:song%3a" + str(identifier) + ".mp4?sid=" + applemusic_service_id + "&flags=" + applemusic_flags + "&sn=" + applemusic_sn
        return uri
        

    # playing music on Sonos

    # plays a song on the Sonos speaker located in the room where Mycroft is placed
    @intent_handler("play.song.intent")
    def play_song(self, message):
        result_dict = search_song_applemusic(title=message.data.get('title'), interpreter=message.data.get('interpreter'), country_code = SonosMusicController.country_code)
        uri = SonosMusicController.convert_to_uri(result_dict["trackId"])
        SonosMusicController.speaker.clear_queue()
        SonosMusicController.speaker.play_uri(uri)
        self.log.info("Playing " + str(result_dict["trackName"]) + " by " + str(result_dict["artistName"]) + " on " + str(SonosMusicController.room))
        self.speak_dialog("playing.song", {"title": result_dict["trackName"], "interpreter": result_dict["artistName"]})
        

    # plays an album on the Sonos speaker located in the room where Mycroft is placed
    @intent_handler("play.album.intent")
    def play_album(self, message):
        result_dict = search_album_applemusic(title=message.data.get("title"), interpreter=message.data.get("interpreter"))
        self.log.info("Playing the album " + str(results_dict["collectionName"]) + " by " + str(result_dict["artistName"]) + " on " + str(SonosMusicController.room))
        self.speak_dialog("playing.album", {"title": result_dict["collectionName"], "interpreter": result_dict["artistName"]})
        SonosMusicController.speaker.clear_queue()
        final_uris_list = []
        for current_id in result_dict:
            final_uris_list.append(SonosMusicController.convert_to_uri(current_id))
        SonosMusicController.play_uris(final_uris_list)
                

    @intent_handler("play.music.intent")
    def play_music(self, message):
        result_dict = search_songs_of_artist_applemusic(interpreter=message.data.get("interpreter"))
        self.log.info("Playing songs by " + result_dict["interpreter"] + " on " + str(SonosMusicController.room))
        self.speak_dialog("playing.music", {"interpreter": result_dict["interpreter"]})
        SonosMusicController.speaker.clear_queue()
        final_uris_list = []
        for current_song in result_dict["song_list"]:
            final_uris_list.append(SonosMusicController.convert_to_uri(current_song))
            if result_dict["song_list"][30] == current_song:
                SonosMusicController.play_uris(final_uris_list)
                return

            # just used for debugging
            # if (result_dict["song_list"][10] == current_song) or (result_dict["song_list"][20] == current_song):
            #     state = requests.get(SonosMusicController.url + "state")
            #     state_json = state.json()
            #     if str(state_json["playbackState"]) == "STOPPED":
            #         SonosMusicController.sonos_api(action="play")

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
