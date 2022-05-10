from mycroft import MycroftSkill, intent_handler
# used to get the placement of the Mycroft device
from mycroft.api import DeviceApi
# used to make breaks in the code
import time
# used to control the Sonos speakers
import soco
from soco.data_structures import *
# used for internet radio
from pyradios import RadioBrowser
# used to shutdown this skill itself
from mycroft.messagebus import Message


# contains all the necessary search algorithms to search for music on the various services
from .search_algorithms import *
# contains important (static) values for the music services
from .static_values import *


class SonosMusicController(MycroftSkill):

    # important values for the skill to function
    # location information
    room = ""
    country_code = ""
    # value that stores the volume of the Sonos speaker when Mycroft lowers its volume
    volume = "0"
    # helps with the volume increase after Mycroft has been falsely activated
    increase_volume_after_false_activation = False

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
        # the name of the room the Mycroft device is located in (has to be the name of the Sonos speaker)
        SonosMusicController.room = str(DeviceApi().get()["description"])
        SonosMusicController.music_service = self.settings.get("service_selection")
        SonosMusicController.country_code = str(DeviceApi().get_location()["city"]["state"]["country"]["code"]).lower()

        SonosMusicController.initialize_soco(self)

        SonosMusicController.initialize_music_services(self)

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
        # sets up the listeners that increase the volume back to normal level when Mycroft has been falsely activated
        self.add_event("recognizer_loop:record_end", self.increase_volume_of_sonos_speaker_after_false_activation)
        self.add_event("recognizer_loop:utterance", self.filter_out_real_activations)


    # initialisation methods:
    def initialize_soco(self):
        # TODO: add error handling. What happens if the skill for some reason doesn't find any speakers on startup? Maybe continue searching ...
        SonosMusicController.all_speakers = soco.discover()
        counter = 0
        while counter < 5:
            for current_speaker in SonosMusicController.all_speakers:
                if current_speaker.player_name == SonosMusicController.room:
                    SonosMusicController.speaker = current_speaker
                    return
                    # TODO: add default value for speaker here or do something different (e.g. speaker not found dialog)
            time.sleep(6)
            counter = counter + 1

        self.speak_dialog("room.not.found.error", {"room": SonosMusicController.room})
        # make Mycroft shudown itself:
        # self.bus.emit(Message('mycroft.skills.shutdown',{"id": "sonos-music-controller-skill.qw3rtzui0p","folder": "/opt/mycroft/skills/sonos-music-controller-skill.qw3rtzui0p"}))
    
    def initialize_music_services(self):
        if SonosMusicController.music_service == None or SonosMusicController.music_service == "":
            self.speak_dialog("no.service.chosen.error")
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
            uri = "x-sonos-http:song:" + str(identifier) + ".mp4?sid=" + applemusic_service_id + "&flags=" + applemusic_flags + "&sn=" + applemusic_sn
            return uri

    # converts the given uri to a didl item that can be handled way better by soco (e.g. song can be skipped)
    def convert_to_didl_item(uri = "", title = ""):
        resources = [DidlResource(uri=uri, protocol_info="sonos.com-http:*:audio/mp4:*")]
        item = DidlMusicTrack(resources=resources, title=title, parent_id="-1", item_id="-1")
        return item

    # converts the uri used by the Sonos speakers internally to the song id used by the music services
    def convert_to_music_service_id(uri = ""):
        service = SonosMusicController.music_service
        if service == "spotify":
            return ""
        elif service == "apple_music":
            part01 = uri.split(":")[2]
            part02 = part01.split(".")[0]
            music_service_id = part02
            return music_service_id
    
    
    # function to clear the sonos queue
    def clear_queue():
        SonosMusicController.speaker.clear_queue()

    # plays the given uris (most of the time a fancy string that contains some important information)
    # the first uri in the list will be played immediately, all the other ones are being added to the queue
    # uris can either be urls or Sonos intern uris, e.g. x-sonos-http:SOME_ID&SOME_SERVICE_ID&SOME_OTHER_ID
    def play_uris(uri_list = []):
        SonosMusicController.clear_queue()
        for current_uri in uri_list:
            item = SonosMusicController.convert_to_didl_item(current_uri)
            SonosMusicController.speaker.add_to_queue(item)
            if uri_list[0] == current_uri:
                time.sleep(1)
                SonosMusicController.speaker.play_from_queue(0)


    # functions to automatically lower the volume of the Sonos speaker and to increase it again when Mycroft has finished speaking
    def reduce_volume_of_sonos_speaker(self):
        # gets the current volume level of the Sonos speaker and stores it in volume
        if SonosMusicController.speaker.get_current_transport_info().get("current_transport_state") == "PLAYING":
            SonosMusicController.volume = str(SonosMusicController.speaker.volume)
            # reduces the volume of the Sonos speaker
            SonosMusicController.speaker.volume = "5"
        else:
            # this just tells increase_volume_of_sonos_speaker() not to increase the volume
            SonosMusicController.volume = "0"

    def increase_volume_of_sonos_speaker(self):
        if SonosMusicController.volume != "0":
            SonosMusicController.speaker.volume = SonosMusicController.volume

    # increases the volume after a few seconds when Mycroft couldn't understand any utterances
    # solves the problem that Mycroft lowered the volume of the Sonos speaker every time he got falsely activated
    def increase_volume_of_sonos_speaker_after_false_activation(self):
        if SonosMusicController.volume != "0":
            SonosMusicController.increase_volume_after_false_activation = True
            # TODO: make this solution here better and more reliable (not a static value like 10 seconds)
            # longest time for Mycroft to send the audio recording to the STT service and receive an answer from it with the utterance (for now 10 seconds)
            time.sleep(10)
        if SonosMusicController.increase_volume_after_false_activation == True:
            SonosMusicController.speaker.volume = SonosMusicController.volume
            SonosMusicController.increase_volume_after_false_activation = False

    # when Mycroft understand an utterance this function will be executed
    # it tells increase_volume_of_sonos_speaker_after_false_activation() that it shouldn't increase the volume because
    # increase_volume_of_sonos_speaker() will do so after the audio output is done 
    def filter_out_real_activations(self, message):
        SonosMusicController.increase_volume_after_false_activation = False

    # General controls for Sonos
    # controlled via the mycroft-playback-control messagebus
    # TODO: fix next_song and previous_song (they are for some reason currently not working, idk why)
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

    @intent_handler('much.louder.intent')
    def much_louder(self, message):
        old_volume = SonosMusicController.volume
        new_volume = int(old_volume) + 20
        SonosMusicController.speaker.volume = str(new_volume)


    @intent_handler('quieter.intent')
    def quieter(self, message):
        old_volume = SonosMusicController.volume
        new_volume = int(old_volume) - 10
        #TODO: implement error handling: what will happen if volume is below 0?
        SonosMusicController.speaker.volume = str(new_volume)

    @intent_handler('much.quieter.intent')
    def much_quieter(self, message):
        old_volume = SonosMusicController.volume
        new_volume = int(old_volume) - 20
        SonosMusicController.speaker.volume = str(new_volume)



    @intent_handler('which.song.intent')
    def which_song_is_playing(self):
        if SonosMusicController.music_service != "apple_music":
            self.speak_dialog("not.working.error", {"service": "spotify"})

        track_info = SonosMusicController.speaker.get_current_track_info()
        title = track_info["title"]
        result_dict = track_info
        # is executed when the playing song has been started by this skill
        if "x-sonos" in title:
            # takes the Apple Music Song ID and looks it up on the iTunes Search API to get the required information (because soco often can't give us this information)
            music_service_id = SonosMusicController.convert_to_music_service_id(track_info["uri"])
            # only works for Apple Music
            # TODO: make this compatible with spotify
            result_dict = lookup_id_applemusic(music_service_id = music_service_id, country_code = SonosMusicController.country_code)

        self.speak_dialog("which.song", {"title": result_dict["title"], "artist": result_dict["artist"]})


        

    # playing music on Sonos

    # plays a song on the Sonos speaker located in the room where Mycroft is placed
    @intent_handler("play.song.intent")
    def play_song(self, message):
        try:
            result_dict = search_song(title=message.data.get('title'), artist=message.data.get('artist'),
                                      country_code = SonosMusicController.country_code, service = SonosMusicController.music_service, self = self)
            # logging stuff
            self.log.info("Playing " + str(result_dict["trackName"]) + " by " + str(result_dict["artistName"]) + " on " + str(SonosMusicController.room))
            self.speak_dialog("playing.song", {"title": result_dict["trackName"], "artist": result_dict["artistName"]})

            # responsible for playing the actual songs on the Sonos speaker
            uri = SonosMusicController.convert_to_uri(result_dict["trackId"])
            SonosMusicController.play_uris([uri])
        # throws an error if no song is found for the search terms
        except:
            artist = message.data.get("artist")
            if artist == None: 
                self.speak_dialog("no.song.found", {"title": message.data.get('title')})
            else: 
                self.speak_dialog("no.song.found.with.artist", {"title": message.data.get('title'), "artist": artist})
        
        

    # plays an album on the Sonos speaker located in the room where Mycroft is placed
    @intent_handler("play.album.intent")
    def play_album(self, message):
        try:
            result_dict = search_album(title=message.data.get("title"), artist=message.data.get("artist"),
                                       country_code = SonosMusicController.country_code, service = SonosMusicController.music_service)
            self.log.info("Playing the album " + str(result_dict["collectionName"]) + " by " + str(result_dict["artistName"]) + " on " + str(SonosMusicController.room))
            self.speak_dialog("playing.album", {"title": result_dict["collectionName"], "artist": result_dict["artistName"]})
            # responsible for playing the actual songs on the Sonos speaker
            final_uris_list = []
            for current_id in result_dict["songIds"]:
                final_uris_list.append(SonosMusicController.convert_to_uri(current_id))
            SonosMusicController.play_uris(final_uris_list)
        # throws an error if no albums (no songs in this album) are found for the search terms
        except:
            artist = message.data.get("artist")
            if artist == None: 
                self.speak_dialog("no.album.found", {"title": message.data.get('title')})
            else: 
                self.speak_dialog("no.album.found.with.artist", {"title": message.data.get('title'), "artist": artist})
            
                

    @intent_handler("play.music.intent")
    def play_music(self, message):
        try:
            result_dict = search_songs_of_artist(artist=message.data.get("artist"),
                                                 country_code = SonosMusicController.country_code, service = SonosMusicController.music_service)
            self.log.info("Playing songs by " + result_dict["artist"] + " on " + str(SonosMusicController.room))
            self.speak_dialog("playing.music", {"artist": result_dict["artist"]})
            final_uris_list = []
            for current_song in result_dict["song_list"]:
                final_uris_list.append(SonosMusicController.convert_to_uri(current_song))
                if result_dict["song_list"][-1] == current_song:
                    SonosMusicController.play_uris(final_uris_list)
                    return
        # throws an error if a search for the specified artist on apple music doesn't produce any results
        except:
           self.speak_dialog("no.music.found", {"artist": message.data.get("artist")})


    @intent_handler("play.radio.intent")
    def play_radio(self, message):
        title = message.data.get("title")
        try: 
            if title == None:
                title = ""
            radio_browser = RadioBrowser()
            radio_search_results = radio_browser.search(name = title, order = "clickcount")
            # the api returns the search results in exactly the opposite order
            best_result = radio_search_results[-1]
            radio_url = best_result["url_resolved"]
            radio_uri_for_sonos = ""
            # Sonos speakers need the prefix "x-rincon-mp3radio://" to play Internet radio
            if "https://" in radio_url:
                radio_uri_for_sonos = radio_url.replace("https://", "x-rincon-mp3radio://") 
            else:
                radio_uri_for_sonos = radio_url.replace("http://", "x-rincon-mp3radio://") 
            
            SonosMusicController.speaker.play_uri(uri = radio_uri_for_sonos, title = best_result["name"], force_radio = True)
            self.speak_dialog("playing.radio", {"radio": str(best_result["name"])})
        except:
            self.speak_dialog("no.radio.found.error", {"radio": title})



def create_skill():
    return SonosMusicController()
