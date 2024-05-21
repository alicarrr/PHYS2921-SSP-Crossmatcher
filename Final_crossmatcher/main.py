import casda_util
import proper_motion
import crossmatcher
import scipy
import pandas as pd
import numpy as np
import os
import getpass
import time
from astroquery.casda import Casda


# Import the centralized logger
from logger_config import logger


def main(debug: bool = False, verbose: bool = False):
    # Set current file as path
    os.chdir(os.path.dirname(os.path.abspath(__file__)))

    # Login to CASDA
    username = input('Enter your CASDA username: ')
    casda = Casda()
    casda.login(username=username)
    logger.info("Logged in successfully using interactive username input.")
    
    if debug:
        logger.info("INITIAL HOT JUPITERS \\ NASA CATALOGUE FILTERING")

    # Search radius for crossmatching
    search_radius = 3

    # How many planets to sample and therefore which source file to use
    source = None
    sample_paths = {'10': ".\\Hot_Jupiters\\Hot_Jupiters_10_Samples.csv",
                    '88': ".\\Hot_Jupiters\\Hot_Jupiters_88_Samples.csv",
                    '123': ".\\Hot_Jupiters\\Hot_Jupiters_123_Samples.csv",
                    'Proxima_B_Test' : ".\\proxima_cen_b_test\\PS_2024.05.09_04.24.22.csv",
                    'all': "NASA_exoplanet_archive_declination_filtered_with_proper_motion_values.csv",
                    "123d": ".\\Hot_Jupiters\\Hot_Jupiters_123_Detections.csv"}
    
    # Make a list of all sample options to print for user input
    sample_options = ', '.join(str(key) for key in sample_paths.keys())

    while True:
        # Request how many samples the user wants to test
        sample_size = input(f'How many samples? ({sample_options}): ')

        if sample_size in sample_paths:
            # Set source as the corresponding file to the input given
            source = sample_paths[sample_size]
            break
        else:
            # Return an error as the input does not match any keys
            logger.info("Not a valid number of sources.")

    logger.info(f'RESULTS FOR {sample_size} EXOPLANETS')

    # Find list of all planets in source file
    source_list_sorted = crossmatcher.find_planets_in_source(source)

    # List of planets with GAIA 2 ID
    source_list_filtered = proper_motion.filter_for_gaia(source_list_sorted)

    if debug:
        logger.info(f"GAIA2-filtered no-duplicate source list sorted by latest update: {source_list_filtered}")

    # Make csv of gaia only planets
    source_list_filtered.to_csv('.\\Hot_Jupiters\\Filtered_NASA_only_GAIA.csv')

    ##################################
    # Source by source crossmatching #
    ##################################
    # Set index of the loop to 0, this is used for counting when to add pauses to data retrieval. 
    # This time delay is needed to reduce the chance of CASDA erroring due to lack of access.
    i = 0

    # loop through each row of the sourcelist which corresponds with a planet
    for index, row_source in source_list_filtered.iterrows():

        ##########################################
        ## GETTING CURRENT EXAMINED SOURCE INFO ##
        ##########################################

        # ra and dec of planet
        source_ra = row_source['ra']
        source_dec = row_source['dec']
        
        # Filter for planet name in row
        raw_planet_name = row_source['pl_name']
        # Remove spaces from planet name 
        planet_name = row_source['pl_name'].replace(' ', '')

        # make name of matches file
        output_filename = f"{planet_name}_catalogues"

        if debug:
            logger.info(f"EXAMINING SOURCE [planet name, ra, dec]: [{planet_name, source_ra, source_dec}]")
            logger.info(f"BEGINNING CASDA DOWNLOAD FOR SOURCE")

        ###############################
        ## PROPER MOTION CORRECTIONS ##
        ###############################

        if debug:
            logger.info("BEGIN SOURCE PROPER MOTION CORRECTION")

        # catalogue file with epoch to proper motion correct to
        pm_catalogue_filename = casda_util.casda_search_closest_catalogue(source_ra=source_ra, 
                                                                          source_dec=source_dec, 
                                                                          casda=casda,
                                                                          debug=debug)
        # pm_catalogue_filename = "selavy-image.i.VAST_1453-62.SB50301.cont.taylor.0.restored.conv.components.xml"
    
        # if no sources within 3 degrees, then just skip to next source
        if not pm_catalogue_filename:
            logger.info(f"NO CATALOGUES WITHIN 3 DEGREES OF SOURCE [planet name, ra, dec]: [{planet_name, source_ra, source_dec}]")

            continue

        if debug:
            logger.info(f"Catalogue to proper motion correct to: {pm_catalogue_filename}")

        # extract epoch to proper motion correct to from pubdat
        pm_epoch = casda_util.extract_epoch_from_pubdat_catalogue(pm_catalogue_filename)

        # add pm_epoch only to the row of row_source
        source_list_filtered.at[index, 'epoch'] = pm_epoch

        if debug:
            logger.info(f"Modified source list (with added epoch): ")
            logger.info(source_list_filtered.head())

        # perform proper motion correction for current planet
        source_list_filtered = proper_motion.proper_correct_planet(source_list_filtered, raw_planet_name)
        
        if debug:
            logger.info(f"Modified source list (with added ra_corrected, dec_corrected): ")
            logger.info(source_list_filtered.head())
        
        # Save csv of corrected ra and dec for this planet to new folder
        _, source_filename = os.path.split(source)
        source_filename = source_filename[:-4]
        proper_motion_downloads_path = os.path.join(os.path.dirname(__file__), "NASA_with_Proper_Motion\\")
        proper_motion_filename = f'{source_filename}_proper_corrected_NASA'
        
        # Convert DataFrame of matches into a csv
        casda_util.pandas_to_csv(proper_motion_filename, proper_motion_downloads_path, source_list_filtered)

        #############################
        ## SEARCH CASDA FOR SOURCE ##
        #############################

        if debug:
            logger.info("BEGIN CASDA SEARCH FOR SOURCE")

        # perform CASDA search on current planet
        # Unnamed: 0.1 stores the original index values, so its a bit of a 'hack' to use 
        pm_corrected_source_ra = source_list_filtered.loc[source_list_filtered['pl_name'] == raw_planet_name, 'ra_corrected'].values[0]
        pm_corrected_source_dec = source_list_filtered.loc[source_list_filtered['pl_name'] == raw_planet_name, 'dec_corrected'].values[0]
        planet_matches = casda_util.casda_search(source_ra=pm_corrected_source_ra,
                                                 source_dec=pm_corrected_source_dec,
                                                 casda=casda,
                                                 output_filename=output_filename,
                                                 debug=debug)
        # planet_matches = pd.read_csv(".\casda_matches\ProximaCenb_catalogues.csv")

        # If no matches, skip to next source
        if planet_matches is None:
            logger.info(f"NO CASDA MATCHES WITHIN 3 ARCSECS OF SOURCE [planet name, ra, dec]: [{planet_name, source_ra, source_dec}]")
            continue

        if planet_matches.empty:
            logger.info(f"NO CASDA MATCHES WITHIN 3 ARCSECS OF SOURCE [planet name, ra, dec]: [{planet_name, source_ra, source_dec}]")
            continue

        ###################
        ## CROSSMATCHING ##
        ###################
        if debug:
            logger.info("BEGIN CROSSMATCHING")
        
        # retrieve CSV with CASDA downloads
        casda_csv = f'.\\casda_csv_downloads\\{output_filename}.csv'
        # retrieve CSV with proper motion corrected NASA data for the planet
        proper_motion_csv = f".\\NASA_with_Proper_Motion\\{source_filename}_proper_corrected_NASA.csv"

        # Crossmatch between the proper motion corrected NASA file and the CASDA downloads
        crossmatcher.crossmatch_planet(casda_csv,proper_motion_csv, search_radius, raw_planet_name)

        if debug:
            logger.info(f"CROSSMATCH SUCCESS FOR SOURCE [planet name, ra, dec]: [{planet_name, source_ra, source_dec}]")

        # Add time delay based on number of iterations performed so far and increase counter for next source
        if i % 100 == 0:
            time.sleep(10)
        elif i % 25 == 0:
            time.sleep(2)
        
        i += 1


if __name__ == "__main__":
    main(debug=True, verbose=True)
  