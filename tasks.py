""" The top-level functions called by the main file """
import os

import numpy as np

import manage_input
import manage_output
from constants import CSV_URL, DEFAULT_START, IMAGES
from manage_app import (
    get_df,
    filter_regional_data,
    pivot_regional_data,
    normalize_smooth,
    get_raw_log_data,
    compare_regions,
)
from manage_output import plot_graphs, delete_images


def compare_ita_vs_region(region, download, pop):
    """Compares a chosen region VS its complementary - Italy

    Args:
        pop (Series): region, population
        region (str): the region to compare
        download (bool): true to download a new csv file is

    Returns:
        None
    """

    Italia_no_region = f"Italia_no_{region}"

    cov_df = get_df(CSV_URL, download)
    cov_regs = filter_regional_data(cov_df, [region])
    pivot_regs = pivot_regional_data(cov_regs)

    # Add total Italy
    pivot_regs_all = pivot_regional_data(cov_df)
    pivot_regs_all_no_region = pivot_regs_all.drop(columns=region)
    pivot_regs[Italia_no_region] = pivot_regs_all_no_region.sum(axis=1)

    # Update series
    pop[Italia_no_region] = pop["Italia"] - pop[region]
    roll_pivot_regs = normalize_smooth(pivot_regs, pop, region)
    log_pivot_regs = np.log(roll_pivot_regs)
    plot_graphs(
        pivot_regs=pivot_regs,
        log_pivot_regs=log_pivot_regs,
        suptitle=f"{region} vs rest of Italy",
        regions=[region],
    )


def scheduled_reset_operations():
    """Performs the end-of-day scheduled operations

    - Downloads the data
    - Deletes the old plots
    - Finds the default inputs
    """

    # Download new
    cov_df = get_df(CSV_URL, download=True)
    pop = manage_input.get_pop()
    # Reset plots
    delete_images()

    # Choose max min
    pivot_regs, log_pivot_regs = get_raw_log_data(cov_df, pop.index, pop)
    last_day_log = log_pivot_regs.iloc[-1:]
    min_region = last_day_log.idxmin(axis=1)[0]
    max_region = last_day_log.idxmax(axis=1)[0]

    # Write the default start file
    with open(DEFAULT_START, "w") as f:
        f.write(min_region + "\n")
        f.write(max_region)


def build_page(error_message, filename, regions, pop):
    """Builds a complete webpage

    Prepares the content and fills the template in.

    Args:
        pop (dict): region, population
        regions (list): the selected regions
        filename (str): the file name for the chosen inputs
        error_message (str): message to display on top of the page

    Returns:
        str: the Html web page
    """

    (
        form_img_template,
        form_img_template_css,
    ) = manage_output.get_template()  # Get the template for the web page

    plot_html = manage_output.get_plot_html(
        filename=filename, regions=regions
    )  # Get plot area
    reg_options = manage_output.get_reg_options(
        regions=regions, pop=pop
    )  # Get the options area html

    return_page = manage_output.get_full_page(
        form_img_template,
        form_img_template_css,
        plot_html=plot_html,
        error_message=error_message,
        reg_options=reg_options,
    )
    return return_page


def get_plot_file(regions, pop):
    """Returns the file name of the plot.

    Generates the plot if needed.

    Args:
        regions (list): the selected regions
        pop (dict): region, population

    Returns:
        str: the file name for the chosen inputs
    """

    filename = manage_output.get_filename_from_regions(regions)

    # Only produce a plot if the file is missing
    if not os.path.isfile(os.path.join(IMAGES, filename)):
        compare_regions(regions, pop, download=False)

    return filename
