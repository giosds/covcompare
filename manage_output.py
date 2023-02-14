"""Functions to plot the graphs and handle the html. """
import datetime
import os
import glob
import pathlib
import zlib


import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns
sns.set()

from constants import IMAGES, CSV_URL
import sort_regions
import timeseries_funcs

sort_functions = {
    "pca": sort_regions.sort_by_pca,
    "pop_density": sort_regions.sort_by_pop_density,
    "alphabetical": sort_regions.sort_by_alphabetical,
}

'''
NOT USED:
"distance": sort_regions.sort_by_distance,
"distance_initials": sort_regions.sort_by_distance_initials,
"correlation": sort_regions.sort_by_correlation,
"random": sort_regions.sort_by_random,
"kmeans": sort_regions.sort_by_kmeans
'''

########################################################################################################################
# Functions used to handle the plots
########################################################################################################################


def get_last_update():
    """Returns the last update of the data file."""

    filepath = pathlib.Path(os.path.basename(CSV_URL))
    last_update = datetime.datetime.fromtimestamp(filepath.stat().st_mtime).strftime("%b %d %Y")
    return last_update

def plot_graphs(pivot_regs, log_pivot_regs, suptitle, regions):
    """Plots two graphs: raw values and transformed values.

    Saves graphs to a file
    Args:
        pivot_regs (pandas.DataFrame): raw data
        log_pivot_regs (pandas.DataFrame): transformed values
        suptitle (str): title of the graph
        regions (list of str): regions to plot
    """

    filename = get_filename_from_regions(
        regions
    )  # Filenames are a function of the selected region

    last_update = get_last_update()

    fig, (ax1, ax2) = plt.subplots(2, figsize=(8, 12))
    fig.suptitle(suptitle)

    ax1.plot(pivot_regs)
    ax1.legend(pivot_regs.columns.values, loc="upper left")
    ax1.set_title(f"VALORI ASSOLUTI NUOVI CONTAGI (fino a: {last_update})")
    ax1.grid(True)
    ax2.plot(log_pivot_regs)
    ax2.legend(log_pivot_regs.columns.values, loc="upper left")
    ax2.set_title("\nVALORI TRASFORMATI (proporzionali agli abitanti, scala log)")
    ax2.grid(True)
    fig.autofmt_xdate(rotation=-45, ha="left")
    fig.tight_layout()
    fig.savefig(os.path.join(IMAGES, filename))


def delete_images():
    """Deletes all image files of the day.

    Used by the scheduler.
    """

    files = glob.glob(IMAGES + "/*")
    for f in files:
        print(f)
        os.remove(f)

def plot_vert_lines(ax, x_coords, color):
    """ Plots vertical lines.

    Args:
        plt: The image.
        x_coords (list or ndarray): X coordinates
    """
    for c in x_coords:
        ax.axvline(c, color=color, linestyle="--", alpha=0.5)

def build_heatmap(log_pivot_regs, how):
    """Builds a heatmap. Regions are sorted.

    Args:
        log_pivot_regs (pandas.DataFrame): Transformed values.
        how: A sorting algorithm among those listed in sort_functions dictionary
    """
    log_pivot_regs = log_pivot_regs.copy()

    # Sort region names according to a selected function
    ordered_list = sort_functions[how](log_pivot_regs.dropna())
    log_pivot_regs.index = log_pivot_regs.index.strftime("%Y-%m-%d")

    select_log_pivot_regs = log_pivot_regs
    trans_log_pivot_regs = select_log_pivot_regs.T
    logs_ordered_by_dens = trans_log_pivot_regs.reindex(ordered_list)

    # Add heatmap
    sns.heatmap(logs_ordered_by_dens, cmap="RdYlGn_r")

    # Set elements
    plt.xlabel("Nuovi contagi giornalieri (log)")
    plt.ylabel(f"Regioni ordinate: {how}")
    plt.title("Heatmap", size=14)
    plt.tight_layout()

    filename = os.path.join(IMAGES, f"heatmap_{how}.jpg")
    plt.savefig(filename)
    plt.close()


def build_clustered_plot(log_pivot_regs):
    """Dtw clusters of regions, with peaks.

    Args:
        log_pivot_regs (pandas.DataFrame): Transformed values.

    """

    n_clusters = 3  # How many clusters to find

    fig, ax = plt.subplots()
    clust_centers, cluster_labels, clust_peaks = timeseries_funcs.get_clusters(log_pivot_regs, n_clusters=n_clusters)

    ax.plot(clust_centers.T)  # Plot the clusterized areas
    for n in range(n_clusters-1,-1,-1):  # Draw vertical lines at peaks
        plot_vert_lines(ax, clust_peaks[n], sns.color_palette("pastel")[n])

    cluster_legends = ["("+",\n".join(j)+")" for j in cluster_labels]
    plt.legend(cluster_legends, bbox_to_anchor=(0, 1))  # Legend outside of plot area

    ax.tick_params(axis='y', which='both', labelleft=False)  # Delete vertical tick labels
    fig.autofmt_xdate(rotation=-60, ha="left")  # Horizontal labels small and rotated
    ax.tick_params(colors=sns.color_palette()[0], labelsize="x-small")
    ax.xaxis.set_major_locator(plt.FixedLocator([p for p in clust_peaks[0]]))  # Horizontal labels only at peaks

    fig.tight_layout()
    fig.savefig(os.path.join(IMAGES, "peaks_clusters.jpg"))


########################################################################################################################
# Functions used to handle the html
########################################################################################################################

# Load the main web page
def get_template():
    """Returns the template for the web page.

    Returns:
        (str, str): template html, page css
    """

    with open("form_img_template.html", "r") as f:
        html_template = f.read()
    with open("form_img_template.css", "r") as f:
        css_template = f.read()
    return html_template, css_template


def get_full_page(
    html_template,
    css_template,
    plot_html="",
    error_message="",
    reg_options="",
    heatmap_html=''
):
    """Returns a web page, complete with plot area and region names.

    Args:
        html_template (str): html code for the webpage
        css_template (str): css for the webpage
        plot_html (str): html for the plot image
        error_message (str): html to show in case the input were wrong
        reg_options (str): html for the options of the multi choice box
        heatmap_html (str): html for the heatmap image

    Returns:
        str: the complete web page
    """

    web_page = html_template.format(
        css=css_template,
        plot_html=plot_html,
        error_message=error_message,
        reg_options=reg_options,
        heatmap_html=heatmap_html,
    )
    return web_page


def get_plot_html(filename, regions):
    """Returns the html img tag for the chosen regions.

    Args:
        filename (str): Name of the plot image.
        regions (list of str): Regions to plot.

    Returns:
        str: Html for the plot image.
    """

    html_code = f'<img src="/static/{filename}" alt="{regions}" id="plot-img">'

    return html_code.format(filename=filename, regions=regions)


def get_heatmap_html(filename):
    """Returns the html img tag for the chosen regions.

    Args:
        filename (str): Name of the plot image.

    Returns:
        str: Html for the plot image.
    """

    html_code = f'<img src="/static/{filename}" alt="heatmap" id="heatmap-img">'

    return html_code.format(filename=filename)


def incorrect_input_message():
    """Adds an error message to the page.

    Returns:
        str: html to show in case the input were wrong
    """

    html_code = "<br><p>The value is incorrect. Please enter a valid sequence of region codes</p><br>"
    return html_code


def get_reg_options(regions, pop):
    """Builds the options of a multi choice box

    Args:
        pop: regions-population
        regions: the (possibly default) regions to pre-select

    Returns:
        str: html for the options of the multi choice box

    """

    option_template = '<option value="{name}"{selected}>{name}</option>'

    option_list = []
    selected = " selected"
    for name in pop.index:
        activate_selected = name in regions
        new_option = option_template.format(
            name=name, selected=selected * activate_selected
        )
        option_list.append(new_option)

    html_code = "\n".join(option_list)

    return html_code


def get_filename_from_regions(regions):
    """Returns a filename for the plot.

    The file name is a hash of the input strings.

    Args:
        regions (list of str): the selected regions

    Returns:
        str: the file name for the chosen inputs
    """

    filename_checksum = zlib.adler32("".join(regions).encode("utf-8"))
    filename = str(filename_checksum) + ".png"

    return filename
