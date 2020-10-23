from flask import Flask, request
import re
import SpotifyAPI
import AppleMusicAPI
import SongComparer
import logging
from os import environ

app = Flask(__name__)
app.secret_key = 'some key for session'

spotify_service = SpotifyAPI.SpotifyAPI()
applemusic_service = AppleMusicAPI.AppleMusicAPI()
song_compare_service = SongComparer.SongComparer()


@app.route('/get-applemusic-songs')
def getAppleMusicSongs():
    apple_playlist_id = request.args.get("apple_playlist_id")
    playlist_name = request.args.get("x`x`")

    logging.info("The playlist_id is " + apple_playlist_id)
    apple_songs = []
    try:
        apple_songs = applemusic_service.getPlayList(apple_playlist_id)
    except Exception as e:
        logging.error(e.__str__())

    session = None
    try:
        session = spotify_service.session()
    except Exception as e:
        print(e.__str__())
        logging.error(e.__str__())

    spotify_songs = []
    for apple_song in apple_songs:
        name = re.sub("[\(\[].*?[\)\]]", "", apple_song.name).strip()
        results = spotify_service.searchForTrack(session, name + " " + apple_song.artist)
        spotify_song = song_compare_service.find_apple_song_in_spotify_results(apple_song, results)
        if spotify_song is None:
            logging.info("Song not found is " + apple_song.name + " by " + apple_song.artist)
            print(apple_song.name + " by " + apple_song.artist)
        else:
            spotify_songs.append(spotify_song)

    user_id = session.me()['id']
    play_list_id = None
    try:
        created_playlist = session.user_playlist_create(user_id, playlist_name, public=True)
        play_list_id = created_playlist['uri']
    except Exception as e:
        logging.error(e.__str__())

    for spotify_song in spotify_songs:
        if spotify_song is not None and play_list_id is not None:
            try:
                logging.info(play_list_id)
                session.playlist_add_items(play_list_id, [spotify_song['uri']])
            except Exception as e:
                logging.error(e.__str__())

    return {"FINISH": "FINISH"}
#
# @app.route('/')
# def hello_world():
#     return 'Hello, World!'
#

from flask_session import Session
# app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(64)
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_FILE_DIR'] = './.flask_session/'
Session(app)


caches_folder = './.spotify_caches/'
if not os.path.exists(caches_folder):
    os.makedirs(caches_folder)

def session_cache_path():
    return caches_folder + session.get('uuid')

@app.route('/')
def index():
    if not session.get('uuid'):
        # Step 1. Visitor is unknown, give random ID
        session['uuid'] = str(uuid.uuid4())

    auth_manager = spotipy.oauth2.SpotifyOAuth(scope='user-read-currently-playing playlist-modify-private',
                                                cache_path=session_cache_path(),
                                                show_dialog=True)

    if request.args.get("code"):
        # Step 3. Being redirected from Spotify auth page
        auth_manager.get_access_token(request.args.get("code"))
        return redirect('/')

    if not auth_manager.get_cached_token():
        # Step 2. Display sign in link when no token
        auth_url = auth_manager.get_authorize_url()
        return f'<h2><a href="{auth_url}">Sign in</a></h2>'

    # Step 4. Signed in, display data
    spotify = spotipy.Spotify(auth_manager=auth_manager)
    return f'<h2>Hi {spotify.me()["display_name"]}, ' \
           f'<small><a href="/sign_out">[sign out]<a/></small></h2>' \
           f'<a href="/playlists">my playlists</a> | ' \
           f'<a href="/currently_playing">currently playing</a> | ' \
		   f'<a href="/current_user">me</a>' \

'''
TODO: Implement Dependency injection later 
from dependency_injector import containers, providers
class Container(containers.DeclarativeContainer):
    spotify_service = providers.Singleton(SpotifyAPI.SpotifyAPI())
    applemusic_service = providers.Singleton(AppleMusicAPI.AppleMusicAPI())

container = Container()
'''

if __name__ == "__main__":
    port = int(environ.get('PORT', 5000))
    app.run(port=port)
