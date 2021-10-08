# <img src="https://raw.githack.com/FortAwesome/Font-Awesome/master/svgs/solid/play-circle.svg" card_color="#000000" width="50" height="50" style="vertical-align:bottom"/> Sonos Music Controller
A Mycroft AI skill to control everything on your Sonos speakers. Version 0.3.3

## About
With this skill you can control every aspect of you Sonos system with your Mycroft smart speaker! It supports all the basic commands you need, such as play, pause, volume control and skipping songs, but also provides the option of playing music via your favorite services (outlined below).
### Supported services
* Spotify
* Apple Music

Services that I hope will be supported in the future:
* local Music Library
* Amazon Music

### Alternatives
There's currently one alternative for this skill that I know of and that provides the same functionality: https://github.com/smartgic/mycroft-sonos-controller-skill. There are also some other Mycroft skills on GitHub for controlling your Sonos speakers (but without support of music services or with some external dependencies), to find them just search GitHub for "mycroft sonos"

## Installation
Just install this skill using mycroft-msm. No further authentication required!
```
mycroft-msm install https://github.com/QW3RTZUI0P/sonos-music-controller-skill
```
The skill takes the speaker with the name you specified in the "placement" variable in the device settings on home.mycroft.ai, so please be sure that this value is exactly like the name of your Sonos speaker. Also, to play music from a service you have to be authenticated for it (through the Sonos app).
To start using music services, please configure your preferred one in the Mycroft settings on home.mycroft.ai.
If you want to use this skill on the unstable branch just run
```
git pull origin beta
```
in the skill directory.


## Examples
* play
* pause
* next track
* previous track
* louder
* quieter
* Play Perfect by Ed Sheeran
* Play the album Parachute by Coldplay
* Play music by Eminem

## Technical stuff
This skill uses the SoCo python package to control the Sonos speakers. To play music from different services, it uses the service APIs ([iTunes Search API](https://affiliate.itunes.apple.com/resources/documentation/itunes-store-web-service-search-api/) and [Spotify API](https://developer.spotify.com/documentation/web-api/)), searchs with them for music, takes the ID and converts this ID to an URI the Sonos speakers can understand. I found these URIs in jishis repo https://github.com/jishi/node-sonos-http-api. Without this repo I couldn't have done this.
It also supports auto-controlling the volume of the Sonos speaker in the room the Mycroft device is placed in. When Mycroft starts recording the volume is decreased and when Mycroft has finished speaking the volume is increased to its original level.

## Contributing
Please feel free to open an issue or create a PR at any time. Help and/or feedback are gladly appreciated!

## Category
**Music & Audio**

## Tags
#Music
#Sonos
#Spotify
#Home

## Credits
QW3RTZUI0P \
Huge Credits to: 
* https://github.com/jishi/node-sonos-http-api
* https://github.com/SoCo/SoCo
