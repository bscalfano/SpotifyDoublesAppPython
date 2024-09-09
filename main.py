import os
import base64
import json
import re
from dotenv import load_dotenv
from requests import post, get

##############################################
#                  CLASSES                   #
##############################################
class Song:
    def __init__(self, song_json):
        self.id = song_json['id']
        self.name = song_json['name']
        self.shortened_name = shorten_song_name(song_json['name'])
        self.album_name = song_json['album']['name']
        self.album_id = song_json['album']['id']
        self.album_type = song_json['album']['album_type']
        self.album_total_tracks = song_json['album']['total_tracks']
        self.album_image = song_json['album']['images'][0]['url']
        self.album_release_date = song_json['album']['release_date']
        self.artist_name = song_json['artists'][0]['name']
        self.artist_id = song_json['artists'][0]['id']
        self.disc_number = song_json['disc_number']
        self.duration_ms = song_json['duration_ms']
        self.explicit = song_json['explicit']
        self.popularity = song_json['popularity']


        

load_dotenv()

client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")

print("Client ID: ", client_id)
print("Client Secret: ", client_secret)

def get_token():
    auth_string = client_id + ":" + client_secret
    auth_bytes = auth_string.encode("utf-8")
    auth_base64 = str(base64.b64encode(auth_bytes), "utf-8")

    url = "https://accounts.spotify.com/api/token"
    headers = {
        "Authorization": "Basic " + auth_base64,
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {"grant_type": "client_credentials"}
    result = post(url, headers=headers, data=data)
    json_result = json.loads(result.content)
    token = json_result["access_token"]
    return token






def get_auth_header(token):
    return {"Authorization": "Bearer " + token}

def search_for_artist(token, artist_name):
    url = "https://api.spotify.com/v1/search"
    headers = get_auth_header(token)
    query = f"?q={artist_name}&type=artist&limit=1"

    query_url = url + query
    result = get(query_url, headers=headers)
    json_result = json.loads(result.content)["artists"]["items"]
    if len(json_result) == 0:
        print("No artist with this name exists...")
        return None
    
    return json_result[0]

def get_songs_by_artist(token, artist_id):
    url = f"https://api.spotify.com/v1/artists/{artist_id}/top-tracks?country=US"
    headers = get_auth_header(token)
    result = get(url, headers=headers)
    json_result = json.loads(result.content)["tracks"]
    return json_result

def get_playlists_by_user_id(token, user_id):
    url = f"https://api.spotify.com/v1/users/{user_id}/playlists"
    headers = get_auth_header(token)
    result = get(url, headers=headers)
    json_result = json.loads(result.content)["items"]
    return json_result

def get_playlist_id_by_name(playlists, name):
    for playlist in playlists:
        if playlist["name"] == name:
            return playlist["id"]
    return "Playlist not found"

def get_playlist_id_by_name_and_user_id(token, playlist_name, user_id):
    playlists = get_playlists_by_user_id(token, user_id)
    return get_playlist_id_by_name(playlists, playlist_name)

def get_song_array_by_playlist(token, playlist_id):
    url = f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks"
    headers = get_auth_header(token)
    result = get(url, headers=headers)
    total_tracks = json.loads(result.content)["total"]
    offset = 0
    songs = []
    while offset < total_tracks:
        url = f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks?offset={offset}"
        result = get(url, headers=headers)
        offset += 100
        json_result = json.loads(result.content)["items"]
        for song in json_result:
            songs.append(Song(song['track']))
    if len(songs) == total_tracks:
        return songs
    else:
        return

def get_song_names_by_song_array(songs):
    song_names = []
    for song in songs:
        song_names.append(song.name)
    return song_names

def shorten_song_name(song_name):
    song_name = re.sub(r'\W+', '', song_name)
    return song_name.upper()

def shorten_song_names(song_names):
    shortened_song_names = []
    for song_name in song_names:
        shortened_song_name = shorten_song_name(song_name)
        shortened_song_names.append(shortened_song_name)
    return shortened_song_names

def find_duplicate_names(songs):
    shortened_names_and_ids = []
    duplicate_songs = []
    for song in songs:
        for shortened_name_and_id in shortened_names_and_ids:
            if shortened_name_and_id[0] == song.shortened_name:
                dupe_song = get_song_by_id(shortened_name_and_id[1])
                if not is_song_in_array(duplicate_songs, dupe_song.id):
                    duplicate_songs.append(dupe_song)
                if not is_song_in_array(duplicate_songs, song.id):
                    duplicate_songs.append(song)
        shortened_names_and_ids.append((song.shortened_name, song.id))
    return duplicate_songs

def get_song_by_id(id):
    url = f"https://api.spotify.com/v1/tracks/{id}"
    headers = get_auth_header(token)
    result = get(url, headers=headers)
    song = Song(json.loads(result.content))
    return song

def is_song_in_array(songs, id):
    for song in songs:
        if song.id == id:
            return True
    return False




token = get_token()
# print("Token: ", token)

# artist = search_for_artist(token, "The Wonder Years")
# artist_id = artist["id"]
# print("Artist ID: ", artist_id)

# songs = get_songs_by_artist(token, artist_id)
# for i, song in enumerate(songs):
#     print(f"{i + 1}. {song['name']}")

# playlists = get_playlists_by_user_id(token, "Brisken86")
# for i, playlist in enumerate(playlists):
#     print(f"{i + 1}. {playlist['name']}")

# print(get_playlist_id_by_name(playlists, "Mega"))

playlist_id = get_playlist_id_by_name_and_user_id(token, "Mega", "Brisken86")
print(playlist_id)
songs = get_song_array_by_playlist(token, playlist_id)
song_names = get_song_names_by_song_array(songs)

# for i, song_name in enumerate(song_names):
#     print(f"{i + 1}. {song_name}")

# shortened_song_names = shorten_song_names(song_names)
# for shortened_song_name in shortened_song_names:
#     print(shortened_song_name)

# song_array = []
# for song in song_list:
#     song_array.append(Song(song['track']))

duplicate_songs = find_duplicate_names(songs)

for song in duplicate_songs:
    print(song.name, "-", song.artist_name)