import sys
import spotipy
import numpy as np
import spotipy.util as util
import matplotlib.pyplot as plt
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import AgglomerativeClustering
from sklearn import decomposition

N_CLUSTERS = 5


CLIENT_ID = ''
CLIENT_SECRET = ''
REDIRECT_URI = 'http://localhost/'

username = 'aleksiy123'
scope = 'user-library-read playlist-read-private playlist-modify-private'
token = util.prompt_for_user_token(username, scope, client_id=CLIENT_ID, client_secret=CLIENT_SECRET, redirect_uri=REDIRECT_URI)


def get_all_user_saved_tracks():
    limit = 50
    offset = 0
    results = []
    cur_res = sp.current_user_saved_tracks(offset=offset, limit=limit)
    results.extend(cur_res['items'])
    offset += len(cur_res['items'])
    while len(cur_res['items']) == limit:
        cur_res = sp.current_user_saved_tracks(offset=offset, limit=limit)
        results.extend(cur_res['items'])
        offset += len(cur_res['items'])
    return results

def get_all_user_playlists():
    limit = 50
    offset = 0
    results = []
    cur_res = sp.current_user_playlists(offset=offset, limit=limit)
    results.extend(cur_res['items'])
    offset += len(cur_res['items'])
    while len(cur_res['items']) == limit:
        cur_res = sp.current_user_playlists(offset=offset, limit=limit)
        results.extend(cur_res['items'])
        offset += len(cur_res['items'])
    return results

def create_playlists(labels_unique):
    current_playlists = get_all_user_playlists()
    playlist_dict = {playlist['name'] : playlist for playlist in current_playlists}
    playlists = {}
    for label in labels_unique:
        name = 'cluster {}'.format(label)
        if name in playlist_dict:
            playlist = playlist_dict[name]
        else:
            playlist = sp.user_playlist_create(username, name, public=False)
        playlists[label] = playlist
    return playlists

def bin_track_ids(ids, labels):
    track_bin = {}
    for track_id, label in zip(ids, labels):
        if label not in track_bin:
            track_bin[label] = []
        track_bin[label].append(track_id)
    return track_bin

def replace_playlist_songs(track_bin, playlists):
    for label, track_ids in track_bin.iteritems():
        playlist = playlists[label]
        sp.user_playlist_replace_tracks(username, playlist['id'], track_ids)


if token:
    sp = spotipy.Spotify(auth=token)
    sp.trace = False
    tracks = get_all_user_saved_tracks()   
    ids = [item['track']['id'] for item in tracks]
    names = [item['track']['name'] for item in tracks]
    features = sp.audio_features(tracks=ids)
    feature_keys = [
        'danceability', 
        'energy', 
        #'key', 
        'loudness', 
         #'mode', 
        'speechiness', 
        'acousticness', 
        'instrumentalness', 
        'liveness', 
        'valence', 
         #'tempo', 
         #'time_signature'
        ]

    data = np.array([[track[k] for k in feature_keys] for track in features])
    std_data = StandardScaler().fit_transform(data)
    pca = decomposition.PCA(n_components=2)
    pca_data =  pca.fit_transform(std_data)

    ms = AgglomerativeClustering(N_CLUSTERS, affinity='manhattan', linkage='complete')
    ms.fit(std_data)
    labels = ms.labels_
    labels_unique = np.unique(labels)
    n_clusters = len(labels_unique)

    colors = 'bgrcmyk'
    for name, label, x, y in zip(names, labels, pca_data[:, 0], pca_data[:, 1]):
        plt.scatter(x, y, color=colors[label])
        plt.annotate(name, xy=(x, y))
    plt.show()

    track_bin = bin_track_ids(ids, labels)
    playlists = create_playlists(labels_unique)
    replace_playlist_songs(track_bin, playlists)

else:
    print("Can't get token for", username)