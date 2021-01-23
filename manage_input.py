""" Functions to parse and prepare the input data """

import string
import pandas as pd

from constants import POPULATION_CSV


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


def get_pop():
    """Reads in a region-population Series.

    Returns:
        pandas.Series: region, population
    """
    write_pop()  # TODO debug
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
    pd.Series(pop_dict, name="Population").to_csv("population.csv")
    pd.DataFrame.from_dict(pop_dict, orient="index", columns=["Population"]).to_csv(
        "population.csv", index=True
    )
