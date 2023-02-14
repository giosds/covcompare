""" The top-level functions."""

import os

import numpy as np

from constants import CSV_URL, DEFAULT_START, IMAGES
import manage_app
import manage_input
import manage_output


def compare_ita_vs_region(region, download, pop):
    """Compares a chosen region VS its complementary - Italy.

    Args:
        pop (Series): Region, population.
        region (str): The region to compare.
        download (bool): True to download a new csv file.
    """

    Italia_no_region = f"Italia_no_{region}"

    cov_df = manage_input.get_df(CSV_URL, download)
    cov_regs = manage_app.filter_regional_data(cov_df, [region])
    pivot_regs = manage_app.pivot_regional_data(cov_regs)

    # Add total Italy
    pivot_regs_all = manage_app.pivot_regional_data(cov_df)
    pivot_regs_all_no_region = pivot_regs_all.drop(columns=region)
    pivot_regs[Italia_no_region] = pivot_regs_all_no_region.sum(axis=1)

    # Update series
    pop[Italia_no_region] = pop["Italia"] - pop[region]
    roll_pivot_regs = manage_app.normalize_smooth(pivot_regs, pop, region)
    log_pivot_regs = np.log(roll_pivot_regs)
    manage_output.plot_graphs(
        pivot_regs=pivot_regs,
        log_pivot_regs=log_pivot_regs,
        suptitle=f"{region} vs rest of Italy",
        regions=[region],
    )


def scheduled_reset_operations(download):
    """Performs the end-of-day scheduled operations.

    - Downloads the data
    - Deletes the old plots
    - Finds the default inputs
    """

    # Download new
    cov_df = manage_input.get_df(CSV_URL, download=download)
    pop = manage_input.get_pop()
    # Reset plots
    manage_output.delete_images()

    # Pivot all data
    pivot_regs, log_pivot_regs = manage_app.get_raw_log_data(cov_df, pop.index, pop)

    # Build heatmaps
    generate_all_heatmaps(log_pivot_regs)

    # Choose max min
    last_day_log = log_pivot_regs.iloc[-1:]
    min_region = last_day_log.idxmin(axis=1)[0]
    max_region = last_day_log.idxmax(axis=1)[0]

    # Write the default start file
    with open(DEFAULT_START, "w") as f:
        f.write(min_region + "\n")
        f.write(max_region)


def build_page(error_message, filename, regions, pop, heatmap_filename):
    """Builds a complete webpage.

    Prepares the content and fills the template in.

    Args:
        pop (dict): Region, population.
        regions (list): The selected regions.
        filename (str): The file name for the chosen inputs.
        error_message (str): Message to display on top of the page.

    Kwargs:
        heatmap_filename: File for the heatmap plot.

    Returns:
        str: The Html web page.
    """

    (
        form_img_template,
        form_img_template_css,
    ) = manage_output.get_template()  # Get the template for the web page

    plot_html = manage_output.get_plot_html(
        filename=filename, regions=regions
    )  # Get plot area

    heatmap_html = manage_output.get_heatmap_html(
        filename=heatmap_filename
    )  # Get heatmap area

    reg_options = manage_output.get_reg_options(
        regions=regions, pop=pop
    )  # Get the options area html

    return_page = manage_output.get_full_page(
        form_img_template,
        form_img_template_css,
        plot_html=plot_html,
        error_message=error_message,
        reg_options=reg_options,
        heatmap_html=heatmap_html,
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
        manage_app.compare_regions(regions, pop, download=False)

    return filename


def generate_all_heatmaps(log_pivot_regs):
    """Generates all the heatmap files.

    Args:
        log_pivot_regs (pandas.DataFrame) : The data
    """

    for sort_name in manage_output.sort_functions.keys():
        manage_output.build_heatmap(log_pivot_regs, sort_name)
    manage_output.build_clustered_plot(log_pivot_regs)

def get_heatmap_file(how):
    """Returns the file name of the heatmap.

    Launches all scheduled operations if needed

    Args:
        how (list): the selected heatmap

    Returns:
        str: the file name for the chosen heatmap
    """

    filepath = f"heatmap_{how}.jpg"

    # Reset all if the file is missing
    if not os.path.isfile(os.path.join(IMAGES, filepath)):
        scheduled_reset_operations()

    return filepath
