import re
from fuzzywuzzy import fuzz
import logging


class SongComparer:
    def compare(self, songa, songb):
        cleaned_songa = re.sub('[\W_]+', '', songa)
        cleaned_songb = re.sub('[\W_]+', '', songb)

        return fuzz.partial_ratio(cleaned_songa.lower(), cleaned_songb.lower())

    def song_compare(self, apple_song, spotify_song):
        # track the percentage on the searches
        if self.compare(apple_song.name, spotify_song.name) > 85:
            if self.compare(apple_song.artist, spotify_song.artist) > 85:
                if self.compare(apple_song.album, spotify_song.album) > 85:
                    return True
        return False

        # Check 85 percentage match on artist, year, and song name

    def find_apple_song_in_spotify_results(self, apple_song, results):
        for spotify_song in results['tracks']['items']:
            spot_name = re.sub("[\(\[].*?[\)\]]", "", spotify_song['name']).strip()
            if self.compare(spot_name, apple_song.name) > 85:
                for artist in spotify_song['artists']:
                    if self.compare(artist['name'], apple_song.artist) > 85:
                        return spotify_song
