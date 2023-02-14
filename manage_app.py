"""Functions used to treat the data. """

import numpy as np
import pandas as pd

from constants import (
    LOMBARDIA,
    CSV_URL,
    DENOMINAZIONE_REGIONE,
    DEFAULT_START,
    NUOVI_POSITIVI,
)
import manage_input
import manage_output


def filter_regional_data(cov_df, regions):
    """Keeps the selected regions only.

    Args:
        cov_df (pandas.DataFrame): vertical data
        regions (list of str): regions to be returned as columns

    Returns:
        pandas.DataFrame: the selected regions only
    """

    cov_regs = cov_df[cov_df[DENOMINAZIONE_REGIONE].isin(regions)]

    return cov_regs


def pivot_regional_data(cov_regs):
    """Places region data into columns.

    Args:
        cov_regs (pandas.DataFrame): all the data, verticalized

    Returns:
        pandas.DataFrame: regions pivoted as columns
    """

    pivot_regs = pd.pivot_table(
        cov_regs, index="data", values=[NUOVI_POSITIVI], columns=[DENOMINAZIONE_REGIONE]
    )
    pivot_regs = pivot_regs.droplevel(None, axis=1)
    pivot_regs = pivot_regs.where(pivot_regs > 0).fillna(
        method="bfill"
    )  # Last value if the current one is inappropriate

    return pivot_regs


def normalize_smooth(pivot_regs, pop, bench_region):
    """Divides data by population, applies a rolling mean.

    Args:
        pivot_regs (pandas.DataFrame): regions are column names
        pop (pandas.Series): region, population
        bench_region (str): Benchmark region

    Returns:
        pandas.DataFrame: normalized and smoothed DataFrame
    """

    norm_pivot_regs = pivot_regs.copy()
    available_regions = list(norm_pivot_regs.columns)

    # Normalize the population based on a benchmark region
    norm_pivot_regs *= pop[bench_region]
    for region in available_regions:
        norm_pivot_regs[region] /= pop[region]

    # Smooth the data
    roll_pivot_regs = norm_pivot_regs.rolling(7).mean()

    return roll_pivot_regs


def get_default_values():
    """Returns the regions chosen for the default page.

    Returns:
        list of str: the highest and lowest-value regions

    """

    # Reads the default start file
    default_regions = [LOMBARDIA]
    try:
        # The default regions should be chosen by the scheduled script
        with open(DEFAULT_START, "r") as f:
            min_region = f.readline().strip()
            max_region = f.readline().strip()
            default_regions = [min_region, max_region]
    except:
        pass

    return default_regions


def get_raw_log_data(cov_df, regions, pop):
    """

    Args:
        cov_df (pandas.DataFrame): raw data
        regions (list of str): regions to be returned as columns
        pop (pandas.Series): region, population

    Returns:
        (pandas.DataFrame, pandas.DataFrame): raw values, transformed values
    """

    cov_regs = filter_regional_data(cov_df, regions)
    pivot_regs = pivot_regional_data(cov_regs)  # Get the raw values

    roll_pivot_regs = normalize_smooth(pivot_regs, pop, LOMBARDIA).dropna()
    log_pivot_regs = np.log2(roll_pivot_regs).dropna()  # Get the transformed values


    return pivot_regs, log_pivot_regs


def compare_regions(regions, pop, download):
    """Plots the graphs of the chosen regions

    Plots both the absolute values and the transformed values.

    Args:
        regions (list of str): regions to compare
        pop (pandas.Series): region, population
        download (bool): True if a new .csv file is to be downloaded

    Returns:
        None
    """

    cov_df = manage_input.get_df(CSV_URL, download)
    pivot_regs, log_pivot_regs = get_raw_log_data(cov_df, regions, pop)
    manage_output.plot_graphs(
        pivot_regs=pivot_regs,
        log_pivot_regs=log_pivot_regs,
        suptitle=" - ".join(regions),
        regions=regions,
    )
