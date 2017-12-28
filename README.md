# Spotify-Cluster

A simple script that clusters your Spotify library into multiple playlists using Spotify audio features. 

![](https://github.com/aleksiy325/spotify-cluster/blob/master/figures/figure_1.png?raw=true)

Plot PCA dimensionality reduction to 2 dimensions of my library. Largest cluster in blue is mostly made up of metal. Teal is all electronic music. We are going to add some more songs from  `Selected Ambient Works 85–92` and see what happens. The expected outcome is that the additional songs should be near `Ageispolis - Aphex Twin` as they are from the same album and hopefully be in the same cluster or at least close together.

![](https://github.com/aleksiy325/spotify-cluster/blob/master/figures/figure_2.png?raw=true)

Here we have added 3 mores songs from the same album. Two of them are in the same cluster, but `Hedphelym` is in a different cluster. However, just because songs are in the same album does not necessarily mean they will all be in the same cluster.

![](https://github.com/aleksiy325/spotify-cluster/blob/master/figures/figure_3.png?raw=true)

Finally, we add all the songs in the album. The songs are spread out over three clusters. The blue cluster is made up entirely of songs from the album. Purple contains most of the songs as well as some other electronic songs which makes sense. A couple songs also made into teal which seems to be the most random category containing a mix of rap, metal, and electronic songs. I additionally  tried to increase the number of clusters to see if teal would be divided further but this was not the case. The red and blue clusters where subdivided into additional clusters instead. 
