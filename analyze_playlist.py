import matplotlib.pyplot as plt
import sys
import spotipy
import os
import numpy as np
import spotipy.util as util
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.manifold import TSNE
import seaborn as sns

sns.set()
plt.tight_layout()



REDIRECT_URI = 'http://localhost/'
SCOPE = 'user-library-read playlist-read-private'

N_CLUSTERS = 5
OUT_FOLDER = 'out'

token = util.prompt_for_user_token(
    USERNAME, SCOPE, client_id=CLIENT_ID, client_secret=CLIENT_SECRET, redirect_uri=REDIRECT_URI)


def get_playlist_tracks(username, playlist_id):
    results = sp.user_playlist_tracks(username, playlist_id)
    tracks = results['items']
    while results['next']:
        results = sp.next(results)
        tracks.extend(results['items'])
    return tracks


def get_audio_features(track_ids):
    features = []
    for i in range(0, len(tracks), 50):
        features.extend(sp.audio_features(tracks=track_ids[i: i + 50]))
    return features


def get_users_names(user_ids):
    names = {}
    for user_id in user_ids:
        names[user_id] = sp.user(user_id)['display_name']
    return names

def find_elbow(start, stop, data):
    y = []
    x = range(start, stop)
    for k in x:
        clustering = KMeans(n_clusters=k, random_state=123)
        clustering.fit(data)
        y.append(clustering.inertia_)
    elbow_df = pd.DataFrame()
    elbow_df['num_clusters'] = x
    elbow_df['ssd'] = y

    fig, ax = plt.subplots()
    profile = sns.lineplot(x='num_clusters', y='ssd', data=elbow_df, ax=ax)
    
    fname = os.path.join(OUT_FOLDER, 'elbow.png')
    fig.set_size_inches(8, 6)
    plt.tight_layout()
    fig.savefig(fname)

def plot_clusters_stats(df):
    cluster_labels_unique = df['cluster'].unique()
    for cluster_label in cluster_labels_unique:
        cluster_df = df.loc[df['cluster'] == cluster_label]
        cluster_df = cluster_df.drop(columns=['cluster', 'x', 'y'])
        mean_s = cluster_df.mean()
        mean_df = pd.DataFrame({'feature': mean_s.index, 'mean': mean_s.values})
        fig, ax = plt.subplots(ncols=1)

        profile = sns.barplot(x='mean', y='feature', data=mean_df, ax=ax[0])

        count_s = cluster_df['added_by'].value_counts() 
        count_df =  pd.DataFrame({'person': count_s.index, 'count': count_s.values})
        profile = sns.barplot(x='count', y='person', data=count_df, ax=ax[1])

        fig.suptitle('Cluster {}'.format(cluster_label))

        print(cluster_df)

        fname = os.path.join(OUT_FOLDER, 'cluster-{}.png'.format(cluster_label))
        fig.set_size_inches(8, 4)
        plt.tight_layout()
        fig.savefig(fname)

def plot_clusters(df):
    n_clusters = df['cluster'].nunique()
    fig, ax = plt.subplots(ncols=2)

    cluster_palette = sns.color_palette('bright', n_clusters)
    sns.scatterplot(data=df, x='x', y='y', hue='cluster',
                    palette=cluster_palette, ax=ax[0])

    added_by_palette = sns.color_palette('bright', len(added_by_keys))
    sns.scatterplot(data=df, x='x', y='y', hue='added_by',
                    palette=added_by_palette, ax=ax[1])

    fname = os.path.join(OUT_FOLDER, 'clusters.png')
    fig.set_size_inches(16, 12)
    plt.tight_layout()
    fig.savefig(fname)



sp = spotipy.Spotify(auth=token)

tracks = get_playlist_tracks(USERNAME, PLAYLIST)
ids = [track['track']['id'] for track in tracks]

added_by = [track['added_by']['id'] for track in tracks]
added_by_keys = set(added_by)
display_names_map = get_users_names(added_by_keys)
display_names = [display_names_map[user_id] for user_id in added_by]

features = get_audio_features(ids)
feature_keys = [
    'danceability',
    'energy',
    # 'key',
    # 'loudness',
    # 'mode',
    'speechiness',
    'acousticness',
    'instrumentalness',
    # 'liveness',
    'valence',
    # 'tempo',
    # 'time_signature'
]

data = np.array([[track[k] for k in feature_keys] for track in features])
std_data = StandardScaler().fit_transform(data)

clustering = KMeans(n_clusters=N_CLUSTERS, random_state=123)
clustering.fit(std_data)
cluster_labels = clustering.labels_

tsne = TSNE(n_components=2, random_state=123)
reduced = tsne.fit_transform(std_data)

df = pd.DataFrame(data)
df.columns = feature_keys
df['x'] = reduced[:, 0]
df['y'] = reduced[:, 1]
df['added_by'] = display_names
df['cluster'] = cluster_labels
df['name'] = [track['track']['name'] for track in tracks]
df['artists'] = [', '.join(artist['name'] for artist in track['track']['artists']) for track in tracks]
df['id'] = [track['track']['id'] for track in tracks]


find_elbow(1, 11, std_data)
plot_clusters_stats(df)
plot_clusters(df)

track_ids = df.sort_values(['cluster', 'energy'])['id'].to_list()

def reorder(current_order, new_order):
    current_order = current_order[:]
    for i, track_id in enumerate(new_order):
        cur_idx = current_order.index(track_id)
        val = current_order.pop(cur_idx)
        current_order.insert(i, val)
        sp.user_playlist_reorder_tracks(USERNAME, PLAYLIST, range_start=cur_idx, insert_before=i, range_length=1)
        print('Moved ' + cur_idx + ' to ' + i)

reorder(ids, track_ids)