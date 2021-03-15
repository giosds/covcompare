""" This file is used to sort the regions for the heatmap """
import random

import numpy as np
import pandas as pd
from scipy.spatial import distance
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA

from constants import LOMBARDIA
import manage_input


def sort_by_correlation(log_pivot_regs):
    """Each region is the most correlated with the preceding one.

    Args:
        log_pivot_regs (pandas.DataFrame):  The data (n.days * n.regions), without NaN values

    Returns:
        list: A list of sorted regions
    """
    corr_regs = log_pivot_regs.corr(method="spearman")
    reg_list = list(corr_regs.columns)

    ordered_list = []
    selected = LOMBARDIA
    while len(reg_list) > 1:  # Find the next best correlated region
        ordered_list.append(selected)
        reg_list.remove(selected)
        selected = corr_regs.loc[reg_list, selected].idxmax()
    ordered_list.append(selected)
    return ordered_list


def sort_by_distance(log_pivot_regs):
    """Each region is the closest to the 5 preceding one, using euclidean distances.

    Args:
        log_pivot_regs (pandas.DataFrame):  The data (n.days * n.regions), without NaN values

    Returns:
        list: A list of sorted regions
    """

    reg_list = list(log_pivot_regs.columns)
    ordered_list = []

    selected = LOMBARDIA
    while (
        len(reg_list) > 1
    ):  # Find the next region, whose distance is the closest to the preceding 5 distances
        ordered_list.append(selected)
        reg_list.remove(selected)
        to_sort = log_pivot_regs.loc[:, reg_list]
        already_sorted = log_pivot_regs.loc[:, ordered_list[-5:]]
        dists = distance.cdist(
            to_sort.T, already_sorted.T
        )  # Euclidean distances between already sorted and candidates
        meandists = np.linalg.norm(
            dists, axis=1
        )  # l2 norm for the region distance vectors
        mindist = meandists.argmin()  # Select the lowest l2 norm
        selected = to_sort.columns[mindist]

    ordered_list.append(selected)

    return ordered_list


def sort_by_distance_initials(log_pivot_regs):
    """Each region is the closest to the top 5 regions.

    Args:
        log_pivot_regs (pandas.DataFrame):  The data (n.days * n.regions), without NaN values

    Returns:
        list: A list of sorted regions
    """
    reg_list = list(log_pivot_regs.columns)
    ordered_list = []

    # Order regions by distance from the preceding 5 distances
    selected = LOMBARDIA
    while (
        len(reg_list) > 1
    ):  # Find the next region, whose distance is the closest to the top 5 distances
        ordered_list.append(selected)
        reg_list.remove(selected)
        to_sort = log_pivot_regs.loc[:, reg_list]
        already_sorted = log_pivot_regs.loc[:, ordered_list[:5]]
        dists = distance.cdist(
            to_sort.T, already_sorted.T
        )  # Euclidean distances between top sorted and candidates
        meandists = np.linalg.norm(
            dists, axis=1
        )  # l2 norm for the region distance vectors
        mindist = meandists.argmin()  # Select the lowest l2 norm
        selected = to_sort.columns[mindist]

    ordered_list.append(selected)

    return ordered_list


def sort_by_kmeans(log_pivot_regs):
    """Two K-means clusters identify a direction for placing the regions.

    The regions are clustered to two representative sets.
    The clusters are n.days-dimensional vector.
    All the regions are then projected on the vector passing through the clusters.
    Similar results to Pca.

    Args:
        log_pivot_regs (pandas.DataFrame):  The data (n.days * n.regions), without NaN values

    Returns:
        list: A list of sorted regions
    """

    kmeans = KMeans(n_clusters=2, random_state=0).fit(log_pivot_regs.T)

    clust_centers = kmeans.cluster_centers_
    o = clust_centers[:1, :].T
    region_vectors = log_pivot_regs.values - o
    proj_line = clust_centers[1:2, :].T - o
    proj_vectors = np.dot(region_vectors.T, proj_line) / np.dot(proj_line.T, proj_line)
    trans_regs_df = pd.DataFrame(data=proj_vectors, index=log_pivot_regs.columns)
    sorted_trans_regs_df = trans_regs_df.sort_values(0, ascending=True)
    ordered_list = sorted_trans_regs_df.index
    return ordered_list


def sort_by_pca(log_pivot_regs):
    """Pca reduces all the daily variations to a single dimension, which is used to sort the regions.

    Args:
        log_pivot_regs (pandas.DataFrame) : The data (n.days * n.regions), without NaN values

    Returns:
        list: A list of sorted regions
    """

    pca = PCA(1)
    pca.fit(log_pivot_regs.T)
    trans_regs = pca.transform(log_pivot_regs.T)
    trans_regs_df = pd.DataFrame(data=trans_regs, index=log_pivot_regs.columns)
    sorted_trans_regs_df = trans_regs_df.sort_values(0, ascending=False)
    ordered_list = sorted_trans_regs_df.index

    return ordered_list


def sort_by_pop_density(*args):
    """The regions with the heghest population density come first.

    Args:
        args: Ensures a compatible function signature

    Returns:
        list: A list of sorted regions
    """

    pop_density = manage_input.get_dens()
    ordered_list = pop_density.sort_values(ascending=False).index

    return ordered_list


def sort_by_random(log_pivot_regs):
    """The regions with the highest population density come first.

    Args:
        log_pivot_regs (pandas.DataFrame) : The data (n.days * n.regions), without NaN values

    Returns:
        list: A list of sorted regions
    """

    ordered_list = list(log_pivot_regs.columns)
    random.shuffle(ordered_list)
    return ordered_list


def sort_by_alphabetical(log_pivot_regs):
    """Alphabetical sorting of the regions.

    Args:
        log_pivot_regs (pandas.DataFrame):  The data (n.days * n.regions), without NaN values

    Returns:
        list: A list of sorted regions
    """

    ordered_list = sorted(log_pivot_regs.columns)
    return ordered_list
