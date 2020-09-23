import requests
import logging
import AppleTrack
import re

class AppleMusicAPI:
    def getPlayList(self, applePlaylistId):
        endpoint = "https://api.music.apple.com/v1/catalog/us/playlists/" + applePlaylistId
        bearer = self.getBearerToken()
        headers = {"Authorization": "Bearer " + bearer}

        data = None
        try:
            data = requests.get(endpoint, headers=headers).json()
            logging.info(str(data))
        except Exception as e:
            logging.error(str(e))

        songs = []
        if data != None:
            tracks = data['data'][0]['relationships']['tracks']['data']
            for song in tracks:
                name = re.sub("[\(\[].*?[\)\]]", "", song["attributes"]['name']).strip()
                print(song["attributes"]['artistName'])
                artist = self.parseArtistName(song["attributes"]['artistName'])
                album = song["attributes"]['albumName']
                date = song["attributes"]['releaseDate']
                appleTrack = AppleTrack.AppleTrack(name, artist[0], album, date)
                songs.append(appleTrack)

        return songs

    def parseArtistName(self, stra):
        return re.split('& |, ', stra)
        # TODO: re.split('&|& |,| x | & ', stra) Limits the API Rate. Need to look into this.

    def getBearerToken(self):
        response = requests.get("https://us-central1-musickit-jwt.cloudfunctions.net/jwtFunction").json()
        return response['token']
