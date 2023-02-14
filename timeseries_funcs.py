"""Clusterizes the time series."""

from scipy import signal
import numpy as np
import pandas as pd

from tslearn.clustering import TimeSeriesKMeans


def get_clusters(log_pivot_regs, n_clusters=3):
    """Dynamic time warping clusterizes the regions and finds their peaks.

    Args:
        log_pivot_regs (pandas.DataFrame): Transformed values.
        n_clusters: Region clusters to make.

    Returns:
        pandas.DataFrame: (n_clusters, n_days) clustered trajectory.
        list: (n_clusters, n_peaks) list of lists containing the grouped region names
        list of ndarray: list of peak x coordinates
    """

    # Finds the clusters
    model = TimeSeriesKMeans(n_clusters=n_clusters, metric="dtw", n_init=10, n_jobs=-1, random_state=42)
    model.fit_transform(log_pivot_regs.values.T[:, :, np.newaxis])
    clust_centers = model.cluster_centers_.squeeze()

    # Sorts the clusters, biggest one first
    clust_centers_argsort = clust_centers.sum(axis=1).argsort()[::-1]
    clust_centers = clust_centers[clust_centers_argsort, :]

    # Gets the region names in each cluster
    ordered_labels = [clust_centers_argsort[lab] for lab in model.labels_]
    cluster_labels = [[log_pivot_regs.columns[l] for l in range(len(ordered_labels)) if ordered_labels[l] == c]
                      for c in range(n_clusters)]

    # Finds the peaks in each cluster
    f_peaks = lambda cc: signal.find_peaks(np.hstack([cc, 0]), prominence=2, distance=15, width=8)[0]
    clust_peaks = [f_peaks(cc) for cc in clust_centers]

    clust_centers = pd.DataFrame(clust_centers, columns=log_pivot_regs.index.strftime("%Y-%m-%d"))

    return clust_centers, cluster_labels, clust_peaks



