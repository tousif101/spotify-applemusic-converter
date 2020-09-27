from flask import Flask, request
import re
import SpotifyAPI
import AppleMusicAPI
import SongComparer
import logging

app = Flask(__name__)
app.secret_key = 'some key for session'

spotify_service = SpotifyAPI.SpotifyAPI()
applemusic_service = AppleMusicAPI.AppleMusicAPI()
song_compare_service = SongComparer.SongComparer()


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
                session.playlist_add_items(play_list_id, [spotify_song['uri']])
            except Exception as e:
                logging.error(e.__str__())

    return {"FINISH": "FINISH"}

@app.route('/')
def hello_world():
    return 'Hello, World!'


'''
TODO: Implement Dependency injection later 
from dependency_injector import containers, providers
class Container(containers.DeclarativeContainer):
    spotify_service = providers.Singleton(SpotifyAPI.SpotifyAPI())
    applemusic_service = providers.Singleton(AppleMusicAPI.AppleMusicAPI())

container = Container()
'''

if __name__ == "__main__":
    app.run(host='0.0.0.0')
