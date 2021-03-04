# Playing Music
This skill uses the SoCo python package to provide its functionality. Because SoCo unfortunately doesn't support music services at the moment (although there is work being done in [this pull request](https://github.com/SoCo/SoCo/pull/763)), this skill uses a different method of playing music. Huge credit to jishis [node-sonos-http-api](https://github.com/jishi/node-sonos-http-api), without this project I couldn't have created this skill. His project also supports playing music without authentication, but setting up a separate server wouldn't be very user-friendly for a Mycroft skill.

## URIs
The SoCo package allows you to play URIs on your speakers (mostly http addresses), but how does this help at playing music via services? Jishis project kind of reversed engineered the mechanism Sonos uses for this functionality, namely which URIs you have to pass to the speakers for them to play a song from a music service. Those URIs are outlined below.

### General
To play one of those URIs below, replace the variables in it with the values you want and then pass them to a Sonos speaker object in SoCo via the .play_uri() method. Please be sure to encode the URI in the right way, otherwise it won't work.

### Spotify
The URI for Spotify songs looks like this:
```
x-sonos-spotify:TRACK_ID?sid=SID&flags=FLAGS&sn=SN
```
TRACK_ID = the URI of a Spotify item, e.g. spotify:track:0tgVpDi06FyKpA1z0VMD4v. You can get this either via the Spotify Search API or using the web player by getting the link to an item
SID = the service ID of Spotify on your system. One working value has been 9, but you can get your value by executing .musicServices.ListAvailableServices() on a SoCo speaker object and looking for Service ID in the returned string
FLAGS = I don't know what this variable means but working values have been 0, 32 or 8224
SN = I don't know what this variable means but it seems that it's not important which value it takes. Working ones have been 1 or 19.

Example:

### Apple Music
The URI for Apple Music songs looks like this:
```
x-sonos-http:ID.mp4?sid=204&flags=8224&sn=4
```
ID = the ID of a song returned by the [iTunes Search API](https://affiliate.itunes.apple.com/resources/documentation/itunes-store-web-service-search-api/)
Example:
