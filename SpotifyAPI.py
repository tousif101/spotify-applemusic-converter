import uuid
import spotipy
import spotipy.util as util

class SpotifyAPI:
    def session(self):
        scope = "user-library-read playlist-modify-public user-read-private user-read-email"
        user = str(uuid.uuid1())
        
        token = util.prompt_for_user_token(user, scope)
        sp = None
        if token:
            sp = spotipy.Spotify(auth=token)
        else:
            token = util.prompt_for_user_token(user, scope)
            sp = spotipy.Spotify(auth=token)
        return sp

    def searchForTrack(self,session,token):
        query = "track:"+token
        # results=session.search(q=query,type='track')
        # Turn Me On Konesh
        results = session.search(token)
        return results
    

