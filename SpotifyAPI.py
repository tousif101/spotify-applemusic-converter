import spotipy
from spotipy.oauth2 import SpotifyOAuth
import uuid
import spotipy.util as util


class SpotifyAPI:
    def session(self):
        # scope = "user-library-read playlist-modify-public user-read-private user-read-email"
        # spotify = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope))
        # return spotify

        scope = "user-library-read playlist-modify-public user-read-private user-read-email"

        # auth_manager = SpotifyOAuth(scope=scope)
        # return spotipy.Spotify(auth_manager=auth_manager)

        user = str(uuid.uuid1())
        token = util.prompt_for_user_token(user, scope)
        # sp = None
        # if token:
        #   sp = spotipy.Spotify(auth=token)
        # else:
        #     token = util.prompt_for_user_token(user, scope)
        #     sp = spotipy.Spotify(auth=token)
        # return sp
        return spotipy.Spotify(auth=token)

    def searchForTrack(self, session, token):
        results = session.search(token)
        return results
