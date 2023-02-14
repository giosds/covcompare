""" Functions to parse and prepare the input data """
import os

import pandas as pd
import requests
import string

from constants import POPULATION_CSV, DENSITY_CSV


def validate_input(inputs, pop):
    """Returns a list of input strings.

    Args:
        inputs (list of str): input list of strings
        pop (pandas.Series): region, population

    Returns:
        list of str: the input list, after validating the input
    """

    assert all(s in pop.index for s in inputs)
    return inputs


def get_dens():
    """Reads in a region-density Series.

    Returns:
        pandas.Series: region, population density
    """

    try:
        dens = pd.read_csv(DENSITY_CSV, index_col=0, squeeze=True)
    except:
        write_dens()
        dens = pd.read_csv(DENSITY_CSV, index_col=0, squeeze=True)

    return dens


def get_pop():
    """Reads in a region-population Series.

    Returns:
        pandas.Series: region, population
    """

    try:
        pop = pd.read_csv(POPULATION_CSV, index_col=0, squeeze=True)
    except:
        write_pop()
        pop = pd.read_csv(POPULATION_CSV, index_col=0, squeeze=True)

    return pop


def standardize_str(s):
    """ Returns a clean string: lowercase; punctuation is stripped"""
    r = s.lower().translate(str.maketrans("", "", string.punctuation + " "))
    return r


def get_regions_data():
    """For setup

    Retrieves the region,population data

    Independent execution.
    Replace filename.
    """

    # download from http://dati.istat.it/Index.aspx?DataSetCode=DCIS_POPRES1# to istat_data.csv
    filename = "istat_data.csv"
    # Match to data
    replace_region_names = {
        "Friuli-Venezia Giulia": "Friuli Venezia Giulia",
        "Provincia Autonoma Bolzano / Bozen": "P.A. Bolzano",
        "Provincia Autonoma Trento": "P.A. Trento",
        "Valle d'Aosta / Vallée d'Aoste": "Valle d'Aosta",
    }
    csv_pop_df = pd.read_csv(filename)
    pop_dict = (
        csv_pop_df[(csv_pop_df["Sesso"] == "totale") & (csv_pop_df["ETA1"] == "TOTAL")]
        .set_index("Territorio", drop=True)["Value"]
        .rename(index=replace_region_names)
        .sort_index()
        .to_dict()
    )
    write_pop(pop_dict)


def write_pop(pop_dict=None):
    """For setup

    Writes a population csv file

    Args:
        pop_dict (dict of (str, int)): a region, population Dictionary

    Returns:
        None
    """
    if pop_dict is None:
        pop_dict = {
            "Abruzzo": 1305770,
            "Basilicata": 556934,
            "Calabria": 1924701,
            "Campania": 5785861,
            "Emilia-Romagna": 4467118,
            "Friuli Venezia Giulia": 1211357,
            "Lazio": 5865544,
            "Liguria": 1543127,
            "Lombardia": 10103969,
            "Marche": 1518400,
            "Molise": 302265,
            "P.A. Bolzano": 532080,
            "P.A. Trento": 542739,
            "Piemonte": 4341375,
            "Puglia": 4008296,
            "Sardegna": 1630474,
            "Sicilia": 4968410,
            "Toscana": 3722729,
            "Umbria": 880285,
            "Valle d'Aosta": 125501,
            "Veneto": 4907704,
        }  # , 'Italia': 60244639

    pd.DataFrame.from_dict(pop_dict, orient="index", columns=["Population"]).to_csv(
        POPULATION_CSV, index=True
    )


def write_dens(dens_dict=None):
    """For setup

    Writes a population csv file

    Args:
        pop_dict (dict of (str, int)): a region, population Dictionary

    Returns:
        None
    """
    if dens_dict is None:
        dens_dict = {
            "Abruzzo": 121,
            "Basilicata": 55,
            "Calabria": 126,
            "Campania": 423,
            "Emilia-Romagna": 199,
            "Friuli Venezia Giulia": 153,
            "Lazio": 340,
            "Liguria": 285,
            "Lombardia": 423,
            "Marche": 162,
            "Molise": 68,
            "P.A. Bolzano": 72,
            "P.A. Trento": 87,
            "Piemonte": 171,
            "Puglia": 205,
            "Sardegna": 68,
            "Sicilia": 192,
            "Toscana": 162,
            "Umbria": 104,
            "Valle d'Aosta": 38,
            "Veneto": 268,
        }

    pd.DataFrame.from_dict(dens_dict, orient="index", columns=["Density"]).to_csv(
        DENSITY_CSV, index=True
    )


def get_df(csv_url, download):
    """Downloads or reads the data from file.

    Args:
        csv_url (str): url of csv file
        download (bool): : True to download a new file

    Returns:
        DataFrame
    """

    file_name = os.path.basename(csv_url)

    # Download from Github
    if download:
        req = requests.get(csv_url)
        url_content = req.content
        csv_file = open(file_name, "wb")
        csv_file.write(url_content)
        csv_file.close()

    cov_df = pd.read_csv(file_name)
    cov_df["data"] = pd.to_datetime(cov_df["data"])

    return cov_df

