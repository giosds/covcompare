""" This file is used to generate the dynamic Html of the webpage. If not a web app, executes compare_regions()"""

import os

from flask import Flask, request

import manage_input
import manage_output
import manage_app
import tasks


app = Flask(__name__)
app.config["DEBUG"] = False


@app.route("/", methods=["GET", "POST"])
def compare_region_cov():
    """Builds a webpage.

    Called on loading the page or after an http post

    Returns:
        str: Html of the page to be built
    """

    print("Cwd = ", os.getcwd())
    error_message = ""
    pop = manage_input.get_pop()  # Get regions-population data
    regions = manage_app.get_default_values()  # Find the first areas to show

    if request.method == "POST":
        try:
            inputs = request.form.getlist("multi_regions")
            regions = manage_input.validate_input(inputs, pop)
        except:
            # Something went wrong with the input parsing
            error_message = manage_output.incorrect_input_message()

    filename = tasks.get_plot_file(
        regions, pop
    )  # Gets the file name of the plot to display
    return_page = tasks.build_page(error_message, filename, regions, pop)

    return return_page


# For development purposes
if __name__ == "__main__":
    download = True
    pop = manage_input.get_pop()
    regions = manage_app.get_default_values()
    manage_app.compare_regions(regions, pop, download=download)
