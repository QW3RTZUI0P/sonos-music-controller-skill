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
    # location information
    room = ""
    country_code = ""
    # radio stations. Can be edited on home.mycroft.ai
    radio01 = ""
    # value that stores the volume of the Sonos speaker when Mycroft lowers its volume
    volume = "0"
    # value that stores whether the Sonos speaker is playing
    is_sonos_playing = False

    # the music service chosen by the user
    # possible values: "spotify" or "apple_music"
    music_service = ""

    # values for the soco package
    all_speakers = []
    speaker = None

    # values for Spotify
    spotify_sn = ""

    def __init__(self):
        MycroftSkill.__init__(self)

    def initialize(self):
        # get the skill settings
        SonosMusicController.room = str(DeviceApi().get()["description"])
        SonosMusicController.radio01 = self.settings.get("radio")
        SonosMusicController.music_service = self.settings.get("service_selection")

        SonosMusicController.country_code = str(DeviceApi().get_location()["city"]["state"]["country"]["code"]).lower()

        # initializes soco
        SonosMusicController.initialize_soco()

        SonosMusicController.initialize_music_services()

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
        if SonosMusicController.music_service == "":
            self.speak_dialog("no.service.chosen.error")

    # initialisation methods:
    def initialize_soco():
        SonosMusicController.all_speakers = soco.discover()
        for current_speaker in SonosMusicController.all_speakers:
            if current_speaker.player_name == SonosMusicController.room:
                SonosMusicController.speaker = current_speaker
    
    def initialize_music_services():
        if SonosMusicController.music_service == None or SonosMusicController.music_service == "":
            self.speak_dialog("no.music.service.chosen")
        elif SonosMusicController.music_service == "spotify":
            SonosMusicController.initialize_spotify()
        elif SonosMusicController.music_service == "apple_music":
            pass

    def initialize_spotify():
        # TODO: add mechanism to get the Spotify sid and sn values
        pass

    # takes the given identifier and converts it to an uri (currently only Apple Music and Spotify)
    # TODO: check if Spotify uris are right and functional
    def convert_to_uri(identifier = ""):
        service = SonosMusicController.music_service
        if service == "spotify":
            # TODO: is it important which values sid, flags and sn have??
            uri = "x-sonos-spotify:spotify:track:" + str(identifier) + "?sid=9&flags=0&sn=19"
            return uri
        elif service == "apple_music":
            uri = "x-sonos-http:song%3a" + str(identifier) + ".mp4?sid=" + applemusic_service_id + "&flags=" + applemusic_flags + "&sn=" + applemusic_sn
            return uri
    
    
    # function to clear the queue
    def clear_queue():
        SonosMusicController.speaker.clear_queue()

    # plays the given uris (most of the time a fancy string that contains some important information)
    # the first uri in the list will be played immediately, all the other ones are being added to the queue
    # uris can either be urls or Sonos intern uris, e.g. x-sonos-http:SOME_ID&SOME_SERVICE_ID&SOME_OTHER_ID
    def play_uris(uri_list = []):
        for current_uri in uri_list:
            #if uri_list[0] == current_uri:
            #    SonosMusicController.speaker.play_uri(current_uri)
            #else:
            SonosMusicController.speaker.add_uri_to_queue(current_uri)
        SonosMusicController.speaker.next()
        SonosMusicController.speaker.play()


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
        new_volume = int(old_volume) + 10
        #TODO: implement error handling: what will happen if volume is above 100?
        SonosMusicController.speaker.volume = str(new_volume)

    @intent_handler('quieter.intent')
    def quieter(self, message):
        old_volume = SonosMusicController.volume
        new_volume = int(old_volume) - 10
        #TODO: implement error handling: what will happen if volume is below zero?
        SonosMusicController.speaker.volume = str(new_volume)


    
        

    # playing music on Sonos

    # plays a song on the Sonos speaker located in the room where Mycroft is placed
    @intent_handler("play.song.intent")
    def play_song(self, message):
        try:
            result_dict = search_song(title=message.data.get('title'), interpreter=message.data.get('interpreter'), country_code = SonosMusicController.country_code, service = SonosMusicController.music_service, instance = self)
            uri = SonosMusicController.convert_to_uri(result_dict["trackId"])
            SonosMusicController.speaker.clear_queue()
            SonosMusicController.speaker.play_uri(uri)
            self.log.info("Playing " + str(result_dict["trackName"]) + " by " + str(result_dict["artistName"]) + " on " + str(SonosMusicController.room))
            self.speak_dialog("playing.song", {"title": result_dict["trackName"], "interpreter": result_dict["artistName"]})
            self.log.info(result_dict["url"])
        except IndexError:
            interpreter = message.data.get("interpreter")
            if interpreter == None: 
                self.speak_dialog("no.song.found", {"title": message.data.get('title')})
            else: 
                self.speak_dialog("no.song.found.with.interpreter", {"title": message.data.get('title'), "interpreter": interpreter})
        
        

    # plays an album on the Sonos speaker located in the room where Mycroft is placed
    @intent_handler("play.album.intent")
    def play_album(self, message):
        try:
            result_dict = search_album(title=message.data.get("title"), interpreter=message.data.get("interpreter"), country_code = SonosMusicController.country_code, service = SonosMusicController.music_service)
            self.log.info("Playing the album " + str(result_dict["collectionName"]) + " by " + str(result_dict["artistName"]) + " on " + str(SonosMusicController.room))
            self.speak_dialog("playing.album", {"title": result_dict["collectionName"], "interpreter": result_dict["artistName"]})
            SonosMusicController.speaker.clear_queue()
            final_uris_list = []
            for current_id in result_dict["songIds"]:
                final_uris_list.append(SonosMusicController.convert_to_uri(current_id))
            SonosMusicController.play_uris(final_uris_list)
        except IndexError:
            interpreter = message.data.get("interpreter")
            if interpreter == None: 
                self.speak_dialog("no.album.found", {"title": message.data.get('title')})
            else: 
                self.speak_dialog("no.album.found.with.interpreter", {"title": message.data.get('title'), "interpreter": interpreter})
            
                

    @intent_handler("play.music.intent")
    def play_music(self, message):
        try:
            result_dict = search_songs_of_artist(interpreter=message.data.get("interpreter"), country_code = SonosMusicController.country_code, service = SonosMusicController.music_service)
            self.log.info("Playing songs by " + result_dict["interpreter"] + " on " + str(SonosMusicController.room))
            self.speak_dialog("playing.music", {"interpreter": result_dict["interpreter"]})
            SonosMusicController.speaker.clear_queue()
            final_uris_list = []
            for current_song in result_dict["song_list"]:
                final_uris_list.append(SonosMusicController.convert_to_uri(current_song))
                if result_dict["song_list"][-1] == current_song:
                    SonosMusicController.play_uris(final_uris_list)
                    return
        except IndexError:
           self.speak_dialog("no.music.found", {"interpreter": message.data.get("interpreter")})

            # just used for debugging
            # if (result_dict["song_list"][10] == current_song) or (result_dict["song_list"][20] == current_song):
            #     state = requests.get(SonosMusicController.url + "state")
            #     state_json = state.json()
            #     if str(state_json["playbackState"]) == "STOPPED":
            #         SonosMusicController.sonos_api(action="play")

    @intent_handler("play.radio.intent")
    def play_radio(self, message):
        title = message.data.get("title")
        if title == None:
            title = ""
        radiostation = ""
        self.speak_dialog("playing.radio", {"radio": str(title)})
        if title == "":
            radiostation = SonosMusicController.radio01
        elif SonosMusicController.radio01 in title:
            radiostation = "favorite/radiogong"

        SonosMusicController.sonos_api_clear_queue(action=radiostation)


def create_skill():
    return SonosMusicController()
