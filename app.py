import os
from flask import Flask, session, request, redirect
from flask_session import Session
import spotipy
import uuid

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(64)
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_FILE_DIR'] = './.flask_session/'
Session(app)

caches_folder = './.spotify_caches/'
if not os.path.exists(caches_folder):
    os.makedirs(caches_folder)

def session_cache_path():
    return caches_folder + session.get('uuid')

global_session = None

@app.route('/')
def index():
    if not session.get('uuid'):
        # Step 1. Visitor is unknown, give random ID
        session['uuid'] = str(uuid.uuid4())

    auth_manager = spotipy.oauth2.SpotifyOAuth(scope="user-library-read playlist-modify-public user-read-private user-read-email",
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
    global_session = spotify
    return f'<h2>Hi {spotify.me()["display_name"]}, ' \
           f'<small><a href="/sign_out">[sign out]<a/></small></h2>' \
           f'<a href="/playlists">my playlists</a> | ' \
           f'<a href="/currently_playing">currently playing</a> | ' \
           f'<a href="/current_user">me</a>' \


#Make new Spotify session each time!

@app.route('/get-applemusic-songs')
def getAppleMusicSongs():
    apple_playlist_id = request.args.get("apple_playlist_id")
    playlist_name = request.args.get("playlist_name")
    logging.info("The playlist_id is " + apple_playlist_id)
    apple_songs = []
    try:
        apple_songs = applemusic_service.getPlayList(apple_playlist_id)
    except Exception as e:
        logging.error(e.__str__())

    auth_manager = spotipy.oauth2.SpotifyOAuth(cache_path=session_cache_path())
    if not auth_manager.get_cached_token():
        return redirect('/')

    session = spotipy.Spotify(auth_manager=auth_manager)

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

def sign_out():
    os.remove(session_cache_path())
    session.clear()
    try:
        # Remove the CACHE file (.cache-test) so that a new user can authorize.
        os.remove(session_cache_path())
    except OSError as e:
        print("Error: %s - %s." % (e.filename, e.strerror))
    return redirect('/')


@app.route('/playlists')
def playlists():
    auth_manager = spotipy.oauth2.SpotifyOAuth(cache_path=session_cache_path())
    if not auth_manager.get_cached_token():
        return redirect('/')

    spotify = spotipy.Spotify(auth_manager=auth_manager)
    return spotify.current_user_playlists()


@app.route('/currently_playing')
def currently_playing():
    auth_manager = spotipy.oauth2.SpotifyOAuth(cache_path=session_cache_path())
    if not auth_manager.get_cached_token():
        return redirect('/')
    spotify = spotipy.Spotify(auth_manager=auth_manager)
    track = spotify.current_user_playing_track()
    if not track is None:
        return track
    return "No track currently playing."


@app.route('/current_user')
def current_user():
    auth_manager = spotipy.oauth2.SpotifyOAuth(cache_path=session_cache_path())
    if not auth_manager.get_cached_token():
        return redirect('/')
    spotify = spotipy.Spotify(auth_manager=auth_manager)
    return spotify.current_user()


if __name__ == "__main__":
    port = int(environ.get('PORT', 5000))
    app.run(port=port)
