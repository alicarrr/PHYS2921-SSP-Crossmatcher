import pandas as pd
from astropy.coordinates import SkyCoord 
from astropy import units as u 
from astropy.coordinates import search_around_sky

import logging
from logging.handlers import RotatingFileHandler

# Import the centralized logger
from logger_config import logger

def find_planets_in_source(source: str):
    """Find all planets in a source file (i.e. remove duplicate planets from the source list)

    Args:
        source (str): csv filename of source list of exoplanets of interest 
        from the NASA exoplanet database

    Returns:
        source_list_sorted (DataFrame): filtered version of 'source' which contains 
        only one instance of each planet, the one with the most recent row update
    """
    # Read the source list and filter for unique planets
    source_list = pd.read_csv(source).drop_duplicates(subset = ['ra'])
    
    # Ensure 'rowupdate' is a datetime type
    source_list['rowupdate'] = pd.to_datetime(source_list['rowupdate'], format = "%d/%m/%Y")
    
    # proxima cen b test
    # source_list['rowupdate'] = pd.to_datetime(source_list['rowupdate'], format = "%Y-%m-%d")

    # Sort by 'rowupdate' in descending order
    data_sorted = source_list.sort_values('rowupdate', ascending = False)

    # Drop duplicates keeping the first entry which is the newest
    source_list_sorted = data_sorted.drop_duplicates(subset = ['ra'])

    return source_list_sorted


def crossmatch(filename: str, source_list:str, search_radius:float, planet_name:str=None):
    """Compare coordinates from a CASDA sourcelist against the NASA database 
    to see if any files with the same position match. 
    
    This function is accessed in the function 'cross_match_planet'.

    Args:
        filename (str): filename of CASDA catalogue
        source_list (str): filename of the NASA list of sources to be crossmatched
        search_radius (float): search radius around each source (will be converted to arcseconds)
        planet_name (str, optional): Name of the planet to be matched. Defaults to None.

    Returns:
        _type_: _description_
        idx (NDArray[Any]): indexes that match in the Source Catalog
        idx_to_crossmatch (NDArray[Any]): Indices in Catalog to crossmatch that 
            correspond with the same element of 'idx'
        d2d1 (Angle | Any): on-sky separation between the coordinates.
    """
    # Load catalogue data for the planet
    casda_catalogue = pd.read_csv(filename)
    # print(casda_catalogue.head()[["ra_deg_cont", "dec_deg_cont"]])

    source_list_sorted = pd.read_csv(source_list)

    if planet_name is not None:
        source_list_sorted = source_list_sorted[source_list_sorted['pl_name'] == planet_name]
    
    # SkyCoord objects for CASDA catalogue and sourcelist
    casda_catalog_coords = SkyCoord(ra = casda_catalogue['ra_deg_cont'].values,
                                    dec = casda_catalogue['dec_deg_cont'].values, 
                                    unit = "deg")
    
    sources_catalog_coords = SkyCoord(ra = source_list_sorted['ra_corrected'], 
                                      dec = source_list_sorted['dec_corrected'], 
                                      unit = "deg")

    # Search radius for crossmatching in arcseconds
    search_radius_arcsecond = search_radius * u.arcsecond

    # Perform crossmatching
    idx, idx_to_crossmatch, d2d1, _ = search_around_sky(casda_catalog_coords, sources_catalog_coords, seplimit = search_radius_arcsecond)
    
    return idx, idx_to_crossmatch, d2d1


def crossmatch_planet(filename: str, source_list:str, search_radius:float, planet_name:str) -> None:
    """Crossmatch NASA database with CASDA database for a planet using the 'crossmatching' function

    Args:
        filename (str): filename of CASDA catalogue
        source_list (str): filename of the NASA list of sources to be crossmatched
        search_radius (float): search radius around each source (will be converted to arcseconds)
        planet_name (str): Name of the planet to be matched. Defaults to None.
    """
    # print initial statements indicating which file and sourcelist will be examined
    logger.info(f"Loading CASDA data from: {filename}")
    logger.info(f"Loading Proper Motion Corrected Data from: {source_list}")
 
    try:
        # Perform crossmatching for the planet
        idx, idx_to_crossmatch, d2d1 = crossmatch(filename, source_list, search_radius, planet_name)
        # Print performance of crossmatching
        logger.info(f"Crossmatch results for {planet_name}:")
        logger.info(f"Matches in Source Catalog: {idx}")
        logger.info(f"Indices in Catalog to crossmatch: {idx_to_crossmatch}")
        logger.info(f"Separation distances: {d2d1}")
    except FileNotFoundError as e:
        # Raise an error if the planet name is undefined or crossmatch raises an error
        logger.info(f"Catalogue file for {planet_name} not found.")
        logger.info(f"{e}")