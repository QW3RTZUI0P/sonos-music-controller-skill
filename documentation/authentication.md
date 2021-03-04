# Authentication
This skill doesn't require any user authentication (at least until now) and provides all it's functionality without any setup.

But how exactly does the skill get the required values to play music, such as song, album and playlist IDs?

## Spotify
The skill uses the [Spotify Web API](https://developer.spotify.com/documentation/web-api/) to get the important data, which requires an access token. Currently the used access token is taken from the [GitHub pages site](https://github.com/jumelon/public_spotify_access_token) of [this GitHub Repository](https://github.com/jumelon/public_spotify_access_token).
This repository contains the access token that is freely provided by Spotify when you visit open.spotify.com. Just look at the source code of this site and search for "accessToken" and you'll find one.
I am aware that, according to the [Spotify Terms and Conditions](https://developer.spotify.com/terms/), it is not really permitted to use their API for voice enabled applications without their agreement. But because this skill basically does what everyone does who uses the Spotify Web Player (searching for items on Spotify, the web player is probably just a nice wrapper for this) I hope it's not too bad. 
If Spotify doesn't agree with me here and wants me to stop this, I will gladly invent a new way of authenticating (probably with user authentication like the Mycroft Spotify skill does).

## Apple Music
The skill uses the [iTunes Search API](https://affiliate.itunes.apple.com/resources/documentation/itunes-store-web-service-search-api/) to get the required data from Apple Music. This API fortunately doesn't required any form of authentication and can be accessed by everyone.

