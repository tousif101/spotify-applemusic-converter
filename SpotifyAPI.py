import spotipy
from spotipy.oauth2 import SpotifyOAuth


class SpotifyAPI:
    def session(self):
        scope = "user-library-read playlist-modify-public user-read-private user-read-email"

        spotify = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope))
        return spotify

    def searchForTrack(self,session,token):
        query = "track:"+token
        # results=session.search(q=query,type='track')
        # Turn Me On Konesh
        results = session.search(token)
        return results
    

