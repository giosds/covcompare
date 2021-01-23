""" Functions to plot the graphs and handle the html """
import os
import glob
import zlib

import matplotlib

from constants import IMAGES

matplotlib.use("Agg")
import matplotlib.pyplot as plt


########################################################################################################################
# Functions used to handle the plots
########################################################################################################################


def plot_graphs(pivot_regs, log_pivot_regs, suptitle, regions):
    """Plots two graphs: raw values and transformed values.

    Saves graphs to a file
    Args:
        pivot_regs (pandas.DataFrame): raw data
        log_pivot_regs (pandas.DataFrame): transformed values
        suptitle (str): title of the graph
        regions (list of str): regions to plot

    Returns:
        None
    """

    filename = get_filename_from_regions(
        regions
    )  # Filenames are a function of the selected region

    fig, (ax1, ax2) = plt.subplots(2, figsize=(8, 12))
    fig.suptitle(suptitle)

    ax1.plot(pivot_regs)
    ax1.legend(pivot_regs.columns.values, loc="upper left")
    ax1.set_title("VALORI ASSOLUTI NUOVI CONTAGI")
    ax1.grid(True)
    ax2.plot(log_pivot_regs)
    ax2.legend(log_pivot_regs.columns.values, loc="upper left")
    ax2.set_title("VALORI TRASFORMATI (proporzionali agli abitanti, scala log)")
    ax2.grid(True)
    fig.autofmt_xdate(rotation=-45, ha="left")
    fig.savefig(os.path.join(IMAGES, filename))  # TODO path


def delete_images():
    """Deletes all image files of the day.

    Used by the scheduler.
    """

    files = glob.glob(IMAGES + "/*")
    for f in files:
        print(f)
        os.remove(f)


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
):
    """Returns a web page, complete with plot area and region names.

    Args:
        html_template (str): html code for the webpage
        css_template (str): css for the webpage
        plot_html (str): html for the plot image
        error_message (str): html to show in case the input were wrong
        reg_options (str): html for the options of the multi choice box

    Returns:
        str: the complete web page
    """

    web_page = html_template.format(
        css=css_template,
        plot_html=plot_html,
        error_message=error_message,
        reg_options=reg_options,
    )
    return web_page


def get_plot_html(filename, regions):
    """Returns the html img tag for the chosen regions.

    Args:
        filename (str): name of the plot image
        regions (list of str): regions to plot

    Returns:
        str: html for the plot image
    """
    html_code = f'<img src="/static/{filename}" alt="{regions}" id="plot-img">'

    return html_code.format(filename=filename, regions=regions)


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
