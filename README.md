# <img src="https://raw.githack.com/FortAwesome/Font-Awesome/master/svgs/solid/play-circle.svg" card_color="#000000" width="50" height="50" style="vertical-align:bottom"/> Sonos Music Controller
A Mycroft skill to control the music on your Sonos speakers

## About
This skill uses the SoCo python package to control the Sonos speakers. To play music from different services, it uses the service APIs ([iTunes Search API](https://affiliate.itunes.apple.com/resources/documentation/itunes-store-web-service-search-api/) and [Spotify API](https://developer.spotify.com/documentation/web-api/)), searchs with them for music, takes the ID and converts this ID to an URI the Sonos speakers can understand. I found this URIs with jishis repo https://github.com/jishi/node-sonos-http-api so without it I couldn't have done this.

## Installation
Just install this skill using mycroft-msm. No further authentication required!
'''
mycroft-msm install https://github.com/QW3RTZUI0P/sonos-music-controller-skill
'''
The skill takes the speaker with the name you specified in the "placement" variable in the device settings on home.mycroft.ai, so please be sure that this value is exactly like the name of your Sonos speaker.


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

## Credits
QW3RTZUI0P

## Category
**Music & Audio**

## Tags
#Music
#Sonos
#Spotify
#Home

## Credits
Huge Credits to: https://github.com/jishi/node-sonos-http-api
https://github.com/SoCo/SoCo
