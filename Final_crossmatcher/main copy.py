import filter_nasa
import casda_util
import proper_motion
import crossmatcher

import glob
import pandas as pd
import numpy as np
import os
import getpass
import sys
from concurrent.futures import ProcessPoolExecutor
import astroquery
from astroquery.casda import Casda

import time

import logging
from logging.handlers import RotatingFileHandler

# Import the centralized logger
from logger_config import logger

def login_to_casda():
    try:
        username = 'brian.w.tjahjadi@gmail.com'
        casda = Casda()
        casda.login(username=username)
        logger.info("Logged in successfully using interactive username input.")
        return casda
    except Exception as e:
        logger.error(f"Failed to login: {e}")
        sys.exit(1)  # Exit the program with an error code
    

def main(debug: bool = False, verbose: bool = False):
    os.chdir(os.path.dirname(os.path.abspath(__file__)))

    casda = login_to_casda()
    logger.info('Starting to process exoplanets.')

    # Variables for crossmatching
    search_radius = 3

    sample_paths = {'10': ".\\Hot_Jupiters\\Hot_Jupiters_10_Samples.csv",
                    '88': ".\\Hot_Jupiters\\Hot_Jupiters_88_Samples.csv",
                    '123': ".\\Hot_Jupiters\\Hot_Jupiters_123_Samples.csv",
                    'Proxima_B_Test' : ".\\proxima_cen_b_test\\PS_2024.05.09_04.24.22.csv",
                    '123?' : ".\\Hot_Jupiters\\Hot_Jupiters_123_Detections.csv"}
    sample_options = ', '.join(str(key) for key in sample_paths.keys())

    while True:
        sample_size = input(f'How many samples? ({sample_options}): ')
        if sample_size in sample_paths:
            source = sample_paths[sample_size]
            logger.info(f'RESULTS FOR {sample_size} EXOPLANETS')

            break
        else:
            logger.info("Not a valid number of sources.")
    # Find list of all planets in source file
    source_list_sorted = crossmatcher.find_planets_in_source(source)

    # List of planets with GAIA 2 ID
    source_list_filtered = proper_motion.filter_for_gaia(source_list_sorted)
    if debug:
        logger.info(f"GAIA2-filtered no-duplicate source list sorted by latest update: {source_list_filtered}")

    # Make csv of gaia only planets
    source_list_filtered.to_csv('.\\Hot_Jupiters\\Filtered_NASA_only_GAIA.csv')

    chunk_size = 25

    with ProcessPoolExecutor(max_workers = 20) as executor:
        # Distribute chunks to different cores
        futures = [executor.submit(process_chunk, source_list_filtered.iloc[start:start + chunk_size], start, debug, casda, logger, source, source_list_filtered) for start in range(0, len(source_list_filtered), chunk_size)]
        for future in futures:
            
            future.result()
    logger.info('Finished processing all exoplanets.')


def process_chunk(chunk, start_index, debug, casda, logger, source, source_list_filtered):
    if debug:
        logger.info(f"Processing chunk starting at index {start_index} with {len(chunk)} entries.")
    
    # Variables for crossmatching
    search_radius = 3


    for index, row_source in chunk.iterrows():
        # ra and dec of planet
        source_ra = row_source['ra']
        source_dec = row_source['dec']
        
        # Filter for planet name in row
        raw_planet_name = row_source['pl_name']
        planet_name = row_source['pl_name'].replace(' ', '')

        # make name of matches file
        output_filename = f"{planet_name}_catalogues"

        if debug:
            logger.info(f"EXAMINING SOURCE [planet name, ra, dec]: [{planet_name, source_ra, source_dec}]")
            logger.info(f"BEGINNING CASDA DOWNLOAD FOR SOURCE")

        # Beginning Proper Motion Correction
        if debug:
            logger.info("BEGIN SOURCE PROPER MOTION CORRECTION")

        # catalogue file with epoch to proper motion correct to
        pm_catalogue_filename = casda_util.casda_search_closest_catalogue(source_ra=source_ra, 
                                                                          source_dec=source_dec, 
                                                                          casda=casda,
                                                                          debug=debug)
        if not pm_catalogue_filename:
            logger.info(f"NO CATALOGUES WITHIN 3 DEGREES OF SOURCE [planet name, ra, dec]: [{planet_name, source_ra, source_dec}]")
            continue

        if debug:
            logger.info(f"Catalogue to proper motion correct to: {pm_catalogue_filename}")

        # epoch to proper motion correct to
        pm_epoch = casda_util.extract_epoch_from_pubdat_catalogue(pm_catalogue_filename)

        # add pm_epoch only to the row of row_source
        chunk.at[index, 'epoch'] = pm_epoch 

        if debug:
            logger.info(f"Modified source list (with added epoch): {chunk.head()}")

        # Perform proper motion correction
        source_list_filtered = proper_motion.proper_correct_planet(source_list_filtered, raw_planet_name)

        if debug:
            logger.info(f"Modified source list (with added ra_corrected, dec_corrected): {source_list_filtered.head()}")
        
        # Save csv of corrected RA and DEC
        _, source_filename = os.path.split(source)
        source_filename = source_filename[:-4]
        proper_motion_downloads_path = os.path.join(os.path.dirname(__file__), "NASA_with_Proper_Motion\\")
        proper_motion_filename = f'{planet_name}_proper_corrected_NASA.csv'
        
        casda_util.pandas_to_csv(proper_motion_filename, proper_motion_downloads_path, source_list_filtered)

        # Search CASDA for the current planet
        if debug:
            logger.info("BEGIN CASDA SEARCH FOR SOURCE")

        # perform casda search on current planet
        # Unnamed: 0.1 stores the original index values, so its a bit of a 'hack' to use 
        pm_corrected_source_ra = chunk.loc[chunk['pl_name'] == raw_planet_name, 'ra_corrected'].values[0]
        pm_corrected_source_dec = chunk.loc[chunk['pl_name'] == raw_planet_name, 'dec_corrected'].values[0]

        # pm_corrected_source_ra = chunk.loc[index, 'ra_corrected']
        # pm_corrected_source_dec = chunk.loc[index, 'dec_corrected']

        planet_matches = casda_util.casda_search(source_ra=pm_corrected_source_ra,
                                                 source_dec=pm_corrected_source_dec,
                                                 casda=casda,
                                                 output_filename=output_filename,
                                                 debug=debug)
        if planet_matches is None or planet_matches.empty:
            logger.info(f"NO CASDA MATCHES FOR SOURCE [planet name, ra, dec]: [{planet_name, source_ra, source_dec}]")
            continue

        # Crossmatching
        if debug:
            logger.info("BEGIN CROSSMATCHING")

        casda_csv = f'.\\casda_csv_downloads\\{output_filename}.csv'
        proper_motion_csv = f".\\NASA_with_Proper_Motion\\{source_filename}_proper_corrected_NASA.csv"


        crossmatcher.crossmatch_planet(casda_csv, proper_motion_csv, search_radius, raw_planet_name)

        if debug:
            logger.info(f"*CROSSMATCH SUCCESS FOR SOURCE [planet name, ra, dec]: [{planet_name, source_ra, source_dec}]")

        time.sleep(2)



import logging
from logging.handlers import RotatingFileHandler

def setup_logger():
    logger = logging.getLogger('ExoplanetLogger')
    logger.setLevel(logging.INFO)
    handler = RotatingFileHandler('out_exoplanets.txt', maxBytes=10000, backupCount=5)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.propagate = False  # Prevent the log messages from being duplicated in the python output
    return logger



if __name__ == "__main__":
    main(debug=False, verbose=False)
