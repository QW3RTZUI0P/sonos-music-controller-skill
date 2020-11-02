from mycroft import MycroftSkill, intent_file_handler


class SonosMusicController(MycroftSkill):
    def __init__(self):
        MycroftSkill.__init__(self)

    @intent_file_handler('controller.music.sonos.intent')
    def handle_controller_music_sonos(self, message):
        self.speak_dialog('controller.music.sonos')


def create_skill():
    return SonosMusicController()

